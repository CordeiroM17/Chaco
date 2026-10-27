# -*- coding: utf-8 -*-
"""
ESTILO FIESTA — la variante festiva de `estilo_diario.py`.

Misma base (papel, Georgia, filetes, resaltado inline **rojo** / *negrita*)
para que se lea como de la misma familia que el carrusel de Cravero, pero con
tres cosas de festejo encima:

  - bastones blancos y negros arriba y abajo (la camiseta),
  - papel picado (confeti) en los bordes, en negro, rojo de imprenta y dorado,
  - el cabezal dice "EDICIÓN ESPECIAL" en vez de "ESTADÍSTICAS DEL NEGRO".

Además trae placas propias: `portada_foto` (tapa oscura con mosaico de fotos),
`foto_texto` (foto arriba + texto abajo) y `nombres` (grilla de nombres para
agradecer al plantel).

NO modifica estilo_diario.py en disco: reemplaza `D.cabezal` en memoria
mientras este módulo está importado, así que importarlo solo afecta al
carrusel que lo usa.

    import estilo_fiesta as F
    img = F.dato("19", "Jornadas seguidas en zona de descenso", "...")
    F.guardar(img, "salida/02.png")
"""
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFilter

import estilo_diario as D

W, H, MARGEN = D.W, D.H, D.MARGEN
PAPEL, TINTA, MUTED, ACENTO = D.PAPEL, D.TINTA, D.MUTED, D.ACENTO
DORADO = (232, 178, 58)            # el acento de la marca de la cuenta
BLANCO = (250, 249, 245)
SERIF, SERIF_B, SERIF_I, SERIF_BI = D.SERIF, D.SERIF_B, D.SERIF_I, D.SERIF_BI
fuente, texto, parrafo, filete = D.fuente, D.texto, D.parrafo, D.filete
guardar, contact_sheet = D.guardar, D.contact_sheet

BASTON = 30                        # ancho de cada bastón de la franja
FRANJA = 16                        # alto de la franja de bastones


# --------------------------------------------------------------------------
# ADORNOS
# --------------------------------------------------------------------------
def bastones(img, y0, alto=FRANJA, claro=BLANCO, oscuro=TINTA):
    d = ImageDraw.Draw(img)
    for i, x in enumerate(range(0, W, BASTON)):
        d.rectangle([x, y0, x + BASTON - 1, y0 + alto - 1],
                    fill=oscuro if i % 2 == 0 else claro)


def confeti(img, semilla=7, n=70, colores=None, zona="bordes", evitar=None):
    """Papel picado. `zona="bordes"` lo deja en la franja exterior (no pisa el
    texto); `zona="todo"` lo reparte por toda la placa (para la tapa)."""
    colores = colores or [TINTA, ACENTO, DORADO, DORADO, (120, 112, 98)]
    rnd = random.Random(semilla)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    puestos = 0
    while puestos < n:
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        if zona == "bordes":
            borde = min(x, W - x, y, H - y)
            if borde > MARGEN - 18 or borde < FRANJA + 4 and (y < 40 or y > H - 40):
                continue
        if evitar and evitar[0] < x < evitar[2] and evitar[1] < y < evitar[3]:
            continue
        c = rnd.choice(colores)
        pieza = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pieza)
        forma = rnd.random()
        if forma < 0.55:                     # tira
            w, h = rnd.randint(6, 9), rnd.randint(16, 24)
            pd.rectangle([20 - w / 2, 20 - h / 2, 20 + w / 2, 20 + h / 2], fill=c)
        elif forma < 0.85:                   # círculo
            r = rnd.randint(4, 7)
            pd.ellipse([20 - r, 20 - r, 20 + r, 20 + r], fill=c)
        else:                                # triangulito
            r = rnd.randint(7, 10)
            pd.polygon([(20, 20 - r), (20 + r, 20 + r), (20 - r, 20 + r)], fill=c)
        pieza = pieza.rotate(rnd.uniform(0, 360), resample=Image.BICUBIC)
        capa.alpha_composite(pieza, (int(x) - 20, int(y) - 20))
        puestos += 1
    base = img.convert("RGBA")
    base.alpha_composite(capa)
    return base.convert("RGB")


def _cabezal_fiesta(d, seccion=None):
    filete(d, MARGEN, grosor=4)
    texto(d, (W / 2, MARGEN + 20), "CHACO FOR EVER", SERIF_B, 27,
          fill=TINTA, anchor="ma", tracking=7)
    filete(d, MARGEN + 66, grosor=1, color=D.FILETE_S)
    texto(d, (MARGEN, MARGEN + 76), "EDICIÓN ESPECIAL", SERIF_B, 15,
          fill=ACENTO, anchor="la", tracking=3)
    if seccion:
        texto(d, (W - MARGEN, MARGEN + 76), seccion.upper(), SERIF_B, 15,
              fill=ACENTO, anchor="ra", tracking=3)


