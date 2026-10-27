# -*- coding: utf-8 -*-
"""
Identidad visual de la cuenta de Instagram de estadisticas de Chaco For Ever.

Base: blanco y negro (colores del club) + acento DORADO.
Todo lo que se publica sale de aca, para que las placas tengan un estandar
unico y reconocible. No depende del pipeline de informes; es material para
los fanaticos.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# LIENZO
# --------------------------------------------------------------------------
W = H = 1080                      # feed cuadrado de Instagram
W_HISTORIA, H_HISTORIA = 1080, 1920  # historia de Instagram (9:16)
MARGEN = 84                       # margen de seguridad interno

# --------------------------------------------------------------------------
# PALETA  (el estandar de colores)
# --------------------------------------------------------------------------
NEGRO   = (14, 14, 14)            # #0E0E0E  fondo principal
CARBON  = (28, 28, 28)            # #1C1C1C  tarjetas / bloques
TINTA    = (245, 245, 245)        # #F5F5F5  texto principal (blanco roto)
BLANCO   = (255, 255, 255)        # #FFFFFF  rayas del club
DORADO   = (232, 178, 58)         # #E8B23A  acento (numeros, titulos, lineas)
DORADO_OSC = (183, 138, 40)       # #B78A28  dorado apagado (sombras/detalle)
GRIS     = (150, 150, 150)        # #969696  texto secundario / captions
GRIS_OSC = (70, 70, 70)           # #464646  separadores
CHIP     = (244, 244, 244)        # #F4F4F4  fondo del chip detras de los escudos
                                  # (sobre negro da contraste; un tema claro lo
                                  #  iguala al fondo para que no se vea la caja)

# --------------------------------------------------------------------------
# TIPOGRAFIAS  (rutas del sistema Windows)
# --------------------------------------------------------------------------
_FONTS = Path("C:/Windows/Fonts")
F_BLACK  = str(_FONTS / "seguibl.ttf")     # Segoe UI Black  -> titulos / numeros
F_BOLD   = str(_FONTS / "segoeuib.ttf")    # Segoe UI Bold   -> subtitulos
F_SEMI   = str(_FONTS / "seguisb.ttf")     # Segoe UI Semibold -> etiquetas
F_REG    = str(_FONTS / "segoeui.ttf")     # Segoe UI        -> cuerpo
F_COND   = str(_FONTS / "bahnschrift.ttf") # Bahnschrift     -> numeros gigantes (condensada)

HANDLE = "@chacoforever.stats"   # cambiar por el usuario real de la cuenta
_cache = {}


def fuente(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


# --------------------------------------------------------------------------
# PRIMITIVAS DE TEXTO
# --------------------------------------------------------------------------
def _ancho(draw, texto, font, tracking=0):
    if tracking == 0:
        return draw.textbbox((0, 0), texto, font=font)[2]
    return sum(draw.textbbox((0, 0), c, font=font)[2] for c in texto) + tracking * (len(texto) - 1)


def fit_font(draw, texto, path, max_ancho, size_ini, size_min=24):
    """Reduce el tamano hasta que el texto entre en max_ancho."""
    size = size_ini
    while size > size_min:
        f = fuente(path, size)
        if draw.textbbox((0, 0), texto, font=f)[2] <= max_ancho:
            return f
        size -= 2
    return fuente(path, size_min)


def texto(draw, xy, s, path, size, fill=TINTA, anchor="la", tracking=0):
    """Dibuja texto. Soporta 'tracking' (espaciado entre letras) para versales."""
    font = fuente(path, size)
    if tracking == 0:
        draw.text(xy, s, font=font, fill=fill, anchor=anchor)
        return _ancho(draw, s, font)
    x, y = xy
    total = _ancho(draw, s, font, tracking)
    if anchor and anchor[0] == "m":
        x -= total / 2
    elif anchor and anchor[0] == "r":
        x -= total
    va = anchor[1] if len(anchor) > 1 else "a"
    for c in s:
        draw.text((x, y), c, font=font, fill=fill, anchor="l" + va)
        x += draw.textbbox((0, 0), c, font=font)[2] + tracking
    return total


def parrafo(draw, xy, s, path, size, fill=TINTA, max_ancho=W - 2 * MARGEN,
            interlinea=1.28, anchor_x="l"):
    """Texto con salto de linea automatico por ancho. Devuelve la 'y' final."""
    font = fuente(path, size)
    palabras, linea, lineas = s.split(), "", []
    for p in palabras:
        prueba = (linea + " " + p).strip()
        if draw.textbbox((0, 0), prueba, font=font)[2] <= max_ancho:
            linea = prueba
        else:
            lineas.append(linea)
            linea = p
    if linea:
        lineas.append(linea)
    x, y = xy
    dy = int(size * interlinea)
    for ln in lineas:
        if anchor_x == "m":
            draw.text((x, y), ln, font=font, fill=fill, anchor="ma")
        else:
            draw.text((x, y), ln, font=font, fill=fill, anchor="la")
        y += dy
    return y


# --------------------------------------------------------------------------
# ELEMENTOS DE MARCA
# --------------------------------------------------------------------------
def lienzo(fondo=NEGRO, tam=None):
    """tam=(ancho, alto); por defecto el feed cuadrado (W, H). Para una
    historia, pasar tam=(W_HISTORIA, H_HISTORIA)."""
    img = Image.new("RGB", tam or (W, H), fondo)
    return img, ImageDraw.Draw(img)


def rayas(draw, box, colores=None, n=9, borde=None):
    """Rayas verticales blanco/negro (el motivo del club) dentro de un box.
    Con colores=None toma (BLANCO, NEGRO) de la paleta ACTUAL en tiempo de
    llamada, para que un tema (ver temas.py) pueda reasignarlas."""
    if colores is None:
        colores = (BLANCO, NEGRO)
    x0, y0, x1, y1 = box
    ancho = (x1 - x0) / n
    for i in range(n):
        c = colores[i % len(colores)]
        draw.rectangle([x0 + i * ancho, y0, x0 + (i + 1) * ancho, y1], fill=c)
    if borde:
        draw.rectangle(box, outline=borde, width=2)


def cabecera(draw, kicker=None):
    """Marca de agua superior: rayas + wordmark CHACO FOR EVER + linea dorada."""
    rayas(draw, (MARGEN, MARGEN, MARGEN + 66, MARGEN + 44), n=5)
    texto(draw, (MARGEN + 88, MARGEN + 2), "CHACO FOR EVER", F_BLACK, 30,
          fill=TINTA, anchor="la", tracking=2)
    texto(draw, (MARGEN + 88, MARGEN + 40), "ESTADISTICAS", F_SEMI, 17,
          fill=DORADO, anchor="la", tracking=6)
    if kicker:
        texto(draw, (W - MARGEN, MARGEN + 12), kicker.upper(), F_BOLD, 20,
              fill=GRIS, anchor="ra", tracking=3)


def pie(draw, nota=None, handle=HANDLE, alto=None):
    """Pie: linea dorada + handle + nota (fuente del dato). 'alto' = alto real
    del lienzo si no es el cuadrado por defecto (ver lienzo(tam=...))."""
    y = (alto or H) - MARGEN - 24
    draw.rectangle([MARGEN, y - 22, MARGEN + 54, y - 18], fill=DORADO)
    texto(draw, (MARGEN, y), handle, F_SEMI, 22, fill=TINTA, anchor="la")
    if nota:
        texto(draw, (W - MARGEN, y), nota, F_REG, 18, fill=GRIS, anchor="ra")


def linea_dorada(draw, x, y, largo=140, grosor=8):
    draw.rectangle([x, y, x + largo, y + grosor], fill=DORADO)


def guardar(img, ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    img.save(ruta, "PNG")
    return str(ruta)
