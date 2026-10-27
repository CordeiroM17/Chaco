"""
consultas.py
============
Leer la base de jugadores (data/jugadores/, la arma construir.py).

    from src.jugadores import consultas as Q
    Q.buscar("Pacheco")                       # jugadores que matchean
    Q.historial(2468554)                      # temporada por temporada + carrera
    pool = Q.pool(["2025", "2026"])           # una fila por (temporada, jugador, equipo)
    pct = Q.percentiles(pool, universo="historico")   # contra todos los años
    Q.puesto(pct, 2468554, "xg_p90")          # "3° de 111 delanteros"

Ajuste por régimen de datos
---------------------------
SofaScore cambió cómo mide la Primera Nacional desde el 1/7/2026 (ver
construir.CORTES_REGIMEN): quites -55%, despejes +77%, regates -35%... Sin
corregir, un refuerzo de invierno 2026 parece no quitar nunca y despejar todo.

`pool(ajustado=True)` (default) lleva cada stat del régimen nuevo a la escala
del régimen de referencia con un factor por estadística y por posición
(G/D/M/F): factor = tasa por-90 en el régimen de referencia / tasa en el otro.
Es un reescalado: conserva el orden de los jugadores DENTRO de cada régimen y
los vuelve comparables entre regímenes. Los datos crudos no se tocan
(`ajustado=False` devuelve el pool tal cual, igual al de scouting.py).

No se ajustan: goles, asistencias, goles en contra, penales, tarjetas, rating,
minutos ni las físicas — son hechos, no conteos de un proveedor. Una stat que
en un régimen dejó de medirse (`unsuccessfulTouch` vale 0 en el B) queda con
su tasa calculada SOLO sobre los minutos donde sí se midió.
"""

import os

import numpy as np
import pandas as pd

import config
from src.analysis import scouting as SC
from src.jugadores import construir as C


ARCHIVO_FACTORES = os.path.join(C.DIR, "factores_regimen.csv")
ARCHIVO_AJUSTADO = os.path.join(C.DIR, "jugador_temporada_ajustada.csv")

# Hechos del partido, no conteos del proveedor: no se reescalan.
NO_AJUSTAR = {
    "goals", "goalAssist", "ownGoals", "penaltyWon", "penaltyConceded",
    "penaltyMiss", "penaltyFaced", "penaltySave", "sm_goles_penal",
    "sm_tiros_penal", "amarillas", "rojas", "doble_amarilla",
    "goles_recibidos", "psxg_enfrentado",
}

# Mínimo de eventos (en cada régimen) para confiar en un factor por posición;
# por debajo se usa el factor de todas las posiciones juntas, y si tampoco
# alcanza, 1 (no se ajusta).
MIN_EVENTOS_FACTOR = 30


def _stats_ajustables():
    return ([c for c in C.STATS_SOFASCORE
             if c not in C.STATS_FISICAS and c not in NO_AJUSTAR]
            + [c for c in C._COLS_SHOTMAP if c not in NO_AJUSTAR])


def _jp_todas(temporadas=None):
    temporadas = [str(t) for t in (temporadas or C._temporadas_disponibles())]
    frames = [C.cargar("jugador_partido", t) for t in temporadas]
    frames = [f for f in frames if not f.empty]
    if not frames:
        return pd.DataFrame()
    jp = pd.concat(frames, ignore_index=True)
    jp["temporada"] = jp["temporada"].astype(str)
    return jp


