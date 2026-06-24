#!/usr/bin/env python3
"""Dashboard único (Gantt + monitor + distribuciones) estética escandinava minimalista.
Lee registro_excepcion_unificado.csv + episodios_excepcion.csv -> dashboard_excepcion.html"""
import csv, json, datetime
from collections import Counter, defaultdict
HOY=datetime.date(2026,6,24); T0=datetime.date(1976,1,1); T1=datetime.date(2026,12,31); SPAN=(T1-T0).days
def D(s):
    try:return datetime.date.fromisoformat(s)
    except:return None

reg=[r for r in csv.DictReader(open('registro_excepcion_unificado.csv',encoding='utf-8')) if D(r['fecha'])]
eps=list(csv.DictReader(open('episodios_excepcion.csv',encoding='utf-8')))

def srctag(r): return 'OEA' if 'OEA' in r['fuente'] else 'ONU'
paises_split={}; tipos_split={}
for r in reg:
    paises_split.setdefault(r['pais'],{'OEA':0,'ONU':0})[srctag(r)]+=1
    tipos_split.setdefault(r['tipo'] or '—',{'OEA':0,'ONU':0})[srctag(r)]+=1
anios=Counter(r['anio'] for r in reg)
fuentes=Counter(r['fuente'] for r in reg)
ult={}
for r in reg:
    d=D(r['fecha'])
    if r['pais'] not in ult or d>ult[r['pais']]: ult[r['pais']]=d
recencia=[]
for p,d in sorted(ult.items(),key=lambda x:x[1],reverse=True):
    dias=(HOY-d).days; sem='rojo' if dias<90 else('ambar' if dias<365 else 'verde')
    recencia.append({'pais':p,'ultima':d.isoformat(),'dias':dias,'sem':sem,'n':paises_split[p]['OEA']+paises_split[p]['ONU']})

by=defaultdict(list); tot=defaultdict(int)
for e in eps: by[e['pais']].append(e); tot[e['pais']]+=int(e['dias'])
tl_paises=sorted(by,key=lambda p:-tot[p])
timeline=[{'pais':p,'n':len(by[p]),
    'eps':[{'x':round((D(e['inicio'])-T0).days/SPAN*100,3),'w':round(max(int(e['dias']),25)/SPAN*100,3),
            'ini':e['inicio'],'fin':e['fin'],'d':int(e['dias']),'ext':int(e['n_extensiones']),
            'reg':e['regimen'],'src':e['fuentes'],'cerr':e['cerrado_explicito']} for e in by[p]]} for p in tl_paises]
ymarks=[{'y':y,'x':round((datetime.date(y,1,1)-T0).days/SPAN*100,3)} for y in range(1980,2027,5)]

data={'rows':[{'pais':r['pais'],'fecha':r['fecha'],'anio':r['anio'],'fuente':r['fuente'],'tipo':r['tipo'],
    'evento':r['evento'],'detalle':r['detalle'],'causa':r['causa'],'ref':r['ref'],'url':r['url'],'texto':r.get('texto','')} for r in reg],
  'paises':sorted(paises_split.items(),key=lambda x:-(x[1]['OEA']+x[1]['ONU'])),
  'tipos':sorted(tipos_split.items(),key=lambda x:-(x[1]['OEA']+x[1]['ONU'])),
  'anios':sorted(anios.items()),'recencia':recencia,'timeline':timeline,'ymarks':ymarks,
  'total':len(reg),'npais':len(paises_split),'noea':fuentes.get('OEA Art.27',0),'nonu':fuentes.get('ONU Art.4',0),
  'neps':len(eps),'rango':[min(r['anio'] for r in reg),max(r['anio'] for r in reg)],'gen':HOY.isoformat()}

HTML=r'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Estados de excepción · Américas</title>
<style>
:root{
 --bg:#f4f2ec;--surface:#fbfaf6;--ink:#2f2d27;--mut:#6c6759;--faint:#8c8779;--line:#e2ddd2;--line2:#cdc7b8;
 --blue:#4f7197;--mauve:#7e6b96;--ochre:#b08a45;--sage:#6f8f78;--rose:#ad7d8e;--neutral:#928c7e;
 --track:#e7e2d6;--rojo:#b85c4e;--ambar:#b78a42;--verde:#6c9073}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
 font:400 14px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,sans-serif;
 -webkit-font-smoothing:antialiased;letter-spacing:.1px}
