"""
similitud.py
============
Recomendador de jugadores por k-NN: "gemelos estadísticos" dentro de un rol.

Responde la pregunta que aparece en cada mercado de pases: *se me va el 5
titular, ¿quién en la categoría juega parecido y lo puedo pagar?*

Es un EMBUDO DE PRESELECCIÓN, no un decisor. Reduce los ~600 jugadores de la
divisional a una lista corta para que el cuerpo técnico la valide por video: sin
datos de posicionamiento sin balón ni de presión coordinada, ningún modelo
estadístico puede cerrar un fichaje solo.

Pipeline (docs/Criterios.txt):

    métricas p90/PAdj  →  suavizado  →  RobustScaler  →  pesos del rol  →  k-NN

Un modelo POR ROL: comparar un central con un extremo no significa nada, y
trabajar dentro del rol deja ~70-120 filas con ~12 features, que es un espacio
denso y sano.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import RobustScaler

from src.analysis import scouting as SC


# Features por rol: 11-13 cada uno, mezclando volumen (p90/PAdj) con eficiencia
# (porcentajes). Se apoyan en los pesos de PESOS_SCORE pero son más amplias: el
# score mide "qué tan bueno", la similitud mide "de qué manera juega".
FEATURES_ROL = {
    "DFC": [
        "duelos_aereos_pct", "duelos_terrestres_pct", "aerial_duels_won_p90",
        "clearances_padj", "interceptions_padj", "tackles_padj", "bloqueos_padj",
        "recuperaciones_padj", "accurate_passes_p90", "pase_pct",
        "pase_campo_rival_pct", "accurate_long_balls_p90", "touches_p90",
    ],
    "LAT": [
        "duelos_terrestres_pct", "duelos_aereos_pct", "tackles_padj",
        "interceptions_padj", "recuperaciones_padj", "accurate_crosses_p90",
        "centro_pct", "key_passes_p90", "dribbles_won_p90", "regate_pct",
        "accurate_passes_p90", "pase_pct", "touches_p90",
    ],
    "MCD": [
        "recuperaciones_padj", "interceptions_padj", "tackles_padj",
        "duelos_terrestres_pct", "duelos_aereos_pct", "accurate_passes_p90",
        "pase_pct", "pase_campo_propio_pct", "pase_campo_rival_pct",
        "key_passes_p90", "touches_p90", "possession_lost_p90", "fouls_p90",
    ],
    "MC": [
        "accurate_passes_p90", "pase_pct", "pase_campo_rival_pct",
        "key_passes_p90", "xa_p90", "dribbles_won_p90", "regate_pct",
        "tackles_padj", "interceptions_padj", "recuperaciones_padj",
        "touches_p90", "xg_p90", "possession_lost_p90",
    ],
    "EXT_MP": [
        "key_passes_p90", "xa_p90", "assists_p90", "dribbles_won_p90",
        "regate_pct", "accurate_crosses_p90", "centro_pct",
        "shots_on_target_p90", "xg_p90", "goals_p90", "touches_p90",
        "duelos_terrestres_pct", "possession_lost_p90",
    ],
    "DC": [
        "goals_p90", "xg_p90", "shots_total_p90", "shots_on_target_p90",
        "conversion_pct", "aerial_duels_won_p90", "duelos_aereos_pct",
        "key_passes_p90", "xa_p90", "assists_p90", "touches_p90",
        "duelos_terrestres_pct", "dribbles_won_p90",
    ],
}


def pesos_de_features(rol):
    """
    Peso de cada feature del rol, derivado de los pesos del scoring model (§3).

    Es la alternativa que propone Criterios.txt a hacer PCA: si el rol pondera
    seis métricas defensivas, se reparte ese 30% entre ellas en vez de dejar que
    sumen seis veces. Resuelve la redundancia igual que el PCA pero sin perder
    la interpretabilidad, que acá es el producto —hay que poder decirle al DT
    "se parece porque gana los mismos duelos y saca la pelota igual".

    Las features que no entran en ningún componente del score reciben el peso
    mínimo del rol, para que aporten sin dominar.
    """
    features = FEATURES_ROL.get(rol, [])
    componentes = SC.PESOS_SCORE.get(rol, {})
    pesos = {}
    for _, (peso, metricas) in componentes.items():
        cuota = peso / max(len(metricas), 1)
        for m in metricas:
            pesos[m] = pesos.get(m, 0.0) + cuota
    if not pesos:
        return {f: 1.0 for f in features}
    piso = min(pesos.values()) if pesos else 0.05
    return {f: pesos.get(f, piso) for f in features}


@dataclass
class EspacioRol:
    """Espacio vectorial de un rol, listo para consultar vecinos."""
    rol: str
    df: pd.DataFrame
    X: np.ndarray
    features: list
    metrica: str
    scaler: object = None
    pca: object = None
    nn: object = None
    _vi: np.ndarray = field(default=None, repr=False)

    def __len__(self):
        return len(self.df)


def espacio_rol(pool, rol, min_minutos=SC.MIN_MINUTOS, metrica="ponderada",
                usar_pca=False, varianza_pca=0.85):
    """
    Arma el espacio de comparación de un rol.

    `metrica`:
      - "ponderada"   (default) euclídea sobre features escaladas y ponderadas
                      por el scoring model del rol.
      - "euclidiana"  sin ponderar, todas las features pesan igual.
      - "mahalanobis" incorpora la matriz de covarianza (Ledoit-Wolf, que la
                      hace estable con n≈70-120) para neutralizar la redundancia
                      de forma automática.

    `usar_pca` está disponible pero NO es el default: con 12 features,
    PCA(0.85) retiene 5-6 componentes —apenas comprime— y como sin whitening es
    solo una rotación, las listas de vecinos salen casi idénticas. Cuesta
    interpretabilidad y no compra nada. Sí se usa para el mapa 2D (`mapa_rol`).
    """
    features = [f for f in FEATURES_ROL.get(rol, []) if f in pool.columns]
    if not features:
        raise ValueError(f"El rol {rol!r} no tiene features definidas.")

    d = pool[(pool["rol"] == rol) & (pool["minutos"] >= min_minutos)].copy()
    if d.empty:
        raise ValueError(f"No hay jugadores en el rol {rol!r}.")

    X = d[features].astype(float)
    X = X.fillna(X.median())            # imputa con la mediana del propio rol

    scaler = RobustScaler()             # mediana + IQR: aguanta los outliers
    Xs = scaler.fit_transform(X)        # que en esta categoría son reales

    pca = None
    if usar_pca:
        pca = PCA(n_components=varianza_pca, random_state=42)
        Xs = pca.fit_transform(Xs)

    vi = None
    if metrica == "ponderada" and not usar_pca:
        pesos = pesos_de_features(rol)
        # Escalar cada eje por sqrt(peso) hace que la euclídea sobre la matriz
        # resultante sea exactamente la distancia ponderada.
        w = np.sqrt(np.array([pesos.get(f, 0.05) for f in features], dtype=float))
        Xs = Xs * w
        nn = NearestNeighbors(metric="euclidean")
    elif metrica == "mahalanobis":
        cov = LedoitWolf().fit(Xs)
        vi = np.linalg.pinv(cov.covariance_)
        nn = NearestNeighbors(metric="mahalanobis", metric_params={"VI": vi},
                              algorithm="brute")
    else:
        nn = NearestNeighbors(metric="euclidean")

    nn.fit(Xs)
    return EspacioRol(rol=rol, df=d.reset_index(drop=True), X=Xs,
                      features=features, metrica=metrica, scaler=scaler,
                      pca=pca, nn=nn, _vi=vi)


def _fila_del_jugador(espacio, player_id=None, nombre=None):
    """Índice posicional del jugador dentro del espacio. Avisa si el nombre es
    ambiguo: `nombre` es el shortName de SofaScore y hay homónimos."""
    d = espacio.df
    if player_id is not None:
        hit = d.index[d["player_id"] == int(player_id)]
        if len(hit) == 0:
            raise ValueError(f"player_id {player_id} no está en el rol {espacio.rol}.")
        if len(hit) > 1:
            # Jugador transferido a mitad de temporada: una fila por club
            # (ver _agregar_por_jugador). Se queda con el club de más minutos.
            hit = [d.loc[hit, "minutos"].idxmax()]
        return int(hit[0])
    if nombre is None:
        raise ValueError("Hay que pasar player_id o nombre.")
    hit = d.index[d["nombre"].astype(str).str.strip().str.lower()
                  == str(nombre).strip().lower()]
    if len(hit) == 0:
        raise ValueError(f"{nombre!r} no está en el rol {espacio.rol} "
                         f"(¿tiene los minutos mínimos?).")
    if len(hit) > 1:
        equipos = ", ".join(d.loc[hit, "equipo"].astype(str))
        raise ValueError(f"{nombre!r} matchea {len(hit)} jugadores ({equipos}). "
                         f"Usá player_id.")
    return int(hit[0])


_COLS_SALIDA = ["player_id", "nombre", "equipo", "zona", "banda", "edad",
                "minutos", "pj", "rating", "score_rol", "score_pct",
                "valor_mercado_eur", "pos_tabla", "posesion", "muestra_chica"]


def gemelos(espacio, player_id=None, nombre=None, k=10, filtros=None,
            excluir_mismo_equipo=False):
    """
    Los k jugadores más parecidos del rol, ordenados por similitud.

    `filtros` (dict, todos opcionales) se aplican DESPUÉS de calcular las
    distancias, nunca antes: si filtrás primero, el vecino más parecido puede
    quedar afuera del subconjunto y el ranking pierde sentido.
        edad_max, edad_min, minutos_min, pj_min, valor_max_eur,
        excluir_equipos (lista), solo_equipos (lista), pos_tabla_desde

    `similitud` = 100 / (1 + distancia), para que se lea de un vistazo.
    """
    i = _fila_del_jugador(espacio, player_id, nombre)
    d = espacio.df

    dist, idx = espacio.nn.kneighbors(espacio.X[i].reshape(1, -1),
                                      n_neighbors=len(d))
    orden = [(j, dd) for j, dd in zip(idx[0], dist[0]) if j != i]

    out = d.iloc[[j for j, _ in orden]].copy()
    out["distancia"] = [dd for _, dd in orden]

    if excluir_mismo_equipo:
        out = out[out["team_id"] != d.at[i, "team_id"]]
    out = _aplicar_filtros(out, filtros)

    out["similitud"] = (100.0 / (1.0 + out["distancia"])).round(1)
    cols = [c for c in _COLS_SALIDA if c in out.columns] + ["distancia", "similitud"]
    return out[cols].head(k).reset_index(drop=True)


def _aplicar_filtros(df, filtros):
    if not filtros:
        return df
    f = filtros
    if f.get("edad_max") is not None:
        df = df[df["edad"].notna() & (df["edad"] <= f["edad_max"])]
    if f.get("edad_min") is not None:
        df = df[df["edad"].notna() & (df["edad"] >= f["edad_min"])]
    if f.get("minutos_min") is not None:
        df = df[df["minutos"] >= f["minutos_min"]]
    if f.get("pj_min") is not None:
        df = df[df["pj"] >= f["pj_min"]]
    if f.get("valor_max_eur") is not None:
        df = df[df["valor_mercado_eur"].notna()
                & (df["valor_mercado_eur"] <= f["valor_max_eur"])]
    if f.get("excluir_equipos"):
        df = df[~df["equipo"].isin(f["excluir_equipos"])]
    if f.get("solo_equipos"):
        df = df[df["equipo"].isin(f["solo_equipos"])]
    if f.get("pos_tabla_desde") is not None:
        df = df[df["pos_tabla"].notna()
                & (df["pos_tabla"] >= f["pos_tabla_desde"])]
    if f.get("banda") and "banda" in df.columns:
        # "ambas" siempre entra: un polivalente cubre cualquiera de los dos
        # carriles, así que no hay razón para descartarlo.
        df = df[df["banda"].isin([f["banda"], "ambas"])]
    return df


# ───────────────────────── terna de fichajes (§5) ────────────────────────────
_METRICAS_DESEQUILIBRIO = {
    "DFC":    ["duelos_aereos_pct", "interceptions_padj"],
    "LAT":    ["regate_pct", "accurate_crosses_p90"],
    "MCD":    ["recuperaciones_padj", "pase_pct"],
    "MC":     ["key_passes_p90", "dribbles_won_p90"],
    "EXT_MP": ["dribbles_won_p90", "key_passes_p90"],
    "DC":     ["goals_p90", "duelos_aereos_pct"],
}


def terna_fichajes(espacio, pool, player_id=None, nombre=None, k_pool=40):
    """
    Tres alternativas por puesto (§5), buscadas ENTRE LOS GEMELOS y no sobre
    toda la liga —que es la mejora que propone Criterios.txt sobre el filtro
    rígido por percentiles: dos jugadores con el mismo índice pueden jugar de
    formas completamente distintas.

      - `top_performer`: rendimiento probado (score_pct >= 80, pj >= 20)
      - `moneyball`:     score_pct >= 70 en un equipo de la mitad de abajo,
                         ordenado por valor de mercado ascendente
      - `apuesta`:       <= 23 años, score_pct >= 65, y top 10% del rol en
                         alguna métrica de desequilibrio

    Si un perfil queda vacío devuelve un DataFrame con una columna `nota` que
    dice qué filtro no encontró a nadie: fallar en silencio acá es peor.
    """
    i = _fila_del_jugador(espacio, player_id, nombre)
    banda = espacio.df.iloc[i].get("banda")
    filtros = {"banda": banda} if banda in ("IZQ", "DER") else None
    cand = gemelos(espacio, player_id=player_id, nombre=nombre, k=k_pool,
                   excluir_mismo_equipo=True, filtros=filtros)
    rol = espacio.rol
    del_rol = pool[pool["rol"] == rol]

    # Corte de "mitad de abajo" por zona, no global: las dos zonas tienen tablas
    # separadas y distinta cantidad de equipos.
    mitad = del_rol.groupby("zona")["pos_tabla"].median().to_dict()

    def vacio(nota):
        return pd.DataFrame({"nota": [nota]})

    top = cand[(cand["score_pct"] >= 80) & (cand["pj"] >= 20)]
    top = top if not top.empty else vacio(
        "Ningún gemelo llega a score_pct >= 80 con 20+ partidos.")

    zona_mitad = cand["zona"].map(mitad)
    money = cand[(cand["score_pct"] >= 70) & cand["pos_tabla"].notna()
                 & (cand["pos_tabla"] >= zona_mitad)]
    money = (money.sort_values("valor_mercado_eur", na_position="last")
             if not money.empty else
             vacio("Ningún gemelo con score_pct >= 70 juega en la mitad de abajo."))

    # El desequilibrio ORDENA, no filtra. Pedirlo como condición dura además de
    # sub-23 y percentil 65 dejaba el perfil vacío en casi todos los puestos:
    # sobre ~40 vecinos, la intersección de las tres condiciones casi nunca
    # existe. Así el perfil siempre devuelve algo y la columna `desequilibrio`
    # marca a los que además tienen una cualidad en el top 10% del puesto.
    destacadas = {}
    for m in _METRICAS_DESEQUILIBRIO.get(rol, []):
        if m not in del_rol.columns:
            continue
        umbral = del_rol[m].quantile(0.90)
        for pid in del_rol.loc[del_rol[m] >= umbral, "player_id"]:
            destacadas.setdefault(pid, []).append(_etiqueta(m))

    apuesta = cand[cand["edad"].notna() & (cand["edad"] <= 23)
                   & (cand["score_pct"] >= 65)].copy()
    if apuesta.empty:
        apuesta = vacio("Ningún gemelo sub-23 llega al percentil 65 del puesto.")
    else:
        apuesta["desequilibrio"] = [", ".join(destacadas.get(p, []))
                                    for p in apuesta["player_id"]]
        apuesta = apuesta.sort_values(
            ["desequilibrio", "similitud"],
            ascending=[False, False], key=lambda s: s.str.len()
            if s.name == "desequilibrio" else s)

    return {"top_performer": top.reset_index(drop=True),
            "moneyball": money.reset_index(drop=True),
            "apuesta": apuesta.reset_index(drop=True)}


def mejoras(espacio, pool, player_id=None, nombre=None, k=8,
            margen_pct=15, respetar_banda=True, filtros=None,
            incluir_mismo_equipo=False):
    """
    Los mejores del puesto que además superan al jugador actual — el modo a usar
    cuando el titular es FLOJO.

    Buscar un gemelo sirve para reemplazar a alguien bueno que se va. Para
    mejorar un puesto malo es el enfoque equivocado: si el perfil del titular es
    el perfil mediocre del puesto, sus vecinos también van a serlo, y fichar un
    clon es un movimiento lateral. Acá se rankea por `score_rol` y la similitud
    queda como dato secundario: mide qué tan parecido es el reemplazo, o sea qué
    tan fácil es meterlo sin cambiar el funcionamiento del equipo.

    `margen_pct`: cuántos puntos de percentil tiene que sacarle al actual para
    considerarse una mejora real y no ruido de medición.

    `respetar_banda`: en LAT y EXT_MP filtra por el carril del jugador actual.
    Sin esto se proponen laterales derechos para reemplazar a un izquierdo.
    """
    i = _fila_del_jugador(espacio, player_id, nombre)
    d = espacio.df
    actual = d.iloc[i]

    dist, idx = espacio.nn.kneighbors(espacio.X[i].reshape(1, -1),
                                      n_neighbors=len(d))
    distancias = dict(zip(idx[0], dist[0]))

    cand = d.drop(index=i).copy()
    cand["distancia"] = [distancias.get(j, np.nan) for j in cand.index]
    cand["similitud"] = (100.0 / (1.0 + cand["distancia"])).round(1)

    if not incluir_mismo_equipo:
        cand = cand[cand["team_id"] != actual["team_id"]]

    if respetar_banda and actual.get("banda") in ("IZQ", "DER"):
        cand = _aplicar_filtros(cand, {"banda": actual["banda"]})
    cand = _aplicar_filtros(cand, filtros)

    piso = (actual["score_pct"] or 0) + margen_pct
    cand = cand[cand["score_pct"] >= piso]
    cand["delta_pct"] = (cand["score_pct"] - actual["score_pct"]).round(1)

    cols = ([c for c in _COLS_SALIDA if c in cand.columns]
            + ["delta_pct", "similitud"])
    return (cand.sort_values("score_rol", ascending=False)[cols]
            .head(k).reset_index(drop=True))


def diagnostico(pool, rol, player_id=None, nombre=None, n_peores=4):
    """
    En qué componentes del índice del puesto pierde el jugador.

    Devuelve un DataFrame componente / peso / percentil, ordenado de peor a
    mejor: es lo que dice QUÉ hay que ir a buscar en el mercado, en vez de
    "conseguir uno mejor".
    """
    d = pool[pool["rol"] == rol]
    fila = (d[d["player_id"] == int(player_id)] if player_id is not None
            else d[d["nombre"].astype(str).str.strip().str.lower()
                   == str(nombre).strip().lower()])
    if fila.empty:
        return None
    fila = fila.iloc[0]

    filas = []
    for comp, (peso, metricas) in SC.PESOS_SCORE.get(rol, {}).items():
        vals = [fila.get(f"{m}_pct") for m in metricas
                if f"{m}_pct" in d.columns and pd.notna(fila.get(f"{m}_pct"))]
        if not vals:
            continue
        filas.append({"componente": comp, "peso": peso,
                      "percentil": round(float(np.mean(vals)), 1),
                      "metricas": ", ".join(_etiqueta(m) for m in metricas)})
    out = pd.DataFrame(filas).sort_values("percentil")
    out.attrs["n_peores"] = n_peores
    return out.reset_index(drop=True)


def mapa_rol(espacio, n_componentes=2):
    """Proyección 2D del rol para graficar. Acá el PCA sí aporta: es la forma
    natural de ver dónde cae cada jugador y detectar roles mal asignados."""
    pca = PCA(n_components=n_componentes, random_state=42)
    coords = pca.fit_transform(espacio.X)
    out = espacio.df[[c for c in _COLS_SALIDA if c in espacio.df.columns]].copy()
    for i in range(n_componentes):
        out[f"pc{i + 1}"] = coords[:, i]
    # Como tupla y no como array de numpy: pandas compara los `attrs` al
    # concatenar, y un array ahí rompe cualquier concat/nlargest posterior.
    out.attrs["varianza"] = tuple(round(float(v), 4)
                                  for v in pca.explained_variance_ratio_)
    return out


def comparacion_desde_pool(pool, rol, player_id_a, player_id_b, etiquetas=None):
    """
    Arma el dict que consume `visualization.players.plot_players_radar`, pero
    con las features del rol en vez de las 12 fijas de PIZZA_METRICS.

    Los rangos de los ejes son los percentiles 5-95 del rol, para que el radar
    se lea contra la demarcación y no contra toda la liga.
    """
    d = pool[pool["rol"] == rol]
    features = [f for f in FEATURES_ROL.get(rol, []) if f in d.columns]
    fa = d[d["player_id"] == int(player_id_a)]
    fb = d[d["player_id"] == int(player_id_b)]
    if fa.empty or fb.empty:
        return None
    fa, fb = fa.iloc[0], fb.iloc[0]

    etiquetas = etiquetas or {}
    labels, va, vb, ranges = [], [], [], []
    for f in features:
        labels.append(etiquetas.get(f, _etiqueta(f)))
        va.append(float(fa[f]) if pd.notna(fa[f]) else 0.0)
        vb.append(float(fb[f]) if pd.notna(fb[f]) else 0.0)
        lo, hi = float(d[f].quantile(0.05)), float(d[f].quantile(0.95))
        ranges.append((lo, hi if hi > lo else lo + 1e-6))

    return {"labels": labels, "values_a": va, "values_b": vb, "ranges": ranges,
            "player_a": fa["nombre"], "player_b": fb["nombre"]}


_ETIQUETAS = {
    "duelos_aereos_pct": "Duelo aéreo %", "duelos_terrestres_pct": "Duelo suelo %",
    "aerial_duels_won_p90": "Aéreos ganados", "clearances_padj": "Despejes",
    "interceptions_padj": "Intercepciones", "tackles_padj": "Quites",
    "bloqueos_padj": "Bloqueos", "recuperaciones_padj": "Recuperaciones",
    "accurate_passes_p90": "Pases precisos", "pase_pct": "Pase %",
    "pase_campo_rival_pct": "Pase campo rival %", "pase_campo_propio_pct": "Pase campo propio %",
    "accurate_long_balls_p90": "Pelotas largas", "touches_p90": "Toques",
    "accurate_crosses_p90": "Centros precisos", "centro_pct": "Centro %",
    "key_passes_p90": "Pases clave", "dribbles_won_p90": "Regates ganados",
    "regate_pct": "Regate %", "xa_p90": "xA", "xg_p90": "xG",
    "assists_p90": "Asistencias", "goals_p90": "Goles",
    "shots_on_target_p90": "Tiros al arco", "shots_total_p90": "Tiros",
    "conversion_pct": "Conversión %", "possession_lost_p90": "Pérdidas",
    "fouls_p90": "Faltas",
    "npxg_p90": "npxG", "xgot_p90": "xGOT", "goles_sin_penal_p90": "Goles sin penal",
    "npxg_por_remate": "npxG por remate", "remates_cabeza_p90": "Remates de cabeza",
    "remates_pelota_parada_p90": "Remates de pelota parada",
    "remates_cabeza_pct": "Remates de cabeza %",
    "remates_pelota_parada_pct": "Remates de pelota parada %",
    "dribbles_attempted_p90": "Regates intentados", "regateado_p90": "Veces regateado",
    "regates_frenados_pct": "Regates frenados %", "malos_controles_p90": "Malos controles",
    "penales_provocados": "Penales provocados", "penales_cometidos": "Penales cometidos",
    "penales_errados": "Penales errados", "despejes_en_linea": "Despejes en la línea",
    "tiros_al_palo": "Tiros al palo", "atajadas_dentro_area_p90": "Atajadas dentro del área",
    "atajadas_dentro_area_pct": "Atajadas dentro del área %",
    "km_recorridos_p90": "Km recorridos", "sprints_p90": "Sprints",
}


def _etiqueta(col):
    return _ETIQUETAS.get(col, col.replace("_p90", "").replace("_padj", "")
                          .replace("_", " ").capitalize())
