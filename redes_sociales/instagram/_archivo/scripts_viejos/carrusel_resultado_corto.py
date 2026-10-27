# -*- coding: utf-8 -*-
"""
Carrusel CORTO de resultado (4 placas), para las fechas en las que SofaScore no
publica el análisis completo del partido: sin xG, sin remates, sin ratings, solo
el marcador, los incidentes (goles, cambios, expulsiones) y las tarjetas.

Es el plan B de carrusel_partido.py: cuando la carpeta del partido trae un
`statistics_clean.csv` con dos filas (nada más que tarjetas), armar el carrusel
largo obliga a inventar números. Este cuenta lo que sí se sabe y no finge el resto.

Para reusarlo se cambia el bloque DATOS y se corre:

    python scripts/carrusel_resultado_corto.py

------------------------------------------------------------------------------
PARTIDO ARMADO ACÁ: Gimnasia de Jujuy 1-0 Chaco For Ever · fecha 25 · 16/08/2026
Datos crudos:
  data/temporadas/2026/partidos/2026-08-16_vs_gimnasia_de_jujuy_a/incidents_clean.csv
  data/temporadas/2026/partidos/2026-08-16_vs_gimnasia_de_jujuy_a/statistics_clean.csv
SofaScore no cargó estadísticas de este partido: el statistics_clean.csv tiene
solo amarillas y rojas, y los ratings de los jugadores vienen vacíos. Por eso el
carrusel es corto y se apoya en los incidentes y en la tabla.
------------------------------------------------------------------------------
"""
from pathlib import Path
import placas as P
import marca as M
import temas

RAIZ = Path(__file__).resolve().parents[1]
ESCUDOS = RAIZ / "assets" / "escudos"

CUENTA = "@chacoforever.stats"
COMPETENCIA = "Primera Nacional 2026"
TEMA = "oscuro"                      # post-partido: negro + dorado

DATOS = {
    "fecha": 25,
    "rival": "Gimnasia de Jujuy",
    "condicion": "visitante",

    # ---- Marcador -----------------------------------------------------------
    "local": "Gimnasia de Jujuy",
    "gl": 1,
    "visitante": "Chaco For Ever",
    "gv": 0,
    "torneo_txt": "Fecha 25 · en Jujuy · 16/08",
    "detalle": (
        "Gol de F. Maidana a los 63'. Terminamos con diez por la expulsión de "
        "J. Carrizo a los 87'."),
    "escudo_local": ESCUDOS / "gimnasia_de_jujuy.png",
    "escudo_visitante": ESCUDOS / "chaco_for_ever.png",

    # ---- El partido en corto ------------------------------------------------
    "ficha_titulo": "La fecha 25, en corto",
    "ficha_sub": "Lo que dejó el partido en Jujuy",
    "ficha_filas": [
        ("Resultado", "1 - 0 en contra"),
        ("El gol", "F. Maidana, 63'"),
        ("Expulsado", "J. Carrizo, 87'"),
        ("Cambio en el arco", "Caprio por Canuto, 52'"),
        ("Racha", "segunda derrota seguida"),
    ],
    "ficha_destacar": "Expulsado",

    # ---- El dato que importa: la tabla --------------------------------------
    "dato_kicker": "LO QUE DEJA",
    "dato_num": "2",
    "dato_lab": "los puntos que nos separan de salir del descenso",
    "dato_ctx": (
        "Seguimos 17° con 22 puntos en 24 partidos. Central Norte de Salta, que "
        "hoy marca el corte, tiene 24. Quedan 12 fechas por jugar."),

    # ---- Cierre -------------------------------------------------------------
    "cierre_frase": (
        "Dos derrotas seguidas después de tres triunfos al hilo. El sábado "
        "recibimos a Los Andes, y en casa sacamos casi el doble de puntos que "
        "afuera."),
}

SALIDA = RAIZ / "placas" / f"resultado_fecha_{DATOS['fecha']}_{DATOS['rival'].lower().replace(' ', '_')}"
NOTA = f"Fecha {DATOS['fecha']} · {COMPETENCIA} · SofaScore"


def _ruta(p):
    return str(p) if p and Path(p).exists() else None


def construir():
    d = DATOS
    esc_l, esc_v = _ruta(d["escudo_local"]), _ruta(d["escudo_visitante"])
    if not (esc_l and esc_v):          # o los dos escudos o ninguno
        esc_l = esc_v = None
    return [
        P.resultado(
            d["local"], d["gl"], d["visitante"], d["gv"],
            torneo=d["torneo_txt"], detalle=d["detalle"], nota="SofaScore",
            logo_local=esc_l, logo_visitante=esc_v),
        P.ficha(
            d["ficha_titulo"], d["ficha_sub"], d["ficha_filas"],
            nota=NOTA, destacar=d["ficha_destacar"]),
        P.dato(
            d["dato_num"], d["dato_lab"], d["dato_ctx"],
            kicker=d["dato_kicker"], nota=NOTA),
        P.cita(d["cierre_frase"], autor="El resumen", nota=None),
    ]


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    temas.aplicar(TEMA)
    for i, img in enumerate(construir(), 1):
        M.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")

    from PIL import Image
    files = sorted(SALIDA.glob("[0-9]*.png"))
    th = [Image.open(f).convert("RGB").resize((300, 300)) for f in files]
    cols = 2
    rows = (len(th) + cols - 1) // cols
    s = Image.new("RGB", (cols * 300 + (cols + 1) * 10, rows * 300 + (rows + 1) * 10), (45, 45, 45))
    for i, t in enumerate(th):
        r, c = divmod(i, cols)
        s.paste(t, (10 + c * 310, 10 + r * 310))
    s.save(SALIDA / "_preview.png")
    print("OK _preview.png ->", SALIDA)


if __name__ == "__main__":
    main()
