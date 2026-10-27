"""
players.py
==========
Análisis individual de jugadores con contexto comparativo.

El "pool" agrega a TODOS los jugadores que aparecen en los lineups de los
partidos scrapeados (Chaco + cada rival enfrentado). Eso da una población
de referencia de la Primera Nacional para calcular percentiles por-90,
que alimentan el radar de pizza y el radar clásico.
"""

import os
import pandas as pd
import numpy as np

import config
from src.analysis.season import load_matches


# Métricas del pizza/radar agrupadas por faceta del juego.
# Clave = columna en lineups_clean.csv, valor = etiqueta para mostrar.
PIZZA_METRICS = {
    "ataque": {
        "goals":               "Goles",
        "xg":                  "xG",
        "shots_on_target":     "Tiros al arco",
        "dribbles_won":        "Regates ganados",
    },
    "posesion": {
        "accurate_passes":     "Pases precisos",
        "key_passes":          "Pases clave",
        "xa":                  "xA",
        "touches":             "Toques",
    },
    "defensa": {
        "tackles":             "Quites",
        "interceptions":       "Intercepciones",
        "clearances":          "Despejes",
        "duels_won":           "Duelos ganados",
    },
}

# Colores por grupo (mismo orden que PIZZA_METRICS)
PIZZA_GROUP_COLORS = {
    "ataque":   "#d62728",   # rojo
    "posesion": "#e8a200",   # ámbar
    "defensa":  "#2b3a67",   # azul pizarra
}


def _all_pizza_metrics():
    cols = {}
    for group in PIZZA_METRICS.values():
        cols.update(group)
    return cols


# SofaScore escribe el mismo club con dos nombres en distintos partidos. Sin
# normalizar, al agrupar por (jugador, equipo) un jugador de ese club queda
# partido en dos filas con la mitad de la muestra cada una.
_TEAM_NAME_ALIASES = {
    "Gimnasia Y Esgrima De Jujuy": "Gimnasia Jujuy",
}


def player_pool(match_keys=None, base_dir=None, season=None, min_minutes=90,
                sources=None, ajustado=True):
    """
    Agrega los lineups de todos los partidos (AMBOS equipos) en una tabla
    por jugador con métricas por-90.

    min_minutes filtra jugadores con poca muestra. Default 90' (un partido
    completo): cada rival solo aparece ~2 veces contra Chaco, así que un
    umbral alto dejaría el pool casi solo con jugadores de Chaco.

    `sources` permite armar un pool a partir de VARIAS carpetas de datos a la
    vez (lista de tuplas (base_dir, [match_keys])) — p.ej. mezclar los partidos
    de Chaco con los del rival para comparar un jugador de cada equipo en el
    mismo pool. Si no se pasa, usa el par (base_dir, match_keys) clásico.

    `ajustado` (default True): los partidos desde el 1/7/2026 se llevan a la
    escala de antes del cambio de medición de SofaScore (quites -55%, despejes
    +77%, regates -35%...; ver src/jugadores/consultas.py). Es el mismo ajuste
    que usa scouting.pool_liga(), así la pizza de un jugador de Chaco y el pool
    de la liga están en la misma escala. False = números crudos.

    Retorna DataFrame: player_name, team_name, matches, minutes, is_chaco,
                       y cada métrica de PIZZA_METRICS en valor por-90.
    """
    if sources is None:
        base_dir = base_dir or config.season_data_dir(season)
        if match_keys is None:
            match_keys = list(load_matches(season).keys())
        sources = [(base_dir, match_keys)]

    metric_cols = list(_all_pizza_metrics().keys())
    frames = []
    for bdir, mks in sources:
        for mk in mks:
            path = os.path.join(bdir, mk, "lineups_clean.csv")
            if not os.path.exists(path):
                continue
            df = pd.read_csv(path)
            df["match_key"] = mk
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    all_df = pd.concat(frames, ignore_index=True)
    for c in metric_cols + ["minutes_played"]:
        all_df[c] = pd.to_numeric(all_df.get(c), errors="coerce").fillna(0)

    if "position" not in all_df.columns:
        all_df["position"] = ""
    all_df["team_name"] = all_df["team_name"].replace(_TEAM_NAME_ALIASES)

    if ajustado:
        # Import diferido: src.jugadores importa src.analysis.
        from src.jugadores import consultas as Q
        from src.scraping.chaco_scraper import PLAYER_STAT_FIELDS
        a_crudo = {limpio: crudo for crudo, limpio in PLAYER_STAT_FIELDS.items()}
        all_df = Q.ajustar_tabla(
            all_df, fechas=all_df["match_key"].astype(str).str[:10],
            posiciones=all_df["position"],
            columnas={c: a_crudo[c] for c in metric_cols if c in a_crudo})

    # Se agrupa por (jugador, EQUIPO), no solo por jugador: un lineup trae los
    # dos equipos del partido, así que un homónimo o un jugador que cambió de
    # club a mitad de año (ej. G. Ramirez: All Boys → Chaco; A. Alonso: Gimnasia
    # Jujuy → Chaco) sumaría sus minutos de los DOS clubes en una sola fila.
    # Con el corte por equipo, el pizza de un jugador de Chaco toma SOLO sus
    # partidos con Chaco en esta temporada.
    grouped = (all_df.groupby(["player_name", "team_name"])
               .agg(position=("position", "last"),
                    matches=("match_key", "nunique"),
                    minutes=("minutes_played", "sum"),
                    **{c: (c, "sum") for c in metric_cols})
               .reset_index())

    grouped = grouped[grouped["minutes"] >= min_minutes].copy()

    # Por-90
    for c in metric_cols:
        grouped[f"{c}_p90"] = (grouped[c] / grouped["minutes"] * 90).round(2)

    grouped["is_chaco"] = grouped["team_name"].str.contains(
        "Chaco", case=False, na=False)
    return grouped.reset_index(drop=True)


