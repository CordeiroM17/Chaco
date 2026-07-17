"""
pre_match.py
============
Análisis pre-partido: forma reciente de Chaco, scouting del rival,
head-to-head y perfil táctico.

Requiere que rivals_scraper haya descargado los partidos del rival antes
de llamar a las funciones de análisis del rival.
"""

import os
import re
import json
import pandas as pd
import numpy as np

import config
from src.analysis.season import (
    is_home_match, get_result, compute_score_from_incidents,
    get_opponent, get_match_date, build_season_table, load_matches,
    season_player_stats, markov_game_state,
)


# ─── Forma reciente de Chaco ─────────────────────────────────────────────────

def chaco_recent_form(n=5, season=None):
    """
    Últimos N partidos de Chaco (desde los datos ya scrapeados).

    Retorna DataFrame con: match_key, date, opponent, venue, result,
                           chaco_goals, rival_goals, chaco_xg, rival_xg
    """
    season = season or config.CURRENT_SEASON
    base_dir = config.season_data_dir(season)
    matches = load_matches(season)

    rows = []
    for mk in matches:
        event_path = os.path.join(base_dir, mk, "event_clean.csv")
        if not os.path.exists(event_path):
            continue
        home_match = is_home_match(mk)
        chaco_g, rival_g = compute_score_from_incidents(mk, base_dir)

        shot_path = os.path.join(base_dir, mk, "shotmap_clean.csv")
        chaco_xg = rival_xg = None
        if os.path.exists(shot_path):
            df_sh = pd.read_csv(shot_path)
            chaco_xg = round(df_sh[df_sh["isHome"] == home_match]["xg"].sum(), 2)
            rival_xg  = round(df_sh[df_sh["isHome"] != home_match]["xg"].sum(), 2)

        rows.append({
            "match_key":   mk,
            "date":        get_match_date(mk),
            "opponent":    get_opponent(mk),
            "venue":       "Local" if home_match else "Visitante",
            "chaco_goals": chaco_g,
            "rival_goals": rival_g,
            "result":      get_result(chaco_g, rival_g),
            "chaco_xg":    chaco_xg,
            "rival_xg":    rival_xg,
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).sort_values("date")
    return df.tail(n).reset_index(drop=True)


def chaco_form_summary(form_df):
    """Estadísticas de la forma reciente de Chaco."""
    if form_df.empty:
        return {}
    return {
        "partidos":      len(form_df),
        "victorias":     (form_df["result"] == "W").sum(),
        "empates":       (form_df["result"] == "D").sum(),
        "derrotas":      (form_df["result"] == "L").sum(),
        "goles_favor":   form_df["chaco_goals"].sum(),
        "goles_contra":  form_df["rival_goals"].sum(),
        "xg_favor":      form_df["chaco_xg"].mean().round(2) if "chaco_xg" in form_df else None,
        "xg_contra":     form_df["rival_xg"].mean().round(2) if "rival_xg" in form_df else None,
        "forma_str":     "".join(form_df["result"].tolist()),
    }


# ─── Forma del rival ─────────────────────────────────────────────────────────

def rival_match_keys(rival_slug, season=None):
    """Carga todos los partidos scrapeados del rival."""
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    if not os.path.isdir(rival_dir):
        return []
    return [
        d for d in sorted(os.listdir(rival_dir))
        if os.path.isdir(os.path.join(rival_dir, d))
    ]


def rival_form(rival_slug, season=None):
    """
    Últimos partidos del rival (desde datos de rivals_scraper).

    Retorna DataFrame con: match_key, date, rival_played, venue,
                           goals_for, goals_against, result, xg_for, xg_against
    """
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    rival_info = config.RIVALS.get(rival_slug, {})
    rival_id = rival_info.get("id")

    match_dirs = rival_match_keys(rival_slug, season)
    if not match_dirs:
        return pd.DataFrame()

    rows = []
    for mk in match_dirs:
        match_path = os.path.join(rival_dir, mk)

        # Determinar quién es el rival y si juega de local
        is_home = mk.endswith("_h")  # el rival era local
        date_str = re.match(r"(\d{4}-\d{2}-\d{2})", mk)
        date_str = date_str.group(1) if date_str else mk

        # Cargar incidents para el marcador
        inc_path = os.path.join(match_path, "incidents_clean.csv")
        gf = ga = None
        if os.path.exists(inc_path):
            df_inc = pd.read_csv(inc_path)
            goals = df_inc[df_inc["type"] == "goal"]
            gf = len(goals[goals["is_home"] == is_home])
            ga = len(goals[goals["is_home"] != is_home])

        # xG desde shotmap
        xg_for = xg_against = None
        sh_path = os.path.join(match_path, "shotmap_clean.csv")
        if os.path.exists(sh_path):
            df_sh = pd.read_csv(sh_path)
            xg_for     = round(df_sh[df_sh["isHome"] == is_home]["xg"].sum(), 2)
            xg_against = round(df_sh[df_sh["isHome"] != is_home]["xg"].sum(), 2)

        opponent_raw = mk.split("_vs_", 1)[1].rsplit("_", 1)[0].replace("_", " ").title() if "_vs_" in mk else "?"

        rows.append({
            "match_key":     mk,
            "date":          date_str,
            "opponent":      opponent_raw,
            "venue":         "Local" if is_home else "Visitante",
            "goals_for":     gf,
            "goals_against": ga,
            "result":        get_result(gf, ga) if gf is not None else "?",
            "xg_for":        xg_for,
            "xg_against":    xg_against,
        })

    df = pd.DataFrame(rows).sort_values("date", ascending=True).reset_index(drop=True)
    return df


def rival_form_summary(form_df):
    """Estadísticas de la forma reciente del rival."""
    if form_df.empty:
        return {}
    return {
        "partidos":     len(form_df),
        "victorias":    (form_df["result"] == "W").sum(),
        "empates":      (form_df["result"] == "D").sum(),
        "derrotas":     (form_df["result"] == "L").sum(),
        "goles_favor":  form_df["goals_for"].sum(),
        "goles_contra": form_df["goals_against"].sum(),
        "xg_favor":     form_df["xg_for"].mean().round(2) if "xg_for" in form_df else None,
        "xg_contra":    form_df["xg_against"].mean().round(2) if "xg_against" in form_df else None,
        "forma_str":    "".join(form_df["result"].tolist()),
    }


# ─── Perfil táctico del rival ─────────────────────────────────────────────────

def rival_tactical_profile(rival_slug, season=None):
    """
    Promedio de métricas de equipo del rival en los partidos scrapeados.
    Indica si el rival tiende a dominar posesión, presionar alto, etc.
    """
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    match_dirs = rival_match_keys(rival_slug, season)

    if not match_dirs:
        return {}

    all_stats = []
    for mk in match_dirs:
        stats_path = os.path.join(rival_dir, mk, "statistics_clean.csv")
        if not os.path.exists(stats_path):
            continue
        df_st = pd.read_csv(stats_path)
        is_home = mk.endswith("_h")
        rival_col = "home_val" if is_home else "away_val"

        match_stats = {}
        for _, row in df_st.iterrows():
            metric = row.get("metric", "")
            val = row.get(rival_col)
            if val is not None:
                try:
                    match_stats[metric] = float(val)
                except (ValueError, TypeError):
                    pass
        if match_stats:
            all_stats.append(match_stats)

    if not all_stats:
        return {}

    df_all = pd.DataFrame(all_stats)
    profile = {}
    for col in df_all.columns:
        vals = df_all[col].dropna()
        if not vals.empty:
            profile[col] = round(vals.mean(), 2)

    return profile


# ─── Jugadores clave del rival ────────────────────────────────────────────────

def rival_key_players(rival_slug, season=None, top_n=7):
    """
    Jugadores más destacados del rival en sus últimos partidos.
    Retorna DataFrame con: player_name, team_side, avg_rating, goals, assists,
                           avg_xg, matches_played
    """
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    rival_info = config.RIVALS.get(rival_slug, {})
    match_dirs = rival_match_keys(rival_slug, season)

    if not match_dirs:
        return pd.DataFrame()

    all_players = []
    for mk in match_dirs:
        lin_path = os.path.join(rival_dir, mk, "lineups_clean.csv")
        sh_path  = os.path.join(rival_dir, mk, "shotmap_clean.csv")
        if not os.path.exists(lin_path):
            continue

        df_lin = pd.read_csv(lin_path)
        is_home = mk.endswith("_h")
        rival_side = "home" if is_home else "away"
        rival_players = df_lin[df_lin["team_side"] == rival_side].copy()

        if os.path.exists(sh_path):
            df_sh = pd.read_csv(sh_path)
            rival_shots = df_sh[df_sh["isHome"] == is_home]
            xg_map = rival_shots.groupby("player_name")["xg"].sum()
            rival_players["xg_shotmap"] = rival_players["player_name"].map(xg_map).fillna(0)
        else:
            rival_players["xg_shotmap"] = 0

        all_players.append(rival_players)

    if not all_players:
        return pd.DataFrame()

    df = pd.concat(all_players, ignore_index=True)
    df["rating"] = pd.to_numeric(df.get("rating"), errors="coerce")
    df["goals"]  = pd.to_numeric(df.get("goals"), errors="coerce").fillna(0)
    df["assists"]= pd.to_numeric(df.get("assists"), errors="coerce").fillna(0)

    agg = df.groupby("player_name").agg(
        avg_rating    =("rating",      "mean"),
        goals         =("goals",       "sum"),
        assists       =("assists",     "sum"),
        avg_xg        =("xg_shotmap",  "mean"),
        matches_played=("player_name", "count"),
    ).reset_index()
    agg["avg_rating"] = agg["avg_rating"].round(2)
    agg["avg_xg"]     = agg["avg_xg"].round(3)

    return agg.nlargest(top_n, "avg_rating").reset_index(drop=True)


# ─── Mejor once del rival ─────────────────────────────────────────────────────

def rival_best_xi(rival_slug, season=None):
    """
    El once que más repitió el rival en sus últimos partidos scrapeados: 1
    arquero (el de más titularidades) + los 10 jugadores de campo con más
    titularidades (empate se rompe por rating promedio). Es una aproximación
    razonable a "con qué equipo sale a jugar" — no es una alineación oficial
    del próximo partido, sale de los partidos que sí tenemos descargados.

    Devuelve un DataFrame de 11 filas: player_name, position, starts,
    matches_played, avg_rating, goals, assists, avg_minutes.
    """
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    match_dirs = rival_match_keys(rival_slug, season)
    if not match_dirs:
        return pd.DataFrame()

    all_players = []
    for mk in match_dirs:
        lin_path = os.path.join(rival_dir, mk, "lineups_clean.csv")
        if not os.path.exists(lin_path):
            continue
        df_lin = pd.read_csv(lin_path)
        rival_side = "home" if mk.endswith("_h") else "away"
        all_players.append(df_lin[df_lin["team_side"] == rival_side].copy())

    if not all_players:
        return pd.DataFrame()

    df = pd.concat(all_players, ignore_index=True)
    df["rating"] = pd.to_numeric(df.get("rating"), errors="coerce")
    df["goals"] = pd.to_numeric(df.get("goals"), errors="coerce").fillna(0)
    df["assists"] = pd.to_numeric(df.get("assists"), errors="coerce").fillna(0)
    df["minutes_played"] = pd.to_numeric(df.get("minutes_played"), errors="coerce").fillna(0)
    df["is_starter"] = df.get("is_starter", False).astype(bool)

    agg = df.groupby("player_name").agg(
        starts=("is_starter", "sum"),
        matches_played=("player_name", "count"),
        avg_rating=("rating", "mean"),
        goals=("goals", "sum"),
        assists=("assists", "sum"),
        avg_minutes=("minutes_played", "mean"),
        position=("position", lambda s: s.mode().iat[0] if not s.mode().empty else None),
    ).reset_index()
    agg["avg_rating"] = agg["avg_rating"].round(2)
    agg["avg_minutes"] = agg["avg_minutes"].round(0)

    # Cupos por línea según la formación más usada, para que el once salga
    # balanceado (con defensores, mediocampistas Y delanteros) en vez de los
    # 10 de campo con más titularidades a secas — así los delanteros, que
    # suelen rotar más, no quedan afuera del "mejor once".
    n_def, n_mid, n_fwd = _formation_line_counts(rival_slug, season)

    def _pick(pos, n, exclude):
        pool = agg[(agg["position"] == pos) & (~agg["player_name"].isin(exclude))]
        return pool.sort_values(["starts", "avg_rating"], ascending=False).head(n)

    keeper = agg[agg["position"] == "G"].sort_values(
        ["starts", "avg_rating"], ascending=False).head(1)

    chosen = [keeper]
    used = set(keeper["player_name"])
    for pos, n in (("D", n_def), ("M", n_mid), ("F", n_fwd)):
        pick = _pick(pos, n, used)
        used.update(pick["player_name"])
        chosen.append(pick)

    # Si alguna línea no llenó su cupo (faltan jugadores de esa posición en la
    # muestra), completar hasta 11 con los mejores de campo que queden.
    xi = pd.concat(chosen, ignore_index=True)
    if len(xi) < 11:
        resto = agg[(agg["position"] != "G") & (~agg["player_name"].isin(used))]
        resto = resto.sort_values(["starts", "avg_rating"], ascending=False)
        xi = pd.concat([xi, resto.head(11 - len(xi))], ignore_index=True)

    return xi


def _formation_line_counts(rival_slug, season=None, default=(4, 4, 2)):
    """Cupos (defensores, mediocampistas, delanteros) de la formación más
    usada por el rival. Para '4-2-3-1' -> D=4, F=1 (último), M=todo lo del
    medio (2+3=5). Si no hay dato, usa 4-4-2."""
    try:
        forms = rival_formations_used(rival_slug, season)
        vals = forms["formation"].dropna() if forms is not None else None
        if vals is None or vals.empty:
            return default
        top = vals.value_counts().index[0]
        nums = [int(x) for x in str(top).split("-") if x.strip().isdigit()]
        if len(nums) < 2:
            return default
        n_def = nums[0]
        n_fwd = nums[-1]
        n_mid = sum(nums[1:-1]) if len(nums) > 2 else 0
        # el arquero no cuenta; los de campo deben sumar 10
        if n_def + n_mid + n_fwd != 10:
            return default
        return n_def, n_mid, n_fwd
    except Exception:
        return default


def rival_formations_used(rival_slug, season=None):
    """
    Formaciones que usó el rival en cada uno de sus últimos partidos
    scrapeados (columna 'formation' de lineups_clean, la misma para todo el
    equipo en ese partido). Muestra variedad/preferencia táctica.

    Devuelve un DataFrame: match_key, date, opponent, formation.
    """
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    match_dirs = rival_match_keys(rival_slug, season)
    if not match_dirs:
        return pd.DataFrame()

    rows = []
    for mk in match_dirs:
        lin_path = os.path.join(rival_dir, mk, "lineups_clean.csv")
        if not os.path.exists(lin_path):
            continue
        df_lin = pd.read_csv(lin_path)
        is_home = mk.endswith("_h")
        rival_side = "home" if is_home else "away"
        team = df_lin[df_lin["team_side"] == rival_side]
        if team.empty:
            continue
        formation = team["formation"].iloc[0] if "formation" in team.columns else None
        date_str = re.match(r"(\d{4}-\d{2}-\d{2})", mk)
        opponent_raw = mk.split("_vs_", 1)[1].rsplit("_", 1)[0].replace("_", " ").title() \
            if "_vs_" in mk else "?"
        rows.append({
            "match_key": mk,
            "date": date_str.group(1) if date_str else mk,
            "opponent": opponent_raw,
            "formation": formation,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("date").reset_index(drop=True)
    return df


def rival_manager_timeline(rival_slug, season=None):
    """
    DT del rival partido a partido, en orden cronológico, a partir de los
    `raw/managers.json` cacheados (se bajan con
    scraping.rivals_scraper.scrape_rival_managers). Marca en qué partido hubo
    cambio de entrenador.

    Devuelve un DataFrame: match_key, date, opponent, manager, changed (bool).
    Vacío si todavía no se descargó ningún DT.
    """
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    match_dirs = rival_match_keys(rival_slug, season)
    if not match_dirs:
        return pd.DataFrame()

    rows = []
    for mk in match_dirs:
        mpath = os.path.join(rival_dir, mk, "raw", "managers.json")
        if not os.path.exists(mpath):
            continue
        data = json.load(open(mpath, encoding="utf-8"))
        key = "homeManager" if mk.endswith("_h") else "awayManager"
        manager = (data.get(key) or {}).get("name")
        date_str = re.match(r"(\d{4}-\d{2}-\d{2})", mk)
        opponent = mk.split("_vs_", 1)[1].rsplit("_", 1)[0].replace("_", " ").title() \
            if "_vs_" in mk else "?"
        rows.append({
            "match_key": mk,
            "date": date_str.group(1) if date_str else mk,
            "opponent": opponent,
            "manager": manager,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values("date").reset_index(drop=True)
    prev = df["manager"].shift(1)
    df["changed"] = df["manager"].notna() & prev.notna() & (df["manager"] != prev)
    return df


def rival_manager_summary(timeline_df):
    """
    Resume la timeline de DTs en spells (períodos de cada entrenador):
    lista de dicts {manager, from_date, to_date, matches}. El último de la
    lista es el DT actual (con los datos que tenemos). Colapsa repeticiones
    consecutivas del mismo DT en un solo spell.
    """
    if timeline_df is None or timeline_df.empty:
        return []
    spells = []
    for _, r in timeline_df.iterrows():
        m = r["manager"]
        if m is None:
            continue
        if spells and spells[-1]["manager"] == m:
            spells[-1]["to_date"] = r["date"]
            spells[-1]["matches"] += 1
        else:
            spells.append({"manager": m, "from_date": r["date"],
                           "to_date": r["date"], "matches": 1})
    return spells


# ─── Perfil disciplinario del rival ───────────────────────────────────────────

def rival_discipline_profile(rival_slug, season=None):
    """
    Perfil de faltas/tarjetas del rival en sus últimos partidos scrapeados.
    OJO: como solo se scrapean los últimos N partidos (no la temporada
    completa del rival), esto NO permite calcular a cuántas amarillas está de
    la suspensión (no sabemos su acumulado real de la temporada) — es una
    lectura de tendencia reciente ("¿son un equipo que se va mucho a la falta
    últimamente?"), no una alerta de suspensión.

    GOTCHA de datos: las columnas yellow_cards/red_cards de lineups_clean NO
    vienen pobladas cuando el partido se scrapeó vía rivals_scraper (a
    diferencia de los partidos propios de Chaco, donde sí). Por eso las
    tarjetas se cuentan de incidents_clean (type=='yellow'/'red', is_home,
    player) — esa sí es confiable en ambos casos. Solo 'fouls' sale de
    lineups_clean (esa columna sí está poblada).

    Devuelve (team_df, player_df):
      team_df:   match_key, date, opponent, fouls, yellow_cards, red_cards (por partido)
      player_df: player_name, position, yellow_cards, red_cards, matches_played
                 (top acumulado reciente, ordenado por tarjetas)
    """
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    match_dirs = rival_match_keys(rival_slug, season)
    if not match_dirs:
        return pd.DataFrame(), pd.DataFrame()

    team_rows = []
    all_players_pos = []
    card_rows = []
    for mk in match_dirs:
        lin_path = os.path.join(rival_dir, mk, "lineups_clean.csv")
        inc_path = os.path.join(rival_dir, mk, "incidents_clean.csv")
        if not os.path.exists(lin_path):
            continue
        df_lin = pd.read_csv(lin_path)
        is_home = mk.endswith("_h")
        rival_side = "home" if is_home else "away"
        team = df_lin[df_lin["team_side"] == rival_side].copy()
        if team.empty:
            continue

        fouls = pd.to_numeric(team.get("fouls"), errors="coerce").fillna(0)
        date_str = re.match(r"(\d{4}-\d{2}-\d{2})", mk)
        opponent_raw = mk.split("_vs_", 1)[1].rsplit("_", 1)[0].replace("_", " ").title() \
            if "_vs_" in mk else "?"

        yellow_n = red_n = 0
        if os.path.exists(inc_path):
            inc = pd.read_csv(inc_path)
            if "type" in inc.columns:
                rival_cards = inc[inc["type"].isin(["yellow", "red"])
                                  & (inc["is_home"] == is_home)]
                yellow_n = int((rival_cards["type"] == "yellow").sum())
                red_n = int((rival_cards["type"] == "red").sum())
                for _, r in rival_cards.iterrows():
                    name = str(r.get("player", "")).strip()
                    if name and name.lower() != "nan":
                        card_rows.append({"player_name": name, "type": r["type"]})

        team_rows.append({
            "match_key": mk,
            "date": date_str.group(1) if date_str else mk,
            "opponent": opponent_raw,
            "fouls": int(fouls.sum()),
            "yellow_cards": yellow_n,
            "red_cards": red_n,
        })
        all_players_pos.append(team[["player_name", "position"]])

    team_df = pd.DataFrame(team_rows)
    if not team_df.empty:
        team_df = team_df.sort_values("date").reset_index(drop=True)

    if not card_rows or not all_players_pos:
        return team_df, pd.DataFrame()

    apps = pd.concat(all_players_pos, ignore_index=True)
    pos_map = apps.drop_duplicates("player_name").set_index("player_name")["position"]
    matches_played = apps.groupby("player_name").size().rename("matches_played")

    cards_df = pd.DataFrame(card_rows)
    player_df = cards_df.groupby("player_name")["type"].value_counts().unstack(fill_value=0)
    for col in ("yellow", "red"):
        if col not in player_df.columns:
            player_df[col] = 0
    player_df = player_df.rename(columns={"yellow": "yellow_cards", "red": "red_cards"}).reset_index()
    player_df["position"] = player_df["player_name"].map(pos_map)
    player_df = player_df.merge(matches_played, on="player_name", how="left")
    player_df["carga"] = player_df["yellow_cards"] + player_df["red_cards"] * 3
    player_df = player_df.sort_values("carga", ascending=False).drop(columns="carga").reset_index(drop=True)
    player_df = player_df[["player_name", "position", "yellow_cards", "red_cards", "matches_played"]]

    return team_df, player_df


def rival_home_away_split(rival_slug, season=None):
    """
    Rendimiento del rival separado en LOCAL y VISITANTE, sobre todos sus
    partidos descargados. Clave para el scouting: si el partido es en nuestra
    cancha, lo que importa es su forma de VISITANTE.

    Devuelve un DataFrame de 2 filas (venue='Local'/'Visitante') con:
    pj, V, E, D, gf, gc, pts, pts_pj.
    """
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    match_dirs = rival_match_keys(rival_slug, season)
    if not match_dirs:
        return pd.DataFrame()

    acc = {"Local": [0, 0, 0, 0, 0], "Visitante": [0, 0, 0, 0, 0]}  # V,E,D,gf,gc
    for mk in match_dirs:
        venue = "Local" if mk.endswith("_h") else "Visitante"
        # En la carpeta del rival, compute_score_from_incidents devuelve
        # (goles del rival, goles del oponente) — el rival es el "equipo de
        # la carpeta".
        rival_g, opp_g = compute_score_from_incidents(mk, rival_dir)
        if rival_g is None:
            continue
        a = acc[venue]
        if rival_g > opp_g:
            a[0] += 1
        elif rival_g == opp_g:
            a[1] += 1
        else:
            a[2] += 1
        a[3] += rival_g
        a[4] += opp_g

    rows = []
    for venue, (v, e, d, gf, gc) in acc.items():
        pj = v + e + d
        pts = v * 3 + e
        rows.append({
            "venue": venue, "pj": pj, "V": v, "E": e, "D": d,
            "gf": gf, "gc": gc, "pts": pts,
            "pts_pj": round(pts / pj, 2) if pj else 0.0,
        })
    return pd.DataFrame(rows)


def rival_suspension_risk(rival_slug, season=None, yellows_for_ban=5):
    """
    Jugadores del rival a UNA amarilla de la suspensión, según el acumulado de
    tarjetas de todos sus partidos descargados. Como ahora se baja la temporada
    completa del rival (no una muestra), este acumulado sí es utilizable como
    alerta real (asumiendo que los partidos descargados son todos los de liga).

    Devuelve un DataFrame: player_name, position, yellow_cards, to_ban.
    """
    _, player_df = rival_discipline_profile(rival_slug, season)
    if player_df is None or player_df.empty:
        return pd.DataFrame()
    df = player_df.copy()
    # a cuántas amarillas de la próxima suspensión (ciclo de yellows_for_ban)
    df["to_ban"] = yellows_for_ban - (df["yellow_cards"] % yellows_for_ban)
    at_risk = df[(df["yellow_cards"] > 0) & (df["to_ban"] == 1)]
    at_risk = at_risk.sort_values("yellow_cards", ascending=False).reset_index(drop=True)
    return at_risk[["player_name", "position", "yellow_cards", "to_ban"]]


# ─── Head to head ────────────────────────────────────────────────────────────

def head_to_head(rival_slug, season=None):
    """
    Busca TODOS los enfrentamientos históricos de Chaco vs el rival, en TODAS
    las temporadas con datos scrapeados (no solo la actual) — varios rivales
    de 2026 ya se habían enfrentado en 2025.

    OJO: NO matchea por el slug del match_key (`rival_slug in mk`) porque el
    slug puede cambiar entre temporadas (ej. 'club_mitre' en 2025 vs 'mitre'
    en 2026, 'gimnasia_jujuy' vs 'gimnasia_de_jujuy'). Matchea por el
    `team_id` de SofaScore (event_clean.csv: home_team_id/away_team_id contra
    config.RIVALS[rival_slug]['id']), que es estable entre temporadas.

    El parámetro `season` se ignora (se mantiene por compatibilidad con
    llamadas existentes) — siempre busca en config.MATCHES_FILES completo.

    Retorna DataFrame con TODOS los cruces encontrados, ordenado por fecha:
    match_key, season, date, venue, chaco_goals, rival_goals, result.
    """
    rival_id = config.RIVALS.get(rival_slug, {}).get("id")
    if rival_id is None:
        return pd.DataFrame()

    h2h_rows = []
    for s in config.MATCHES_FILES:
        try:
            matches = load_matches(s)
        except FileNotFoundError:
            continue
        base_dir = config.season_data_dir(s)
        for mk in matches:
            ev_path = os.path.join(base_dir, mk, "event_clean.csv")
            if not os.path.exists(ev_path):
                continue
            ev = pd.read_csv(ev_path)
            if ev.empty:
                continue
            row = ev.iloc[0]
            home_id = row.get("home_team_id")
            away_id = row.get("away_team_id")
            try:
                is_rival_match = int(home_id) == rival_id or int(away_id) == rival_id
            except (TypeError, ValueError):
                is_rival_match = False
            if not is_rival_match:
                continue

            home_match = is_home_match(mk)
            chaco_g, rival_g = compute_score_from_incidents(mk, base_dir)
            h2h_rows.append({
                "match_key":   mk,
                "season":      s,
                "date":        get_match_date(mk),
                "venue":       "Local" if home_match else "Visitante",
                "chaco_goals": chaco_g,
                "rival_goals": rival_g,
                "result":      get_result(chaco_g, rival_g),
            })

    df = pd.DataFrame(h2h_rows)
    if not df.empty:
        df = df.sort_values("date").reset_index(drop=True)
    return df


def head_to_head_summary(h2h_df):
    """Resumen W/D/L + goles del historial H2H (h2h_df de head_to_head)."""
    if h2h_df is None or h2h_df.empty:
        return {}
    return {
        "partidos":     len(h2h_df),
        "victorias":    int((h2h_df["result"] == "W").sum()),
        "empates":      int((h2h_df["result"] == "D").sum()),
        "derrotas":     int((h2h_df["result"] == "L").sum()),
        "goles_favor":  int(h2h_df["chaco_goals"].sum()),
        "goles_contra": int(h2h_df["rival_goals"].sum()),
        "forma_str":    "".join(h2h_df["result"].tolist()),
    }


def head_to_head_goalscorers(h2h_df):
    """
    De los partidos del H2H (head_to_head), quién anotó de cada lado: jugadores
    del rival que le hicieron goles a Chaco, y jugadores de Chaco que le
    hicieron goles al rival — "quién nos rompió antes / a quién le hicimos daño".

    Devuelve (chaco_scorers_df, rival_scorers_df): player, goals, matches.
    """
    from collections import defaultdict
    if h2h_df is None or h2h_df.empty:
        empty = pd.DataFrame(columns=["player", "goals"])
        return empty, empty

    chaco_goals = defaultdict(int)
    rival_goals = defaultdict(int)

    for _, r in h2h_df.iterrows():
        mk, season = r["match_key"], r["season"]
        base_dir = config.season_data_dir(season)
        ip = os.path.join(base_dir, mk, "incidents_clean.csv")
        if not os.path.exists(ip):
            continue
        inc = pd.read_csv(ip)
        if "type" not in inc.columns:
            continue
        chaco_home = is_home_match(mk)
        for _, g in inc[inc["type"] == "goal"].iterrows():
            scorer = str(g.get("player", "")).strip()
            if not scorer or scorer.lower() == "nan":
                continue
            if bool(g.get("is_home", True)) == chaco_home:
                chaco_goals[scorer] += 1
            else:
                rival_goals[scorer] += 1

    def _to_df(d):
        if not d:
            return pd.DataFrame(columns=["player", "goals"])
        return pd.DataFrame([{"player": p, "goals": g} for p, g in d.items()]) \
            .sort_values("goals", ascending=False).reset_index(drop=True)

    return _to_df(chaco_goals), _to_df(rival_goals)


# ─── Alerta de amonestados (suspensión por acumulación) ──────────────────────

def discipline_alert(next_match_key, season=None, suspension_at=5):
    """
    Alerta operativa: jugadores de Chaco que llegan al próximo partido a 1
    amarilla de la suspensión por acumulación. Cuenta SOLO los partidos
    jugados ANTES de `next_match_key` (si contara la temporada completa,
    avisaría de riesgos que ya pasaron o que corresponden a partidos
    posteriores al que se está por jugar).

    Misma regla cíclica que plot_discipline de temporada (amarillas %
    suspension_at == suspension_at-1): a las suspension_at-1, suspension_at*2-1,
    etc. Reusa season_player_stats restringido a esos partidos previos.

    Devuelve un DataFrame: player, amarillas, rojas, partidos — solo los
    jugadores en riesgo (vacío si nadie está en el corte).
    """
    season = season or config.season_from_match_key(next_match_key)
    base_dir = config.season_data_dir(season)
    matches = load_matches(season)
    next_date = pd.to_datetime(get_match_date(next_match_key))

    prior_mks = [
        mk for mk in matches
        if os.path.exists(os.path.join(base_dir, mk, "lineups_clean.csv"))
        and pd.to_datetime(get_match_date(mk)) < next_date
    ]
    if not prior_mks:
        return pd.DataFrame(columns=["player", "amarillas", "rojas", "partidos"])

    df = season_player_stats(prior_mks, base_dir)
    if df.empty:
        return pd.DataFrame(columns=["player", "amarillas", "rojas", "partidos"])

    df = df.rename(columns={"player": "player"})[["player", "amarillas", "rojas", "partidos"]].copy()
    near = suspension_at - 1
    en_riesgo = (df["amarillas"] >= near) & (df["amarillas"] % suspension_at == near)
    return df[en_riesgo].sort_values("amarillas", ascending=False).reset_index(drop=True)


# ─── Cadena de Markov del rival (estado del marcador) ─────────────────────────

def rival_markov(rival_slug, season=None):
    """
    Cadena de Markov del estado del marcador del RIVAL, reutilizando
    season.markov_game_state sobre sus partidos ya scrapeados. Los match_keys
    del rival vienen nombrados desde SU perspectiva (sufijo _h/_a = el rival de
    local/visitante), que es justo lo que espera markov_game_state vía
    is_home_match, así que la matriz sale directo en la óptica del rival: S+ =
    el rival ganando por 1, S- = el rival perdiendo por 1, etc.

    Devuelve (matrix_df 5x5, transitions_df) — mismo formato que la de Chaco.
    Si el rival no tiene partidos scrapeados, devuelve DataFrames vacíos.
    """
    season = season or config.CURRENT_SEASON
    rival_dir = os.path.join(config.rivals_dir(season), rival_slug)
    keys = rival_match_keys(rival_slug, season)
    if not keys:
        return (pd.DataFrame(),
                pd.DataFrame(columns=["match_key", "minute", "from_state", "to_state"]))
    return markov_game_state(keys, rival_dir)


def rival_markov_summary(matrix_df, transitions_df=None):
    """
    Traduce la matriz de transición del rival a lecturas de scouting: qué le
    pasa más seguido cuando empata (S0), cuando se pone en ventaja de un gol
    (S+) y cuando va perdiendo por uno (S-). Cada lectura trae las
    probabilidades, una frase lista para el informe y, si se pasa
    transitions_df, la cantidad de veces que se dio ese estado (n = tamaño de
    muestra, para marcar cuándo un dato es de muestra chica).

    Devuelve un dict; vacío si no hay datos.
    """
    if matrix_df is None or matrix_df.empty:
        return {}

    n_por_estado = {}
    if transitions_df is not None and not transitions_df.empty:
        n_por_estado = transitions_df["from_state"].value_counts().to_dict()

    def _row(s):
        if s not in matrix_df.index:
            return {}
        return {k: float(v) for k, v in matrix_df.loc[s].items() if v > 0}

    out = {}

    # Desde el empate (S0): ¿golpea primero o suele quedar en desventaja?
    s0 = _row("S0")
    if s0:
        p_ade, p_atr = s0.get("S+", 0.0), s0.get("S-", 0.0)
        d = {"al_frente": round(p_ade, 2), "en_desventaja": round(p_atr, 2),
             "n": int(n_por_estado.get("S0", 0))}
        if p_atr > p_ade:
            d["lectura"] = (f"Desde el 0-0, el próximo gol suele ser en contra suya "
                            f"({round(100*p_atr)}%): le cuesta romper el empate a su favor.")
        else:
            d["lectura"] = (f"Desde el 0-0 suele golpear primero: se pone en ventaja el "
                            f"{round(100*p_ade)}% de las veces.")
        out["desde_empate"] = d

    # Desde ganando por 1 (S+): estira, o lo empatan
    sp = _row("S+")
    if sp:
        p_estira, p_empatan = sp.get("S++", 0.0), sp.get("S0", 0.0)
        d = {"estira_a_2": round(p_estira, 2), "lo_empatan": round(p_empatan, 2),
             "n": int(n_por_estado.get("S+", 0))}
        if p_empatan >= p_estira:
            d["lectura"] = (f"Cuando se pone 1-0 le cuesta cerrarlo: lo alcanzan el "
                            f"{round(100*p_empatan)}% de las veces.")
        else:
            d["lectura"] = (f"Cuando se pone 1-0 tiende a estirar la diferencia "
                            f"({round(100*p_estira)}%): si toma aire, golpea de nuevo.")
        out["ganando_por_1"] = d

    # Desde perdiendo por 1 (S-): reacciona, o se hunde
    sm = _row("S-")
    if sm:
        p_empata, p_hunde = sm.get("S0", 0.0), sm.get("S--", 0.0)
        d = {"empata": round(p_empata, 2), "se_hunde": round(p_hunde, 2),
             "n": int(n_por_estado.get("S-", 0))}
        if p_hunde > p_empata:
            d["lectura"] = (f"Si se pone 0-1 se cae: el {round(100*p_hunde)}% de las veces "
                            f"recibe el segundo antes de reaccionar.")
        else:
            d["lectura"] = (f"Si se pone 0-1 reacciona: empata el {round(100*p_empata)}% de "
                            f"las veces antes de recibir otro.")
        out["perdiendo_por_1"] = d

    return out


# ─── Perfil de equipo a favor / en contra (para comparar Chaco vs rival) ──────

# metric en statistics_clean.csv -> clave del perfil. Cada una tiene columna
# del equipo y del rival (home_val/away_val según la localía del equipo).
_TWOWAY_STATS = {
    "Ball possession":  "possession",
    "Total shots":      "shots",
    "Shots on target":  "sot",
    "Shots off target": "shots_off",
    "Blocked shots":    "shots_blocked",
    "Corner kicks":     "corners",
    "Fouls":            "fouls",
    "Accurate passes":  "passes_acc",
    "Tackles":          "tackles",
    "Interceptions":    "interceptions",
    "Clearances":       "clearances",
}


def team_two_way_profile(match_keys, base_dir):
    """
    Perfil promedio POR PARTIDO de un equipo, en ataque (_for) y en defensa
    (_against), sobre los partidos indicados. Sirve tanto para Chaco (pasando
    sus match_keys + season_data_dir) como para un rival (sus match_keys +
    rivals_dir/slug), porque en ambos casos el sufijo _h/_a del match_key marca
    la localía del equipo analizado.

    Fuentes: statistics_clean (posesión, remates, córners, faltas, pases,
    quites, intercepciones, despejes), shotmap_clean (xG y remates for/against)
    e incidents_clean (goles for/against).

    Devuelve un dict de promedios por partido: goals_for/against,
    xg_for/against, shots_for/against, sot_for/against, shots_off_*,
    shots_blocked_*, corners_*, fouls_*, y las de sólo el equipo (possession,
    passes_acc, tackles, interceptions, clearances). Incluye n_matches.
    """
    from collections import defaultdict
    acc = defaultdict(list)
    n = 0

    for mk in match_keys:
        mdir = os.path.join(base_dir, mk)
        if not os.path.isdir(mdir):
            continue
        team_home = is_home_match(mk)
        used = False

        # --- estadísticas del partido ---
        sp = os.path.join(mdir, "statistics_clean.csv")
        if os.path.exists(sp):
            st = pd.read_csv(sp)
            for _, r in st.iterrows():
                key = _TWOWAY_STATS.get(r.get("metric"))
                if not key:
                    continue
                tv = pd.to_numeric(r.get("home_val" if team_home else "away_val"), errors="coerce")
                ov = pd.to_numeric(r.get("away_val" if team_home else "home_val"), errors="coerce")
                if pd.notna(tv):
                    acc[f"{key}_for"].append(float(tv))
                if pd.notna(ov):
                    acc[f"{key}_against"].append(float(ov))
            used = True

        # --- xG y cantidad de remates (shotmap) ---
        shp = os.path.join(mdir, "shotmap_clean.csv")
        if os.path.exists(shp):
            sh = pd.read_csv(shp)
            if "isHome" in sh.columns:
                fm = sh[sh["isHome"] == team_home]
                ag = sh[sh["isHome"] != team_home]
                acc["xg_for"].append(round(fm["xg"].sum(), 3))
                acc["xg_against"].append(round(ag["xg"].sum(), 3))
                used = True

        # --- goles (incidents) ---
        ip = os.path.join(mdir, "incidents_clean.csv")
        if os.path.exists(ip):
            inc = pd.read_csv(ip)
            if "type" in inc.columns:
                g = inc[inc["type"] == "goal"]
                acc["goals_for"].append(int((g["is_home"] == team_home).sum()))
                acc["goals_against"].append(int((g["is_home"] != team_home).sum()))
                used = True

        if used:
            n += 1

    prof = {k: round(sum(v) / len(v), 2) for k, v in acc.items() if v}
    prof["n_matches"] = n
    return prof


def chaco_two_way_profile(season=None):
    """Perfil for/against de Chaco sobre sus partidos ya jugados."""
    season = season or config.CURRENT_SEASON
    base = config.season_data_dir(season)
    mks = [mk for mk in load_matches(season)
           if os.path.exists(os.path.join(base, mk, "statistics_clean.csv"))]
    return team_two_way_profile(mks, base)


def rival_two_way_profile(rival_slug, season=None):
    """Perfil for/against del rival sobre sus partidos scrapeados."""
    season = season or config.CURRENT_SEASON
    base = os.path.join(config.rivals_dir(season), rival_slug)
    return team_two_way_profile(rival_match_keys(rival_slug, season), base)


def cross_team_player_pool(rival_slug, season=None, min_minutes=90):
    """
    Pool de jugadores por-90 que mezcla los partidos de Chaco con los del rival,
    para poder comparar un jugador de Chaco con uno del rival en el mismo radar
    (reusa players.player_pool con `sources`). El único cruce directo Chaco-rival
    queda contado en ambas carpetas; al ser métricas por-90 el efecto es marginal.
    """
    from src.analysis.players import player_pool
    season = season or config.CURRENT_SEASON
    chaco_base = config.season_data_dir(season)
    chaco_mks = list(load_matches(season).keys())
    rival_base = os.path.join(config.rivals_dir(season), rival_slug)
    rival_mks = rival_match_keys(rival_slug, season)
    sources = [(chaco_base, chaco_mks), (rival_base, rival_mks)]
    return player_pool(sources=sources, min_minutes=min_minutes)
