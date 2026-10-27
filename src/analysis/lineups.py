"""
lineups.py
==========
Impacto de duplas y tríos de MEDIOCAMPO de Chaco For Ever.

Para cada combinación de N jugadores (default: los volantes centrales), calcula
cuánto tiempo jugaron JUNTOS y cómo le fue al equipo en esos minutos —
diferencia de xG y de goles por 90 — contra el resto de los minutos del equipo
("con y sin").

Se apoya en la lógica de intervalos de `season.shared_minutes_network`:
    intervalo de un jugador = [substitute_in (0 si titular), +minutes_played]

Insumos por partido (data/temporadas/{season}/partidos/{mk}/):
    lineups_clean.csv   -> quién estuvo y en qué minutos
    shotmap_clean.csv   -> tiros con minuto y xG
    incidents_clean.csv -> goles y rojas con minuto

OJO con lo que esto NO controla: rival, localía, y en los tramos con expulsados
el equipo con más hombres genera más xG. Por eso se reporta aparte el número
SOLO 11v11 (`*_11v11`). Es un embudo para mirar, no un ranking cerrado.

Uso:
    from src.analysis.lineups import chaco_midfielders, combo_impact, best_midfield
    mids = chaco_midfielders(season="2026")
    duplas = combo_impact(match_keys, base_dir, mids, size=2)
"""
import os
from itertools import combinations

import numpy as np
import pandas as pd

import config
from src.analysis.season import is_home_match

# Techo de minutos de un partido (90' + descuento). Los intervalos que se pasan
# de acá se recortan para no inflar los denominadores.
MATCH_MAX_MIN = 100.0

# Roles finos de scouting.py (rol = posición media en cancha).
CENTRAL_MID_ROLES = ("MCD", "MC")
WIDE_MID_ROLES = ("EXT_MP",)
DEF_ROLES = ("DFC",)          # zaga central
FLANK_ROLES = ("LAT", "EXT_MP")   # banda: lateral + extremo del mismo lado
ATTACK_ROLES = ("DC",)        # delantero centro
ATTACK_WIDE_ROLES = ("DC", "EXT_MP")   # ataque + banda para el trío


# ─── Roster por rol ─────────────────────────────────────────────────────────

def _pool_path(season):
    return os.path.join(config._SEASON_DATA_DIR.format(season=season),
                        "..", "pool_scouting.csv")

# rol fino → posición gruesa de SofaScore (G/D/M/F)
_ROLE_TO_POS = {"DFC": "D", "LAT": "D", "MCD": "M", "MC": "M", "EXT_MP": "M",
                "DC": "F", "ARQ": "G"}
# posición gruesa → rol fino aproximado (para los que no están en el pool bajo
# Chaco: transferidos a mitad de año, o pool viejo). Es un fallback: D podría ser
# DFC o LAT y M podría ser MCD/MC/EXT_MP — se elige el más común.
_POS_TO_ROLE = {"G": "ARQ", "D": "DFC", "M": "MC", "F": "DC"}


def _drop_left(names, exclude_left):
    """Saca a los jugadores de config.JUGADORES_FUERA (los que ya no están en
    el club). Este módulo analiza CARACTERÍSTICAS ACTUALES del equipo — la mejor
    dupla/trío de hoy —, así que por default no cuenta a los que se fueron."""
    if not exclude_left:
        return list(names)
    fuera = config.jugadores_fuera()
    return [n for n in names if str(n).strip().lower() not in fuera]


