# -*- coding: utf-8 -*-
"""
HISTORIAS (9:16) · Fecha 34 · Chaco For Ever 1-2 Central Norte de Salta (local)

    python ig.py historias f34_central_norte

Automáticas: ratings, shotmap (partido 2026-10-18_vs_central_norte_h). A mano: tramos.
La sanción de Luque (roja a los 75') no se conoce: las placas solo dicen que fue expulsado.
"""
from plantillas.base import ASSETS

ORDEN = ["ratings", "shotmap", "tramos"]
# Opcionales: "stats", "segundo_tiempo", "grafico:heatmap_equipo", "grafico:heatmap_rival"

DATOS = {
    "match_key": "2026-10-18_vs_central_norte_h",
    "season": "2026",
    "fecha": 34,
    "rival": "Central Norte de Salta",

    "heatmap_equipo_ruta": ASSETS / "partido/heatmap_equipo_ig.png",
    "heatmap_equipo_titulo": "Dónde vivió cada equipo",
    "heatmap_equipo_sub": "Chaco con la pelota; Central Norte, a la ráfaga final.",
    "heatmap_rival_ruta": ASSETS / "partido/heatmap_rival_ig.png",
    "heatmap_rival_titulo": "Dónde jugó Central Norte",
    "heatmap_rival_sub": "14 de sus 21 remates dentro del área.",

    # ---- El partido por tramos (los xG se calculan solos desde el shotmap) -------------
    "area_x": 15,
    "tramos_titulo": [("¿QUÉ PASÓ CON", "tinta"), ("LA ROJA?", "acento")],
    "tramos_sub": "Chaco 1-2 Central Norte · el partido por tramos",
    "tramos_lista": [
        {"rango": "0' – 36'", "nombre": "Parejo hasta el córner", "desde": 0, "hasta": 36,
         "eventos": ["10'  Rosales remata desviado (0.45 de xG)",
                     "11'  Amarilla a Valdez; 25' lo reemplaza Mihovilcevich",
                     "36'  Gol de Felissia · 0-1, de cabeza, córner de Vedoya"]},
        {"rango": "36' – 47'", "nombre": "Respuesta antes del descanso", "desde": 36, "hasta": 47,
         "eventos": ["45'+2  Gol de Fernández · 1-1 (0.84 de xG)",
                     "45'+2  Romero remata con 0.46 de xG; ataja Hass"]},
        {"rango": "47' – 75'", "nombre": "Chaco manda", "desde": 47, "hasta": 75,
         "eventos": ["Central Norte no remató entre el 48' y el 79'",
                     "52'  Díaz Chaves por Nievas; 72'  Lioi y Tevez entran",
                     "75'  Expulsan a Luque (roja directa)"]},
        {"rango": "75' – final", "nombre": "La ráfaga", "desde": 75, "hasta": 99,
         "destacar": True,
         "eventos": ["80'  Central Norte vuelve a rematar; 11 remates desde ahí",
                     "88'  Tres remates: Lamosa, Mateo (gol, 1-2) e Isa",
                     "Chaco: 2 remates y 0.00 de xG"]},
    ],
    "tramos_resultado": ("Hasta el 75' Chaco generó 2.43 de xG contra 0.90. Del 75' al final, "
                         "Central Norte sumó 2.47 y el Negro 0.00."),
    "tramos_pie": "Caprio hizo 6 atajadas.",
}
