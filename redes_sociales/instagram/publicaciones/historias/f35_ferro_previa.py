# -*- coding: utf-8 -*-
"""
HISTORIAS DE LA PREVIA · Fecha 35 · Ferro Carril Oeste (L) vs Chaco For Ever (V)

    python ig.py historias f35_ferro_previa

Complementan el carrusel (publicaciones/pre_partido/f35_ferro.py). Tema "hueso".
Datos: standings.csv (tras la fecha 34), informe pre-partido de Ferro y el antecedente
de la fecha 17 (Chaco 1-2 Ferro, 07/06/2026). Probabilidades: Monte Carlo Dixon-Coles,
200.000 temporadas, corrido el 23/10 (el desempate por diferencia de gol es una suposición).
"""
from plantillas.base import ESCUDOS

ORDEN = [
    "comparativa:temporada",
    "comparativa:ida",
    "tarjetas:jugadores",
    "tarjetas:salvacion",
]

DATOS = {
    "fecha": 35,
    "rival": "Ferro",
    "tema": "hueso",
    "carpeta": "historias_previa_fecha_35_ferro",
    "nota": "Previa Fecha 35 · Primera Nacional 2026 · SofaScore",

    "temporada_titulo": "Ferro y el Negro",
    "temporada_sub": "La temporada, cara a cara · antes de la fecha 35",
    "temporada_filas": [
        ("Puntos", "40", "65"),
        ("Goles a favor", "33", "38"),
        ("Goles en contra", "36", "28"),
        ("xG a favor por partido", "1.08", "1.36"),
        ("Partidos sin recibir gol", "12", "16"),
        ("Puntos por partido en esta condición", "0.82", "1.88"),
    ],

    "ida_titulo": "El último cruce",
    "ida_sub": "Fecha 17 · Chaco 1-2 Ferro · 7 de junio",
    "ida_filas": [
        ("Posesión", "47%", "53%"),
        ("xG (goles esperados)", "0.44", "0.90"),
        ("Remates", "5", "12"),
        ("Remates al arco", "1", "8"),
        ("Córners", "5", "6"),
        ("Goles", "1", "2"),
    ],

    "jugadores_titulo": [("JUGADOR", "acento"), ("POR JUGADOR", "tinta")],
    "jugadores_sub": "Lo bueno y lo flojo de tres piezas clave de Ferro",
    "jugadores_kicker": "ASÍ LLEGA EL RIVAL",
    "jugadores_lista": [
        ("E. Hoyos · el motor",
         "5° de 111 volantes en pases clave y 6° en toques. 3 goles y 5 asistencias.",
         ESCUDOS / "ferro_carril_oeste.png", "EH"),
        ("L. Parisi · el goleador",
         "9 goles por su izquierda: 2° de 146 extremos en xG por partido. Casi no asiste.",
         ESCUDOS / "ferro_carril_oeste.png", "LP"),
        ("F. Tévez · central",
         "Sale bien jugando, pero pierde por arriba: 121° de 151 centrales en duelo aéreo.",
         ESCUDOS / "ferro_carril_oeste.png", "FT"),
    ],
    "jugadores_resultado": "Por arriba: Pacheco y Romero contra una zaga que no gana en el aire.",

    "salvacion_titulo": [("LO QUE SE JUEGA", "acento"), ("FERRO", "tinta")],
    "salvacion_sub": "Su camino al primer puesto de la Zona A",
    "salvacion_kicker": "FECHA 35",
    "salvacion_lista": [
        ("Si gana", "Llega a 68 y es primero: Godoy Cruz llega a 66 como máximo.",
         ESCUDOS / "ferro_carril_oeste.png", "V"),
        ("Si empatan", "Sigue primero en el 95% de las simulaciones.",
         ESCUDOS / "godoy_cruz.png", "E"),
        ("Si gana el Negro", "Ferro sigue primero en el 88%, pero la cuenta se abre.",
         ESCUDOS / "chaco_for_ever.png", "D"),
    ],
    "salvacion_resultado": "Nosotros, salvados y sin Reducido: jugamos por la posición final.",
}
