#!/usr/bin/env python3
"""Monitor combinado de estados de excepción (OEA Art.27 + ONU Art.4) -> monitor_estados_excepcion.html
Lee registro_excepcion_unificado.csv. Self-contained (datos embebidos). Abrir con doble clic."""
import csv, json, datetime, os
from collections import Counter

HOY = datetime.date(2026,6,23)
SRC = 'registro_excepcion_unificado.csv'
rows=list(csv.DictReader(open(SRC,encoding='utf-8')))
for r in rows:
    try: r['_d']=datetime.date.fromisoformat(r['fecha'])
    except: r['_d']=None
rows=[r for r in rows if r['_d']]

paises=Counter(r['pais'] for r in rows)
anios=Counter(r['anio'] for r in rows)
fuentes=Counter(r['fuente'] for r in rows)
tipos=Counter(r['tipo'] for r in rows if r['tipo'])
# recencia por país (semáforo)
ult={}
for r in rows:
    if r['pais'] not in ult or r['_d']>ult[r['pais']]: ult[r['pais']]=r['_d']
recencia=[]
for p,d in sorted(ult.items(), key=lambda x:x[1], reverse=True):
    dias=(HOY-d).days
    sem='rojo' if dias<90 else ('ambar' if dias<365 else 'verde')
    recencia.append({'pais':p,'ultima':d.isoformat(),'dias':dias,'sem':sem,'n':paises[p]})

data={'rows':[{'pais':r['pais'],'fecha':r['fecha'],'anio':r['anio'],'fuente':r['fuente'],
               'tipo':r['tipo'],'evento':r['evento'],'detalle':r['detalle'],'causa':r['causa'],
               'ref':r['ref'],'url':r['url'],'texto':r.get('texto','')} for r in rows],
      'paises':paises.most_common(),'anios':sorted(anios.items()),
      'fuentes':fuentes.most_common(),'tipos':tipos.most_common(),
      'recencia':recencia,'total':len(rows),'npais':len(paises),
      'rango':[min(r['anio'] for r in rows),max(r['anio'] for r in rows)],'gen':HOY.isoformat()}