# ─────────────────────────── factores de régimen ─────────────────────────────
def factores_regimen(guardar=True, verbose=True):
    """
    Factor de cada stat y posición para llevar cada régimen a la escala del
    inicial (construir.REGIMEN_INICIAL). Se calcula con TODAS las temporadas
    de la base (filas con datos completos) y se guarda en
    data/jugadores/factores_regimen.csv.
    """
    jp = _jp_todas()
    j = jp[(jp["minutos"] > 0) & (jp["nivel_datos"] == "completo")].copy()
    j["posicion"] = j["posicion"].fillna("?")
    ref = C.REGIMEN_INICIAL
    stats = [c for c in _stats_ajustables() if c in j.columns]

    filas = []
    for reg in sorted(r for r in j["regimen"].unique() if r != ref):
        for pos in ["todas", "G", "D", "M", "F"]:
            sel = j if pos == "todas" else j[j["posicion"] == pos]
            a, b = sel[sel["regimen"] == ref], sel[sel["regimen"] == reg]
            min_a, min_b = a["minutos"].sum(), b["minutos"].sum()
            for m in stats:
                ea, eb = a[m].sum(), b[m].sum()
                ta = ea / min_a * 90 if min_a else np.nan
                tb = eb / min_b * 90 if min_b else np.nan
                if ea >= MIN_EVENTOS_FACTOR and eb >= MIN_EVENTOS_FACTOR:
                    factor, origen = ta / tb, "propio"
                elif ea >= MIN_EVENTOS_FACTOR and eb == 0:
                    factor, origen = np.nan, "no_medida"   # dejó de medirse
                else:
                    factor, origen = None, "poca_muestra"  # se resuelve abajo
                filas.append({"regimen": reg, "posicion": pos, "metrica": m,
                              "eventos_ref": ea, "eventos": eb,
                              "tasa_ref_p90": ta, "tasa_p90": tb,
                              "factor": factor, "origen": origen})
    f = pd.DataFrame(filas)
    if f.empty:
        return f

    # Poca muestra en una posición → el factor de todas las posiciones juntas;
    # poca muestra también ahí → 1 (no se ajusta).
    glob = f[f["posicion"] == "todas"].set_index(["regimen", "metrica"])
    poca = f["origen"] == "poca_muestra"
    for i in f.index[poca]:
        r = f.loc[i]
        g = glob.loc[(r["regimen"], r["metrica"])]
        if r["posicion"] != "todas" and g["origen"] in ("propio", "no_medida"):
            f.loc[i, ["factor", "origen"]] = [g["factor"], "global"]
        else:
            f.loc[i, ["factor", "origen"]] = [1.0, "sin_ajuste"]
    f["factor"] = f["factor"].astype(float)

    if guardar:
        f.to_csv(ARCHIVO_FACTORES, index=False)
    if verbose:
        g = f[f["posicion"] == "todas"].copy()
        g["cambio_%"] = ((1 / g["factor"] - 1) * 100).round(0)
        muy = g[g["cambio_%"].abs() >= 15].sort_values("cambio_%")
        print(f"Factores de régimen ({len(f)} filas) en {ARCHIVO_FACTORES}")
        print("Stats que cambian 15% o más en el régimen nuevo (todas las posiciones):")
        print(muy[["regimen", "metrica", "tasa_ref_p90", "tasa_p90", "cambio_%"]]
              .round(3).to_string(index=False))
        sin = g[g["factor"].isna()]["metrica"].tolist()
        if sin:
            print(f"Dejaron de medirse en el régimen nuevo: {sin}")
    return f


def ajustar_jp(jp, factores=None):
    """jugador_partido con las stats del régimen no inicial llevadas a la
    escala del inicial. Las que dejaron de medirse quedan NaN en ese régimen."""
    if factores is None:
        factores = (pd.read_csv(ARCHIVO_FACTORES) if os.path.exists(ARCHIVO_FACTORES)
                    else factores_regimen(verbose=False))
    jp = jp.copy()
    otro = jp["regimen"] != C.REGIMEN_INICIAL
    if not otro.any() or factores.empty:
        return jp
    pos = jp["posicion"].fillna("?")
    por_pos = factores.set_index(["regimen", "posicion", "metrica"])["factor"]
    glob = factores[factores["posicion"] == "todas"].set_index(["regimen", "metrica"])["factor"]
    for m in factores["metrica"].unique():
        if m not in jp.columns:
            continue
        idx = jp.index[otro]
        f = [por_pos.get((r, p, m), glob.get((r, m), 1.0))
             for r, p in zip(jp.loc[idx, "regimen"], pos.loc[idx])]
        jp.loc[idx, m] = jp.loc[idx, m] * np.array(f, dtype=float)
    return jp


