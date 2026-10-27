# -*- coding: utf-8 -*-
"""
Historias de Instagram (9:16) con gráficos del informe de partido, re-hechos
en la paleta de la marca (negro/blanco/dorado) en vez del tema claro del PDF.

Reutilizable: cambiás MATCH_KEY/SEASON y volvés a correr.

    python scripts/historias_partido.py

Genera, en placas/historias_{MATCH_KEY}/:
  01_ratings.png    — ranking_historia con el rating de todos los que jugaron
  02_shotmap.png     — shotmap_historia (graficos_partido_marca.py) embebido
  03_stats.png       — comparacion_historia con las mismas métricas que
                        plot_match_stats (src/visualization/season.py)
  05_combinacion_chaco.png — combinacion_historia: cómo puede salvarse Chaco
  04_salvados.png    — salvados_historia: equipos matemáticamente salvados
                        del descenso (editar SALVADOS abajo cada fecha)

------------------------------------------------------------------------------
PARTIDO ARMADO ACÁ: Fecha 31 · Ciudad de Bolívar 2-1 Chaco For Ever (visitante)
------------------------------------------------------------------------------
"""
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]           # .../redes_sociales/instagram
PROYECTO = RAIZ.parents[1]
sys.path.insert(0, str(PROYECTO))

import config
import placas as P
import marca as M
import temas
import graficos_partido_marca as G
from src.analysis.season import is_home_match
from src.visualization.season import _STATS_ORDER, _STATS_ES, _fmt_stat

# ==========================================================================
#  QUÉ GENERAR — lo único que cambiás por partido
# ==========================================================================
MATCH_KEY = "2026-10-04_vs_defensores_de_belgrano_h"
SEASON = "2026"
RIVAL_NOMBRE = "Defensores de Belgrano"

COMPETENCIA = "Primera Nacional 2026"
FECHA = 32
NOTA = f"Fecha {FECHA} · {COMPETENCIA} · SofaScore"

import unicodedata
_SLUG = "".join(c for c in unicodedata.normalize("NFD", RIVAL_NOMBRE.lower()) if unicodedata.category(c) != "Mn").replace(" ", "_")
SALIDA = RAIZ / "placas" / f"historias_fecha_{FECHA}_{_SLUG}"
ASSETS = RAIZ / "assets" / "partido"


ESCUDOS = RAIZ / "assets" / "escudos"
# Equipos matemáticamente salvados (points_bounds → "Matemáticamente salvado").
# Se editan a mano cada fecha: van los que se salvaron EN esta fecha.
QUEDAN = 4
SALVADOS = [
    ("Almirante Brown", ESCUDOS / "almirante_brown.png", "46 puntos  ·  6° en la tabla"),
    ("Estudiantes de Buenos Aires", ESCUDOS / "estudiantes_caseros.png", "45 puntos  ·  7° en la tabla"),
    ("Ciudad de Bolívar", ESCUDOS / "ciudad_de_bolivar.png", "45 puntos  ·  8° en la tabla"),
]
SALVADOS_PIE = "Ferro, Morón, Godoy Cruz, Madryn y Colón ya estaban a salvo."


# Combinación para que Chaco se salve matemáticamente tras la fecha 34 (verificada con
# el cálculo de combinaciones del 2026-10-07; no cuenta la diferencia de gol).
# Editar cada fecha: partidos, puntos y techos salen de standings.csv / fixture.csv.
COMBINACION = [
    ("Chaco suma al menos 1 punto",
     "Entre Deportivo Madryn (V, fecha 33) y Central Norte (L, fecha 34). Perder los dos no alcanza.",
     ESCUDOS / "chaco_for_ever.png"),
    ("Acassuso pierde los 2",
     "Defensores de Belgrano (V, fecha 33) y Deportivo Madryn (L, fecha 34).",
     ESCUDOS / "acassuso.png"),
    ("San Miguel pierde los 2",
     "Almirante Brown (V, fecha 33) y Ciudad de Bolívar (L, fecha 34).",
     ESCUDOS / "san_miguel.png"),
]
COMBINACION_RESULTADO = ("Con eso, Chaco queda con 38 puntos o más. Acassuso llegaría a 35 "
                         "como máximo y San Miguel a 37: ya no lo alcanzan.")
COMBINACION_PIE = ("Se define recién después de la fecha 34. En la fecha 33 todavía no alcanza con "
                   "ninguna combinación. No se cuenta la diferencia de gol.")