def _chaco_lineup_players(season="2026", base_dir=None):
    """Jugadores que ACTUARON para Chaco esta temporada, de los lineups del
    Negro (no del pool). Devuelve DataFrame: player_name, minutos, matches,
    position (la más común), avg_y (media de average_positions).

    Esto es lo que arregla a los que cambiaron de club a mitad de año: el pool
    de scouting los colapsa en su otro equipo (ej. M. S. Romero queda como
    Nueva Chicago), pero acá se leen sus minutos REALES con la camiseta de Chaco.
    """
    if base_dir is None:
        base_dir = config.season_data_dir(season)
    if not os.path.isdir(base_dir):
        return pd.DataFrame(columns=["player_name", "minutos", "matches", "position", "avg_y"])

    acc = {}
    for mk in sorted(os.listdir(base_dir)):
        mdir = os.path.join(base_dir, mk)
        lp = os.path.join(mdir, "lineups_clean.csv")
        if not os.path.exists(lp):
            continue
        lin = pd.read_csv(lp)
        side = "home" if is_home_match(mk) else "away"
        team = lin[lin["team_side"] == side].copy()

        ys = {}
        ap = os.path.join(mdir, "average_positions_clean.csv")
        if os.path.exists(ap):
            apdf = pd.read_csv(ap)
            for _, r in apdf[apdf["team_side"] == side].iterrows():
                pid = pd.to_numeric(r.get("player_id"), errors="coerce")
                y = pd.to_numeric(r.get("average_y"), errors="coerce")
                if pd.notna(pid) and pd.notna(y):
                    ys[int(pid)] = float(y)

        for _, r in team.iterrows():
            m = pd.to_numeric(r.get("minutes_played"), errors="coerce")
            if pd.isna(m) or m <= 0:
                continue
            n = r["player_name"]
            d = acc.setdefault(n, {"minutos": 0.0, "matches": 0, "pos": [], "ys": []})
            d["minutos"] += float(m)
            d["matches"] += 1
            if pd.notna(r.get("position")):
                d["pos"].append(r["position"])
            pid = pd.to_numeric(r.get("player_id"), errors="coerce")
            if pd.notna(pid) and int(pid) in ys:
                d["ys"].append(ys[int(pid)])

    rows = []
    for n, d in acc.items():
        pos = max(set(d["pos"]), key=d["pos"].count) if d["pos"] else None
        rows.append({
            "player_name": n, "minutos": round(d["minutos"], 1),
            "matches": d["matches"], "position": pos,
            "avg_y": (sum(d["ys"]) / len(d["ys"])) if d["ys"] else float("nan"),
        })
    return (pd.DataFrame(rows).sort_values("minutos", ascending=False)
            .reset_index(drop=True))


def _infer_banda(avg_y, anchor_y, anchor_banda):
    """Lado de un jugador a partir de su average_y media, calibrado con un
    jugador del pool cuya banda ya conocemos (para cancelar el flip local/visita).
    Devuelve 'DER' | 'IZQ' | None."""
    if pd.isna(avg_y) or pd.isna(anchor_y):
        return None
    izq_es_menor = anchor_y < 50 if anchor_banda == "IZQ" else anchor_y >= 50
    if izq_es_menor:
        return "IZQ" if avg_y < 50 else "DER"
    return "DER" if avg_y < 50 else "IZQ"


def chaco_players_by_role(season="2026", roles=(), banda=None, min_minutes=300,
                          pool_path=None, base_dir=None, exclude_left=True):
    """Jugadores de Chaco de esos roles finos, ordenados por minutos.

    `banda` in {'DER', 'IZQ'} filtra por carril (siempre incluye 'ambas').
    `exclude_left=True` (default) saca a los de config.JUGADORES_FUERA — este
    módulo es sobre el equipo de HOY, no sobre lo que pasó en la temporada.

    La lista base sale del pool de scouting (rol fino + banda). Se le SUMAN los
    jugadores que actuaron para Chaco según sus lineups y que el pool no tiene
    bajo Chaco — típicamente los que llegaron a mitad de año (el pool los deja
    en su club anterior). A esos el rol se aproxima de la posición G/D/M/F.
    """
    pool_path = pool_path or _pool_path(season)
    if base_dir is None:
        base_dir = config.season_data_dir(season)
    roles = tuple(roles)
    wanted_pos = {_ROLE_TO_POS.get(r) for r in roles}

    names, seen = [], set()
    pool_ch = pd.DataFrame()
    if os.path.exists(pool_path):
        p = pd.read_csv(pool_path)
        pool_ch = p[pd.to_numeric(p["team_id"], errors="coerce") == config.CHACO_TEAM_ID]
        ch = pool_ch[pool_ch["rol"].isin(roles)
                     & (pd.to_numeric(pool_ch["minutos"], errors="coerce") >= min_minutes)]
        if banda:
            ch = ch[ch["banda"].isin([banda, "ambas"])]
        for _, r in ch.sort_values("minutos", ascending=False).iterrows():
            names.append(r["nombre"])
            seen.add(str(r["nombre"]).strip().lower())

    # ── jugadores de los lineups de Chaco que el pool no tiene bajo Chaco ──
    lu = _chaco_lineup_players(season, base_dir)
    pool_names = set(pool_ch["nombre"].astype(str).str.strip().str.lower()) if not pool_ch.empty else set()
    extra = lu[(lu["minutos"] >= min_minutes)
               & (lu["position"].isin(wanted_pos))
               & (~lu["player_name"].astype(str).str.strip().str.lower().isin(seen | pool_names))].copy()

    # Desambiguar la posición gruesa con la amplitud (|avg_y - 50|): un 'M' con
    # avg_y ~50 es un volante central, no un extremo; un 'D' amplio es lateral.
    # Solo se aplica cuando el query pide roles de UN solo carril (central O banda).
    only_central = set(roles) <= {"DFC", "MCD", "MC"}
    only_wide = set(roles) <= {"LAT", "EXT_MP"}
    if not extra.empty and (only_central or only_wide):
        amp = (extra["avg_y"] - 50).abs()
        thr = 24.0 if "D" in wanted_pos else 20.0
        wide_enough = amp >= thr
        extra = extra[amp.isna() | (wide_enough if only_wide else ~wide_enough)]

    if banda and not extra.empty:
        # calibrar el lado con un lateral/extremo del pool cuya banda conocemos
        anchor = None
        if not pool_ch.empty:
            a = pool_ch[pool_ch["banda"].isin(["DER", "IZQ"])
                        & pool_ch["rol"].isin(("LAT", "EXT_MP"))]
            for _, ar in a.iterrows():
                ay = lu.loc[lu["player_name"] == ar["nombre"], "avg_y"]
                if not ay.empty and pd.notna(ay.iloc[0]):
                    anchor = (float(ay.iloc[0]), ar["banda"])
                    break
        keep = []
        for _, r in extra.iterrows():
            side = _infer_banda(r["avg_y"], *anchor) if anchor else None
            keep.append(side is None or side == banda)   # si no se puede inferir, se incluye
        extra = extra[pd.Series(keep, index=extra.index)]

    for _, r in extra.sort_values("minutos", ascending=False).iterrows():
        if str(r["player_name"]).strip().lower() not in seen:
            names.append(r["player_name"])
            seen.add(str(r["player_name"]).strip().lower())

    return _drop_left(names, exclude_left)