# ─────────────────────────────────── pool ────────────────────────────────────
def _tasas_solo_medidas(pool, jp_aj, temporada):
    """Para las stats que en algún régimen no se miden (NaN tras ajustar), el
    pool de scouting las sumó como 0. Acá se rehace su total y su p90 solo
    con los minutos donde existen."""
    mapeo = C._mapeo_a_pool()
    j = jp_aj[(jp_aj["minutos"] > 0) & (jp_aj["temporada"] == str(temporada))]
    for crudo, nombre in mapeo.items():
        if crudo not in j.columns or nombre not in pool.columns:
            continue
        no_medido = j[crudo].isna() & (j["nivel_datos"] == "completo")
        if not no_medido.any():
            continue
        medida = j[j[crudo].notna()]
        clave = ["player_id", "team_id"]
        tot = medida.groupby(clave)[crudo].sum()
        mins = medida.groupby(clave)["minutos"].sum()
        idx = pd.MultiIndex.from_frame(pool[clave])
        pool[nombre] = tot.reindex(idx).values
        if f"{nombre}_p90" in pool.columns:
            pool[f"{nombre}_p90"] = (tot / mins.where(mins > 0) * 90).reindex(idx).values
    return pool


def pool(temporadas=None, ajustado=True, min_minutos=0, refrescar=False):
    """
    Una fila por (temporada, jugador, equipo), con las mismas columnas que
    jugador_temporada.csv (= el pool de scouting.py + extras).

    ajustado=True: stats del régimen nuevo llevadas a la escala del de
    referencia (ver docstring del módulo). Se cachea en
    jugador_temporada_ajustada.csv y se regenera solo si la base o los
    factores son más nuevos.
    """
    temporadas = [str(t) for t in (temporadas or C._temporadas_disponibles())]
    if not ajustado:
        jt = C.cargar("jugador_temporada")
    else:
        base = os.path.join(C.DIR, "jugador_temporada.csv")
        vencido = (refrescar or not os.path.exists(ARCHIVO_AJUSTADO)
                   or os.path.getmtime(ARCHIVO_AJUSTADO) < os.path.getmtime(base))
        if vencido:
            jt = _armar_ajustado()
        else:
            jt = pd.read_csv(ARCHIVO_AJUSTADO, low_memory=False)
    jt["temporada"] = jt["temporada"].astype(str)
    jt = jt[jt["temporada"].isin(temporadas) & (jt["minutos"] >= min_minutos)]
    return jt.reset_index(drop=True)


def _armar_ajustado():
    factores = factores_regimen(verbose=False)
    partidos = C.cargar("partidos")
    partidos["temporada"] = partidos["temporada"].astype(str)
    equipos = C.cargar("equipos")
    equipos["temporada"] = equipos["temporada"].astype(str)
    frames = []
    for t in C._temporadas_disponibles():
        jp = C.cargar("jugador_partido", t)
        if jp.empty:
            continue
        jp["temporada"] = jp["temporada"].astype(str)
        jp_aj = ajustar_jp(jp, factores)
        jt = C._jugador_temporada(t, jp_aj, partidos[partidos["temporada"] == t],
                                  equipos[equipos["temporada"] == t])
        frames.append(_tasas_solo_medidas(jt, jp_aj, t))
    jt = pd.concat(frames, ignore_index=True)
    jt.to_csv(ARCHIVO_AJUSTADO, index=False)
    return jt


# ──────────────────────────────── percentiles ────────────────────────────────
# Métricas donde MENOS es mejor: el percentil se invierte para que siempre
# "alto = bueno" (pierde poco la pelota = percentil alto).
MENOS_ES_MEJOR = {
    "possession_lost", "dispossessed", "errores_a_remate", "regateado",
    "malos_controles", "fouls", "yellow_cards", "red_cards",
    "big_chances_missed", "duels_lost", "aerial_duels_lost", "offsides",
    "centros_no_atajados", "penales_cometidos", "goles_en_contra",
    "doble_amarilla",
}


