"""
scouting.py
===========
Pool de scouting de TODA la categoría (Primera Nacional, Zona A + Zona B) y
auditoría del plantel propio.

Es la base del recomendador de jugadores: una fila por `player_id` con métricas
por-90, ajustadas por posesión (PAdj), suavizadas por tamaño de muestra, y con
un rol fino derivado de la posición media en cancha.

Ojo con el doble conteo: cada partido del torneo está guardado en la carpeta de
LOS DOS equipos, así que hay que deduplicar por `event_id` antes de agregar
(`eventos_unicos`). Sin eso, los minutos y los partidos salen al doble.

El pool NO reemplaza a `players.player_pool()`: aquel agrupa por nombre y sirve
para las pizzas de un equipo; este agrupa por `player_id` sobre la liga entera.
"""

import os
import json

import numpy as np
import pandas as pd

import config
from src.analysis import liga as L


# ─────────────────────────────── roles ───────────────────────────────────────
# Demarcaciones finas. SofaScore solo trae G/D/M/F, así que el rol sale de la
# posición media en cancha (average_positions_clean.csv).
ROLES = ("ARQ", "DFC", "LAT", "MCD", "MC", "EXT_MP", "DC")

ROL_NOMBRE = {
    "ARQ":    "Arquero",
    "DFC":    "Defensor central",
    "LAT":    "Lateral / carrilero",
    "MCD":    "Mediocampista defensivo (5)",
    "MC":     "Mediocampista mixto",
    "EXT_MP": "Extremo / mediapunta",
    "DC":     "Delantero centro",
}

# Cortes de la regla de rol, medidos sobre la temporada 2026 (no elegidos a ojo):
#
#   amp = mediana(|average_y - 50|)  → amplitud: qué tan por afuera juega.
#   Se usa el valor ABSOLUTO y no la mediana de y, porque un extremo que cambia
#   de banda entre partidos promedia y≈50 y quedaría clasificado como interior.
#
#   Histograma de amp de los defensores: bimodal, pico en 15-22 (central) y en
#   27-37 (lateral), con un valle real en 25-27.5 donde caen solo 7 jugadores.
#   De ahí AMP_ANCHO = 26.
#
#   average_x = profundidad (0 = arco propio, 100 = arco rival). Ya viene
#   normalizada por dirección de ataque: el arquero da x≈9 tanto de local como
#   de visitante, así que NO hay que espejar nada.
AMP_ANCHO = 26.0    # amp >= esto → juega por afuera
X_MCD     = 49.0    # M por adentro con x menor a esto → 5 posicional
X_MC      = 58.0    # M por adentro entre X_MCD y esto → volante mixto

# Un jugador se considera de una banda si jugó ahí al menos este % de sus
# partidos como titular. Entre medio queda "ambas" (polivalente de carril).
PCT_BANDA = 70.0

# Umbral de muestra de la especificación (§2.1).
MIN_MINUTOS   = 600
MUESTRA_CHICA = 900   # por debajo de esto, la salida lo avisa


# ───────────────────────── métricas del JSON crudo ───────────────────────────
# `lineups_clean.csv` se queda con 50 columnas, pero el raw trae varias que la
# especificación pide y que el CSV limpio no expone. Cobertura medida sobre
# 1867 jugadores: todas al 100% salvo las de pases por mitad de cancha (89-98%).
_RAW_STATS = {
    "ballRecovery":                 "recuperaciones",
    "outfielderBlock":              "bloqueos",
    "errorLeadToAShot":             "errores_a_remate",
    "wonTackle":                    "quites_ganados",
    "totalOppositionHalfPasses":    "pases_campo_rival",
    "accurateOppositionHalfPasses": "pases_campo_rival_ok",
    "totalOwnHalfPasses":           "pases_campo_propio",
    "accurateOwnHalfPasses":        "pases_campo_propio_ok",
    # Específicas de arquero (solo el propio arquero las tiene != 0).
    # `accurateKeeperSweeper` se descartó: SofaScore la manda en 0 siempre en
    # esta categoría, no distingue la salida exitosa de la que no.
    "goodHighClaim":                "centros_atajados",
    "crossNotClaimed":              "centros_no_atajados",
    "totalKeeperSweeper":           "salidas_arquero",
    "savedShotsFromInsideTheBox":   "atajadas_dentro_area",
    # Regates que le hicieron (lo pasaron) y malos controles: 98% de cobertura.
    "challengeLost":                "regateado",
    "unsuccessfulTouch":            "malos_controles",
    # Eventos raros (<1% de las filas): sirven como totales de temporada, no
    # como tasa por-90.
    "penaltyWon":                   "penales_provocados",
    "penaltyConceded":              "penales_cometidos",
    "penaltyMiss":                  "penales_errados",
    "clearanceOffLine":             "despejes_en_linea",
    "hitWoodwork":                  "tiros_al_palo",
}

# Datos físicos: SofaScore los manda en el 1,6% de las filas jugador-partido
# (unos pocos partidos con tracking). Ausente NO es cero: quedan NaN y el por-90
# se calcula solo sobre los minutos de los partidos que sí los traen.
_TRACKING_STATS = {
    "kilometersCovered": "km_recorridos",
    "numberOfSprints":   "sprints",
}

# Remate por remate del shotmap_clean.csv, agregado por jugador y partido.
_SITUACIONES_PELOTA_PARADA = ("corner", "free-kick", "set-piece",
                              "throw-in-set-piece")
_SHOTMAP_STATS = ["remates_shotmap", "npxg", "xgot", "goles_penal",
                  "remates_penal", "remates_cabeza", "remates_pelota_parada"]

# Métricas de conteo que ya vienen en lineups_clean.csv. En SofaScore una celda
# vacía significa CERO (omite las stats nulas), así que van con fillna(0).
_CSV_STATS = [
    "goals", "assists", "total_passes", "accurate_passes", "key_passes",
    "total_crosses", "accurate_crosses", "total_long_balls",
    "accurate_long_balls", "big_chances_created", "big_chances_missed",
    "xg", "xa", "touches", "possession_lost", "dispossessed",
    "shots_on_target", "shots_off_target", "shots_blocked",
    "dribbles_attempted", "dribbles_won", "tackles", "interceptions",
    "clearances", "duels_won", "duels_lost", "aerial_duels_won",
    "aerial_duels_lost", "was_fouled", "fouls", "offsides",
    "yellow_cards", "red_cards", "saves",
]

# Todo lo que se agrega sumando a lo largo de la temporada.
METRICAS = _CSV_STATS + list(_RAW_STATS.values()) + _SHOTMAP_STATS
TRACKING = list(_TRACKING_STATS.values())

# Métricas defensivas que se ajustan por posesión (§2.2): un central de un
# equipo que se pasa 70 minutos defendiendo infla despejes e intercepciones.
METRICAS_PADJ = ("tackles", "interceptions", "clearances",
                 "recuperaciones", "bloqueos")


