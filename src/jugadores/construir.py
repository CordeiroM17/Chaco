"""
construir.py
============
Arma la base de jugadores de Primera Nacional en data/jugadores/ a partir de
lo scrapeado en data/temporadas/{año}/ (la carpeta de Chaco y las de todos
los rivales). No scrapea nada: solo lee y ordena.

    data/jugadores/
      ├── partidos.csv              una fila por partido (event_id)
      ├── equipos.csv               una fila por (temporada, equipo)
      ├── jugadores.csv             una fila por persona (player_id)
      ├── jugador_partido/{año}.csv una fila por (partido, jugador), TODAS las
      │                             stats del lineups.json crudo
      ├── jugador_temporada.csv     una fila por (temporada, jugador, equipo)
      └── _ingesta.csv              qué carpeta se leyó de cada partido

Es incremental: un partido solo se vuelve a leer si cambió la carpeta elegida
o alguno de sus archivos (se compara la fecha de modificación). Las tablas
derivadas (partidos/equipos/jugadores/jugador_temporada) se rearman siempre,
porque salen de jugador_partido en segundos.

Tres reglas que todo lo demás asume:

1. Un partido = un event_id. Cada partido está guardado en la carpeta de LOS
   DOS equipos; se elige UNA copia (la que trae más datos) y la otra se ignora.
2. SofaScore no manda las stats que valen cero. En un partido CON análisis
   (algún jugador trae `totalPass`) la celda vacía es 0; en uno SIN análisis
   (solo goles y minutos) queda vacía. `nivel_datos` lo deja asentado por fila.
3. Las claves son player_id y team_id. El slug es solo una etiqueta.

`jugador_temporada` reutiliza la agregación de src/analysis/scouting.py tal
cual, para que el pool de cada temporada salga idéntico al de pool_liga().
"""

import os
import re
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

import config
from src.analysis import scouting as SC
from src.scraping.chaco_scraper import (PLAYER_STAT_FIELDS, parse_incidents,
                                        parse_lineups,
                                        _enrich_lineups_from_incidents)


DIR = os.path.join(config._ROOT, "data", "jugadores")
DIR_JP = os.path.join(DIR, "jugador_partido")
_TEMPORADAS_DIR = os.path.join(config._ROOT, "data", "temporadas")


def _archivo(nombre):
    return os.path.join(DIR, f"{nombre}.csv")


# ───────────────────────────── stats de SofaScore ────────────────────────────
# Las 66 stats que se vieron en 2026, en un orden legible. Si una temporada
# trae alguna que no está acá, se agrega igual al final de la tabla.
STATS_SOFASCORE = [
    # ataque
    "goals", "goalAssist", "expectedGoals", "expectedAssists", "totalShots",
    "onTargetScoringAttempt", "shotOffTarget", "blockedScoringAttempt",
    "hitWoodwork", "bigChanceCreated", "bigChanceMissed", "keyPass",
    "totalOffside",
    # pase
    "totalPass", "accuratePass", "totalLongBalls", "accurateLongBalls",
    "totalCross", "accurateCross", "totalOwnHalfPasses", "accurateOwnHalfPasses",
    "totalOppositionHalfPasses", "accurateOppositionHalfPasses",
    # conducción
    "touches", "totalContest", "wonContest", "unsuccessfulTouch",
    "possessionLostCtrl", "dispossessed",
    # duelos
    "duelWon", "duelLost", "aerialWon", "aerialLost", "challengeLost",
    "wasFouled", "fouls",
    # defensa
    "totalTackle", "wonTackle", "interceptionWon", "totalClearance",
    "clearanceOffLine", "outfielderBlock", "ballRecovery", "errorLeadToAShot",
    "ownGoals",
    # penales
    "penaltyWon", "penaltyConceded", "penaltyMiss",
    # arquero
    "saves", "savedShotsFromInsideTheBox", "goodHighClaim", "crossNotClaimed",
    "totalKeeperSweeper", "accurateKeeperSweeper", "penaltyFaced", "penaltySave",
    # físicas (solo en ~1.6% de los partidos)
    "kilometersCovered", "numberOfSprints", "topSpeed", "metersCoveredRunningKm",
    "metersCoveredHighSpeedRunningKm", "metersCoveredSprintingKm",
]

# ─────────────────────────── régimen de los datos ────────────────────────────
# SofaScore cambió la forma de medir la Primera Nacional desde el 1/7/2026 (la
# Liga Profesional NO cambió). Promedio por equipo y partido, 1er semestre 2026
# contra 2º: quites -55%, regates -35%, duelos perdidos -27%, despejes +77%,
# ocasiones claras +40%, xG +21%, pases/toques +10%, y `unsuccessfulTouch`
# deja de venir (0). 2025 y el 1er semestre 2026 son comparables entre sí
# (diferencias < 7%). Ninguna marca del JSON lo distingue (statisticalVersion
# vale 2 en los dos), así que el régimen se asigna por fecha.
#
# Cada corte es (desde_fecha, régimen). Si SofaScore vuelve a cambiar, se
# agrega otro corte acá y se vuelve a correr construir().
CORTES_REGIMEN = (("2026-07-01", "B"),)
REGIMEN_INICIAL = "A"


def regimen_de(fecha):
    """Régimen de datos de un partido según su fecha ('YYYY-MM-DD...')."""
    reg = REGIMEN_INICIAL
    f = str(fecha or "")[:10]
    for desde, nombre in CORTES_REGIMEN:
        if f >= desde:
            reg = nombre
    return reg


# Las físicas NO se completan con cero: que falten quiere decir que SofaScore
# no las midió en ese partido, no que el jugador no corrió.
STATS_FISICAS = ("kilometersCovered", "numberOfSprints", "topSpeed",
                 "metersCoveredRunningKm", "metersCoveredHighSpeedRunningKm",
                 "metersCoveredSprintingKm")

# Claves del bloque `statistics` que no son una stat del jugador o que en esta
# categoría no sirven: `goalsPrevented` viene vacío en el 100% de los partidos
# (el PSxG del arquero sale del shotmap, ver psxg_enfrentado).
_CLAVES_IGNORADAS = {"statisticsType", "ratingVersions", "minutesPlayed",
                     "rating", "goalsPrevented"}

_SITUACIONES_PELOTA_PARADA = {"corner", "free-kick", "set-piece",
                              "throw-in-set-piece"}


# ──────────────────────────────── utilidades ─────────────────────────────────
def _leer_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _leer_csv(path, **kw):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path, **kw)
    except Exception:
        return pd.DataFrame()


def _evento(carpeta):
    ev = _leer_json(os.path.join(carpeta, "raw", "event.json"))
    if not ev:
        return None
    return ev.get("event", ev)


def _rel(path):
    return os.path.relpath(path, config._ROOT).replace("\\", "/")


def _temporadas_disponibles():
    if not os.path.isdir(_TEMPORADAS_DIR):
        return []
    return sorted(d for d in os.listdir(_TEMPORADAS_DIR)
                  if d.isdigit() and os.path.isdir(os.path.join(_TEMPORADAS_DIR, d)))


# Archivos cuya fecha de modificación entra en la firma del partido: si se
# re-scrapea cualquiera de ellos, el partido se vuelve a leer.
_ARCHIVOS_FIRMA = ("raw/event.json", "raw/lineups.json", "lineups_clean.csv",
                   "incidents_clean.csv", "shotmap_clean.csv",
                   "average_positions_clean.csv", "statistics_clean.csv",
                   "event_clean.csv")


def _firma(carpeta):
    tiempos = []
    for a in _ARCHIVOS_FIRMA:
        p = os.path.join(carpeta, a)
        tiempos.append(f"{os.path.getmtime(p):.0f}" if os.path.exists(p) else "-")
    return "|".join(tiempos)


