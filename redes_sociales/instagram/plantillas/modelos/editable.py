# -*- coding: utf-8 -*-
"""
PUBLICACIÓN EDITABLE · título de la publicación

    python ig.py editable <nombre-de-este-archivo>

Acá las placas las escribís vos, a mano, sobre un estilo ya asentado. Elegí ESTILO:
  "diario"  papel + serif + filetes    -> D.portada, D.portada_escudo, D.dato, D.tabla,
                                          D.remate, D.columna, D.grafico, D.grafico_full
  "fiesta"  diario + bastones/confeti  -> F.dato, F.tabla, F.columna, F.remate, F.grafico,
                                          F.portada_foto, F.foto_texto, F.nombres
  "riesgo"  blanco + cinta de peligro  -> R.portada, R.explicacion, R.dato, R.cierre,
                                          R.grafico, R.grafico_full
  "marca"   negro + dorado (partidos)  -> P.portada, P.dato, P.ranking, P.ficha, P.dato_vs,
                                          P.cita, P.trayectoria, P.grafico_marca ...
Los textos de estilo "diario"/"fiesta" aceptan **rojo** y *negrita* en el medio de la frase.
construir(E) recibe el módulo del estilo (se llama E acá para que sirva con cualquiera).
"""
from plantillas.base import ASSETS

ESTILO = "diario"                   # diario | fiesta | riesgo | marca
CARPETA = "mi_publicacion"          # sale en placas/mi_publicacion/
NOTA = "Primera Nacional 2026 · Zona A"


def construir(E):
    s = []

    # 01 — tapa
    s.append(E.portada(
        "Sección", "Titular\nde la publicación",
        "La bajada: una o dos frases que expliquen de qué va.",
        nota=NOTA, centrado=True))

    # 02 — un dato grande
    s.append(E.dato(
        "00", "Qué mide el número",
        "El contexto, con **una palabra en rojo** y *otra en negrita*.",
        kicker="El dato", nota=NOTA, centrado=True))

    # 03 — una tabla corta
    s.append(E.tabla(
        "Título de la tabla", "Una línea de contexto",
        [("Etiqueta uno", "00"), ("Etiqueta dos", "00"), ("Etiqueta tres", "00")],
        kicker="La tabla", nota=NOTA, destacar="Etiqueta dos", centrado=True))

    # 04 — gráfico propio (png del pipeline o de nucleo/graficos_*)
    # s.append(E.grafico(str(ASSETS / "mi_grafico.png"), "Título", "Subtítulo", nota=NOTA))

    # 05 — cierre
    s.append(E.remate("La frase que cierra la publicación.", firma="Firma", nota=NOTA))

    return s
