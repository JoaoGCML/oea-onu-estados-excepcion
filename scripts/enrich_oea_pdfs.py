#!/usr/bin/env python3
"""Descarga + OCR + parseo de los PDFs de notificaciones OEA Art.27.
Resumible (salta lo ya hecho). Salida: notif_oea_art27_enriquecido.csv
Uso: python3 enrich_oea_pdfs.py
"""
import csv, os, re, subprocess, tempfile, time, sys, glob

LIST="https://www.oas.org/es/sla/ddi/tratados_multilaterales_interamericanos_suspencion_garantias.asp"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
COOK="cookies.txt"; TXTDIR="txt"; NPAGES=5; DPI=200
os.makedirs(TXTDIR,exist_ok=True)

def prime():
    subprocess.run(["curl","-s","-c",COOK,"-A",UA,"-H","Accept-Language: es-ES,es;q=0.9",LIST,"-o","/dev/null"],timeout=60)

def dl(url,dst):
    url=url.replace("http://","https://")
    cmd=["curl","-s","-L","-b",COOK,"-c",COOK,"-A",UA,
        "-H","Accept: text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
        "-H","Accept-Language: es-ES,es;q=0.9","-H",f"Referer: {LIST}",
        "-H","Sec-Fetch-Dest: document","-H","Sec-Fetch-Mode: navigate",
        "-H","Sec-Fetch-Site: same-origin","-H","Upgrade-Insecure-Requests: 1",
        url,"-o",dst]
    subprocess.run(cmd,timeout=120)
    return os.path.exists(dst) and os.path.getsize(dst)>20000 and open(dst,'rb').read(4)==b'%PDF'

def ocr(pdf):
    d=tempfile.mkdtemp(); base=os.path.join(d,"p")
    subprocess.run(["pdftoppm","-r",str(DPI),"-f","1","-l",str(NPAGES),"-png",pdf,base],
                   stderr=subprocess.DEVNULL,timeout=180)
    txt=[]
    for png in sorted(glob.glob(base+"*.png")):
        r=subprocess.run(["tesseract",png,"-","-l","spa"],capture_output=True,timeout=120)
        txt.append(r.stdout.decode('utf-8','ignore'))
        os.remove(png)
    try: os.rmdir(d)
    except: pass
    return "\n".join(txt)

# ---- parsers ----
def p_decreto(t):
    m=re.search(r'Decreto\s+(?:Supremo|Ejecutivo|Legislativo|de Urgencia)?\s*(?:N[°ºo*\.]*\s*)([0-9]{1,5}[\-/]?[0-9]{0,4})',t,re.I)
    return m.group(0).strip().replace('\n',' ') if m else ""
def p_tipo(t):
    for pat,lab in [(r'estado de excepci[óo]n','estado de excepción'),(r'estado de emergencia','estado de emergencia'),
        (r'estado de sitio','estado de sitio'),(r'estado de cat[áa]strofe','estado de catástrofe'),
        (r'conmoci[óo]n interior','conmoción interior'),(r'estado de calamidad','estado de calamidad'),
        (r'suspensi[óo]n de garant[íi]as','suspensión de garantías'),(r'state of (public )?emergency','state of emergency'),
        (r'estado de prevenci[óo]n','estado de prevención'),(r'r[ée]gimen de excepci[óo]n','régimen de excepción')]:
        if re.search(pat,t,re.I): return lab
    return ""
def p_articulo(t):
    m=re.search(r'[Aa]rt[íi]culo\s+(\d{1,3})\s+de\s+la\s+Constituci[óo]n',t)
    return f"Art. {m.group(1)} Constitución" if m else ""
def p_causa(t):
    c=[]
    for pat,lab in [(r'desastre natural|emergencia sanitaria|pandemi|covid|sismo|terremoto|inundaci|lluvias','desastre/salud'),
        (r'narcotr[áa]fico|crimen organizado|inseguridad|delincuencia|bandas|violencia','seguridad/crimen'),
        (r'conmoci[óo]n (interna|interior)|disturbios|protesta|conflictividad','orden público'),
        (r'peligro (para la seguridad|externo)|amenaza externa|guerra','seguridad estado')]:
        if re.search(pat,t,re.I): c.append(lab)
    return "; ".join(dict.fromkeys(c))
def p_plazo(t):
    m=re.search(r'(?:por (?:un )?(?:plazo|t[ée]rmino|per[íi]odo) de\s*)(\d{1,3})\s*d[íi]as',t,re.I)
    return int(m.group(1)) if m else ""
def p_alcance(t):
    if re.search(r'(en )?todo el territorio (nacional)?',t,re.I): return "nacional"
    m=re.search(r'(?:en (?:los|las) (?:departamentos?|provincias?|regiones?|municipios?) de\s+)([A-ZÁÉÍÓÚ][^\.\n]{3,80})',t)
    return ("subnacional: "+m.group(1).strip()) if m else ""
def p_derechos(t):
    m=re.search(r'derechos?\s+(?:a (?:la|las|los)?\s*)?([^\.]{5,160})',t,re.I)
    return re.sub(r'\s+',' ',m.group(1)).strip()[:160] if m else ""

rows=list(csv.DictReader(open('notif_oea_art27.csv',encoding='utf-8')))
prime()
done=0; ok=0; fail=0; t0=time.time()
out_rows=[]
for i,r in enumerate(rows):
    rid=(r['url_pdf'].rsplit('/',1)[-1] if r['url_pdf'] else f"NOPDF_{i}").replace('.pdf','')
    tf=os.path.join(TXTDIR,rid+".txt")
    text=""
    if os.path.exists(tf):
        text=open(tf,encoding='utf-8').read()
    elif r['url_pdf']:
        tmp=tempfile.mktemp(suffix='.pdf')
        good=dl(r['url_pdf'],tmp)
        if not good:  # maybe blocked -> reprime + retry
            time.sleep(4); prime(); time.sleep(1); good=dl(r['url_pdf'],tmp)
        if good:
            try: text=ocr(tmp); open(tf,'w',encoding='utf-8').write(text); ok+=1
            except Exception as e: fail+=1; text=""
        else: fail+=1
        if os.path.exists(tmp): os.remove(tmp)
        time.sleep(0.6)
    nr=dict(r)
    nr.update({'decreto':p_decreto(text),'tipo':p_tipo(text),'base_legal':p_articulo(text),
        'causa':p_causa(text),'plazo_dias':p_plazo(text),'alcance':p_alcance(text),
        'derechos':p_derechos(text),'ocr_chars':len(text)})
    out_rows.append(nr)
    done+=1
    if done%25==0:
        el=time.time()-t0
        print(f"[{done}/{len(rows)}] ok={ok} fail={fail} | {el:.0f}s | {rid[:40]}",flush=True)
        # incremental save
        cols=list(rows[0].keys())+['decreto','tipo','base_legal','causa','plazo_dias','alcance','derechos','ocr_chars']
        with open('notif_oea_art27_enriquecido.csv','w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(out_rows)

cols=list(rows[0].keys())+['decreto','tipo','base_legal','causa','plazo_dias','alcance','derechos','ocr_chars']
with open('notif_oea_art27_enriquecido.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(out_rows)
print(f"\nDONE total={done} ok_ocr={ok} fail={fail} elapsed={time.time()-t0:.0f}s -> notif_oea_art27_enriquecido.csv",flush=True)