def chaco_role_map(season="2026", pool_path=None, base_dir=None):
    """{nombre: rol_fino} para los jugadores de Chaco. Sale del pool; a los que
    no están en el pool bajo Chaco (transferidos a mitad de año) se les aproxima
    el rol de la posición G/D/M/F de sus lineups."""
    rmap = {}
    pool_path = pool_path or _pool_path(season)
    if os.path.exists(pool_path):
        p = pd.read_csv(pool_path)
        ch = p[pd.to_numeric(p["team_id"], errors="coerce") == config.CHACO_TEAM_ID]
        rmap.update(dict(zip(ch["nombre"], ch["rol"])))
    for _, r in _chaco_lineup_players(season, base_dir).iterrows():
        if r["player_name"] in rmap or r["position"] not in _POS_TO_ROLE:
            continue
        rol = _POS_TO_ROLE[r["position"]]
        amp = abs(r["avg_y"] - 50) if pd.notna(r["avg_y"]) else None
        if amp is not None:
            if r["position"] == "D":
                rol = "LAT" if amp >= 24 else "DFC"
            elif r["position"] == "M":
                rol = "EXT_MP" if amp >= 20 else "MC"
        rmap[r["player_name"]] = rol
    return rmap


def chaco_midfielders(season="2026", roles=CENTRAL_MID_ROLES, min_minutes=300,
                      pool_path=None, base_dir=None, exclude_left=True):
    """Alias histórico: mediocampistas de Chaco. Ver chaco_players_by_role."""
    return chaco_players_by_role(season, roles=roles, min_minutes=min_minutes,
                                 pool_path=pool_path, base_dir=base_dir,
                                 exclude_left=exclude_left)


# ─── Unidades del equipo (líneas) ───────────────────────────────────────────

