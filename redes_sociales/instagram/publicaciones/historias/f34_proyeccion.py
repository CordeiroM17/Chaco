# -*- coding: utf-8 -*-
"""
HISTORIAS · Proyección tras la fecha 33 (descenso + Reducido)

    python ig.py historias f34_proyeccion

Proyección: Dixon-Coles, 100.000 simulaciones, seed 33, tabla y fixture del 2026-10-13
(outputs/temporadas/2026/global_grupo_a/liga/proyeccion/). Quedan 27 partidos de la Zona A.
Reducido por posición = 2° a 8° de la zona. Cotas exactas (MILP sobre los partidos restantes,
sin diferencia de gol): Chaco necesita sumar los 9 puntos (49) para estar 8° o mejor; con 7
(2V+1E) solo si los desempates acompañan; con menos, no.
"""
from plantillas.base import ESCUDOS

ORDEN = ["barras:descenso", "tarjetas:reducido"]

DATOS = {
    "fecha": 33,
    "rival": "Deportivo Madryn",
    "carpeta": "historias_proyeccion_fecha_33",
    "nota": "Proyección tras la fecha 33 · Primera Nacional 2026",

    # ---- Probabilidad de descenso -----------------------------------------------------
    "descenso_titulo": "Quién baja",
    "descenso_sub": "Probabilidad de descenso · 100.000 simulaciones",
    "descenso_unidad": "%",
    "descenso_destacar": "Chaco For Ever",
    "descenso_filas": [
        ("Acassuso", 72.2),
        ("San Miguel", 61.6),
        ("All Boys", 32.2),
        ("Central Norte", 17.6),
        ("Mitre", 11.9),
        ("San Telmo", 3.2),
        ("Defensores", 1.1),
        ("Chaco For Ever", 0.0),
    ],

    # ---- Qué hay que mirar en la fecha 34: Chaco y el Reducido ---------------------------
    "reducido_kicker": "LA PRÓXIMA FECHA",
    "reducido_titulo": [("¿Y EL", "acento"), ("REDUCIDO?", "tinta")],
    "reducido_sub": "Chaco necesita ganar los tres que quedan (49 puntos)",
    "reducido_lista": [
        ("Chaco vs Central Norte",
         "Ganar es obligatorio. Con 2 victorias y 1 empate solo entra por desempate.",
         ESCUDOS / "chaco_for_ever.png", "V"),
        ("Godoy Cruz vs Estudiantes",
         "Estudiantes tiene 48. Si pierde, queda al alcance.",
         ESCUDOS / "estudiantes_caseros.png", "48"),
        ("San Miguel vs Ciudad de Bolívar",
         "Bolívar tiene 48. Si pierde, queda al alcance (pero San Miguel suma).",
         ESCUDOS / "ciudad_de_bolivar.png", "48"),
        ("Colón vs Almirante Brown",
         "Almirante tiene 47. Si no suma, queda al alcance.",
         ESCUDOS / "almirante_brown.png", "47"),
    ],
    "reducido_resultado": "Hoy tiene 2.6% de probabilidad de entrar al Reducido.",
    "reducido_pie": "Entran los puestos 2° a 8° de la zona. Chaco es 10° con 40 puntos.",
}
