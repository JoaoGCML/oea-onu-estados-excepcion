#!/usr/bin/env python3
"""Reconstruye EPISODIOS de estado de excepción encadenando notificaciones (declaración→extensiones→fin)
por país. Dedup cruzado OEA↔ONU. -> episodios_excepcion.csv
Heurística: eventos del mismo país dentro de GAP días = mismo episodio; 'fin/levantamiento' lo cierra."""
import csv,datetime
from collections import defaultdict
GAP=75   # días: hasta 75d entre notificaciones = misma vigencia (renovación); más = lapso
TAIL=30  # días de cola si el episodio no termina con un 'fin' explícito
def D(s):
    try:return datetime.date.fromisoformat(s)
    except:return None
def norm(p): return {'Perú':'Peru','República Dominicana':'RepDom','Trinidad y Tobago':'Trinidad'}.get(p,p)

rows=[r for r in csv.DictReader(open('registro_excepcion_unificado.csv',encoding='utf-8')) if D(r['fecha'])]
# dedup cruzado: agrupar eventos del mismo país dentro de ±7d en un solo evento
by_c=defaultdict(list)
for r in rows: by_c[r['pais']].append(r)
episodes=[]
for pais,evs in by_c.items():
    evs.sort(key=lambda r:r['fecha'])
    # colapsar duplicados ±7d (mismo hecho notificado a ambas)
    merged=[]
    for r in evs:
        d=D(r['fecha'])
        if merged and abs((d-merged[-1]['_d']).days)<=7:
            m=merged[-1]; m['_srcs'].add('OEA' if 'OEA' in r['fuente'] else 'ONU')
            if r['evento']: m['_evs'].append(r['evento'])
            if r.get('tipo') and not m['regimen']: m['regimen']=r['tipo']
            if r.get('tipo') and not m.get('tipo'): m['tipo']=r['tipo']
            continue
        merged.append({'_d':d,'fecha':r['fecha'],'evento':r['evento'],'regimen':r.get('tipo',''),
                       'tipo':r.get('tipo',''),'_srcs':{'OEA' if 'OEA' in r['fuente'] else 'ONU'},
                       '_evs':[r['evento']] if r['evento'] else []})
    # encadenar en episodios
    cur=None
    def closeable(ev): return any('fin' in e for e in ev['_evs'])
    for m in merged:
        if cur is None:
            cur={'pais':pais,'inicio':m['_d'],'fin':m['_d'],'n':1,'n_ext':0,'regimen':m['regimen'],
                 'srcs':set(m['_srcs']),'ended_fin':closeable(m)}
        else:
            gap=(m['_d']-cur['fin']).days
            if gap<=GAP and not cur['ended_fin']:
                cur['fin']=m['_d']; cur['n']+=1; cur['n_ext']+=1; cur['srcs']|=m['_srcs']
                if not cur['regimen'] and m['regimen']: cur['regimen']=m['regimen']
                cur['ended_fin']=closeable(m)
            else:
                episodes.append(cur)
                cur={'pais':pais,'inicio':m['_d'],'fin':m['_d'],'n':1,'n_ext':0,'regimen':m['regimen'],
                     'srcs':set(m['_srcs']),'ended_fin':closeable(m)}
    if cur: episodes.append(cur)

out=[]
for e in episodes:
    fin=e['fin'] if e['ended_fin'] else e['fin']+datetime.timedelta(days=TAIL)
    dur=(fin-e['inicio']).days
    out.append({'pais':e['pais'],'inicio':e['inicio'].isoformat(),'fin':fin.isoformat(),
        'dias':dur,'n_notif':e['n'],'n_extensiones':e['n_ext'],'regimen':e['regimen'] or 'estado de excepción',
        'fuentes':'+'.join(sorted(e['srcs'])),'cerrado_explicito':int(e['ended_fin'])})
out.sort(key=lambda r:(r['pais'],r['inicio']))
with open('episodios_excepcion.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['pais','inicio','fin','dias','n_notif','n_extensiones','regimen','fuentes','cerrado_explicito']);w.writeheader();w.writerows(out)
from collections import Counter
print(f"Episodios reconstruidos: {len(out)} | países: {len(set(r['pais'] for r in out))}")
print("Por país:",dict(Counter(r['pais'] for r in out).most_common()))
print("Duración media (días):",round(sum(r['dias'] for r in out)/len(out)))
print("Episodios largos (>365d):",sum(1 for r in out if r['dias']>365),"| con extensiones:",sum(1 for r in out if r['n_extensiones']>0))
mx=max(out,key=lambda r:r['dias'])
print("Más largo:",mx['pais'],mx['inicio'],"→",mx['fin'],f"({mx['dias']}d, {mx['n_extensiones']} ext)")