def chaco_units(season="2026", base_dir=None, min_minutes=250, exclude_left=True):
    """Config de las líneas de Chaco para pasar a unit_report / combo_impact.

    `exclude_left=True` (default) NO cuenta a los de config.JUGADORES_FUERA:
    esto es la mejor combinación del equipo de HOY.

    Devuelve dict {nombre_linea: {players, size, require, roles_of}}:
      banda_der / banda_izq -> LAT + EXT del mismo lado (dupla obliga 1 de cada rol)
      zaga    -> defensores centrales (dupla)
      medio   -> volantes centrales MCD/MC (dupla)
      ataque  -> delanteros centro (dupla)
      ataque_trio -> DC + EXT, obliga al menos 1 delantero
    """
    kw = dict(season=season, base_dir=base_dir, min_minutes=min_minutes,
              exclude_left=exclude_left)
    lat_d = chaco_players_by_role(roles=("LAT",), banda="DER", **kw)
    ext_d = chaco_players_by_role(roles=("EXT_MP",), banda="DER", **kw)
    lat_i = chaco_players_by_role(roles=("LAT",), banda="IZQ", **kw)
    ext_i = chaco_players_by_role(roles=("EXT_MP",), banda="IZQ", **kw)
    zaga  = chaco_players_by_role(roles=DEF_ROLES, **kw)
    medio = chaco_players_by_role(roles=CENTRAL_MID_ROLES, **kw)
    dc    = chaco_players_by_role(roles=ATTACK_ROLES, **kw)
    ext_a = chaco_players_by_role(roles=("EXT_MP",), **kw)
    rmap = chaco_role_map(season, base_dir=base_dir)

    return {
        "banda_der":   {"players": sorted(set(lat_d) | set(ext_d)), "size": 2,
                        "require": FLANK_ROLES, "roles_of": rmap},
        "banda_izq":   {"players": sorted(set(lat_i) | set(ext_i)), "size": 2,
                        "require": FLANK_ROLES, "roles_of": rmap},
        "zaga":        {"players": zaga, "size": 2},
        "medio":       {"players": medio, "size": 2},
        "ataque":      {"players": dc, "size": 2},
        "ataque_trio": {"players": sorted(set(dc) | set(ext_a)), "size": 3,
                        "require": ATTACK_ROLES, "roles_of": rmap},
    }


def unit_report(match_keys, base_dir, season="2026", min_together=180,
                units=None, base_units=None):
    """Corre combo_impact para cada línea de chaco_units(). Devuelve
    {nombre_linea: DataFrame}. `units` filtra a un subconjunto de líneas."""
    cfg = base_units or chaco_units(season, base_dir=base_dir)
    if units:
        cfg = {k: v for k, v in cfg.items() if k in units}
    out = {}
    for name, u in cfg.items():
        mmt = min_together if u["size"] >= 2 else 1.0
        out[name] = combo_impact(
            match_keys, base_dir, u["players"], size=u["size"],
            min_minutes_together=mmt,
            roles_of=u.get("roles_of"), require_roles=u.get("require"))
    return out


# ─── Lectura de un partido ───────────────────────────────────────────────────

def _load_match(mdir, mk):
    """dict con los intervalos de Chaco en cancha, los tiros y los goles con
    minuto, y las rojas (para el filtro 11v11). None si falta el lineup."""
    lp = os.path.join(mdir, "lineups_clean.csv")
    if not os.path.exists(lp):
        return None
    lin = pd.read_csv(lp)
    side = "home" if is_home_match(mk) else "away"
    chaco_home = side == "home"
    team = lin[lin["team_side"] == side]

    intervals = {}
    match_end = 90.0
    for _, r in team.iterrows():
        mins = pd.to_numeric(r.get("minutes_played"), errors="coerce")
        if pd.isna(mins) or mins <= 0:
            continue
        sin = pd.to_numeric(r.get("substitute_in"), errors="coerce")
        start = float(sin) if pd.notna(sin) else 0.0
        end = start + float(mins)
        intervals[r["player_name"]] = (start, end)
        match_end = max(match_end, end)
    match_end = min(match_end, MATCH_MAX_MIN)

    shots = []
    sp = os.path.join(mdir, "shotmap_clean.csv")
    if os.path.exists(sp):
        sm = pd.read_csv(sp)
        for _, s in sm.iterrows():
            t = pd.to_numeric(s.get("time"), errors="coerce")
            if pd.isna(t):
                continue
            at = pd.to_numeric(s.get("addedTime"), errors="coerce")
            minute = float(t) + (float(at) if pd.notna(at) else 0.0)
            xg = pd.to_numeric(s.get("xg"), errors="coerce")
            is_chaco = bool(s.get("isHome")) == chaco_home
            shots.append((minute, is_chaco, float(xg) if pd.notna(xg) else 0.0))

    goals, reds = [], []
    ip = os.path.join(mdir, "incidents_clean.csv")
    if os.path.exists(ip):
        inc = pd.read_csv(ip)
        if "type" in inc.columns:
            for _, g in inc[inc["type"] == "goal"].iterrows():
                m = pd.to_numeric(g.get("minute"), errors="coerce")
                if pd.notna(m):
                    goals.append((float(m), bool(g.get("is_home", True)) == chaco_home))
            for _, c in inc[inc["type"].isin(["red", "yellowRed"])].iterrows():
                m = pd.to_numeric(c.get("minute"), errors="coerce")
                if pd.notna(m):
                    reds.append((float(m), bool(c.get("is_home", True)) == chaco_home))

    return {"mk": mk, "intervals": intervals, "match_end": match_end,
            "shots": shots, "goals": goals, "reds": reds, "chaco_home": chaco_home}


