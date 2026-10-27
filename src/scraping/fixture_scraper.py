"""
fixture_scraper.py
===================
Descarga el calendario COMPLETO de la Primera Nacional (Zona A + Zona B,
partidos jugados y por jugar) desde SofaScore, fecha por fecha.

El torneo real son 36 equipos (18 por zona) en un único `uniqueTournament`
de SofaScore, con fechas interzonales mezcladas en el calendario. El
endpoint de fecha devuelve el fixture completo de esa jornada (las 36
plazas) incluso para fechas que todavía no se jugaron (status "notstarted"),
así que sirve tanto para reconstruir el historial como para saber qué
partidos faltan.

Endpoint: /api/v1/unique-tournament/{tid}/season/{sid}/events/round/{round}
Guarda en: data/temporadas/{season}/fixture.csv

Uso:
    from src.scraping.fixture_scraper import fetch_fixture
    df = fetch_fixture(season="2026")
"""

import os
import time
import random
from datetime import datetime, timezone

import pandas as pd

import config
from src.scraping.chaco_scraper import SofascoreClient

MAX_ROUNDS = 40  # techo de seguridad; el torneo real corta antes (None del endpoint)


def _parse_round_events(data):
    events = data.get("events", []) if isinstance(data, dict) else []
    rows = []
    for e in events:
        home = e.get("homeTeam", {}) or {}
        away = e.get("awayTeam", {}) or {}
        hs = e.get("homeScore", {}) or {}
        aws = e.get("awayScore", {}) or {}
        status = e.get("status", {}) or {}
        round_info = e.get("roundInfo", {}) or {}
        tournament = e.get("tournament", {}) or {}
        ts = e.get("startTimestamp")
        start_iso = (
            datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            if isinstance(ts, (int, float)) else None
        )
        rows.append({
            "event_id":      e.get("id"),
            "round":         round_info.get("round"),
            # Nombre del sub-torneo devuelto por SofaScore (ej. "Liga
            # Profesional de Fútbol, Apertura" vs "..., Clausura"). En
            # Primera Nacional es constante; en LPF distingue la etapa,
            # porque el endpoint de fecha mezcla Apertura y Clausura bajo el
            # mismo número de round.
            "stage":         tournament.get("name"),
            "start_time_utc": start_iso,
            "status_type":   status.get("type"),
            "status_desc":   status.get("description"),
            "home_team_id":  home.get("id"),
            "home_team":     home.get("name"),
            "away_team_id":  away.get("id"),
            "away_team":     away.get("name"),
            "home_score":    hs.get("current"),
            "away_score":    aws.get("current"),
        })
    return rows


def fetch_tournament_fixture(tournament_id, season_id, out_path, max_rounds=MAX_ROUNDS,
                              headless=True, verbose=True):
    """
    Núcleo genérico: baja el calendario completo de CUALQUIER torneo/temporada
    de SofaScore recorriendo fecha por fecha, hasta que el endpoint deja de
    devolver datos. Reusado por fetch_fixture() (Primera Nacional) y por
    src/scraping/lpf_scraper.py (Liga Profesional).
    """
    all_rows = []
    with SofascoreClient(headless=headless) as client:
        for round_num in range(1, max_rounds + 1):
            path = (f"api/v1/unique-tournament/{tournament_id}"
                     f"/season/{season_id}/events/round/{round_num}")
            data = client.get_json(path)
            if data is None:
                if verbose:
                    print(f"  fecha {round_num:>2}: sin datos (fin del calendario)")
                break
            rows = _parse_round_events(data)
            all_rows.extend(rows)
            if verbose:
                n_done = sum(1 for r in rows if r["status_type"] == "finished")
                print(f"  fecha {round_num:>2}: {len(rows)} partidos "
                      f"({n_done} jugados, {len(rows) - n_done} pendientes/otros)")
            time.sleep(random.uniform(config.MIN_DELAY, config.MAX_DELAY))

    if not all_rows:
        print("No se pudo obtener el calendario.")
        return None

    df = pd.DataFrame(all_rows).drop_duplicates(subset="event_id").reset_index(drop=True)
    df = df.sort_values(["round", "start_time_utc"]).reset_index(drop=True)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8")
    if verbose:
        n_finished = (df["status_type"] == "finished").sum()
        n_teams = len(set(df["home_team_id"]) | set(df["away_team_id"]))
        print(f"\nCalendario guardado: {out_path}  "
              f"({len(df)} partidos, {n_finished} jugados, {n_teams} equipos)")
    return df


