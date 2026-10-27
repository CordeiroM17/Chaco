# -*- coding: utf-8 -*-
"""
PLANTILLA: análisis post-partido (carrusel). Tema oscuro (negro + dorado).

Lo que cambia cada fecha vive en publicaciones/post_partido/<fecha>.py (DATOS + ORDEN).
Para crear una nueva:   python ig.py nuevo post_partido f34_rival
Para generarla:         python ig.py post_partido f34_rival

Claves de DATOS propias de esta plantilla (el resto son placas por prefijo, ver base.py):
    fecha, local, visitante, goles_local, goles_visitante, condicion ('local'|'visitante')
    resumen_marcador, escudo_local, escudo_visitante
    formacion, formacion_rival, posesion, xg, tiros, corners, duelos      (ficha_partido)
    figura, figura_bajada, figura_teaser, figura_stats, [figura_destacar]
    figura_foto (ruta o None), [figura_foto_focal/zoom/offset], figura_escudo, figura_escudo_leyenda
    [nota]                             (pie de las placas; default "Fecha N · ...")
"""
from pathlib import Path

from plantillas import base as B

TIPO = "post_partido"
TEMA = "oscuro"

ORDEN = [
    "resultado",
    "ficha_partido",
    "dato:gol",
    "figura",
    "figura_numeros",
    "ranking:once",
    "dato:slot7",
    "grafico:mapa_asociacion",
    "grafico:figura_heatmap",
    "dato:arco",
    "ficha:tramos",
    "dato:quiebre",
    "ficha:st",
    "dato_vs:goles",
    "ficha:defensa",
    "grafico:heatmap_rival",
    "grafico:heatmap_equipo",
    "dato_vs:patron",
    "ficha:tabla",
    "cita:cierre",
]


def contexto(d):
    rival = d["local"] if d["condicion"] == "visitante" else d["visitante"]
    return {"fecha": d["fecha"], "rival": rival, "rival_corto": rival,
            "apellido_figura": B.apellido(d.get("figura", ""))}


def _resultado(d, cx):
    return B.P.resultado(
        d["local"], d["goles_local"], d["visitante"], d["goles_visitante"],
        torneo=f"{B.COMPETENCIA} · Fecha {d['fecha']}",
        detalle=d["resumen_marcador"], nota="SofaScore",
        logo_local=B.ruta(d.get("escudo_local")),
        logo_visitante=B.ruta(d.get("escudo_visitante")))


def _ficha_partido(d, cx):
    condicion = "de local" if d["condicion"] == "local" else "de visitante"
    return B.P.ficha(
        "La ficha del partido",
        f"Chaco For Ever vs {cx['rival']} · {condicion}",
        [("Formación", d["formacion"]),
         ("Formación rival", d["formacion_rival"]),
         ("Posesión", d["posesion"]),
         ("xG (goles esperados)", d["xg"]),
         ("Tiros (al arco)", d["tiros"]),
         ("Córners", d["corners"]),
         ("Duelos ganados", d["duelos"])],
        nota=cx["nota"], destacar="xG (goles esperados)")


def _foto_figura(d, salida):
    """Prioridad: figura_foto si existe; si no, un 'foto_figura.*' en la carpeta de
    salida del partido; si no, None (se dibuja el marco reservado)."""
    f = d.get("figura_foto")
    if f and Path(f).exists():
        return str(f)
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        cand = Path(salida) / f"foto_figura{ext}"
        if cand.exists():
            return str(cand)
    return None


def _figura(d, cx):
    return B.P.portada_jugador(
        d["figura"], etiqueta="El jugador del partido",
        subtitulo=d["figura_bajada"], teaser=d["figura_teaser"], nota=cx["nota"],
        foto=_foto_figura(d, cx["salida"]),
        foto_focal=d.get("figura_foto_focal", (0.8, 0.6)),
        foto_zoom=d.get("figura_foto_zoom", 1),
        foto_offset=d.get("figura_foto_offset", (0, 0)),
        escudo=B.ruta(d.get("figura_escudo")),
        escudo_leyenda=d.get("figura_escudo_leyenda"))


def _figura_numeros(d, cx):
    return B.P.ficha(
        f"{cx['apellido_figura']} en números", "Su partido, dato por dato",
        d["figura_stats"], nota=cx["nota"], destacar=d.get("figura_destacar", "Gol"))


ESPECIALES = {"resultado": _resultado, "ficha_partido": _ficha_partido,
              "figura": _figura, "figura_numeros": _figura_numeros}


def generar(datos, orden=None, salida=None):
    variables = contexto(datos)
    d = B.formatear(datos, variables)
    salida = salida or B.PLACAS / f"partido_fecha_{d['fecha']}_{B.slug(variables['rival'])}"
    cx = {"nota": d.get("nota", f"Fecha {d['fecha']} · {B.COMPETENCIA} · SofaScore"),
          "rival": variables["rival"], "apellido_figura": variables["apellido_figura"],
          "salida": salida}
    B.temas.aplicar(TEMA)
    placas = B.construir(orden or ORDEN, d, cx, ESPECIALES)
    return B.guardar_serie(placas, salida)
