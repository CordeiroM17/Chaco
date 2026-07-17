"""
post_match.py
=============
Análisis profundo de un partido individual.
Diseñado para usarse después de scrapear el partido con chaco_scraper.fetch_match().
"""

import os
import pandas as pd
import numpy as np

import config
from src.analysis.season import is_home_match, get_opponent, get_match_date, compute_score_from_incidents, get_result


def load_match_data(match_key, season=None):
    """
    Carga todos los CSVs disponibles de un partido.

    Retorna
    -------
    dict con claves: 'event', 'stats', 'lineups', 'incidents', 'shotmap',
                     'avg_positions', 'momentum', 'best_players', 'heatmaps'
    Cualquier archivo no encontrado retorna None en su clave.
    """
    base_dir = config.season_data_dir(season)
    match_dir = os.path.join(base_dir, match_key)

    def _load(filename):
        path = os.path.join(match_dir, filename)
        return pd.read_csv(path) if os.path.exists(path) else None

    return {
        "event":         _load("event_clean.csv"),
        "stats":         _load("statistics_clean.csv"),
        "lineups":       _load("lineups_clean.csv"),
        "incidents":     _load("incidents_clean.csv"),
        "shotmap":       _load("shotmap_clean.csv"),
        "avg_positions": _load("average_positions_clean.csv"),
        "momentum":      _load("momentum_clean.csv"),
        "best_players":  _load("best_players_clean.csv"),
        "heatmaps":      _load("player_heatmaps_clean.csv"),
    }


def xg_analysis(match_key, data=None, season=None):
    """
    Compara xG vs goles reales. Indica si el resultado fue justo.

    Retorna dict con: chaco_xg, rival_xg, chaco_goals, rival_goals,
                      chaco_xg_diff, rival_xg_diff, verdict
    """
    if data is None:
        data = load_match_data(match_key, season)

    home_match = is_home_match(match_key)
    chaco_g, rival_g = compute_score_from_incidents(match_key, config.season_data_dir(season))

    df_sh = data.get("shotmap")
    if df_sh is None or df_sh.empty:
        return None

    chaco_xg = round(df_sh[df_sh["isHome"] == home_match]["xg"].sum(), 2)
    rival_xg  = round(df_sh[df_sh["isHome"] != home_match]["xg"].sum(), 2)

    chaco_diff = round((chaco_g or 0) - chaco_xg, 2)
    rival_diff  = round((rival_g  or 0) - rival_xg,  2)

    result = get_result(chaco_g, rival_g)
    chaco_deserved = "ganó" if chaco_xg > rival_xg else ("empató" if abs(chaco_xg - rival_xg) < 0.3 else "perdió")
    verdict = f"Chaco {chaco_deserved} en xG ({chaco_xg:.2f} vs {rival_xg:.2f})"
    if result == "W" and chaco_xg < rival_xg:
        verdict += " — victoria por encima del xG"
    elif result == "L" and chaco_xg > rival_xg:
        verdict += " — derrota injusta según xG"

    return {
        "chaco_xg":    chaco_xg,
        "rival_xg":    rival_xg,
        "chaco_goals": chaco_g,
        "rival_goals": rival_g,
        "chaco_xg_diff": chaco_diff,
        "rival_xg_diff": rival_diff,
        "verdict":     verdict,
    }


def player_performance_table(match_key, data=None, season=None):
    """
    Tabla completa de jugadores de Chaco con sus métricas del partido.
    Combina lineups_clean (rating, stats) y shotmap (xG individual).
    """
    if data is None:
        data = load_match_data(match_key, season)

    df_lin = data.get("lineups")
    df_sh  = data.get("shotmap")

    if df_lin is None or df_lin.empty:
        return pd.DataFrame()

    home_match = is_home_match(match_key)
    chaco_side = "home" if home_match else "away"
    chaco = df_lin[df_lin["team_side"] == chaco_side].copy()

    # xG individual desde shotmap
    if df_sh is not None and not df_sh.empty:
        chaco_shots = df_sh[df_sh["isHome"] == home_match]
        xg_by_player = chaco_shots.groupby("player_name")["xg"].sum().round(3)
        shots_by_player = chaco_shots.groupby("player_name").size()
        chaco["xg_shotmap"] = chaco["player_name"].map(xg_by_player).fillna(0)
        chaco["shots"]      = chaco["player_name"].map(shots_by_player).fillna(0)
    else:
        chaco["xg_shotmap"] = 0
        chaco["shots"] = 0

    keep_cols = [
        "player_name", "position", "is_starter", "minutes_played", "rating",
        "goals", "assists", "shots", "xg_shotmap", "xa",
        "key_passes", "total_passes", "accurate_passes",
        "tackles", "interceptions", "duels_won", "duels_lost",
        "yellow_cards", "red_cards", "substitute_in", "substitute_out",
    ]
    available = [c for c in keep_cols if c in chaco.columns]
    result = chaco[available].copy()
    result["rating"] = pd.to_numeric(result["rating"], errors="coerce")
    return result.sort_values("rating", ascending=False, na_position="last").reset_index(drop=True)


