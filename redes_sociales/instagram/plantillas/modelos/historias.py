# -*- coding: utf-8 -*-
"""
HISTORIAS (9:16) · Fecha NN · vs RIVAL

    python ig.py historias <nombre-de-este-archivo>

Automáticas (salen del partido): ratings, shotmap, stats, segundo_tiempo.
A mano (se completan acá): salvados, combinacion, tramos, goles_empate.
Elegí cuáles salen, y en qué orden, con ORDEN. Para las que usan datos a mano completá
las claves de abajo (los títulos llevan colores simbólicos: "acento" = dorado, "tinta" = texto).
"""
from plantillas.base import ESCUDOS

ORDEN = ["ratings", "shotmap", "stats"]
# Disponibles: "ratings", "shotmap", "stats", "segundo_tiempo", "tramos",
#              "salvados", "combinacion", "goles_empate"

DATOS = {
    # ---- Partido (siempre) ------------------------------------------------------
    "match_key": "AAAA-MM-DD_vs_rival_h",      # nombre de la carpeta del partido en data/
    "season": "2026",
    "fecha": 0,
    "rival": "Nombre Completo",

    # ---- salvados --------------------------------------------------------------
    "salvados_titulo": [("MATEMÁTICAMENTE", "acento"), ("SALVADOS", "tinta")],
    "salvados_sub": "Se suman en la fecha {fecha} · quedan 0 por jugar",
    "salvados_lista": [
        ("Equipo", ESCUDOS / "archivo.png", "00 puntos  ·  0° en la tabla"),
    ],
    "salvados_pie": "Los que ya estaban a salvo.",

    # ---- combinacion -----------------------------------------------------------
    "combinacion_titulo": [("¿CÓMO SE SALVA", "acento"), ("EL NEGRO?", "tinta")],
    "combinacion_sub": "Una combinación posible tras la fecha NN",
    "combinacion_lista": [
        ("Condición", "Detalle de la condición.", ESCUDOS / "chaco_for_ever.png"),
    ],
    "combinacion_resultado": "Con eso, ...",
    "combinacion_pie": "Aclaraciones.",

    # ---- tramos (xG por tramo se calcula solo; los eventos se escriben) --------------
    "area_x": 15,
    "tramos_titulo": [("¿QUÉ PASÓ?", "acento")],
    "tramos_sub": "Chaco For Ever vs {rival} · el partido por tramos",
    "tramos_lista": [
        {"rango": "0' – 45'", "nombre": "Primer tiempo", "desde": 0, "hasta": 45,
         "eventos": ["Hecho 1", "Hecho 2"]},
        {"rango": "45' – 90'", "nombre": "Segundo tiempo", "desde": 45, "hasta": 99,
         "destacar": True, "eventos": ["Hecho 1"]},
    ],
    "tramos_resultado": "Qué dicen los tramos.",
    "tramos_pie": "",

    # ---- goles_empate (tarjetas con escudo y minuto) -----------------------------
    "goles_empate_titulo": [("LOS GOLES", "acento"), ("DEL PARTIDO", "tinta")],
    "goles_empate_sub": "Cómo llegó {rival} al resultado",
    "goles_empate_lista": [
        ("Jugador, 1-0", "Cómo fue el gol.", ESCUDOS / "chaco_for_ever.png", "00'"),
    ],
    "goles_empate_resultado": "Lo que dicen los goles.",
}