def _menos_es_mejor(col):
    base = col
    for suf in ("_p90", "_padj"):
        if base.endswith(suf):
            base = base[: -len(suf)]
    return base in MENOS_ES_MEJOR


def columnas_metricas(pool_df):
    """Columnas candidatas a percentil: tasas, ajustadas por posesión,
    porcentajes y rating."""
    return [c for c in pool_df.columns
            if c.endswith(("_p90", "_padj", "_pct")) or c == "rating"]


def percentiles(pool_df, columnas=None, universo="temporada", min_minutos=600,
                suavizar=True, invertir=True):
    """
    Percentil (0-100), puesto y tamaño del universo de cada métrica, DENTRO
    del rol.

    universo:
      'temporada' → contra los del mismo rol en la MISMA temporada.
      'historico' → contra todas las temporadas-jugador del rol en el pool
                    (muestra más grande; conviene con pool(ajustado=True)).
    min_minutos: quién entra al universo. Los que no llegan igual reciben su
                 percentil (ubicado contra el universo), con `en_universo`=False.
    suavizar: empuja las tasas de muestra chica hacia la mediana del rol
              (scouting.suavizar_p90, K=8 partidos) antes de rankear.
    invertir: en MENOS_ES_MEJOR, percentil alto = hace poco eso.

    Devuelve el pool con, por métrica: `{m}_pct`, `{m}_puesto`, `{m}_de`.
    """
    df = pool_df.copy()
    columnas = [c for c in (columnas or columnas_metricas(df)) if c in df.columns]
    columnas = [c for c in columnas if not c.endswith("_pct") or c in pool_df.columns]
    if suavizar:
        grupos = [df] if universo == "historico" else [g for _, g in df.groupby("temporada")]
        df = pd.concat([SC.suavizar_p90(g) for g in grupos])
    df = df.copy()
    df["en_universo"] = df["minutos"] >= min_minutos
    claves = ["rol"] if universo == "historico" else ["temporada", "rol"]

    nuevas = {}
    for c in columnas:
        pct = pd.Series(np.nan, index=df.index)
        puesto = pd.Series(np.nan, index=df.index)
        de = pd.Series(np.nan, index=df.index)
        signo = -1 if (invertir and _menos_es_mejor(c)) else 1
        for _, g in df.groupby(claves):
            univ = (g.loc[g["en_universo"], c] * signo).dropna().sort_values()
            if univ.empty:
                continue
            vals = (g[c] * signo)
            arr = univ.values
            # percentil: proporción del universo con valor <= al del jugador
            pct.loc[g.index] = [np.searchsorted(arr, v, side="right") / len(arr) * 100
                                if pd.notna(v) else np.nan for v in vals]
            # puesto: 1 + cuántos del universo lo superan
            puesto.loc[g.index] = [len(arr) - np.searchsorted(arr, v, side="right") + 1
                                   if pd.notna(v) else np.nan for v in vals]
            # El que no llega al mínimo de minutos se ubica como si se sumara
            # al universo: "de N+1", nunca "171° de 170".
            de.loc[g.index] = len(arr) + (~g["en_universo"]).astype(int)
        nuevas[f"{c}_pct"] = pct.round(1)
        nuevas[f"{c}_puesto"] = puesto
        nuevas[f"{c}_de"] = de
    salida = pd.concat([df.drop(columns=[k for k in nuevas if k in df.columns]),
                        pd.DataFrame(nuevas)], axis=1)
    salida.attrs["universo"] = universo
    salida.attrs["min_minutos"] = min_minutos
    return salida