D.cabezal = _cabezal_fiesta        # todas las placas de D salen con este cabezal


def festejar(img, semilla=7):
    """Hoy no agrega adornos (sin confeti ni bastones); queda el gancho por si se quiere volver."""
    return img


# --------------------------------------------------------------------------
# PLACAS DE estilo_diario, YA FESTEJADAS
# --------------------------------------------------------------------------
def dato(*a, semilla=11, **k):
    return festejar(D.dato(*a, **k), semilla)


def tabla(*a, semilla=12, **k):
    return festejar(D.tabla(*a, **k), semilla)


def columna(*a, semilla=13, **k):
    return festejar(D.columna(*a, **k), semilla)


def remate(frase, firma=None, nota=None, semilla=14):
    """Frase de cierre en bastardilla, SIN comillas (para que no parezca una
    cita textual)."""
    img, d = D.lienzo()
    D.cabezal(d)
    ancho = W - 2 * MARGEN - 20
    alto_fr = D.alto_parrafo(d, frase, SERIF_I, 50, ancho, 1.32)
    y0 = D._y_centrado(alto_fr + (56 if firma else 0))
    y = parrafo(d, (MARGEN, y0), frase, SERIF_I, 50, fill=TINTA,
                max_ancho=ancho, interlinea=1.32)
    if firma:
        y += 30
        filete(d, y, x1=MARGEN + 110, grosor=3)
        texto(d, (MARGEN, y + 26), firma.upper(), SERIF_B, 19, fill=MUTED,
              anchor="la", tracking=4)
    D.pie(d, nota=nota)
    return festejar(img, semilla)


def grafico(*a, semilla=15, **k):
    return festejar(D.grafico(*a, **k), semilla)


# --------------------------------------------------------------------------
# PLACAS NUEVAS
# --------------------------------------------------------------------------
def _crop(img, bw, bh, fx=0.5, fy=0.5, zoom=1.0):
    iw, ih = img.size
    t = bw / bh
    nw, nh = (int(ih * t), ih) if iw / ih > t else (iw, int(iw / t))
    nw, nh = int(nw / zoom), int(nh / zoom)
    x = max(0, min(int((iw - nw) * fx), iw - nw))
    y = max(0, min(int((ih - nh) * fy), ih - nh))
    return img.crop((x, y, x + nw, y + nh)).resize((bw, bh), Image.LANCZOS)


def _bn(img, oscuro=(14, 13, 11), claro=(236, 232, 222)):
    g = ImageOps.grayscale(ImageOps.autocontrast(img.convert("RGB"), cutoff=1))
    return ImageOps.colorize(g, black=oscuro, white=claro)


def _velo(size, top_a, bot_a, color=(10, 9, 8)):
    w, h = size
    col = Image.new("L", (1, h))
    for yy in range(h):
        col.putpixel((0, yy), int(top_a + (bot_a - top_a) * (yy / (h - 1)) ** 1.6))
    alfa = col.resize((w, h))
    capa = Image.new("RGBA", size, color + (0,))
    capa.putalpha(alfa)
    return capa