.wrap{max-width:1180px;margin:0 auto;padding:0 32px}
header{padding:48px 0 8px}
h1{font-size:25px;font-weight:500;margin:0 0 6px;letter-spacing:-.2px}
.lede{color:var(--mut);font-size:14px;max-width:680px;margin:0}
nav{position:sticky;top:0;z-index:20;background:rgba(244,242,236,.92);backdrop-filter:blur(8px);
 border-bottom:1px solid var(--line2);margin-top:24px}
nav .wrap{display:flex;gap:4px;padding-top:6px;padding-bottom:6px;flex-wrap:wrap}
nav a{color:var(--mut);text-decoration:none;font-size:13px;padding:8px 14px;border-radius:8px;letter-spacing:.2px}
nav a:hover{color:var(--ink);background:#e8e3d8}
section{padding:40px 0;border-bottom:1px solid var(--line2);scroll-margin-top:52px}
.eyebrow{font-size:11.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--mut);margin:0 0 18px;font-weight:500}
h2{font-size:18px;font-weight:500;margin:0 0 4px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:1px;background:var(--line2);border:1px solid var(--line2);border-radius:14px;overflow:hidden}
.kpi{background:var(--surface);padding:20px 22px}
.kpi b{display:block;font-size:28px;font-weight:500;letter-spacing:-.5px}
.kpi span{color:var(--mut);font-size:12.5px}
.kpi.oea b{color:var(--blue)}.kpi.onu b{color:var(--mauve)}
.card{background:var(--surface);border:1px solid var(--line2);border-radius:14px;padding:22px 24px}
.cols{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px}
@media(max-width:900px){.cols{grid-template-columns:1fr}}
.h3{font-size:12.5px;font-weight:500;color:var(--mut);margin:0 0 14px;letter-spacing:.2px}
.bar{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:13px}
.bar .lbl{width:118px;text-align:right;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .tr{flex:1;background:var(--track);border-radius:6px;overflow:hidden;height:14px;display:flex}
.bar .fl{height:100%}.fl.oea{background:var(--blue)}.fl.onu{background:var(--mauve)}
.bar .v{width:42px;color:var(--mut);font-variant-numeric:tabular-nums}
.sem{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:7px}
.rojo{background:var(--rojo)}.ambar{background:var(--ambar)}.verde{background:var(--verde)}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12px;color:var(--mut);margin:0 0 18px;align-items:center}
.lg{display:inline-flex;align-items:center;gap:7px}.sw{width:13px;height:11px;border-radius:3px}
.r-emergencia{background:var(--blue)}.r-sitio{background:var(--ochre)}.r-excepcion{background:var(--mauve)}
.r-garantias{background:var(--sage)}.r-conmocion{background:var(--rose)}.r-otro{background:var(--neutral)}
.tl{position:relative}
.tlrow{display:flex;align-items:center;height:25px;position:relative;z-index:1}
.tllbl{width:138px;min-width:138px;text-align:right;padding-right:14px;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tllbl small{color:var(--faint);font-variant-numeric:tabular-nums}
.tltrack{position:relative;flex:1;height:100%}
.tltrack::before{content:"";position:absolute;left:0;right:0;top:11px;height:3px;background:var(--track);border-radius:2px}
.ovl{position:absolute;left:138px;right:0;top:0;bottom:22px;pointer-events:none;z-index:0}
.gl{position:absolute;top:0;bottom:0;width:1px;background:var(--line)}
.gll{position:absolute;bottom:-18px;font-size:10.5px;color:var(--mut);transform:translateX(-50%);font-variant-numeric:tabular-nums}
.ep{position:absolute;top:6px;height:13px;border-radius:3px;cursor:pointer;border:1px solid rgba(47,45,39,.14)}
.ep:hover{box-shadow:0 0 0 1.5px var(--ink)}
.ep .tk{position:absolute;top:0;bottom:0;width:1px;background:rgba(251,250,246,.7)}
.axisp{height:24px;margin-left:138px;position:relative;margin-top:6px}
.yrchart{display:flex;align-items:flex-end;gap:3px;height:160px;border-bottom:1px solid var(--line2)}
.yrcol{flex:1;min-width:9px;display:flex;flex-direction:column;justify-content:flex-end;height:100%;align-items:center}
.yrbar{width:100%;background:var(--blue);border-radius:3px 3px 0 0;min-height:2px}
.yrlbl{font-size:9.5px;color:var(--faint);margin-top:7px;font-variant-numeric:tabular-nums}
.ctrls{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
select,input{font:inherit;background:var(--surface);border:1px solid var(--line2);color:var(--ink);padding:8px 11px;border-radius:9px;font-size:13px}
input::placeholder{color:var(--faint)}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:500;position:sticky;top:46px;background:var(--bg);cursor:pointer;white-space:nowrap;font-size:12px;letter-spacing:.3px}
.rowmain{cursor:pointer}.rowmain:hover td{background:#ece8de}
.exp{color:var(--faint);font-size:9px;margin-right:4px}
td .src{font-size:11px;padding:1px 8px;border-radius:20px}
.src.OEA{background:#dde6ef;color:#3a5470}.src.ONU{background:#e6dfee;color:#574868}
.tag{font-size:11.5px;padding:1px 9px;border-radius:6px;background:#e7e2d6;color:#595448}
.texto{background:#ede9e0;padding:13px 15px;border-radius:10px;color:#403e36;font-size:12.5px;line-height:1.6;white-space:pre-wrap;max-width:980px}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
.tablewrap{max-height:600px;overflow:auto;border:1px solid var(--line2);border-radius:12px}
.note{color:var(--mut);font-size:12px;margin-top:16px;line-height:1.65}
.tip{position:fixed;background:#fff;border:1px solid var(--line2);border-radius:10px;padding:11px 13px;font-size:12px;pointer-events:none;display:none;z-index:50;max-width:300px;box-shadow:0 8px 28px rgba(60,55,40,.16);line-height:1.5}
.tip b{font-weight:500}.tip .k{color:var(--mut)}
footer{padding:32px 0;color:var(--faint);font-size:12px}
</style></head><body>
<div class="wrap"><header>
<h1>Estados de excepción · Américas</h1>
<p class="lede">Registro combinado de notificaciones formales de suspensión de garantías — OEA Art. 27 CADH (2014→) y ONU Art. 4 PIDCP (1976→) — con reconstrucción de periodos de vigencia y renovaciones.</p>
</header></div>
<nav><div class="wrap">
<a href="#resumen">Resumen</a><a href="#vigencia">Vigencia</a><a href="#distrib">Distribuciones</a><a href="#registro">Registro</a>
</div></nav>
<div class="wrap">

<section id="resumen">
<p class="eyebrow">Resumen</p>
<div class="kpis">
 <div class="kpi"><b>__TOTAL__</b><span>notificaciones</span></div>
 <div class="kpi"><b>__NEPS__</b><span>episodios de vigencia</span></div>
 <div class="kpi"><b>__NPAIS__</b><span>países</span></div>
 <div class="kpi"><b>__RANGO__</b><span>periodo cubierto</span></div>
 <div class="kpi oea"><b>__NOEA__</b><span>OEA Art. 27</span></div>
 <div class="kpi onu"><b>__NONU__</b><span>ONU Art. 4</span></div>
</div>
</section>

<section id="vigencia">
<p class="eyebrow">Vigencia</p>
<h2>Cuándo estuvo activo cada estado de excepción, y sus renovaciones</h2>
<div class="legend" style="margin-top:14px">
 <span class="lg"><span class="sw r-emergencia"></span>emergencia</span>
 <span class="lg"><span class="sw r-sitio"></span>sitio</span>
 <span class="lg"><span class="sw r-excepcion"></span>excepción</span>
 <span class="lg"><span class="sw r-garantias"></span>susp. garantías</span>
 <span class="lg"><span class="sw r-conmocion"></span>conmoción</span>
 <span class="lg" style="color:var(--faint)">· marcas claras = renovaciones · ancho = duración</span>
</div>
<div class="card"><div class="tl" id="tl"></div></div>
<p class="note">Cada barra es un periodo de vigencia continua: las renovaciones a ≤75 días se encadenan; un levantamiento o un lapso mayor cierra el episodio. Las barras sin levantamiento explícito llevan +30 días de cola estimada. Pasa el cursor para ver detalle.</p>
</section>

<section id="distrib">
<p class="eyebrow">Distribuciones</p>
<h2>Quién, qué tipo, qué fuente, qué tan reciente</h2>
<div class="cols" style="margin-top:18px">
 <div class="card"><p class="h3">Notificaciones por país</p><div id="cpais"></div></div>
 <div class="card"><p class="h3">Por tipo de régimen</p><div id="ctipo"></div></div>
 <div class="card"><p class="h3">Recencia — última por país</p><div id="crec"></div></div>
</div>
<div class="card" style="margin-top:18px"><p class="h3">Notificaciones por año</p><div class="yrchart" id="canio"></div></div>
</section>

<section id="registro">
<p class="eyebrow">Registro</p>
<h2>Cada notificación — clic en una fila para ver el texto</h2>
<div class="ctrls" style="margin-top:18px">
 <select id="ffuente"><option value="">Ambas fuentes</option><option value="OEA Art.27">OEA Art. 27</option><option value="ONU Art.4">ONU Art. 4</option></select>
 <select id="fpais"><option value="">Todos los países</option></select>
 <select id="fanio"><option value="">Todos los años</option></select>
 <input id="fq" placeholder="buscar tipo, detalle, país…" style="flex:1;min-width:180px">
</div>
<div class="tablewrap"><table id="tbl"><thead><tr>
 <th data-k="fecha">Fecha</th><th data-k="pais">País</th><th data-k="fuente">Fuente</th>
 <th data-k="tipo">Régimen</th><th data-k="evento">Evento</th><th data-k="detalle">Detalle</th><th>Doc</th>
</tr></thead><tbody></tbody></table></div>
<p class="note"><b id="kfilt">__TOTAL__</b> registros en vista. Columna Doc: PDF oficial (OEA) o C.N. del depositario (ONU). Ambas fuentes son positivos confirmados (suspensiones notificadas), no un censo: muchas emergencias no se notifican. EE. UU. y Canadá no aparecen — nunca derogaron del PIDCP.</p>
</section>

<footer>Generado __GEN__ · fuentes: Depto. Derecho Internacional OEA · UN Treaty Collection (MTDSG IV-4)</footer>
</div>
<div class="tip" id="tip"></div>
<script>
const D=__DATA__;
function rc(r){r=(r||'').toLowerCase();if(r.includes('sitio'))return'r-sitio';if(r.includes('garant'))return'r-garantias';if(r.includes('conmoci'))return'r-conmocion';if(r.includes('excepci'))return'r-excepcion';if(r.includes('emergencia'))return'r-emergencia';return'r-otro';}
function regvar(cls){return{'r-emergencia':'blue','r-sitio':'ochre','r-excepcion':'mauve','r-garantias':'sage','r-conmocion':'rose','r-otro':'neutral'}[cls];}
function bars(el,arr){const mx=Math.max(...arr.map(a=>a[1].OEA+a[1].ONU));
 document.getElementById(el).innerHTML=arr.map(([k,o])=>`<div class="bar"><div class="lbl">${k}</div><div class="tr"><div class="fl oea" style="width:${o.OEA/mx*100}%"></div><div class="fl onu" style="width:${o.ONU/mx*100}%"></div></div><div class="v">${o.OEA+o.ONU}</div></div>`).join('');}
bars('cpais',D.paises);bars('ctipo',D.tipos);
document.getElementById('crec').innerHTML=D.recencia.map(r=>`<div class="bar"><div class="lbl"><span class="sem ${r.sem}"></span>${r.pais}</div><div style="flex:1;color:var(--mut);font-size:12px">${r.ultima}</div><div class="v">${r.dias}d</div></div>`).join('');
const my=Math.max(...D.anios.map(a=>a[1]));
document.getElementById('canio').innerHTML=D.anios.map(([y,n])=>`<div class="yrcol" title="${y}: ${n}"><div class="yrbar" style="height:${n/my*100}%"></div><div class="yrlbl">${(+y)%5==0?y:''}</div></div>`).join('');
let tl='';
tl+=`<div class="ovl">${D.ymarks.map(m=>`<span class="gl" style="left:${m.x}%"></span><span class="gll" style="left:${m.x}%">${m.y}</span>`).join('')}</div>`;
D.timeline.forEach(p=>{let b=p.eps.map((e,i)=>{const cls=rc(e.reg);let tk='';const ne=Math.min(e.ext,20);for(let k=1;k<=ne;k++)tk+=`<span class="tk" style="left:${k/(ne+1)*100}%"></span>`;return `<div class="ep" style="left:${e.x}%;width:${e.w}%;background:var(--${regvar(cls)})" data-p="${p.pais}" data-i="${i}">${tk}</div>`;}).join('');
 tl+=`<div class="tlrow"><div class="tllbl">${p.pais} <small>${p.n}</small></div><div class="tltrack">${b}</div></div>`;});
tl+=`<div class="axisp"></div>`;
document.getElementById('tl').innerHTML=tl;
const tip=document.getElementById('tip'),idx={};D.timeline.forEach(p=>idx[p.pais]=p.eps);
document.querySelectorAll('.ep').forEach(el=>{el.onmousemove=ev=>{const e=idx[el.dataset.p][+el.dataset.i];
 tip.innerHTML=`<b>${el.dataset.p}</b> · ${e.reg}<br><span class="k">inicio</span> ${e.ini} → <span class="k">fin</span> ${e.fin}${e.cerr=='1'?' (levantado)':' (est.)'}<br><span class="k">duración</span> ${e.d} días · <span class="k">extensiones</span> ${e.ext}<br><span class="k">fuente</span> ${e.src}`;
 tip.style.display='block';tip.style.left=Math.min(ev.clientX+14,innerWidth-310)+'px';tip.style.top=(ev.clientY+14)+'px';};el.onmouseleave=()=>tip.style.display='none';});
const ff=document.getElementById('ffuente'),fp=document.getElementById('fpais'),fa=document.getElementById('fanio'),fq=document.getElementById('fq');
[...new Set(D.rows.map(r=>r.pais))].sort().forEach(p=>fp.add(new Option(p,p)));
[...new Set(D.rows.map(r=>r.anio))].sort().reverse().forEach(y=>fa.add(new Option(y,y)));
let sk='fecha',sa=false;
function render(){let r=D.rows.filter(x=>(!ff.value||x.fuente==ff.value)&&(!fp.value||x.pais==fp.value)&&(!fa.value||x.anio==fa.value)&&(!fq.value||(x.tipo+' '+x.detalle+' '+x.pais+' '+x.evento).toLowerCase().includes(fq.value.toLowerCase())));
 r.sort((a,b)=>{let v=a[sk]>b[sk]?1:-1;return sa?v:-v});document.getElementById('kfilt').textContent=r.length;
 document.querySelector('#tbl tbody').innerHTML=r.slice(0,2000).map((x,i)=>{const s=x.fuente.includes('OEA')?'OEA':'ONU';
  const doc=x.url?`<a href="${x.url}" target="_blank">${s=='OEA'?'PDF':'C.N.'} ↗</a>`:(x.ref||'—');
  const m=`<tr class="rowmain" data-i="${i}"><td>${x.texto?'<span class="exp">▸</span>':''}${x.fecha}</td><td>${x.pais}</td><td><span class="src ${s}">${s}</span></td><td>${x.tipo?`<span class="tag">${x.tipo}</span>`:'—'}</td><td>${x.evento||'—'}</td><td>${x.detalle||'—'}</td><td>${doc}</td></tr>`;
  const d=x.texto?`<tr id="det${i}" style="display:none"><td colspan="7"><div class="texto">${x.texto.replace(/</g,'&lt;')}${x.url?` <a href="${x.url}" target="_blank">[documento oficial ↗]</a>`:''}</div></td></tr>`:'';
  return m+d;}).join('');
 document.querySelectorAll('.rowmain').forEach(tr=>tr.onclick=()=>{const d=document.getElementById('det'+tr.dataset.i);if(d){d.style.display=d.style.display=='none'?'table-row':'none';const e=tr.querySelector('.exp');if(e)e.textContent=d.style.display=='none'?'▸':'▾';}});}
ff.onchange=fp.onchange=fa.onchange=render;fq.oninput=render;
document.querySelectorAll('#tbl th[data-k]').forEach(th=>th.onclick=()=>{const k=th.dataset.k;sa=(sk==k)?!sa:false;sk=k;render();});
render();
</script></body></html>'''
out=(HTML.replace('__DATA__',json.dumps(data,ensure_ascii=False))
 .replace('__TOTAL__',str(data['total'])).replace('__NEPS__',str(data['neps']))
 .replace('__NPAIS__',str(data['npais'])).replace('__NOEA__',str(data['noea'])).replace('__NONU__',str(data['nonu']))
 .replace('__RANGO__',f"{data['rango'][0]}–{data['rango'][1]}").replace('__GEN__',data['gen']))
open('dashboard_excepcion.html','w',encoding='utf-8').write(out)
print(f"OK -> dashboard_excepcion.html | {data['total']} notif · {data['neps']} episodios · {data['npais']} países")
