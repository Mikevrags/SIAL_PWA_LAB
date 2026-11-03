"""SIAL laboratory login, localhost only. Not for production deployment."""
import os, sys, json, sqlite3, secrets, hashlib, hmac, time, urllib.parse, smtplib, ssl
from email.message import EmailMessage
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DB=ROOT/'sial_auth_lab.sqlite3'
HOST='127.0.0.1'; PORT=int(os.getenv('SIAL_PORT','8765'))

def db():
 c=sqlite3.connect(DB,timeout=10);c.row_factory=sqlite3.Row
 c.executescript('''CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY,salt TEXT NOT NULL,hash TEXT NOT NULL,profiles TEXT NOT NULL,failed INTEGER DEFAULT 0,locked INTEGER DEFAULT 0);CREATE TABLE IF NOT EXISTS sessions(tokenhash TEXT PRIMARY KEY,email TEXT,profile TEXT,expires INTEGER);CREATE TABLE IF NOT EXISTS resets(tokenhash TEXT PRIMARY KEY,email TEXT,expires INTEGER,used INTEGER DEFAULT 0);''');return c

def ph(p,s):return hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),450000).hex()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
ROLE_NAMES={'superadmin':'SuperAdministrador','admin_general':'Administrador General','coord_deportivo':'Coordinador Deportivo','coord_financiero':'Coordinador Financiero','capturista':'Capturista','entrenador':'Entrenador','oficial_mesa':'Oficial de mesa','arbitro':'Árbitro (temporal)'}
def role_data(role,scope):
 if role not in ROLE_NAMES:raise ValueError('Perfil desconocido: '+role)
 return {'id':role,'name':ROLE_NAMES[role],'scope':scope}
def set_profiles(email,roles,scope):
 with db() as c:
  if not c.execute('SELECT 1 FROM users WHERE email=?',(email.lower(),)).fetchone():raise ValueError('Cuenta no encontrada')
  c.execute('UPDATE users SET profiles=? WHERE email=?',(json.dumps([role_data(r,scope) for r in roles]),email.lower()))
  c.execute('DELETE FROM sessions WHERE email=?',(email.lower(),))
def user(email):
 with db() as c:return c.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
def setup(email,password):
 if len(password)<12:raise ValueError('La contraseña debe tener mínimo 12 caracteres')
 salt=secrets.token_hex(16)
 with db() as c:c.execute('INSERT INTO users(email,salt,hash,profiles) VALUES(?,?,?,?)',(email.lower(),salt,ph(password,salt),json.dumps([{'id':'superadmin','name':'SuperAdministrador','scope':'LAB'}])))