def substitution_impact(match_key, data=None, season=None):
    """
    Para cada cambio de Chaco, calcula el xG generado antes y después.
    Útil para evaluar si los cambios mejoraron el rendimiento ofensivo.
    """
    if data is None:
        data = load_match_data(match_key, season)

    df_inc = data.get("incidents")
    df_sh  = data.get("shotmap")

    if df_inc is None or df_sh is None or df_sh.empty:
        return pd.DataFrame()

    home_match = is_home_match(match_key)
    subs = df_inc[
        (df_inc["type"] == "substitution") &
        (df_inc["is_home"] == home_match)
    ].copy()

    if subs.empty:
        return pd.DataFrame()

    subs["minute"] = pd.to_numeric(subs["minute"], errors="coerce")
    sub_minutes = sorted(subs["minute"].dropna().tolist())

    chaco_shots = df_sh[df_sh["isHome"] == home_match].copy()
    chaco_shots["time"] = pd.to_numeric(chaco_shots["time"], errors="coerce")

    rows = []
    breakpoints = [0] + sub_minutes + [95]
    for i in range(len(breakpoints) - 1):
        start, end = breakpoints[i], breakpoints[i + 1]
        phase = chaco_shots[(chaco_shots["time"] >= start) & (chaco_shots["time"] < end)]
        change_info = subs[subs["minute"] == end].iloc[0] if end in sub_minutes else None
        rows.append({
            "phase":        f"{int(start)}'–{int(end)}'",
            "shots":        len(phase),
            "xg":           round(phase["xg"].sum(), 3),
            "player_in":    change_info["player"] if change_info is not None else "—",
            "player_out":   str(change_info.get("description", "")).replace("OUT: ", "") if change_info is not None else "—",
        })

    return pd.DataFrame(rows)


def momentum_phases(match_key, data=None, season=None, window=5):
    """
    Identifica fases del partido según el momentum (ventana deslizante).
    Retorna DataFrame con: phase_start, phase_end, avg_momentum, label
    Labels: 'Chaco domina', 'Equilibrado', 'Rival domina'
    """
    if data is None:
        data = load_match_data(match_key, season)

    df_mom = data.get("momentum")
    if df_mom is None or df_mom.empty:
        return pd.DataFrame()

    df = df_mom.copy()
    df["minute"] = pd.to_numeric(df.get("minute", df.columns[0]), errors="coerce")
    df["value"]  = pd.to_numeric(df.get("value",  df.columns[1]), errors="coerce")
    df = df.dropna().sort_values("minute")

    home_match = is_home_match(match_key)
    # Positivo = local domina. Si Chaco es visitante, invertimos.
    if not home_match:
        df["value"] = -df["value"]

    df["smooth"] = df["value"].rolling(window=window, center=True).mean()
    df["label"]  = df["smooth"].apply(
        lambda v: "Chaco domina" if v > 0.1 else ("Rival domina" if v < -0.1 else "Equilibrado")
    )

    return df[["minute", "value", "smooth", "label"]]


def xg_by_phase(match_key, data=None, season=None, bin_size=15):
    """
    xG acumulado por tramos de tiempo (default 15') para Chaco y el rival.

    Retorna DataFrame con: phase (ej. "0-15'"), chaco_xg, rival_xg,
                           chaco_shots, rival_shots
    """
    if data is None:
        data = load_match_data(match_key, season)

    df_sh = data.get("shotmap")
    if df_sh is None or df_sh.empty:
        return pd.DataFrame()

    home_match = is_home_match(match_key)
    df = df_sh.copy()
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["xg"]   = pd.to_numeric(df["xg"],   errors="coerce").fillna(0)
    df = df.dropna(subset=["time"])

    max_min = max(90, int(df["time"].max()))
    bins = list(range(0, max_min + bin_size, bin_size))

    rows = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        seg = df[(df["time"] > lo) & (df["time"] <= hi)]
        chaco = seg[seg["isHome"] == home_match]
        rival = seg[seg["isHome"] != home_match]
        rows.append({
            "phase":       f"{lo}-{hi}'",
            "phase_start": lo,
            "chaco_xg":    round(chaco["xg"].sum(), 2),
            "rival_xg":    round(rival["xg"].sum(), 2),
            "chaco_shots": len(chaco),
            "rival_shots": len(rival),
        })
    return pd.DataFrame(rows)


def defensive_actions_table(match_key, data=None, season=None, min_minutes=15):
    """
    Acciones defensivas por jugador de Chaco (estilo WhoScored, sin coordenadas):
    quites, intercepciones, despejes, duelos ganados/perdidos, faltas.

    Retorna DataFrame ordenado por acciones defensivas totales.
    """
    if data is None:
        data = load_match_data(match_key, season)

    df_lin = data.get("lineups")
    if df_lin is None or df_lin.empty:
        return pd.DataFrame()

    home_match = is_home_match(match_key)
    chaco_side = "home" if home_match else "away"
    df = df_lin[df_lin["team_side"] == chaco_side].copy()

    cols = ["tackles", "interceptions", "clearances", "duels_won", "duels_lost",
            "aerial_duels_won", "aerial_duels_lost", "fouls", "minutes_played"]
    for c in cols:
        df[c] = pd.to_numeric(df.get(c), errors="coerce").fillna(0)

    df = df[df["minutes_played"] >= min_minutes].copy()
    if df.empty:
        return pd.DataFrame()

    df["def_actions"] = df["tackles"] + df["interceptions"] + df["clearances"]
    total_duels = df["duels_won"] + df["duels_lost"]
    df["duels_pct"] = np.where(total_duels > 0,
                               (df["duels_won"] / total_duels * 100).round(1), 0)

    out_cols = ["player_name", "position", "minutes_played", "tackles",
                "interceptions", "clearances", "def_actions",
                "duels_won", "duels_lost", "duels_pct",
                "aerial_duels_won", "aerial_duels_lost", "fouls"]
    return (df[out_cols]
            .sort_values("def_actions", ascending=False)
            .reset_index(drop=True))
