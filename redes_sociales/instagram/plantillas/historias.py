# -*- coding: utf-8 -*-
"""
PLANTILLA: historias de Instagram (9:16) de un partido. Tema oscuro.

Dos clases de placa:
  - AUTOMÁTICAS: salen solas del partido (MATCH_KEY) -> ratings, shotmap, stats.
  - A MANO: las completás en DATOS cada fecha -> salvados, combinacion, tramos,
    goles_empate, segundo_tiempo (este último es automático también).

ORDEN define cuáles se generan y en qué orden. Las historias salen numeradas con el
nombre de la placa: 01_ratings.png, 02_shotmap.png, ...

Para crear una nueva:   python ig.py nuevo historias f34_rival
Para generarla:         python ig.py historias f34_rival

Claves de DATOS:
    match_key, season, fecha, rival                       (siempre)
    [nota], [carpeta] (nombre de la carpeta de salida), [tema] ('oscuro' default | 'hueso')
  Para una PREVIA no hace falta match_key: solo valen las placas a mano y las genéricas.
  genéricas ("tipo:prefijo", como en el carrusel):
    comparativa:p  p_titulo, p_sub, p_filas [(etiqueta, chaco, rival[, fracción 0-1])],
                   [p_local, p_rival]   (la fracción se calcula sola de los números)
    tarjetas:p     p_titulo [(texto, 'acento'|'tinta')], p_sub, p_lista [(titulo, detalle,
                   escudo[, badge])], [p_resultado, p_pie, p_kicker]
    barras:p       p_titulo p_filas [(nombre, valor)] [p_sub p_unidad p_destacar p_piso]
    matriz:p       p_titulo [(texto,color)], p_sub, p_cols [..], p_filas [(etiqueta,
                   [(texto,'si'|'cond'|'no'), ...])], [p_col_titulo, p_pie, p_kicker]
    grafico:p      p_ruta, [p_titulo, p_sub]   (png de cancha ya generado, en 9:16)
  salvados:       salvados_titulo [(texto, 'acento'|'tinta'), ...], salvados_sub,
                  salvados_lista [(equipo, escudo, detalle)], salvados_pie
  combinacion:    combinacion_titulo, combinacion_sub, combinacion_lista
                  [(titulo, detalle, escudo)], combinacion_resultado, combinacion_pie
  tramos:         tramos_titulo, tramos_sub, tramos_lista [{rango,nombre,desde,hasta,
                  eventos,[destacar]}], tramos_resultado, tramos_pie, [area_x]
  goles_empate:   goles_empate_titulo, goles_empate_sub, goles_empate_lista
                  [(titulo, detalle, escudo, badge)], goles_empate_resultado
"""
import re
from pathlib import Path

from plantillas import base as B

TIPO = "historias"
TEMA = "oscuro"

ORDEN = ["ratings", "shotmap", "stats", "salvados", "combinacion"]
# También disponibles: "tramos", "segundo_tiempo", "goles_empate"

AREA_X = 15     # coord_x <= 15 = dentro del área (coincide con "Shots inside box" de SofaScore)


def contexto(d):
    return {"fecha": d["fecha"], "rival": d["rival"], "rival_corto": d["rival"]}


def _titulo(partes):
    """[('TEXTO', 'acento'|'tinta'), ...] -> colores del tema ACTUAL."""
    colores = {"acento": B.P.DORADO, "tinta": B.P.TINTA}
    return [(t, colores[c]) for t, c in partes]


def _match_dir(d):
    import config
    return Path(config.season_data_dir(d["season"])) / d["match_key"]


# ---------------------------------------------------------------- automáticas
def _ratings(d, cx):
    import pandas as pd
    from src.analysis.season import is_home_match
    lin = pd.read_csv(_match_dir(d) / "lineups_clean.csv")
    side = "home" if is_home_match(d["match_key"]) else "away"
    ch = lin[lin["team_side"] == side].copy()
    ch["rating"] = pd.to_numeric(ch["rating"], errors="coerce")
    ch = ch.dropna(subset=["rating"]).sort_values("rating", ascending=False)
    filas = [(r["player_name"], round(float(r["rating"]), 1)) for _, r in ch.iterrows()]
    return B.P.ranking_historia(
        "Ratings del Partido", filas,
        subtitulo=f"Chaco For Ever vs {d['rival']} · todo el plantel que jugó",
        nota=cx["nota"], destacar=0, piso=4.0)