# ─────────────────────── elegir una copia por partido ────────────────────────
def _copias_por_evento(temporada):
    """{event_id: [carpetas]} de los partidos TERMINADOS de Primera Nacional
    que hay en disco para la temporada (Chaco + todos los rivales)."""
    base = os.path.join(_TEMPORADAS_DIR, str(temporada))
    raices = [os.path.join(base, "partidos")]
    rb = os.path.join(base, "rivals")
    if os.path.isdir(rb):
        raices += [os.path.join(rb, d) for d in sorted(os.listdir(rb))
                   if os.path.isdir(os.path.join(rb, d))]

    copias = {}
    for raiz in raices:
        if not os.path.isdir(raiz):
            continue
        for mk in sorted(os.listdir(raiz)):
            carpeta = os.path.join(raiz, mk)
            if not os.path.isdir(carpeta):
                continue
            ev = _evento(carpeta)
            if not ev or ev.get("id") is None:
                continue
            torneo = ((ev.get("tournament") or {}).get("uniqueTournament") or {}).get("id")
            if torneo != config.UNIQUE_TOURNAMENT_ID:
                continue
            if (ev.get("status") or {}).get("type") != "finished":
                continue
            copias.setdefault(int(ev["id"]), []).append(carpeta)
    return copias


def _puntaje_copia(carpeta):
    """Cuánto trae una copia: (jugadores con stats completas, jugadores con
    minutos, CSV limpios presentes, fecha del lineups.json). Gana la más alta.

    El desempate por fecha no es arbitrario: SofaScore corrige minutos y stats
    días después del partido, y la copia más vieja puede quedar desfasada (ej.
    Temperley-Atlanta F23: la copia de Temperley sumaba 1022' por equipo, la
    de Atlanta, scrapeada después, los 990' que corresponden)."""
    path = os.path.join(carpeta, "raw", "lineups.json")
    lin = _leer_json(path) or {}
    completos = con_minutos = 0
    for side in ("home", "away"):
        for e in (lin.get(side) or {}).get("players", []) or []:
            st = e.get("statistics") or {}
            completos += "totalPass" in st
            con_minutos += bool(st.get("minutesPlayed"))
    limpios = sum(os.path.exists(os.path.join(carpeta, a))
                  for a in _ARCHIVOS_FIRMA if a.endswith(".csv"))
    fecha = os.path.getmtime(path) if os.path.exists(path) else 0
    return (completos, con_minutos, limpios, fecha)


def _elegir_copias(temporada):
    return {eid: max(cs, key=_puntaje_copia)
            for eid, cs in _copias_por_evento(temporada).items()}


# ───────────────────────────── leer un partido ───────────────────────────────
def _zona_del_torneo(nombre):
    """'Primera Nacional, Group B' → 'B'. None si el nombre no trae la zona
    (en 2026 SofaScore lo llama 'Primera B Nacional' a secas)."""
    m = re.search(r"(?:Group|Grupo|Zona)\s+([A-Z])\b", str(nombre or ""))
    return m.group(1) if m else None


def _manager(equipo):
    m = (equipo or {}).get("manager") or {}
    return m.get("id"), m.get("name")


def _fila_partido(eid, carpeta, temporada, ev, lin):
    home, away = ev.get("homeTeam") or {}, ev.get("awayTeam") or {}
    hs, as_ = ev.get("homeScore") or {}, ev.get("awayScore") or {}
    ts = ev.get("startTimestamp")
    torneo = ev.get("tournament") or {}
    ec = _leer_csv(os.path.join(carpeta, "event_clean.csv"))
    ec = ec.iloc[0] if not ec.empty else pd.Series(dtype=object)
    pos_h, pos_a = SC._posesion_del_partido(carpeta)
    sm = _leer_csv(os.path.join(carpeta, "shotmap_clean.csv"))
    ap = _leer_csv(os.path.join(carpeta, "average_positions_clean.csv"))
    dt_h, dt_h_nombre = _manager(home)
    dt_a, dt_a_nombre = _manager(away)
    detalle = any("totalPass" in (e.get("statistics") or {})
                  for side in ("home", "away")
                  for e in ((lin or {}).get(side) or {}).get("players", []) or [])
    return {
        "event_id": eid,
        "temporada": str(temporada),
        "season_id": (ev.get("season") or {}).get("id"),
        "torneo_id": (torneo.get("uniqueTournament") or {}).get("id"),
        "torneo_nombre": torneo.get("name"),
        "fecha_utc": (datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
                      if ts else None),
        "ronda": (ev.get("roundInfo") or {}).get("round"),
        "zona_torneo": _zona_del_torneo(torneo.get("name")),
        "home_team_id": home.get("id"),
        "away_team_id": away.get("id"),
        "home_slug": config.slug_de(home.get("id"), home.get("name")),
        "away_slug": config.slug_de(away.get("id"), away.get("name")),
        "home_nombre": home.get("name"),
        "away_nombre": away.get("name"),
        "home_goles": hs.get("current"),
        "away_goles": as_.get("current"),
        "home_goles_ht": hs.get("period1"),
        "away_goles_ht": as_.get("period1"),
        "estado": (ev.get("status") or {}).get("type"),
        "arbitro": ec.get("referee"),
        "estadio": ec.get("venue"),
        "publico": ec.get("attendance"),
        "dt_home_id": dt_h, "dt_home": dt_h_nombre,
        "dt_away_id": dt_a, "dt_away": dt_a_nombre,
        "posesion_home": pos_h,
        "posesion_away": pos_a,
        "tiene_lineups": bool(lin),
        "tiene_stats_detalle": detalle,
        "tiene_stats_jugador": bool(ev.get("hasEventPlayerStatistics")),
        "tiene_xg": bool(ev.get("hasXg")),
        "tiene_shotmap": os.path.exists(os.path.join(carpeta, "shotmap_clean.csv")),
        "tiros_shotmap": len(sm),
        "tiene_posiciones": not ap.empty,
        "tiene_heatmap": bool(ev.get("hasEventPlayerHeatMap")),
        "carpeta": _rel(carpeta),
    }


# Correcciones de identidad que la base aplica y scouting.py no. Solo se
# apagan en comparar_con_pool(), para comparar código contra código.
_CORRECCIONES = {"alias": True, "shotmap": True}


def _norm_nombre(s):
    return config.slugify_equipo(s) if isinstance(s, str) and s.strip() else None


def _reasignar_shotmap(sm, lin):
    """
    El shotmap a veces anota el remate con OTRO player_id que el lineup del
    mismo partido (perfil duplicado de SofaScore: 925 de 25.807 remates en
    2025-26, ej. M. González de Los Andes, 1087036 en el shotmap y 1183703 en
    el lineup). Sin esto, esos remates no se le cargan a nadie.

    Cada remate con un id que no está en el lineup se reasigna al jugador del
    MISMO equipo con el mismo nombre corto (o, si no, el mismo apellido),
    siempre que haya uno solo. Devuelve (shotmap corregido, pares
    [(id_shotmap, id_lineup, nombre)]).
    """
    if sm.empty or "player_id" not in sm.columns or not lin:
        return sm, []
    por_lado = {}
    for side in ("home", "away"):
        nombres, apellidos = {}, {}
        for e in (lin.get(side) or {}).get("players", []) or []:
            p = e.get("player") or {}
            if p.get("id") is None:
                continue
            corto = _norm_nombre(p.get("shortName") or p.get("name"))
            nombres.setdefault(corto, set()).add(int(p["id"]))
            ape = corto.split("_")[-1] if corto else None
            apellidos.setdefault(ape, set()).add(int(p["id"]))
        por_lado[side] = (nombres, apellidos)
    en_lineup = {i for n, _ in por_lado.values() for ids in n.values() for i in ids}

    sm = sm.copy()
    sm["player_id"] = pd.to_numeric(sm["player_id"], errors="coerce")
    pares = {}
    for i, r in sm.iterrows():
        pid = r["player_id"]
        if pd.isna(pid) or int(pid) in en_lineup or r.get("situation") == "own-goal":
            continue
        side = "home" if str(r.get("isHome")).lower() == "true" else "away"
        nombres, apellidos = por_lado.get(side, ({}, {}))
        corto = _norm_nombre(r.get("player_name"))
        cand = nombres.get(corto) or apellidos.get(corto.split("_")[-1] if corto else None)
        if cand and len(cand) == 1:
            nuevo = next(iter(cand))
            sm.at[i, "player_id"] = nuevo
            pares[(int(pid), nuevo)] = r.get("player_name")
    return sm, [(a, b, n) for (a, b), n in pares.items()]


