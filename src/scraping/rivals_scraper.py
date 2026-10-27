"""
rivals_scraper.py
=================
Descarga los últimos N partidos de Primera Nacional de un equipo rival.
Usa el mismo SofascoreClient que chaco_scraper.py.

Endpoint principal: /api/v1/team/{team_id}/events/last/0

Baja EXACTAMENTE los mismos datos que el scraper de Chaco: reutiliza su
`fetch_match`, así que cada partido de rival queda con los mismos 9 endpoints
crudos y los mismos 9 CSV limpios que un partido del Negro.

Los datos se guardan en:
  data/temporadas/{season}/rivals/{rival_slug}/{match_key}/
    ├── raw/event.json, statistics.json, lineups.json, incidents.json,
    │       shotmap.json, average_positions.json, graph.json,
    │       best_players.json, heatmaps.json, managers.json
    ├── event_clean.csv
    ├── statistics_clean.csv
    ├── lineups_clean.csv          (enriquecido con incidencias: cambios y tarjetas)
    ├── incidents_clean.csv
    ├── shotmap_clean.csv
    ├── average_positions_clean.csv
    ├── momentum_clean.csv
    ├── best_players_clean.csv
    └── player_heatmaps_clean.csv

OJO con event_clean.csv: las columnas `chaco_home` / `chaco_goals` /
`rival_goals` vienen del parser de Chaco y acá se leen desde la óptica del
EQUIPO SCRAPEADO (el rival), no de For Ever — el match_key es suyo.

Uso:
    from src.scraping.rivals_scraper import scrape_rival_recent
    scrape_rival_recent("temperley", n_matches=5, season="2026")
"""

import os
import json
import time
import random
from datetime import datetime, timezone

import config
from src.scraping.chaco_scraper import (
    SofascoreClient,
    fetch_match,
    _match_done,
    _scrape_series,
)


def get_rival_season_events(client, team_id, season_id, max_pages=8, tournament_id=None):
    """
    Devuelve TODOS los eventos finalizados del equipo en la temporada
    `season_id` de `tournament_id` (default: config.UNIQUE_TOURNAMENT_ID,
    Primera Nacional), en orden cronológico ASCENDENTE (más viejo primero).
    Cada elemento es (event_id, event_dict).

    `tournament_id` parametrizable para reusar esta misma función con otro
    torneo (ej. Liga Profesional, ver src/scraping/lpf_scraper.py) sin
    duplicar la lógica de paginación/filtrado.

    El endpoint `events/last/{page}` devuelve eventos de TODAS las
    competiciones del equipo (reservas, copas, torneos regionales) y de
    CUALQUIER temporada del mismo torneo, todo mezclado en un único feed
    cronológico — por eso hay que filtrar por torneo Y por season_id, no
    solo por torneo (si no, se cuela la temporada anterior). La página 0 es
    la ventana más reciente; páginas más altas van más atrás en el tiempo, y
    dentro de cada página los eventos ya vienen en orden ascendente.

    Se corta la paginación cuando 2 páginas seguidas no aportan ningún
    evento nuevo de esa temporada (ya quedó atrás el arranque de temporada)
    o cuando se acaban las páginas (hasNextPage=False).
    """
    tournament_id = tournament_id or config.UNIQUE_TOURNAMENT_ID
    seen_ids = set()
    collected = []
    misses = 0
    page = 0
    while page < max_pages:
        data = client.get_json(f"api/v1/team/{team_id}/events/last/{page}")
        if not data:
            break

        new_this_page = 0
        for ev in data.get("events", []):
            ut_id = ((ev.get("tournament", {}) or {}).get("uniqueTournament", {}) or {}).get("id")
            sid = (ev.get("season", {}) or {}).get("id")
            status_type = (ev.get("status", {}) or {}).get("type", "")
            if ut_id != tournament_id or sid != season_id or status_type != "finished":
                continue
            if ev["id"] in seen_ids:
                continue
            seen_ids.add(ev["id"])
            collected.append(ev)
            new_this_page += 1

        misses = 0 if new_this_page else misses + 1
        if misses >= 2 or not data.get("hasNextPage"):
            break
        page += 1

    collected.sort(key=lambda e: e.get("startTimestamp") or 0)
    return [(ev["id"], ev) for ev in collected]


