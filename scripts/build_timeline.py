#!/usr/bin/env python3
"""Genera timeline_estados_excepcion.html: Gantt de episodios de estado de excepción por país,
mostrando vigencia (inicio→fin), renovaciones/extensiones y régimen. Lee episodios_excepcion.csv."""
import csv, json, datetime
from collections import defaultdict
T0=datetime.date(1976,1,1); T1=datetime.date(2026,12,31); SPAN=(T1-T0).days
def D(s): return datetime.date.fromisoformat(s)
eps=list(csv.DictReader(open('episodios_excepcion.csv',encoding='utf-8')))
by=defaultdict(list); tot=defaultdict(int)
for e in eps:
    by[e['pais']].append(e); tot[e['pais']]+=int(e['dias'])
paises=sorted(by, key=lambda p:-tot[p])
data={'paises':[{'pais':p,'tot':tot[p],'n':len(by[p]),
        'eps':[{'x':round((D(e['inicio'])-T0).days/SPAN*100,3),
                'w':round(max(int(e['dias']),20)/SPAN*100,3),
                'ini':e['inicio'],'fin':e['fin'],'d':int(e['dias']),'ext':int(e['n_extensiones']),
                'reg':e['regimen'],'src':e['fuentes'],'cerr':e['cerrado_explicito']} for e in by[p]]}
        for p in paises],
    'years':list(range(1976,2027,5)),
    'ymarks':[{'y':y,'x':round((datetime.date(y,1,1)-T0).days/SPAN*100,3)} for y in range(1976,2027,5)],
    'total':len(eps)}