# ---- ¿Qué pasó? Análisis del empate (editar cada fecha) ------------------------------
# Tramos: los xG y el conteo de remates se calculan solos desde el shotmap; los hechos
# de cada tramo (eventos) y el texto de cierre se escriben a mano.
AREA_X = 15          # coord_x <= 15 = dentro del área (coincide con "Shots inside box" de SofaScore)
TRAMOS = [
    {"rango": "0' – 45'", "nombre": "Primer tiempo", "desde": 0, "hasta": 45,
     "eventos": ["5'  Gol de Nievas · 1-0 (cabezazo, centro de Ojeda)",
                 "45'+3  Gol de Nievas · 2-0 (tras un pase entre líneas)",
                 "Dos goles con solo 0.46 de xG; Caprio atajó un remate de 0.70 de xGOT"]},
    {"rango": "45' – 60'", "nombre": "Arranque del segundo tiempo", "desde": 45, "hasta": 60,
     "eventos": ["49'  Cabezazo de Aguirre, afuera (0.22 de xG)",
                 "60'  Defensores cambia a dos: entran Benítez y Ardaiz"]},
    {"rango": "60' – 69'", "nombre": "Tras los cambios de Defensores", "desde": 60, "hasta": 69,
     "eventos": ["63'  Gol de Benítez · 2-1 (remate de 0.05 de xG)",
                 "Partido parejo: 1 remate nuestro y 2 de ellos"]},
    {"rango": "69' – 90'", "nombre": "Tras los cambios de Chaco", "desde": 69, "hasta": 99,
     "destacar": True,
     "eventos": ["69' a 82'  Chaco hace 5 cambios: salen Nievas, Chaves, Gaggi y Romero",
                 "85'  Gol de Aguirre · 2-2 (0.36 de xG)",
                 "Ellos: 6 remates, 4 en el área. Nosotros: 4 remates, ninguno en el área"]},
]
TRAMOS_RESULTADO = ("Entre el 60' y el 69' el partido estuvo parejo (0.08 – 0.09). El desnivel "
                    "apareció después: del 69' al final Defensores sumó 0.86 de xG y el Negro 0.14.")
TRAMOS_PIE = ("Según el índice de momentum de SofaScore, del 69' al final solo el 17% de los "
              "minutos fue favorable al Negro.")

# Los dos goles del empate (cartas de la historia 08)
GOLES_EMPATE = [
    ("Benítez, 2-1", "Remate a unos 22 metros del arco: 0.05 de xG, el más improbable "
     "de los cuatro goles. Había entrado a los 60'.",
     ESCUDOS / "defensores_de_belgrano.png", "63'"),
    ("Aguirre, 2-2", "Remate de derecha dentro del área: 0.36 de xG, la segunda ocasión "
     "más clara del partido. Asistió E. González.",
     ESCUDOS / "defensores_de_belgrano.png", "85'"),
    ("Lo que atajó Caprio", "Tres atajadas, dos de valor alto: el remate de Moyano a los 45' "
     "(0.70 de xGOT) y el cabezazo de Aguirre a los 80' (0.64).",
     ESCUDOS / "chaco_for_ever.png", "3"),
]
GOLES_EMPATE_RESULTADO = ("Los dos goles salieron de remates de 0.05 y 0.36 de xG. En el total, "
                          "Defensores generó 1.80 de xG contra 1.60 del Negro: un empate parejo.")


def _match_dir():
    return Path(config.season_data_dir(SEASON)) / MATCH_KEY


def slide_ratings():
    lin = pd.read_csv(_match_dir() / "lineups_clean.csv")
    home = is_home_match(MATCH_KEY)
    side = "home" if home else "away"
    ch = lin[lin["team_side"] == side].copy()
    ch["rating"] = pd.to_numeric(ch["rating"], errors="coerce")
    ch = ch.dropna(subset=["rating"]).sort_values("rating", ascending=False)
    filas = [(r["player_name"], round(float(r["rating"]), 1)) for _, r in ch.iterrows()]
    return P.ranking_historia(
        "Ratings del Partido",
        filas,
        subtitulo=f"Chaco For Ever vs {RIVAL_NOMBRE} · todo el plantel que jugó",
        nota=NOTA, destacar=0, piso=4.0)


