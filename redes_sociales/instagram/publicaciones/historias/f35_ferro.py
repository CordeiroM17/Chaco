# -*- coding: utf-8 -*-
"""
HISTORIAS · Fecha 35 · Ferro Carril Oeste 0-3 Chaco For Ever (visitante)

    python ig.py historias f35_ferro

Automáticas: ratings, shotmap, stats (partido 2026-10-24_vs_ferro_carril_oeste_a).
A mano: tramos y la placa de la punta. Godoy Cruz 3-0 a Mitre (25/10) sale del fixture.csv
re-scrapeado el 26/10. El desempate si Ferro y Godoy igualan en puntos no se conoce: no se menciona.
"""
from plantillas.base import ESCUDOS

ORDEN = ["ratings", "shotmap", "stats", "tramos", "tarjetas:fiesta"]

DATOS = {
    "match_key": "2026-10-24_vs_ferro_carril_oeste_a",
    "season": "2026",
    "fecha": 35,
    "rival": "Ferro Carril Oeste",
    "nota": "Fecha 35 · Primera Nacional 2026 · SofaScore",

    # ---- El partido por tramos ---------------------------------------------------------
    "area_x": 15,
    "tramos_titulo": [("CÓMO SE", "tinta"), ("GANÓ", "acento")],
    "tramos_sub": "Ferro 0-3 Chaco · el partido por tramos",
    "tramos_lista": [
        {"rango": "0' – 44'", "nombre": "Golpe al minuto", "desde": 0, "hasta": 44,
         "eventos": ["1'  Gol de Romero · 0-1 (asistió Chaves)",
                     "Ferro remata 11 veces: 1.14 de xG contra 0.50",
                     "44'  Expulsan a González (Ferro)"]},
        {"rango": "44' – 46'", "nombre": "El segundo antes del descanso", "desde": 44, "hasta": 46,
         "eventos": ["45'+1  Gol de Díaz Chaves · 0-2"]},
        {"rango": "46' – 74'", "nombre": "Ferro empuja, Caprio responde", "desde": 46, "hasta": 74,
         "eventos": ["49'-60'  Marra y Dening al arco; Caprio ataja",
                     "62'  Entran Pruzzo, Valenzuela y Lioi"]},
        {"rango": "74' – final", "nombre": "El tercero", "desde": 74, "hasta": 99,
         "destacar": True,
         "eventos": ["74'  Gol de Romero de cabeza · 0-3 (asistió Fernández)",
                     "81'  García remata con 0.82 de xGOT; ataja Caprio"]},
    ],
    "tramos_resultado": ("Ferro tuvo 2.33 de xG y 23 remates. Chaco convirtió tres de cinco "
                         "al arco y Caprio atajó los diez que recibió."),
    "tramos_pie": "Caprio: 10 atajadas, 9.5 de puntaje, el más alto del año.",

    # ---- La fiesta de Ferro y la punta -------------------------------------------------
    "fiesta_kicker": "LA PUNTA DE LA ZONA A",
    "fiesta_titulo": [("ARRUINAMOS", "acento"), ("LA FIESTA", "tinta")],
    "fiesta_sub": "Ferro quería el primer puesto con una fecha de sobra",
    "fiesta_lista": [
        ("Ferro 0-3 Chaco",
         "Con una victoria llegaba a 68 y Godoy, a 66 como máximo. Se quedó en 65.",
         ESCUDOS / "ferro_carril_oeste.png", "65"),
        ("Mitre 0-3 Godoy Cruz",
         "Godoy ganó de visitante y llegó a 63 puntos: quedó a dos de Ferro.",
         ESCUDOS / "godoy_cruz.png", "63"),
        ("Fecha 36",
         "Ferro visita a Acassuso y Godoy recibe a Almirante Brown. Se define en la última.",
         ESCUDOS / "chaco_for_ever.png", "36"),
    ],
    "fiesta_resultado": "De cinco puntos de ventaja a dos, y el Negro tuvo que ver.",
    "fiesta_pie": "Puntos tras la fecha 35 · Primera Nacional 2026",
}
