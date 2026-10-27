"""
lpf_scraper.py
===============
Scraping de la Liga Profesional Argentina (primera división) desde
SofaScore — torneo APARTE de la Primera Nacional donde juega Chaco For
Ever (config.UNIQUE_TOURNAMENT_ID_LPF=155, distinto de config.UNIQUE_TOURNAMENT_ID=703).

Formato 2026 confirmado en vivo contra la API: Apertura + Clausura, cada
uno con Zona A/B de 15 equipos, más "Anual 2026" (30, todos contra todos
acumulado) y "Promedios 2026" (30, la tabla que define descenso). Los 6
grupos y las dos etapas viven bajo un único season_id
(config.SEASON_IDS_LPF) — el endpoint de fecha devuelve Apertura y
Clausura mezcladas bajo el mismo número de "round", diferenciadas por el
campo `stage` (nombre del sub-torneo).

Reusa la infraestructura existente en vez de duplicarla:
  - fetch_match / SofascoreClient       (chaco_scraper.py)
  - get_rival_recent_events, scrape_rival_recent (rivals_scraper.py, con
    tournament_id parametrizable)
  - fetch_tournament_fixture             (fixture_scraper.py)

Guarda en:
  data/liga_profesional/{season}/standings/{grupo}.csv
  data/liga_profesional/{season}/fixture.csv
  data/liga_profesional/{season}/equipos/{slug}/{match_key}/...  (igual
    estructura que data/temporadas/{season}/rivals/{slug}/)

Uso:
    from src.scraping.lpf_scraper import fetch_standings_lpf, fetch_fixture_lpf, scrape_all_lpf_teams
    fetch_standings_lpf(season="2026")
    fetch_fixture_lpf(season="2026")
    scrape_all_lpf_teams(season="2026")
"""

import os
import time
import random

import pandas as pd

import config
from src.scraping.chaco_scraper import SofascoreClient
from src.scraping.fixture_scraper import fetch_tournament_fixture
from src.scraping.rivals_scraper import scrape_rival_recent, scrape_rival_managers
from src.scraping.standings_scraper import _rows_from_group

# Nombre de archivo por grupo de standings, tal como aparece en `name` en
# la respuesta de SofaScore para season_id=87913 (2026). Si SofaScore
# renombra los grupos en otra temporada, ajustar acá.
STANDINGS_GROUPS = {
    "apertura_zona_a": "Apertura, Group A",
    "apertura_zona_b": "Apertura, Group B",
    "clausura_zona_a": "Clausura, Group A",
    "clausura_zona_b": "Clausura, Group B",
    "anual":            "Anual",
    "promedios":        "Promedios",
}


def fetch_standings_lpf(season=None, headless=True):
    """
    Baja las 6 tablas de posiciones de la Liga Profesional (Apertura/Clausura
    x Zona A/B + Anual + Promedios) en un solo request y las guarda en
    data/liga_profesional/{season}/standings/{grupo}.csv.

    Devuelve dict {grupo: DataFrame}.
    """
    season = season or config.CURRENT_SEASON
    season_id = config.SEASON_IDS_LPF.get(season)
    if not season_id:
        print(f"⚠️  No hay season_id LPF configurado para temporada '{season}'.")
        return None

    path = (f"api/v1/unique-tournament/{config.UNIQUE_TOURNAMENT_ID_LPF}"
            f"/season/{season_id}/standings/total")

    print(f"Descargando tablas de posiciones LPF {season}...")
    with SofascoreClient(headless=headless) as client:
        data = client.get_json(path)

    if not data:
        print("❌ No se pudo obtener la tabla de posiciones.")
        return None

    groups_raw = data.get("standings", [])
    out_dir = config.lpf_standings_dir(season)
    os.makedirs(out_dir, exist_ok=True)

    result = {}
    for slug, needle in STANDINGS_GROUPS.items():
        group = next((g for g in groups_raw if needle in (g.get("name") or "")), None)
        if group is None:
            print(f"  ⚠️  no se encontró el grupo '{needle}' en la respuesta")
            continue
        rows = _rows_from_group(group)
        df = pd.DataFrame(rows).sort_values("position").reset_index(drop=True)
        out_path = os.path.join(out_dir, f"{slug}.csv")
        df.to_csv(out_path, index=False, encoding="utf-8")
        print(f"  ✅ {slug}: {len(df)} equipos -> {out_path}")
        result[slug] = df

    return result


