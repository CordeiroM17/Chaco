# -*- coding: utf-8 -*-
"""
Temas de color para las placas. Permite que un carrusel (ej. la previa) use una
paleta distinta a la del post-partido SIN duplicar placas.py: se reasignan en
runtime las constantes de color de marca.py y placas.py, se generan las placas y
se restaura.

Uso:
    import temas
    temas.aplicar("blanco")     # antes de construir las placas
    ...  construir/guardar ...
    temas.restaurar()           # (opcional) vuelve al tema oscuro por defecto

El tema "oscuro" es el estándar actual (post-partido). Los demás están pensados
para diferenciar la PREVIA de un vistazo.
"""
import marca as M
import placas as P

# Las constantes que definen una paleta completa.
_CONST = ("NEGRO", "CARBON", "TINTA", "BLANCO", "DORADO", "DORADO_OSC",
          "GRIS", "GRIS_OSC", "CHIP")

# Cómo leer cada constante (para entender las paletas de abajo):
#   NEGRO      -> fondo de la placa
#   CARBON     -> tarjetas / bloques (dato_vs)
#   TINTA      -> texto principal
#   BLANCO     -> barras del motivo del club (cabecera / laterales)
#   DORADO     -> acento: números gigantes, líneas, etiquetas
#   DORADO_OSC -> acento apagado (marcos punteados)
#   GRIS       -> texto secundario / captions
#   GRIS_OSC   -> separadores y bordes suaves
#
# Regla para que un tema "cierre" con este set de constantes: fondo y tarjetas
# tienen que estar del mismo lado (ambos claros u oscuros) y el texto del lado
# opuesto. Por eso los temas claros usan tarjetas claras + texto oscuro.

TEMAS = {
    # el estándar actual (post-partido): negro + dorado
    "oscuro": {},

    # ---- BLANCO PURO: fondo blanco, texto negro, dorado como acento ---------
    "blanco": {
        "NEGRO": (255, 255, 255),      # fondo
        "CARBON": (247, 247, 245),     # tarjetas gris muy claro
        "TINTA": (20, 20, 22),         # texto negro
        "BLANCO": (20, 20, 22),        # barras oscuras (sobre blanco)
        "DORADO": (198, 148, 32),      # dorado más profundo para contraste sobre blanco
        "DORADO_OSC": (150, 112, 24),
        "GRIS": (96, 96, 100),         # secundario más oscuro para que se lea
        "GRIS_OSC": (220, 220, 222),   # separadores/bordes claros
        "CHIP": (255, 255, 255),       # = fondo: el chip del escudo no se ve
    },

    # ---- HUESO / EDITORIAL: blanco cálido, look "programa de partido" --------
    "hueso": {
        "NEGRO": (243, 240, 233),      # fondo hueso
        "CARBON": (253, 252, 249),     # tarjetas casi blancas
        "TINTA": (28, 26, 24),
        "BLANCO": (28, 26, 24),
        "DORADO": (188, 142, 34),
        "DORADO_OSC": (150, 112, 24),
        "GRIS": (92, 88, 80),          # secundario más oscuro: mejor lectura sobre hueso
        "GRIS_OSC": (206, 202, 192),
        "CHIP": (243, 240, 233),       # = fondo hueso: sin caja detrás del escudo
    },

    # ---- DORADA / MATCHDAY: fondo dorado, texto negro, tarjetas blancas ------
    "dorada": {
        "NEGRO": (233, 180, 60),       # fondo dorado (el color del club como cancha)
        "CARBON": (255, 255, 255),     # tarjetas blancas sobre el dorado
        "TINTA": (22, 20, 16),         # texto negro
        "BLANCO": (22, 20, 16),        # barras negras
        "DORADO": (22, 20, 16),        # el "acento" pasa a ser negro (el fondo ya es dorado)
        "DORADO_OSC": (70, 58, 24),
        "GRIS": (74, 60, 32),          # secundario marrón oscuro sobre dorado
        "GRIS_OSC": (208, 176, 112),   # bordes suaves sobre dorado
        "CHIP": (255, 255, 255),       # chip blanco: enmarca el escudo sobre el dorado
    },
}

_orig = {c: getattr(M, c) for c in _CONST}


def aplicar(nombre):
    """Reasigna la paleta en marca.py y placas.py. Cualquier placa que se genere
    después sale con ese tema."""
    if nombre not in TEMAS:
        raise ValueError(f"Tema desconocido: {nombre}. Opciones: {list(TEMAS)}")
    ov = TEMAS[nombre]
    for c in _CONST:
        val = ov.get(c, _orig[c])
        setattr(M, c, val)
        setattr(P, c, val)


def restaurar():
    """Vuelve al tema oscuro original."""
    for c in _CONST:
        setattr(M, c, _orig[c])
        setattr(P, c, _orig[c])