def puesto(pct_df, player_id, metrica, temporada=None):
    """'3° de 111 delanteros' para un jugador y métrica de una salida de
    percentiles(). Si el jugador tiene varias filas, toma la temporada pedida
    o la de más minutos."""
    f = pct_df[pct_df["player_id"] == player_id]
    if temporada is not None:
        f = f[f["temporada"].astype(str) == str(temporada)]
    if f.empty or f"{metrica}_puesto" not in f.columns:
        return None
    r = f.sort_values("minutos", ascending=False).iloc[0]
    if pd.isna(r[f"{metrica}_puesto"]):
        return None
    plural = SC._ROL_PLURAL.get(r["rol"], "jugadores")
    p, n = int(r[f"{metrica}_puesto"]), int(r[f"{metrica}_de"])
    alcance = ("de todas las temporadas" if pct_df.attrs.get("universo") == "historico"
               else f"de {r['temporada']}")
    texto = f"{p}° de {n} {plural} {alcance}"
    if not r.get("en_universo", True):
        texto += (f" (muestra chica: {int(r['minutos'])}', el universo es de "
                  f"{pct_df.attrs.get('min_minutos', '?')}'+)")
    return {"nombre": r["nombre"], "temporada": r["temporada"], "equipo": r["equipo_slug"],
            "rol": r["rol"], "valor": r[metrica], "percentil": r[f"{metrica}_pct"],
            "puesto": p, "de": n, "en_universo": bool(r.get("en_universo", True)),
            "texto": texto}


# ─────────────────────────────── jugadores ───────────────────────────────────
def buscar(texto, temporada=None):
    """Jugadores cuyo nombre corto o completo contiene `texto` (sin importar
    mayúsculas ni tildes). `temporada` filtra a los que jugaron ese año."""
    j = C.cargar("jugadores")
    norm = lambda s: config.slugify_equipo(s)
    t = norm(texto)
    en_corto = j["nombre_corto"].map(norm).str.contains(t, regex=False, na=False)
    en_completo = j["nombre_completo"].map(norm).str.contains(t, regex=False, na=False)
    out = j[en_corto | en_completo].copy()
    if temporada is not None:
        jt = C.cargar("jugador_temporada")
        ids = jt[jt["temporada"].astype(str) == str(temporada)]["player_id"]
        out = out[out["player_id"].isin(ids)]
    # Primero los que matchean por el nombre corto (el que se usa en todos
    # lados): "Pacheco" tiene que traer a G. Pacheco antes que a un
    # "Oswaldo Enrique Pacheco Oliveros".
    out["_corto"] = en_corto.loc[out.index]
    return (out.sort_values(["_corto", "minutos_total"], ascending=False)
            .drop(columns="_corto").reset_index(drop=True))


_COLS_HISTORIAL = ["temporada", "equipo_slug", "zona", "rol", "banda", "edad", "pj",
                   "titular_pj", "minutos", "muestra", "pct_minutos_equipo",
                   "pct_minutos_otro_regimen", "goals", "assists", "xg", "npxg", "xa",
                   "key_passes_p90", "rating", "valor_mercado_eur"]


def historial(player_id, ajustado=True):
    """
    Recorrido de un jugador: (bio, tabla temporada por temporada, carrera).
    La carrera suma todas sus temporadas en la categoría (minutos, goles,
    asistencias, xG) y da sus tasas por-90 totales.
    """
    jug = C.cargar("jugadores")
    bio = jug[jug["player_id"] == player_id]
    bio = bio.iloc[0].to_dict() if not bio.empty else {}
    p = pool(ajustado=ajustado)
    filas = p[p["player_id"] == player_id].sort_values("temporada")
    tabla = filas[[c for c in _COLS_HISTORIAL if c in filas.columns]].reset_index(drop=True)
    carrera = {}
    if not filas.empty:
        mins = filas["minutos"].sum()
        carrera = {"temporadas": filas["temporada"].nunique(),
                   "equipos": filas["equipo_slug"].nunique(),
                   "pj": int(filas["pj"].sum()), "minutos": mins}
        for c in ("goals", "assists", "xg", "npxg", "xa", "key_passes",
                  "recuperaciones", "tackles", "interceptions"):
            if c in filas.columns:
                carrera[c] = round(filas[c].sum(), 2)
                carrera[f"{c}_p90"] = round(filas[c].sum() / mins * 90, 3) if mins else np.nan
        carrera["rating"] = (round(np.average(filas["rating"].dropna(),
                                              weights=filas.loc[filas["rating"].notna(), "minutos"]), 2)
                             if filas["rating"].notna().any() else np.nan)
    return bio, tabla, carrera


