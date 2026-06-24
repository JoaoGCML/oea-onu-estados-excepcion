#!/usr/bin/env python3
"""Marca duplicados cruzados OEA↔ONU en registro_excepcion_unificado.csv y construye
panel_excepcion_pais_mes.csv (target deduplicado país×mes). Correr tras merge_fuentes.py."""
import csv,datetime
from collections import defaultdict,Counter
def D(s):
    try:return datetime.date.fromisoformat(s)
    except:return None
def norm(p): return {'Perú':'Peru','República Dominicana':'RepDom','Trinidad y Tobago':'Trinidad'}.get(p,p)

rows=[r for r in csv.DictReader(open('registro_excepcion_unificado.csv',encoding='utf-8')) if D(r['fecha'])]
by_c=defaultdict(list)
for i,r in enumerate(rows): by_c[norm(r['pais'])].append(i); r['dup_cross']=''
for c,idxs in by_c.items():
    for a in idxs:
        for b in idxs:
            if a>=b: continue
            ra,rb=rows[a],rows[b]
            if ra['fuente']!=rb['fuente'] and abs((D(ra['fecha'])-D(rb['fecha'])).days)<=10:
                ra['dup_cross']='1'; rb['dup_cross']='1'
ndup=sum(1 for r in rows if r['dup_cross'])
with open('registro_excepcion_unificado.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)

src_cell=defaultdict(set); name={}
for r in rows:
    key=(norm(r['pais']),r['fecha'][:7]); name[norm(r['pais'])]=r['pais']
    src_cell[key].add('OEA' if 'OEA' in r['fuente'] else 'ONU')
pan=[{'pais':name[c],'mes':ym,'anio':ym[:4],'fuentes':'+'.join(sorted(s)),'excepcion':1}
     for (c,ym),s in sorted(src_cell.items(),key=lambda x:x[0][1])]
with open('panel_excepcion_pais_mes.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['pais','mes','anio','fuentes','excepcion']);w.writeheader();w.writerows(pan)
meses=[p['mes'] for p in pan]
print(f"dup_cross marcados: {ndup}/{len(rows)}")
print(f"Panel país×mes deduplicado: {len(pan)} celdas | {min(meses)} → {max(meses)}")
print("Confirmación:",dict(Counter(p['fuentes'] for p in pan)))