def _shotmap_por_jugador(sm):
    """{player_id: {sm_*}} desde shotmap_clean.csv. Los goles en contra se
    descartan: el player_id es el del rival que la metió en su arco."""
    if sm.empty or "player_id" not in sm.columns:
        return {}
    sm = sm[sm["situation"].astype(str) != "own-goal"].copy()
    sm["player_id"] = pd.to_numeric(sm["player_id"], errors="coerce")
    sm = sm[sm["player_id"].notna()]
    sm["xg"] = pd.to_numeric(sm["xg"], errors="coerce").fillna(0)
    sm["xgot"] = pd.to_numeric(sm["xgot"], errors="coerce").fillna(0)
    pen = sm["situation"].astype(str) == "penalty"
    gol = sm["shotType"].astype(str) == "goal"
    out = {}
    for pid, g in sm.groupby("player_id"):
        p = pen.loc[g.index]
        out[int(pid)] = {
            "sm_tiros": len(g),
            "sm_xg": g["xg"].sum(),
            "sm_npxg": g.loc[~p, "xg"].sum(),
            "sm_xgot": g["xgot"].sum(),
            "sm_tiros_penal": int(p.sum()),
            "sm_goles_penal": int((p & gol.loc[g.index]).sum()),
            "sm_tiros_cabeza": int((g["bodyPart"].astype(str) == "head").sum()),
            "sm_tiros_pelota_parada": int(
                g["situation"].astype(str).isin(_SITUACIONES_PELOTA_PARADA).sum()),
        }
    return out


def _filas_jugadores(eid, carpeta, temporada, ev, lin, partido):
    """Una fila por jugador del lineups.json (los dos equipos), incluidos los
    suplentes que no entraron (minutos = 0)."""
    ids = {"home": partido["home_team_id"], "away": partido["away_team_id"]}
    goles = {"home": partido["home_goles"], "away": partido["away_goles"]}
    posesion = {"home": partido["posesion_home"], "away": partido["posesion_away"]}
    fecha = (partido["fecha_utc"] or "")[:10] or None

    # Incidencias: del CSV limpio, o del JSON crudo si la carpeta quedó solo
    # con raw/ (scrapeo cortado antes de generar los CSV).
    inc = _leer_csv(os.path.join(carpeta, "incidents_clean.csv"))
    if inc.empty:
        inc_raw = _leer_json(os.path.join(carpeta, "raw", "incidents.json"))
        inc = parse_incidents(inc_raw) if inc_raw else None
        inc = inc if inc is not None else pd.DataFrame()

    # Cambios y tarjetas: lineups_clean.csv ya los trae cruzados con incidents;
    # si no existe, se cruzan acá con la misma función del scraper.
    lc = _leer_csv(os.path.join(carpeta, "lineups_clean.csv"))
    if lc.empty and lin:
        lc = parse_lineups(lin)
        if lc is not None and not inc.empty:
            lc = _enrich_lineups_from_incidents(lc, inc)
        lc = lc if lc is not None else pd.DataFrame()
    clean = {}
    if not lc.empty and "player_id" in lc.columns:
        lc["player_id"] = pd.to_numeric(lc["player_id"], errors="coerce")
        for _, r in lc[lc["player_id"].notna()].iterrows():
            clean[int(r["player_id"])] = r

    # Doble amarilla: el clean la suma a red_cards; acá se separa.
    doble = (inc[inc["type"].astype(str) == "yellowRed"]["player"].value_counts().to_dict()
             if not inc.empty and "type" in inc.columns else {})

    ap = _leer_csv(os.path.join(carpeta, "average_positions_clean.csv"))
    medias = {}
    if not ap.empty:
        for _, r in ap.iterrows():
            pid = pd.to_numeric(r.get("player_id"), errors="coerce")
            if pd.notna(pid):
                medias[(int(pid), r.get("team_side"))] = (
                    r.get("average_x"), r.get("average_y"), r.get("points_count"))

    sm_path = os.path.join(carpeta, "shotmap_clean.csv")
    hay_shotmap = os.path.exists(sm_path)
    sm = _leer_csv(sm_path)
    sm, pares = _reasignar_shotmap(sm, lin) if _CORRECCIONES["shotmap"] else (sm, [])
    # Queda registrado en partidos.csv: es evidencia de perfiles duplicados
    # (mismo partido, mismo equipo, mismo nombre, dos ids).
    partido["ids_shotmap_reasignados"] = ";".join(f"{a}>{b}" for a, b, _ in pares) or None
    tiros = _shotmap_por_jugador(sm)

    # PSxG que enfrentó cada arco: tiros AL ARCO del rival (save/goal). Mismo
    # criterio que scouting._gk_psxg_metrics.
    psxg_contra = {"home": np.nan, "away": np.nan}
    if hay_shotmap:
        psxg_contra = {"home": 0.0, "away": 0.0}
        if not sm.empty and "shotType" in sm.columns:
            al_arco = sm[sm["shotType"].isin(("save", "goal"))]
            xgot = pd.to_numeric(al_arco["xgot"], errors="coerce")
            es_local = al_arco["isHome"].astype(str).str.lower() == "true"
            psxg_contra = {"home": float(xgot[~es_local].sum()),
                           "away": float(xgot[es_local].sum())}

    filas = []
    for side in ("home", "away"):
        rival = "away" if side == "home" else "home"
        for e in ((lin or {}).get(side) or {}).get("players", []) or []:
            p = e.get("player") or {}
            pid = p.get("id")
            if pid is None:
                continue
            pid_sofascore = int(pid)
            pid = getattr(config, "ALIAS_JUGADORES", {}).get(pid_sofascore, pid_sofascore)
            st = e.get("statistics") or {}
            minutos = float(st.get("minutesPlayed") or 0)
            if minutos <= 0:
                nivel = "sin_minutos"
            else:
                nivel = "completo" if partido["tiene_stats_detalle"] else "basico"
            gf, gc = goles[side], goles[rival]
            resultado = (None if gf is None or gc is None
                         else "G" if gf > gc else "E" if gf == gc else "P")
            c = clean.get(pid_sofascore)
            x, y, puntos = medias.get((pid_sofascore, side), (np.nan, np.nan, np.nan))
            valor = (p.get("proposedMarketValueRaw") or {}).get("value")
            fila = {
                "event_id": eid,
                "temporada": str(temporada),
                "fecha": fecha,
                "ronda": partido["ronda"],
                "player_id": pid,
                "player_id_sofascore": pid_sofascore,
                "team_id": ids[side],
                "rival_id": ids[rival],
                "local": side == "home",
                "nombre_corto": p.get("shortName") or p.get("name"),
                "dorsal": e.get("shirtNumber") or e.get("jerseyNumber"),
                "posicion": e.get("position") or p.get("position"),
                "titular": not e.get("substitute", True),
                "capitan": bool(e.get("captain", False)),
                "minutos": minutos,
                "entro_min": c.get("substitute_in") if c is not None else np.nan,
                "salio_min": c.get("substitute_out") if c is not None else np.nan,
                "goles_equipo": gf,
                "goles_rival": gc,
                "resultado": resultado,
                "posesion_equipo": posesion[side],
                "nivel_datos": nivel,
                "avg_x": x, "avg_y": y, "puntos_posicion": puntos,
                "rating": pd.to_numeric(st.get("rating"), errors="coerce"),
            }
            for k, v in st.items():
                if k in _CLAVES_IGNORADAS or isinstance(v, (dict, list)):
                    continue
                fila[k] = pd.to_numeric(v, errors="coerce")
            for k, v in tiros.get(pid_sofascore, {}).items():
                fila[k] = v
            if hay_shotmap and pid_sofascore not in tiros and minutos > 0:
                for k in ("sm_tiros", "sm_xg", "sm_npxg", "sm_xgot", "sm_tiros_penal",
                          "sm_goles_penal", "sm_tiros_cabeza", "sm_tiros_pelota_parada"):
                    fila[k] = 0
            fila["amarillas"] = c.get("yellow_cards") if c is not None else np.nan
            fila["rojas"] = c.get("red_cards") if c is not None else np.nan
            nombre_clean = c.get("player_name") if c is not None else fila["nombre_corto"]
            fila["doble_amarilla"] = doble.get(nombre_clean, 0)
            fila["_side"] = side
            fila["_psxg_contra"] = psxg_contra[side]

            # Bio tal como estaba cuando se scrapeó el partido (puede cambiar
            # entre partidos: valor de mercado, a veces la altura).
            bio = {"nombre_completo": p.get("name"),
                   "slug_sofascore": p.get("slug"),
                   "altura": p.get("height"),
                   "pais": (p.get("country") or {}).get("name"),
                   "nacimiento_ts": p.get("dateOfBirthTimestamp"),
                   "valor_mercado_eur": valor}
            # Por el id original o el unificado: la de Pacheco está cargada con
            # 83700, que ahora es un alias de 2468554.
            corr = (config.CORRECCIONES_BIO_JUGADORES.get(pid_sofascore)
                    or config.CORRECCIONES_BIO_JUGADORES.get(pid, {}))
            for k_corr, k_bio in (("nombre_completo", "nombre_completo"),
                                  ("altura", "altura"),
                                  ("nacimiento", "nacimiento_ts")):
                if k_corr in corr:
                    bio[k_bio] = corr[k_corr]
            fila.update(bio)
            filas.append(fila)

    if not filas:
        return pd.DataFrame()
    df = pd.DataFrame(filas)

    # Arquero del partido: el de más minutos en la 'G' de cada equipo (mismo
    # criterio que scouting). Solo a él se le cargan PSxG y goles recibidos.
    df["psxg_enfrentado"] = np.nan
    df["goles_recibidos"] = np.nan
    arqueros = df[(df["posicion"] == "G") & (df["minutos"] > 0)]
    for side, g in arqueros.groupby("_side"):
        i = g["minutos"].idxmax()
        df.loc[i, "psxg_enfrentado"] = g.loc[i, "_psxg_contra"]
        df.loc[i, "goles_recibidos"] = g.loc[i, "goles_rival"]
    return df.drop(columns=["_side", "_psxg_contra"])