def get_rival_recent_events(client, team_id, n=None, season_id=None, tournament_id=None,
                            max_pages=8):
    """
    Eventos finalizados del equipo, en orden cronológico ascendente. Si `n`
    es None, devuelve TODOS los de la temporada; si es un entero, se queda
    con los ÚLTIMOS n (los más recientes).

    `max_pages` limita cuántas páginas del feed del equipo se recorren. Para
    una corrida post-fecha alcanza con 2 (el partido nuevo siempre está en la
    página 0-1); la corrida completa / backfill necesita el default.

    OJO histórico: antes esta función tomaba `filtered[:n]` — los PRIMEROS n
    de la lista ascendente, es decir los más VIEJOS de la temporada, no los
    más recientes. Bug real (detectado porque el rival scrapeado quedaba
    siempre con los partidos de febrero-marzo, nunca los últimos jugados).
    """
    season_id = season_id or config.SEASON_IDS.get(config.CURRENT_SEASON)
    events = get_rival_season_events(client, team_id, season_id,
                                     tournament_id=tournament_id, max_pages=max_pages)
    return events[-n:] if n else events


def _build_match_key(ev, rival_team_id):
    """Construye un match_key descriptivo para el partido del rival."""
    ts = ev.get("startTimestamp")
    date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d") if ts else "unknown"

    home = ev.get("homeTeam", {}) or {}
    away = ev.get("awayTeam", {}) or {}

    is_home = home.get("id") == rival_team_id
    opp = away if is_home else home
    # Slug canónico del registro (config.EQUIPOS), el mismo de la carpeta del
    # club en rivals/. Solo si el equipo no está registrado se usa su nombre.
    opponent = config.slug_de(opp.get("id"), opp.get("name"))

    venue = "h" if is_home else "a"
    return f"{date_str}_vs_{opponent}_{venue}"


def scrape_rival_recent(rival_slug, n_matches=None, season=None, headless=False,
                        include_heatmaps=True, team_id=None, team_name=None,
                        tournament_id=None, out_base=None, season_id=None,
                        quick=False, retry_empty=False, force=False):
    """
    Descarga los partidos de Primera Nacional del rival en la temporada
    indicada, con los MISMOS datos que un partido de Chaco (usa fetch_match).

    Parámetros
    ----------
    rival_slug : str
        Clave del rival en config.RIVALS (ej. 'temperley', 'colon'). Si se
        pasan `team_id`/`team_name` explícitos, `rival_slug` se usa solo
        como nombre de carpeta (no hace falta que esté en config.RIVALS) —
        así se reusa esta función para otros torneos, ver
        src/scraping/lpf_scraper.py.
    n_matches : int o None
        Cuántos partidos bajar (los últimos N, los más recientes). Default
        None = TODOS los partidos jugados de la temporada — necesario para
        que análisis como formaciones/disciplina no queden cortos por solo
        mirar una muestra chica.
    season : str, opcional
        Temporada destino. Default: config.CURRENT_SEASON.
    headless : bool
        Correr browser sin ventana.
    include_heatmaps : bool
        Bajar el heatmap de cada jugador que jugó (~22 requests extra por
        partido). Es lo que hace el scraper de Chaco. Ponelo en False solo si
        querés una pasada rápida sin mapas de calor.
    team_id, team_name : opcionales
        Si se pasan, se usan en vez de buscar en config.RIVALS (para
        equipos de otro torneo/registro, ej. Liga Profesional).
    tournament_id : opcional
        Torneo a filtrar en SofaScore. Default: config.UNIQUE_TOURNAMENT_ID
        (Primera Nacional). Pasar config.UNIQUE_TOURNAMENT_ID_LPF para LPF.
    out_base : opcional
        Carpeta destino. Default: config.rivals_dir(season)/rival_slug.
    season_id : opcional
        ID de temporada en SofaScore a filtrar. Default: config.SEASON_IDS
        (Primera Nacional) — OJO, otros torneos tienen su propio registro de
        season_id (ej. config.SEASON_IDS_LPF) y hay que pasarlo explícito,
        si no el filtro de temporada nunca matchea y devuelve 0 partidos.

    Retorna
    -------
    list[str]
        Lista de match_keys descargados. Los partidos ya completos se saltean
        (sin llamadas de red), así que llamar de nuevo para completar partidos
        nuevos es barato. Un partido bajado con la versión vieja del scraper
        (sin event_clean.csv) se vuelve a bajar entero.
    """
    season = season or config.CURRENT_SEASON
    season_id = season_id or config.SEASON_IDS.get(season)

    if team_id is None:
        rival_info = config.RIVALS.get(rival_slug)
        if not rival_info:
            available = list(config.RIVALS.keys())
            raise ValueError(
                f"Rival '{rival_slug}' no encontrado en config.RIVALS.\n"
                f"Disponibles: {available}"
            )
        team_id = rival_info["id"]
        rival_name = team_name or rival_info["name"]
    else:
        rival_name = team_name or rival_slug

    out_base = out_base or os.path.join(config.rivals_dir(season), rival_slug)
    os.makedirs(out_base, exist_ok=True)

    max_pages = 2 if quick else 8
    if n_matches:
        print(f"Scrapeando los últimos {n_matches} partidos de {rival_name} (id={team_id})...")
    else:
        print(f"Scrapeando TODOS los partidos de {rival_name} en la temporada {season} (id={team_id})...")

    with SofascoreClient(headless=headless) as client:
        events = get_rival_recent_events(client, team_id, n=n_matches, season_id=season_id,
                                         tournament_id=tournament_id, max_pages=max_pages)

        if not events:
            print(f"  No se encontraron partidos recientes (tournament_id={tournament_id or config.UNIQUE_TOURNAMENT_ID}, season_id={season_id}) para {rival_name}.")
            return []

        print(f"  {len(events)} partidos en el feed.\n")
        items = [(_build_match_key(ev_data, team_id), mid) for mid, ev_data in events]
        stats = _scrape_series(
            client, items, out_base, include_heatmaps=include_heatmaps,
            retry_empty=retry_empty, force=force,
        )

    print(f"\n✅ {rival_name}: {stats['scraped']} bajados, "
          f"{stats['done']} ya estaban, {stats['error']} con error.")
    return [mk for mk, _ in items]