class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def log_message(self,fmt,*args):print(fmt%args)
 def sendjson(self,data,status=200,cookie=None):
  payload=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(payload)));self.send_header('X-Content-Type-Options','nosniff')
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers();self.wfile.write(payload)
 def body(self):
  n=int(self.headers.get('Content-Length','0'))
  if n>4096:raise ValueError('Solicitud demasiado grande')
  return json.loads(self.rfile.read(n) or '{}')
 def session(self):
  try:
   c=SimpleCookie();c.load(self.headers.get('Cookie',''));token=c['sial_session'].value
   with db() as conn:
    r=conn.execute('SELECT * FROM sessions WHERE tokenhash=? AND expires>?',(digest(token),int(time.time()))).fetchone()
    if r:return r
  except (KeyError, ValueError):pass
  return None
 def safe(self):
  origin=self.headers.get('Origin','')
  return not origin or origin==f'http://{HOST}:{PORT}'
 def do_GET(self):
  if self.path=='/api/auth/session':
   s=self.session()
   if not s:return self.sendjson({'authenticated':False})
   u=user(s['email']);return self.sendjson({'authenticated':True,'user':{'id':u['email'],'email':u['email'],'profiles':json.loads(u['profiles'])}})
  if self.path.split('?')[0] not in ('/','/index.html'):return self.send_error(404)
  self.path='/index.html';return super().do_GET()
 def do_POST(self):
  if not self.path.startswith('/api/auth/') or not self.safe():return self.sendjson({'error':'Acceso denegado'},403)
  try:data=self.body()
  except (ValueError,json.JSONDecodeError):return self.sendjson({'error':'Datos inválidos'},400)
  endpoint=self.path.removeprefix('/api/auth/')
  if endpoint=='login':
   email=str(data.get('email','')).strip().lower();password=str(data.get('password',''))
   u=user(email)
   if not u or u['locked'] or not hmac.compare_digest(ph(password,u['salt']),u['hash']):
    if u and not u['locked']:
     with db() as c:c.execute('UPDATE users SET failed=failed+1,locked=CASE WHEN failed+1>=5 THEN 1 ELSE 0 END WHERE email=?',(email,))
    return self.sendjson({'error':'Credenciales inválidas o cuenta bloqueada; recupera contraseña'},401)
   token=secrets.token_urlsafe(32)
   with db() as c:
    c.execute('UPDATE users SET failed=0 WHERE email=?',(email,))
    c.execute('INSERT INTO sessions VALUES(?,?,?,?)',(digest(token),email,None,int(time.time())+8*3600))
   cookie=f'sial_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800'
   return self.sendjson({'authenticated':True,'user':{'id':email,'email':email,'profiles':json.loads(u['profiles'])}},cookie=cookie)
  if endpoint=='forgot-password':
   email=str(data.get('email','')).strip().lower();u=user(email)
   if u:
    token=secrets.token_urlsafe(32)
    with db() as c:c.execute('INSERT INTO resets VALUES(?,?,?,0)',(digest(token),email,int(time.time())+900))
    # SMTP configuration is mandatory; never expose the reset token in HTTP response or logs.
    if all(os.getenv(k) for k in ('SIAL_SMTP_HOST','SIAL_SMTP_USER','SIAL_SMTP_PASS','SIAL_SMTP_FROM')):
     msg=EmailMessage();msg['Subject']='SIAL: recuperar contraseña';msg['From']=os.environ['SIAL_SMTP_FROM'];msg['To']=email
     msg.set_content(f'Enlace válido 15 minutos: http://{HOST}:{PORT}/?reset={urllib.parse.quote(token)}\nÚsalo únicamente en tu computadora de laboratorio.')
     try:
      with smtplib.SMTP_SSL(os.environ['SIAL_SMTP_HOST'],int(os.getenv('SIAL_SMTP_PORT','465')),context=ssl.create_default_context(),timeout=10) as smtp:
       smtp.login(os.environ['SIAL_SMTP_USER'],os.environ['SIAL_SMTP_PASS']);smtp.send_message(msg)
     except Exception as exc:print('No se pudo enviar correo de recuperación:',type(exc).__name__)
   return self.sendjson({'ok':True})
  if endpoint=='reset-password':
   token=str(data.get('token',''));password=str(data.get('password',''))
   if len(password)<12:return self.sendjson({'error':'Mínimo 12 caracteres'},400)
   with db() as c:
    r=c.execute('SELECT * FROM resets WHERE tokenhash=? AND expires>? AND used=0',(digest(token),int(time.time()))).fetchone()
    if not r:return self.sendjson({'error':'Enlace inválido o caducado'},400)
    salt=secrets.token_hex(16);c.execute('UPDATE users SET salt=?,hash=?,failed=0,locked=0 WHERE email=?',(salt,ph(password,salt),r['email']))
    c.execute('UPDATE resets SET used=1 WHERE email=?',(r['email'],));c.execute('DELETE FROM sessions WHERE email=?',(r['email'],))
   return self.sendjson({'ok':True})
  if endpoint=='active-profile':
   s=self.session()
   if not s:return self.sendjson({'error':'Sesión requerida'},401)
   u=user(s['email']);profile=str(data.get('profileId',''))
   if profile not in [p['id'] for p in json.loads(u['profiles'])]:return self.sendjson({'error':'Perfil no autorizado'},403)
   with db() as c:c.execute('UPDATE sessions SET profile=? WHERE tokenhash=?',(profile,s['tokenhash']))
   return self.sendjson({'ok':True})
  if endpoint=='logout':
   s=self.session()
   if s:
    with db() as c:c.execute('DELETE FROM sessions WHERE tokenhash=?',(s['tokenhash'],))
   return self.sendjson({'ok':True},cookie='sial_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
  return self.sendjson({'error':'No encontrado'},404)

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='list-roles':
  for k,v in ROLE_NAMES.items():print(k,'=',v)
  sys.exit(0)
 if len(sys.argv)>1 and sys.argv[1]=='assign-roles':
  email=input('Correo existente: ').strip().lower()
  print('Perfiles:',', '.join(ROLE_NAMES))
  roles=[r.strip() for r in input('Perfiles separados por coma: ').split(',') if r.strip()]
  if not roles:raise ValueError('Se requiere al menos un perfil')
  scope=input('Alcance de laboratorio (ej. Inv26/J5, o LAB): ').strip() or 'LAB'
  set_profiles(email,roles,scope);print('Perfiles asignados; sesiones anteriores cerradas.');sys.exit(0)
 if len(sys.argv)>1 and sys.argv[1]=='create-user':
  import getpass
  email=input('Correo de SuperAdministrador: ').strip().lower();password=getpass.getpass('Contraseña (mínimo 12 caracteres): ')
  setup(email,password);print('Usuario de laboratorio creado.');sys.exit(0)
 print(f'SIAL LAB: http://{HOST}:{PORT}/ (solo equipo local)')
 ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