def leer_partido(eid, carpeta, temporada):
    """(fila de partidos.csv, DataFrame de jugador_partido) de una carpeta."""
    ev = _evento(carpeta)
    lin = _leer_json(os.path.join(carpeta, "raw", "lineups.json"))
    partido = _fila_partido(eid, carpeta, temporada, ev, lin)
    jugadores = _filas_jugadores(eid, carpeta, temporada, ev, lin, partido) if lin else pd.DataFrame()
    return partido, jugadores


# ───────────────────────── orden y ceros de la tabla ─────────────────────────
_COLS_ID = ["event_id", "temporada", "fecha", "ronda", "player_id",
            "player_id_sofascore", "team_id",
            "rival_id", "local", "nombre_corto", "dorsal", "posicion", "titular",
            "capitan", "minutos", "entro_min", "salio_min", "goles_equipo",
            "goles_rival", "resultado", "posesion_equipo", "nivel_datos",
            "regimen", "avg_x", "avg_y", "puntos_posicion", "rating"]
_COLS_SHOTMAP = ["sm_tiros", "sm_xg", "sm_npxg", "sm_xgot", "sm_tiros_penal",
                 "sm_goles_penal", "sm_tiros_cabeza", "sm_tiros_pelota_parada"]
_COLS_FIN = ["amarillas", "rojas", "doble_amarilla", "psxg_enfrentado",
             "goles_recibidos", "nombre_completo", "slug_sofascore", "altura",
             "pais", "nacimiento_ts", "valor_mercado_eur"]


def _ordenar_jp(jp):
    """Columnas en orden fijo, stats nuevas al final de las de SofaScore, y
    los ceros que SofaScore omite completados donde corresponde."""
    # El alias se aplica en cada corrida sobre el id original, así un alias
    # nuevo en config.ALIAS_JUGADORES entra sin tener que re-leer partidos.
    jp = jp.copy()
    alias = getattr(config, "ALIAS_JUGADORES", {}) if _CORRECCIONES["alias"] else {}
    if "player_id_sofascore" not in jp.columns:
        jp["player_id_sofascore"] = jp["player_id"]
    jp["player_id_sofascore"] = jp["player_id_sofascore"].astype(int)
    jp["player_id"] = jp["player_id_sofascore"].map(lambda x: alias.get(x, x))
    # El régimen se recalcula siempre desde la fecha (si cambia un corte, no
    # hace falta re-leer los partidos).
    jp["regimen"] = jp["fecha"].map(regimen_de)

    conocidas = set(_COLS_ID) | set(_COLS_SHOTMAP) | set(_COLS_FIN)
    extra = sorted(c for c in jp.columns if c not in conocidas and c not in STATS_SOFASCORE)
    stats = [c for c in STATS_SOFASCORE] + extra
    faltan = [c for c in stats + _COLS_SHOTMAP + _COLS_FIN if c not in jp.columns]
    if faltan:
        jp = pd.concat([jp, pd.DataFrame(np.nan, index=jp.index, columns=faltan)], axis=1)

    # Regla 2: en un partido con análisis, la stat que falta vale 0.
    completo = jp["nivel_datos"] == "completo"
    a_cero = [c for c in stats if c not in STATS_FISICAS]
    jp.loc[completo, a_cero] = jp.loc[completo, a_cero].fillna(0)
    # Goles, asistencias y tiros llegan aun sin análisis: ahí también valen 0.
    con_min = jp["minutos"] > 0
    basicas = ["goals", "goalAssist", "ownGoals", "totalShots"]
    jp.loc[con_min, basicas] = jp.loc[con_min, basicas].fillna(0)
    for c in ("amarillas", "rojas"):
        jp[c] = jp[c].fillna(0)

    jp = jp[_COLS_ID + stats + _COLS_SHOTMAP + _COLS_FIN]
    return jp.sort_values(["fecha", "event_id", "team_id", "titular", "minutos"],
                          ascending=[True, True, True, False, False]).reset_index(drop=True)


