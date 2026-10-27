# -*- coding: utf-8 -*-
"""
HISTORIAS EXPRÉS · Fecha 33 · Madryn 1-2 Chaco For Ever (visitante)

    python ig.py historias f33_express

Sin partido en data/ (no hace falta scrapear): todo se carga a mano.
Resultados dados por el usuario: Madryn 1-2 Chaco (lo dio vuelta), San Miguel empató con
Almirante Brown, Acassuso 3-0 Defensores de Belgrano.
Puntos: Chaco 40, San Miguel 32, Acassuso 32, Defensores 37. Quedan 3 fechas.
Cálculo de salvación (MILP sobre los 36 partidos restantes de la Zona A, el resto de la
fecha 33 sin fijar): con 2+ puntos en las fechas 34-36 (Central Norte L, Ferro V, Racing L)
el Negro se salva sin depender de desempates; con 1 punto depende de la diferencia de gol;
con 0 todavía puede caer.
"""
from plantillas.base import ESCUDOS

ORDEN = ["tarjetas:resultados", "matriz:posibilidades"]   # opcional: "tarjetas:salvacion"

DATOS = {
    "fecha": 33,
    "rival": "Deportivo Madryn",
    "carpeta": "historias_fecha_33_express",
    "nota": "Fecha 33 · Primera Nacional 2026",

    # ---- Cómo quedó la parte de abajo ------------------------------------------------
    "resultados_kicker": "FECHA 33",
    "resultados_titulo": [("ASÍ QUEDÓ", "acento"), ("LA PARTE DE ABAJO", "tinta")],
    "resultados_sub": "Los resultados que movieron la zona de descenso",
    "resultados_lista": [
        ("Madryn 1-2 Chaco", "El Negro lo dio vuelta de visitante y llega a 40 puntos.",
         ESCUDOS / "chaco_for_ever.png", "2-1"),
        ("San Miguel y Almirante Brown", "Empataron. San Miguel suma uno y llega a 32 puntos.",
         ESCUDOS / "san_miguel.png", "="),
        ("Acassuso 3-0 Defensores", "Acassuso también llega a 32. Defensores se queda en 37.",
         ESCUDOS / "acassuso.png", "3-0"),
    ],
    "resultados_resultado": "Chaco ganó, pero todavía no está salvado: faltan 3 fechas.",

    # ---- ¿Cómo se salva en la fecha 34? ----------------------------------------------
    # Chaco 40. San Miguel y Acassuso tienen 32 y 9 puntos por jugar: llegan a 41 como máximo.
    # Cálculo exacto (MILP sobre los partidos restantes de la Zona A, sin diferencia de gol):
    #   gana a Central Norte (43)  -> salvado, pase lo que pase
    #   empata (41)                -> salvado si San Miguel NO gana (empata o pierde)
    #   pierde (40)                -> salvado si San Miguel y Acassuso NO ganan
    "salvacion_kicker": "LA SALVACIÓN",
    "salvacion_titulo": [("¿CÓMO SE SALVA", "acento"), ("EL NEGRO?", "tinta")],
    "salvacion_sub": "Fecha 34 · Chaco For Ever vs Central Norte, de local",
    "salvacion_lista": [
        ("Si gana",
         "Llega a 43 puntos y San Miguel y Acassuso no lo alcanzan (máximo 41). Salvado, pase lo que pase.",
         ESCUDOS / "chaco_for_ever.png", "V"),
        ("Si empata",
         "Salvado si San Miguel no le gana a Ciudad de Bolívar. Si San Miguel gana, todavía no.",
         ESCUDOS / "san_miguel.png", "E"),
        ("Si pierde",
         "Salvado solo si San Miguel y Acassuso (con Madryn) tampoco ganan su partido.",
         ESCUDOS / "acassuso.png", "D"),
    ],
    "salvacion_resultado": "Con 40 puntos y 9 en juego, ganar en casa lo define.",
    "salvacion_pie": "No cuenta la diferencia de gol. San Miguel y Acassuso tienen 32 puntos.",

    # ---- Todas las posibilidades de la fecha 34 (matriz) --------------------------------
    "posibilidades_titulo": [("TODAS LAS", "acento"), ("POSIBILIDADES", "tinta")],
    "posibilidades_sub": "Fecha 34 · Chaco vs Central Norte · ¿se salva el Negro?",
    "posibilidades_col_titulo": "Lo que haga San Miguel (vs Ciudad de Bolívar)",
    "posibilidades_cols": ["Gana", "Empata", "Pierde"],
    "posibilidades_filas": [
        ("Chaco gana", [("Salvado", "si"), ("Salvado", "si"), ("Salvado", "si")]),
        ("Chaco empata", [("Todavía no", "no"), ("Salvado", "si"), ("Salvado", "si")]),
        ("Chaco pierde", [("Todavía no", "no"), ("Salvado si Acassuso no gana", "cond"),
                          ("Salvado si Acassuso no gana", "cond")]),
    ],
    "posibilidades_pie": ("Acassuso juega con Madryn. Chaco tiene 40 puntos; San Miguel y Acassuso tienen 32 "
                          "y pueden llegar a 41. No cuenta la diferencia de gol."),
}
