#!/usr/bin/env python3
"""Derogaciones PIDCP Art.4(3) desde UNTC (un_iccpr.html). País=<p class=invisible>, fecha=<p align=right>.
-> un_derogaciones_art4.csv (recall histórico 1976→, incluye no-CADH)."""
import re, csv
html=open('un_iccpr.html',encoding='utf-8',errors='ignore').read()
OEA={'Antigua and Barbuda','Argentina','Bahamas','Bahamas (The)','Barbados','Belize','Bolivia','Bolivia (Plurinational State of)','Brazil','Canada','Chile','Colombia','Costa Rica','Cuba','Dominica','Dominican Republic','Ecuador','El Salvador','Grenada','Guatemala','Guyana','Haiti','Honduras','Jamaica','Mexico','Nicaragua','Panama','Paraguay','Peru','Saint Kitts and Nevis','Saint Lucia','Saint Vincent and the Grenadines','Suriname','Trinidad and Tobago','United States of America','Uruguay','Venezuela','Venezuela (Bolivarian Republic of)'}
ESP={'Argentina':'Argentina','Bolivia':'Bolivia','Bolivia (Plurinational State of)':'Bolivia','Brazil':'Brasil','Chile':'Chile','Colombia':'Colombia','Ecuador':'Ecuador','El Salvador':'El Salvador','Guatemala':'Guatemala','Jamaica':'Jamaica','Nicaragua':'Nicaragua','Panama':'Panamá','Peru':'Perú','Suriname':'Suriname','Trinidad and Tobago':'Trinidad y Tobago','Venezuela':'Venezuela','Venezuela (Bolivarian Republic of)':'Venezuela','Dominican Republic':'República Dominicana','Uruguay':'Uruguay','Paraguay':'Paraguay','Bahamas (The)':'Bahamas','Nicaragua':'Nicaragua'}
M={'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
DATE=re.compile(r'^(\d{1,2}) ([A-Z][a-z]+) (\d{4})$')
def strip(s):
    s=re.sub(r'<[^>]+>',' ',s);s=re.sub(r'&nbsp;',' ',s);return re.sub(r'\s+',' ',s).strip()
def clasif(s):
    s=s.lower()
    if re.search(r'terminat|lifted|cessation|repeal|ceased|no longer|end of the state',s): return 'fin/levantamiento'
    if re.search(r'extension|extend|prorog|prolong|renew',s): return 'extensión'
    if re.search(r'proclamat|declar|decree|impos|state of (siege|emergency)|martial|availed itself',s): return 'declaración'
    return 'otro'
def regimen(s):
    s=s.lower()
    if 'martial law' in s: return 'ley marcial'
    if 'state of siege' in s or 'state siege' in s or 'estado de sitio' in s: return 'estado de sitio'
    if 'state of catastrophe' in s: return 'estado de catástrofe'
    if 'internal commotion' in s or 'state of disturbance' in s or 'conmoci' in s: return 'conmoción interior'
    if 'state of alarm' in s: return 'estado de alarma'
    if 'state of emergency' in s or 'health emergency' in s or 'estado de emergencia' in s: return 'estado de emergencia'
    if 'state of exception' in s or 'estado de excepci' in s: return 'estado de excepción'
    if 'constitutional guarantees' in s or 'suspension of guarantees' in s or 'suspension of the guarantees' in s: return 'suspensión de garantías'
    return ''
def cn(s):
    m=re.search(r'(C\.N\.\d+\.\d{4})',s);return m.group(1) if m else ''
def cn_url(ref):
    m=re.match(r'C\.N\.(\d+)\.(\d{4})',ref)
    if not m: return ''
    n,y=m.groups()
    return f"https://treaties.un.org/doc/Publication/CN/{y}/CN.{n}.{y}-Eng.pdf"

notifs=re.findall(r'divNotificationText"[^>]*>(.*?)</div>',html,re.S)
rows=[]
for body in notifs:
    cm=re.search(r"<p class='invisible'>([^<]+)</p>",body)
    if not cm: continue
    country=cm.group(1).strip()
    if country not in OEA: continue
    parts=re.split(r'<p align=?["\']?right["\']?>\s*([^<]+?)\s*</p>',body)
    for k in range(1,len(parts),2):
        dm=DATE.match(parts[k].strip())
        if not dm or dm.group(2) not in M: continue
        d,mo,y=dm.groups()
        seg=strip(parts[k+1] if k+1<len(parts) else '')
        rows.append({'pais':ESP.get(country,country),'pais_en':country,
            'fecha':f"{int(y):04d}-{M[mo]:02d}-{int(d):02d}",'anio':y,
            'tipo_evento':clasif(seg),'regimen':regimen(seg),'regimen_origen':('directo' if regimen(seg) else ''),
            'cn_ref':cn(seg),'url_pdf':cn_url(cn(seg)),'texto':seg[:1500],
            'fuente':'ONU_PIDCP_art4','snippet':seg[:220]})
rows.sort(key=lambda r:r['fecha'])
# Propagación: una prórroga/terminación sin régimen hereda el de la declaración previa del mismo país
last={}
for r in rows:
    if r['regimen']:
        last[r['pais']]=r['regimen']
    elif r['pais'] in last:
        r['regimen']=last[r['pais']]; r['regimen_origen']='heredado'
cols=['pais','pais_en','fecha','anio','tipo_evento','regimen','regimen_origen','cn_ref','url_pdf','fuente','texto','snippet']
with open('un_derogaciones_art4.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
from collections import Counter
print(f"TOTAL notificaciones (OEA): {len(rows)} | rango {rows[0]['fecha']} → {rows[-1]['fecha']}")
print("Por país:",dict(Counter(r['pais'] for r in rows).most_common()))
print("Tipo:",dict(Counter(r['tipo_evento'] for r in rows)))
print("Régimen:",dict(Counter(r['regimen'] for r in rows if r['regimen']).most_common()))
print("Por década:",dict(sorted(Counter(r['fecha'][:3]+'0s' for r in rows).items())))