# ──────────────────────────────── ingesta ────────────────────────────────────
def _ingestar_temporada(temporada, ingesta, partidos_previos, forzar, verbose):
    """Lee los partidos nuevos o cambiados de una temporada. Devuelve
    (jugador_partido de la temporada, filas de partidos, filas de ingesta)."""
    elegidas = _elegir_copias(temporada)
    jp_path = os.path.join(DIR_JP, f"{temporada}.csv")
    jp_viejo = _leer_csv(jp_path)

    previo = {}
    if not ingesta.empty:
        ing = ingesta[ingesta["temporada"].astype(str) == str(temporada)]
        previo = {int(r.event_id): (r.carpeta, r.firma) for r in ing.itertuples()}

    reusar, leer = set(), []
    for eid, carpeta in elegidas.items():
        firma = _firma(carpeta)
        if not forzar and previo.get(eid) == (_rel(carpeta), firma):
            reusar.add(eid)
        else:
            leer.append((eid, carpeta, firma))

    if verbose:
        print(f"[{temporada}] {len(elegidas)} partidos: {len(reusar)} sin cambios, "
              f"{len(leer)} a leer")

    filas_p, frames, filas_ing = [], [], []
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for eid, carpeta, firma in leer:
        partido, jug = leer_partido(eid, carpeta, temporada)
        filas_p.append(partido)
        if not jug.empty:
            frames.append(jug)
        filas_ing.append({"event_id": eid, "temporada": str(temporada),
                          "carpeta": _rel(carpeta), "firma": firma,
                          "procesado_en": ahora, "jugadores": len(jug)})

    if not jp_viejo.empty and reusar:
        frames.insert(0, jp_viejo[jp_viejo["event_id"].isin(reusar)])
    jp = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not jp.empty:
        jp = _ordenar_jp(jp)

    p_viejos = (partidos_previos[partidos_previos["event_id"].isin(reusar)]
                if not partidos_previos.empty else pd.DataFrame())
    partidos = pd.concat([p_viejos, pd.DataFrame(filas_p)], ignore_index=True)

    ing_viejos = (ingesta[ingesta["event_id"].isin(reusar)
                          & (ingesta["temporada"].astype(str) == str(temporada))]
                  if not ingesta.empty else pd.DataFrame())
    ing = pd.concat([ing_viejos, pd.DataFrame(filas_ing)], ignore_index=True)
    return jp, partidos, ing


# ────────────────────────────── zonas y equipos ──────────────────────────────
def _tablas_de_posiciones(temporada):
    """Tablas de posiciones de la temporada con su zona. standings.csv es
    standings[0] del endpoint (Zona A) y standings_zona_b.csv la B."""
    filas = []
    for path, zona in ((config.standings_file(temporada), "A"),
                       (config.standings_zona_b_file(temporada), "B")):
        t = _leer_csv(path)
        if not t.empty:
            t["zona"] = zona
            filas.append(t)
    return pd.concat(filas, ignore_index=True) if filas else pd.DataFrame()


def _zonas_equipo(partidos_t, temporada):
    """{team_id: zona}. Primero del nombre del torneo ('..., Group B'), que es
    lo más confiable; si la temporada no lo trae (2026), de las tablas."""
    zonas = {}
    if not partidos_t.empty and partidos_t["zona_torneo"].notna().any():
        z = partidos_t[partidos_t["zona_torneo"].notna()]
        largo = pd.concat([
            z[["home_team_id", "zona_torneo"]].rename(columns={"home_team_id": "team_id"}),
            z[["away_team_id", "zona_torneo"]].rename(columns={"away_team_id": "team_id"}),
        ])
        zonas = largo.groupby("team_id")["zona_torneo"].agg(SC._moda).to_dict()
    tablas = _tablas_de_posiciones(temporada)
    if not tablas.empty:
        for tid, zona in zip(tablas["team_id"], tablas["zona"]):
            zonas.setdefault(int(tid), zona)
    return {int(k): v for k, v in zonas.items()}


def _equipos(partidos):
    filas = []
    for temporada, pt in partidos.groupby("temporada"):
        zonas = _zonas_equipo(pt, temporada)
        tablas = _tablas_de_posiciones(temporada)
        pos = ({int(r.team_id): (r.position, r.points) for r in tablas.itertuples()}
               if not tablas.empty else {})
        largo = pd.concat([
            pt[["home_team_id", "home_nombre"]].set_axis(["team_id", "nombre"], axis=1),
            pt[["away_team_id", "away_nombre"]].set_axis(["team_id", "nombre"], axis=1),
        ])
        for tid, g in largo.groupby("team_id"):
            tid = int(tid)
            # El nombre de config si el equipo está registrado (es el que usa
            # todo el pipeline: 'Gimnasia Jujuy', no 'Gimnasia y Esgrima de
            # Jujuy'); si no, el más frecuente de SofaScore.
            nombre = (config.EQUIPOS.get(tid) or {}).get("name") or SC._moda(g["nombre"])
            p, pts = pos.get(tid, (np.nan, np.nan))
            filas.append({"team_id": tid, "slug": config.slug_de(tid, nombre),
                          "nombre": nombre, "temporada": str(temporada),
                          "zona": zonas.get(tid), "partidos": len(g),
                          "pos_final": p, "pts_final": pts})
    return pd.DataFrame(filas).sort_values(["temporada", "zona", "pos_final", "slug"])


# ──────────────────────────────── jugadores ──────────────────────────────────
def _jugadores(jp_todo, equipos, previos):
    jp = jp_todo.sort_values(["fecha", "event_id"])
    slug_eq = {(str(r.temporada), int(r.team_id)): r.slug for r in equipos.itertuples()}
    jugaron = jp[jp["minutos"] > 0]

    def _ultimo(serie):
        s = serie.dropna()
        return s.iloc[-1] if not s.empty else None

    agg = jp.groupby("player_id").agg(
        nombre_corto=("nombre_corto", SC._moda),
        nombre_completo=("nombre_completo", SC._moda),
        slug_sofascore=("slug_sofascore", SC._moda),
        nacimiento_ts=("nacimiento_ts", SC._moda),
        altura_cm=("altura", SC._moda),
        pais=("pais", SC._moda),
        primera_temporada=("temporada", "min"),
        ultima_temporada=("temporada", "max"),
        convocatorias=("event_id", "nunique"),
    )
    agg["posicion_habitual"] = jugaron.groupby("player_id")["posicion"].agg(SC._moda)
    agg["partidos_total"] = jugaron.groupby("player_id")["event_id"].nunique()
    agg["minutos_total"] = jugaron.groupby("player_id")["minutos"].sum()

    con_valor = jp[jp["valor_mercado_eur"].notna()]
    agg["valor_mercado_eur"] = con_valor.groupby("player_id")["valor_mercado_eur"].agg(_ultimo)
    agg["valor_mercado_fecha"] = con_valor.groupby("player_id")["fecha"].agg(_ultimo)

    # Equipos en orden cronológico, por slug canónico.
    def _equipos_de(g):
        vistos = []
        for t, tid in zip(g["temporada"].astype(str), g["team_id"]):
            s = slug_eq.get((t, int(tid)), config.slug_de(tid))
            if s not in vistos:
                vistos.append(s)
        return ";".join(vistos)
    agg["equipos"] = jp.groupby("player_id")[["temporada", "team_id"]].apply(_equipos_de)

    agg = agg.reset_index()
    agg["nacimiento"] = pd.to_datetime(agg["nacimiento_ts"], unit="s", errors="coerce").dt.date
    agg["bio_corregida"] = agg["player_id"].isin(config.CORRECCIONES_BIO_JUGADORES)
    agg[["partidos_total", "minutos_total"]] = agg[["partidos_total", "minutos_total"]].fillna(0)

    # El link de Transfermarkt se carga a mano: se conserva entre corridas.
    agg["transfermarkt_url"] = None
    if not previos.empty and "transfermarkt_url" in previos.columns:
        tm = previos.set_index("player_id")["transfermarkt_url"].dropna()
        agg["transfermarkt_url"] = agg["player_id"].map(tm)

    cols = ["player_id", "nombre_corto", "nombre_completo", "slug_sofascore",
            "nacimiento", "nacimiento_ts", "altura_cm", "pais", "bio_corregida",
            "posicion_habitual", "valor_mercado_eur", "valor_mercado_fecha",
            "primera_temporada", "ultima_temporada", "equipos", "convocatorias",
            "partidos_total", "minutos_total", "transfermarkt_url"]
    return agg[cols].sort_values("player_id")


