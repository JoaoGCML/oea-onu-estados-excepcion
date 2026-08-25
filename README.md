# Bases de datos — Estados de excepción (Américas/OEA)

Handoff para ciencia de datos. Registro de **declaratorias de estado de excepción/emergencia/sitio/ley marcial** notificadas formalmente, países OEA, **1976→2026**. Carpeta: `ARGOS_KIT/estados_excepcion/`.

## Qué es esto (y qué NO es)
Son **notificaciones formales de suspensión de garantías** de dos depositarios oficiales:
- **OEA Art. 27 CADH** (notificadas a la Secretaría General OEA) — cobertura digital **2014→**.
- **ONU Art. 4 PIDCP** (derogaciones al depositario UN Treaty Collection) — **1976→**.

⚠️ **Sesgo clave para el modelado:** son **positivos confirmados de alta precisión pero cobertura parcial** (≈precision alta, recall bajo). Muchas emergencias reales NUNCA se notifican → **ausencia de registro ⇏ ausencia de emergencia**. No usar el "0" como cero-verdadero sin una fuente de recall (pendiente: dataset Bjørnskov/Hafner-Burton de facto país-año). EE.UU. y Canadá no aparecen: nunca derogaron del PIDCP (no es un hueco de datos).

---

## Archivos (4 niveles)

### 1. `panel_excepcion_pais_mes.csv` — 532 filas · **el target deduplicado (USAR PARA MODELAR)**
Una celda por país×mes con excepción vigente; colapsa el doble conteo OEA↔ONU.
| col | descripción |
|---|---|
| `pais` | país (ES) |
| `mes` | YYYY-MM |
| `anio` | YYYY |
| `fuentes` | `OEA` / `ONU` / `OEA+ONU` (confirmación cruzada) |
| `excepcion` | 1 (presencia; sólo celdas positivas — la rejilla completa país×mes con ceros hay que construirla) |
- 171 celdas confirmadas por ambas fuentes, 164 sólo-OEA, 197 sólo-ONU. Rango 1976-09 → 2026-06.

### 2. `registro_excepcion_unificado.csv` — 1315 filas · registro maestro (trazabilidad)
Cada notificación individual de ambas fuentes, esquema común + contenido.
| col | descripción |
|---|---|
| `pais, fecha, anio` | país, fecha ISO, año |
| `fuente` | `OEA Art.27` / `ONU Art.4` |
| `tipo` | régimen (estado de emergencia/sitio/excepción/susp. garantías/…) |
| `evento` | declaración / extensión / fin-levantamiento / declaración-prórroga |
| `detalle` | nº decreto (OEA) o ref C.N. (ONU) |
| `causa` | seguridad/crimen, desastre/salud, orden público… (sólo OEA, por OCR) |
| `ref` | nº de nota (OEA) / C.N. (ONU) |
| `url` | PDF oficial (OEA) o C.N. depositario (ONU) |
| `texto` | texto de la notificación (ONU nativo; OEA por OCR) |
| `dup_cross` | **1 = tiene gemelo en la otra fuente (±10 días)** → 709/1315 marcadas. Clave para deduplicar. |

### 3. Fuentes crudas (auditoría)
- `un_derogaciones_art4.csv` — 776 filas ONU. Cols extra: `pais_en`, `tipo_evento`, `regimen`, `regimen_origen` (`directo`/`heredado` — heredado = régimen propagado desde la declaración previa porque la prórroga no lo reexpresa), `cn_ref`, `url_pdf`, `texto`, `snippet`.
- `notif_oea_art27_enriquecido.csv` — 539 filas OEA. Cols extra (extraídas por **OCR** de PDFs escaneados, con ruido): `decreto`, `tipo`, `base_legal`, `causa`, `plazo_dias` (sólo ~4%), `alcance` (~56%), `derechos`, `ocr_chars`.
- `notif_oea_art27.csv` — 539 filas OEA sin enriquecer (sólo país/fecha/nota/url).

