# -*- coding: utf-8 -*-
"""
PLANTILLA: previa de partido (carrusel).

Idea fija del formato: contar el partido que viene con dos patas verificables
(cómo fue el último cruce + cómo es el rival) y cerrar con cómo llega el Negro.
El tema visual es "hueso" (blanco cálido) para distinguir la previa del post-partido.

Lo que cambia cada fecha vive en publicaciones/pre_partido/<fecha>.py (DATOS + ORDEN).
Para crear una nueva:   python ig.py nuevo pre_partido f34_rival
Para generarla:         python ig.py pre_partido f34_rival

Claves de DATOS propias de esta plantilla (el resto son placas por prefijo, ver base.py):
    fecha, rival, condicion ('local'|'visitante', del Negro), [rival_corto]
    portada_bajada, [portada_titulo]   (default "Ahora,\\n{rival_corto}")
    escudo_negro, escudo_rival
    [nota]                             (pie de las placas; default "Previa Fecha N · ...")
"""
from plantillas import base as B

TIPO = "pre_partido"
TEMA = "hueso"

# Orden por defecto. Cada publicación puede pisarlo con su propio ORDEN.
ORDEN = [
    "portada",
    "dato:d1",          # el rasgo que define al rival
    "ficha:ficha_rival",  # el rival en la condición que nos toca
    "dato_vs:nasta",    # su amenaza
    "dato:d2",
    "dato:d3",
    "resultado:ida",    # el último cruce
    "ficha:ida_ficha",
    "dato:ida_dato",
    "dato:vuelve",      # cómo se mueve el marcador
    "dato:arquero",
    "dato_vs:llega",    # cómo llega el Negro
    "cita:cierre",
]


def contexto(d):
    rival = d["rival"]
    variables = {"fecha": d["fecha"], "rival": rival,
                 "rival_corto": d.get("rival_corto", rival)}
    return variables


def _portada(d, cx):
    condicion = "de local" if d["condicion"] == "local" else "de visitante"
    return B.P.portada(
        B.formatear(d.get("portada_titulo", "Ahora,\n{rival_corto}"), cx["variables"]),
        d["portada_bajada"],
        etiqueta=f"Previa · Fecha {d['fecha']} · {condicion}",
        nota="SofaScore")


ESPECIALES = {"portada": _portada}


def generar(datos, orden=None, salida=None):
    variables = contexto(datos)
    d = B.formatear(datos, variables)
    cx = {"nota": d.get("nota", f"Previa Fecha {d['fecha']} · {B.COMPETENCIA} · SofaScore"),
          "variables": variables}
    salida = salida or B.PLACAS / f"previa_fecha_{d['fecha']}_{B.slug(d['rival'])}"
    B.temas.aplicar(TEMA)
    placas = B.construir(orden or ORDEN, d, cx, ESPECIALES)
    return B.guardar_serie(placas, salida)
