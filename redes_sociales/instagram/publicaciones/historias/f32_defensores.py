# -*- coding: utf-8 -*-
"""
HISTORIAS (9:16) · Fecha 32 · Chaco For Ever 2-2 Defensores de Belgrano (local)

    python ig.py historias f32_defensores

Automáticas (salen del partido): ratings, shotmap, stats, segundo_tiempo.
A mano (se completan acá cada fecha): salvados, combinacion, tramos, goles_empate.
"""
from plantillas.base import ASSETS, ESCUDOS

# Cuáles se generan y en qué orden. Incluye lo que salió del carrusel (tramos, goles del
# empate, gráfico de cancha). Opcionales: "stats", "segundo_tiempo", grafico:figura_heatmap,
# grafico:heatmap_rival.
ORDEN = ["ratings", "shotmap", "tramos", "goles_empate", "grafico:heatmap_equipo",
         "salvados", "combinacion"]

DATOS = {
    # ---- Partido -------------------------------------------------------------
    "match_key": "2026-10-04_vs_defensores_de_belgrano_h",
    "season": "2026",
    "fecha": 32,
    "rival": "Defensores de Belgrano",

    # ---- Gráficos de cancha (9:16). Se generan con nucleo/graficos_partido_marca.py ------
    "heatmap_equipo_ruta": ASSETS / "partido/heatmap_equipo_ig.png",
    "heatmap_equipo_titulo": "Dónde vivió cada equipo",
    "heatmap_equipo_sub": "Un partido parejo en la cancha: 49% de pelota para el Negro, 51% para Defensores.",
    "figura_heatmap_ruta": ASSETS / "partido/heatmap_figura_ig.png",
    "figura_heatmap_titulo": "Dónde jugó Nievas",
    "figura_heatmap_sub": "Volante por el centro de la cancha, con llegada al área en sus dos goles.",
    "heatmap_rival_ruta": ASSETS / "partido/heatmap_rival_ig.png",
    "heatmap_rival_titulo": "Dónde jugó Defensores",
    "heatmap_rival_sub": "51% de pelota y 9 de sus 15 remates desde adentro del área.",

    # ---- Matemáticamente salvados --------------------------------------------
    # Van los equipos que se salvaron EN esta fecha (points_bounds -> "Matemáticamente
    # salvado"). Los que ya estaban salvados antes van en salvados_pie.
    "salvados_titulo": [("MATEMÁTICAMENTE", "acento"), ("SALVADOS", "tinta")],
    "salvados_sub": "Se suman en la fecha {fecha} · quedan 4 por jugar",
    "salvados_lista": [
        ("Almirante Brown", ESCUDOS / "almirante_brown.png", "46 puntos  ·  6° en la tabla"),
        ("Estudiantes de Buenos Aires", ESCUDOS / "estudiantes_caseros.png", "45 puntos  ·  7° en la tabla"),
        ("Ciudad de Bolívar", ESCUDOS / "ciudad_de_bolivar.png", "45 puntos  ·  8° en la tabla"),
    ],
    "salvados_pie": "Ferro, Morón, Godoy Cruz, Madryn y Colón ya estaban a salvo.",

    # ---- Cómo se salva Chaco ---------------------------------------------------
    # Combinación para que Chaco se salve matemáticamente tras la fecha 34 (verificada con
    # el cálculo de combinaciones del 2026-10-07; no cuenta la diferencia de gol).
    # Editar cada fecha: partidos, puntos y techos salen de standings.csv / fixture.csv.
    "combinacion_titulo": [("¿CÓMO SE SALVA", "acento"), ("EL NEGRO?", "tinta")],
    "combinacion_sub": "Una combinación posible tras la fecha 34 · quedarían 2 por jugar",
    "combinacion_lista": [
        ("Chaco suma al menos 1 punto",
         "Entre Deportivo Madryn (V, fecha 33) y Central Norte (L, fecha 34). Perder los dos no alcanza.",
         ESCUDOS / "chaco_for_ever.png"),
        ("Acassuso pierde los 2",
         "Defensores de Belgrano (V, fecha 33) y Deportivo Madryn (L, fecha 34).",
         ESCUDOS / "acassuso.png"),
        ("San Miguel pierde los 2",
         "Almirante Brown (V, fecha 33) y Ciudad de Bolívar (L, fecha 34).",
         ESCUDOS / "san_miguel.png"),
    ],
    "combinacion_resultado": ("Con eso, Chaco queda con 38 puntos o más. Acassuso llegaría a 35 "
                              "como máximo y San Miguel a 37: ya no lo alcanzan."),
    "combinacion_pie": ("Se define recién después de la fecha 34. En la fecha 33 todavía no alcanza con "
                        "ninguna combinación. No se cuenta la diferencia de gol."),

    # ---- ¿Qué pasó? El partido por tramos ---------------------------------------
    # Los xG y el conteo de remates se calculan solos desde el shotmap; los hechos de
    # cada tramo (eventos) y el texto de cierre se escriben a mano.
    "area_x": 15,      # coord_x <= 15 = dentro del área (coincide con "Shots inside box")
    "tramos_titulo": [("¿QUÉ PASÓ EN EL 2-2?", "acento")],
    "tramos_sub": "Chaco For Ever 2-2 {rival} · el partido por tramos",
    "tramos_lista": [
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
    ],
    "tramos_resultado": ("Entre el 60' y el 69' el partido estuvo parejo (0.08 – 0.09). El desnivel "
                         "apareció después: del 69' al final Defensores sumó 0.86 de xG y el Negro 0.14."),
    "tramos_pie": ("Según el índice de momentum de SofaScore, del 69' al final solo el 17% de los "
                   "minutos fue favorable al Negro."),

    # ---- Los dos goles del empate -----------------------------------------------
    "goles_empate_titulo": [("LOS GOLES", "acento"), ("DEL EMPATE", "tinta")],
    "goles_empate_sub": "Cómo llegó {rival} al 2-2",
    "goles_empate_lista": [
        ("Benítez, 2-1", "Remate a unos 22 metros del arco: 0.05 de xG, el más improbable "
         "de los cuatro goles. Había entrado a los 60'.",
         ESCUDOS / "defensores_de_belgrano.png", "63'"),
        ("Aguirre, 2-2", "Remate de derecha dentro del área: 0.36 de xG, la segunda ocasión "
         "más clara del partido. Asistió E. González.",
         ESCUDOS / "defensores_de_belgrano.png", "85'"),
        ("Lo que atajó Caprio", "Tres atajadas, dos de valor alto: el remate de Moyano a los 45' "
         "(0.70 de xGOT) y el cabezazo de Aguirre a los 80' (0.64).",
         ESCUDOS / "chaco_for_ever.png", "3"),
    ],
    "goles_empate_resultado": ("Los dos goles salieron de remates de 0.05 y 0.36 de xG. En el total, "
                               "Defensores generó 1.80 de xG contra 1.60 del Negro: un empate parejo."),
}
