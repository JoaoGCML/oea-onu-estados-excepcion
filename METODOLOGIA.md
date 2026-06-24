# Estrategia — Declaratorias de estado de excepción / emergencia / ley marcial · Países OEA

Complemento operativo de [[FUENTES_5_EVENTOS]] (categoría 3) y [[CINCO_EVENTOS_PANEL]]. Objetivo: construir un registro fechado y verificable de declaratorias de régimen extraordinario para los **35 miembros de la OEA**, como target de la categoría 3 del panel.

**Decisiones de alcance (2026-06-23):**
- **Horizonte: 1950 → presente.** Pre-2000 es mayormente grano anual (Bjørnskov, notificaciones ONU); 2000→ permite mensual.
- **Solo declaratorias NACIONALES.** Se excluyen estados de excepción subnacionales (regiones/provincias). Se documenta la decisión para no leer ausencia subnacional como cero.
- **Orden de implementación: (1) Capa A+ notificaciones OEA/ONU → (2) kit de gacetas + lexicón Tier A.**

---

## 0. El insight OEA: registros supranacionales de notificación

A diferencia del resto del mundo, los miembros de la OEA tienen **dos depositarios oficiales** donde los Estados están *obligados* a notificar cuando suspenden garantías. Son fuentes primarias, fechadas y con autoridad — el "acto verificable" que pide la lógica del Test.

| Registro | Base legal | Qué notifica | Cobertura |
|---|---|---|---|
| **OEA — Secretaría General** | **Art. 27.3 CADH** (suspensión de garantías) | disposiciones suspendidas, motivos y **fecha de término** | Estados parte CADH (~23-25) |
| **ONU — Treaty Collection (C.N. depositary notifications)** | **Art. 4.3 PIDCP** (derogations) | derogaciones con fecha inicio/fin y artículos | Estados parte PIDCP (casi todos OEA, incl. EEUU/Canadá/Caribe) |

⚠️ **Caveat que define el diseño:** no todos los OEA son parte de la CADH (EEUU, Canadá y varios del Caribe nunca la ratificaron; Trinidad y Venezuela la denunciaron). Para esos, el ancla es PIDCP-Art.4 + registro doméstico (EEUU: *National Emergencies Act* → Federal Register; Canadá: *Emergencies Act*).

### Hallazgos de validación (2026-06-23) — registros localizados

**OEA Art.27** — página oficial del Depto. de Derecho Internacional:
`http://www.oas.org/es/sla/ddi/tratados_multilaterales_interamericanos_suspencion_garantias.asp`
- Cobertura digital: **~2013 → presente** (archivo por año; pre-2013 no está aquí).
- Organización: cronológica inversa, **PDF por notificación**, con país + fecha + Nº de nota verbal. Sin motivo explícito en el listado (está en el PDF).
- Notificadores observados: Perú (mayoría), El Salvador, Colombia, Ecuador, Chile, Guatemala, Bolivia, Haití, Panamá.

**ONU PIDCP Art.4** — depositario UN Treaty Collection (C.N. notifications, MTDSG cap. IV.4) + tracking del CCPR Centre.
- Históricamente **solo ~13 Estados** han notificado derogaciones (de ellos, OEA: Chile, Colombia, Ecuador, El Salvador, Guatemala, Perú).

### ⚠️ Limitación crítica: alta precisión, baja cobertura (seed ≠ censo)
Ambos registros capturan **solo las suspensiones formalmente notificadas**, no todas las declaratorias. Casi todos los Estados que decretan emergencias **no notifican** (la propia ONU lo constata: "casi todos los países toman medidas excepcionales, muy pocos notifican"). Implicación de diseño:
- Capa A+ = **lista-semilla de positivos confirmados** (úsala como verdad de positivos y para anclar fechas), **NO como censo ni como fuente de cero-verdadero**.
- La **cobertura (recall)** la dan las gacetas (Capa B) + datasets estructurados país-año (Capa A: Bjørnskov, Hafner-Burton, OxCGRT/COVID).
- Ausencia de notificación ⇏ ausencia de emergencia → esas celdas son `MISSING`, nunca `0`.
- Pre-2013 (relevante para horizonte 1950→): la OEA digital no cubre; el peso recae en Bjørnskov/Hafner-Burton (anual) + gacetas históricas.