# ─────────────────────────── jugador_temporada ───────────────────────────────
# Columnas del shotmap de jugador_partido → nombre que usa scouting.py.
_SHOTMAP_A_POOL = {
    "sm_tiros":               "remates_shotmap",
    "sm_npxg":                "npxg",
    "sm_xgot":                "xgot",
    "sm_goles_penal":         "goles_penal",
    "sm_tiros_penal":         "remates_penal",
    "sm_tiros_cabeza":        "remates_cabeza",
    "sm_tiros_pelota_parada": "remates_pelota_parada",
}


def _mapeo_a_pool():
    """Nombre crudo de SofaScore → nombre del pool. Se lee de scouting.py en
    cada corrida (no se copia), porque el pool sigue sumando métricas: así lo
    que agregue allá entra acá solo."""
    m = {k: v for k, v in PLAYER_STAT_FIELDS.items()
         if v not in ("rating", "minutes_played", "goals_prevented")}
    m.update(SC._RAW_STATS)
    m.update(getattr(SC, "_TRACKING_STATS", {}))
    m.update({k: v for k, v in _SHOTMAP_A_POOL.items()
              if v in getattr(SC, "_SHOTMAP_STATS", [])})
    return m


# Stats que el pool NO calcula. Se suman y se pasan a p90 sobre los minutos en
# los que la stat existe. Si scouting.py empieza a calcular alguna con el
# mismo nombre, se deja la suya y esta se saltea.
EXTRA_TEMPORADA = {
    "ownGoals":                        "goles_en_contra",
    "penaltyFaced":                    "penales_enfrentados",
    "penaltySave":                     "penales_atajados",
    "totalShots":                      "tiros_total_sofascore",
    "doble_amarilla":                  "doble_amarilla",
    "metersCoveredHighSpeedRunningKm": "km_alta_intensidad",
    "metersCoveredSprintingKm":        "km_sprint",
}
# Cortes de visualization/players._sample_tier.
_CORTES_MUESTRA = ((900, "amplia"), (450, "media"), (180, "chica"))


def _muestra(minutos):
    for corte, etiqueta in _CORTES_MUESTRA:
        if minutos >= corte:
            return etiqueta
    return "muy_chica"


def _a_formato_scouting(jp, nombres_equipo):
    """jugador_partido → las filas jugador-partido que espera scouting.py
    (las mismas que arma scouting._leer_partido)."""
    todo = jp[jp["minutos"] > 0].copy()
    todo = todo.rename(columns=_mapeo_a_pool())
    faltan = [c for c in SC.METRICAS if c not in todo.columns
              and c not in ("yellow_cards", "red_cards")]
    if faltan:
        print(f"  ojo: scouting.py pide métricas que la base no sabe armar "
              f"(quedan en 0): {faltan}")
    for c in SC.METRICAS:
        if c not in todo.columns:
            todo[c] = 0.0
        todo[c] = pd.to_numeric(todo[c], errors="coerce").fillna(0.0)
    # Las físicas quedan NaN donde no hubo tracking (scouting lo espera así).
    for c in getattr(SC, "TRACKING", []):
        if c not in todo.columns:
            todo[c] = np.nan
    todo["yellow_cards"] = todo["amarillas"]
    todo["red_cards"] = todo["rojas"]
    todo["player_name"] = todo["nombre_corto"]
    todo["position"] = todo["posicion"]
    todo["es_titular"] = todo["titular"].astype(bool)
    todo["nacimiento"] = todo["nacimiento_ts"]
    todo["team_name"] = todo["team_id"].map(nombres_equipo)
    todo["event_id"] = todo["event_id"].astype(str)
    return todo


def _extras_temporada(jp, ya_estan=()):
    """Totales y p90 de las stats que el pool no tiene, por (jugador, equipo).
    `ya_estan`: columnas que el pool ya trae, para no duplicarlas."""
    j = jp[jp["minutos"] > 0].copy()
    clave = ["player_id", "team_id"]
    minutos = j.groupby(clave)["minutos"].sum()
    out = pd.DataFrame(index=minutos.index)
    # Los ids originales de SofaScore detrás de la fila (más de uno si se
    # unificaron con config.ALIAS_JUGADORES): para cruzar con datos crudos.
    if "player_id_sofascore" in j.columns:
        out["player_ids_sofascore"] = j.groupby(clave)["player_id_sofascore"].agg(
            lambda s: ";".join(str(int(x)) for x in sorted(set(s))))
    completos = j[j["nivel_datos"] == "completo"].groupby(clave)["minutos"].sum()
    out["pct_minutos_datos_completos"] = (
        completos.reindex(out.index).fillna(0) / minutos * 100).round(1)
    # Qué parte de sus minutos se midió en un régimen distinto del inicial: un
    # refuerzo de invierno 2026 tiene casi todo en el B (ver CORTES_REGIMEN).
    otro = j[j["regimen"] != REGIMEN_INICIAL].groupby(clave)["minutos"].sum()
    out["pct_minutos_otro_regimen"] = (otro.reindex(out.index).fillna(0) / minutos * 100).round(1)
    for crudo, nombre in EXTRA_TEMPORADA.items():
        if crudo not in j.columns or nombre in ya_estan:
            continue
        con_dato = j[j[crudo].notna()]
        tot = con_dato.groupby(clave)[crudo].sum()
        mins = con_dato.groupby(clave)["minutos"].sum()
        out[nombre] = tot
        out[f"{nombre}_p90"] = (tot / mins.where(mins > 0) * 90).round(3)
    out["minutos_con_shotmap"] = (j[j["sm_tiros"].notna()].groupby(clave)["minutos"]
                                  .sum().reindex(out.index).fillna(0))
    if "minutos_tracking" not in ya_estan:
        out["minutos_con_fisico"] = (j[j["kilometersCovered"].notna()].groupby(clave)["minutos"]
                                     .sum().reindex(out.index).fillna(0))
    out["vel_max"] = j.groupby(clave)["topSpeed"].max()
    return out.reset_index()


def _jugador_temporada(temporada, jp, partidos_t, equipos_t):
    if jp.empty:
        return pd.DataFrame()
    nombres = equipos_t.set_index("team_id")["nombre"].to_dict()
    todo = _a_formato_scouting(jp, nombres)

    posesiones = pd.concat([
        partidos_t[["home_team_id", "posesion_home"]].set_axis(["team_id", "posesion"], axis=1),
        partidos_t[["away_team_id", "posesion_away"]].set_axis(["team_id", "posesion"], axis=1),
    ]).dropna()
    posesion = posesiones.groupby("team_id")["posesion"].mean().reset_index()

    df = SC._agregar_por_jugador(todo)
    df = SC.metricas_derivadas(df, posesion)
    # Edad al 1 de julio de la temporada: en una temporada vieja, la edad de
    # hoy no dice nada.
    df["edad"] = df["nacimiento"].apply(
        lambda ts: SC._edad_desde_timestamp(ts, referencia=f"{temporada}-07-01"))
    df["rol"] = [SC.asignar_rol(p, x, a)
                 for p, x, a in zip(df["posicion"], df["pos_x"], df["amplitud"])]
    df["banda"] = [SC.asignar_banda(p, r) for p, r in zip(df["pct_izq"], df["rol"])]
    df = SC._contexto_de_tabla(df, temporada)
    eventos = {str(r.event_id): os.path.join(config._ROOT, r.carpeta)
               for r in partidos_t.itertuples()}
    gk = SC._gk_psxg_metrics(eventos, todo)
    df = df.merge(gk, on=["player_id", "team_id"], how="left")

    # La zona sale de _zonas_equipo (que también entiende el 'Group B' de
    # 2025); el contexto de tabla de scouting solo conoce standings.csv.
    zonas = equipos_t.set_index("team_id")["zona"].to_dict()
    df["zona"] = df["team_id"].map(zonas).fillna(df.get("zona"))
    slugs = equipos_t.set_index("team_id")["slug"].to_dict()
    df["equipo_slug"] = df["team_id"].map(slugs)
    df["temporada"] = str(temporada)
    df["muestra"] = df["minutos"].apply(_muestra)

    df = df.merge(_extras_temporada(jp, ya_estan=set(df.columns)),
                  on=["player_id", "team_id"], how="left")
    primero = ["temporada", "player_id", "team_id", "equipo_slug", "zona"]
    return df[primero + [c for c in df.columns if c not in primero]]