# ─────────────────── ajuste de cualquier tabla partido a partido ─────────────
def ajustar_tabla(df, fechas, posiciones, columnas, factores=None):
    """
    Aplica los factores de régimen a una tabla con UNA FILA POR JUGADOR Y
    PARTIDO que no viene de la base (ej. los lineups_clean.csv que agrega
    players.player_pool para las pizzas de Chaco).

    fechas, posiciones: secuencias alineadas con df ('YYYY-MM-DD...' y G/D/M/F).
    columnas: {columna_de_df: stat_cruda_de_SofaScore}, ej. {'tackles':
              'totalTackle'}. Las que no tienen factor (goles, asistencias,
              tarjetas) quedan igual.
    """
    if factores is None:
        factores = (pd.read_csv(ARCHIVO_FACTORES) if os.path.exists(ARCHIVO_FACTORES)
                    else factores_regimen(verbose=False))
    if factores.empty:
        return df
    df = df.copy()
    reg = pd.Series([C.regimen_de(f) for f in fechas], index=df.index)
    otro = reg != C.REGIMEN_INICIAL
    if not otro.any():
        return df
    pos = pd.Series(list(posiciones), index=df.index).fillna("?")
    por_pos = factores.set_index(["regimen", "posicion", "metrica"])["factor"]
    glob = factores[factores["posicion"] == "todas"].set_index(["regimen", "metrica"])["factor"]
    con_factor = set(factores["metrica"])
    idx = df.index[otro]
    for col, crudo in columnas.items():
        if col not in df.columns or crudo not in con_factor:
            continue
        f = [por_pos.get((r, p, crudo), glob.get((r, crudo), 1.0))
             for r, p in zip(reg.loc[idx], pos.loc[idx])]
        df.loc[idx, col] = (pd.to_numeric(df.loc[idx, col], errors="coerce")
                            * np.array(f, dtype=float))
    return df