---

## 1. Definición del target (qué cuenta)

Acto primario, formal y datable que activa un régimen constitucional extraordinario. No la noticia ni la "tensión": el decreto/ley/proclamación.

- **Tipos (sinónimos del mismo objeto):** estado de excepción / emergencia / sitio / catástrofe / conmoción interior / defensa / calamidade pública / suspensión de garantías / *state of (public) emergency* / *martial law*.
- **Atributos:** alcance (nacional), causa (seguridad / desastre / salud / económica), base constitucional (artículo), **fecha inicio**, **fecha fin**, **renovaciones/prórrogas**, levantamiento.
- **Onset vs. en-vigor:** codificar **ambos** (mes de declaración/renovación = evento; mes con régimen activo = estado), desde intervalos inicio→fin. Es una *duración*, no un instante.

---

## 2. Universo OEA segmentado por tier de acceso

35 Estados miembro. La extracción no es uniforme:

| Tier | Países | Gaceta | Lexicón |
|---|---|---|---|
| **A — gaceta digital abierta ES/PT** | Perú (*El Peruano*), Colombia (*Diario Oficial*), México (*DOF*), Chile (*Diario Oficial*), Argentina (*Boletín Oficial*), Ecuador (*Registro Oficial*), Brasil (*DOU*), Bolivia, El Salvador, Costa Rica | excelente | conocido |
| **B — gaceta parcial / PDF** | Guatemala, Honduras, Nicaragua, Panamá, Paraguay, Uruguay, R. Dominicana, Venezuela, Haití | irregular | conocido |
| **C — Caribe anglófono / micro-Estados** | Jamaica, Trinidad, Bahamas, Barbados, Guyana, Belice, Antigua, Dominica, Granada, St. Kitts, St. Lucia, St. Vincent, Suriname | *Statutory Instruments*/*Gazettes* dispersos | "state of (public) emergency", *Emergency Powers Act* |
| **D — registro propio robusto** | EEUU (Federal Register / NEA), Canadá (Emergencies Act) | excelente | distinto |

---

## 3. Arquitectura por capas

```
Capa A+ (autoritativa): notificaciones OEA Art.27 + ONU PIDCP Art.4
        → lista maestra fechada de suspensiones formales. EMPEZAR AQUÍ.
Capa A  (esqueleto estructurado país-año, cero-verdadero histórico):
        Bjørnskov & Voigt declaraciones (de facto ~1949-2017) ·
        Hafner-Burton/Helfer/Fariss · OxCGRT/ICNL/CoronaNet (COVID 2020-22)
Capa A* (de jure, FEATURE — NO target): INEP Bjørnskov & Voigt + Constitute/CCP
Capa B  (acto primario fechado): GACETA OFICIAL por país ← detalle/autoridad
Capa C  (descubrimiento + relleno): GDELT, Keesing's, prensa local, ICNL tracker
```

**Regla de confianza por celda:** notificación/gaceta = autoridad; noticia sin gaceta = "sospecha" (gap de acceso → revisión manual); loguear la fuente de cada celda.

**Cero verdadero vs MISSING:** mes-país = 0 solo si (a) capa autoritativa cubre ese período y no hay acto, o (b) gaceta accesible sin decreto. Donde no hay cobertura → `MISSING`, no 0 (lección AIJ: un modelo con MISSING-como-0 aprende cobertura, no riesgo).

---

## 4. Kit operativo por país (se construye una vez)

**(a) `gacetas_oea.csv`** — inventario de gacetas:
`país · nombre_gaceta · URL · método_acceso (API/scrape/PDF/paywall) · años_cubiertos · ¿buscable?`

**(b) `lexico_excepcion.csv`** — lexicón legal (un keyword genérico falla por terminología constitucional):
`país · término(s) constitucional(es) · instrumento (decreto supremo/ejecutivo/proclamation/SI) · artículo · idioma`

Terminología por país (base, ampliar): Perú/El Salvador "régimen/estado de excepción/emergencia"; Chile "estado de catástrofe/sitio/emergencia/asamblea"; Colombia "conmoción interior / emergencia económica-social-ecológica"; Ecuador/Bolivia/Venezuela "estado de excepción"; Brasil "estado de defesa / sítio / calamidade pública"; México "suspensión de garantías (art. 29) / declaratoria de emergencia"; Argentina "estado de sitio / emergencia pública"; Caribe anglófono "state of (public) emergency".

---

## 5. Esquema del registro de declaratoria

```
country · instrument_id (Nº decreto/ley) · type · scope (=nacional) · cause
· legal_basis (art.) · date_start · date_end · renewals[] · lifting_date
· source_layer (notif_OEA / notif_ONU / gaceta / noticia) · source_url · confidence
```

---

## 6. Fases

1. **Capa A+** — bajar registro OEA Art.27 + ONU C.N. derogations → lista maestra fechada (mayor retorno, OEA-específica). ← arranque.
2. **Kit gacetas + lexicón Tier A** (10 países ES/PT) y confirmar contra Capa A+.
3. **Validar con COVID 2020-2022** (todos declararon; OxCGRT/ICNL = verdad).
4. **Densificar a gaceta** Tier A.
5. **Capa C** (GDELT/noticias) para descubrir y cubrir Tier B/C/D.
6. **Loguear cero-verdadero vs MISSING** por país-período.

---

## 7. Estado de ejecución

- ✅ **Capa A+ OEA scrapeada** → `estados_excepcion/notif_oea_art27.csv` (script `estados_excepcion/scrape_oea_art27.py`, reproducible). **538 notificaciones, 16 países, 2014–2026** (501/538 con PDF). Por país: Perú 195, Ecuador 56, El Salvador 50, Chile 37, Rep. Dominicana 37, Guatemala 36, Paraguay 34, Colombia 33, Argentina 31, Panamá 10, Bolivia 8, Honduras 6, Jamaica 2, Suriname/Venezuela/Uruguay 1. Pico 2020 (130 = COVID).
  - Confirmado: la OEA digital arranca en **2014** (no hay página 2013; 2025 está en la principal).
  - Recordatorio de uso: son **positivos confirmados** (úsense para anclar fechas/positivos), NO censo. La mayoría (Perú) refleja la práctica peruana de notificar cada prórroga.
- ✅ **Emparejamiento PDF corregido** → 531 PDFs únicos (bug previo: se reusaba 1 PDF para muchas filas; fix = pareo posicional por país en `rematch_pdfs.py`).
- ✅ **Enriquecimiento por OCR** (`enrich_v2.py` paralelo + `parse_enriquecido.py`) → `notif_oea_art27_enriquecido.csv`. **509/539 filas con PDF leído (OCR tesseract spa)**, 448 con tipo clasificado. Campos extraídos: `tipo · decreto · base_legal · causa · plazo_dias · alcance · derechos`.
  - ⚠️ Descarga de PDFs: la OEA bloquea hotlinking (302→wearesorry.htm); se evade con headers de navegador completos (Sec-Fetch-*) + cookie de sesión. PDFs son **escaneados** → requieren OCR.
  - **Tipos:** estado de emergencia 266 · estado de excepción 100 · régimen de excepción 47 · estado de sitio 12 · estado de calamidad 12 · estado de prevención 5 · conmoción interior 4.
  - **Causas (OCR):** seguridad/crimen, desastre/salud, orden público, seguridad estado.
- ✅ **Monitor visual** → `estados_excepcion/monitor_estados_excepcion.html` (autónomo; desgloses por país/tipo/causa/año, semáforo de recencia, tabla filtrable con enlace a cada PDF). Regenerar: `python3 build_monitor.py`.
- ✅ **ONU Art.4 PIDCP derogaciones scrapeadas** → `estados_excepcion/un_derogaciones_art4.csv` (script `parse_un_derogaciones.py` desde `un_iccpr.html` de UNTC, parseo por estructura HTML: país=`<p class=invisible>`, fecha=`<p align=right>`). **776 notificaciones de países OEA, 1976→2026.** Por país: Perú 473, Guatemala 91, Ecuador 85, Colombia 25, Chile 21, Venezuela 18, El Salvador 17, Paraguay 10, Trinidad y Tobago 9, Jamaica 8, Argentina 7, Rep. Dom. 6, Panamá/Bolivia 2, Uruguay/Suriname 1. Régimen: emergencia 601, sitio 22, ley marcial 2. Tipo: declaración 273, extensión 450, fin 41. EEUU/Canadá NO aparecen (nunca derogaron del PIDCP).
  - **Valor recall:** extiende el registro a **1976** (vs OEA 2014) y añade no/ex-CADH (Venezuela, Trinidad, Jamaica, Uruguay, Suriname).
  - ⚠️ Gotcha resuelto: el texto plano daba 3968 falsos (capturaba fechas citadas en el cuerpo); la estructura HTML (`<p align=right>`) aísla solo las fechas de recepción.
- ✅ **Registro unificado** → `registro_excepcion_unificado.csv` (OEA+ONU, esquema común, **1315 registros, 17 países, 1976→2026**) + **monitor combinado** con filtro de fuente y barras OEA/ONU.
- ⚠️ **Duplicación OEA↔ONU (validado):** son canales separados (Art.27 CADH vs Art.4 PIDCP) pero notifican el MISMO hecho. En 2014→, **~258/539 registros OEA (~48%) tienen gemelo ONU (±10d)**; total **709/1315 filas marcadas `dup_cross`**. Los 1315 NO son 1315 emergencias distintas. (Pre-2014 no hay solape: solo ONU.) Perú = solape extremo (notifica todo a ambos); El Salvador/Chile/Colombia/Argentina = casi solo OEA.
- ✅ **Panel deduplicado `panel_excepcion_pais_mes.csv`** (el target del modelo): colapsa ambas fuentes a país×mes binario → **532 celdas país-mes con excepción, 1976-09→2026-06**. Confirmación cruzada: **171 por ambas fuentes** (alta confianza), 164 solo-OEA, 197 solo-ONU. Por década: 80s 24, 90s 27, 00s 47, 10s 114, 20s 318.
- **P1 validado:** toda notificación Art.4 PIDCP es emergencia por definición legal; las 151 sin etiqueta de régimen son extensiones/terminaciones/"suspensión de garantías" (no son no-emergencias). **Resuelto:** clasificador de régimen ampliado + propagación declaración→prórrogas → solo 4/776 sin régimen (`regimen_origen` = directo/heredado).
- ✅ **Contenido para ambas fuentes:** ONU → texto completo nativo (776/776) + **PDF C.N. del depositario** construible `treaties.un.org/doc/Publication/CN/{año}/CN.{n}.{año}-Eng.pdf` (519/776; los pre-2009 no tienen C.N. digital pero sí texto; URLs validadas, sin anti-bot). OEA → texto OCR (529). En `registro_excepcion_unificado.csv` cols `url`+`texto`; monitor con filas expandibles.
- ✅ **Episodios de vigencia** (`build_episodes.py` → `episodios_excepcion.csv`): encadena notificaciones por país (renovaciones a ≤75d = mismo episodio; 'fin' lo cierra; +30d cola si no hay levantamiento explícito). **163 episodios, 17 países.** Validación: El Salvador 2022-03→2026 (1553d, 47 extensiones) = régimen de excepción de Bukele capturado como un episodio continuo. 12 episodios >365d, 76 con extensiones.
- ✅ **Visualización Gantt** (`build_timeline.py` → `timeline_estados_excepcion.html`): barras de vigencia por país en eje 1976→2026, color por régimen, marcas internas = renovaciones, tooltip con inicio/fin/duración/extensiones.
- ⏳ **Pendiente:** (a) dataset Bjørnskov & Voigt / Hafner-Burton de facto SOE (país-año 1949→) — replicación académica **no descargable abiertamente** (Dataverse/paywall); el usuario podría aportarlo como hizo con el INEP; (b) gacetas + lexicón Tier A para recall pre-1976 y emergencias no notificadas; (c) afinar parseo OEA (plazo 4%, alcance 56%) y causa con LLM.

## Historial
- **2026-06-23** — Estrategia inicial + ejecución Capa A+ OEA. Insight central: registros de notificación OEA Art.27 CADH + ONU PIDCP Art.4 como capa autoritativa (A+). Alcance fijado: 1950→, solo nacionales, arranque por Capa A+ luego kit gacetas Tier A. Scraper OEA → 538 notificaciones 2014-2026.
