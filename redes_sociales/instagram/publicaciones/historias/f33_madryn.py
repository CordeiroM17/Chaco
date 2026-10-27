# -*- coding: utf-8 -*-
"""
HISTORIAS (9:16) · Fecha 33 · Deportivo Madryn 1-2 Chaco For Ever (visitante)

    python ig.py historias f33_madryn

Automáticas: ratings, shotmap (partido 2026-10-11_vs_deportivo_madryn_a). A mano: tramos.
Las de la salvación y la proyección están en f33_express.py y f34_proyeccion.py.
"""
from plantillas.base import ASSETS

ORDEN = ["ratings", "shotmap", "tramos"]
# Opcionales: "stats", "segundo_tiempo", "grafico:heatmap_equipo", "grafico:heatmap_rival"

DATOS = {
    "match_key": "2026-10-11_vs_deportivo_madryn_a",
    "season": "2026",
    "fecha": 33,
    "rival": "Deportivo Madryn",

    "heatmap_equipo_ruta": ASSETS / "partido/heatmap_equipo_ig.png",
    "heatmap_equipo_titulo": "Dónde vivió cada equipo",
    "heatmap_equipo_sub": "Madryn con la pelota; el Negro, atrás y rápido al final.",
    "heatmap_rival_ruta": ASSETS / "partido/heatmap_rival_ig.png",
    "heatmap_rival_titulo": "Dónde jugó Madryn",
    "heatmap_rival_sub": "64% de pelota y 9 de sus 15 remates dentro del área.",

    # ---- El partido por tramos (los xG se calculan solos desde el shotmap) -------------
    "area_x": 15,
    "tramos_titulo": [("¿CÓMO SE DIO VUELTA?", "acento")],
    "tramos_sub": "Madryn 1-2 Chaco For Ever · el partido por tramos",
    "tramos_lista": [
        {"rango": "0' – 15'", "nombre": "Madryn arranca arriba", "desde": 0, "hasta": 15,
         "eventos": ["6'  Gol de Silba · 1-0 (0.58 de xG)",
                     "14'  Gol de Nievas · 1-1 (0.06 de xG)"]},
        {"rango": "15' – 45'", "nombre": "El resto del primer tiempo", "desde": 15, "hasta": 45,
         "eventos": ["33' y 38'  Caprio ataja a Solís y a Machado",
                     "Madryn: 2 remates en el área; el Negro, ninguno"]},
        {"rango": "45' – 89'", "nombre": "Segundo tiempo", "desde": 45, "hasta": 89,
         "eventos": ["46'  Entran Lioi, Ojeda y Valdez; 49' Mihovilcevich; 65' Pacheco",
                     "51'  Caprio le ataja a Silba (0.20 de xG)",
                     "Madryn: 5 remates en el área; el Negro, 2"]},
        {"rango": "89' – final", "nombre": "El final", "desde": 89, "hasta": 99,
         "destacar": True,
         "eventos": ["90+2'  Fernández falla un penal (0.76 de xG)",
                     "90+2'  Gol de Fernández · 1-2 (0.62 de xG), asistió Pacheco",
                     "Cuatro remates del Negro; uno de Madryn"]},
    ],
    "tramos_resultado": ("Hasta el 89' Madryn generó 1.91 de xG y el Negro 0.36. En los últimos "
                         "minutos el Negro sumó 1.53, más del 80% de todo el partido."),
    "tramos_pie": "Caprio hizo 4 atajadas.",
}