def portada_foto(fotos, volanta):
    """Tapa festiva: mosaico de fotos en blanco y negro (paneles verticales
    separados por un hilo dorado) y una sola cinta dorada con la `volanta`,
    centrada a 3/4 de altura (28% desde arriba, a la altura del dedo de la foto derecha). Sin titular ni bajada.
    `fotos` = [(ruta, fx, fy, zoom), ...] — fx/fy eligen el encuadre."""
    img = Image.new("RGB", (W, H), (12, 11, 10))
    n = len(fotos)
    hilo = 6
    pw = (W - hilo * (n - 1)) // n
    x = 0
    for i, (ruta, fx, fy, zoom) in enumerate(fotos):
        ancho = pw if i < n - 1 else W - x
        f = _crop(Image.open(ruta), ancho, H, fx, fy, zoom)
        img.paste(_bn(f), (x, 0))
        x += ancho
        if i < n - 1:
            ImageDraw.Draw(img).rectangle([x, 0, x + hilo - 1, H], fill=DORADO)
            x += hilo

    base = img.convert("RGBA")
    base.alpha_composite(_velo((W, H), 60, 170))
    img = base.convert("RGB")
    d = ImageDraw.Draw(img)

    # cinta dorada centrada, a 3/4 de altura
    size, trk = 38, 8
    fv = fuente(SERIF_B, size)
    tw = D._ancho(d, volanta.upper(), fv, trk)
    cy = int(H * 0.28)
    pad_x, pad_y = 34, 26
    d.rectangle([W / 2 - tw / 2 - pad_x, cy - size / 2 - pad_y,
                 W / 2 + tw / 2 + pad_x, cy + size / 2 + pad_y], fill=DORADO)
    texto(d, (W / 2, cy), volanta.upper(), SERIF_B, size, fill=TINTA,
          anchor="mm", tracking=trk)

    # marca arriba a la izquierda
    texto(d, (MARGEN, MARGEN - 40), "CHACO FOR EVER", SERIF_B, 24,
          fill=BLANCO, anchor="la", tracking=7)
    # instagram abajo a la derecha, sobre un chip claro para que no se pierda
    fh = fuente(SERIF_I, 23)
    tw = D._ancho(d, D.HANDLE, fh)
    xr, yb = W - MARGEN + 10, H - MARGEN + 14
    d.rounded_rectangle([xr - tw - 28, yb - 40, xr, yb], radius=8,
                        fill=(236, 232, 222))
    texto(d, (xr - 14, yb - 20), D.HANDLE, SERIF_I, 23, fill=TINTA, anchor="rm")
    return img


def foto_texto(ruta, titulo, cuerpo, kicker=None, nota=None, fx=0.5, fy=0.4,
               zoom=1.0, alto_foto=470, semilla=16):
    """Foto apaisada arriba (con filete, como foto de diario) y debajo título +
    cuerpo centrados. Para el agradecimiento al cuerpo técnico."""
    img, d = D.lienzo()
    D.cabezal(d, seccion=kicker)
    y = D.CABEZAL_Y + 4
    ancho = W - 2 * MARGEN
    foto = _crop(Image.open(ruta).convert("RGB"), ancho, alto_foto, fx, fy, zoom)
    img.paste(foto, (MARGEN, y))
    d.rectangle([MARGEN - 1, y - 1, MARGEN + ancho, y + alto_foto], outline=D.FILETE, width=2)
    y += alto_foto + 34

    alto_tit = D.alto_parrafo(d, titulo, SERIF_B, 46, ancho - 20, 1.2)
    alto_cue = D.alto_parrafo(d, cuerpo, SERIF, 25, ancho - 30, 1.48)
    libre = D.PIE_Y - y - (alto_tit + 18 + alto_cue)
    y += max(libre / 2 - 6, 0)
    y = parrafo(d, (W / 2, y), titulo, SERIF_B, 46, fill=TINTA,
                max_ancho=ancho - 20, interlinea=1.2, anchor_x="m")
    y += 18
    parrafo(d, (W / 2, y), cuerpo, SERIF, 25, fill=MUTED,
            max_ancho=ancho - 30, interlinea=1.48, anchor_x="m")
    D.pie(d, nota=nota)
    return festejar(img, semilla)


def nombres(titulo, bajada, lista, destacados=(), kicker=None, nota=None,
            cols=3, semilla=17):
    """Grilla de nombres centrada (el 'gracias' al plantel). Los de
    `destacados` salen en negrita roja."""
    img, d = D.lienzo()
    D.cabezal(d, seccion=kicker)
    ancho = W - 2 * MARGEN
    ft = D.fit_font(d, titulo, SERIF_B, ancho, 58, 34)
    filas = (len(lista) + cols - 1) // cols
    paso = min(52, int((D.PIE_Y - D.CABEZAL_Y - 170) / max(filas, 1)))
    size = min(28, paso - 16)
    alto = int(ft.size * 1.2) + 44 + 30 + filas * paso
    y = D._y_centrado(alto)
    d.text((W / 2, y), titulo, font=ft, fill=TINTA, anchor="ma")
    y += int(ft.size * 1.2)
    texto(d, (W / 2, y), bajada, SERIF_I, 24, fill=MUTED, anchor="ma")
    y += 44
    filete(d, y, x0=W / 2 - 75, x1=W / 2 + 75, grosor=3)
    y += 30
    cw = ancho / cols
    for i, nom in enumerate(lista):
        r, c = divmod(i, cols)
        dest = nom in destacados
        texto(d, (MARGEN + cw * c + cw / 2, y + r * paso), nom,
              SERIF_B if dest else SERIF, size,
              fill=ACENTO if dest else TINTA, anchor="ma")
    D.pie(d, nota=nota)
    return festejar(img, semilla)
