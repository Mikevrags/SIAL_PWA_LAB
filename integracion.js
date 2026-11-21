/* SIAL laboratorio: puente acta/impresión, no altera la captura histórica */
(()=>{
'use strict';
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const stamp=()=>new Date().toISOString().replace(/[:.]/g,'-');
function snapshot(){
 if(typeof game==='undefined'||typeof state==='undefined')throw Error('Partido no seleccionado');
 const g=JSON.parse(JSON.stringify(game)),s=JSON.parse(JSON.stringify(state));
 const ficticio=s.rosters.some(r=>r.some(p=>/FICTICIO|MAQUETA/i.test(String(p.nombre||''))));
 return {esquema:'SIAL_LAB_ACTA_INTEGRADA_01',generado:new Date().toISOString(),estatus:'BORRADOR_NO_OFICIAL',advertencias:[...(ficticio?['Contiene jugadores de maqueta']:[]),...(s.rosters.some(r=>!r.length)?['Roster incompleto o vacío']:[])],partido:g,estado:s};
}
function guardar(nombre,contenido,tipo){const a=document.createElement('a');const u=URL.createObjectURL(new Blob([contenido],{type:tipo}));a.href=u;a.download=nombre;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1500);}
function actaHtml(d){const g=d.partido,s=d.estado;const teams=g.teams||['Equipo A','Equipo B'];
const roster=(t)=>`<h3>${esc(teams[t])}</h3><table><thead><tr><th>Dorsal</th><th>Jugador</th><th>Estado</th><th>PersonaID</th></tr></thead><tbody>${(s.rosters[t]||[]).map(p=>`<tr><td>${esc(p.dorsal)}</td><td>${esc(p.nombre)}</td><td>${esc(p.estado||'SIN VALIDAR')}</td><td>${esc(p.persona_id||'—')}</td></tr>`).join('')||'<tr><td colspan="4">SIN ROSTER VALIDADO</td></tr>'}</tbody></table>`;
const events=(s.events||[]).map((e,i)=>`<tr><td>${esc(e.numero??i+1)}</td><td>${esc(e.periodo)}</td><td>${esc(e.tiempo)}</td><td>${esc(e.equipo)}</td><td>${esc(e.dorsal)}</td><td>${esc(e.jugador)}</td><td>${esc(e.accion)}</td><td>${esc(e.points??'')}</td></tr>`).join('');
return `<!doctype html><html lang="es"><meta charset="utf-8"><title>SIAL · Acta borrador · ${esc(g.id)}</title><style>body{font:12px Arial,sans-serif;margin:18mm;color:#111}h1{font-size:20px}h2{font-size:15px;border-bottom:2px solid #222}h3{font-size:13px}table{width:100%;border-collapse:collapse;margin:10px 0}th,td{border:1px solid #777;padding:4px;text-align:left}th{background:#eee}.warning{border:2px solid #a00;padding:9px;font-weight:bold}.break{break-before:page}header{display:flex;justify-content:space-between}@page{size:letter portrait;margin:12mm}button{padding:8px 14px}@media print{button{display:none}}</style><header><h1>SIAL BASKET · ACTA DE LABORATORIO</h1><button onclick="window.print()">Imprimir / Guardar PDF</button></header><p class="warning">BORRADOR NO OFICIAL · REQUIERE REVISIÓN Y VALIDACIÓN ${esc(d.advertencias.join(' · '))}</p><p><b>Partido:</b> ${esc(g.id)} · <b>Fecha:</b> ${esc(g.date)} · <b>Hora:</b> ${esc(g.time)} · <b>Cancha:</b> ${esc(g.court)} · <b>Grupo:</b> ${esc(g.group)} · <b>Categoría:</b> ${esc(g.category)}</p><h2>Equipos y rosters</h2>${roster(0)}${roster(1)}<h2 class="break">Cronología de eventos (${(s.events||[]).length})</h2><table><thead><tr><th>#</th><th>Periodo</th><th>Tiempo</th><th>Equipo</th><th>Dorsal</th><th>Jugador</th><th>Acción</th><th>Puntos</th></tr></thead><tbody>${events||'<tr><td colspan="8">Sin eventos registrados</td></tr>'}</tbody></table><p>Generado: ${esc(d.generado)}. Datos locales del dispositivo. No sustituye el acta oficial SDC.</p></html>`;
}
function add(){const host=document.getElementById('a1tools')||document.querySelector('main');if(!host||document.getElementById('sialIntegratedPrint'))return;
const wrap=document.createElement('span');wrap.style.cssText='display:inline-flex;gap:6px;flex-wrap:wrap;margin:4px';
const b=(id,label,fn)=>{const x=document.createElement('button');x.id=id;x.type='button';x.textContent=label;x.addEventListener('click',()=>{try{fn()}catch(e){alert('SIAL: '+e.message)}});wrap.append(x)};
b('sialIntegratedJson','ACTA + EVENTOS JSON',()=>{const d=snapshot();guardar(`SIAL_${d.partido.id}_INTEGRADO_${stamp()}.json`,JSON.stringify(d,null,2),'application/json')});
b('sialIntegratedPrint','ACTA / IMPRIMIR',()=>{const d=snapshot();const w=window.open('','_blank');if(!w){alert('Permite ventanas emergentes para imprimir');return;}w.document.open();w.document.write(actaHtml(d));w.document.close()});
host.append(wrap)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',add);else add();
})();
