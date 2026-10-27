# -*- coding: utf-8 -*-
"""
PLANTILLA: publicaciones EDITABLES (Cravero, permanencia, curiosidades, hitos...).

A diferencia de la previa y el post-partido, estas no siguen un guion fijo: cada una
cuenta algo distinto. Por eso la publicación escribe SUS placas a mano, pero sobre un
ESTILO ya asentado, así que nunca se arma una identidad visual desde cero.

Una publicación editable es un archivo en publicaciones/editables/ con:

    ESTILO  = "diario"            # diario | fiesta | riesgo | marca
    CARPETA = "cravero_fecha_28"  # sale en placas/<CARPETA>/
    def construir(E):             # E = el módulo del estilo elegido
        return [E.portada(...), E.dato(...), ...]
    def previo(): ...             # (opcional) chequeos antes de armar; avisan, no frenan

Estilos (qué placas trae cada uno, todas se llaman como E.<placa>(...)):

  diario   papel + serif, ras izquierdo, filetes.   portada, portada_escudo, dato,
           tabla, remate, columna, grafico, grafico_full           (estilo_diario.py)
  fiesta   diario + bastones y papel picado.        dato, tabla, columna, remate,
           grafico, portada_foto, foto_texto, nombres              (estilo_fiesta.py)
  riesgo   fondo blanco, cinta de peligro, rojo.    portada, explicacion, dato,
           cierre, grafico, grafico_full                          (estilo_riesgo.py)
  marca    el estándar negro + dorado (el de las     portada, dato, ranking, resultado,
           placas de partido).  TEMA opcional       ficha, dato_vs, cita, trayectoria...
                                                                   (placas.py)

Para crear una nueva:   python ig.py nuevo editable mi_post
Para generarla:         python ig.py editable mi_post
"""
import importlib

from plantillas import base as B

TIPO = "editable"

ESTILOS = {"diario": "estilo_diario", "fiesta": "estilo_fiesta",
           "riesgo": "estilo_riesgo", "marca": "placas"}


def generar(modulo, salida=None):
    """`modulo` es la publicación ya importada (ESTILO, CARPETA, construir, [previo])."""
    estilo = getattr(modulo, "ESTILO", "diario")
    if estilo not in ESTILOS:
        raise ValueError(f"ESTILO '{estilo}' desconocido. Opciones: {sorted(ESTILOS)}")
    if estilo == "marca":
        B.temas.aplicar(getattr(modulo, "TEMA", "oscuro"))
    E = importlib.import_module(ESTILOS[estilo])
    if hasattr(modulo, "previo"):
        modulo.previo()
    salida = salida or B.PLACAS / modulo.CARPETA
    placas = [(f"{i}", img) for i, img in enumerate(modulo.construir(E), 1)]
    return B.guardar_serie(placas, salida)
