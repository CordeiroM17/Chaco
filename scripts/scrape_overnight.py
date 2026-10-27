"""
scrape_overnight.py
====================
Driver para dejar corriendo sin supervisión el scraping de:
  1. Standings Zona B de Primera Nacional (instantáneo)
  2. Standings + fixture completo de Liga Profesional (instantáneo)
  3. Partidos completos de los 18 equipos de Zona B (Primera Nacional)
  4. Partidos completos de los 30 equipos de Liga Profesional

Cada paso es idempotente: si se corta a la mitad, correr el script de nuevo
retoma donde quedó sin repetir requests ya hechos (scrape_rival_recent
saltea partidos ya bajados). Por eso conviene lanzarlo con
`Start-Process` (detached) y dejarlo las veces que haga falta — un solo
"toda la noche" no alcanza para el volumen completo (~350 partidos de Zona B
+ ~900 de LPF), va a necesitar varias corridas.

Uso:
    venv\\Scripts\\python.exe scripts\\scrape_overnight.py
"""

import os
import sys
import time
import traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.scraping.standings_scraper import fetch_standings_zona_b
from src.scraping.lpf_scraper import fetch_standings_lpf, fetch_fixture_lpf, scrape_team_lpf
from src.scraping.rivals_scraper import scrape_rival_recent

SEASON = "2026"


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def step(name, fn):
    log(f"--- INICIO: {name} ---")
    try:
        fn()
        log(f"--- OK: {name} ---")
    except Exception as e:
        log(f"--- ERROR en {name}: {e} ---")
        traceback.print_exc()


def run():
    log("======== scrape_overnight arrancó ========")

    step("standings Zona B (Primera Nacional)",
         lambda: fetch_standings_zona_b(season=SEASON, headless=True))

    step("standings Liga Profesional (6 tablas)",
         lambda: fetch_standings_lpf(season=SEASON, headless=True))

    step("fixture Liga Profesional (Apertura+Clausura+playoffs)",
         lambda: fetch_fixture_lpf(season=SEASON, headless=True))

    # --- Zona B: partidos completos de los 18 equipos ---
    zona_b_slugs = list(config.RIVALS_ZONA_B_2026.keys())
    log(f"Zona B: {len(zona_b_slugs)} equipos a scrapear")
    for i, slug in enumerate(zona_b_slugs):
        name = config.RIVALS_ZONA_B_2026[slug]["name"]
        step(f"Zona B [{i+1}/{len(zona_b_slugs)}] {name} ({slug})",
             lambda slug=slug: scrape_rival_recent(
                 slug, season=SEASON, headless=True, include_heatmaps=True))

    # --- Liga Profesional: partidos completos de los 30 equipos ---
    lpf_slugs = list(config.LPF_TEAMS_2026.keys())
    log(f"Liga Profesional: {len(lpf_slugs)} equipos a scrapear")
    for i, slug in enumerate(lpf_slugs):
        name = config.LPF_TEAMS_2026[slug]["name"]
        step(f"LPF [{i+1}/{len(lpf_slugs)}] {name} ({slug})",
             lambda slug=slug: scrape_team_lpf(
                 slug, season=SEASON, headless=True, include_heatmaps=True))

    log("======== scrape_overnight terminó TODO ========")


if __name__ == "__main__":
    run()
