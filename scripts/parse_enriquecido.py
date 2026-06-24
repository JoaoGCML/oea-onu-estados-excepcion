#!/usr/bin/env python3
"""Parsea los txt OCR -> notif_oea_art27_enriquecido.csv (rápido, sin red, resumible)."""
import csv,os,re
TXTDIR="txt"
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
    return m.group(1) if m else ""
def p_alcance(t):
    if re.search(r'(en )?todo el territorio (nacional)?',t,re.I): return "nacional"
    m=re.search(r'(?:en (?:los|las) (?:departamentos?|provincias?|regiones?|municipios?) de\s+)([A-ZÁÉÍÓÚ][^\.\n]{3,80})',t)
    return ("subnacional: "+m.group(1).strip()) if m else ""
def p_derechos(t):
    m=re.search(r'derechos?\s+(?:a (?:la|las|los)?\s*)?([^\.]{5,160})',t,re.I)
    return re.sub(r'\s+',' ',m.group(1)).strip()[:160] if m else ""

rows=list(csv.DictReader(open('notif_oea_art27.csv',encoding='utf-8')))
extra=['decreto','tipo','base_legal','causa','plazo_dias','alcance','derechos','ocr_chars']
for r in rows:
    rid=r['url_pdf'].rsplit('/',1)[-1].replace('.pdf','') if r['url_pdf'] else ''
    tf=os.path.join(TXTDIR,rid+'.txt')
    t=open(tf,encoding='utf-8').read() if rid and os.path.exists(tf) else ''
    r.update({'decreto':p_decreto(t),'tipo':p_tipo(t),'base_legal':p_articulo(t),'causa':p_causa(t),
        'plazo_dias':p_plazo(t),'alcance':p_alcance(t),'derechos':p_derechos(t),'ocr_chars':len(t)})
cols=list(rows[0].keys())
with open('notif_oea_art27_enriquecido.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
con=sum(1 for r in rows if int(r['ocr_chars'])>0)
print(f"Enriquecido: {len(rows)} filas | con texto OCR: {con} | con tipo: {sum(1 for r in rows if r['tipo'])}")