def player_percentiles(player_name, pool_df=None, season=None, reference_df=None,
                       team_name=None):
    """
    Percentil (0-100) del jugador en cada métrica por-90 vs el pool completo.

    `reference_df` (opcional): pool contra el que se calcula el percentil,
    cuando es distinto de aquel donde se busca al jugador. Sirve para graficar
    a alguien con pocos minutos (que se busca en un pool sin filtrar) pero
    comparándolo siempre contra la misma referencia de la liga (jugadores con
    90'+), para que la escala no cambie de un pizza a otro.

    `team_name` (opcional): desambigua homónimos / jugadores que cambiaron de
    club — el pool ahora tiene una fila por (jugador, equipo).

    Retorna dict: {grupo: [(etiqueta, percentil, valor_p90), ...]}
    o None si el jugador no está en el pool.
    """
    if pool_df is None or pool_df.empty:
        pool_df = player_pool(season=season)
    if pool_df.empty:
        return None
    ref_df = reference_df if reference_df is not None and not reference_df.empty else pool_df

    row = pool_df[pool_df["player_name"] == player_name]
    if team_name is not None and "team_name" in row.columns:
        row = row[row["team_name"] == team_name]
    if row.empty:
        return None
    # más de una fila (homónimo sin desambiguar): la de más minutos
    row = row.sort_values("minutes", ascending=False).iloc[0] if "minutes" in row.columns else row.iloc[0]

    result = {}
    for group, metrics in PIZZA_METRICS.items():
        entries = []
        for col, label in metrics.items():
            p90_col = f"{col}_p90"
            val = row[p90_col]
            pct = round((ref_df[p90_col] < val).mean() * 100)
            entries.append((label, int(pct), float(val)))
        result[group] = entries
    return result


def compare_players(player_a, player_b, pool_df=None, season=None):
    """
    Valores por-90 de dos jugadores para el radar clásico, con los rangos
    (min-max del pool) de cada métrica para escalar los ejes.

    Retorna dict: labels, values_a, values_b, ranges [(low, high), ...]
    o None si alguno no está en el pool.
    """
    if pool_df is None or pool_df.empty:
        pool_df = player_pool(season=season)
    if pool_df.empty:
        return None

    def _pick(name):
        r = pool_df[pool_df["player_name"] == name]
        if r.empty:
            return None
        return (r.sort_values("minutes", ascending=False).iloc[0]
                if "minutes" in r.columns else r.iloc[0])

    row_a, row_b = _pick(player_a), _pick(player_b)
    if row_a is None or row_b is None:
        return None

    labels, values_a, values_b, ranges = [], [], [], []
    for group, metrics in PIZZA_METRICS.items():
        for col, label in metrics.items():
            p90_col = f"{col}_p90"
            labels.append(label)
            values_a.append(float(row_a[p90_col]))
            values_b.append(float(row_b[p90_col]))
            lo = float(pool_df[p90_col].quantile(0.05))
            hi = float(pool_df[p90_col].quantile(0.95))
            if hi <= lo:
                hi = lo + 1e-6
            ranges.append((lo, hi))

    return {
        "labels":   labels,
        "values_a": values_a,
        "values_b": values_b,
        "ranges":   ranges,
        "player_a": player_a,
        "player_b": player_b,
    }
