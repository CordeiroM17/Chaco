# Chaco For Ever — Análisis de datos

Pipeline modular para analizar a Chaco For Ever (Primera Nacional, Argentina) a
partir de datos de SofaScore. Cada partido se guarda como una carpeta limpia y
autocontenida (equipo + rival, por partido y por jugador) para sacar estadísticas
de toda la temporada sin re-scrapear.

Todo se configura desde un único cerebro central: **`config.py`**.

## Estructura

```
config.py                         # cerebro central: IDs, rutas, rivales, helpers

data/
  Teams links/
    Chaco_For_Ever_Matches_Season_2025.py   # dict MATCHES {match_key: url}
  matches_index.csv                          # índice maestro (generado)
  temporadas/<season>/
    partidos/<match_key>/         # 9 CSVs limpios + raw/ por partido
    rivals/<rival_slug>/          # últimos N partidos de cada rival (scouting)
    standings.csv                 # tabla de posiciones

src/
  scraping/
    chaco_scraper.py       # API directa de SofaScore por event_id (todos los endpoints)
    rivals_scraper.py      # últimos N partidos de cualquier rival
    standings_scraper.py   # tabla de posiciones de la Primera Nacional
  analysis/
    season.py              # resúmenes y stats de temporada / jugadores
    post_match.py          # análisis profundo de un partido (xG, cambios, momentum)
    pre_match.py           # scouting: forma, perfil táctico rival, H2H
  visualization/
    season.py              # shotmaps, evolución de puntos, xG, top jugadores
    match.py               # momentum, posiciones promedio, heatmaps, timeline, ratings
    pre_match.py           # forma comparada, tendencia xG, radar, jugadores rival
  reports/
    season.py              # informes de temporada/partido/jugador con Claude
    post_match.py          # informe narrativo post-partido
    pre_match.py           # informe de scouting pre-partido

notebooks/                 # puntos de entrada (configurar y correr)
  analisis_temporada.ipynb       # temporada completa
  analisis_post_partido.ipynb    # un partido específico
  analisis_pre_partido.ipynb     # scouting del próximo rival

outputs/
  temporadas/<season>/
    graficos/              # gráficos de temporada
    informes/              # informes de temporada
    partidos/<match_key>/  # gráficos + informe por partido
    pre_partido/<rival>/   # gráficos + informe de scouting
```

`match_key` (clave de cada partido): `YYYY-MM-DD_vs_<rival>_<h|a>`, donde `_h`
= Chaco de local y `_a` = de visitante. La condición de local/visitante de Chaco
se deduce de ahí, **no** de quién figura como home/away en SofaScore.

## Cómo usarlo

Los tres notebooks son los puntos de entrada. Cada uno tiene una celda de
configuración al principio (`SEASON`, `MATCH_KEY`, `RIVAL_SLUG`, etc.) y se corre
de arriba a abajo. Detectan automáticamente qué datos ya existen y **no
re-scrapean** lo que ya está bajado.

| Notebook | Para qué | Configurar |
|----------|----------|------------|
| `analisis_temporada.ipynb` | Temporada completa: tabla, stats, gráficos, pizzas de jugadores e informe | `SEASON`, `SCRAPE_MISSING` |
| `analisis_post_partido.ipynb` | Un partido: shotmap, momentum, heatmaps (grid + individuales), radios de acción, xG por tramos, defensa, informe | `SEASON`, `MATCH_KEY` |
| `analisis_pre_partido.ipynb` | Scouting del rival: forma, perfil táctico, H2H, informe | `SEASON`, `NEXT_MATCH_KEY`, `RIVAL_SLUG` |
| `descargar_video.ipynb` | **Fase B**: baja el video de un partido desde el link del player (lpfplay/AFA) | `PAGE_URL`, `SEASON`, `MATCH_KEY`, `QUALITY` |
| `analisis_video.ipynb` | **Fase B**: video del partido → tracking validado contra SofaScore | `SEASON`, `MATCH_KEY`, `TEST_SECONDS` |

Los notebooks usan `%autoreload 2`, así que editar cualquier módulo de `src/` se
refleja sin reiniciar el kernel.

## Datos por partido (scraper)

`src/scraping/chaco_scraper.py` le pega directo a la API interna de SofaScore con
el `event_id` de cada URL. Para esquivar Cloudflare navega con un navegador real
(`undetected_chromedriver`, con fallback a Selenium) y lee el JSON del body.

| Endpoint API                     | Archivo limpio                  | Contenido |
|----------------------------------|---------------------------------|-----------|
| `event/{id}`                     | `event_clean.csv`               | Metadata + marcador + árbitro + estadio |
| `event/{id}/statistics`          | `statistics_clean.csv`          | Stats de equipo por grupo |
| `event/{id}/lineups`             | `lineups_clean.csv`             | Jugadores + stats completas por jugador |
| `event/{id}/incidents`           | `incidents_clean.csv`           | Goles, cambios y tarjetas (timeline) |
| `event/{id}/shotmap`             | `shotmap_clean.csv`             | Tiros con xG, xGOT y coordenadas |
| `event/{id}/average-positions`   | `average_positions_clean.csv`   | Posición promedio por jugador |
| `event/{id}/graph`               | `momentum_clean.csv`            | Momentum por minuto |
| `event/{id}/best-players`        | `best_players_clean.csv`        | Figuras del partido (si hay) |
| `event/{id}/player/{pid}/heatmap`| `player_heatmaps_clean.csv`     | Heatmap por jugador que jugó |

El JSON crudo de cada endpoint queda en `<match_key>/raw/`, así se puede
re-parsear sin volver a scrapear.

## Pipeline de video (Fase B)

`src/video/` convierte el video de un partido en tracking con coordenadas
**OPTA 0-100** (el mismo sistema que SofaScore — todo se cruza directo):

- `downloader.py` — baja el video desde el link del player. Captura el
  `master.m3u8` con un navegador headless (el stream no está en el HTML) y lo
  descarga con yt-dlp. Probado con lpfplay.com / immergo.tv (HLS sin DRM).
- `schema.py` — contrato de datos (`tracking/positions.csv`, `ball_positions.csv`)
- `pipeline.py` — video → detección (YOLOv8) → tracking (ByteTrack) → equipos
  (clusters de camiseta) → homografía → CSV
- `validation.py` — valida el tracking contra SofaScore (lineups = minutos y
  jugadores oficiales; plausibilidad espacial de la homografía)

Convención: el video va en `data/temporadas/{año}/partidos/{match_key}/video/`
y los derivados quedan en `.../tracking/`. Dependencias en
`requirements-video.txt`; pesos de los modelos en `models/` (ver su README).

## Cambiar de temporada

1. Crear `data/Teams links/Chaco_For_Ever_Matches_Season_<año>.py` con el dict de URLs.
2. Completar `config.SEASON_IDS["<año>"]` con el season_id de SofaScore.
3. Poner `SEASON = "<año>"` en el notebook que corresponda.

IDs clave (en `config.py`): Chaco team_id **252726**, Primera Nacional
uniqueTournament_id **703**, temporada 2025 season_id **71009**.

> El scraper depende de un Chrome instalado. Es respetuoso con el sitio (pausas
> aleatorias y reintentos ante bloqueos de Cloudflare). Conviene correr primero
> un solo partido para validar antes de bajar la temporada entera.