def slide_shotmap():
    save = ASSETS / "shotmap_historia_ig.png"
    G.shotmap_historia(MATCH_KEY, SEASON, save)
    return P.grafico_marca_historia(
        str(save), "Mapa de Tiros",
        subtitulo=f"Chaco For Ever vs {RIVAL_NOMBRE} · por tipo de remate",
        nota="Fuente: SofaScore")


def slide_stats():
    st = pd.read_csv(_match_dir() / "statistics_clean.csv")
    st = st[st["metric"].isin(_STATS_ORDER)].drop_duplicates(subset="metric", keep="first")
    st = st.set_index("metric")
    home = is_home_match(MATCH_KEY)

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

    return P.comparacion_historia(
        "Resumen del Partido",
        f"Chaco For Ever vs {RIVAL_NOMBRE}",
        filas, home_label="Chaco For Ever", away_label=RIVAL_NOMBRE, nota=NOTA)


def slide_salvados():
    return P.salvados_historia(
        [("MATEMÁTICAMENTE", P.DORADO), ("SALVADOS", P.TINTA)],
        f"Se suman en la fecha {FECHA} · quedan {QUEDAN} por jugar",
        [(n, str(e), det) for n, e, det in SALVADOS],
        pie_texto=SALVADOS_PIE,
        nota=f"Fecha {FECHA} · {COMPETENCIA}")


def slide_combinacion():
    return P.combinacion_historia(
        [("¿CÓMO SE SALVA", P.DORADO), ("EL NEGRO?", P.TINTA)],
        "Una combinación posible tras la fecha 34 · quedarían 2 por jugar",
        [(t, dtl, str(e)) for t, dtl, e in COMBINACION],
        resultado_texto=COMBINACION_RESULTADO,
        pie_texto=COMBINACION_PIE,
        nota=f"Fecha {FECHA} · {COMPETENCIA}")


def _shots_chaco():
    """Shotmap del partido con la columna 'chaco' (True = remate de Chaco)."""
    sm = pd.read_csv(_match_dir() / "shotmap_clean.csv")
    sm["chaco"] = sm["isHome"] == is_home_match(MATCH_KEY)
    sm["area"] = sm["coord_x"] <= AREA_X
    return sm


def slide_tramos():
    sm = _shots_chaco()
    tramos = []
    for t in TRAMOS:
        w = sm[(sm["time"] > t["desde"]) & (sm["time"] <= t["hasta"])] if t["desde"] else sm[sm["time"] <= t["hasta"]]
        tramos.append(dict(t, xg=(round(w.loc[w.chaco, "xg"].sum(), 2),
                                   round(w.loc[~w.chaco, "xg"].sum(), 2))))
    return P.tramos_historia(
        [("¿QUÉ PASÓ EN EL 2-2?", P.DORADO)],
        f"Chaco For Ever 2-2 {RIVAL_NOMBRE} · el partido por tramos",
        tramos, resultado_texto=TRAMOS_RESULTADO, pie_texto=TRAMOS_PIE,
        nota=NOTA, kicker="EL PARTIDO")


def slide_segundo_tiempo():
    sm = _shots_chaco()
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
    return P.comparacion_historia(
        "El segundo tiempo en números",
        f"Chaco For Ever vs {RIVAL_NOMBRE} · del 46' al final",
        filas, home_label="Chaco For Ever", away_label=RIVAL_NOMBRE, nota=NOTA)


def slide_goles_empate():
    return P.combinacion_historia(
        [("LOS GOLES", P.DORADO), ("DEL EMPATE", P.TINTA)],
        f"Cómo llegó {RIVAL_NOMBRE} al 2-2",
        [(t, dtl, str(e), b) for t, dtl, e, b in GOLES_EMPATE],
        resultado_texto=GOLES_EMPATE_RESULTADO, nota=NOTA, kicker="EL EMPATE")


def main():
    temas.aplicar("oscuro")
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, fn in [("01_ratings", slide_ratings),
                       ("02_shotmap", slide_shotmap),
                       ("03_stats", slide_stats),
                       ("04_salvados", slide_salvados),
                       ("05_combinacion_chaco", slide_combinacion)]:   # slide_tramos / slide_segundo_tiempo / slide_goles_empate quedan disponibles
        img = fn()
        M.guardar(img, SALIDA / f"{nombre}.png")
        print("OK", f"{nombre}.png")
    print("->", SALIDA)


if __name__ == "__main__":
    main()