# ──────────────────────── comparables de todas las temporadas ────────────────
def comparables(player_id, temporada=None, temporadas=None, k=10, filtros=None,
                min_minutos=SC.MIN_MINUTOS, metrica="ponderada", rol=None):
    """
    Gemelos estadísticos de un jugador buscando en TODAS las temporadas de la
    base (o las de `temporadas`), con el mismo espacio k-NN de similitud.py:
    features del rol, suavizado, RobustScaler y pesos del scoring model.

    Cada candidato es una (temporada, jugador, equipo): "se parece a cómo
    jugaba X en 2025". El propio jugador no aparece como gemelo de sí mismo en
    otra temporada. Sobre pool(ajustado=True), así 2025 y 2026 son comparables.

    temporada: cuál de las temporadas del jugador tomar como referencia
               (default: la de más minutos).
    filtros:   los de similitud.gemelos (edad_max, minutos_min, valor_max_eur,
               excluir_equipos, banda...) más `temporadas_candidatos` (lista).
    rol:       forzar el rol (default: el del jugador en esa temporada).
    """
    from src.analysis import similitud as SIM

    p = pool(temporadas)
    p = pd.concat([SC.suavizar_p90(g) for _, g in p.groupby("temporada")], ignore_index=True)
    p = SC.scores_compuestos(p)

    filas = p[p["player_id"] == player_id]
    if temporada is not None:
        filas = filas[filas["temporada"] == str(temporada)]
    if filas.empty:
        raise ValueError(f"player_id {player_id} no está en el pool"
                         + (f" de {temporada}" if temporada else "") + ".")
    ref = filas.sort_values("minutos", ascending=False).iloc[0]
    rol = rol or ref["rol"]
    if pd.isna(rol):
        raise ValueError(f"{ref['nombre']} no tiene rol asignado (nunca fue titular).")

    espacio = SIM.espacio_rol(p, rol, min_minutos=min(min_minutos, ref["minutos"]),
                              metrica=metrica)
    d = espacio.df
    hit = d.index[(d["player_id"] == player_id) & (d["temporada"] == ref["temporada"])
                  & (d["team_id"] == ref["team_id"])]
    if len(hit) == 0:
        raise ValueError(f"{ref['nombre']} no entra al espacio del rol {rol}.")
    i = int(hit[0])
    dist, idx = espacio.nn.kneighbors(espacio.X[i].reshape(1, -1), n_neighbors=len(d))
    out = d.iloc[idx[0]].copy()
    out["distancia"] = dist[0]
    out = out[(out["player_id"] != player_id) & (out["minutos"] >= min_minutos)]

    filtros = dict(filtros or {})
    temps = filtros.pop("temporadas_candidatos", None)
    if temps:
        out = out[out["temporada"].isin([str(t) for t in temps])]
    out = SIM._aplicar_filtros(out, filtros)
    out["similitud"] = (100.0 / (1.0 + out["distancia"])).round(1)
    cols = ["temporada", "player_id", "nombre", "equipo_slug", "zona", "rol", "banda",
            "edad", "minutos", "pj", "rating", "score_pct", "valor_mercado_eur",
            "pct_minutos_otro_regimen", "distancia", "similitud"]
    out = out[[c for c in cols if c in out.columns]].head(k).reset_index(drop=True)
    out.attrs["referencia"] = (f"{ref['nombre']} ({ref['equipo_slug']}, {ref['temporada']}, "
                               f"{rol}, {int(ref['minutos'])}')")
    return out


# ─────────────────────────────── Transfermarkt ───────────────────────────────
def _fecha_tm(texto):
    """'06/06/1994 (32)' → Timestamp, o NaT."""
    import re
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", str(texto or ""))
    if not m:
        return pd.NaT
    d, mes, a = (int(x) for x in m.groups())
    return pd.Timestamp(year=a, month=mes, day=d)


def desde_transfermarkt(ficha, verbose=True):
    """
    Busca en la base al jugador de una ficha de Transfermarkt (la que devuelve
    transfermarkt_scraper.fetch_player). Primero por el link ya vinculado; si
    no, por apellido + fecha de nacimiento; si no hay fecha que coincida,
    devuelve los candidatos por apellido para confirmar a mano.

    Devuelve (player_id o None, candidatos DataFrame). Un player_id solo se
    devuelve cuando el match es seguro (link vinculado o apellido + nacimiento).
    """
    jug = C.cargar("jugadores")
    url = ficha.get("url")
    if url and "transfermarkt_url" in jug.columns:
        ya = jug[jug["transfermarkt_url"] == url]
        if not ya.empty:
            return int(ya.iloc[0]["player_id"]), ya

    bio = ficha.get("bio") or {}
    nac = _fecha_tm(bio.get("nacimiento"))
    nombres = [bio.get("nombre"), bio.get("nombre_completo")]
    apellidos = {config.slugify_equipo(n).split("_")[-1] for n in nombres if n}
    norm = lambda s: config.slugify_equipo(s) if isinstance(s, str) else ""
    corto, completo = jug["nombre_corto"].map(norm), jug["nombre_completo"].map(norm)
    mask = pd.Series(False, index=jug.index)
    for a in apellidos:
        mask |= corto.str.contains(a, regex=False) | completo.str.contains(a, regex=False)
    cand = jug[mask].copy()
    if cand.empty:
        if verbose:
            print(f"{bio.get('nombre')}: no aparece en la base (no jugó en Primera Nacional "
                  f"en las temporadas scrapeadas).")
        return None, cand
    cand["nacimiento"] = pd.to_datetime(cand["nacimiento"], errors="coerce")
    cand["misma_fecha"] = (cand["nacimiento"] == nac) if pd.notna(nac) else False
    seguros = cand[cand["misma_fecha"]]
    if len(seguros) == 1:
        return int(seguros.iloc[0]["player_id"]), seguros
    if verbose:
        print(f"{bio.get('nombre')}: {len(cand)} candidatos por apellido, ninguno con la misma "
              f"fecha de nacimiento ({bio.get('nacimiento')}). Confirmá a mano y usá "
              f"vincular_transfermarkt(player_id, url).")
    return None, cand.sort_values("minutos_total", ascending=False)