### 4. `episodios_excepcion.csv` — 163 filas · periodos de vigencia reconstruidos
Encadena notificaciones por país (renovaciones ≤75 días = mismo episodio; 'fin' lo cierra; +30 días de cola si no hay levantamiento explícito).
| col | descripción |
|---|---|
| `pais, inicio, fin` | país y fechas ISO del episodio |
| `dias` | duración |
| `n_notif, n_extensiones` | nº de notificaciones / extensiones en el episodio |
| `regimen` | tipo de régimen |
| `fuentes` | OEA / ONU / OEA+ONU |
| `cerrado_explicito` | 1 = terminó por levantamiento notificado; 0 = fin estimado (+30d) |
- Heurística (no captura emergencias no notificadas). Validación: El Salvador 2022→2026 = 1.553 días, 47 extensiones (régimen de Bukele).

---

## Notas metodológicas (importantes para el modelo)
1. **Deduplicar antes de contar**: OEA y ONU notifican el MISMO hecho por canales distintos. Usar `dup_cross` o trabajar sobre `panel_excepcion_pais_mes.csv`.
2. **Cobertura desigual en el tiempo**: ONU 1976→, OEA sólo 2014→. Perú sobre-notifica (cada prórroga); otros notifican poco.
3. **Cero-verdadero vs MISSING**: la rejilla país×mes completa con ceros NO está incluida; el "0" sólo es verdadero donde una fuente exhaustiva cubre. Falta capa de recall (de facto).
4. **Campos OCR (OEA) tienen ruido**; los de ONU son texto nativo (más limpios).
5. **`regimen_origen=heredado`** marca régimen inferido por propagación, no leído directo.

## Pipeline reproducible (scripts en la misma carpeta)
```
scrape_oea_art27.py + rematch_pdfs.py        -> notif_oea_art27.csv (OEA crudo)
enrich_v2.py + parse_enriquecido.py          -> notif_oea_art27_enriquecido.csv (OCR)
parse_un_derogaciones.py                     -> un_derogaciones_art4.csv (ONU)
merge_fuentes.py                             -> registro_excepcion_unificado.csv
build_panel.py                               -> + dup_cross  &  panel_excepcion_pais_mes.csv
build_episodes.py                            -> episodios_excepcion.csv
build_dashboard.py                           -> dashboard_excepcion.html (visualización)
```

## Fuentes y atribución

### Fuentes oficiales (capa de notificaciones)
- **OEA** — Departamento de Derecho Internacional, Secretaría General: notificaciones de suspensión de garantías, Art. 27 CADH.
- **ONU** — UN Treaty Collection, MTDSG Cap. IV-4: derogaciones notificadas al depositario, Art. 4(3) PIDCP. PDFs C.N.: `treaties.un.org/doc/Publication/CN/{año}/CN.{n}.{año}-Eng.pdf`. Seguimiento complementario del **Centre for Civil and Political Rights (CCPR Centre)**.
- **Gacetas y diarios oficiales nacionales** — actos primarios de declaración, prórroga y levantamiento (capa no notificada).

### Bases académicas y de referencia
Este registro se apoya en, y dialoga con, bases construidas por otros equipos de investigación, a quienes se agradece y atribuye expresamente:

- **Bjørnskov, C. (Aarhus University) & Voigt, S. (Universität Hamburg)** — base INEP sobre constituciones y poderes de emergencia *de jure* (214 países, 1789–2013), empleada como capa de referencia de jure. Ver Bjørnskov & Voigt (2018), *The Architecture of Emergency Constitutions*, International Journal of Constitutional Law 16(1).
- **Hafner-Burton, E. M., Helfer, L. R., & Fariss, C. J. (2011)** — *Emergency and Escape: Explaining Derogations from Human Rights Treaties*, International Organization 65(4) — referencia sobre el registro de derogaciones del PIDCP y sus sesgos.
- **Bjørnskov, C., & Rode, M. (2020)** — *Regime types and regime change: A new dataset on democracy, coups, and political institutions*, Review of International Organizations 15 — base de contexto de rupturas de régimen.
- **Oxford COVID-19 Government Response Tracker (OxCGRT)** e **ICNL COVID-19 Civic Freedom Tracker** — referencia para las emergencias del período COVID-19.

La compilación, el emparejamiento OEA↔ONU, la construcción de episodios y cualquier error son responsabilidad exclusiva de este repositorio; las bases citadas pertenecen a sus autores y se rigen por sus propios términos. Si se usa este registro en investigación, se pide citar también las fuentes anteriores cuando corresponda.
