"""
season.py
=========
Análisis de temporada completa: resumen por partido, tabla de posiciones propia,
estadísticas globales y análisis de jugadores.
"""

import os
import re
import math
import importlib.util

import pandas as pd
import numpy as np

import config

CHACO_NAME = "Chaco For Ever"

KEY_METRICS = [
    "Ball possession", "Expected goals", "Total shots",
    "Shots on target", "Goalkeeper saves", "Corner kicks",
    "Fouls", "Passes", "Accurate passes", "Tackles",
    "Yellow cards", "Red cards",
]


# ─── Utilidades ──────────────────────────────────────────────────────────────

def is_home_match(match_key):
    return match_key.endswith("_h")


def get_opponent(match_key):
    parts = match_key.split("_vs_")
    if len(parts) < 2:
        return "Desconocido"
    rival = parts[1].rsplit("_", 1)[0]
    return rival.replace("_", " ").title()


def get_match_date(match_key):
    m = re.match(r"(\d{4}-\d{2}-\d{2})", match_key)
    return m.group(1) if m else match_key


def load_matches(season=None):
    """Carga el dict MATCHES de la temporada indicada desde config."""
    s = season or config.CURRENT_SEASON
    path = config.MATCHES_FILES.get(s)
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Archivo de matches no encontrado para temporada {s}: {path}")
    spec = importlib.util.spec_from_file_location("matches_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MATCHES


# ─── Marcadores ──────────────────────────────────────────────────────────────

def compute_score_from_incidents(match_key, base_dir=None):
    base_dir = base_dir or config.season_data_dir()
    path = os.path.join(base_dir, match_key, "incidents_clean.csv")
    if not os.path.exists(path):
        return _compute_score_from_shotmap(match_key, base_dir)

    df = pd.read_csv(path)
    goals = df[df["type"] == "goal"]
    home_match = is_home_match(match_key)
    chaco_goals = len(goals[goals["is_home"] == home_match])
    rival_goals  = len(goals[goals["is_home"] != home_match])
    return chaco_goals, rival_goals


def _compute_score_from_shotmap(match_key, base_dir):
    path = os.path.join(base_dir, match_key, "shotmap_clean.csv")
    if not os.path.exists(path):
        return None, None
    df = pd.read_csv(path)
    goals = df[df["shotType"] == "goal"]
    home_match = is_home_match(match_key)
    chaco_goals = len(goals[goals["isHome"] == home_match])
    rival_goals  = len(goals[goals["isHome"] != home_match])
    return chaco_goals, rival_goals


def get_result(chaco_goals, rival_goals):
    if chaco_goals is None:
        return "?"
    if chaco_goals > rival_goals:
        return "W"
    if chaco_goals < rival_goals:
        return "L"
    return "D"


# ─── Resumen de partido ───────────────────────────────────────────────────────

def match_summary(match_key, base_dir=None):
    """Devuelve un dict con el resumen completo de un partido."""
    base_dir = base_dir or config.season_data_dir()
    home_match = is_home_match(match_key)
    chaco_g, rival_g = compute_score_from_incidents(match_key, base_dir)

    summary = {
        "match_key": match_key,
        "date":      get_match_date(match_key),
        "opponent":  get_opponent(match_key),
        "venue":     "Local" if home_match else "Visitante",
        "chaco_goals": chaco_g,
        "rival_goals": rival_g,
        "result":    get_result(chaco_g, rival_g),
    }

    stats_path = os.path.join(base_dir, match_key, "statistics_clean.csv")
    if os.path.exists(stats_path):
        df_st = pd.read_csv(stats_path)
        for metric in KEY_METRICS:
            row = df_st[df_st["metric"] == metric]
            if not row.empty:
                val = row.iloc[0]["home_val"] if home_match else row.iloc[0]["away_val"]
                summary[metric.lower().replace(" ", "_")] = val

    shot_path = os.path.join(base_dir, match_key, "shotmap_clean.csv")
    if os.path.exists(shot_path):
        df_sh = pd.read_csv(shot_path)
        chaco_filter = df_sh["isHome"] == home_match
        rival_filter  = df_sh["isHome"] != home_match
        summary["chaco_xg"]          = round(df_sh[chaco_filter]["xg"].sum(), 3)
        summary["rival_xg"]           = round(df_sh[rival_filter]["xg"].sum(), 3)
        summary["chaco_total_shots"]  = int(chaco_filter.sum())
        summary["rival_total_shots"]  = int(rival_filter.sum())

    return summary


# ─── Temporada completa ───────────────────────────────────────────────────────

# Columnas mínimas que produce match_summary (para devolver una tabla vacía
# con el esquema correcto en vez de explotar).
_SEASON_TABLE_COLUMNS = [
    "match_key", "date", "opponent", "venue",
    "chaco_goals", "rival_goals", "result", "points", "points_cumsum",
]


def build_season_table(match_keys, base_dir=None):
    base_dir = base_dir or config.season_data_dir()
    rows = [match_summary(mk, base_dir) for mk in match_keys]
    df = pd.DataFrame(rows)

    # Temporada vacía (sin fixtures cargados) o sin partidos con datos:
    # devolvemos un DataFrame con el esquema esperado en vez de un KeyError.
    if df.empty or "result" not in df.columns:
        return pd.DataFrame(columns=_SEASON_TABLE_COLUMNS)

    df["points"]         = df["result"].map({"W": 3, "D": 1, "L": 0})
    df["points_cumsum"]  = df["points"].cumsum()
    return df


def season_stats(season_df):
    # Temporada sin partidos con datos: resumen en cero, sin reventar.
    if season_df is None or season_df.empty or "result" not in season_df.columns:
        return {
            "partidos": 0, "victorias": 0, "empates": 0, "derrotas": 0,
            "puntos": 0, "goles_favor": 0, "goles_contra": 0,
            "diferencia_goles": 0, "xg_favor": None, "xg_contra": None,
            "rendimiento_local": "0V-0E-0D", "rendimiento_visitante": "0V-0E-0D",
            "sin_datos": True,
        }
    total  = len(season_df)
    wins   = (season_df["result"] == "W").sum()
    draws  = (season_df["result"] == "D").sum()
    losses = (season_df["result"] == "L").sum()
    gf = season_df["chaco_goals"].sum()
    ga = season_df["rival_goals"].sum()
    pts = season_df["points"].sum()
    return {
        "partidos":              int(total),
        "victorias":             int(wins),
        "empates":               int(draws),
        "derrotas":              int(losses),
        "puntos":                int(pts),
        "goles_favor":           int(gf) if pd.notna(gf) else 0,
        "goles_contra":          int(ga) if pd.notna(ga) else 0,
        "diferencia_goles":      int(gf - ga) if pd.notna(gf) and pd.notna(ga) else 0,
        "xg_favor":              round(season_df["chaco_xg"].sum(), 2) if "chaco_xg" in season_df else None,
        "xg_contra":             round(season_df["rival_xg"].sum(), 2) if "rival_xg" in season_df else None,
        "rendimiento_local":     _venue_record(season_df, "Local"),
        "rendimiento_visitante": _venue_record(season_df, "Visitante"),
    }


def _venue_record(df, venue):
    sub = df[df["venue"] == venue]
    if sub.empty:
        return "0V-0E-0D"
    w = (sub["result"] == "W").sum()
    d = (sub["result"] == "D").sum()
    l = (sub["result"] == "L").sum()
    return f"{w}V-{d}E-{l}D"


# ─── Puntos esperados (xPoints) ───────────────────────────────────────────────
# Convierte el xG REAL de un partido puntual (no un rating de temporada — para
# eso está src/analysis/simulation.py) en puntos esperados, vía Poisson
# independiente sobre esos dos valores de xG. "Cuántos puntos mereció Chaco
# en ESTE partido según lo que generó y concedió."

def _poisson_pmf(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * lam ** k / math.factorial(k)


def expected_points(xg_for, xg_against, max_goals=10):
    """Puntos esperados de un partido a partir del xG generado y concedido en
    ESE partido. Modela los goles de cada lado como Poisson independiente con
    media = xG real del partido, y suma la probabilidad de cada marcador
    posible (0..max_goals por lado) para sacar P(gana)/P(empata)/P(pierde).

    Devuelve dict: p_win, p_draw, p_loss, xpoints (= 3*p_win + p_draw)."""
    xg_for = max(float(xg_for or 0), 0.0)
    xg_against = max(float(xg_against or 0), 0.0)

    p_win = p_draw = p_loss = 0.0
    for gf in range(max_goals + 1):
        pf = _poisson_pmf(gf, xg_for)
        for ga in range(max_goals + 1):
            p = pf * _poisson_pmf(ga, xg_against)
            if gf > ga:
                p_win += p
            elif gf == ga:
                p_draw += p
            else:
                p_loss += p

    # Normaliza por la cola truncada en max_goals (residuo chico con xG de
    # fútbol real, pero así las tres probabilidades siempre suman 1).
    total = p_win + p_draw + p_loss
    if total > 0:
        p_win, p_draw, p_loss = p_win / total, p_draw / total, p_loss / total

    return {
        "p_win":  round(p_win, 4),
        "p_draw": round(p_draw, 4),
        "p_loss": round(p_loss, 4),
        "xpoints": round(3 * p_win + p_draw, 3),
    }


def season_xpoints_table(season_df):
    """A partir de build_season_table(), agrega xpoints por partido (vía
    expected_points sobre chaco_xg/rival_xg) y el acumulado real vs. esperado
    a lo largo de la temporada. Partidos sin xG (falta el shotmap) quedan con
    xpoints NaN — no distorsionan el resto del acumulado porque
    Series.cumsum() por default saltea los NaN (no resetea el acumulado)."""
    df = season_df.copy()
    if "chaco_xg" not in df.columns or "rival_xg" not in df.columns:
        df["xpoints"] = np.nan
        df["xpoints_cumsum"] = np.nan
        return df

    def _xp(row):
        if pd.isna(row["chaco_xg"]) or pd.isna(row["rival_xg"]):
            return np.nan
        return expected_points(row["chaco_xg"], row["rival_xg"])["xpoints"]

    df["xpoints"] = df.apply(_xp, axis=1)
    df["xpoints_cumsum"] = df["xpoints"].cumsum()
    return df


# ─── Análisis de jugadores ────────────────────────────────────────────────────

def player_stats_per_match(match_key, base_dir=None):
    """Stats de jugadores de Chaco en ese partido (lineups + shotmap)."""
    base_dir = base_dir or config.season_data_dir()
    home_match = is_home_match(match_key)
    chaco_side = "home" if home_match else "away"
    rows = []

    lineups_path = os.path.join(base_dir, match_key, "lineups_clean.csv")
    if not os.path.exists(lineups_path):
        return pd.DataFrame()

    df_lin = pd.read_csv(lineups_path)
    chaco_players = df_lin[df_lin["team_side"] == chaco_side].copy()

    df_shots = pd.DataFrame()
    shot_path = os.path.join(base_dir, match_key, "shotmap_clean.csv")
    if os.path.exists(shot_path):
        all_shots = pd.read_csv(shot_path)
        df_shots = all_shots[all_shots["isHome"] == home_match]

    for _, player in chaco_players.iterrows():
        name = player.get("player_name", "")
        p_shots = df_shots[df_shots["player_name"] == name] if not df_shots.empty else pd.DataFrame()
        rows.append({
            "match_key":       match_key,
            "player":          name,
            "position":        player.get("position"),
            "is_starter":      player.get("is_starter"),
            "minutes":         player.get("minutes_played"),
            "rating":          player.get("rating"),
            "goals_lineup":    player.get("goals"),
            "assists":         player.get("assists"),
            "yellow_cards":    player.get("yellow_cards"),
            "red_cards":       player.get("red_cards"),
            "substitute_in":   player.get("substitute_in"),
            "substitute_out":  player.get("substitute_out"),
            "total_shots":     len(p_shots),
            "shots_on_target": len(p_shots[p_shots["shotType"].isin(["goal", "save"])]) if not p_shots.empty else 0,
            "goals_shotmap":   len(p_shots[p_shots["shotType"] == "goal"]) if not p_shots.empty else 0,
            "xg":              round(p_shots["xg"].sum(), 3) if not p_shots.empty else 0,
        })

    return pd.DataFrame(rows)


def season_player_stats(match_keys, base_dir=None):
    """Agrega stats de jugador en toda la temporada."""
    base_dir = base_dir or config.season_data_dir()
    all_dfs = [player_stats_per_match(mk, base_dir) for mk in match_keys]
    all_dfs = [d for d in all_dfs if not d.empty]
    if not all_dfs:
        return pd.DataFrame()

    df_all = pd.concat(all_dfs, ignore_index=True)
    agg = df_all.groupby("player").agg(
        partidos         =("match_key",     "count"),
        titularidades    =("is_starter",    lambda x: x.astype(bool).sum()),
        minutos          =("minutes",       "sum"),
        rating_promedio  =("rating",        "mean"),
        goles            =("goals_shotmap", "sum"),
        asistencias      =("assists",       "sum"),
        amarillas        =("yellow_cards",  "sum"),
        rojas            =("red_cards",     "sum"),
        tiros_totales    =("total_shots",   "sum"),
        tiros_al_arco    =("shots_on_target","sum"),
        xg_total         =("xg",            "sum"),
    ).reset_index()
    agg["rating_promedio"] = agg["rating_promedio"].round(2)
    agg["xg_total"] = agg["xg_total"].round(3)
    return agg.sort_values("minutos", ascending=False)


def top_scorers(season_player_df, top_n=5):
    return season_player_df.nlargest(top_n, "goles")[["player", "goles", "xg_total", "partidos"]]


def most_used_players(season_player_df, top_n=15):
    return season_player_df.nlargest(top_n, "minutos")[
        ["player", "partidos", "titularidades", "minutos", "rating_promedio"]
    ]


# ─── Disponibilidad: refuerzos vs. jugadores de todo el año ──────────────────

def player_availability(match_keys, base_dir=None):
    """
    Por cada jugador de Chaco: en qué partido apareció por primera vez y cuántos
    minutos tuvo DISPONIBLES desde ese debut (90' por cada partido desde el
    debut en adelante, incluido).

    Existe para no castigar a los refuerzos. Un jugador que llegó en la fecha 19
    nunca va a llegar a los 450'/600' que acumula un titular de todo el año,
    pero puede haber jugado el 100% de lo que se jugó desde que llegó — y
    entonces merece estar en los gráficos igual que un titular histórico.

    Devuelve DataFrame ordenado por pct_disponible:
      player, debut, fecha_debut, partidos_desde_debut, partidos_jugados,
      minutos, minutos_disponibles, pct_disponible, es_incorporacion
    """
    base_dir = base_dir or config.season_data_dir()
    dated = sorted(match_keys, key=get_match_date)
    total = len(dated)

    primera = {}     # player -> índice del partido de debut
    minutos = {}     # player -> minutos acumulados
    jugados = {}     # player -> partidos con minutos > 0
    for idx, mk in enumerate(dated):
        path = os.path.join(base_dir, mk, "lineups_clean.csv")
        if not os.path.exists(path):
            continue
        lin = pd.read_csv(path)
        side = "home" if is_home_match(mk) else "away"
        for _, r in lin[lin["team_side"] == side].iterrows():
            name = r.get("player_name")
            if not isinstance(name, str) or not name:
                continue
            primera.setdefault(name, idx)
            mins = pd.to_numeric(r.get("minutes_played"), errors="coerce")
            mins = 0.0 if pd.isna(mins) else float(mins)
            minutos[name] = minutos.get(name, 0.0) + mins
            if mins > 0:
                jugados[name] = jugados.get(name, 0) + 1

    if not primera:
        return pd.DataFrame()

    rows = []
    for name, idx in primera.items():
        desde_debut = total - idx
        disponibles = desde_debut * 90.0
        mins = minutos.get(name, 0.0)
        rows.append({
            "player":                name,
            "debut":                 dated[idx],
            "fecha_debut":           get_match_date(dated[idx]),
            "partidos_desde_debut":  desde_debut,
            "partidos_jugados":      jugados.get(name, 0),
            "minutos":               mins,
            "minutos_disponibles":   disponibles,
            "pct_disponible":        round(mins / disponibles * 100, 1) if disponibles else 0.0,
            # "incorporación" = no estaba desde el arranque de la temporada
            "es_incorporacion":      idx > 0,
        })
    return (pd.DataFrame(rows)
            .sort_values(["pct_disponible", "minutos"], ascending=False)
            .reset_index(drop=True))


def relevant_players(availability, min_minutes=450, min_pct=45.0,
                     min_minutes_reciente=180):
    """
    Set de nombres con muestra suficiente para los gráficos individuales
    (pizzas, rating, calendario de carga, redes).

    Un jugador entra si cumple CUALQUIERA de las dos condiciones:
      a) acumuló `min_minutes` en la temporada  — el criterio de siempre; o
      b) jugó al menos `min_pct`% de los minutos disponibles desde su debut,
         con un piso de `min_minutes_reciente` para no colar a alguien que
         entró dos veces.

    La (b) es la que rescata a los refuerzos del mercado de mitad de año.
    """
    if availability is None or availability.empty:
        return set()
    por_total = availability["minutos"] >= min_minutes
    por_ritmo = ((availability["pct_disponible"] >= min_pct) &
                 (availability["minutos"] >= min_minutes_reciente))
    return set(availability.loc[por_total | por_ritmo, "player"])


# ─── Análisis de cambios ──────────────────────────────────────────────────────

def substitution_analysis(match_keys, base_dir=None):
    base_dir = base_dir or config.season_data_dir()
    rows = []
    for mk in match_keys:
        path = os.path.join(base_dir, mk, "incidents_clean.csv")
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        home_match = is_home_match(mk)
        subs = df[(df["type"] == "substitution") & (df["is_home"] == home_match)]
        for _, s in subs.iterrows():
            rows.append({
                "match_key":  mk,
                "minute":     s.get("minute"),
                "player_in":  s.get("player"),
                "player_out": str(s.get("description", "")).replace("OUT: ", ""),
            })
    if not rows:
        return pd.DataFrame()
    df_subs = pd.DataFrame(rows)
    df_subs["minute"] = pd.to_numeric(df_subs["minute"], errors="coerce")
    return df_subs


# ─── Red de minutos compartidos ──────────────────────────────────────────────

def shared_minutes_network(match_keys, base_dir, min_minutes=180, players=None):
    """
    Grafo de relaciones del plantel de Chaco: minutos que cada dupla compartió
    en cancha y qué tan bien le fue al equipo en esos minutos.

    Intervalo en cancha de un jugador = [inicio, inicio+minutes_played], con
    inicio=substitute_in (NaN → 0, es titular). La diferencia de gol de una
    dupla = goles de Chaco menos del rival ocurridos mientras ambos estaban.

    `players` (opcional): iterable de nombres que reemplaza al filtro por
    min_minutes. Conviene pasarle el plantel con muestra (relevant_players):
    bajar min_minutes para que entren los refuerzos también mete jugadores de
    paso que quedan como nodos sueltos sin ninguna cuerda.

    Devuelve (nodes_df, edges_df):
      nodes_df: player_name, minutes (total temporada), matches
      edges_df: p1, p2, minutes_together, goal_diff, gd_per90
    """
    from collections import defaultdict
    node_min = defaultdict(float)
    node_matches = defaultdict(int)
    pair_min = defaultdict(float)
    pair_gd = defaultdict(float)

    for mk in match_keys:
        mdir = os.path.join(base_dir, mk)
        lp = os.path.join(mdir, "lineups_clean.csv")
        if not os.path.exists(lp):
            continue
        lin = pd.read_csv(lp)
        chaco_side = "home" if is_home_match(mk) else "away"
        team = lin[lin["team_side"] == chaco_side]

        intervals = {}
        for _, r in team.iterrows():
            mins = pd.to_numeric(r.get("minutes_played"), errors="coerce")
            if pd.isna(mins) or mins <= 0:
                continue
            sin = pd.to_numeric(r.get("substitute_in"), errors="coerce")
            start = float(sin) if pd.notna(sin) else 0.0
            name = r["player_name"]
            intervals[name] = (start, start + float(mins))
            node_min[name] += float(mins)
            node_matches[name] += 1

        # Goles por minuto: de Chaco vs del rival (para la diferencia de la dupla)
        chaco_goals, rival_goals = [], []
        ip = os.path.join(mdir, "incidents_clean.csv")
        if os.path.exists(ip):
            inc = pd.read_csv(ip)
            if "type" in inc.columns:
                chaco_is_home = (chaco_side == "home")
                for _, gr in inc[inc["type"] == "goal"].iterrows():
                    m = pd.to_numeric(gr.get("minute"), errors="coerce")
                    if pd.isna(m):
                        continue
                    tgt = chaco_goals if bool(gr.get("is_home", True)) == chaco_is_home \
                        else rival_goals
                    tgt.append(float(m))

        names = list(intervals)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                s = max(intervals[a][0], intervals[b][0])
                e = min(intervals[a][1], intervals[b][1])
                if e - s <= 0:
                    continue
                key = tuple(sorted((a, b)))
                pair_min[key] += e - s
                pair_gd[key] += (sum(1 for g in chaco_goals if s < g <= e)
                                 - sum(1 for g in rival_goals if s < g <= e))

    nodes = pd.DataFrame(
        [{"player_name": n, "minutes": node_min[n], "matches": node_matches[n]}
         for n in node_min])
    if nodes.empty:
        return nodes, pd.DataFrame(
            columns=["p1", "p2", "minutes_together", "goal_diff", "gd_per90"])
    if players is not None:
        nodes = nodes[nodes["player_name"].isin(set(players))]
    else:
        nodes = nodes[nodes["minutes"] >= min_minutes]
    nodes = nodes.sort_values("minutes", ascending=False).reset_index(drop=True)
    keep = set(nodes["player_name"])

    edges = [{"p1": a, "p2": b, "minutes_together": m, "goal_diff": pair_gd[(a, b)],
              "gd_per90": pair_gd[(a, b)] / (m / 90.0) if m else 0.0}
             for (a, b), m in pair_min.items() if a in keep and b in keep]
    edges_df = (pd.DataFrame(edges).sort_values("minutes_together", ascending=False)
                .reset_index(drop=True) if edges else pd.DataFrame(
                    columns=["p1", "p2", "minutes_together", "goal_diff", "gd_per90"]))
    return nodes, edges_df


# ─── Duplas asociativas de temporada (posición + volumen de pases) ───────────

def pass_association_network(match_keys, base_dir, min_matches=5):
    """
    Duplas asociativas de la temporada: a diferencia de shared_minutes_network
    (minutos juntos en cancha), esto mide QUÉ TAN CERCA jugaron y CUÁNTO
    pasaron, partido a partido, usando average_positions_clean.csv +
    lineups_clean.csv (posición promedio real y pases acertados reales de
    SofaScore — mismo dato que plot_pass_association a nivel partido, acá
    agregado a nivel temporada).

    Por partido, para cada par de titulares de Chaco se calcula un puntaje =
    volumen de pases combinado (sqrt(pases_a * pases_b)) ponderado por
    cercanía (inverso de la distancia en cancha, 0-100 OPTA) — dos jugadores
    que pasan mucho Y juegan cerca puntúan más que dos que pasan mucho pero
    lejos (ej. arquero y 9). Se promedia sobre los partidos que jugaron
    juntos como titulares.

    Devuelve (nodes_df, edges_df):
      nodes_df: player_name, passes (total temporada), matches (titular)
      edges_df: p1, p2, matches_together, avg_score (asociación promedio
                por partido), avg_combined_passes
    """
    from collections import defaultdict
    node_passes = defaultdict(float)
    node_matches = defaultdict(int)
    pair_score = defaultdict(float)
    pair_passes = defaultdict(float)
    pair_matches = defaultdict(int)

    for mk in match_keys:
        mdir = os.path.join(base_dir, mk)
        ap_path = os.path.join(mdir, "average_positions_clean.csv")
        lp_path = os.path.join(mdir, "lineups_clean.csv")
        if not (os.path.exists(ap_path) and os.path.exists(lp_path)):
            continue
        ap = pd.read_csv(ap_path)
        lin = pd.read_csv(lp_path)
        chaco_side = "home" if is_home_match(mk) else "away"

        df = ap[ap["team_side"] == chaco_side].merge(
            lin[["player_name", "is_starter", "accurate_passes"]],
            on="player_name", how="left")
        df = df[df["is_starter"] == True].reset_index(drop=True)
        if df.empty:
            continue
        df["accurate_passes"] = pd.to_numeric(df["accurate_passes"], errors="coerce").fillna(0)

        for _, r in df.iterrows():
            node_passes[r["player_name"]] += float(r["accurate_passes"])
            node_matches[r["player_name"]] += 1

        pos = df[["average_x", "average_y"]].values
        names = df["player_name"].tolist()
        passes = df["accurate_passes"].values
        n = len(df)
        for i in range(n):
            for j in range(i + 1, n):
                dist = float(np.linalg.norm(pos[i] - pos[j]))
                closeness = 1.0 / (1.0 + dist / 20.0)   # 20 OPTA ~ "cerca"
                combined = float(np.sqrt(max(passes[i], 0) * max(passes[j], 0)))
                key = tuple(sorted((names[i], names[j])))
                pair_score[key] += combined * closeness
                pair_passes[key] += combined
                pair_matches[key] += 1

    nodes = pd.DataFrame(
        [{"player_name": n, "passes": node_passes[n], "matches": node_matches[n]}
         for n in node_passes])
    if nodes.empty:
        return nodes, pd.DataFrame(
            columns=["p1", "p2", "matches_together", "avg_score", "avg_combined_passes"])
    nodes = nodes.sort_values("passes", ascending=False).reset_index(drop=True)

    edges = [{"p1": a, "p2": b, "matches_together": pair_matches[(a, b)],
              "avg_score": pair_score[(a, b)] / pair_matches[(a, b)],
              "avg_combined_passes": pair_passes[(a, b)] / pair_matches[(a, b)]}
             for (a, b) in pair_matches if pair_matches[(a, b)] >= min_matches]
    edges_df = (pd.DataFrame(edges).sort_values("avg_score", ascending=False)
                .reset_index(drop=True) if edges else pd.DataFrame(
                    columns=["p1", "p2", "matches_together", "avg_score", "avg_combined_passes"]))
    return nodes, edges_df


# ─── Red de asistencias de temporada ─────────────────────────────────────────

def assists_network(match_keys, base_dir):
    """
    Red de asistencias de Chaco en la temporada: quién habilita a quién en los
    goles. Sale de incidents_clean (columnas 'player' = goleador, 'assist' =
    asistente), filtrando solo los goles de Chaco.

    Devuelve (nodes_df, edges_df):
      nodes_df: player, goals, assists  (participación en goles)
      edges_df: assister, scorer, count  (cantidad de goles conectados)
    """
    from collections import defaultdict
    goals = defaultdict(int)
    assists = defaultdict(int)
    pair = defaultdict(int)

    for mk in match_keys:
        ip = os.path.join(base_dir, mk, "incidents_clean.csv")
        if not os.path.exists(ip):
            continue
        inc = pd.read_csv(ip)
        if "type" not in inc.columns:
            continue
        chaco_is_home = is_home_match(mk)
        gl = inc[inc["type"] == "goal"]
        for _, r in gl.iterrows():
            if bool(r.get("is_home", True)) != chaco_is_home:
                continue  # gol del rival
            scorer = str(r.get("player", "")).strip()
            if not scorer or scorer.lower() == "nan":
                continue
            goals[scorer] += 1
            asr = r.get("assist")
            if pd.notna(asr) and str(asr).strip() and str(asr).strip().lower() != "nan":
                asr = str(asr).strip()
                assists[asr] += 1
                pair[(asr, scorer)] += 1

    names = set(goals) | set(assists)
    nodes = pd.DataFrame(
        [{"player": n, "goals": goals.get(n, 0), "assists": assists.get(n, 0)}
         for n in names])
    if not nodes.empty:
        nodes = nodes.sort_values(["goals", "assists"], ascending=False).reset_index(drop=True)
    edges = pd.DataFrame(
        [{"assister": a, "scorer": s, "count": c} for (a, s), c in pair.items()])
    if not edges.empty:
        edges = edges.sort_values("count", ascending=False).reset_index(drop=True)
    else:
        edges = pd.DataFrame(columns=["assister", "scorer", "count"])
    return nodes, edges


# ─── Calendario de carga (minutos + descanso) ────────────────────────────────

def load_calendar(match_keys, base_dir, top_n=16, players=None):
    """
    Carga de minutos por jugador a lo largo del calendario + días de descanso
    entre partidos. Usa event_clean (fecha real del partido) y lineups_clean
    (minutos de Chaco).

    `players` (opcional): iterable de nombres a mostrar. Si se pasa, reemplaza
    al ranking por minutos totales de top_n — necesario para que los refuerzos
    de mitad de año entren al calendario, que es justamente donde se ve cómo
    cambió el reparto de minutos cuando llegaron.

    Devuelve (matrix_df, meta_df):
      matrix_df: índice = jugador, columnas = etiquetas de partido en orden,
                 valores = minutos jugados (0 si no jugó). Solo top_n jugadores
                 con más minutos totales (o los de `players`).
      meta_df:   una fila por partido (label, date, opponent, venue, rest_days)
    """
    from datetime import datetime

    def _match_date(mk):
        ev = os.path.join(base_dir, mk, "event_clean.csv")
        if os.path.exists(ev):
            e = pd.read_csv(ev)
            if not e.empty and "start_time_utc" in e.columns:
                try:
                    return pd.to_datetime(e.iloc[0]["start_time_utc"]).tz_localize(None)
                except Exception:
                    pass
        return pd.to_datetime(get_match_date(mk))

    dated = sorted(match_keys, key=_match_date)
    per_player = {}
    meta_rows = []
    prev_date = None
    for mk in dated:
        d = _match_date(mk)
        rest = (d - prev_date).days if prev_date is not None else None
        prev_date = d
        opp = get_opponent(mk)
        venue = "L" if is_home_match(mk) else "V"
        label = f"{d.strftime('%d/%m')} {opp[:10]} ({venue})"
        meta_rows.append({"match_key": mk, "label": label, "date": d,
                          "opponent": opp, "venue": venue, "rest_days": rest})
        lp = os.path.join(base_dir, mk, "lineups_clean.csv")
        if not os.path.exists(lp):
            continue
        lin = pd.read_csv(lp)
        side = "home" if is_home_match(mk) else "away"
        team = lin[lin["team_side"] == side]
        for _, r in team.iterrows():
            mins = pd.to_numeric(r.get("minutes_played"), errors="coerce")
            if pd.isna(mins):
                mins = 0.0
            per_player.setdefault(r["player_name"], {})[label] = float(mins)

    meta_df = pd.DataFrame(meta_rows)
    labels = meta_df["label"].tolist()
    matrix = pd.DataFrame(per_player).T.reindex(columns=labels).fillna(0.0)
    matrix["__total__"] = matrix.sum(axis=1)
    matrix = matrix.sort_values("__total__", ascending=False)
    if players is not None:
        matrix = matrix[matrix.index.isin(set(players))]
    else:
        matrix = matrix.head(top_n)
    matrix = matrix.drop(columns="__total__")
    return matrix, meta_df


# ─── Amenaza por tipo de jugada ──────────────────────────────────────────────

# Agrupación de la columna `situation` del shotmap en categorías legibles.
_SITUATION_GROUP = {
    "regular": "Juego abierto",
    "fast-break": "Contraataque",
    "corner": "Córner",
    "free-kick": "Tiro libre",
    "set-piece": "Pelota parada",
    "throw-in-set-piece": "Lateral",
    "penalty": "Penal",
}
_SITUATION_ORDER = ["Juego abierto", "Contraataque", "Córner", "Tiro libre",
                    "Lateral", "Pelota parada", "Penal"]


def threat_by_situation(match_keys, base_dir):
    """
    Goles, xG y tiros a favor y en contra según el tipo de jugada (`situation`
    del shotmap): juego abierto vs pelota parada, córner, etc. Responde de dónde
    vienen los goles propios y en contra (accionable para entrenar la semana).

    Devuelve un DataFrame: situation, shots_for, shots_against, goals_for,
    goals_against, xg_for, xg_against.
    """
    from collections import defaultdict
    acc = defaultdict(lambda: {"shots_for": 0, "shots_against": 0,
                               "goals_for": 0, "goals_against": 0,
                               "xg_for": 0.0, "xg_against": 0.0})
    for mk in match_keys:
        sp = os.path.join(base_dir, mk, "shotmap_clean.csv")
        if not os.path.exists(sp):
            continue
        df = pd.read_csv(sp)
        home_match = is_home_match(mk)
        for _, r in df.iterrows():
            grp = _SITUATION_GROUP.get(str(r.get("situation")), "Juego abierto")
            is_chaco = bool(r.get("isHome")) == home_match
            side = "for" if is_chaco else "against"
            acc[grp][f"shots_{side}"] += 1
            xg = pd.to_numeric(r.get("xg"), errors="coerce")
            acc[grp][f"xg_{side}"] += float(xg) if pd.notna(xg) else 0.0
            if str(r.get("shotType")) == "goal":
                acc[grp][f"goals_{side}"] += 1

    rows = [{"situation": k, **v} for k, v in acc.items()]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["__ord"] = df["situation"].map(
        {s: i for i, s in enumerate(_SITUATION_ORDER)}).fillna(99)
    df["xg_for"] = df["xg_for"].round(2)
    df["xg_against"] = df["xg_against"].round(2)
    return df.sort_values("__ord").drop(columns="__ord").reset_index(drop=True)


# ─── xG según estado del marcador ────────────────────────────────────────────

def _score_events(match_key, base_dir):
    """Lista ordenada de (minuto, delta_chaco) por cada gol del partido."""
    ip = os.path.join(base_dir, match_key, "incidents_clean.csv")
    if not os.path.exists(ip):
        return []
    inc = pd.read_csv(ip)
    if "type" not in inc.columns:
        return []
    chaco_is_home = is_home_match(match_key)
    ev = []
    for _, r in inc[inc["type"] == "goal"].iterrows():
        m = pd.to_numeric(r.get("minute"), errors="coerce")
        if pd.isna(m):
            continue
        delta = 1 if bool(r.get("is_home", True)) == chaco_is_home else -1
        ev.append((float(m), delta))
    return sorted(ev, key=lambda x: x[0])


def _state_label(diff):
    return "Ganando" if diff > 0 else ("Perdiendo" if diff < 0 else "Empatando")


def xg_by_score_state(match_keys, base_dir):
    """
    xG y tiros a favor y en contra según el estado del marcador de Chaco
    (ganando / empatando / perdiendo) al momento de cada tiro, más los minutos
    jugados en cada estado (para normalizar por 90'). Responde si el equipo
    genera cuando va arriba o se repliega de más.

    Devuelve un DataFrame: state, minutes, shots_for, shots_against, goals_for,
    goals_against, xg_for, xg_against, xg_for_p90, xg_against_p90.
    """
    from collections import defaultdict
    minutes = defaultdict(float)
    agg = defaultdict(lambda: {"shots_for": 0, "shots_against": 0,
                               "goals_for": 0, "goals_against": 0,
                               "xg_for": 0.0, "xg_against": 0.0})

    for mk in match_keys:
        ev = _score_events(mk, base_dir)
        # minutos por estado
        sp = os.path.join(base_dir, mk, "shotmap_clean.csv")
        max_shot = 0.0
        shots = pd.DataFrame()
        if os.path.exists(sp):
            shots = pd.read_csv(sp)
            mm = pd.to_numeric(shots.get("time"), errors="coerce")
            max_shot = float(mm.max()) if mm.notna().any() else 0.0
        end = max(90.0, max_shot, ev[-1][0] if ev else 0.0)
        prev, diff = 0.0, 0
        for m, delta in ev:
            minutes[_state_label(diff)] += max(0.0, m - prev)
            diff += delta
            prev = m
        minutes[_state_label(diff)] += max(0.0, end - prev)

        # tiros por estado (marcador ANTES del tiro: goles con minuto < t)
        if shots.empty:
            continue
        home_match = is_home_match(mk)
        for _, r in shots.iterrows():
            t = pd.to_numeric(r.get("time"), errors="coerce")
            if pd.isna(t):
                continue
            d = sum(delta for (m, delta) in ev if m < float(t))
            st = _state_label(d)
            is_chaco = bool(r.get("isHome")) == home_match
            side = "for" if is_chaco else "against"
            agg[st][f"shots_{side}"] += 1
            xg = pd.to_numeric(r.get("xg"), errors="coerce")
            agg[st][f"xg_{side}"] += float(xg) if pd.notna(xg) else 0.0
            if str(r.get("shotType")) == "goal":
                agg[st][f"goals_{side}"] += 1

    order = ["Ganando", "Empatando", "Perdiendo"]
    rows = []
    for st in order:
        d = agg[st]
        mins = minutes[st]
        rows.append({
            "state": st, "minutes": round(mins, 1),
            **{k: (round(v, 2) if k.startswith("xg") else v) for k, v in d.items()},
            "xg_for_p90": round(d["xg_for"] / (mins / 90.0), 2) if mins else 0.0,
            "xg_against_p90": round(d["xg_against"] / (mins / 90.0), 2) if mins else 0.0,
        })
    return pd.DataFrame(rows)


# ─── Toques en último tercio / área rival ────────────────────────────────────

def final_third_touches(match_keys, base_dir, top_n=14, min_touches=40,
                        players=None):
    """
    Participación ofensiva por jugador de Chaco: toques totales y cuántos caen en
    el último tercio (x>66, coords OPTA 0-100) y dentro del área rival
    (x>83 y 21.1<y<78.9). No necesita datos de pases. Sale de player_heatmaps.

    `players` (opcional): iterable de nombres al que restringir el resultado —
    p.ej. el plantel con muestra suficiente (ver relevant_players), para que un
    refuerzo no quede afuera solo por el ranking de top_n.

    Devuelve un DataFrame: player, touches, final_third, box, pct_final_third,
    ordenado por toques en el último tercio (desc), top_n jugadores.
    Ojo: los toques son ACUMULADOS del año, así que un jugador que llegó a
    mitad de temporada va a mostrar barras más cortas aunque participe mucho.
    """
    from collections import defaultdict
    tot = defaultdict(int)
    f3 = defaultdict(int)
    box = defaultdict(int)
    for mk in match_keys:
        hp = os.path.join(base_dir, mk, "player_heatmaps_clean.csv")
        if not os.path.exists(hp):
            continue
        h = pd.read_csv(hp)
        side = "home" if is_home_match(mk) else "away"
        team = h[h["team_side"] == side]
        for _, r in team.iterrows():
            name = r["player_name"]
            x = pd.to_numeric(r.get("x"), errors="coerce")
            y = pd.to_numeric(r.get("y"), errors="coerce")
            if pd.isna(x) or pd.isna(y):
                continue
            tot[name] += 1
            if x > 66:
                f3[name] += 1
            if x > 83 and 21.1 < y < 78.9:
                box[name] += 1

    allowed = set(players) if players is not None else None
    rows = [{"player": p, "touches": tot[p], "final_third": f3[p], "box": box[p],
             "pct_final_third": round(100 * f3[p] / tot[p], 1) if tot[p] else 0.0}
            for p in tot
            if tot[p] >= min_touches and (allowed is None or p in allowed)]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values("final_third", ascending=False).head(top_n).reset_index(drop=True)


# ─── Cadena de Markov del estado del marcador ────────────────────────────────

_MARKOV_STATES = ["S--", "S-", "S0", "S+", "S++"]


def _diff_to_state(diff):
    if diff >= 2:
        return "S++"
    if diff == 1:
        return "S+"
    if diff == 0:
        return "S0"
    if diff == -1:
        return "S-"
    return "S--"


def markov_game_state(match_keys, base_dir):
    """
    Cadena de Markov del estado del marcador desde la perspectiva de Chaco:
    S++ (ganando 2+), S+ (ganando 1), S0 (empate), S- (perdiendo 1), S--
    (perdiendo 2+). Cada gol de la temporada dispara una transición de
    estado; se arma la matriz estocástica empírica P (fila = estado de
    origen, normalizada a que sume 1) contando cuántas veces se pasó de un
    estado a otro. También se conserva el detalle crudo con el minuto de
    cada transición, para poder mirar en qué tramo del partido ocurren
    (p.ej. si las ventajas de 1 gol se diluyen tarde → "pánico táctico").

    Usa incidents_clean (home_score/away_score ya acumulados en cada
    incidente de gol) + is_home_match para saber la perspectiva de Chaco.

    Devuelve (matrix_df, transitions_df):
      matrix_df: 5x5 (S--..S++), P[i, j] = prob. de pasar de i a j
      transitions_df: match_key, minute, from_state, to_state
    """
    from collections import defaultdict
    trans_rows = []
    counts = defaultdict(lambda: defaultdict(int))

    for mk in match_keys:
        ip = os.path.join(base_dir, mk, "incidents_clean.csv")
        if not os.path.exists(ip):
            continue
        inc = pd.read_csv(ip)
        if "type" not in inc.columns:
            continue
        chaco_home = is_home_match(mk)
        goals = inc[inc["type"] == "goal"].copy()
        goals["minute"] = pd.to_numeric(goals["minute"], errors="coerce")
        goals = goals.dropna(subset=["minute"]).sort_values("minute")

        current = "S0"
        for _, r in goals.iterrows():
            home_score = pd.to_numeric(r.get("home_score"), errors="coerce")
            away_score = pd.to_numeric(r.get("away_score"), errors="coerce")
            if pd.isna(home_score) or pd.isna(away_score):
                continue
            diff = (home_score - away_score) if chaco_home else (away_score - home_score)
            nxt = _diff_to_state(diff)
            counts[current][nxt] += 1
            trans_rows.append({"match_key": mk, "minute": float(r["minute"]),
                               "from_state": current, "to_state": nxt})
            current = nxt

    matrix = pd.DataFrame(0.0, index=_MARKOV_STATES, columns=_MARKOV_STATES)
    for i in _MARKOV_STATES:
        total = sum(counts[i].values())
        if total:
            for j in _MARKOV_STATES:
                matrix.loc[i, j] = counts[i][j] / total
    transitions_df = pd.DataFrame(trans_rows) if trans_rows else pd.DataFrame(
        columns=["match_key", "minute", "from_state", "to_state"])
    return matrix, transitions_df


# ─── Centralidad de eigenvector en minutos compartidos ───────────────────────

def eigenvector_centrality_network(nodes_df, edges_df, min_minutes=180):
    """
    Centralidad de eigenvector sobre el grafo de minutos compartidos
    (shared_minutes_network): identifica qué jugadores son el verdadero
    "núcleo" del equipo, no solo por cuánto juegan sino por cómo le fue al
    equipo cuando compartieron cancha con otros jugadores importantes.

    El peso de cada arista pondera los minutos juntos por el rendimiento neto
    de esa dupla (gd_per90 = diferencia de gol cada 90'). Centralidad de
    eigenvector requiere pesos no negativos para converger a una solución con
    sentido (Perron-Frobenius); por eso el peso se re-escala como
    minutos_juntos * (1 + gd_per90/10), acotado a un piso de
    minutos_juntos * 0.1 (una dupla mala no cae a ~0 o negativo, solo pesa
    menos que una neutra).

    Devuelve nodes_df con una columna nueva 'eigen_centrality' (0-1,
    normalizada por el máximo), ordenado descendente.
    """
    import networkx as nx

    out = nodes_df.copy()
    out["eigen_centrality"] = 0.0
    if edges_df is None or edges_df.empty:
        return out

    ed = edges_df[edges_df["minutes_together"] >= min_minutes].copy()
    if ed.empty:
        return out
    ed["weight"] = ed["minutes_together"] * (1 + ed["gd_per90"] / 10.0)
    ed["weight"] = ed["weight"].clip(lower=ed["minutes_together"] * 0.1)

    G = nx.Graph()
    for _, r in ed.iterrows():
        G.add_edge(r["p1"], r["p2"], weight=float(r["weight"]))
    if G.number_of_edges() == 0:
        return out

    cent = nx.eigenvector_centrality_numpy(G, weight="weight")
    out["eigen_centrality"] = out["player_name"].map(cent).fillna(0.0)
    maxc = out["eigen_centrality"].max()
    if maxc > 0:
        out["eigen_centrality"] = out["eigen_centrality"] / maxc
    return out.sort_values("eigen_centrality", ascending=False).reset_index(drop=True)


# ─── Entropía espacial de Shannon del shotmap ────────────────────────────────

def shot_entropy(match_keys, base_dir, bins=5, x_min=0.0, chaco_only=True):
    """
    Entropía de Shannon de la distribución espacial del peligro generado
    (ponderada por xG). Divide la zona de tiro en una grilla de bins x bins y
    mide qué tan repartido está el ataque entre esas celdas: entropía alta =
    ataque impredecible (peligro parejo entre sectores); entropía baja = el
    equipo siempre genera desde el mismo sector — fácil de leer para el rival.

    OJO con el sistema de coordenadas: `coord_x` del shotmap es la distancia
    AL ARCO que se ataca (0 = línea de gol, crece alejándose) — al revés de
    la convención "0→100 en la dirección de ataque" que usan los heatmaps de
    jugadores. Por eso acá no se recorta un "último tercio" por x_min; casi
    todo el shotmap ya es, por definición, zona de tiro (en 2026 coord_x va
    de ~3 a ~56). x_min se deja como parámetro por si se lo quiere acotar.

    H = -sum(P_i * log2(P_i)),  P_i = xG de la celda i / xG total.
    Máximo teórico = log2(bins**2) (peligro perfectamente parejo).

    Devuelve dict: entropy, max_entropy, pct_of_max, n_shots, bins, x_min,
    zone_xg (DataFrame x_bin, y_bin, xg, pct — para graficar la grilla).
    """
    frames = []
    for mk in match_keys:
        sp = os.path.join(base_dir, mk, "shotmap_clean.csv")
        if not os.path.exists(sp):
            continue
        df = pd.read_csv(sp)
        if df.empty:
            continue
        if chaco_only:
            home_match = is_home_match(mk)
            df = df[df["isHome"].astype(bool) == home_match]
        frames.append(df[["coord_x", "coord_y", "xg"]])

    max_entropy = float(np.log2(bins * bins))
    empty = {"entropy": 0.0, "max_entropy": round(max_entropy, 3), "pct_of_max": 0.0,
             "n_shots": 0, "bins": bins, "x_min": x_min, "zone_xg": pd.DataFrame()}
    if not frames:
        return empty

    shots = pd.concat(frames, ignore_index=True)
    shots["coord_x"] = pd.to_numeric(shots["coord_x"], errors="coerce")
    shots["coord_y"] = pd.to_numeric(shots["coord_y"], errors="coerce")
    shots["xg"] = pd.to_numeric(shots["xg"], errors="coerce").fillna(0.0)
    shots = shots.dropna(subset=["coord_x", "coord_y"])
    shots = shots[shots["coord_x"] >= x_min]
    if shots.empty:
        return empty

    x_edges = np.linspace(x_min, 100.0, bins + 1)
    y_edges = np.linspace(0.0, 100.0, bins + 1)
    shots["x_bin"] = pd.cut(shots["coord_x"], bins=x_edges, labels=False, include_lowest=True)
    shots["y_bin"] = pd.cut(shots["coord_y"], bins=y_edges, labels=False, include_lowest=True)
    shots = shots.dropna(subset=["x_bin", "y_bin"])

    zone_xg = shots.groupby(["x_bin", "y_bin"], as_index=False)["xg"].sum()
    total_xg = zone_xg["xg"].sum()
    if total_xg <= 0:
        return {**empty, "n_shots": len(shots), "zone_xg": zone_xg}

    zone_xg["pct"] = zone_xg["xg"] / total_xg
    p = zone_xg["pct"].values
    entropy = float(-np.sum(p * np.log2(p + 1e-9)))
    return {"entropy": round(entropy, 3), "max_entropy": round(max_entropy, 3),
            "pct_of_max": round(100 * entropy / max_entropy, 1) if max_entropy else 0.0,
            "n_shots": len(shots), "bins": bins, "x_min": x_min, "zone_xg": zone_xg}


# ─── Riesgo de colapso defensivo (Cox Proportional Hazards) ─────────────────

def build_defensive_survival_dataset(match_keys, base_dir, xg_threshold=0.15,
                                     fatigue_window_days=14):
    """
    Arma el dataset de supervivencia para el modelo de riesgo de colapso
    defensivo: por cada partido, cuánto tardó el rival en generar un tiro
    peligroso (xG >= xg_threshold) según la fatiga acumulada por la línea
    defensiva (minutos jugados por los defensores 'D' de Chaco en los
    `fatigue_window_days` previos AL partido) y la presión del rival
    (momentum) en ese instante.

    "Falla" = primer tiro rival con xG >= xg_threshold. duration = su minuto;
    si no ocurrió ninguno, duration = fin del partido (90 o el último tiro
    registrado, lo que sea mayor) y event=0 (censurado).

    NOTA: momentum_at_risk toma el valor de momentum en el minuto de
    duration — es una simplificación (CoxPHFitter estándar asume covariables
    fijas por fila, no verdaderamente variables en el tiempo), suficiente
    para una lectura direccional del cuerpo técnico, no para un paper.

    Devuelve un DataFrame: match_key, duration, event, defensive_fatigue,
    momentum_at_risk.
    """
    def _match_date(mk):
        ev = os.path.join(base_dir, mk, "event_clean.csv")
        if os.path.exists(ev):
            e = pd.read_csv(ev)
            if not e.empty and "start_time_utc" in e.columns:
                try:
                    return pd.to_datetime(e.iloc[0]["start_time_utc"]).tz_localize(None)
                except Exception:
                    pass
        return pd.to_datetime(get_match_date(mk))

    dated = sorted(match_keys, key=_match_date)
    history = []  # (fecha, minutos de defensores) de partidos ya procesados
    rows = []

    for mk in dated:
        d = _match_date(mk)
        fatigue = sum(mins for (hd, mins) in history
                      if 0 < (d - hd).days <= fatigue_window_days)

        lp = os.path.join(base_dir, mk, "lineups_clean.csv")
        def_minutes = 0.0
        if os.path.exists(lp):
            lin = pd.read_csv(lp)
            side = "home" if is_home_match(mk) else "away"
            team = lin[(lin["team_side"] == side) & (lin["position"] == "D")]
            def_minutes = float(pd.to_numeric(team["minutes_played"], errors="coerce")
                                .fillna(0.0).sum())

        sp = os.path.join(base_dir, mk, "shotmap_clean.csv")
        duration, event = 90.0, 0
        if os.path.exists(sp):
            shots = pd.read_csv(sp)
            if not shots.empty:
                home_match = is_home_match(mk)
                shots["time"] = pd.to_numeric(shots["time"], errors="coerce")
                rival_shots = shots[shots["isHome"].astype(bool) != home_match].copy()
                rival_shots["xg"] = pd.to_numeric(rival_shots["xg"], errors="coerce")
                all_times = shots["time"].dropna()
                last_time = float(all_times.max()) if not all_times.empty else 90.0
                risky = rival_shots[rival_shots["xg"] >= xg_threshold].dropna(subset=["time"])
                if not risky.empty:
                    risky = risky.sort_values("time")
                    duration, event = max(float(risky.iloc[0]["time"]), 0.1), 1
                else:
                    duration = max(90.0, last_time)

        momentum_at_risk = 0.0
        mp = os.path.join(base_dir, mk, "momentum_clean.csv")
        if os.path.exists(mp):
            mom = pd.read_csv(mp)
            if not mom.empty and "minute" in mom.columns:
                mom["minute"] = pd.to_numeric(mom["minute"], errors="coerce")
                mom = mom.dropna(subset=["minute"])
                if not mom.empty:
                    idx = (mom["minute"] - duration).abs().idxmin()
                    momentum_at_risk = float(mom.loc[idx, "value"])

        rows.append({"match_key": mk, "duration": duration, "event": event,
                     "defensive_fatigue": fatigue, "momentum_at_risk": momentum_at_risk})
        history.append((d, def_minutes))

    return pd.DataFrame(rows)


def fit_defensive_hazard_model(df_survival):
    """
    Ajusta el modelo de riesgo proporcional de Cox sobre el dataset de
    build_defensive_survival_dataset. Requiere `lifelines`. Devuelve el
    CoxPHFitter ya ajustado (cph.summary trae los hazard ratios en
    exp(coef)).

    Con ~34 partidos la muestra es chica para Cox: tomar los hazard ratios
    como una señal direccional para el cuerpo técnico, no como un resultado
    estadísticamente definitivo.
    """
    from lifelines import CoxPHFitter
    cph = CoxPHFitter()
    cph.fit(df_survival[["duration", "event", "defensive_fatigue", "momentum_at_risk"]],
            duration_col="duration", event_col="event")
    return cph


# ─── Goles por ventana de tiempo ──────────────────────────────────────────────

_TIME_WINDOWS = [(0, 15), (15, 30), (30, 45), (45, 60), (60, 75), (75, 90), (90, 200)]
_TIME_LABELS = ["0-15'", "15-30'", "30-45'", "45-60'", "60-75'", "75-90'", "90+'"]


def goals_by_time_window(match_keys, base_dir, windows=None):
    """
    Distribución de los goles de Chaco (a favor y en contra) por ventana de
    tiempo del partido. Responde en qué minutos el equipo hace goles y en
    cuáles los recibe — complemento temporal de markov_game_state (esa mide
    el ESTADO del marcador; esta mide el MOMENTO en que se mueve).

    Usa incidents_clean (type=='goal', minute, is_home) + is_home_match.

    Devuelve un DataFrame: window (etiqueta), goals_for, goals_against,
    pct_for (% de los goles a favor de la temporada que caen en esa ventana),
    pct_against (ídem en contra).
    """
    windows = windows or _TIME_WINDOWS
    labels = _TIME_LABELS if windows is _TIME_WINDOWS else [f"{a}-{b}'" for a, b in windows]

    def _bucket(m):
        for (lo, hi), lab in zip(windows, labels):
            if lo <= m < hi:
                return lab
        return labels[-1]

    from collections import defaultdict
    gf = defaultdict(int)
    ga = defaultdict(int)

    for mk in match_keys:
        ip = os.path.join(base_dir, mk, "incidents_clean.csv")
        if not os.path.exists(ip):
            continue
        inc = pd.read_csv(ip)
        if "type" not in inc.columns:
            continue
        chaco_home = is_home_match(mk)
        goals = inc[inc["type"] == "goal"].copy()
        goals["minute"] = pd.to_numeric(goals["minute"], errors="coerce")
        for _, r in goals.dropna(subset=["minute"]).iterrows():
            lab = _bucket(float(r["minute"]))
            if bool(r.get("is_home", True)) == chaco_home:
                gf[lab] += 1
            else:
                ga[lab] += 1

    total_for = sum(gf.values()) or 1
    total_against = sum(ga.values()) or 1
    rows = [{"window": lab, "goals_for": gf[lab], "goals_against": ga[lab],
             "pct_for": round(100 * gf[lab] / total_for, 1),
             "pct_against": round(100 * ga[lab] / total_against, 1)}
            for lab in labels]
    return pd.DataFrame(rows)
