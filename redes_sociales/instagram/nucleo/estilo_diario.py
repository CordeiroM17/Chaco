# -*- coding: utf-8 -*-
"""
ESTILO DIARIO — una segunda identidad visual para la cuenta, pensada para los
posts de datos sueltos / curiosidades.

Por qué existe: `marca.py` + `placas.py` son el estándar de la cuenta (fondo
negro, número gigante centrado en sans condensada, acento dorado). Sirve para el
post-partido y la previa, pero cuando todo sale igual el feed se aplana. Este
módulo es deliberadamente OTRA publicación: papel, tipografía serif (Georgia),
composición al ras izquierdo, filetes finos y aire. Parece un recorte de diario,
no una placa de estadísticas.

NO toca marca.py ni placas.py: es autocontenido, así que los carruseles viejos
siguen saliendo igual.

    import estilo_diario as D
    img = D.dato("16", "El puesto que lo devolvió a zona segura", "cuerpo...",
                 kicker="La tabla")
    D.guardar(img, "salida/02.png")
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# LIENZO
# --------------------------------------------------------------------------
W = H = 1080
MARGEN = 96                     # margen ancho: el aire es parte del estilo

# --------------------------------------------------------------------------
# PALETA — papel y tinta. Sin negro puro ni blanco puro.
# --------------------------------------------------------------------------
PAPEL   = (244, 241, 233)       # #F4F1E9  fondo, blanco cálido de papel
TINTA   = (22, 20, 15)          # #16140F  texto principal
MUTED   = (110, 103, 91)        # #6E675B  secundario / captions
FILETE  = (24, 22, 17)          # filetes fuertes
FILETE_S = (190, 184, 170)      # filetes suaves
ACENTO  = (150, 42, 34)         # #962A22  rojo de imprenta: kickers y remarcados

# --------------------------------------------------------------------------
# TIPOGRAFIAS — Georgia. Sus numeros son "old style" (con ascendentes y
# descendentes desparejas), que es justo lo que le da el aire de imprenta.
# --------------------------------------------------------------------------
_F = Path("C:/Windows/Fonts")
SERIF      = str(_F / "georgia.ttf")
SERIF_B    = str(_F / "georgiab.ttf")
SERIF_I    = str(_F / "georgiai.ttf")
SERIF_BI   = str(_F / "georgiaz.ttf")

HANDLE = "@chacoforever.stats"
_cache = {}


def fuente(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


# --------------------------------------------------------------------------
# PRIMITIVAS
# --------------------------------------------------------------------------
def _ancho(d, s, font, tracking=0):
    if tracking == 0:
        return d.textbbox((0, 0), s, font=font)[2]
    return sum(d.textbbox((0, 0), c, font=font)[2] for c in s) + tracking * (len(s) - 1)


def fit_font(d, s, path, max_ancho, size_ini, size_min=20):
    size = size_ini
    while size > size_min:
        f = fuente(path, size)
        if d.textbbox((0, 0), s, font=f)[2] <= max_ancho:
            return f
        size -= 2
    return fuente(path, size_min)


def texto(d, xy, s, path, size, fill=TINTA, anchor="la", tracking=0):
    """Texto simple. `tracking` separa las letras (para versalitas)."""
    font = fuente(path, size)
    if tracking == 0:
        d.text(xy, s, font=font, fill=fill, anchor=anchor)
        return _ancho(d, s, font)
    x, y = xy
    total = _ancho(d, s, font, tracking)
    if anchor and anchor[0] == "m":
        x -= total / 2
    elif anchor and anchor[0] == "r":
        x -= total
    va = anchor[1] if len(anchor) > 1 else "a"
    for c in s:
        d.text((x, y), c, font=font, fill=fill, anchor="l" + va)
        x += d.textbbox((0, 0), c, font=font)[2] + tracking
    return total


def _lineas(d, s, path, size, max_ancho):
    """Corta el texto en líneas que entren en max_ancho."""
    font = fuente(path, size)
    linea, out = "", []
    for p in s.split():
        prueba = (linea + " " + p).strip()
        if d.textbbox((0, 0), prueba, font=font)[2] <= max_ancho:
            linea = prueba
        else:
            out.append(linea)
            linea = p
    if linea:
        out.append(linea)
    return out


# --------------------------------------------------------------------------
# RESALTADO INLINE  ── marcá palabras/frases en el texto:
#   **frase**  -> resaltado fuerte: negrita + rojo de imprenta (ACENTO)
#   *frase*    -> énfasis suave: negrita, mismo color
# Funciona en el `cuerpo`/`titulo` de dato(), en los párrafos de columna() y
# en la `bajada` de portada(). Si el texto no tiene '*', todo sigue igual.
# --------------------------------------------------------------------------
import re as _re
_RE_MARCA = _re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*")


def _tramos(s):
    """'a **b** c *d*' -> [('a ',''),('b','a'),(' c ',''),('d','b')]"""
    out, i = [], 0
    for m in _RE_MARCA.finditer(s):
        if m.start() > i:
            out.append((s[i:m.start()], ""))
        if m.group(1) is not None:
            out.append((m.group(1), "a"))
        else:
            out.append((m.group(2), "b"))
        i = m.end()
    if i < len(s):
        out.append((s[i:], ""))
    return out


def _fuente_de(est, path, size):
    return fuente(SERIF_B if est in ("a", "b") else path, size)


def _color_de(est, fill):
    return ACENTO if est == "a" else fill


def _wrap_rico(d, s, path, size, fill, max_ancho):
    """Devuelve [ [ (texto, font, color), ... ], ... ] — una lista de líneas,
    cada línea una lista de segmentos con su tipografía y color."""
    space_w = d.textbbox((0, 0), " ", font=fuente(path, size))[2]
    lineas, cur, curw = [], [], 0
    for txt, est in _tramos(s):
        font = _fuente_de(est, path, size)
        color = _color_de(est, fill)
        for m in _re.finditer(r"\S+|\s+", txt):
            chunk = m.group(0)
            if chunk.isspace():
                if cur:
                    cur.append((" ", fuente(path, size), fill))
                    curw += space_w
                continue
            w = d.textbbox((0, 0), chunk, font=font)[2]
            if cur and curw + w > max_ancho:
                while cur and cur[-1][0] == " ":
                    cur.pop()
                lineas.append(cur)
                cur, curw = [], 0
            cur.append((chunk, font, color))
            curw += w
    if cur:
        while cur and cur[-1][0] == " ":
            cur.pop()
        lineas.append(cur)
    return lineas


def alto_parrafo(d, s, path, size, max_ancho=None, interlinea=1.42):
    """Alto que va a ocupar el párrafo. Sirve para centrar el bloque antes de
    dibujarlo (si no, todas las placas quedan con un hueco muerto abajo)."""
    max_ancho = max_ancho or (W - 2 * MARGEN)
    if "*" in s:
        n = len(_wrap_rico(d, s, path, size, TINTA, max_ancho))
    else:
        n = len(_lineas(d, s, path, size, max_ancho))
    return n * int(size * interlinea)


def parrafo(d, xy, s, path, size, fill=TINTA, max_ancho=None, interlinea=1.42,
            anchor_x="l"):
    """Texto con corte de línea por ancho. Devuelve la 'y' final.
    Acepta resaltado inline con **frase** (negrita + rojo) y *frase* (negrita)."""
    max_ancho = max_ancho or (W - 2 * MARGEN)
    x, y = xy
    dy = int(size * interlinea)
    if "*" not in s:
        for ln in _lineas(d, s, path, size, max_ancho):
            d.text((x, y), ln, font=fuente(path, size), fill=fill,
                   anchor="ma" if anchor_x == "m" else "la")
            y += dy
        return y
    for segs in _wrap_rico(d, s, path, size, fill, max_ancho):
        total = sum(d.textbbox((0, 0), t, font=f)[2] for t, f, _ in segs)
        sx = x - total / 2 if anchor_x == "m" else x
        for t, f, c in segs:
            d.text((sx, y), t, font=f, fill=c, anchor="la")
            sx += d.textbbox((0, 0), t, font=f)[2]
        y += dy
    return y


def filete(d, y, x0=None, x1=None, grosor=1, color=FILETE):
    x0 = MARGEN if x0 is None else x0
    x1 = (W - MARGEN) if x1 is None else x1
    d.rectangle([x0, y, x1, y + grosor - 1], fill=color)


def lienzo():
    img = Image.new("RGB", (W, H), PAPEL)
    return img, ImageDraw.Draw(img)


# --------------------------------------------------------------------------
# ELEMENTOS FIJOS: cabezal y pie
# --------------------------------------------------------------------------
def cabezal(d, seccion=None):
    """Cabezal tipo diario: filete grueso, nombre centrado en versalitas,
    filete fino y la sección a la derecha."""
    filete(d, MARGEN, grosor=4)
    texto(d, (W / 2, MARGEN + 20), "CHACO FOR EVER", SERIF_B, 27,
          fill=TINTA, anchor="ma", tracking=7)
    filete(d, MARGEN + 66, grosor=1, color=FILETE_S)
    texto(d, (MARGEN, MARGEN + 76), "ESTADÍSTICAS DEL NEGRO", SERIF, 15,
          fill=MUTED, anchor="la", tracking=3)
    if seccion:
        texto(d, (W - MARGEN, MARGEN + 76), seccion.upper(), SERIF_B, 15,
              fill=ACENTO, anchor="ra", tracking=3)


def pie(d, nota=None):
    y = PIE_Y
    filete(d, y, grosor=1, color=FILETE_S)
    texto(d, (MARGEN, y + 14), HANDLE, SERIF_I, 21, fill=TINTA, anchor="la")
    if nota:
        texto(d, (W - MARGEN, y + 16), nota, SERIF, 16, fill=MUTED, anchor="ra")


# Zona util: entre el cabezal y el pie. Todo el contenido se centra ahi adentro.
CABEZAL_Y = MARGEN + 110        # donde termina el cabezal
PIE_Y = H - MARGEN - 34         # donde arranca el pie


def _y_centrado(alto_bloque):
    """'y' inicial para que un bloque de ese alto quede centrado en la zona util."""
    libre = (PIE_Y - CABEZAL_Y) - alto_bloque
    return CABEZAL_Y + max(libre / 2, 0)


# --------------------------------------------------------------------------
# PLACAS
# --------------------------------------------------------------------------
def portada(volanta, titulo, bajada, nota=None, centrado=False):
    """Tapa: volanta breve, titular grande y bajada en bastardilla.
    `titulo` acepta \\n para forzar los cortes de línea del titular.
    `centrado=True` alinea todo al medio en vez de al ras izquierdo."""
    img, d = lienzo()
    cabezal(d)

    lineas = titulo.split("\n")
    fuentes = [fit_font(d, ln, SERIF_B, W - 2 * MARGEN, 104, 46) for ln in lineas]
    alto_baj = alto_parrafo(d, bajada, SERIF_I, 28, W - 2 * MARGEN - 40, 1.45)
    alto = 46 + sum(int(f.size * 1.06) for f in fuentes) + 26 + 34 + alto_baj

    y = _y_centrado(alto)
    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    texto(d, (xc, y), volanta.upper(), SERIF_B, 19, fill=ACENTO,
          anchor=ax + "a", tracking=4)
    y += 46

    for ln, f in zip(lineas, fuentes):
        d.text((xc, y), ln, font=f, fill=TINTA, anchor=ax + "a")
        y += int(f.size * 1.06)

    y += 26
    if centrado:
        filete(d, y, x0=W / 2 - 75, x1=W / 2 + 75, grosor=3)
    else:
        filete(d, y, x1=MARGEN + 150, grosor=3)
    y += 34
    parrafo(d, (xc, y), bajada, SERIF_I, 28, fill=MUTED,
            max_ancho=W - 2 * MARGEN - 40, interlinea=1.45, anchor_x=ax)

    pie(d, nota=nota)
    return img


def portada_escudo(escudo_ruta, volanta, titulo, bajada, nota=None, escudo_px=190):
    """Tapa con el escudo del club centrado entre la volanta y el título,
    dentro de un chip de papel con borde fino (mismo lenguaje que
    `_escudo_en_zona` de placas.py, pero en la estética de diario: sin
    rayas ni dorado). Siempre centrada — no tiene variante al ras.
    `titulo` acepta \\n para forzar los cortes de línea del titular."""
    img, d = lienzo()
    cabezal(d)

    lineas = titulo.split("\n")
    fuentes = [fit_font(d, ln, SERIF_B, W - 2 * MARGEN, 88, 42) for ln in lineas]
    alto_baj = alto_parrafo(d, bajada, SERIF_I, 28, W - 2 * MARGEN - 40, 1.45)
    alto = 46 + (escudo_px + 40) + 40 + sum(int(f.size * 1.08) for f in fuentes) + \
        26 + 34 + alto_baj

    y = _y_centrado(alto)
    xc = W / 2
    texto(d, (xc, y), volanta.upper(), SERIF_B, 19, fill=ACENTO,
          anchor="ma", tracking=4)
    y += 46

    pad = 22
    cy = y + escudo_px / 2
    d.ellipse([xc - escudo_px / 2 - pad, y - pad,
               xc + escudo_px / 2 + pad, y + escudo_px + pad],
              fill=PAPEL, outline=FILETE, width=2)
    try:
        lg = Image.open(escudo_ruta).convert("RGBA").resize(
            (escudo_px, escudo_px), Image.LANCZOS)
        img.paste(lg, (int(xc - escudo_px / 2), int(y)), lg)
    except FileNotFoundError:
        pass
    y += escudo_px + 40

    for ln, f in zip(lineas, fuentes):
        d.text((xc, y), ln, font=f, fill=TINTA, anchor="ma")
        y += int(f.size * 1.08)

    y += 26
    filete(d, y, x0=W / 2 - 75, x1=W / 2 + 75, grosor=3)
    y += 34
    parrafo(d, (xc, y), bajada, SERIF_I, 28, fill=MUTED,
            max_ancho=W - 2 * MARGEN - 40, interlinea=1.45, anchor_x="m")

    pie(d, nota=nota)
    return img


def dato(numero, titulo, cuerpo="", kicker=None, nota=None, centrado=False):
    """El caballito del carrusel: número grande en serif, filete, título y
    cuerpo en columna angosta. `centrado=True` alinea todo al medio."""
    img, d = lienzo()
    cabezal(d, seccion=kicker)

    f = fit_font(d, str(numero), SERIF_B, W - 2 * MARGEN, 250, 90)
    alto_tit = alto_parrafo(d, titulo, SERIF_B, 42, W - 2 * MARGEN - 30, 1.24)
    alto_cue = alto_parrafo(d, cuerpo, SERIF, 26, W - 2 * MARGEN - 60, 1.5) if cuerpo else 0
    alto = int(f.size * 1.16) + 40 + alto_tit + (22 + alto_cue if cuerpo else 0)

    y = _y_centrado(alto)
    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    d.text((xc if centrado else MARGEN - 6, y), str(numero), font=f, fill=TINTA,
           anchor=ax + "a")
    y += int(f.size * 1.16)

    if centrado:
        filete(d, y, x0=W / 2 - 75, x1=W / 2 + 75, grosor=3)
    else:
        filete(d, y, x1=MARGEN + 150, grosor=3)
    y += 40

    y = parrafo(d, (xc, y), titulo, SERIF_B, 42, fill=TINTA,
                max_ancho=W - 2 * MARGEN - 30, interlinea=1.24, anchor_x=ax)
    if cuerpo:
        y += 22
        parrafo(d, (xc, y), cuerpo, SERIF, 26, fill=MUTED,
                max_ancho=W - 2 * MARGEN - 60, interlinea=1.5, anchor_x=ax)

    pie(d, nota=nota)
    return img


def tabla(titulo, bajada, filas, kicker=None, nota=None, destacar=None, centrado=False):
    """Tabla de datos al estilo de una tabla de diario: filas separadas por
    filetes suaves. `filas` = [(etiqueta, valor), ...]. Por defecto etiqueta a
    la izquierda y valor a la derecha; con `centrado=True` cada fila sale como
    una sola línea 'etiqueta   valor' centrada, y título/bajada al medio."""
    img, d = lienzo()
    cabezal(d, seccion=kicker)

    f = fit_font(d, titulo, SERIF_B, W - 2 * MARGEN, 62, 36)
    alto_fila = 74
    total = int(f.size * 1.18) + (46 if bajada else 0) + 18 + len(filas) * alto_fila

    y = _y_centrado(total)
    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    d.text((xc, y), titulo, font=f, fill=TINTA, anchor=ax + "a")
    y += int(f.size * 1.18)
    if bajada:
        texto(d, (xc, y), bajada, SERIF_I, 25, fill=MUTED, anchor=ax + "a")
        y += 46

    y += 18
    filete(d, y, grosor=3)
    y += 1

    alto = alto_fila
    f_etq = fuente(SERIF, 27)
    for etq, val in filas:
        y += alto
        resaltar = (destacar is not None and etq == destacar)
        cy = y - alto / 2 + 4
        if centrado:
            f_val = fuente(SERIF_B if resaltar else SERIF, 29)
            lbl = etq + "   "
            w_lbl = _ancho(d, lbl, f_etq)
            w_val = _ancho(d, val, f_val)
            x0 = W / 2 - (w_lbl + w_val) / 2
            d.text((x0, cy), lbl, font=f_etq, fill=TINTA if resaltar else MUTED, anchor="lm")
            d.text((x0 + w_lbl, cy), val, font=f_val,
                   fill=ACENTO if resaltar else TINTA, anchor="lm")
        else:
            texto(d, (MARGEN + 4, cy), etq, SERIF, 27,
                  fill=TINTA if resaltar else MUTED, anchor="lm")
            texto(d, (W - MARGEN - 4, cy), val,
                  SERIF_B if resaltar else SERIF, 29,
                  fill=ACENTO if resaltar else TINTA, anchor="rm")
        filete(d, y, grosor=1, color=FILETE_S)

    pie(d, nota=nota)
    return img


def remate(frase, firma=None, nota=None):
    """Cierre: una frase grande en bastardilla, con comillas de imprenta."""
    img, d = lienzo()
    cabezal(d)

    alto_fr = alto_parrafo(d, frase, SERIF_I, 46, W - 2 * MARGEN - 20, 1.32)
    y0 = _y_centrado(134 + alto_fr + (56 if firma else 0))

    d.text((MARGEN - 10, y0), "“", font=fuente(SERIF_B, 170),
           fill=ACENTO, anchor="la")

    y = parrafo(d, (MARGEN, y0 + 134), frase, SERIF_I, 46, fill=TINTA,
                max_ancho=W - 2 * MARGEN - 20, interlinea=1.32)
    if firma:
        y += 30
        filete(d, y, x1=MARGEN + 110, grosor=3)
        texto(d, (MARGEN, y + 26), firma.upper(), SERIF_B, 19, fill=MUTED,
              anchor="la", tracking=4)

    pie(d, nota=nota)
    return img


def columna(titulo, parrafos, kicker=None, nota=None, centrado=False):
    """Nota corta al estilo de una columna de diario: título + varios párrafos.
    El primero va en redonda negra (lead), el resto en gris."""
    img, d = lienzo()
    cabezal(d, seccion=kicker)

    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    ancho = W - 2 * MARGEN
    alto_tit = alto_parrafo(d, titulo, SERIF_B, 46, ancho, 1.18)
    alt = [alto_parrafo(d, p, SERIF, 26, ancho, 1.5) + 26 for p in parrafos]
    y = _y_centrado(alto_tit + 34 + sum(alt))

    y = parrafo(d, (xc, y), titulo, SERIF_B, 46, fill=TINTA,
                max_ancho=ancho, interlinea=1.18, anchor_x=ax)
    y += 20
    if centrado:
        filete(d, y, x0=W / 2 - 75, x1=W / 2 + 75, grosor=3)
    else:
        filete(d, y, x1=MARGEN + 150, grosor=3)
    y += 30
    for i, p in enumerate(parrafos):
        y = parrafo(d, (xc, y), p, SERIF_I if i == 0 else SERIF, 26,
                    fill=TINTA if i == 0 else MUTED, max_ancho=ancho,
                    interlinea=1.5, anchor_x=ax)
        y += 26

    pie(d, nota=nota)
    return img


def _recortar_blanco(im, umbral=248, pad=6):
    """Recorta el marco blanco/casi-blanco de una figura de matplotlib."""
    from PIL import ImageChops
    fondo = Image.new("RGB", im.size, (255, 255, 255))
    dif = ImageChops.difference(im.convert("RGB"), fondo).convert("L")
    bbox = dif.point(lambda p: 255 if p > (255 - umbral) else 0).getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    return im.crop((max(0, x0 - pad), max(0, y0 - pad),
                    min(im.size[0], x1 + pad), min(im.size[1], y1 + pad)))


def _pegar_grafico(img, ruta_png, zona):
    """Pega la figura dentro de `zona` con un filete fino alrededor (aire de
    foto recortada de diario). Devuelve la caja ocupada."""
    x0, y0, x1, y1 = zona
    cw, ch = x1 - x0, y1 - y0
    g = _recortar_blanco(Image.open(ruta_png).convert("RGB"))
    g.thumbnail((cw, ch), Image.LANCZOS)
    gx = int(x0 + (cw - g.width) / 2)
    gy = int(y0 + (ch - g.height) / 2)
    img.paste(g, (gx, gy))
    ImageDraw.Draw(img).rectangle([gx - 1, gy - 1, gx + g.width, gy + g.height],
                                  outline=FILETE_S, width=1)
    return (gx, gy, gx + g.width, gy + g.height)


def grafico(ruta_png, titulo=None, subtitulo=None, kicker=None, nota=None,
            centrado=True):
    """Cabezal + título opcional + la figura en el espacio que queda."""
    img, d = lienzo()
    cabezal(d, seccion=kicker)
    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    y = CABEZAL_Y + 6
    if titulo:
        f = fit_font(d, titulo, SERIF_B, W - 2 * MARGEN, 44, 28)
        d.text((xc, y), titulo, font=f, fill=TINTA, anchor=ax + "a")
        y += int(f.size * 1.2)
    if subtitulo:
        y = parrafo(d, (xc, y), subtitulo, SERIF_I, 22, fill=MUTED,
                    max_ancho=W - 2 * MARGEN, interlinea=1.35, anchor_x=ax)
    if titulo or subtitulo:
        y += 16
    _pegar_grafico(img, ruta_png, (MARGEN - 14, y, W - MARGEN + 14, PIE_Y - 16))
    pie(d, nota=nota)
    return img


def grafico_full(ruta_png, nota=None, credito=None):
    """Sin cabezal: la figura ocupa casi toda la placa. Deja solo el filete de
    arriba, el pie y (opcional) un crédito arriba a la derecha."""
    img, d = lienzo()
    filete(d, MARGEN - 10, grosor=3)
    top = MARGEN + 6
    if credito:
        texto(d, (W - MARGEN, MARGEN - 34), credito.upper(), SERIF_B, 14,
              fill=ACENTO, anchor="ra", tracking=3)
    _pegar_grafico(img, ruta_png, (MARGEN - 20, top, W - MARGEN + 20,
                                   H - MARGEN - 20))
    texto(d, (MARGEN, H - MARGEN - 6), HANDLE, SERIF_I, 20, fill=TINTA, anchor="la")
    if nota:
        texto(d, (W - MARGEN, H - MARGEN - 2), nota, SERIF, 14, fill=MUTED,
              anchor="ra")
    return img


def guardar(img, ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    img.save(ruta, "PNG")
    return str(ruta)


def contact_sheet(carpeta, cols=3, lado=300):
    """Vista previa de todas las placas de la carpeta en una grilla."""
    carpeta = Path(carpeta)
    files = sorted(carpeta.glob("[0-9]*.png"))
    th = [Image.open(f).convert("RGB").resize((lado, lado)) for f in files]
    rows = (len(th) + cols - 1) // cols
    s = Image.new("RGB", (cols * lado + (cols + 1) * 10,
                          rows * lado + (rows + 1) * 10), (45, 45, 45))
    for i, t in enumerate(th):
        r, c = divmod(i, cols)
        s.paste(t, (10 + c * (lado + 10), 10 + r * (lado + 10)))
    s.save(carpeta / "_preview.png")
    return carpeta / "_preview.png"