# ─── Ventanas y agregación ───────────────────────────────────────────────────

def _combo_window(combo, match):
    """(start, end) donde TODOS los del combo están en cancha, o None.
    Cada jugador tiene un solo intervalo, así que es la intersección directa."""
    iv = match["intervals"]
    if not all(p in iv for p in combo):
        return None
    s = max(iv[p][0] for p in combo)
    e = min(iv[p][1] for p in combo)
    return (s, e) if e - s > 1e-6 else None


def _complement(window, end):
    """Tramos de [0, end] fuera de `window` (o None -> todo el partido)."""
    if window is None:
        return [(0.0, end)]
    s, e = window
    out = []
    if s > 0:
        out.append((0.0, min(s, end)))
    if e < end:
        out.append((e, end))
    return out


def _even_strength_subwindows(s, e, reds):
    """Sub-tramos de (s, e) donde Chaco y el rival tienen los mismos hombres."""
    cuts = sorted({s, e} | {m for (m, _) in reds if s < m < e})
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        mid = 0.5 * (a + b)
        ch = sum(1 for (m, isc) in reds if m <= mid and isc)
        rv = sum(1 for (m, isc) in reds if m <= mid and not isc)
        if ch == rv:
            out.append((a, b))
    return out


def _sum_in_windows(events, windows):
    """events: [(minuto, es_chaco, valor)]. -> (suma_chaco, suma_rival)."""
    cs = rs = 0.0
    for minute, is_chaco, val in events:
        if any(a < minute <= b for a, b in windows):
            if is_chaco:
                cs += val
            else:
                rs += val
    return cs, rs


def _p90(x, minutes):
    return x / (minutes / 90.0) if minutes and minutes > 0 else np.nan


def _match_events(match):
    shots = match["shots"]
    goals = [(m, isc, 1.0) for (m, isc) in match["goals"]]
    return shots, goals