def _shotmap(d, cx):
    import graficos_partido_marca as G
    save = B.ASSETS / "partido" / "shotmap_historia_ig.png"
    G.shotmap_historia(d["match_key"], d["season"], save)
    return B.P.grafico_marca_historia(
        str(save), "Mapa de Tiros",
        subtitulo=f"Chaco For Ever vs {d['rival']} · por tipo de remate",
        nota="Fuente: SofaScore")


def _stats(d, cx):
    import pandas as pd
    from src.analysis.season import is_home_match
    from src.visualization.season import _STATS_ORDER, _STATS_ES, _fmt_stat
    st = pd.read_csv(_match_dir(d) / "statistics_clean.csv")
    st = st[st["metric"].isin(_STATS_ORDER)].drop_duplicates(subset="metric", keep="first")
    st = st.set_index("metric")
    home = is_home_match(d["match_key"])
    filas = []
    for metric in _STATS_ORDER:
        if metric not in st.index:
            continue
        row = st.loc[metric]
        h = float(pd.to_numeric(row["home_val"], errors="coerce") or 0)
        a = float(pd.to_numeric(row["away_val"], errors="coerce") or 0)
        chaco_val, rival_val = (h, a) if home else (a, h)
        total = chaco_val + rival_val
        frac = 0.5 if total == 0 else chaco_val / total
        filas.append((_STATS_ES.get(metric, metric),
                      _fmt_stat(metric, chaco_val), _fmt_stat(metric, rival_val), frac))
    return B.P.comparacion_historia(
        "Resumen del Partido", f"Chaco For Ever vs {d['rival']}",
        filas, home_label="Chaco For Ever", away_label=d["rival"], nota=cx["nota"])


def _shots_chaco(d):
    """Shotmap del partido con la columna 'chaco' (True = remate de Chaco)."""
    import pandas as pd
    from src.analysis.season import is_home_match
    sm = pd.read_csv(_match_dir(d) / "shotmap_clean.csv")
    sm["chaco"] = sm["isHome"] == is_home_match(d["match_key"])
    sm["area"] = sm["coord_x"] <= d.get("area_x", AREA_X)
    return sm


def _segundo_tiempo(d, cx):
    sm = _shots_chaco(d)
    st = sm[sm["time"] > 45]
    c, r = st[st.chaco], st[~st.chaco]

    def par(vc, vr, fmt):
        tot = vc + vr
        return (fmt.format(vc), fmt.format(vr), 0.5 if tot == 0 else vc / tot)

    filas = [
        ("Goles", *par(int((c.shotType == "goal").sum()), int((r.shotType == "goal").sum()), "{:.0f}")),
        ("Goles esperados (xG)", *par(c.xg.sum(), r.xg.sum(), "{:.2f}")),
        ("Remates", *par(len(c), len(r), "{:.0f}")),
        ("Remates al arco", *par(int(c.xgot.notna().sum()), int(r.xgot.notna().sum()), "{:.0f}")),
        ("Remates dentro del área", *par(int(c.area.sum()), int(r.area.sum()), "{:.0f}")),
        ("xG por remate", *par(c.xg.mean(), r.xg.mean(), "{:.2f}")),
        ("xGOT (calidad de los remates al arco)", *par(c.xgot.sum(), r.xgot.sum(), "{:.2f}")),
    ]
    return B.P.comparacion_historia(
        "El segundo tiempo en números",
        f"Chaco For Ever vs {d['rival']} · del 46' al final",
        filas, home_label="Chaco For Ever", away_label=d["rival"], nota=cx["nota"])


def _tramos(d, cx):
    sm = _shots_chaco(d)
    tramos = []
    for t in d["tramos_lista"]:
        w = (sm[(sm["time"] > t["desde"]) & (sm["time"] <= t["hasta"])] if t["desde"]
             else sm[sm["time"] <= t["hasta"]])
        tramos.append(dict(t, xg=(round(w.loc[w.chaco, "xg"].sum(), 2),
                                  round(w.loc[~w.chaco, "xg"].sum(), 2))))
    return B.P.tramos_historia(
        _titulo(d["tramos_titulo"]), d["tramos_sub"], tramos,
        resultado_texto=d["tramos_resultado"], pie_texto=d.get("tramos_pie", ""),
        nota=cx["nota"], kicker="EL PARTIDO")