def load_standings_lpf(grupo, season=None):
    """Carga una tabla de LPF ya scrapeada desde CSV local (sin scraping)."""
    path = os.path.join(config.lpf_standings_dir(season), f"{grupo}.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def fetch_fixture_lpf(season=None, headless=True, max_rounds=40, verbose=True):
    """
    Baja el calendario completo de LPF (Apertura + Clausura + playoffs,
    30 equipos) recorriendo fecha por fecha. Guarda en
    data/liga_profesional/{season}/fixture.csv.
    """
    season = season or config.CURRENT_SEASON
    season_id = config.SEASON_IDS_LPF.get(season)
    if not season_id:
        print(f"No hay season_id LPF configurado para temporada '{season}'.")
        return None

    return fetch_tournament_fixture(
        config.UNIQUE_TOURNAMENT_ID_LPF, season_id, config.lpf_fixture_file(season),
        max_rounds=max_rounds, headless=headless, verbose=verbose,
    )


def load_fixture_lpf(season=None):
    path = config.lpf_fixture_file(season)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def scrape_team_lpf(team_slug, season=None, headless=False, include_heatmaps=True,
                     n_matches=None, quick=False, retry_empty=False, force=False):
    """
    Descarga TODOS los partidos de LPF de un equipo (mismos 9 endpoints que
    un partido de Chaco: event/statistics/lineups/incidents/shotmap/
    average_positions/graph/best_players + heatmaps). Reusa
    rivals_scraper.scrape_rival_recent pasándole el team_id/tournament_id de
    LPF y la carpeta de salida propia (data/liga_profesional/), en vez de
    config.RIVALS y config.rivals_dir() que son de Primera Nacional.
    """
    season = season or config.CURRENT_SEASON
    team_info = config.LPF_TEAMS_2026.get(team_slug)
    if not team_info:
        raise ValueError(
            f"Equipo '{team_slug}' no encontrado en config.LPF_TEAMS_2026.\n"
            f"Disponibles: {list(config.LPF_TEAMS_2026.keys())}"
        )

    return scrape_rival_recent(
        team_slug, n_matches=n_matches, season=season, headless=headless,
        include_heatmaps=include_heatmaps,
        team_id=team_info["id"], team_name=team_info["name"],
        tournament_id=config.UNIQUE_TOURNAMENT_ID_LPF,
        season_id=config.SEASON_IDS_LPF.get(season),
        out_base=config.lpf_team_dir(team_slug, season),
        quick=quick, retry_empty=retry_empty, force=force,
    )


def scrape_managers_lpf(team_slug, season=None, headless=True):
    """
    DT de cada partido ya scrapeado de un equipo de LPF (mismo endpoint
    /managers que Primera Nacional). Reusa scrape_rival_managers pasándole
    la carpeta propia de LPF (data/liga_profesional/) en vez de
    config.rivals_dir(), que es de Primera Nacional.
    """
    season = season or config.CURRENT_SEASON
    return scrape_rival_managers(
        team_slug, season=season, headless=headless,
        out_base=config.lpf_team_dir(team_slug, season),
    )


def scrape_all_lpf_teams(season=None, headless=True, include_heatmaps=True,
                          delay_between_teams=True, quick=False):
    """
    Recorre los 30 equipos de config.LPF_TEAMS_2026 y baja la temporada
    completa de cada uno. Es idempotente (scrape_rival_recent saltea
    partidos ya bajados) — cortar y volver a correr no repite trabajo.

    Es la corrida grande: ~30 equipos x ~30 partidos x (8 endpoints +
    heatmaps) con delay de config.MIN_DELAY-MAX_DELAY entre requests. Pensado
    para dejarlo corriendo sin supervisión (ver
    scripts/scrape_overnight.py para el driver con logging a archivo).
    """
    season = season or config.CURRENT_SEASON
    slugs = list(config.LPF_TEAMS_2026.keys())
    resultados = {}
    for i, slug in enumerate(slugs):
        print(f"\n{'='*70}\n[{i+1}/{len(slugs)}] {config.LPF_TEAMS_2026[slug]['name']} ({slug})\n{'='*70}")
        try:
            resultados[slug] = scrape_team_lpf(
                slug, season=season, headless=headless,
                include_heatmaps=include_heatmaps, quick=quick,
            )
        except Exception as e:
            print(f"  ERROR con {slug}: {e}")
            resultados[slug] = []
        if delay_between_teams and i < len(slugs) - 1:
            time.sleep(random.uniform(config.MIN_DELAY, config.MAX_DELAY))
    return resultados
