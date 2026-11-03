// SIAL v41: sin autenticación offline; no servir login desde caché sin servidor.
const CACHE='sial-lab-v043-assets';
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['./icon.png','./manifest.webmanifest'])))});
self.addEventListener('activate',e=>e.waitUntil(Promise.all([self.clients.claim(),caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('sial-lab-')&&k!==CACHE).map(k=>caches.delete(k))))])));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==self.location.origin||u.pathname.startsWith('/api/'))return;
if(u.pathname.endsWith('/')||u.pathname.endsWith('/index.html')){e.respondWith(fetch(e.request,{cache:'no-store'}));return;}
e.respondWith(fetch(e.request,{cache:'no-store'}).catch(()=>caches.match(e.request)))});
