#!/usr/bin/env python3
"""Une OEA Art.27 (enriquecido + texto OCR) + ONU Art.4 (texto MTDSG + PDF C.N.)
en registro_excepcion_unificado.csv (esquema común con url y texto para ambas)."""
import csv,os,re
TXTDIR="txt"
def oea_texto(url):
    if not url: return ''
    tf=os.path.join(TXTDIR,url.rsplit('/',1)[-1].replace('.pdf','')+'.txt')
    if os.path.exists(tf):
        t=open(tf,encoding='utf-8').read()
        return re.sub(r'\s+',' ',t).strip()[:1500]
    return ''
out=[]
# OEA Art.27
if os.path.exists('notif_oea_art27_enriquecido.csv'):
    for r in csv.DictReader(open('notif_oea_art27_enriquecido.csv',encoding='utf-8')):
        out.append({'pais':r['pais'],'fecha':r['fecha'],'anio':r['anio'],
            'fuente':'OEA Art.27','tipo':r.get('tipo','') or 'suspensión de garantías',
            'evento':'declaración/prórroga','detalle':r.get('decreto','') or r.get('nota_no',''),
            'causa':r.get('causa',''),'ref':r.get('nota_no',''),'url':r.get('url_pdf',''),
            'texto':oea_texto(r.get('url_pdf',''))})
# ONU Art.4
if os.path.exists('un_derogaciones_art4.csv'):
    for r in csv.DictReader(open('un_derogaciones_art4.csv',encoding='utf-8')):
        out.append({'pais':r['pais'],'fecha':r['fecha'],'anio':r['anio'],
            'fuente':'ONU Art.4','tipo':r.get('regimen','') or 'derogación PIDCP',
            'evento':r.get('tipo_evento',''),'detalle':r.get('cn_ref',''),
            'causa':'','ref':r.get('cn_ref',''),'url':r.get('url_pdf',''),
            'texto':r.get('texto','')})
out.sort(key=lambda r:r['fecha'])
cols=['pais','fecha','anio','fuente','tipo','evento','detalle','causa','ref','url','texto']
with open('registro_excepcion_unificado.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(out)
from collections import Counter
print(f"Unificado: {len(out)} registros | rango {out[0]['fecha']} → {out[-1]['fecha']}")
print("Por fuente:",dict(Counter(r['fuente'] for r in out)))
print("Con URL:",sum(1 for r in out if r['url']),"| con texto:",sum(1 for r in out if r['texto']))