def rival_already_scraped(rival_slug, season=None, min_matches=1):
    """Retorna True si hay al menos min_matches partidos del rival ya descargados."""
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    if not os.path.isdir(rival_dir):
        return False
    matches = [d for d in os.listdir(rival_dir) if os.path.isdir(os.path.join(rival_dir, d))]
    return len(matches) >= min_matches


def scrape_rival_managers(rival_slug, season=None, headless=True, out_base=None):
    """
    Descarga el DT de cada partido ya scrapeado del rival, usando el endpoint
    `/event/{id}/managers` (que NO viene en el lineups/event que bajamos por
    defecto). Sirve para detectar cambios de entrenador a lo largo de la
    temporada.

    Guarda `raw/managers.json` en la carpeta de cada partido. Es idempotente:
    los partidos que ya lo tienen se saltean sin llamada de red, así que
    correrlo de nuevo para completar partidos nuevos es barato.

    out_base : opcional
        Carpeta donde están los partidos ya scrapeados del equipo. Default:
        config.rivals_dir(season)/rival_slug (Primera Nacional). Pasar
        config.lpf_team_dir(slug, season) para reusar esto con equipos de
        Liga Profesional (ver src/scraping/lpf_scraper.py).

    Retorna la lista de match_keys para los que quedó disponible el DT.
    """
    season = season or config.CURRENT_SEASON
    rival_dir = out_base or os.path.join(config.rivals_dir(season), rival_slug)
    if not os.path.isdir(rival_dir):
        print(f"  No hay datos scrapeados de {rival_slug} en {season}.")
        return []

    match_keys = sorted(
        d for d in os.listdir(rival_dir) if os.path.isdir(os.path.join(rival_dir, d))
    )

    pending = []
    for mk in match_keys:
        mpath = os.path.join(rival_dir, mk, "raw", "managers.json")
        ev_path = os.path.join(rival_dir, mk, "raw", "event.json")
        if os.path.exists(mpath) or not os.path.exists(ev_path):
            continue
        ev = json.load(open(ev_path, encoding="utf-8"))
        ev = ev.get("event", ev)
        pending.append((mk, ev.get("id"), mpath))

    if pending:
        print(f"Scrapeando DT de {len(pending)} partidos de {rival_slug}...")
        with SofascoreClient(headless=headless) as client:
            for i, (mk, mid, mpath) in enumerate(pending):
                data = client.get_json(f"api/v1/event/{mid}/managers")
                if data:
                    with open(mpath, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False)
                print(f"  [{i+1}/{len(pending)}] {mk}  ok={bool(data)}")
                if i < len(pending) - 1:
                    time.sleep(random.uniform(config.MIN_DELAY, config.MAX_DELAY))
    else:
        print(f"  Todos los partidos de {rival_slug} ya tienen DT descargado.")

    done = [mk for mk in match_keys
            if os.path.exists(os.path.join(rival_dir, mk, "raw", "managers.json"))]
    return done