def _moda(serie):
    """Valor más frecuente, o None si no hay ninguno. `position` viene NaN en
    algunas filas y `.mode().iat[0]` reventaría con IndexError."""
    s = serie.dropna()
    if s.empty:
        return None
    m = s.mode()
    return m.iat[0] if not m.empty else None


def _num(serie):
    """Serie a número con los vacíos en 0 (celda vacía = cero en SofaScore)."""
    return pd.to_numeric(serie, errors="coerce").fillna(0.0)


# ──────────────────────── deduplicación de partidos ──────────────────────────
def _slugs_liga(season="2026", zonas=("A", "B")):
    """Slugs únicos de los equipos de las zonas pedidas.

    group_a_teams() y group_b_teams() se solapan (gimnasia_jujuy figura en
    RIVALS_2026 pero juega en Zona B), así que hay que deduplicar o el equipo
    entra dos veces."""
    slugs = {}
    if "A" in zonas:
        for s in config.group_a_teams(season):
            slugs.setdefault(s, "A")
    if "B" in zonas:
        for s in config.group_b_teams(season):
            slugs.setdefault(s, "B")
    return slugs


def eventos_unicos(season="2026", zonas=("A", "B")):
    """
    Mapea {event_id: carpeta_del_partido}, quedándose con UNA sola carpeta por
    partido. Es la única defensa contra el doble conteo y todo el pool cuelga
    de acá: los ~964 directorios de partido son en realidad 482 partidos.

    Devuelve también {team_id: zona} para poder etiquetar después.
    """
    eventos, zona_por_equipo = {}, {}
    for slug, zona in _slugs_liga(season, zonas).items():
        base_dir, _, _ = L.team_context(slug, season)
        if not os.path.isdir(base_dir):
            continue
        # A propósito NO se usa el filtro CORE_CSVS de team_context: para el
        # pool alcanza con lineups + event. Pedir además shotmap/statistics
        # tiraría los partidos sin análisis de SofaScore, que igual tienen
        # los minutos y las stats por jugador.
        for mk in sorted(os.listdir(base_dir)):
            carpeta = os.path.join(base_dir, mk)
            ev_path = os.path.join(carpeta, "event_clean.csv")
            if not os.path.exists(ev_path):
                continue
            if not os.path.exists(os.path.join(carpeta, "lineups_clean.csv")):
                continue
            try:
                ev = pd.read_csv(ev_path).iloc[0]
            except Exception:
                continue
            eid = str(ev.get("event_id"))
            for col in ("home_team_id", "away_team_id"):
                tid = ev.get(col)
                if pd.notna(tid):
                    zona_por_equipo.setdefault(int(tid), zona)
            eventos.setdefault(eid, carpeta)
    return eventos, zona_por_equipo