def combo_impact(match_keys, base_dir, players, size=2,
                 min_minutes_together=90.0, return_per_match=False,
                 roles_of=None, require_roles=None):
    """Impacto de cada combinación de `size` jugadores de `players`.

    Devuelve un DataFrame ordenado por xgdiff_p90_con (desc). Columnas:
      combo, jugadores, n, partidos_juntos, minutos_juntos
      xgf_p90_con / xga_p90_con / xgdiff_p90_con   -> equipo con el combo en cancha
      goldiff_p90_con
      minutos_sin / xgdiff_p90_sin                 -> el resto de los minutos del año
      xgdiff_p90_sin_mp                            -> "sin", pero SOLO en los partidos
                                                      donde el combo jugó (control de calendario)
      delta_xgdiff = xgdiff_p90_con - xgdiff_p90_sin_mp
      minutos_11v11 / xgdiff_p90_11v11             -> solo tramos con 11 vs 11

    size=1 devuelve el impacto individual (equipo con ese jugador en cancha).
    """
    matches = []
    for mk in match_keys:
        m = _load_match(os.path.join(base_dir, mk), mk)
        if m:
            matches.append(m)

    require_roles = tuple(require_roles) if require_roles else ()

    rows, per_match_rows = [], []
    for combo in combinations(sorted(set(players)), size):
        if require_roles:
            combo_roles = {(roles_of or {}).get(p) for p in combo}
            if not all(r in combo_roles for r in require_roles):
                continue
        agg = dict(on_min=0.0, off_min=0.0, es_min=0.0, mp_min=0.0, n=0,
                   on_xgf=0.0, on_xga=0.0, off_xgf=0.0, off_xga=0.0,
                   on_gf=0.0, on_ga=0.0, off_gf=0.0, off_ga=0.0,
                   es_xgf=0.0, es_xga=0.0, mp_xgf=0.0, mp_xga=0.0)
        for m in matches:
            shots, goals = _match_events(m)
            end = m["match_end"]
            win = _combo_window(combo, m)
            comp = _complement(win, end)

            if win is not None:
                s, e = win
                agg["on_min"] += e - s
                agg["n"] += 1
                xgf, xga = _sum_in_windows(shots, [win])
                gf, ga = _sum_in_windows(goals, [win])
                agg["on_xgf"] += xgf; agg["on_xga"] += xga
                agg["on_gf"] += gf; agg["on_ga"] += ga

                esw = _even_strength_subwindows(s, e, m["reds"])
                agg["es_min"] += sum(b - a for a, b in esw)
                exgf, exga = _sum_in_windows(shots, esw)
                agg["es_xgf"] += exgf; agg["es_xga"] += exga

                # "sin" pero SOLO en los partidos donde el combo apareció
                # (control que saca el sesgo de calendario: los que llegaron a
                # mitad de año jugarían solo en la buena racha).
                mxgf, mxga = _sum_in_windows(shots, comp)
                agg["mp_min"] += sum(b - a for a, b in comp)
                agg["mp_xgf"] += mxgf; agg["mp_xga"] += mxga

                if return_per_match:
                    per_match_rows.append({
                        "combo": " + ".join(combo), "mk": m["mk"],
                        "minutos": round(e - s, 1),
                        "xgf": round(xgf, 2), "xga": round(xga, 2),
                        "gf": int(gf), "ga": int(ga),
                        "local": m["chaco_home"],
                    })

            for a, b in comp:
                agg["off_min"] += b - a
            oxgf, oxga = _sum_in_windows(shots, comp)
            ogf, oga = _sum_in_windows(goals, comp)
            agg["off_xgf"] += oxgf; agg["off_xga"] += oxga
            agg["off_gf"] += ogf; agg["off_ga"] += oga

        if agg["on_min"] < min_minutes_together:
            continue
        rows.append({
            "combo": " + ".join(combo),
            "jugadores": combo,
            "n": size,
            "partidos_juntos": agg["n"],
            "minutos_juntos": round(agg["on_min"], 1),
            "xgf_p90_con": round(_p90(agg["on_xgf"], agg["on_min"]), 3),
            "xga_p90_con": round(_p90(agg["on_xga"], agg["on_min"]), 3),
            "xgdiff_p90_con": round(_p90(agg["on_xgf"] - agg["on_xga"], agg["on_min"]), 3),
            "goldiff_p90_con": round(_p90(agg["on_gf"] - agg["on_ga"], agg["on_min"]), 3),
            "minutos_sin": round(agg["off_min"], 1),
            "xgdiff_p90_sin": round(_p90(agg["off_xgf"] - agg["off_xga"], agg["off_min"]), 3),
            "xgdiff_p90_sin_mp": round(_p90(agg["mp_xgf"] - agg["mp_xga"], agg["mp_min"]), 3),
            "delta_xgdiff": round(
                _p90(agg["on_xgf"] - agg["on_xga"], agg["on_min"])
                - _p90(agg["mp_xgf"] - agg["mp_xga"], agg["mp_min"]), 3),
            "minutos_11v11": round(agg["es_min"], 1),
            "xgdiff_p90_11v11": round(_p90(agg["es_xgf"] - agg["es_xga"], agg["es_min"]), 3),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("xgdiff_p90_con", ascending=False).reset_index(drop=True)
    if return_per_match:
        return df, pd.DataFrame(per_match_rows)
    return df


def best_midfield(match_keys, base_dir, season="2026", include_wide=False,
                  sizes=(1, 2, 3), min_minutes=300, min_minutes_together=120.0,
                  exclude_left=True):
    """Corre combo_impact para solos / duplas / tríos y devuelve un dict.

    include_wide=True suma los volantes de banda (EXT_MP) al pool de candidatos.
    exclude_left=True (default) no cuenta a los de config.JUGADORES_FUERA.
    """
    roles = CENTRAL_MID_ROLES + (WIDE_MID_ROLES if include_wide else ())
    mids = chaco_midfielders(season=season, roles=roles, min_minutes=min_minutes,
                             base_dir=base_dir, exclude_left=exclude_left)
    out = {"jugadores": mids}
    for k in sizes:
        mmt = 1.0 if k == 1 else min_minutes_together
        out[k] = combo_impact(match_keys, base_dir, mids, size=k,
                              min_minutes_together=mmt)
    return out
