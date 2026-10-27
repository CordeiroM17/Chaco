# -*- coding: utf-8 -*-
"""
HISTORIAS DE LA PREVIA · Fecha 33 · Deportivo Madryn (L) vs Chaco For Ever (V)

    python ig.py historias f33_madryn_previa

Complementan el carrusel de la previa (publicaciones/pre_partido/f33_madryn.py): acá va el
material que salió del carrusel corto. Tema "hueso" para que se vean como la previa.
Datos: standings.csv (tras la fecha 32), informe pre-partido de Madryn y el antecedente de
la fecha 15 (Chaco 1-2 Madryn, 24/05/2026).
"""
from plantillas.base import ESCUDOS

ORDEN = [
    "comparativa:temporada",   # cara a cara de la temporada
    "comparativa:ida",         # el último cruce, en números (era ida_ficha + ida_dato)
    "tarjetas:jugadores",      # jugador por jugador (era jugadores:clave)
    # "tarjetas:marcador",     # opcional: cómo se mueve el marcador (era dato:vuelve)
]

DATOS = {
    "fecha": 33,
    "rival": "Deportivo Madryn",
    "tema": "hueso",
    "carpeta": "historias_previa_fecha_33_deportivo_madryn",
    "nota": "Previa Fecha 33 · Primera Nacional 2026 · SofaScore",

    # ---- Cara a cara de la temporada (Chaco izquierda, Madryn derecha) ----------------
    "temporada_titulo": "Madryn y el Negro",
    "temporada_sub": "La temporada, cara a cara · antes de la fecha 33",
    "temporada_filas": [
        ("Puntos", "37", "53"),
        ("Goles a favor", "30", "46"),
        ("Goles en contra", "33", "28"),
        ("xG a favor por partido", "1.01", "1.12"),
        ("xG en contra por partido", "0.98", "1.12"),
        ("Puntos por partido en esta condición", "0.69", "2.00"),
    ],

    # ---- El último cruce: fecha 15, Chaco 1-2 Madryn ----------------------------------
    "ida_titulo": "El último cruce",
    "ida_sub": "Fecha 15 · Chaco For Ever 1-2 Madryn · 24 de mayo",
    "ida_filas": [
        ("Posesión", "63%", "37%"),
        ("xG (goles esperados)", "0.80", "0.36"),
        ("Remates", "13", "5"),
        ("Remates al arco", "3", "1"),
        ("Córners", "4", "0"),
        ("Goles", "1", "2"),
    ],

    # ---- Jugador por jugador -----------------------------------------------------------
    "jugadores_titulo": [("JUGADOR", "acento"), ("POR JUGADOR", "tinta")],
    "jugadores_sub": "Lo bueno y lo flojo de tres piezas clave de Madryn",
    "jugadores_kicker": "ASÍ LLEGA EL RIVAL",
    "jugadores_lista": [
        ("L. Silba · el goleador",
         "Convierte casi todo lo que patea (13 goles). Toca poco y pierde los duelos aéreos.",
         ESCUDOS / "deportivo_madryn.png", "LS"),
        ("F. Recalde · el eje",
         "Ordena con el pase y gana por abajo. Casi no pisa el área rival.",
         ESCUDOS / "deportivo_madryn.png", "FR"),
        ("C. Corvalán · central",
         "Gana casi todos los duelos por abajo. Casi no gana por arriba.",
         ESCUDOS / "deportivo_madryn.png", "CC"),
    ],
    "jugadores_resultado": "Por arriba: Pacheco y Romero contra un Corvalán que casi no gana en el aire.",

    # ---- (opcional) cómo se mueve el marcador -------------------------------------------
    "marcador_titulo": [("CÓMO SE MUEVE", "acento"), ("EL MARCADOR", "tinta")],
    "marcador_sub": "Madryn, según cómo arranca el partido",
    "marcador_lista": [
        ("Hace el primer gol", "En el 57% de las veces que el partido sigue 0-0.",
         ESCUDOS / "deportivo_madryn.png", "57%"),
        ("Si se pone 1-0", "Estira la ventaja el 65% de las veces.",
         ESCUDOS / "deportivo_madryn.png", "65%"),
    ],
    "marcador_resultado": "Conviene no recibir primero y sostener el partido parejo.",
}