# ------------------------------------------------------------------- a mano
def _salvados(d, cx):
    return B.P.salvados_historia(
        _titulo(d["salvados_titulo"]), d["salvados_sub"],
        [(n, str(e), det) for n, e, det in d["salvados_lista"]],
        pie_texto=d.get("salvados_pie", ""),
        nota=f"Fecha {d['fecha']} · {B.COMPETENCIA}")


def _combinacion(d, cx):
    return B.P.combinacion_historia(
        _titulo(d["combinacion_titulo"]), d["combinacion_sub"],
        [(t, dtl, str(e)) for t, dtl, e in d["combinacion_lista"]],
        resultado_texto=d["combinacion_resultado"], pie_texto=d.get("combinacion_pie", ""),
        nota=f"Fecha {d['fecha']} · {B.COMPETENCIA}")


def _goles_empate(d, cx):
    return B.P.combinacion_historia(
        _titulo(d["goles_empate_titulo"]), d["goles_empate_sub"],
        [(t, dtl, str(e), b) for t, dtl, e, b in d["goles_empate_lista"]],
        resultado_texto=d["goles_empate_resultado"], nota=cx["nota"], kicker="EL EMPATE")


# ----------------------------------------------------------------- genéricas
def _num(s):
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(s))
    return float(m.group(0).replace(",", ".")) if m else 0.0


def _comparativa(p, d, cx):
    filas = []
    for f in B._req(d, p, "filas"):
        etq, a, b = f[:3]
        tot = _num(a) + _num(b)
        frac = f[3] if len(f) > 3 else (0.5 if tot == 0 else _num(a) / tot)
        filas.append((etq, str(a), str(b), frac))
    return B.P.comparacion_historia(
        B._req(d, p, "titulo"), B._opc(d, p, "sub", ""), filas,
        home_label=B._opc(d, p, "local", "Chaco For Ever"),
        away_label=B._opc(d, p, "rival", d["rival"]), nota=cx["nota"])


def _tarjetas(p, d, cx):
    lista = [tuple(str(x) if i == 2 else x for i, x in enumerate(it))
             for it in B._req(d, p, "lista")]
    return B.P.combinacion_historia(
        _titulo(B._req(d, p, "titulo")), B._opc(d, p, "sub", ""), lista,
        resultado_texto=B._opc(d, p, "resultado", ""), pie_texto=B._opc(d, p, "pie", ""),
        nota=cx["nota"], kicker=B._opc(d, p, "kicker", "EL PARTIDO"))


def _grafico_historia(p, d, cx):
    r = B.ruta(B._req(d, p, "ruta"))
    if not r:
        raise B.Falta(f"{p}_ruta (no existe el archivo: {d.get(p + '_ruta')})")
    return B.P.grafico_marca_historia(r, B._opc(d, p, "titulo", ""), B._opc(d, p, "sub", ""),
                                      nota="Fuente: SofaScore")