# ──────────────────────────────── principal ──────────────────────────────────
def construir(temporadas=None, forzar=False, verbose=True):
    """
    Actualiza data/jugadores/. `temporadas` = lista de años a re-ingestar
    (default: todas las que haya en data/temporadas/). Las demás se dejan como
    están. `forzar=True` vuelve a leer todos los partidos aunque no cambiaron.
    """
    os.makedirs(DIR_JP, exist_ok=True)
    temporadas = [str(t) for t in (temporadas or _temporadas_disponibles())]
    ingesta = _leer_csv(_archivo("_ingesta"))
    partidos = _leer_csv(_archivo("partidos"))

    for t in temporadas:
        jp, partidos_t, ing_t = _ingestar_temporada(t, ingesta, partidos, forzar, verbose)
        if not partidos.empty:
            partidos = partidos[partidos["temporada"].astype(str) != t]
        partidos = pd.concat([partidos, partidos_t], ignore_index=True)
        if not ingesta.empty:
            ingesta = ingesta[ingesta["temporada"].astype(str) != t]
        ingesta = pd.concat([ingesta, ing_t], ignore_index=True)
        jp_path = os.path.join(DIR_JP, f"{t}.csv")
        if not jp.empty:
            jp.to_csv(jp_path, index=False)
        elif os.path.exists(jp_path):
            os.remove(jp_path)

    partidos["temporada"] = partidos["temporada"].astype(str)
    partidos["regimen"] = partidos["fecha_utc"].map(regimen_de)
    partidos = partidos.sort_values(["temporada", "fecha_utc", "event_id"])
    partidos.to_csv(_archivo("partidos"), index=False)
    ingesta.sort_values(["temporada", "event_id"]).to_csv(_archivo("_ingesta"), index=False)

    # Tablas derivadas: siempre desde cero, sobre TODAS las temporadas.
    equipos = _equipos(partidos)
    equipos.to_csv(_archivo("equipos"), index=False)

    jps = {t: _leer_csv(os.path.join(DIR_JP, f"{t}.csv"), low_memory=False)
           for t in sorted(partidos["temporada"].unique())}
    jps = {t: d for t, d in jps.items() if not d.empty}
    if not jps:
        return
    jp_todo = pd.concat(jps.values(), ignore_index=True)
    jp_todo["temporada"] = jp_todo["temporada"].astype(str)

    jugadores = _jugadores(jp_todo, equipos, _leer_csv(_archivo("jugadores")))
    jugadores.to_csv(_archivo("jugadores"), index=False)

    frames = []
    for t, jp in jps.items():
        jt = _jugador_temporada(t, jp, partidos[partidos["temporada"] == t],
                                equipos[equipos["temporada"] == t])
        if not jt.empty:
            frames.append(jt)
    jt = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    jt.to_csv(_archivo("jugador_temporada"), index=False)

    if verbose:
        print(f"\nBase en {DIR}")
        print(f"  partidos          : {len(partidos)}")
        print(f"  equipos           : {len(equipos)} (temporada × equipo)")
        print(f"  jugadores         : {len(jugadores)}")
        print(f"  jugador_partido   : {len(jp_todo)} filas en {len(jps)} temporadas")
        print(f"  jugador_temporada : {len(jt)} filas")


def hay_partidos_nuevos(temporada):
    """True si alguna carpeta de partido de la temporada (o algún CSV limpio
    adentro) es más nueva que la última corrida de construir(). Solo mira
    fechas de modificación: tarda menos de un segundo."""
    ref = _archivo("jugador_temporada")
    if not os.path.exists(ref):
        return True
    limite = os.path.getmtime(ref)
    base = os.path.join(_TEMPORADAS_DIR, str(temporada))
    raices = [os.path.join(base, "partidos")]
    rb = os.path.join(base, "rivals")
    if os.path.isdir(rb):
        raices += [e.path for e in os.scandir(rb) if e.is_dir()]
    for raiz in raices:
        if not os.path.isdir(raiz):
            continue
        if os.path.getmtime(raiz) > limite:        # se agregó una carpeta
            return True
        for e in os.scandir(raiz):
            if not e.is_dir():
                continue
            if e.stat().st_mtime > limite:          # se agregó un archivo
                return True
            lc = os.path.join(e.path, "lineups_clean.csv")
            if os.path.exists(lc) and os.path.getmtime(lc) > limite:   # re-scrapeado
                return True
    return False


# ──────────────────────────────── controles ──────────────────────────────────
def cargar(tabla, temporada=None):
    """Lee una tabla de la base. tabla='jugador_partido' pide `temporada`."""
    if tabla == "jugador_partido":
        return _leer_csv(os.path.join(DIR_JP, f"{temporada}.csv"), low_memory=False)
    return _leer_csv(_archivo(tabla), low_memory=False)


def verificar(temporada, verbose=True):
    """
    Integridad de una temporada. Levanta AssertionError si algo no cierra:
      - un event_id por partido y un (event_id, player_id) por fila
      - ningún jugador con más partidos que fechas
      - ~11 jugadores en cancha por equipo y partido (si diera ~22 sería
        doble conteo, que no rompe nada más y por eso se mira explícito)
    """
    jp = cargar("jugador_partido", temporada)
    partidos = cargar("partidos")
    partidos = partidos[partidos["temporada"].astype(str) == str(temporada)]
    assert not jp.empty, f"No hay jugador_partido para {temporada}."

    dup_p = partidos["event_id"].duplicated().sum()
    dup_j = jp.duplicated(["event_id", "player_id"]).sum()
    jugaron = jp[jp["minutos"] > 0]
    max_pj = jugaron.groupby(["player_id"])["event_id"].nunique().max()
    rondas = partidos["ronda"].nunique()
    en_cancha = (jugaron.groupby(["event_id", "team_id"])["minutos"].sum() / 90)
    completos = jp.loc[jp["minutos"] > 0, "nivel_datos"].eq("completo").mean() * 100
    diag = {"partidos": len(partidos), "con_lineups": jp["event_id"].nunique(),
            "jugadores": jp["player_id"].nunique(), "max_partidos": int(max_pj),
            "rondas": int(rondas), "en_cancha_mediana": float(en_cancha.median()),
            "pct_filas_completas": round(completos, 1)}
    if verbose:
        print(f"[{temporada}] partidos {diag['partidos']} (con lineups {diag['con_lineups']}) · "
              f"jugadores {diag['jugadores']} · máx. partidos de un jugador "
              f"{diag['max_partidos']} (rondas {diag['rondas']})")
        print(f"  en cancha por equipo y partido (mediana): {diag['en_cancha_mediana']:.2f} · "
              f"filas con datos completos: {diag['pct_filas_completas']}%")
    assert dup_p == 0, f"{dup_p} partidos repetidos en partidos.csv"
    assert dup_j == 0, f"{dup_j} filas (partido, jugador) repetidas"
    assert max_pj <= rondas + 2, "DOBLE CONTEO: más partidos que fechas"
    assert 10.0 <= diag["en_cancha_mediana"] <= 12.0, "DOBLE CONTEO: no da 11 en cancha"
    if verbose:
        print("  OK")
    return diag


