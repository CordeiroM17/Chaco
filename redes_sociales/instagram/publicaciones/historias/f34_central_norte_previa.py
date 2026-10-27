# -*- coding: utf-8 -*-
"""
HISTORIAS DE LA PREVIA · Fecha 34 · Chaco For Ever (L) vs Central Norte (V)

    python ig.py historias f34_central_norte_previa

Complementan el carrusel de la previa (publicaciones/pre_partido/f34_central_norte.py).
Tema "hueso" para que se vean como la previa. Datos: standings.csv (tras la fecha 33),
informe pre-partido de Central Norte y el antecedente de la fecha 16 (CN 1-1 Chaco, 31/05/2026).
La cuenta de la salvación es exacta (todas las combinaciones de los 27 partidos restantes,
sin diferencia de gol).
"""
from pathlib import Path

from plantillas.base import ESCUDOS

PRE = Path(__file__).resolve().parents[4] / "outputs/temporadas/2026/pre_partido/central_norte_h"

ORDEN = [
    "comparativa:temporada",   # cara a cara de la temporada
    "comparativa:ida",         # el último cruce, en números
    "tarjetas:jugadores",      # jugador por jugador
    "grafico:zonas",           # jugadores y zonas donde cuidarnos (cancha)
    "tarjetas:salvacion",      # qué necesitamos el domingo
]

DATOS = {
    "fecha": 34,
    "rival": "Central Norte",
    "tema": "hueso",
    "carpeta": "historias_previa_fecha_34_central_norte",
    "nota": "Previa Fecha 34 · Primera Nacional 2026 · SofaScore",

    # ---- Cara a cara de la temporada (Chaco izquierda, CN derecha) -------------------
    "temporada_titulo": "Central Norte y el Negro",
    "temporada_sub": "La temporada, cara a cara · antes de la fecha 34",
    "temporada_filas": [
        ("Puntos", "40", "34"),
        ("Goles a favor", "32", "21"),
        ("Goles en contra", "34", "30"),
        ("xG a favor por partido", "1.04", "0.89"),
        ("Empates", "10", "16"),
        ("Puntos por partido en esta condición", "1.62", "0.75"),
    ],

    # ---- El último cruce: fecha 16, CN 1-1 Chaco ----------------------------------
    "ida_titulo": "El último cruce",
    "ida_sub": "Fecha 16 · Central Norte 1-1 Chaco · 31 de mayo",
    "ida_filas": [
        ("Posesión", "70%", "30%"),
        ("xG (goles esperados)", "0.41", "0.08"),
        ("Remates", "10", "3"),
        ("Remates al arco", "3", "1"),
        ("Córners", "4", "0"),
        ("Goles", "1", "1"),
    ],

    # ---- Jugador por jugador ---------------------------------------------------------
    "jugadores_titulo": [("JUGADOR", "acento"), ("POR JUGADOR", "tinta")],
    "jugadores_sub": "Lo bueno y lo flojo de tres piezas clave de Central Norte",
    "jugadores_kicker": "ASÍ LLEGA EL RIVAL",
    "jugadores_lista": [
        ("F. Vedoya · el mejor",
         "Patea al arco y pone el último pase por la izquierda. 2 goles y 2 asistencias.",
         ESCUDOS / "central_norte_de_salta.png", "FV"),
        ("F. Borda · el 9",
         "Gana casi todo por arriba (14 remates de cabeza). Define poco: 4 goles en 53 remates.",
         ESCUDOS / "central_norte_de_salta.png", "FB"),
        ("A. Lamosa · central",
         "Titular en 31 partidos. Casi no intercepta ni despeja, y pierde por arriba.",
         ESCUDOS / "central_norte_de_salta.png", "AL"),
    ],
    "jugadores_resultado": "Por arriba: Pacheco y Romero contra un Lamosa que casi no gana en el aire.",

    # ---- Zonas donde cuidarnos: cancha armada con scratchpad/cn_zonas_plot.py --------
    # (heatmaps de temporada de Vedoya, Borda y Rosales en campo rival; 12 de sus 21
    # goles salieron del centro del área; 7 de pelota parada)
    "zonas_ruta": PRE / "zonas_cuidarnos_ig.png",
    "zonas_titulo": "Dónde cuidarnos",
    "zonas_sub": "Por dónde ataca Central Norte y quién lo hace",

    # ---- Qué necesitamos el domingo --------------------------------------------------
    "salvacion_titulo": [("LA CUENTA", "acento"), ("DEL DOMINGO", "tinta")],
    "salvacion_sub": "Qué necesita el Negro para salvarse matemáticamente",
    "salvacion_kicker": "FECHA 34",
    "salvacion_lista": [
        ("Si ganamos", "Salvados, pase lo que pase en el resto.",
         ESCUDOS / "chaco_for_ever.png", "V"),
        ("Si empatamos", "Salvados si San Miguel no le gana a Ciudad de Bolívar.",
         ESCUDOS / "san_miguel.png", "E"),
        ("Si perdemos", "Salvados si ni Acassuso ni San Miguel ganan.",
         ESCUDOS / "acassuso.png", "D"),
    ],
    "salvacion_resultado": "Acassuso y San Miguel juegan el sábado: llegamos sabiendo la cuenta.",
}