def vincular_transfermarkt(player_id, url):
    """Guarda el link de Transfermarkt del jugador en jugadores.csv (se
    conserva entre corridas de construir())."""
    path = os.path.join(C.DIR, "jugadores.csv")
    jug = pd.read_csv(path, low_memory=False)
    if player_id not in set(jug["player_id"]):
        raise ValueError(f"player_id {player_id} no está en la base.")
    jug["transfermarkt_url"] = jug["transfermarkt_url"].astype(object)
    jug.loc[jug["player_id"] == player_id, "transfermarkt_url"] = url
    jug.to_csv(path, index=False)


# ─────────────────── chequeo de cambios de medición (fin de año) ─────────────
_STATS_CHEQUEO = ["totalTackle", "wonContest", "totalClearance", "duelLost",
                  "expectedGoals", "totalPass", "touches", "ballRecovery",
                  "interceptionWon", "keyPass", "goals"]


def chequeo_medicion(temporadas=None, umbral=0.25, verbose=True):
    """
    Promedio por equipo y partido de stats sensibles, mes a mes. Marca los
    meses que se apartan más de `umbral` (25%) de la mediana de los 3 meses
    anteriores DENTRO del mismo régimen: así se detecta si SofaScore volvió
    a cambiar la forma de medir (como el 1/7/2026). Un salto sostenido varios
    meses es un corte nuevo para construir.CORTES_REGIMEN; un mes suelto con
    pocos partidos suele ser ruido.
    """
    jp = _jp_todas(temporadas)
    j = jp[(jp["minutos"] > 0) & (jp["nivel_datos"] == "completo")].copy()
    j["mes"] = j["fecha"].str[:7]
    stats = [s for s in _STATS_CHEQUEO if s in j.columns]
    eq = j.groupby(["mes", "regimen", "event_id", "team_id"])[stats].sum()
    m = eq.groupby(["mes", "regimen"]).mean()
    m["partidos"] = eq.reset_index().groupby(["mes", "regimen"])["event_id"].nunique()
    m = m.reset_index()
    alertas = []
    for reg, g in m.groupby("regimen"):
        g = g.sort_values("mes").reset_index(drop=True)
        for i in range(3, len(g)):
            base = g.loc[i - 3:i - 1, stats].median()
            desvio = (g.loc[i, stats] - base) / base.replace(0, np.nan)
            for s, dv in desvio.items():
                if pd.notna(dv) and abs(dv) > umbral and s != "goals":
                    alertas.append({"mes": g.loc[i, "mes"], "regimen": reg, "stat": s,
                                    "partidos": int(g.loc[i, "partidos"]),
                                    "valor": round(g.loc[i, s], 2),
                                    "mediana_3_meses_previos": round(base[s], 2),
                                    "cambio_%": round(dv * 100, 1)})
    alertas = pd.DataFrame(alertas)
    if verbose:
        if alertas.empty:
            print(f"Sin saltos de más de {umbral:.0%} dentro de cada régimen: la medición "
                  f"parece estable.")
        else:
            print("Meses con saltos (revisar si es un cambio de medición de SofaScore):")
            print(alertas.to_string(index=False))
    return m, alertas