# ────────────────────────── lectura de un partido ────────────────────────────
def _stats_del_raw(carpeta):
    """{player_id: {metrica: valor, bio...}} desde raw/lineups.json.

    El JSON crudo trae recuperaciones, bloqueos, errores que derivan en remate,
    quites ganados y pases por mitad de cancha —que el CSV limpio no expone—
    más la fecha de nacimiento, la altura y el valor de mercado."""
    path = os.path.join(carpeta, "raw", "lineups.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}

    out = {}
    for side in ("home", "away"):
        for entry in (data.get(side) or {}).get("players", []) or []:
            jugador = entry.get("player") or {}
            pid = jugador.get("id")
            if pid is None:
                continue
            fila = {}
            stats = entry.get("statistics") or {}
            for clave, nombre in _RAW_STATS.items():
                fila[nombre] = float(stats.get(clave) or 0)
            for clave, nombre in _TRACKING_STATS.items():
                v = pd.to_numeric(stats.get(clave), errors="coerce")
                fila[nombre] = float(v) if pd.notna(v) else np.nan

            fila["nombre_completo"] = jugador.get("name")
            fila["altura"] = jugador.get("height")
            fila["pais"] = (jugador.get("country") or {}).get("name")
            fila["nacimiento"] = jugador.get("dateOfBirthTimestamp")
            valor = jugador.get("proposedMarketValueRaw") or {}
            fila["valor_mercado_eur"] = valor.get("value")
            fila.update(config.CORRECCIONES_BIO_JUGADORES.get(int(pid), {}))
            out[int(pid)] = fila
    return out


def _remates_del_partido(carpeta):
    """{player_id: {npxg, xgot, remates_cabeza, ...}} desde shotmap_clean.csv.

    Los goles en contra se descartan: el shotmap los anota al jugador que la
    metió en su arco. `xgot` solo existe para los remates al arco, así que su
    suma ya es "xG post-remate de lo que fue al arco"."""
    path = os.path.join(carpeta, "shotmap_clean.csv")
    if not os.path.exists(path):
        return {}
    try:
        sh = pd.read_csv(path)
    except Exception:
        return {}
    if sh.empty or "player_id" not in sh.columns:
        return {}
    sh = sh[sh["situation"] != "own-goal"].copy()
    sh["player_id"] = pd.to_numeric(sh["player_id"], errors="coerce")
    sh = sh[sh["player_id"].notna()]
    sh["xg"] = _num(sh["xg"])
    sh["xgot"] = _num(sh["xgot"])
    penal = sh["situation"] == "penalty"

    out = {}
    for pid, g in sh.groupby(sh["player_id"].astype(int)):
        p = penal.loc[g.index]
        out[pid] = {
            "remates_shotmap":       float(len(g)),
            "npxg":                  float(g.loc[~p, "xg"].sum()),
            "xgot":                  float(g["xgot"].sum()),
            "goles_penal":           float((p & (g["shotType"] == "goal")).sum()),
            "remates_penal":         float(p.sum()),
            "remates_cabeza":        float((g["bodyPart"] == "head").sum()),
            "remates_pelota_parada": float(g["situation"]
                                           .isin(_SITUACIONES_PELOTA_PARADA).sum()),
        }
    return out


def _posesion_del_partido(carpeta):
    """(posesión_home, posesión_away) de statistics_clean.csv, o (None, None)."""
    path = os.path.join(carpeta, "statistics_clean.csv")
    if not os.path.exists(path):
        return None, None
    try:
        st = pd.read_csv(path)
    except Exception:
        return None, None
    fila = st[st["metric"] == "Ball possession"]
    if fila.empty:
        return None, None
    fila = fila.iloc[0]
    h = pd.to_numeric(fila.get("home_val"), errors="coerce")
    a = pd.to_numeric(fila.get("away_val"), errors="coerce")
    return (None if pd.isna(h) else float(h)), (None if pd.isna(a) else float(a))


def _posiciones_medias(carpeta):
    """{(player_id, team_side): (x, y)} de average_positions_clean.csv.

    Solo existe para los titulares, así que los suplentes quedan sin posición
    media y su rol se decide con los partidos en los que sí arrancaron."""
    path = os.path.join(carpeta, "average_positions_clean.csv")
    if not os.path.exists(path):
        return {}
    try:
        ap = pd.read_csv(path)
    except Exception:
        return {}
    out = {}
    for _, r in ap.iterrows():
        pid = pd.to_numeric(r.get("player_id"), errors="coerce")
        x = pd.to_numeric(r.get("average_x"), errors="coerce")
        y = pd.to_numeric(r.get("average_y"), errors="coerce")
        if pd.isna(pid) or pd.isna(x) or pd.isna(y):
            continue
        out[(int(pid), r.get("team_side"))] = (float(x), float(y))
    return out


def _leer_partido(event_id, carpeta):
    """Filas jugador-partido de un partido. Devuelve (df, filas_de_posesión)."""
    lin_path = os.path.join(carpeta, "lineups_clean.csv")
    ev_path = os.path.join(carpeta, "event_clean.csv")
    if not (os.path.exists(lin_path) and os.path.exists(ev_path)):
        return None, []

    try:
        lin = pd.read_csv(lin_path)
        ev = pd.read_csv(ev_path).iloc[0]
    except Exception:
        return None, []
    if lin.empty:
        return None, []

    # lineups_clean.csv no trae team_id y los nombres de equipo varían entre
    # fuentes, así que el id sale del event y se resuelve por team_side.
    ids = {"home": ev.get("home_team_id"), "away": ev.get("away_team_id")}
    pos_h, pos_a = _posesion_del_partido(carpeta)
    posesiones = []
    for side, val in (("home", pos_h), ("away", pos_a)):
        if val is not None and pd.notna(ids.get(side)):
            posesiones.append({"team_id": int(ids[side]), "posesion": val})

    lin["player_id"] = pd.to_numeric(lin["player_id"], errors="coerce")
    lin = lin[lin["player_id"].notna()].copy()
    lin["player_id"] = lin["player_id"].astype(int)
    lin["minutos"] = _num(lin["minutes_played"])
    lin = lin[lin["minutos"] > 0].copy()
    if lin.empty:
        return None, posesiones

    # El rating es NaN cuando no hay calificación: NUNCA va con fillna(0), que
    # hundiría el promedio del jugador.
    lin["rating"] = pd.to_numeric(lin.get("rating"), errors="coerce")

    for c in _CSV_STATS:
        lin[c] = _num(lin.get(c))

    raw = _stats_del_raw(carpeta)
    medias = _posiciones_medias(carpeta)

    for nombre in _RAW_STATS.values():
        lin[nombre] = [float((raw.get(p) or {}).get(nombre, 0) or 0)
                       for p in lin["player_id"]]
    for nombre in TRACKING:
        lin[nombre] = [(raw.get(p) or {}).get(nombre, np.nan)
                       for p in lin["player_id"]]
    remates = _remates_del_partido(carpeta)
    for nombre in _SHOTMAP_STATS:
        lin[nombre] = [(remates.get(p) or {}).get(nombre, 0.0)
                       for p in lin["player_id"]]
    for campo in ("nombre_completo", "altura", "pais", "nacimiento",
                  "valor_mercado_eur"):
        lin[campo] = [(raw.get(p) or {}).get(campo) for p in lin["player_id"]]

    lin["team_id"] = [ids.get(s) for s in lin["team_side"]]
    lin["es_titular"] = lin["is_starter"].astype(str).str.lower().eq("true")
    lin["avg_x"] = [medias.get((p, s), (np.nan, np.nan))[0]
                    for p, s in zip(lin["player_id"], lin["team_side"])]
    lin["avg_y"] = [medias.get((p, s), (np.nan, np.nan))[1]
                    for p, s in zip(lin["player_id"], lin["team_side"])]
    lin["event_id"] = event_id
    lin["ronda"] = ev.get("round")

    cols = (["event_id", "ronda", "team_id", "team_name", "player_id",
             "player_name", "nombre_completo", "position", "es_titular",
             "minutos", "rating", "avg_x", "avg_y", "altura", "pais",
             "nacimiento", "valor_mercado_eur"] + METRICAS + TRACKING)
    return lin[[c for c in cols if c in lin.columns]], posesiones


# ──────────────────────────────── el pool ────────────────────────────────────
def _ruta_cache(season):
    return os.path.join(config._SEASON_DATA_DIR.format(season=season),
                        "..", "pool_scouting.csv")


def partidos_jugador(season="2026", zonas=("A", "B"), verbose=True):
    """Todas las filas jugador-partido de la liga, ya deduplicadas por event_id.

    Es el insumo crudo de `pool_liga`; se expone aparte porque sirve para
    auditar (¿de qué partidos salen los minutos de este jugador?)."""
    eventos, zona_por_equipo = eventos_unicos(season, zonas)
    if verbose:
        print(f"Partidos únicos: {len(eventos)}")

    frames, posesiones = [], []
    for eid, carpeta in eventos.items():
        df, pos = _leer_partido(eid, carpeta)
        if df is not None and not df.empty:
            frames.append(df)
        posesiones.extend(pos)

    if not frames:
        return pd.DataFrame(), pd.DataFrame(), zona_por_equipo

    todo = pd.concat(frames, ignore_index=True)
    pos_df = (pd.DataFrame(posesiones).groupby("team_id")["posesion"]
              .mean().reset_index() if posesiones else pd.DataFrame())
    return todo, pos_df, zona_por_equipo


def asignar_rol(posicion, pos_x, amplitud):
    """Rol fino a partir de la posición gruesa de SofaScore (G/D/M/F) y de la
    posición media en cancha. Devuelve None si nunca fue titular (sin x/y).

    En esta liga SofaScore NO etiqueta extremos como 'F': los 93 delanteros con
    600+ minutos tienen amplitud máxima 15.8. Los extremos salen del bucket 'M'
    con amplitud alta, y se juntan con los mediapuntas en un solo rol —que es
    justo lo que hace la sección 3.5 de la especificación."""
    if posicion == "G":
        return "ARQ"
    if pd.isna(pos_x) or pd.isna(amplitud):
        return None
    ancho = amplitud >= AMP_ANCHO
    if posicion == "D":
        return "LAT" if ancho else "DFC"
    if posicion == "F":
        return "DC"
    if posicion == "M":
        if ancho:
            # Por afuera y adelantado es extremo; por afuera y retrasado es un
            # carrilero de línea de cinco, que funcionalmente es un lateral.
            return "EXT_MP" if pos_x >= 55 else "LAT"
        if pos_x < X_MCD:
            return "MCD"
        if pos_x < X_MC:
            return "MC"
        return "EXT_MP"
    return None


def asignar_banda(pct_izq, rol=None):
    """IZQ / DER / ambas, a partir de en qué proporción de partidos jugó por
    izquierda. Solo tiene sentido para los roles de carril (LAT, EXT_MP); para
    un central o un 5 devuelve None, porque no juegan por una banda fija.

    Es la diferencia entre proponer un reemplazo útil y uno inservible: la
    amplitud que define el rol es un valor absoluto y pierde el lado, así que
    sin esto el pool mezcla laterales izquierdos y derechos en un mismo puesto.
    """
    if rol is not None and rol not in ("LAT", "EXT_MP"):
        return None
    if pd.isna(pct_izq):
        return None
    if pct_izq >= PCT_BANDA:
        return "IZQ"
    if pct_izq <= 100 - PCT_BANDA:
        return "DER"
    return "ambas"


def _agregar_por_jugador(todo):
    """Una fila por (player_id, team_id): identidad, muestra y suma de métricas.

    Se agrupa TAMBIÉN por equipo, no solo por jugador: un jugador transferido a
    mitad de temporada (ej. M. Romero, que jugó 15 fechas en Nueva Chicago y
    volvió a Chaco desde la fecha 19) tiene partidos con dos `team_id`
    distintos. Agrupar solo por `player_id` y resolver el equipo por moda lo
    asignaba entero al club donde jugó MÁS partidos —desapareciéndolo del
    plantel actual y mezclando sus stats con un sistema/plantel distinto—. Acá
    cada paso por un club es su propia fila, con sus propios minutos y su
    propia muestra."""
    clave = ["player_id", "team_id"]

    # El rating es NaN cuando no hay calificación; se promedia ponderando por
    # minutos y SOLO sobre las filas que lo tienen.
    con_rating = todo[todo["rating"].notna()]
    rating = con_rating.groupby(clave).apply(
        lambda g: np.average(g["rating"], weights=g["minutos"]),
        include_groups=False)
    rating_sd = con_rating.groupby(clave)["rating"].std()

    # La posición media solo existe para los titulares. La amplitud se mide en
    # valor absoluto respecto del centro: la mediana de y confundiría a un
    # extremo que cambia de banda (promedia 50) con un interior.
    tit = todo[todo["avg_x"].notna()].copy()
    tit["amplitud"] = (tit["avg_y"] - 50).abs()
    pos_x = tit.groupby(clave)["avg_x"].median()
    amplitud = tit.groupby(clave)["amplitud"].median()

    # La amplitud pierde el lado (es un valor absoluto), y para buscar el
    # reemplazo de un lateral el lado es lo primero: un lateral derecho no
    # sirve para cubrir el carril izquierdo. `y_medio` conserva el signo y
    # `pct_izq` dice en qué proporción de sus partidos jugó por izquierda.
    #
    # OJO con la convención de SofaScore: en average_positions, y BAJO es la
    # DERECHA e y ALTO es la IZQUIERDA. Verificado contra los números de
    # camiseta de los 108 laterales de la temporada: de los que tienen y<40,
    # 46 usan la 4 (lateral derecho) y NINGUNO la 3; de los que tienen y>60,
    # 47 usan la 3 (lateral izquierdo) y ninguno la 4.
    y_medio = tit.groupby(clave)["avg_y"].median()
    pct_izq = tit.assign(_izq=tit["avg_y"] > 50).groupby(clave)["_izq"].mean() * 100

    agg = todo.groupby(clave).agg(
        nombre=("player_name", _moda),
        nombre_completo=("nombre_completo", _moda),
        equipo=("team_name", _moda),
        equipos_n=("team_id", "nunique"),
        posicion=("position", _moda),
        pj=("event_id", "nunique"),
        titular_pj=("es_titular", "sum"),
        minutos=("minutos", "sum"),
        altura=("altura", _moda),
        pais=("pais", _moda),
        nacimiento=("nacimiento", _moda),
        valor_mercado_eur=("valor_mercado_eur", _moda),
        **{c: (c, "sum") for c in METRICAS},
    )

    # Físicos: suma solo de los partidos con tracking (NaN si no hubo ninguno)
    # y los minutos de esos partidos, que son el denominador del por-90.
    con_tracking = todo[todo["km_recorridos"].notna()]
    for c in TRACKING:
        agg[c] = todo.groupby(clave)[c].sum(min_count=1)
    agg["minutos_tracking"] = con_tracking.groupby(clave)["minutos"].sum()
    agg["pj_tracking"] = con_tracking.groupby(clave)["event_id"].nunique()

    agg["rating"] = rating
    agg["rating_sd"] = rating_sd
    agg["pos_x"] = pos_x
    agg["amplitud"] = amplitud
    agg["y_medio"] = y_medio
    agg["pct_izq"] = pct_izq.round(1)
    # `equipos_n` cuenta clubes DISTINTOS en toda la temporada (útil para
    # marcar transferidos), no partidos dentro de esta fila.
    return agg.reset_index()


def _edad_desde_timestamp(ts, referencia=None):
    """Edad en años a partir del dateOfBirthTimestamp de SofaScore (epoch)."""
    if pd.isna(ts):
        return np.nan
    nacimiento = pd.to_datetime(float(ts), unit="s", errors="coerce")
    if pd.isna(nacimiento):
        return np.nan
    ref = pd.Timestamp(referencia) if referencia else pd.Timestamp.today()
    return round((ref - nacimiento).days / 365.25, 1)


def metricas_derivadas(pool, posesion):
    """Agrega p90, PAdj y los porcentajes de acierto/eficacia.

    PAdj (§2.2 de la especificación): en esta categoría un defensor de un equipo
    que se pasa el partido replegado infla despejes e intercepciones sin ser
    mejor. Se corrige por la posesión promedio de SU equipo."""
    df = pool.copy()

    for c in METRICAS:
        df[f"{c}_p90"] = np.where(df["minutos"] > 0,
                                  df[c] / df["minutos"] * 90, 0.0)

    df = df.merge(posesion, on="team_id", how="left")
    # 50 / (100 - posesión): un equipo con 50% de posesión no se toca.
    factor = 50.0 / (100.0 - df["posesion"].fillna(50.0)).clip(lower=1.0)
    for c in METRICAS_PADJ:
        df[f"{c}_padj"] = (df[f"{c}_p90"] * factor).round(3)

    def pct(num, den):
        n, d = df[num], df[den]
        return np.where(d > 0, n / d * 100, np.nan)

    df["duelos_terrestres_ganados"] = (df["duels_won"] - df["aerial_duels_won"]).clip(lower=0)
    df["duelos_terrestres_total"] = ((df["duels_won"] + df["duels_lost"])
                                     - (df["aerial_duels_won"] + df["aerial_duels_lost"])).clip(lower=0)
    df["duelos_terrestres_pct"] = np.where(
        df["duelos_terrestres_total"] > 0,
        df["duelos_terrestres_ganados"] / df["duelos_terrestres_total"] * 100, np.nan)
    df["duelos_terrestres_ganados_p90"] = np.where(
        df["minutos"] > 0, df["duelos_terrestres_ganados"] / df["minutos"] * 90, 0.0)

    df["duelos_aereos_total"] = df["aerial_duels_won"] + df["aerial_duels_lost"]
    df["duelos_aereos_pct"] = pct("aerial_duels_won", "duelos_aereos_total")
    df["pase_pct"] = pct("accurate_passes", "total_passes")
    df["centro_pct"] = pct("accurate_crosses", "total_crosses")
    df["pelota_larga_pct"] = pct("accurate_long_balls", "total_long_balls")
    df["regate_pct"] = pct("dribbles_won", "dribbles_attempted")
    df["pase_campo_rival_pct"] = pct("pases_campo_rival_ok", "pases_campo_rival")
    df["pase_campo_propio_pct"] = pct("pases_campo_propio_ok", "pases_campo_propio")

    df["shots_total"] = (df["shots_on_target"] + df["shots_off_target"]
                         + df["shots_blocked"])
    df["shots_total_p90"] = np.where(df["minutos"] > 0,
                                     df["shots_total"] / df["minutos"] * 90, 0.0)
    df["conversion_pct"] = pct("goals", "shots_total")

    # Sin penales: npxG contra goles de jugada (el penal infla a quien los patea).
    df["goles_sin_penal"] = df["goals"] - df["goles_penal"]
    df["goles_sin_penal_p90"] = np.where(df["minutos"] > 0,
                                         df["goles_sin_penal"] / df["minutos"] * 90, 0.0)
    df["npxg_por_remate"] = np.where(
        df["remates_shotmap"] - df["remates_penal"] > 0,
        df["npxg"] / (df["remates_shotmap"] - df["remates_penal"]), np.nan)
    df["remates_cabeza_pct"] = pct("remates_cabeza", "remates_shotmap")
    df["remates_pelota_parada_pct"] = pct("remates_pelota_parada", "remates_shotmap")
    df["regates_frenados_pct"] = np.where(
        df["tackles"] + df["regateado"] > 0,
        df["tackles"] / (df["tackles"] + df["regateado"]) * 100, np.nan)
    df["atajadas_dentro_area_pct"] = pct("atajadas_dentro_area", "saves")

    for c in TRACKING:
        df[f"{c}_p90"] = np.where(df["minutos_tracking"] > 0,
                                  df[c] / df["minutos_tracking"] * 90, np.nan)
    return df


# Columnas que el cache tiene que traer sí o sí; si falta alguna, se regenera.
_COLUMNAS_REQUERIDAS = ("player_id", "rol", "banda", "pct_izq", "y_medio",
                        "edad", "valor_mercado_eur", "posesion", "pos_tabla",
                        "zona", "saves", "goles_evitados_psxg", "npxg",
                        "malos_controles", "km_recorridos_p90")


def pool_liga(season="2026", min_minutos=MIN_MINUTOS, zonas=("A", "B"),
              usar_cache=True, refrescar=False, verbose=True,
              fuente="base", ajustado=True):
    """
    Pool de scouting de toda la categoría: una fila por (player_id, team_id).

    fuente='base' (default): sale de la base de jugadores (src/jugadores), que
    corrige lo que el cálculo desde carpetas no ve:
      - jugadores con dos player_id en SofaScore (config.ALIAS_JUGADORES),
      - remates que el shotmap anotó con otro id que el lineup,
      - el cambio de medición de SofaScore del 1/7/2026 (ajustado=True; ver
        src/jugadores/consultas.py). ajustado=False da los números crudos.
    refrescar=True (o usar_cache=False) actualiza antes la base (incremental:
    solo lee los partidos nuevos). Mismas columnas que siempre, más las de la
    base (temporada, equipo_slug, pct_minutos_otro_regimen, extras...).
    Para la temporada actual la edad es a HOY (como siempre la mostraron los
    informes); para una pasada, al 1/7 de ese año.

    fuente='carpetas': el cálculo original, leyendo las carpetas de partidos
    sin esas correcciones. Lo usa construir.comparar_con_pool() como control.
    """
    if fuente == "carpetas":
        return _pool_liga_carpetas(season, min_minutos, zonas, usar_cache,
                                   refrescar, verbose)
    # Import diferido: src.jugadores importa este módulo.
    from src.jugadores import construir as C
    from src.jugadores import consultas as Q

    season = str(season)
    refrescar = refrescar or not usar_cache
    en_base = C.cargar("jugador_temporada")
    falta = en_base.empty or season not in set(en_base["temporada"].astype(str))
    vencida = not falta and C.hay_partidos_nuevos(season)
    if vencida and verbose:
        print("Hay partidos scrapeados después de la última actualización de la base: se actualiza.")
    if refrescar or falta or vencida:
        C.construir([season], verbose=verbose)
        refrescar = True
    df = Q.pool([season], ajustado=ajustado, refrescar=refrescar)
    if df.empty:
        return df
    if zonas:
        df = df[df["zona"].isin(zonas) | df["zona"].isna()]
    if season == str(config.CURRENT_SEASON):
        df["edad"] = df["nacimiento"].apply(_edad_desde_timestamp)

    # pool_scouting.csv se sigue escribiendo: hay código que lo lee directo
    # (src/analysis/lineups.py).
    cache = os.path.join(config._ROOT, "data", "temporadas", season, "pool_scouting.csv")
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    df.to_csv(cache, index=False)

    df = df.copy()
    df["muestra_chica"] = df["minutos"] < MUESTRA_CHICA
    out = df[df["minutos"] >= min_minutos].copy()
    if verbose:
        etiqueta = "ajustado por régimen de datos" if ajustado else "crudo"
        print(f"Pool desde la base de jugadores ({etiqueta}): {len(out)} jugadores "
              f"con {min_minutos}+ minutos (de {len(df)} con minutos)")
    return out.reset_index(drop=True)


def _pool_liga_carpetas(season="2026", min_minutos=MIN_MINUTOS, zonas=("A", "B"),
                        usar_cache=True, refrescar=False, verbose=True):
    """
    El pool calculado desde las carpetas de partidos (el método original):
    deduplicado por `event_id`, con rol fino, edad, valor de mercado, métricas
    por-90, PAdj y porcentajes de acierto. El resultado se cachea SIN filtrar
    por minutos, así que cambiar `min_minutos` no obliga a releer todo.
    """
    # Cache propio: pool_scouting.csv ahora lo escribe pool_liga() desde la base.
    cache = os.path.join(config._ROOT, "data", "temporadas", str(season),
                         "pool_scouting_carpetas.csv")
    # Si el cache es de una versión anterior del pool (le faltan columnas que
    # el código de hoy espera), se regenera solo en vez de romper más adelante.
    vencido = False
    if os.path.exists(cache):
        cabecera = pd.read_csv(cache, nrows=0).columns
        vencido = not set(_COLUMNAS_REQUERIDAS).issubset(cabecera)

    if usar_cache and not refrescar and not vencido and os.path.exists(cache):
        df = pd.read_csv(cache)
        if verbose:
            print(f"Pool desde cache: {cache}")
    else:
        if vencido and verbose:
            print("El cache es de una versión anterior del pool: se regenera.")
        todo, posesion, zona_por_equipo = partidos_jugador(season, zonas, verbose)
        if todo.empty:
            return pd.DataFrame()
        df = _agregar_por_jugador(todo)
        df = metricas_derivadas(df, posesion)
        df["edad"] = df["nacimiento"].apply(_edad_desde_timestamp)
        df["rol"] = [asignar_rol(p, x, a) for p, x, a
                     in zip(df["posicion"], df["pos_x"], df["amplitud"])]
        df["banda"] = [asignar_banda(p, r)
                       for p, r in zip(df["pct_izq"], df["rol"])]
        df = _contexto_de_tabla(df, season)
        eventos, _ = eventos_unicos(season, zonas)
        gk = _gk_psxg_metrics(eventos, todo)
        df = df.merge(gk, on=["player_id", "team_id"], how="left")
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        df.to_csv(cache, index=False)
        if verbose:
            print(f"Pool guardado en {cache}")

    df["muestra_chica"] = df["minutos"] < MUESTRA_CHICA
    out = df[df["minutos"] >= min_minutos].copy()
    if verbose:
        print(f"{len(out)} jugadores con {min_minutos}+ minutos "
              f"(de {len(df)} con minutos)")
    return out.reset_index(drop=True)


def verificar_pool(season="2026", zonas=("A", "B"), verbose=True):
    """
    Control de integridad contra el doble conteo.

    Cada partido está guardado en la carpeta de LOS DOS equipos: si la
    deduplicación por `event_id` fallara, los minutos y los partidos saldrían
    al doble sin que nada más se rompa, y todos los p90 seguirían pareciendo
    razonables. Por eso el chequeo es explícito.

    Se corre sobre las filas POR PARTIDO, no sobre el pool agregado: ahí cada
    minuto está atribuido al equipo con el que se jugó. En el pool, en cambio,
    el equipo se resuelve por moda, así que a un jugador transferido a mitad de
    año se le cargan todos los minutos a un solo club y el control daría un
    falso positivo.

    Devuelve un dict con los diagnósticos y levanta AssertionError si algo no
    cierra.
    """
    todo, _, _ = partidos_jugador(season, zonas, verbose=False)
    if todo.empty:
        raise AssertionError("El pool salió vacío.")

    partidos = todo.groupby("team_id")["event_id"].nunique()
    en_cancha = (todo.groupby("team_id")["minutos"].sum() / 90) / partidos
    diag = {
        "partidos": int(todo["event_id"].nunique()),
        "jugadores": int(todo["player_id"].nunique()),
        "equipos": int(todo["team_id"].nunique()),
        "max_partidos": float(todo.groupby("player_id").size().max()),
        "en_cancha_min": float(en_cancha.min()),
        "en_cancha_max": float(en_cancha.max()),
    }
    if verbose:
        print(f"Partidos únicos: {diag['partidos']} · "
              f"jugadores: {diag['jugadores']} · equipos: {diag['equipos']}")
        print(f"Máx. partidos de un jugador : {diag['max_partidos']:.0f}")
        print(f"Jugadores en cancha/partido : {diag['en_cancha_min']:.2f} "
              f"a {diag['en_cancha_max']:.2f}  (tiene que dar ~11)")

    assert diag["max_partidos"] <= 40, (
        "DOBLE CONTEO: hay jugadores con más partidos que fechas de la temporada.")
    assert 10.0 <= diag["en_cancha_min"] and diag["en_cancha_max"] <= 12.0, (
        "DOBLE CONTEO: los minutos por equipo no cierran en 11 jugadores "
        f"({diag['en_cancha_min']:.2f}-{diag['en_cancha_max']:.2f}).")
    if verbose:
        print("\nOK: el pool no tiene doble conteo.")
    return diag


# ───────────────── suavizado, percentiles y scores por rol ───────────────────
def suavizar_p90(pool, columnas=None, k_partidos=8):
    """
    Suavizado empírico bayesiano: empuja las tasas por-90 de los jugadores con
    poca muestra hacia la mediana de su rol.

        valor = (n * crudo + K * mediana_del_rol) / (n + K),  n = minutos / 90

    Con K=8, un jugador de 600' pesa 45% propio y uno de 2200', 75%. Evita el
    clásico "goleador" con dos goles en 700 minutos encabezando el ranking.

    Se aplica SOLO a las tasas (p90 y PAdj), nunca a los porcentajes —que ya son
    ratios— ni al rating.
    """
    df = pool.copy()
    if columnas is None:
        # Los físicos quedan afuera: su muestra son los minutos con tracking,
        # no los minutos totales que usa el peso.
        fisicos = {f"{c}_p90" for c in TRACKING}
        columnas = [c for c in df.columns
                    if (c.endswith("_p90") or c.endswith("_padj"))
                    and c not in fisicos]
    n = df["minutos"] / 90.0
    peso = n / (n + k_partidos)
    for c in columnas:
        if c not in df.columns:
            continue
        mediana = df.groupby("rol")[c].transform("median")
        df[c] = (peso * df[c] + (1 - peso) * mediana.fillna(df[c].median()))
    return df


def percentiles_por_rol(pool, columnas):
    """Percentil 0-100 de cada métrica DENTRO del rol (§2.3).

    Comparar un central contra toda la liga no dice nada; el universo de
    referencia tiene que ser su propia demarcación."""
    df = pool.copy()
    for c in columnas:
        if c not in df.columns:
            continue
        df[f"{c}_pct"] = (df.groupby("rol")[c]
                          .rank(pct=True, na_option="keep") * 100).round(1)
    return df


# Índices compuestos de la sección 3 de la especificación, podados a lo que el
# dataset tiene. Cada componente es un promedio de percentiles dentro del rol;
# el score final es la suma ponderada, en escala 0-100.
#
# Recortes respecto del documento (por datos inexistentes en SofaScore):
#   - `touches_in_box` no existe        → se usa `touches_p90`
#   - `passes_final_third` no existe    → `pase_campo_rival_pct` (medio campo)
#   - pases progresivos no existen      → pelotas largas + pases en campo rival
#   - duelos por zona no existen        → duelos terrestres globales
PESOS_SCORE = {
    "DFC": {
        "duelo_aereo":    (0.30, ["duelos_aereos_pct"]),
        "duelo_suelo":    (0.25, ["duelos_terrestres_pct"]),
        "volumen_def":    (0.20, ["clearances_padj", "interceptions_padj"]),
        "salida":         (0.15, ["accurate_long_balls_p90", "pase_campo_rival_pct"]),
        "rating":         (0.10, ["rating"]),
    },
    "LAT": {
        "duelo_def":      (0.25, ["duelos_terrestres_pct"]),
        "centro":         (0.25, ["accurate_crosses_p90", "centro_pct"]),
        "creacion":       (0.25, ["key_passes_p90", "touches_p90"]),
        "recuperacion":   (0.15, ["recuperaciones_padj"]),
        "rating":         (0.10, ["rating"]),
    },
    "MCD": {
        "recuperacion":   (0.30, ["recuperaciones_padj", "interceptions_padj"]),
        "pase":           (0.25, ["pase_pct"]),
        "duelo_suelo":    (0.25, ["duelos_terrestres_pct"]),
        "bajo_presion":   (0.10, ["pase_campo_propio_pct"]),
        "rating":         (0.10, ["rating"]),
    },
    "MC": {
        "progresion":     (0.25, ["dribbles_won_p90", "pase_campo_rival_pct"]),
        "creacion":       (0.25, ["key_passes_p90"]),
        "presencia_def":  (0.25, ["tackles_padj", "interceptions_padj"]),
        "llegada":        (0.15, ["touches_p90"]),
        "rating":         (0.10, ["rating"]),
    },
    "EXT_MP": {
        "generacion":     (0.30, ["key_passes_p90", "assists_p90", "xa_p90"]),
        "desequilibrio":  (0.25, ["dribbles_won_p90", "touches_p90"]),
        "amenaza":        (0.25, ["shots_on_target_p90", "xg_p90"]),
        "duelo":          (0.10, ["duelos_terrestres_pct"]),
        "rating":         (0.10, ["rating"]),
    },
    "DC": {
        "eficacia":       (0.35, ["goals_p90", "conversion_pct"]),
        "presencia_area": (0.25, ["touches_p90", "shots_on_target_p90"]),
        "juego_aereo":    (0.20, ["aerial_duels_won_p90", "duelos_aereos_pct"]),
        "asociacion":     (0.10, ["assists_p90", "xa_p90"]),
        "rating":         (0.10, ["rating"]),
    },
}


def metricas_del_score(rol):
    """Lista plana de métricas que entran en el score de un rol."""
    cols = []
    for _, metricas in PESOS_SCORE.get(rol, {}).values():
        cols.extend(metricas)
    return list(dict.fromkeys(cols))


def scores_compuestos(pool):
    """
    Score 0-100 por rol (§3) más su percentil dentro del rol.

    El arquero queda sin score a propósito: `goals_prevented` está vacía en el
    100% de los partidos y `saves` aparece en el 6%, así que no hay con qué
    puntuarlo. La especificación tampoco define un GK Score.
    """
    todas = sorted({m for rol in PESOS_SCORE for m in metricas_del_score(rol)})
    df = percentiles_por_rol(pool, todas)

    df["score_rol"] = np.nan
    for rol, componentes in PESOS_SCORE.items():
        mask = df["rol"] == rol
        if not mask.any():
            continue
        total = pd.Series(0.0, index=df.index[mask])
        for peso, metricas in componentes.values():
            cols = [f"{m}_pct" for m in metricas if f"{m}_pct" in df.columns]
            if not cols:
                continue
            total += peso * df.loc[mask, cols].mean(axis=1).fillna(50.0)
        df.loc[mask, "score_rol"] = total.round(1)

    df["score_pct"] = (df.groupby("rol")["score_rol"]
                       .rank(pct=True, na_option="keep") * 100).round(1)
    return df


# ────────────────────── semáforo de continuidad (§4) ─────────────────────────
_ACCIONES = {
    "PRIORIDAD_RENOVACION": (1, "Asegurar renovación. Columna vertebral del equipo."),
    "ROTACION_VALIOSA":     (2, "Mantener con tope salarial de rol secundario."),
    "PRESCINDIBLE":         (3, "No comprometer presupuesto de aumento. Reemplazable."),
    "BAJA_PRIORITARIA":     (4, "Liberar masa salarial o cupo de plantilla."),
    "SIN_EVALUAR":          (5, "Sin score compuesto (arqueros): decidir por video y rating."),
}


def _estado(pct_minutos, score_pct, sd, sd_max):
    # Los arqueros no tienen score: SofaScore no publica goals_prevented y saves
    # aparece en el 6% de los partidos. Marcarlos PRESCINDIBLE sería un error de
    # lectura —el arquero de Chaco tiene el mejor rating del plantel—, así que
    # quedan explícitamente sin evaluar.
    if pd.isna(score_pct):
        return "SIN_EVALUAR"
    sd = sd if pd.notna(sd) else sd_max
    if pct_minutos >= 65 and score_pct >= 70 and sd <= sd_max:
        return "PRIORIDAD_RENOVACION"
    if ((score_pct >= 60 and pct_minutos < 65)
            or (pct_minutos >= 50 and score_pct >= 50 and sd <= sd_max * 0.85)):
        return "ROTACION_VALIOSA"
    if 40 <= score_pct < 60:
        return "PRESCINDIBLE"
    return "BAJA_PRIORITARIA"


def semaforo_plantel(pool, team_id=None, sd_max=None, excluir_bajas=True):
    """
    Clasifica al plantel en PRIORIDAD_RENOVACION / ROTACION_VALIOSA /
    PRESCINDIBLE / BAJA_PRIORITARIA (§4 de la especificación).

    `sd_max` es el techo de irregularidad del rating. El documento propone 0.65,
    pero ese número está calibrado para otra liga: si no se pasa nada, se usa la
    MEDIANA del desvío de la Primera Nacional, para que el criterio separe de
    verdad en vez de aprobar o reprobar a todos.

    `excluir_bajas` saca a los jugadores de `config.JUGADORES_FUERA`: la
    auditoría decide renovaciones, y no tiene sentido clasificar a alguien que
    ya dejó el club.
    """
    team_id = team_id or config.CHACO_TEAM_ID
    if sd_max is None:
        sd_max = float(pool["rating_sd"].median())

    plantel = pool[pool["team_id"] == team_id].copy()
    if excluir_bajas:
        plantel = config.excluir_jugadores_fuera(plantel, col="nombre")
    plantel["estado"] = [
        _estado(pm, sp, sd, sd_max) for pm, sp, sd
        in zip(plantel["pct_minutos_equipo"].fillna(0),
               plantel["score_pct"], plantel["rating_sd"])
    ]
    plantel["tier"] = plantel["estado"].map(lambda e: _ACCIONES[e][0])
    plantel["accion"] = plantel["estado"].map(lambda e: _ACCIONES[e][1])

    cols = ["nombre", "rol", "edad", "pj", "minutos", "pct_minutos_equipo",
            "rating", "rating_sd", "score_rol", "score_pct", "valor_mercado_eur",
            "muestra_chica", "estado", "tier", "accion"]
    return (plantel[[c for c in cols if c in plantel.columns]]
            .sort_values(["tier", "minutos"], ascending=[True, False])
            .reset_index(drop=True))


def _gk_psxg_metrics(eventos, todo):
    """Goles evitados (PSxG − goles recibidos) por arquero.

    PSxG sale de `xgot` (el xG post-remate de SofaScore, que ya pondera dónde
    picó el remate en el arco) de los tiros AL ARCO ('save'/'goal') en
    shotmap_clean.csv, atribuidos al equipo que los recibe. Solo cubre los
    partidos con shotmap (~98% de los 520 de la liga); el resto queda afuera,
    y `partidos_arco_con_shotmap` deja ver cuánta muestra hay detrás de cada
    número. `goals_prevented` de SofaScore no sirve para esto: viene vacío en
    el 100% de los partidos de esta categoría.

    El arquero de cada partido es el que sumó más minutos en la posición 'G'
    de ese equipo en ese partido —cubre la suplencia sin tener que leer el XI
    titular aparte—, y se le carga el resultado del partido ENTERO (no separa
    goles recibidos antes/después de un cambio de arquero a mitad de juego).
    """
    cols_out = ["player_id", "team_id", "psxg_contra", "goles_contra_arco",
                "partidos_arco", "partidos_arco_con_shotmap", "goles_evitados_psxg"]
    porteros = todo[todo["position"] == "G"]
    if porteros.empty:
        return pd.DataFrame(columns=cols_out)

    idx = porteros.groupby(["event_id", "team_id"])["minutos"].idxmax()
    arco_por_partido = porteros.loc[idx, ["event_id", "team_id", "player_id"]].copy()
    arco_por_partido["event_id"] = arco_por_partido["event_id"].astype(str)

    filas = []
    for eid, carpeta in eventos.items():
        sm_path = os.path.join(carpeta, "shotmap_clean.csv")
        ev_path = os.path.join(carpeta, "event_clean.csv")
        if not (os.path.exists(sm_path) and os.path.exists(ev_path)):
            continue
        try:
            sm = pd.read_csv(sm_path)
            ev = pd.read_csv(ev_path).iloc[0]
        except Exception:
            continue
        remates = sm[sm["shotType"].isin(("save", "goal"))]
        # isHome marca al EQUIPO QUE REMATA: lo que remata el visitante lo
        # ataja el arquero local, y viceversa.
        psxg_local = remates.loc[~remates["isHome"], "xgot"].sum()
        psxg_visita = remates.loc[remates["isHome"], "xgot"].sum()
        home_id, away_id = ev.get("home_team_id"), ev.get("away_team_id")
        if pd.notna(home_id):
            filas.append({"event_id": eid, "team_id": int(home_id),
                          "psxg_contra": psxg_local,
                          "goles_contra_arco": ev.get("home_score")})
        if pd.notna(away_id):
            filas.append({"event_id": eid, "team_id": int(away_id),
                          "psxg_contra": psxg_visita,
                          "goles_contra_arco": ev.get("away_score")})
    if not filas:
        return pd.DataFrame(columns=cols_out)

    por_partido = pd.DataFrame(filas)
    por_partido["event_id"] = por_partido["event_id"].astype(str)
    con_shotmap = arco_por_partido.merge(por_partido, on=["event_id", "team_id"], how="inner")

    out = con_shotmap.groupby(["player_id", "team_id"]).agg(
        psxg_contra=("psxg_contra", "sum"),
        goles_contra_arco=("goles_contra_arco", "sum"),
        partidos_arco_con_shotmap=("event_id", "nunique"),
    ).reset_index()
    total_partidos = (arco_por_partido.groupby(["player_id", "team_id"])["event_id"]
                      .nunique().rename("partidos_arco"))
    out = out.merge(total_partidos, on=["player_id", "team_id"], how="left")
    out["psxg_contra"] = out["psxg_contra"].round(2)
    out["goles_evitados_psxg"] = (out["psxg_contra"] - out["goles_contra_arco"]).round(2)
    return out[cols_out]


def _contexto_de_tabla(df, season):
    """Agrega zona, posición en la tabla y puntos del equipo (para el perfil
    Moneyball). Se une por `team_id`: el `team_slug` de standings usa guiones
    y el de config guiones bajos, así que por slug no matchearía.

    La zona sale de en cuál de las dos tablas (A o B) aparece el `team_id`,
    NO de `eventos_unicos`: el fixture real de Primera Nacional tiene partidos
    interzonales (ej. Acassuso-Ferrocarril Midland), así que recorrer la
    carpeta de partidos de cada equipo y taguear zona por rival de cada
    partido contamina el resultado — terminaba etiquetando TODO como zona A
    porque los equipos de zona A se procesan primero y `setdefault` deja fija
    la primera zona que ve cada `team_id`. Las tablas de posiciones, en
    cambio, ya vienen separadas por SofaScore sin ambigüedad."""
    filas = []
    for path, zona in ((config.standings_file(season), "A"),
                       (config.standings_zona_b_file(season), "B")):
        if os.path.exists(path):
            t = pd.read_csv(path)
            t["equipos_zona"] = len(t)
            t["zona"] = zona
            filas.append(t[["team_id", "zona", "position", "points",
                            "matches_played", "equipos_zona"]])
    if not filas:
        df["zona"] = np.nan
        df["pos_tabla"] = np.nan
        df["pts_equipo"] = np.nan
        df["partidos_equipo"] = np.nan
        return df
    tabla = pd.concat(filas, ignore_index=True).drop_duplicates("team_id")
    tabla = tabla.rename(columns={"position": "pos_tabla", "points": "pts_equipo",
                                  "matches_played": "partidos_equipo"})
    df = df.drop(columns=["zona"], errors="ignore").merge(tabla, on="team_id", how="left")
    df["pct_minutos_equipo"] = np.where(
        df["partidos_equipo"].notna() & (df["partidos_equipo"] > 0),
        df["minutos"] / (90.0 * df["partidos_equipo"]) * 100, np.nan).round(1)
    return df


# ---------------------------------------------------------------------------
# Ranking absoluto (para placas e historias de Instagram)
# ---------------------------------------------------------------------------
_ROL_PLURAL = {"ARQ": "arqueros", "DFC": "centrales", "LAT": "laterales",
               "MCD": "volantes centrales", "MC": "volantes", "EXT_MP": "extremos",
               "DC": "delanteros"}


def ranking_puesto(pool, nombre, metrica=None, equipo=None):
    """
    Puesto absoluto de un jugador entre los de su mismo rol en la categoría.

    Para redes se usa esto en lugar del percentil ("3° de 111 volantes" se
    entiende solo; "percentil 98" no). Los informes siguen con percentil.

    pool:    salida de pool_liga + suavizar_p90 + scores_compuestos (con *_pct).
    nombre:  texto contenido en el nombre ("Hoyos", "E. Hoyos").
    metrica: columna sin el sufijo _pct (ej. 'key_passes_p90', 'rating');
             None = puntaje compuesto del rol.
    equipo:  texto contenido en el equipo, para desambiguar homónimos.

    Devuelve dict(nombre, equipo, rol, puesto, de, texto, texto_corto) o None.
    El universo es el del pool (jugadores con los minutos mínimos con que se
    armó), así que conviene citar siempre con ese mismo pool.
    """
    col = "score_pct" if metrica is None else f"{metrica}_pct"
    if col not in pool.columns:
        raise KeyError(f"No hay columna {col} en el pool")
    c = pool[pool["nombre"].str.contains(nombre, case=False, regex=False)]
    if equipo:
        c = c[c["equipo"].str.contains(equipo, case=False, regex=False)]
    if c.empty:
        return None
    r = c.sort_values("minutos", ascending=False).iloc[0]
    univ = pool[(pool["rol"] == r["rol"]) & pool[col].notna()]
    if pd.isna(r[col]):
        return None
    puesto = int((univ[col] > r[col]).sum()) + 1
    n = len(univ)
    plural = _ROL_PLURAL.get(r["rol"], "jugadores")
    return {"nombre": r["nombre"], "equipo": r["equipo"], "rol": r["rol"],
            "puesto": puesto, "de": n,
            "texto": f"{puesto}° de {n} {plural}",
            "texto_corto": f"{puesto}° de {n}"}
