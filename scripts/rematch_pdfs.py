#!/usr/bin/env python3
"""Re-empareja PDFs a entradas por orden posicional dentro de cada país/página (robusto).
Regenera notif_oea_art27.csv con url_pdf correcto."""
import urllib.request,http.cookiejar,ssl,re,csv,unicodedata
ctx=ssl.create_default_context();ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),urllib.request.HTTPSHandler(context=ctx))
op.addheaders=[('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]
BASE="https://www.oas.org/es/sla/ddi/"
PAGES=["tratados_multilaterales_interamericanos_suspencion_garantias.asp"]+[f"tratados_multilaterales_interamericanos_suspencion_garantias_{y}.asp" for y in range(2014,2025)]
MES={'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'setiembre':9,'octubre':10,'noviembre':11,'diciembre':12}
def deacc(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
def cc(s):
    s=deacc(s).lower()
    if 'salvador' in s:return 'el salvador'
    if 'dominic' in s:return 'republica dominicana'
    if 'venez' in s:return 'venezuela'
    if 'surinam' in s:return 'suriname'
    s=re.sub(r'\b(la|el|de|republica|bolivariana|plurinacional|estado|del)\b','',s)
    return re.sub(r'\s+',' ',s).strip()
CANON={'el salvador':'El Salvador','republica dominicana':'República Dominicana','peru':'Perú',
 'panama':'Panamá','mexico':'México','venezuela':'Venezuela','suriname':'Suriname',
 'chile':'Chile','ecuador':'Ecuador','guatemala':'Guatemala','paraguay':'Paraguay',
 'colombia':'Colombia','argentina':'Argentina','bolivia':'Bolivia','honduras':'Honduras',
 'jamaica':'Jamaica','uruguay':'Uruguay'}
ENTRY=re.compile(r'El\s+(\d{1,2})\s+de\s+([a-zA-Záéíóúñ]+)\s+de\s+(\d{4})\s*,?\s*la\s+Secretar[íi]a\s+General\s+recibi[óo]\s+por\s+parte\s+de\s+la\s+Misi[óo]n\s+Permanente\s+de\s+(.+?)\s+ante\s+la\s+OEA',re.I)
NOTA=re.compile(r'Nota\s+No\.?\s*([A-Za-z0-9\-/\. ]+?)\s*(?:,|junto|en cumplimiento|y su)',re.I)

rows=[]
for p in PAGES:
    try: html=op.open(BASE+p,timeout=40).read().decode('utf-8','ignore')
    except Exception as e: print("skip",p,e);continue
    pdfs=re.findall(r'href="([^"]+\.pdf)"',html,re.I)
    # group pdfs by country in filename order
    pdf_by_c={}
    for u in pdfs:
        fn=u.rsplit('/',1)[-1]
        m=re.search(r'suspencion_garantias_(.+?)_(?:nota|No)',fn,re.I)
        c=cc(m.group(1).replace('_',' ')) if m else ''
        pdf_by_c.setdefault(c,[]).append(u)
    txt=re.sub(r'&nbsp;',' ',html);txt=re.sub(r'<[^>]+>',' ',txt);txt=re.sub(r'\s+',' ',txt)
    anchors=[m for m in ENTRY.finditer(txt)]
    ent_by_c={}
    page_entries=[]
    for i,m in enumerate(anchors):
        d,mes,y,pais=m.groups()
        seg=txt[m.start():(anchors[i+1].start() if i+1<len(anchors) else m.start()+500)]
        nm=NOTA.search(seg)
        mnum=MES.get(mes.lower(),0)
        iso=f"{int(y):04d}-{mnum:02d}-{int(d):02d}" if mnum else f"{y}-00-{int(d):02d}"
        c=cc(pais)
        e={'pais':CANON.get(c,pais.strip()),'fecha':iso,'anio':y,'nota_no':(nm.group(1).strip() if nm else ''),'_c':c}
        ent_by_c.setdefault(c,[]).append(e)
    # positional pairing within each country
    for c,ents in ent_by_c.items():
        plist=pdf_by_c.get(c,[])
        for j,e in enumerate(ents):
            e['url_pdf']=plist[j] if j<len(plist) else ''
            e.pop('_c');rows.append(e)
    print(f"{p[-12:]:14s} entries={sum(len(v) for v in ent_by_c.values())} pdfs={len(pdfs)}")

# dedup
seen=set();final=[]
for r in sorted(rows,key=lambda r:r['fecha']):
    k=(r['pais'],r['fecha'],r['nota_no'])
    if k in seen:continue
    seen.add(k)
    r['fuente']='notif_oea_art27';r['url_pagina']=''
    final.append(r)
cols=['pais','fecha','anio','nota_no','fuente','url_pagina','url_pdf']
with open('notif_oea_art27.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
    for r in final: w.writerow({k:r.get(k,'') for k in cols})
uniq=len(set(r['url_pdf'] for r in final if r['url_pdf']))
print(f"\nTOTAL filas: {len(final)} | con PDF: {sum(1 for r in final if r['url_pdf'])} | PDFs únicos: {uniq}")
