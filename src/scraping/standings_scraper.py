"""
standings_scraper.py
====================
Descarga la tabla de posiciones de Primera Nacional desde SofaScore.

Endpoint: /api/v1/unique-tournament/{tid}/season/{sid}/standings/total
Guarda en: data/temporadas/{season}/standings.csv

Uso:
    from src.scraping.standings_scraper import fetch_standings
    df = fetch_standings(season="2025")
"""

import os
import pandas as pd

import config
from src.scraping.chaco_scraper import SofascoreClient


def fetch_standings(season=None, headless=True):
    """
    Baja la tabla de posiciones de Primera Nacional para la temporada dada.
    Guarda el CSV y devuelve el DataFrame.

    Si SEASON_IDS[season] es None en config.py, imprime un aviso y retorna None.
    """
    season = season or config.CURRENT_SEASON
    season_id = config.SEASON_IDS.get(season)

    if not season_id:
        print(
            f"⚠️  No hay season_id configurado para temporada '{season}'.\n"
            f"   Una vez que SofaScore publique la temporada, actualizá "
            f"config.SEASON_IDS['{season}'] con el ID correspondiente."
        )
        return None

    path = (f"api/v1/unique-tournament/{config.UNIQUE_TOURNAMENT_ID}"
            f"/season/{season_id}/standings/total")

    print(f"Descargando tabla de posiciones {season}...")

    with SofascoreClient(headless=headless) as client:
        data = client.get_json(path)

    if not data:
        print("❌ No se pudo obtener la tabla de posiciones.")
        return None

    standings = data.get("standings", [])
    if not standings:
        print("❌ Respuesta sin standings.")
        return None

    rows_raw = standings[0].get("rows", [])
    rows = []
    for r in rows_raw:
        team = r.get("team", {}) or {}
        gf = r.get("scoresFor", 0) or 0
        ga = r.get("scoresAgainst", 0) or 0
        rows.append({
            "position":       r.get("position"),
            "team_id":        team.get("id"),
            "team_name":      team.get("name"),
            "team_slug":      team.get("slug"),
            "matches_played": r.get("matches"),
            "wins":           r.get("wins"),
            "draws":          r.get("draws"),
            "losses":         r.get("losses"),
            "goals_for":      gf,
            "goals_against":  ga,
            "goal_diff":      gf - ga,
            "points":         r.get("points"),
        })

    df = pd.DataFrame(rows).sort_values("position").reset_index(drop=True)

    out_path = config.standings_file(season)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"✅ Tabla guardada: {out_path}  ({len(df)} equipos)")

    # Mostrar posición de Chaco
    chaco_row = df[df["team_id"] == config.CHACO_TEAM_ID]
    if not chaco_row.empty:
        r = chaco_row.iloc[0]
        print(f"\nChaco For Ever: {int(r['position'])}° | "
              f"{int(r['wins'])}V-{int(r['draws'])}E-{int(r['losses'])}D | "
              f"Pts: {int(r['points'])} | GD: {int(r['goal_diff'])}")

    return df


def load_standings(season=None):
    """Carga standings desde CSV local (sin hacer scraping)."""
    path = config.standings_file(season)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)