HTML='''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Línea de tiempo · Estados de Excepción (vigencia y renovaciones)</title>
<style>
:root{--bg:#0f1419;--card:#1a212b;--line:#2a3441;--tx:#e6edf3;--mut:#8b98a9;--grid:#222c38}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--tx);padding:24px}
h1{font-size:20px;margin:0 0 2px}.sub{color:var(--mut);font-size:13px;margin-bottom:18px}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px;font-size:12px;color:var(--mut);align-items:center}
.lg{display:inline-flex;align-items:center;gap:6px}.sw{width:14px;height:12px;border-radius:3px;display:inline-block}
.chart{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 16px 8px;overflow-x:auto}
.row{display:flex;align-items:center;height:26px;position:relative}
.lbl{width:150px;min-width:150px;text-align:right;padding-right:12px;font-size:12.5px;color:var(--tx);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lbl small{color:var(--mut)}
.track{position:relative;flex:1;height:100%;border-left:1px solid var(--grid)}
.ep{position:absolute;top:5px;height:15px;border-radius:3px;cursor:pointer;opacity:.88;border:1px solid rgba(255,255,255,.12)}
.ep:hover{opacity:1;outline:1px solid #fff}
.grid{position:absolute;top:0;bottom:0;width:1px;background:var(--grid)}
.axis{display:flex;position:relative;height:20px;margin-left:150px;margin-top:4px}
.yl{position:absolute;font-size:10px;color:var(--mut);transform:translateX(-50%)}
.reg-emergencia{background:#4da3ff}.reg-sitio{background:#ffb02e}.reg-excepcion{background:#9d7bff}
.reg-garantias{background:#3ad29f}.reg-conmocion{background:#ff7ab0}.reg-otro{background:#7b8a9e}
.tip{position:fixed;background:#0b0f14;border:1px solid var(--line);border-radius:8px;padding:9px 11px;font-size:12px;pointer-events:none;display:none;z-index:9;max-width:280px;box-shadow:0 6px 20px rgba(0,0,0,.5)}
.tip b{color:#fff}.tip .k{color:var(--mut)}
.note{color:var(--mut);font-size:12px;margin-top:14px;line-height:1.6}
</style></head><body>
<h1>Línea de tiempo · Estados de Excepción en las Américas — vigencia y renovaciones</h1>
<div class="sub">Episodios reconstruidos encadenando notificaciones (declaración → extensiones → levantamiento) · OEA Art.27 + ONU Art.4 · __TOTAL__ episodios · 1976→2026</div>
<div class="legend">
 <span class="lg"><span class="sw reg-emergencia"></span>emergencia</span>
 <span class="lg"><span class="sw reg-sitio"></span>sitio</span>
 <span class="lg"><span class="sw reg-excepcion"></span>excepción</span>
 <span class="lg"><span class="sw reg-garantias"></span>susp. garantías</span>
 <span class="lg"><span class="sw reg-conmocion"></span>conmoción interior</span>
 <span class="lg" style="margin-left:8px">▏▏▏ las marcas internas = renovaciones/extensiones · ancho = duración</span>
</div>
<div class="chart" id="chart"></div>
<div class="tip" id="tip"></div>
<div class="note">Cada barra = un episodio de vigencia continua (renovaciones a ≤75 días se encadenan; un levantamiento o un lapso mayor lo cierra). Las barras sin levantamiento explícito llevan +30 días de cola estimada. Pasa el cursor para ver inicio/fin, duración y nº de extensiones. <b>Reconstrucción heurística sobre notificaciones formales</b> — no captura emergencias no notificadas.</div>
<script>
const D=__DATA__;
function regClass(r){r=(r||'').toLowerCase();if(r.includes('sitio'))return'reg-sitio';if(r.includes('garant'))return'reg-garantias';if(r.includes('conmoci'))return'reg-conmocion';if(r.includes('excepci'))return'reg-excepcion';if(r.includes('emergencia'))return'reg-emergencia';return'reg-otro';}
let h='';
D.paises.forEach(p=>{
 let bars=p.eps.map((e,i)=>{
   // marcas de renovación: líneas verticales internas proporcionales a n extensiones (máx 24 visibles)
   let ticks='';const ne=Math.min(e.ext,24);
   for(let k=1;k<=ne;k++){const lx=k/(ne+1)*100;ticks+=`<span style="position:absolute;left:${lx}%;top:0;bottom:0;width:1px;background:rgba(0,0,0,.35)"></span>`;}
   return `<div class="ep ${regClass(e.reg)}" style="left:${e.x}%;width:${e.w}%" data-p="${p.pais}" data-i="${i}">${ticks}</div>`;
 }).join('');
 h+=`<div class="row"><div class="lbl">${p.pais} <small>${p.n}ep</small></div><div class="track">${bars}</div></div>`;
});
let gr=D.ymarks.map(m=>`<div class="grid" style="left:calc(150px + ${m.x}% * (100% - 150px)/100)"></div>`).join('');
document.getElementById('chart').innerHTML=h+'<div class="axis">'+D.ymarks.map(m=>`<span class="yl" style="left:${m.x}%">${m.y}</span>`).join('')+'</div>';
// tooltip
const tip=document.getElementById('tip');
const idx={};D.paises.forEach(p=>idx[p.pais]=p.eps);
document.querySelectorAll('.ep').forEach(el=>{
 el.onmousemove=ev=>{const e=idx[el.dataset.p][+el.dataset.i];
   tip.innerHTML=`<b>${el.dataset.p}</b> · ${e.reg}<br><span class="k">inicio</span> ${e.ini} → <span class="k">fin</span> ${e.fin}${e.cerr=='1'?' (levantado)':' (est.)'}<br><span class="k">duración</span> ${e.d} días · <span class="k">extensiones</span> ${e.ext}<br><span class="k">fuente</span> ${e.src}`;
   tip.style.display='block';tip.style.left=Math.min(ev.clientX+14,window.innerWidth-290)+'px';tip.style.top=(ev.clientY+14)+'px';};
 el.onmouseleave=()=>tip.style.display='none';
});
</script></body></html>'''
out=HTML.replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__TOTAL__',str(data['total']))
open('timeline_estados_excepcion.html','w',encoding='utf-8').write(out)
print(f"OK -> timeline_estados_excepcion.html | {data['total']} episodios | {len(data['paises'])} países")
