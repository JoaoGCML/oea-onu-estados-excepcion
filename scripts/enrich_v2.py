#!/usr/bin/env python3
"""Enriquecimiento PARALELO: descarga+OCR concurrente (5 workers), resumible.
Descarga a /tmp, guarda solo el .txt. Luego parsea -> notif_oea_art27_enriquecido.csv"""
import csv,os,re,subprocess,tempfile,glob,time
from concurrent.futures import ThreadPoolExecutor,as_completed
LIST="https://www.oas.org/es/sla/ddi/tratados_multilaterales_interamericanos_suspencion_garantias.asp"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
COOK="cookies.txt";TXTDIR="txt";NPAGES=4;DPI=150;WORKERS=5
os.makedirs(TXTDIR,exist_ok=True)
subprocess.run(["curl","-s","-c",COOK,"-A",UA,LIST,"-o","/dev/null"],timeout=60)  # prime once

def proc(row):
    u=row['url_pdf']
    if not u: return ('nopdf',row)
    rid=u.rsplit('/',1)[-1].replace('.pdf','')
    tf=os.path.join(TXTDIR,rid+".txt")
    if os.path.exists(tf): return ('cache',row)
    pdf=tempfile.mktemp(suffix='.pdf')
    cmd=["curl","-s","-L","-b",COOK,"-A",UA,"-H","Accept: application/pdf,*/*;q=0.8",
        "-H",f"Referer: {LIST}","-H","Sec-Fetch-Dest: document","-H","Sec-Fetch-Mode: navigate",
        "-H","Sec-Fetch-Site: same-origin",u.replace("http://","https://"),"-o",pdf]
    subprocess.run(cmd,timeout=120)
    ok=os.path.exists(pdf) and os.path.getsize(pdf)>20000 and open(pdf,'rb').read(4)==b'%PDF'
    if not ok:
        if os.path.exists(pdf):os.remove(pdf)
        return ('fail',row)
    d=tempfile.mkdtemp();base=os.path.join(d,"p")
    subprocess.run(["pdftoppm","-r",str(DPI),"-f","1","-l",str(NPAGES),"-png",pdf,base],stderr=subprocess.DEVNULL,timeout=180)
    parts=[]
    for png in sorted(glob.glob(base+"*.png")):
        r=subprocess.run(["tesseract",png,"-","-l","spa"],capture_output=True,timeout=120)
        parts.append(r.stdout.decode('utf-8','ignore'));os.remove(png)
    os.remove(pdf)
    try:os.rmdir(d)
    except:pass
    open(tf,'w',encoding='utf-8').write("\n".join(parts))
    return ('ocr',row)

rows=list(csv.DictReader(open('notif_oea_art27.csv',encoding='utf-8')))
todo=[r for r in rows if r['url_pdf'] and not os.path.exists(os.path.join(TXTDIR,r['url_pdf'].rsplit('/',1)[-1].replace('.pdf','')))]
print(f"Total filas {len(rows)} | faltan OCR: {len(todo)} | workers={WORKERS}",flush=True)
t0=time.time();done=0;c={'ocr':0,'cache':0,'fail':0,'nopdf':0}
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    for fut in as_completed([ex.submit(proc,r) for r in todo]):
        st,_=fut.result();c[st]=c.get(st,0)+1;done+=1
        if done%25==0: print(f"[{done}/{len(todo)}] ocr={c['ocr']} fail={c['fail']} | {time.time()-t0:.0f}s",flush=True)
print(f"OCR fase done: {c} | {time.time()-t0:.0f}s",flush=True)