def posibles_duplicados(verbose=True):
    """
    Jugadores que podrían ser la misma persona con dos player_id (SofaScore
    duplica o fusiona perfiles): mismo nombre corto, mismo equipo y misma
    temporada, y NUNCA en cancha en el mismo partido. No une nada: lista los
    candidatos con nombre completo y nacimiento para decidir a mano y cargar
    los confirmados en config.ALIAS_JUGADORES = {id_duplicado: id_real}.
    """
    frames = [cargar("jugador_partido", t) for t in _temporadas_disponibles()]
    frames = [f for f in frames if not f.empty]
    if not frames:
        return pd.DataFrame()
    jp = pd.concat(frames, ignore_index=True)
    j = jp[jp["minutos"] > 0].copy()
    # Dos llaves: el nombre corto, y el nombre completo sin tildes ni espacios
    # de más (G. Pacheco 83700 y E. Pacheco 2468554 son el mismo Ezequiel
    # Pacheco: cambia la inicial pero no el nombre completo).
    j["_completo"] = j["nombre_completo"].map(
        lambda s: " ".join(config.slugify_equipo(s).split("_")) if pd.notna(s) else None)
    grupos, vistos = [], set()
    for llave in ("nombre_corto", "_completo"):
        for (t, tid, _), g in j.groupby(["temporada", "team_id", llave]):
            ids = frozenset(g["player_id"])
            if len(ids) > 1 and (t, tid, ids) not in vistos:
                vistos.add((t, tid, ids))
                grupos.append((t, tid, g))

    filas = []
    for t, tid, g in grupos:
        nombre = SC._moda(g["nombre_corto"])
        eventos = g.groupby("player_id")["event_id"].apply(set)
        ids = list(eventos.index)
        juntos = any(eventos[a] & eventos[b]
                     for i, a in enumerate(ids) for b in ids[i + 1:])
        if juntos:
            continue   # jugaron el mismo partido: son dos personas
        for pid, gp in g.groupby("player_id"):
            nac = pd.to_datetime(SC._moda(gp["nacimiento_ts"]), unit="s", errors="coerce")
            filas.append({"temporada": t, "equipo": config.slug_de(tid),
                          "nombre_corto": nombre, "player_id": pid,
                          "nombre_completo": SC._moda(gp["nombre_completo"]),
                          "nacimiento": nac.date() if pd.notna(nac) else None,
                          "partidos": gp["event_id"].nunique(),
                          "primer_partido": gp["fecha"].min(),
                          "ultimo_partido": gp["fecha"].max(),
                          "evidencia": "nombre"})

    # Evidencia más fuerte: en un MISMO partido el shotmap y el lineup le dieron
    # ids distintos al mismo jugador (ver _reasignar_shotmap). Solo es un
    # duplicado a unir si el id del shotmap también figura en algún lineup;
    # si no, ya quedó resuelto al reasignar los remates.
    alias = getattr(config, "ALIAS_JUGADORES", {})
    p = cargar("partidos")
    pares = {}
    if "ids_shotmap_reasignados" in p.columns:
        for s, t in zip(p["ids_shotmap_reasignados"].dropna(),
                        p.loc[p["ids_shotmap_reasignados"].notna(), "temporada"]):
            for par in str(s).split(";"):
                a, b = (int(x) for x in par.split(">"))
                pares.setdefault((a, b), set()).add(str(t))
    en_lineup = set(jp["player_id_sofascore"])
    for (a, b), temps in pares.items():
        if a not in en_lineup or alias.get(a, a) == alias.get(b, b):
            continue
        for pid_sofa in (a, b):
            gp = j[j["player_id_sofascore"] == pid_sofa]
            if gp.empty:
                continue
            nac = pd.to_datetime(SC._moda(gp["nacimiento_ts"]), unit="s", errors="coerce")
            filas.append({"temporada": ",".join(sorted(set(gp["temporada"].astype(str)))),
                          "equipo": ";".join(sorted({config.slug_de(x) for x in gp["team_id"]})),
                          "nombre_corto": SC._moda(gp["nombre_corto"]),
                          "player_id": pid_sofa,
                          "nombre_completo": SC._moda(gp["nombre_completo"]),
                          "nacimiento": nac.date() if pd.notna(nac) else None,
                          "partidos": gp["event_id"].nunique(),
                          "primer_partido": gp["fecha"].min(),
                          "ultimo_partido": gp["fecha"].max(),
                          "evidencia": f"shotmap {a}>{b}"})
    out = pd.DataFrame(filas)
    if verbose:
        if out.empty:
            print("Sin candidatos a duplicado.")
        else:
            n_nom = out[out["evidencia"] == "nombre"].groupby(
                ["temporada", "equipo", "nombre_corto"]).ngroups
            n_sm = out[out["evidencia"] != "nombre"]["evidencia"].nunique()
            print(f"{n_nom} por nombre + {n_sm} por shotmap (revisar a mano):")
            print(out.to_string(index=False))
    return out


def comparar_con_pool(temporada="2026", verbose=True, sin_correcciones=True):
    """
    Control del código de agregación: arma jugador_temporada EN MEMORIA con
    las mismas copias de partido que usa scouting.eventos_unicos() y lo compara
    contra un pool_liga() recién regenerado. No toca data/jugadores/.

    Se fuerzan las mismas copias porque la base elige la más completa y nueva
    de cada partido, y scouting la primera que encuentra: con copias distintas
    la diferencia sería de datos, no de código. Diferencias esperadas:
      - `edad`: la base la calcula al 1/7 de la temporada, el pool a hoy.
      - `equipo`: la base usa el nombre de config, el pool mezcla grafías.

    sin_correcciones=True (default) apaga lo que la base corrige y scouting.py
    no — config.ALIAS_JUGADORES y la reasignación de remates del shotmap —
    para que sea una prueba de igualdad de código. Con False se ve el efecto
    de esas correcciones (filas que se unen, remates que se recuperan).
    Devuelve {'filas', 'faltan', 'diferencias'}.
    """
    pool = SC.pool_liga(str(temporada), min_minutos=0, refrescar=True,
                        verbose=False, fuente="carpetas")
    pool = pool.drop(columns=["muestra_chica"], errors="ignore")

    eventos, _ = SC.eventos_unicos(str(temporada))
    previo = dict(_CORRECCIONES)
    if sin_correcciones:
        _CORRECCIONES.update(alias=False, shotmap=False)
    try:
        filas_p, frames = [], []
        for eid, carpeta in eventos.items():
            partido, jug = leer_partido(int(eid), carpeta, temporada)
            filas_p.append(partido)
            if not jug.empty:
                frames.append(jug)
        partidos_t = pd.DataFrame(filas_p)
        jp = _ordenar_jp(pd.concat(frames, ignore_index=True))
    finally:
        _CORRECCIONES.update(previo)
    equipos_t = _equipos(partidos_t)
    jt = _jugador_temporada(str(temporada), jp, partidos_t, equipos_t)
    k = ["player_id", "team_id"]
    m = pool.merge(jt, on=k, how="outer", suffixes=("_pool", "_base"), indicator=True)
    solo = m["_merge"].value_counts().to_dict()
    ambos = m[m["_merge"] == "both"]
    dif = {}
    for c in pool.columns:
        if c in k or f"{c}_base" not in ambos.columns:
            continue
        a, b = ambos[f"{c}_pool"], ambos[f"{c}_base"]
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            distinto = ~(np.isclose(a, b, rtol=1e-6, atol=1e-6, equal_nan=True))
        else:
            distinto = ~((a.astype(str) == b.astype(str)) | (a.isna() & b.isna()))
        if distinto.sum():
            dif[c] = int(distinto.sum())
    faltan = [c for c in pool.columns if c not in k and f"{c}_base" not in ambos.columns]
    if verbose:
        print(f"[{temporada}] filas: {solo}")
        print(f"  columnas del pool que faltan en la base: {faltan or 'ninguna'}")
        print(f"  columnas con diferencias: {dif or 'ninguna'}")
    return {"filas": solo, "faltan": faltan, "diferencias": dif}