HTML='''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitor · Estados de Excepción — Américas (OEA Art.27 + ONU Art.4)</title>
<style>
:root{--bg:#0f1419;--card:#1a212b;--line:#2a3441;--tx:#e6edf3;--mut:#8b98a9;--ac:#4da3ff;
--rojo:#ff5a5a;--ambar:#ffb02e;--verde:#3ad29f;--oea:#4da3ff;--onu:#9d7bff}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--tx);padding:24px}
h1{font-size:20px;margin:0 0 2px}.sub{color:var(--mut);font-size:13px;margin-bottom:20px}
.kpis{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:22px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 18px;min-width:104px}
.kpi b{font-size:24px;display:block}.kpi span{color:var(--mut);font-size:12px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;margin-bottom:22px}
@media(max-width:880px){.grid3{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px}
.card h2{font-size:13px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut);margin:0 0 14px}
.bar{display:flex;align-items:center;gap:8px;margin:5px 0;font-size:13px}
.bar .lbl{width:120px;text-align:right;color:var(--mut);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .tr{flex:1;background:#11171f;border-radius:4px;overflow:hidden;height:18px;display:flex}
.bar .fl{height:100%}.fl.oea{background:var(--oea)}.fl.onu{background:var(--onu)}
.bar .v{width:42px;color:var(--tx)}
.yr{display:flex;align-items:flex-end;gap:2px;height:130px;padding-top:8px;overflow-x:auto}
.yr .col{min-width:11px;flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%}
.yr .cb{width:100%;background:linear-gradient(180deg,#4da3ff,#2b6cb0);border-radius:2px 2px 0 0;min-height:1px}
.yr .yl{font-size:8px;color:var(--mut);transform:rotate(-90deg);white-space:nowrap;margin-top:4px;height:22px}
.sem{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}
.rojo{background:var(--rojo)}.ambar{background:var(--ambar)}.verde{background:var(--verde)}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th,td{text-align:left;padding:6px 9px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;position:sticky;top:0;background:var(--card);cursor:pointer;white-space:nowrap}
tr:hover td{background:#1f2733}a{color:var(--ac);text-decoration:none}a:hover{text-decoration:underline}
.ctrls{display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap}
select,input{background:#11171f;border:1px solid var(--line);color:var(--tx);padding:7px 10px;border-radius:7px;font-size:13px}
.tablewrap{max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:10px}
.note{color:var(--mut);font-size:12px;margin-top:14px;line-height:1.6}
.pill{font-size:11px;color:var(--mut);border:1px solid var(--line);border-radius:20px;padding:2px 9px}
.tag{font-size:11px;padding:1px 7px;border-radius:5px;background:#22303f;color:#bcd}
.src{font-size:11px;padding:1px 7px;border-radius:5px}.src.OEA{background:#16344d;color:#9cf}.src.ONU{background:#2e2350;color:#cbf}
.rowmain{cursor:pointer}.exp{color:var(--ac);font-size:10px}
.texto{background:#11171f;padding:10px 12px;border-radius:6px;color:#c8d3e0;font-size:12px;line-height:1.55;white-space:pre-wrap;max-width:1000px}
</style></head><body>
<h1>Monitor · Estados de Excepción — Américas</h1>
<div class="sub">Registro combinado de notificaciones formales: <b>OEA Art.27 CADH</b> (2014→) + <b>ONU Art.4 PIDCP</b> (1976→) · generado __GEN__</div>
<div class="kpis">
 <div class="kpi"><b>__TOTAL__</b><span>notificaciones</span></div>
 <div class="kpi"><b>__NPAIS__</b><span>países</span></div>
 <div class="kpi"><b>__RANGO__</b><span>rango</span></div>
 <div class="kpi"><b style="color:var(--oea)">__NOEA__</b><span>OEA Art.27</span></div>
 <div class="kpi"><b style="color:var(--onu)">__NONU__</b><span>ONU Art.4</span></div>
 <div class="kpi"><b id="kfilt">__TOTAL__</b><span>en vista filtrada</span></div>
</div>
<div class="grid3">
 <div class="card"><h2>Por país</h2><div id="cpais"></div></div>
 <div class="card"><h2>Por tipo de régimen</h2><div id="ctipo"></div>
   <h2 style="margin-top:16px">Por fuente</h2><div id="cfuente"></div></div>
 <div class="card"><h2>Recencia — última por país</h2><div id="crec"></div></div>
</div>
<div class="card" style="margin-bottom:22px"><h2>Por año — 1976→ (azul OEA / morado ONU; picos 2020 COVID y crisis recientes)</h2><div class="yr" id="canio"></div></div>
<div class="card">
 <h2>Registro completo (clic en encabezado para ordenar)</h2>
 <div class="ctrls">
   <select id="ffuente"><option value="">Ambas fuentes</option><option value="OEA Art.27">OEA Art.27</option><option value="ONU Art.4">ONU Art.4</option></select>
   <select id="fpais"><option value="">Todos los países</option></select>
   <select id="fanio"><option value="">Todos los años</option></select>
   <input id="fq" placeholder="buscar tipo / detalle / país…" style="flex:1;min-width:160px">
 </div>
 <div class="tablewrap"><table id="tbl"><thead><tr>
   <th data-k="fecha">Fecha ▼</th><th data-k="pais">País</th><th data-k="fuente">Fuente</th>
   <th data-k="tipo">Régimen</th><th data-k="evento">Evento</th><th data-k="detalle">Detalle</th><th>Doc</th>
 </tr></thead><tbody></tbody></table></div>
 <div class="note">
  <span class="pill">clic en una fila ▸ para ver el texto completo</span>
  Columna <b>Doc</b>: PDF oficial (OEA) o C.N. del depositario (ONU). Ambas fuentes son <b>positivos confirmados</b> (suspensiones formalmente notificadas), no un censo: muchas emergencias no se notifican → ausencia ⇏ no-emergencia. <b>OEA Art.27</b> cubre 2014→ (texto por OCR); <b>ONU Art.4</b> añade historia desde 1976 y países no/ex-CADH (Venezuela, Trinidad y Tobago, Jamaica, Uruguay, Surinam). EEUU/Canadá no aparecen: nunca derogaron del PIDCP.
 </div>
</div>
<script>
const D=__DATA__;
document.getElementById('kfilt').textContent=D.total;
function barsSplit(el,counter){const mx=Math.max(...Object.values(counter).map(o=>o.OEA+o.ONU));
 document.getElementById(el).innerHTML=Object.entries(counter).sort((a,b)=>(b[1].OEA+b[1].ONU)-(a[1].OEA+a[1].ONU)).map(([k,o])=>
 `<div class="bar"><div class="lbl">${k||'—'}</div><div class="tr"><div class="fl oea" style="width:${o.OEA/mx*100}%"></div><div class="fl onu" style="width:${o.ONU/mx*100}%"></div></div><div class="v">${o.OEA+o.ONU}</div></div>`).join('')}
function split(key){const c={};D.rows.forEach(r=>{const k=r[key]||'—';c[k]=c[k]||{OEA:0,ONU:0};c[k][r.fuente.includes('OEA')?'OEA':'ONU']++});return c}
barsSplit('cpais',split('pais'));barsSplit('ctipo',split('tipo'));
const cf={};D.fuentes.forEach(([k,n])=>cf[k]={OEA:k.includes('OEA')?n:0,ONU:k.includes('ONU')?n:0});barsSplit('cfuente',cf);
const my=Math.max(...D.anios.map(a=>a[1]));
document.getElementById('canio').innerHTML=D.anios.map(([y,n])=>
 `<div class="col" title="${y}: ${n}"><div class="cb" style="height:${n/my*100}%"></div><div class="yl">${y}</div></div>`).join('');
document.getElementById('crec').innerHTML=D.recencia.map(r=>
 `<div class="bar"><div class="lbl"><span class="sem ${r.sem}"></span>${r.pais}</div><div style="flex:1;color:var(--mut)">${r.ultima} · ${r.n} notif</div><div class="v" title="días desde la última">${r.dias}d</div></div>`).join('');
const ff=document.getElementById('ffuente'),fp=document.getElementById('fpais'),fa=document.getElementById('fanio'),fq=document.getElementById('fq');
[...new Set(D.rows.map(r=>r.pais))].sort().forEach(p=>fp.add(new Option(p,p)));
[...new Set(D.rows.map(r=>r.anio))].sort().reverse().forEach(y=>fa.add(new Option(y,y)));
let sortK='fecha',sortAsc=false;
function render(){
 let r=D.rows.filter(x=>(!ff.value||x.fuente==ff.value)&&(!fp.value||x.pais==fp.value)&&(!fa.value||x.anio==fa.value)
   &&(!fq.value||(x.tipo+' '+x.detalle+' '+x.pais+' '+x.evento).toLowerCase().includes(fq.value.toLowerCase())));
 r.sort((a,b)=>{let v=(a[sortK]>b[sortK]?1:-1);return sortAsc?v:-v});
 document.getElementById('kfilt').textContent=r.length;
 document.querySelector('#tbl tbody').innerHTML=r.slice(0,2000).map((x,i)=>{const s=x.fuente.includes('OEA')?'OEA':'ONU';
  const doc=x.url?`<a href="${x.url}" target="_blank">${s=='OEA'?'PDF':'C.N.'} ↗</a>`:(x.ref||'—');
  const main=`<tr class="rowmain" data-i="${i}"><td>${x.texto?'<span class="exp">▸</span> ':''}${x.fecha}</td><td>${x.pais}</td><td><span class="src ${s}">${s}</span></td><td>${x.tipo?`<span class="tag">${x.tipo}</span>`:'—'}</td><td>${x.evento||'—'}</td><td>${x.detalle||'—'}</td><td>${doc}</td></tr>`;
  const det=x.texto?`<tr class="rowdet" id="det${i}" style="display:none"><td colspan="7"><div class="texto">${x.texto.replace(/</g,'&lt;')}${x.url?` <a href="${x.url}" target="_blank">[documento oficial ↗]</a>`:''}</div></td></tr>`:'';
  return main+det}).join('');
 document.querySelectorAll('.rowmain').forEach(tr=>tr.onclick=()=>{const d=document.getElementById('det'+tr.dataset.i);if(d){d.style.display=d.style.display=='none'?'table-row':'none';const e=tr.querySelector('.exp');if(e)e.textContent=d.style.display=='none'?'▸':'▾';}});
}
ff.onchange=fp.onchange=fa.onchange=render;fq.oninput=render;
document.querySelectorAll('#tbl th[data-k]').forEach(th=>th.onclick=()=>{const k=th.dataset.k;sortAsc=(sortK==k)?!sortAsc:false;sortK=k;render();});
render();
</script></body></html>'''
out=(HTML.replace('__DATA__',json.dumps(data,ensure_ascii=False))
  .replace('__TOTAL__',str(data['total'])).replace('__NPAIS__',str(data['npais']))
  .replace('__NOEA__',str(fuentes.get('OEA Art.27',0))).replace('__NONU__',str(fuentes.get('ONU Art.4',0)))
  .replace('__RANGO__',f"{data['rango'][0]}–{data['rango'][1]}").replace('__GEN__',data['gen']))
open('monitor_estados_excepcion.html','w',encoding='utf-8').write(out)
print(f"OK -> monitor_estados_excepcion.html | {data['total']} registros | {data['rango'][0]}–{data['rango'][1]} | OEA {fuentes.get('OEA Art.27',0)} ONU {fuentes.get('ONU Art.4',0)}")
