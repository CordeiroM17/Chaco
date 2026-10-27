"""
audit.py
========
Auditoría de qué partidos quedaron incompletos en el scraping y por qué.

Un partido "incompleto" es uno donde SofaScore devolvió los datos base
(event/lineups/incidents) pero NO alguno de los endpoints de análisis
(statistics, shotmap, average_positions, graph, best_players) — típicamente
partidos de menor cobertura que SofaScore no analiza en detalle.

Se lee del manifiesto por partido (raw/_scrape_state.json, ver chaco_scraper.py),
sin tocar la red. Los partidos viejos sin manifiesto se resuelven con
_backfill_state().

Uso:
    from src.scraping.audit import print_audit
    print_audit("2026")            # Chaco + rivales + LPF de 2026
    df = audit_incomplete("2026")  # DataFrame para trabajar
"""
import os

import pandas as pd

import config
from src.scraping.chaco_scraper import (
    BASE_ENDPOINTS, ANALYSIS_ENDPOINTS, _load_state, _backfill_state, _match_age_days,
)


def _scan_team(scope, team, matches_root):
    rows = []
    if not os.path.isdir(matches_root):
        return rows
    for mk in sorted(os.listdir(matches_root)):
        md = os.path.join(matches_root, mk)
        if not os.path.isdir(md) or not os.path.isdir(os.path.join(md, "raw")):
            continue
        state = _load_state(md) or _backfill_state(md) or {}
        falta_base = [e for e in BASE_ENDPOINTS if state.get(e) != "ok"]
        sin_pedir  = [e for e in ANALYSIS_ENDPOINTS if state.get(e) not in ("ok", "empty")]
        no_public  = [e for e in ANALYSIS_ENDPOINTS if state.get(e) == "empty"]
        if not (falta_base or sin_pedir or no_public):
            continue
        rows.append({
            "scope":        scope,
            "equipo":       team,
            "match_key":    mk,
            "fecha":        mk[:10],
            "falta_base":   ",".join(falta_base),
            "sin_pedir":    ",".join(sin_pedir),
            "no_publicado": ",".join(no_public),
            "dias":         _match_age_days(md),
        })
    return rows


def audit_incomplete(season=None, scope="all"):
    """DataFrame de partidos con algún endpoint sin resolver.

    scope: "all" | "chaco" | "rivals" | "lpf".
    """
    season = season or config.CURRENT_SEASON
    rows = []
    if scope in ("all", "chaco"):
        rows += _scan_team("chaco", "Chaco For Ever", config.season_data_dir(season))
    if scope in ("all", "rivals"):
        rroot = config.rivals_dir(season)
        if os.path.isdir(rroot):
            for slug in sorted(os.listdir(rroot)):
                rows += _scan_team("rival", slug, os.path.join(rroot, slug))
    if scope in ("all", "lpf"):
        lroot = os.path.dirname(config.lpf_team_dir("x", season))
        if os.path.isdir(lroot):
            for slug in sorted(os.listdir(lroot)):
                rows += _scan_team("lpf", slug, os.path.join(lroot, slug))
    return pd.DataFrame(rows)


def print_audit(season=None, scope="all", recientes_dias=7):
    """Imprime la auditoría agrupada por causa y devuelve el DataFrame."""
    df = audit_incomplete(season, scope)
    if df.empty:
        print(f"Temporada {season or config.CURRENT_SEASON}: todo completo — "
              f"no hay partidos con endpoints sin resolver.")
        return df

    rotos    = df[df["falta_base"] != ""]
    resto    = df[df["falta_base"] == ""]
    recientes = resto[(resto["sin_pedir"] != "") &
                      (resto["dias"].fillna(999) <= recientes_dias)]
    sin_analisis = resto[~resto.index.isin(recientes.index)]

    if not rotos.empty:
        print("\n=== FALTA DATA BASE — revisar el link en SofaScore ===")
        print("   (event/lineups/incidents incompletos: el partido puede no tener")
        print("    página, estar sin cargar, o haberse bajado mal)")
        for _, r in rotos.iterrows():
            print(f"  · [{r['scope']}] {r['equipo']}/{r['match_key']}   falta: {r['falta_base']}")

    if not recientes.empty:
        print(f"\n=== PENDIENTE DE REINTENTO — partido de los últimos {recientes_dias} días ===")
        print("   (SofaScore suele cargar el shotmap/posiciones un par de días después;")
        print("    reintentar con retry_empty=True más adelante)")
        for _, r in recientes.iterrows():
            print(f"  · [{r['scope']}] {r['equipo']}/{r['match_key']}   ({r['dias']}d)   sin: {r['sin_pedir']}")

    if not sin_analisis.empty:
        print("\n=== SIN ANÁLISIS EN SOFASCORE — no van a tener shotmap ===")
        print("   (partidos de menor cobertura; revisá el link solo si te interesa ese partido)")
        for _, r in sin_analisis.iterrows():
            falta = r["sin_pedir"] or r["no_publicado"]
            print(f"  · [{r['scope']}] {r['equipo']}/{r['match_key']}   no publicado: {falta}")

    print(f"\nTotal: {len(df)} partidos con algo sin resolver "
          f"({len(rotos)} con data base rota, {len(recientes)} a reintentar, "
          f"{len(sin_analisis)} sin análisis en SofaScore).")
    return df
