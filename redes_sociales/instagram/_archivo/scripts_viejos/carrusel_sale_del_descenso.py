# -*- coding: utf-8 -*-
"""
Carrusel de HITO: el Negro sale de la zona de descenso y queda 16° (agosto 2026).

SOLO DATOS CURIOSOS. No lleva fichas de rendimiento ni análisis de partido: son
los números sueltos que sorprenden y se comparten.

Estética: `estilo_diario.py` (papel + serif + filetes), no el estándar negro de
`marca.py`. Es a propósito, para que no parezca otro post-partido más.

    python scripts/carrusel_sale_del_descenso.py

------------------------------------------------------------------------------
DE DÓNDE SALEN LOS NÚMEROS (todos verificados, no de memoria):

- Zona de descenso: el standings de SofaScore marca `promotion="Relegation"` en
  los puestos 17 y 18 de cada grupo. Chaco quedó 16° del Grupo A con 22 pts.
- Las 19 jornadas seguidas en zona de descenso salen de reconstruir la tabla del
  Grupo A día por día: `scripts/tabla_historica_grupo_a.py`. Chaco estuvo en zona
  del 28/02 al 26/07 sin interrupción, 14 de esas jornadas último. OJO: ya había
  estado fuera una vez, en la fecha 2 (22/02), así que NO es "por primera vez en
  el año" — es "por primera vez desde la fecha 2".
- El DT de cada partido sale de los raw/managers.json cacheados en las carpetas
  de rivals (los 22 partidos de Chaco aparecen ahí). Cravero debuta en la fecha
  19 (07/07, Acassuso) y dirige también las fechas 20, 22 y 23 (San Telmo, Colón
  y Deportivo Morón): 4 partidos en total. En las planillas de las fechas 22 y 23
  SofaScore lista a Santiago Ojeda, pero la ficha del club (api/v1/team/252726)
  marca a Cravero como DT actual: es el ayudante firmando la planilla.
- El resto (goles, xG, puntos) sale de build_season_table sobre los 22 partidos.
------------------------------------------------------------------------------
"""
from pathlib import Path
import estilo_diario as D

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "placas" / "sale_del_descenso_fecha_23"
NOTA = "Primera Nacional 2026 · Grupo A · 23 fechas"


def construir():
    slides = []

    # 01 — Tapa
    slides.append(D.portada(
        "El Negro, 16° del Grupo A",
        "Afuera de la zona\nde descenso",
        "Cinco datos del giro más grande de la temporada, desde que Cravero "
        "se hizo cargo del equipo.",
        nota=NOTA, centrado=True))

    # 02 — La posición
    slides.append(D.dato(
        "16",
        "El puesto que lo devolvió a zona segura",
        "Descienden el 17 y el 18 de cada grupo. Chaco quedó 16° con 22 puntos, "
        "arriba de Central Norte y de Acassuso. Es la primera vez que está "
        "afuera de la zona desde la fecha 2.",
        kicker="La tabla", nota=NOTA, centrado=True))

    # 03 — Cuánto tiempo estuvo abajo
    slides.append(D.dato(
        "19",
        "Jornadas seguidas estuvo en zona de descenso",
        "Del 28 de febrero al 26 de julio, sin salir ni una fecha. En 14 de esas "
        "jornadas fue directamente el último del grupo.",
        kicker="El contexto", nota=NOTA, centrado=True))

    # 04 — El ciclo de Cravero
    slides.append(D.dato(
        "10 de 12",
        "Los puntos que sacó Cravero desde que llegó",
        "Debutó el 7 de julio ante Acassuso. Cuatro partidos dirigidos, tres "
        "victorias y un empate, siete goles a favor y dos en contra.",
        kicker="El cambio", nota=NOTA, centrado=True))

    # 05 — Lo que no había pasado en todo el año
    slides.append(D.dato(
        "2",
        "Victorias de visitante, las primeras del año",
        "En las primeras nueve salidas no había ganado ninguna. Con Cravero ganó "
        "en San Telmo y en Colón, una atrás de la otra.",
        kicker="El dato", nota=NOTA, centrado=True))

    # 06 — Antes y después, en tabla de diario
    slides.append(D.tabla(
        "Otro equipo",
        "Los 18 partidos anteriores contra los 4 de Cravero",
        [("Puntos por partido", "0.67  a  2.50"),
         ("Goles por partido", "0.72  a  1.75"),
         ("Goles recibidos", "1.33  a  0.50"),
         ("Peligro generado (xG)", "0.75  a  1.83"),
         ("Victorias seguidas", "0  a  3")],
        kicker="La comparación", nota=NOTA, destacar="Puntos por partido", centrado=True))

    # 07 — Qué dice la simulación (Monte Carlo, 100.000 temporadas)
    slides.append(D.tabla(
        "Qué dice la simulación",
        "100.000 temporadas simuladas desde la posición actual (16°, 22 pts)",
        [("Posición final esperada", "14.3° (mediana 15°)"),
         ("Probabilidad de mantener la categoría", "78%"),
         ("Probabilidad de descenso", "22%"),
         ("Probabilidad de entrar al Reducido", "2%"),
         ("Probabilidad de ser 1° de la zona", "0%")],
        kicker="La proyección", nota=NOTA, destacar="Probabilidad de mantener la categoría",
        centrado=True))

    return slides


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(construir(), 1):
        D.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    print("OK _preview.png ->", D.contact_sheet(SALIDA))


if __name__ == "__main__":
    main()
