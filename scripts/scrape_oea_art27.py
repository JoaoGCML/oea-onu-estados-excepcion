#!/usr/bin/env python3
"""Scrape OEA Art.27 CADH (suspensión de garantías) notifications -> notif_oea_art27.csv
Capa A+ del registro de estados de excepción para países OEA. Fuente:
oas.org/es/sla/ddi/tratados_multilaterales_interamericanos_suspencion_garantias[_YYYY].asp
"""
import urllib.request, http.cookiejar, re, ssl, csv, time

BASE="https://www.oas.org/es/sla/ddi/"
MAIN="tratados_multilaterales_interamericanos_suspencion_garantias.asp"
YEARS=list(range(2013,2026))  # archive pages _2013.._2024 (+ main covers latest)
PAGES=[MAIN]+[f"tratados_multilaterales_interamericanos_suspencion_garantias_{y}.asp" for y in YEARS]

MESES={'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,
       'agosto':8,'septiembre':9,'setiembre':9,'octubre':10,'noviembre':11,'diciembre':12}

ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
cj=http.cookiejar.CookieJar()
op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders=[('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')]

def fetch(url):
    for _ in range(3):
        try: return op.open(url, timeout=40).read().decode('utf-8','ignore')
        except Exception as e: time.sleep(2); last=e
    print("  FAIL", url, last); return ""

# entry anchor: "El <d> de <mes> de <yyyy> , la Secretaría General recibió por parte de la Misión Permanente de <Pais> ante la OEA ... Nota No. <n> ..."
ENTRY=re.compile(
 r'El\s+(\d{1,2})\s+de\s+([a-zA-Záéíóúñ]+)\s+de\s+(\d{4})\s*,?\s*'
 r'la\s+Secretar[íi]a\s+General\s+recibi[óo]\s+por\s+parte\s+de\s+la\s+Misi[óo]n\s+Permanente\s+de\s+'
 r'(.+?)\s+ante\s+la\s+OEA',re.I)
NOTA=re.compile(r'Nota\s+No\.?\s*([^,\.]+?)\s*(?:,|junto|\.|en cumplimiento)',re.I)

rows=[]
seen=set()
for p in PAGES:
    url=BASE+p
    html=fetch(url)
    if not html: continue
    pdfs=re.findall(r'href="([^"]+\.pdf)"',html,re.I)
    txt=re.sub(r'&nbsp;',' ',html); txt=re.sub(r'<[^>]+>',' ',txt); txt=re.sub(r'\s+',' ',txt)
    # split into entries by anchor positions
    anchors=[m.start() for m in ENTRY.finditer(txt)]
    page_rows=0
    for i,m in enumerate(ENTRY.finditer(txt)):
        d,mes,y,pais=m.groups()
        seg=txt[m.start(): (anchors[i+1] if i+1<len(anchors) else m.start()+600)]
        nm=NOTA.search(seg)
        nota=nm.group(1).strip() if nm else ""
        mes=mes.lower().strip()
        mnum=MESES.get(mes,0)
        try: iso=f"{int(y):04d}-{mnum:02d}-{int(d):02d}" if mnum else f"{y}-??-{int(d):02d}"
        except: iso=f"{y}-{mes}-{d}"
        pais=re.sub(r'\s+',' ',pais).strip().strip('.,')
        # match pdf by normalized nota or country in filename
        norm=lambda s: re.sub(r'[^a-z0-9]','',s.lower())
        pdf=""
        for u in pdfs:
            fn=u.rsplit('/',1)[-1]
            if nota and norm(nota) and norm(nota)[-6:] in norm(fn):
                pdf=u; break
        if not pdf:
            for u in pdfs:
                if norm(pais) and norm(pais) in norm(u.rsplit('/',1)[-1]):
                    pdf=u  # may overwrite; best-effort
        key=(pais,iso,nota)
        if key in seen: continue
        seen.add(key)
        rows.append({'pais':pais,'fecha':iso,'anio':y,'nota_no':nota,
                     'fuente':'notif_oea_art27','url_pagina':url,'url_pdf':pdf})
        page_rows+=1
    print(f"  {p:70s} entries={page_rows} pdfs={len(pdfs)}")

rows.sort(key=lambda r:(r['fecha']))
out="notif_oea_art27.csv"
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['pais','fecha','anio','nota_no','fuente','url_pagina','url_pdf'])
    w.writeheader(); w.writerows(rows)
print(f"\nTOTAL notificaciones: {len(rows)} -> {out}")
from collections import Counter
print("Por país:", dict(Counter(r['pais'] for r in rows).most_common()))
print("Por año :", dict(sorted(Counter(r['anio'] for r in rows).items())))