def _matriz(p, d, cx):
    """Tabla de posibilidades: filas = lo que hace Chaco, columnas = lo que hace otro
    equipo. Cada celda = (texto, estado) con estado 'si' (dorado lleno), 'cond' (borde
    dorado) o 'no' (apagada)."""
    P, M = B.P, B.M
    titulo, filas = B._req(d, p, "titulo", "filas")
    cols = B._req(d, p, "cols")
    img, dr = M.lienzo(P.NEGRO, tam=(P.W_HISTORIA, P.H_HISTORIA))
    M.cabecera(dr, kicker=B._opc(d, p, "kicker", "LAS POSIBILIDADES"))
    y = 215
    for linea, color in _titulo(titulo):
        M.texto(dr, (P.MARGEN, y), linea, P.F_BLACK, 72, fill=color)
        y += 88
    M.texto(dr, (P.MARGEN, y + 10), B._opc(d, p, "sub", ""), P.F_REG, 30, fill=P.GRIS)
    M.linea_dorada(dr, P.MARGEN, y + 68, largo=120, grosor=6)

    x0, x1 = P.MARGEN, P.W_HISTORIA - P.MARGEN
    lw, gap = 210, 14
    cw = (x1 - x0 - lw - gap * len(cols)) / len(cols)
    yh = y + 150
    M.texto(dr, (x0 + lw + gap + (x1 - x0 - lw - gap) / 2, yh - 52),
            B._opc(d, p, "col_titulo", "").upper(), P.F_SEMI, 24, fill=P.GRIS,
            anchor="mm", tracking=2)
    for j, c in enumerate(cols):
        cx_ = x0 + lw + gap + j * (cw + gap) + cw / 2
        M.texto(dr, (cx_, yh), c.upper(), P.F_BLACK, 32, fill=P.TINTA, anchor="mm")
    n = len(filas)
    ytop = yh + 44
    ybot = P.H_HISTORIA - P.MARGEN - 110 - (130 if B._opc(d, p, "pie") else 0)
    ch = min(int((ybot - ytop - gap * (n - 1)) / n), 330)
    for i, (etq, celdas) in enumerate(filas):
        yy = ytop + i * (ch + gap)
        dr.rounded_rectangle([x0, yy, x0 + lw, yy + ch], radius=22, fill=P.CARBON,
                             outline=P.DORADO, width=3)
        M.parrafo(dr, (x0 + lw / 2, yy + ch / 2 - 40), etq, P.F_BLACK, 30, fill=P.TINTA,
                  max_ancho=lw - 24, interlinea=1.15, anchor_x="m")
        for j, (txt, est) in enumerate(celdas):
            xx = x0 + lw + gap + j * (cw + gap)
            if est == "si":
                dr.rounded_rectangle([xx, yy, xx + cw, yy + ch], radius=22, fill=P.DORADO)
                col = P.NEGRO
            elif est == "cond":
                dr.rounded_rectangle([xx, yy, xx + cw, yy + ch], radius=22, fill=P.CARBON,
                                     outline=P.DORADO, width=4)
                col = P.DORADO
            else:
                dr.rounded_rectangle([xx, yy, xx + cw, yy + ch], radius=22, fill=P.CARBON,
                                     outline=P.GRIS_OSC, width=2)
                col = P.GRIS
            M.parrafo(dr, (xx + cw / 2, yy + ch / 2 - 30), txt.upper(), P.F_BLACK, 27,
                      fill=col, max_ancho=cw - 24, interlinea=1.2, anchor_x="m")
    yb = ytop + n * (ch + gap) + 6
    if B._opc(d, p, "pie"):
        M.parrafo(dr, (P.W_HISTORIA / 2, yb), d[f"{p}_pie"], P.F_REG, 25, fill=P.GRIS,
                  max_ancho=P.W_HISTORIA - 2 * P.MARGEN, interlinea=1.3, anchor_x="m")
    M.pie(dr, nota=cx["nota"], alto=P.H_HISTORIA)
    return img


def _barras(p, d, cx):
    """Ranking en barras (9:16) con un equipo/jugador destacado. p_filas = [(nombre, valor)]
    de mayor a menor; p_destacar = nombre a resaltar (default: el primero)."""
    filas = [(n, float(v)) for n, v in B._req(d, p, "filas")]
    dest = B._opc(d, p, "destacar")
    idx = next((i for i, (n, _) in enumerate(filas) if n == dest), 0)
    return B.P.ranking_historia(
        B._req(d, p, "titulo"), filas, subtitulo=B._opc(d, p, "sub", ""),
        unidad=B._opc(d, p, "unidad", ""), nota=cx["nota"], destacar=idx,
        piso=B._opc(d, p, "piso", 0))


TIPOS_HISTORIA = {"barras": _barras, "comparativa": _comparativa, "tarjetas": _tarjetas, "matriz": _matriz,
                  "grafico": _grafico_historia}

ESPECIALES = {"ratings": _ratings, "shotmap": _shotmap, "stats": _stats,
              "segundo_tiempo": _segundo_tiempo, "tramos": _tramos,
              "salvados": _salvados, "combinacion": _combinacion,
              "goles_empate": _goles_empate}


def generar(datos, orden=None, salida=None):
    d = B.formatear(datos, contexto(datos))
    salida = salida or B.PLACAS / d.get(
        "carpeta", f"historias_fecha_{d['fecha']}_{B.slug(d['rival'])}")
    cx = {"nota": d.get("nota", f"Fecha {d['fecha']} · {B.COMPETENCIA} · SofaScore")}
    B.temas.aplicar(d.get("tema", TEMA))
    placas = B.construir(orden or ORDEN, d, cx, ESPECIALES, TIPOS_HISTORIA)
    return B.guardar_serie(placas, salida, con_nombre=True)
