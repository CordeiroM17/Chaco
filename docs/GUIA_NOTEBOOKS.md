# Guía de trabajo con los notebooks

Todos viven en `notebooks/primera_nacional/`. Cada uno tiene arriba una celda **CONFIGURAR ACÁ**: cambiás esas variables y corrés todo (*Run All*). Usá siempre el kernel del `venv`.

Los cuatro momentos del año:

| Momento | Cuándo | Notebooks |
|---|---|---|
| [Pre-partido](#1-pre-partido) | 2 a 4 días antes de jugar | `analisis_pre_partido` |
| [Post-partido](#2-post-partido) | El día después de jugar | `analisis_post_partido` |
| [Fin de fecha](#3-fin-de-fecha) | Cuando terminó la fecha completa (los 36 equipos) | `scraping_todos_los_equipos` → `base_jugadores` → `analisis_temporada` → `analisis_proyeccion_tabla` → `estadisticas_globales_grupo_a` |
| [Fin de año](#4-fin-de-año) | Después de la última fecha | completar datos, base, informe de temporada, mercado, preparar el año nuevo |

Y dos que usás cuando aparecen: [mercado de pases](#5-mercado-de-pases-refuerzos) y [temporadas pasadas](#6-temporadas-pasadas).

---

## 1. Pre-partido

**`analisis_pre_partido`**

| Variable | Qué poner |
|---|---|
| `SEASON` | `'2026'` |
| `NEXT_MATCH_KEY` | `'AAAA-MM-DD_vs_<slug>_<h\|a>'`, ej. `'2026-10-24_vs_ferro_carril_oeste_a'` |
| `RIVAL_SLUG` | el slug de `config.RIVALS`, ej. `'ferro_carril_oeste'` |
| `REFRESCAR_TABLA` | `True` (baja la tabla de las dos zonas y el fixture) |

Antes de correrlo:
- Sacá la localía (`_h` local, `_a` visitante) de `data/temporadas/2026/fixture.csv`, no de memoria. Los partidos reprogramados repiten el número de fecha.
- El slug es el de `config.py` y vale para todas las temporadas: `club_mitre`, `gimnasia_jujuy`, `central_norte`.

El notebook baja solo los partidos del rival que falten (incremental) y su DT partido por partido, y deja todo en `outputs/temporadas/2026/pre_partido/<rival>_<h|a>/`.

Después:
- Revisá la disciplina contra la nota del club. `discipline_alert()` no ve las rojas y no sabe que las amarillas se borran en el receso; si la nota del club dice otra cosa, vale la nota.
- El informe `.tex → PDF` me lo pedís a mí con la carpeta de salida. La previa de Instagram sale con `python ig.py ...` en `redes_sociales/instagram/`.

## 2. Post-partido

1. Agregá el partido al archivo de links de la temporada, `data/Teams links/Chaco_For_Ever_Matches_Season_2026.py`, con su match_key y el link de SofaScore. El notebook lo baja desde ahí.
2. **`analisis_post_partido`**:

| Variable | Qué poner |
|---|---|
| `SEASON` | `'2026'` |
| `MATCH_KEY` | el mismo match_key del paso 1 |
| `REFRESCAR_TABLA` | `True` (scrapear el partido no actualiza la tabla; sin esto el informe cita la de la fecha anterior) |

Las salidas quedan en `outputs/temporadas/2026/partidos/<match_key>/`.

SofaScore tarda hasta 48 h en publicar el shotmap y las posiciones medias. Si el notebook avisa "sin datos en SofaScore", volvé a correrlo al día siguiente.

Después: me pedís el informe `.tex` y el carrusel o las historias (`python ig.py ...`).

## 3. Fin de fecha

Cuando terminó la fecha entera (normalmente lunes o martes), en este orden:

**1. `scraping_todos_los_equipos`.** Configuración: `SEASON = '2026'`, `QUICK = True`, `RETRY_EMPTY = False`. Corré:
- la celda de scraping;
- la **3b** (auditoría), que lista lo que quedó incompleto;
- la **3c**, que refresca `standings.csv` y `fixture.csv`.

Si la auditoría muestra partidos sin shotmap o sin estadísticas, repetí al día siguiente con `RETRY_EMPTY = True`. Una corrida larga puede cortarse después del primer equipo: la auditoría lo muestra.

**2. `base_jugadores`, secciones 1 a 4.** Actualiza la base de jugadores de todas las temporadas, corre los controles y lista los posibles jugadores con dos `player_id`.
- Si aparece un duplicado con `evidencia = shotmap ...`, es casi seguro: cargalo en `config.ALIAS_JUGADORES` y volvé a correr la sección 2.
- Los que solo coinciden en el nombre, revisalos a mano. Hoy quedan cuatro que son personas distintas.

`SC.pool_liga()` actualiza la base solo si detecta partidos nuevos, así que este paso sirve sobre todo para ver los controles y los duplicados.

**3. `analisis_temporada`.** Chaco en la temporada: tabla, jugadores, pizzas y radar.

**4. `analisis_proyeccion_tabla`.** Monte Carlo de la tabla. `ACTUALIZAR_FIXTURE = False` alcanza si ya corriste la 3c.

**5. `estadisticas_globales_grupo_a`.** Poné `VER_FECHA` en la fecha que terminó. Arma el Mejor 11 de la fecha y los rankings.

**Opcionales:**
- `analisis_duplas_mediocampo`: duplas y tríos de cada línea.
- `scouting_similitud`: semáforo del plantel y gemelos.
- `informe_equipo_liga`: informe de cualquier equipo, para vender.

## 4. Fin de año

### Completar los datos

1. `scraping_todos_los_equipos` con `QUICK = False` y `RETRY_EMPTY = True`: recorre la temporada entera de cada equipo y reintenta lo que SofaScore no había publicado.
2. `scraping_temporada_historica` con `SEASON = '2026'`, secciones 2 y 3. Compara contra el fixture y baja cualquier partido que falte en todas las carpetas. Si la sección 2 dice "0 nuevos", no falta nada.
3. Misma notebook, secciones 4 y 5: tabla de las dos zonas y base de jugadores.

### Cerrar la base

`base_jugadores` completo, incluida la **sección 9 (chequeo de la medición)**:
- La sección 9 compara mes a mes las stats más sensibles. Si muestra un salto sostenido de varios meses, como el del 1/7/2026, SofaScore volvió a cambiar la forma de medir. En ese caso agregás el corte en `CORTES_REGIMEN` (en `src/jugadores/construir.py`) y volvés a correr la sección 2.
- Un mes suelto con pocos partidos suele ser ruido.

### Informes y mercado

- `analisis_temporada` → me pedís el informe de temporada `.tex`.
- `scouting_similitud`: semáforo del plantel para decidir renovaciones.
- `base_jugadores` sección 8 y `analisis_refuerzos`: candidatos (ver sección 5 de esta guía).

### Preparar la temporada nueva (`config.py`)

1. `CURRENT_SEASON = '<año>'`.
2. `SEASON_IDS['<año>'] = <id>`. El id está en la URL de la temporada en SofaScore (el número después de `#id:`).
3. `RIVALS_<año>` con los rivales de la zona de Chaco, y el dict de la otra zona. Un equipo que ya existía mantiene su slug, aunque haya bajado y vuelto. A un equipo nuevo le das slug en minúsculas con guiones bajos (`alvarado`, `arsenal_de_sarandi`) y su `team_id`.
4. `group_a_teams()` y `group_b_teams()` devuelven equipos solo para `'2026'`: sumá el año nuevo.
5. `MATCHES_FILES['<año>']` y el archivo nuevo `data/Teams links/Chaco_For_Ever_Matches_Season_<año>.py`.
6. En `scraping_todos_los_equipos`, `EQUIPOS` arma la lista con `RIVALS_2026` y `RIVALS_ZONA_B_2026`: cambialos por los del año nuevo.
7. Revisá `JUGADORES_FUERA`: se vacía o se actualiza con las bajas del receso.
8. Cambiá `SEASON = '2026'` por el año nuevo en la celda de configuración de cada notebook.

## 5. Mercado de pases (refuerzos)

**`analisis_refuerzos`**. En `REFUERZOS` pegás `nombre → link de Transfermarkt` y corrés todo:

| Sección | Qué hace |
|---|---|
| 1 a 4 | Ficha de Transfermarkt: bio, clubes, rendimiento por competición. Usa caché en `data/refuerzos/`. |
| 5 | Lo busca en la base de jugadores por apellido + fecha de nacimiento y muestra su recorrido en Primera Nacional, temporada por temporada, con su puesto en el rol contra todas las temporadas ("32° de 220 delanteros"). |
| 6 | A quién se parece: gemelos k-NN en todas las temporadas. Ajustá `FILTROS_COMP` (ej. `{'edad_max': 27, 'temporadas_candidatos': ['2026']}`). |

Si en la sección 5 el cruce no es seguro, el notebook lista los candidatos. Elegí el correcto y corré `Q.vincular_transfermarkt(player_id, url)`: queda guardado en `data/jugadores/jugadores.csv` y la próxima vez lo encuentra directo.

Para buscar reemplazos de un jugador propio sin link de Transfermarkt: `base_jugadores`, secciones 7 y 8.

## 6. Temporadas pasadas

**`scraping_temporada_historica`** (2024 o anteriores):
1. Agregá el id en `config.SEASON_IDS`.
2. Corré la sección 2: baja el fixture y te avisa qué equipos no están registrados. Sumalos a `RIVALS_<año>` en `config.py` antes de bajar, porque el slug queda en el nombre de las carpetas.
3. Probá con `LIMITE = 3`; si anda, `LIMITE = None` y dejalo correr (unas 4 horas sin heatmaps).
4. Secciones 4 y 5: tabla de posiciones y base de jugadores.

---

## Qué pasa solo y qué no

**Automático:**
- `SC.pool_liga()` lee de la base de jugadores y la actualiza si hay partidos nuevos. Une a los jugadores con dos `player_id`, recupera los remates que el shotmap anotó con otro id y ajusta el cambio de medición del 1/7/2026.
- Las pizzas de Chaco (`players.player_pool`) usan el mismo ajuste.
- Los scrapers no repiten lo que ya bajaron.

**A mano:**
- El link del partido de Chaco en el archivo de links (post-partido).
- Los alias de jugadores duplicados (`config.ALIAS_JUGADORES`).
- Los equipos nuevos en `RIVALS_<año>`.
- Un corte nuevo en `CORTES_REGIMEN` si la sección 9 lo marca.

Si querés ver los números como venían antes del ajuste: `SC.pool_liga(..., ajustado=False)` y `player_pool(..., ajustado=False)`. El cálculo viejo completo, sin base: `SC.pool_liga(..., fuente="carpetas")`.

## Problemas conocidos

| Síntoma | Causa | Qué hacer |
|---|---|---|
| 403 "challenge" de SofaScore | Falta la cookie de la home (captcha) | Correr con ventana (`headless=False`); el cliente la renueva solo |
| 403 de Varnish a todos los pedidos | Ban de la IP | Cambiar de IP (reiniciar el router o usar otra red) y volver a correr: retoma donde quedó |
| "sin datos en SofaScore" en un partido reciente | SofaScore todavía no publicó shotmap/estadísticas | Reintentar al día siguiente (`RETRY_EMPTY = True`) |
| Un jugador aparece dos veces con minutos repartidos | SofaScore le dio dos `player_id` | `base_jugadores` sección 4 → `config.ALIAS_JUGADORES` |
| Un refuerzo de invierno sale con pocos quites y muchos despejes | Números crudos del régimen nuevo | Usar los ajustados (el default) |
| El informe tiene la tabla vieja | No se refrescó `standings.csv` | `REFRESCAR_TABLA = True` o la celda 3c del scraping |