def fetch_fixture(season=None, headless=False, max_rounds=MAX_ROUNDS, verbose=True):
    """
    Baja el calendario completo (36 equipos, Zona A + Zona B) de la Primera
    Nacional para la temporada dada, recorriendo fecha por fecha. Guarda el
    CSV y devuelve el DataFrame. Incluye partidos jugados y por jugar.
    """
    season = season or config.CURRENT_SEASON
    season_id = config.SEASON_IDS.get(season)
    if not season_id:
        print(f"No hay season_id configurado para temporada '{season}'.")
        return None

    return fetch_tournament_fixture(
        config.UNIQUE_TOURNAMENT_ID, season_id, config.fixture_file(season),
        max_rounds=max_rounds, headless=headless, verbose=verbose,
    )


def load_fixture(season=None):
    """Carga el calendario desde CSV local (sin hacer scraping)."""
    path = config.fixture_file(season)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def zona_a_team_ids(season=None):
    """IDs de los 18 equipos de Zona A, leídos de standings.csv (la fuente más
    confiable: la tabla oficial de la zona, sin mezclar rivales interzonales)."""
    from src.scraping.standings_scraper import load_standings
    st = load_standings(season)
    if st is None or st.empty:
        return set()
    return set(int(x) for x in st["team_id"].dropna())


def remaining_fixture_zona_a(season=None):
    """Partidos NO terminados (por jugar o postergados) donde interviene al
    menos un equipo de Zona A — incluye los interzonales de equipos de Zona A
    contra rivales de Zona B, que también suman a la tabla de Zona A.

    Dos correcciones sobre el calendario crudo de SofaScore:

    1. Un partido postergado suele quedar en el calendario con SU FECHA
       ORIGINAL en estado "postponed" (event_id viejo) aunque ya se haya
       jugado reprogramado bajo otro event_id ("finished"). Ese "fantasma"
       nunca pasa a "finished" ni a "canceled" — si no se filtra, el partido
       se cuenta como pendiente cuando en realidad ya se jugó. Se descarta
       cualquier fila no terminada cuyo par exacto (local, visitante) YA
       tenga un partido "finished" en el calendario completo.
    2. Sobre lo que queda, puede haber más de una fila pendiente para el
       mismo par exacto (dos reprogramaciones sucesivas) — se deduplica
       quedándose con la fecha más reciente."""
    fx = load_fixture(season)
    if fx is None or fx.empty:
        return fx
    zona_a = zona_a_team_ids(season)

    finished = fx[fx["status_type"] == "finished"]
    pares_jugados = set(zip(finished["home_team_id"], finished["away_team_id"]))
    ya_jugado = fx.apply(
        lambda r: (r["home_team_id"], r["away_team_id"]) in pares_jugados, axis=1)

    en_zona_a = fx["home_team_id"].isin(zona_a) | fx["away_team_id"].isin(zona_a)
    # "inprogress" NO es un partido por jugar: se está jugando ahora y su
    # resultado ya está (o va a estar en minutos) en standings.csv. Si se
    # simulara, esos puntos se contarían dos veces, una en la tabla base y
    # otra en la simulación. Pasó el 2026-08-21 con Madryn - Mitre.
    pendiente = ~fx["status_type"].isin(["finished", "canceled", "inprogress"])
    rem = fx[en_zona_a & pendiente & ~ya_jugado].copy()
    rem = rem.sort_values("start_time_utc").drop_duplicates(
        subset=["home_team_id", "away_team_id"], keep="last")
    return rem.reset_index(drop=True)


if __name__ == "__main__":
    fetch_fixture()
