# -*- coding: utf-8 -*-
"""
ESTILO RIESGO — tercera identidad visual de la cuenta, para la categoria
"curiosidades" cuando el dato es de ALERTA (riesgo de descenso, rachas
negativas, etc.). NO reemplaza a las otras dos:

  - marca.py + placas.py   -> estandar de la cuenta (fondo negro, dorado)
  - estilo_diario.py       -> datos sueltos con aire de diario (papel, serif)
  - estilo_riesgo.py (ESTE)-> alerta: fondo blanco, franjas tipo cinta de
                               peligro en negro, rojo para lo que asusta

Autocontenido: no toca marca.py, placas.py ni estilo_diario.py.

    import estilo_riesgo as R
    img = R.dato("23%", "Probabilidad de descenso",
                 "Segun la simulacion de 100.000 temporadas...",
                 alerta=True, kicker="EL RIESGO")
    R.guardar(img, "salida/04.png")
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# LIENZO
# --------------------------------------------------------------------------
W = H = 1080
MARGEN = 88

# --------------------------------------------------------------------------
# PALETA — blanco, negro, un rojo de alerta (no el dorado de la marca).
# --------------------------------------------------------------------------
BLANCO  = (250, 250, 248)
NEGRO   = (15, 15, 15)
TINTA   = NEGRO
MUTED   = (65, 65, 63)
ROJO    = (196, 30, 30)          # #C41E1E — el color de "esto es un problema"
GRIS_L  = (225, 224, 219)        # filetes suaves sobre blanco

# --------------------------------------------------------------------------
# TIPOGRAFIAS — Segoe UI (misma familia que marca.py, look sans/moderno,
# a proposito distinto de la serif de estilo_diario.py).
# --------------------------------------------------------------------------
_F = Path("C:/Windows/Fonts")
SANS_BLACK = str(_F / "seguibl.ttf")
SANS_BOLD  = str(_F / "segoeuib.ttf")
SANS_SEMI  = str(_F / "seguisb.ttf")
SANS_REG   = str(_F / "segoeui.ttf")

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
def _ancho(d, s, font):
    return d.textbbox((0, 0), s, font=font)[2]


def fit_font(d, s, path, max_ancho, size_ini, size_min=22):
    size = size_ini
    while size > size_min:
        f = fuente(path, size)
        if d.textbbox((0, 0), s, font=f)[2] <= max_ancho:
            return f
        size -= 2
    return fuente(path, size_min)


def texto(d, xy, s, path, size, fill=TINTA, anchor="la", tracking=0):
    font = fuente(path, size)
    if tracking == 0:
        d.text(xy, s, font=font, fill=fill, anchor=anchor)
        return _ancho(d, s, font)
    x, y = xy
    total = sum(_ancho(d, c, font) for c in s) + tracking * (len(s) - 1)
    if anchor and anchor[0] == "m":
        x -= total / 2
    elif anchor and anchor[0] == "r":
        x -= total
    va = anchor[1] if len(anchor) > 1 else "a"
    for c in s:
        d.text((x, y), c, font=font, fill=fill, anchor="l" + va)
        x += _ancho(d, c, font) + tracking
    return total


def _lineas(d, s, path, size, max_ancho):
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


def alto_parrafo(d, s, path, size, max_ancho=None, interlinea=1.42):
    max_ancho = max_ancho or (W - 2 * MARGEN)
    return len(_lineas(d, s, path, size, max_ancho)) * int(size * interlinea)


def parrafo(d, xy, s, path, size, fill=TINTA, max_ancho=None, interlinea=1.42,
            anchor_x="l"):
    max_ancho = max_ancho or (W - 2 * MARGEN)
    x, y = xy
    dy = int(size * interlinea)
    for ln in _lineas(d, s, path, size, max_ancho):
        d.text((x, y), ln, font=fuente(path, size), fill=fill,
               anchor="ma" if anchor_x == "m" else "la")
        y += dy
    return y


def _texto_multicolor(d, xy, segmentos, path, size, anchor_x="l"):
    """segmentos = [(texto, color), ...] de UNA linea. Los concatena
    respetando el color de cada tramo (para resaltar una palabra en rojo
    dentro de un titulo)."""
    font = fuente(path, size)
    total = sum(_ancho(d, s, font) for s, _ in segmentos)
    x, y = xy
    if anchor_x == "m":
        x -= total / 2
    elif anchor_x == "r":
        x -= total
    for s, color in segmentos:
        d.text((x, y), s, font=font, fill=color, anchor="la")
        x += _ancho(d, s, font)
    return total


def franja_peligro(d, y0, y1, ancho_raya=24, paso=48, fondo=None):
    """Franja tipo cinta de peligro: rayas diagonales negras sobre el fondo
    (blanco por defecto). El "innovar con rayas o cuadrados negros" del
    pedido, pero tematico: cinta de peligro = exactamente lo que representa
    un post de riesgo de descenso."""
    if fondo:
        d.rectangle([0, y0, W, y1], fill=fondo)
    alto = y1 - y0
    despl = alto  # inclinacion ~45°
    x = -alto
    while x < W + alto:
        d.polygon([
            (x, y1), (x + ancho_raya, y1),
            (x + ancho_raya + despl, y0), (x + despl, y0),
        ], fill=NEGRO)
        x += paso


def lienzo():
    img = Image.new("RGB", (W, H), BLANCO)
    return img, ImageDraw.Draw(img)


# --------------------------------------------------------------------------
# ELEMENTOS FIJOS: cabezal (con cinta de peligro) y pie
# --------------------------------------------------------------------------
FRANJA_ALTO = 20
CABEZAL_Y = MARGEN + FRANJA_ALTO + 126    # donde termina el cabezal (deja lugar
                                           # al kicker centrado en 3 lineas)
PIE_Y = H - MARGEN - FRANJA_ALTO - 40     # donde arranca el pie


def cabezal(d, kicker=None, centrado=False):
    franja_peligro(d, 0, FRANJA_ALTO)
    y = FRANJA_ALTO + 28
    if centrado:
        texto(d, (W / 2, y), "CHACO FOR EVER", SANS_BLACK, 38, fill=NEGRO, anchor="ma")
        texto(d, (W / 2, y + 48), "ESTADÍSTICAS", SANS_SEMI, 19, fill=ROJO,
              anchor="ma", tracking=2)
        if kicker:
            texto(d, (W / 2, y + 86), kicker.upper(), SANS_SEMI, 20,
                  fill=MUTED, anchor="ma", tracking=2)
    else:
        texto(d, (MARGEN, y), "CHACO FOR EVER", SANS_BLACK, 30, fill=NEGRO)
        texto(d, (MARGEN, y + 38), "ESTADÍSTICAS", SANS_SEMI, 15, fill=ROJO, tracking=2)
        if kicker:
            texto(d, (W - MARGEN, y + 10), kicker.upper(), SANS_SEMI, 17,
                  fill=MUTED, anchor="ra", tracking=2)


def pie(d, nota=None, centrado=False):
    y = PIE_Y
    if centrado:
        d.rectangle([W / 2 - 30, y, W / 2 + 30, y + 4], fill=ROJO)
        texto(d, (W / 2, y + 18), HANDLE, SANS_SEMI, 27, fill=NEGRO, anchor="ma")
        if nota:
            texto(d, (W / 2, y + 54), nota, SANS_REG, 20, fill=MUTED, anchor="ma")
    else:
        d.rectangle([MARGEN, y, MARGEN + 60, y + 4], fill=ROJO)
        texto(d, (MARGEN, y + 18), HANDLE, SANS_SEMI, 21, fill=NEGRO, anchor="la")
        if nota:
            texto(d, (W - MARGEN, y + 20), nota, SANS_REG, 16, fill=MUTED, anchor="ra")
    franja_peligro(d, H - FRANJA_ALTO, H)


def _y_centrado(alto_bloque, sesgo_arriba=0.22):
    """Reparte el espacio libre entre el cabezal y el contenido, pero NO a la
    mitad: `sesgo_arriba` (0-1) es la fraccion del espacio libre que queda
    ARRIBA (el resto abajo). 0.5 = centrado clasico; menos que eso acerca el
    contenido al cabezal, que es lo que se quiere en todas las placas."""
    libre = (PIE_Y - CABEZAL_Y) - alto_bloque
    return CABEZAL_Y + max(libre * sesgo_arriba, 0)


# --------------------------------------------------------------------------
# PLACAS
# --------------------------------------------------------------------------
def portada(kicker, titulo_lineas, bajada=None, nota=None, centrado=False):
    """Tapa. `titulo_lineas` = lista de lineas, cada linea una lista de
    (texto, color) para poder resaltar una palabra puntual (ej. "DESCENSO"
    en rojo) sin tocar el resto del titulo. `bajada` es OPCIONAL: si se
    omite, el titulo crece para ocupar el lugar que dejaba libre.
    `centrado=True` centra kicker, titulo, filete y bajada."""
    img, d = lienzo()
    cabezal(d, centrado=centrado)

    size_ini = 92 if bajada else 116
    f = fit_font(d, max((t for ln in titulo_lineas for t, _ in ln), key=len),
                 SANS_BLACK, W - 2 * MARGEN, size_ini, 48)
    alto_baj = alto_parrafo(d, bajada, SANS_SEMI, 28, W - 2 * MARGEN, 1.42) if bajada else 0
    alto = 46 + len(titulo_lineas) * int(f.size * 1.08) + 30 + (28 + alto_baj if bajada else 0)

    y = _y_centrado(alto)
    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    texto(d, (xc, y), kicker.upper(), SANS_SEMI, 24, fill=ROJO,
          anchor=ax + "a", tracking=3)
    y += 46

    for ln in titulo_lineas:
        _texto_multicolor(d, (xc, y), ln, SANS_BLACK, f.size, anchor_x=ax)
        y += int(f.size * 1.08)

    y += 30
    if centrado:
        d.rectangle([W / 2 - 65, y, W / 2 + 65, y + 5], fill=NEGRO)
    else:
        d.rectangle([MARGEN, y, MARGEN + 130, y + 5], fill=NEGRO)
    if bajada:
        y += 28
        parrafo(d, (xc, y), bajada, SANS_SEMI, 28, fill=MUTED,
                max_ancho=W - 2 * MARGEN, interlinea=1.42, anchor_x=ax)

    pie(d, nota=nota, centrado=centrado)
    return img


def explicacion(titulo, parrafos, kicker="CÓMO SE HIZO", nota=None, centrado=False):
    """Slide de metodologia para el publico general: titulo + varios
    parrafos cortos en columna. `parrafos` = lista de strings. El PRIMER
    parrafo sale en negrita (a modo de lead/bajada), el resto en semibold."""
    img, d = lienzo()
    cabezal(d, kicker=kicker, centrado=centrado)

    alto_tit = alto_parrafo(d, titulo, SANS_BLACK, 44, W - 2 * MARGEN, 1.18)
    alto_par = sum(
        alto_parrafo(d, p, SANS_BOLD if i == 0 else SANS_SEMI, 27,
                    W - 2 * MARGEN, 1.48) + 24
        for i, p in enumerate(parrafos))
    alto = alto_tit + 30 + alto_par

    y = _y_centrado(alto)
    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    y = parrafo(d, (xc, y), titulo, SANS_BLACK, 44, fill=NEGRO,
                max_ancho=W - 2 * MARGEN, interlinea=1.18, anchor_x=ax)
    y += 30
    for i, p in enumerate(parrafos):
        fuente_p = SANS_BOLD if i == 0 else SANS_SEMI
        color_p = NEGRO if i == 0 else MUTED
        y = parrafo(d, (xc, y), p, fuente_p, 27, fill=color_p,
                    max_ancho=W - 2 * MARGEN, interlinea=1.48, anchor_x=ax)
        y += 24

    pie(d, nota=nota, centrado=centrado)
    return img


def dato(numero, etiqueta, contexto="", kicker=None, nota=None, alerta=False,
         centrado=False):
    """El caballito: numero gigante (rojo si alerta=True, negro si no),
    etiqueta y contexto abajo."""
    img, d = lienzo()
    cabezal(d, kicker=kicker, centrado=centrado)

    color_num = ROJO if alerta else NEGRO
    f = fit_font(d, str(numero), SANS_BLACK, W - 2 * MARGEN, 260, 90)
    alto_etq = alto_parrafo(d, etiqueta, SANS_BOLD, 36, W - 2 * MARGEN, 1.22)
    alto_ctx = alto_parrafo(d, contexto, SANS_SEMI, 27, W - 2 * MARGEN - 20, 1.48) if contexto else 0
    alto = int(f.size * 1.12) + 34 + alto_etq + (20 + alto_ctx if contexto else 0)

    y = _y_centrado(alto)
    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    d.text((xc if centrado else MARGEN - 6, y), str(numero), font=f, fill=color_num,
           anchor=ax + "a")
    y += int(f.size * 1.12)

    if centrado:
        d.rectangle([W / 2 - 65, y, W / 2 + 65, y + 5], fill=color_num)
    else:
        d.rectangle([MARGEN, y, MARGEN + 130, y + 5], fill=color_num)
    y += 34

    y = parrafo(d, (xc, y), etiqueta, SANS_BOLD, 36, fill=NEGRO,
                max_ancho=W - 2 * MARGEN, interlinea=1.22, anchor_x=ax)
    if contexto:
        y += 20
        parrafo(d, (xc, y), contexto, SANS_SEMI, 27, fill=MUTED,
                max_ancho=W - 2 * MARGEN - 20, interlinea=1.48, anchor_x=ax)

    pie(d, nota=nota, centrado=centrado)
    return img


def cierre(frase, nota=None, centrado=False):
    img, d = lienzo()
    cabezal(d, centrado=centrado)

    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    alto_fr = alto_parrafo(d, frase, SANS_BOLD, 40, W - 2 * MARGEN, 1.3)
    y = _y_centrado(alto_fr)
    parrafo(d, (xc, y), frase, SANS_BOLD, 40, fill=NEGRO,
            max_ancho=W - 2 * MARGEN, interlinea=1.3, anchor_x=ax)

    pie(d, nota=nota, centrado=centrado)
    return img


def grafico(ruta_png, titulo=None, subtitulo=None, kicker=None, nota=None,
            centrado=False):
    """Mete un grafico YA GENERADO (matplotlib, fondo claro) tal cual, sin
    tarjeta extra -- el fondo de estilo_riesgo ya es blanco, no hace falta
    "enmarcarlo" como en la paleta oscura. Para las figuras del pipeline de
    proyeccion (posicion_probabilidad.png, distribucion_puntos.png, etc.).

    `titulo` y `subtitulo` son opcionales: sin ellos la placa queda con el
    cabezal, el pie y NADA MAS que la figura, centrada en todo el espacio que
    sobra. Es el modo que usa el apendice de los carruseles, donde la figura ya
    trae su propio titulo adentro y repetirlo arriba es ruido."""
    img, d = lienzo()
    cabezal(d, kicker=kicker, centrado=centrado)

    ax = "m" if centrado else "l"
    xc = W / 2 if centrado else MARGEN
    y = CABEZAL_Y + 10
    if titulo:
        f = fit_font(d, titulo, SANS_BLACK, W - 2 * MARGEN, 40, 26)
        d.text((xc, y), titulo, font=f, fill=NEGRO, anchor=ax + "a")
        y += int(f.size * 1.2)
    if subtitulo:
        y = parrafo(d, (xc, y), subtitulo, SANS_SEMI, 22, fill=MUTED,
                    max_ancho=W - 2 * MARGEN, interlinea=1.35, anchor_x=ax)
    if titulo or subtitulo:
        y += 18

    zona = (MARGEN - 20, y, W - MARGEN + 20, PIE_Y - 20)
    graf = Image.open(ruta_png).convert("RGB")
    cw, ch = zona[2] - zona[0], zona[3] - zona[1]
    graf.thumbnail((cw, ch), Image.LANCZOS)
    gx = zona[0] + (cw - graf.width) // 2
    gy = zona[1] + max(ch - graf.height, 0) // 2
    img.paste(graf, (gx, gy))

    pie(d, nota=nota, centrado=centrado)
    return img


def _recortar_blanco(im, umbral=248, pad=6):
    """Recorta el borde blanco/casi-blanco de una figura de matplotlib para
    que el contenido ocupe más. Si no encuentra nada, devuelve la imagen tal
    cual."""
    from PIL import ImageChops
    fondo = Image.new("RGB", im.size, (255, 255, 255))
    dif = ImageChops.difference(im, fondo).convert("L")
    bbox = dif.point(lambda p: 255 if p > (255 - umbral) else 0).getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(im.size[0], x1 + pad); y1 = min(im.size[1], y1 + pad)
    return im.crop((x0, y0, x1, y1))


def grafico_full(ruta_png, nota=None, credito=None):
    """Igual que `grafico` pero SIN cabezal: la figura ocupa casi toda la placa.
    Para el apéndice de gráficos del modelo, donde cada figura ya trae su propio
    título adentro y el cabezal "CHACO FOR EVER / ESTADÍSTICAS" arriba es ruido
    que come espacio. Deja solo las dos cintas de peligro y el handle abajo.
    `credito` = etiqueta chica arriba a la derecha (ej. 'El modelo completo')."""
    img, d = lienzo()
    franja_peligro(d, 0, FRANJA_ALTO)
    franja_peligro(d, H - FRANJA_ALTO, H)

    top = FRANJA_ALTO + 10
    bot = H - FRANJA_ALTO - 44           # deja una línea para el handle
    zona = (8, top, W - 8, bot)
    cw, ch = zona[2] - zona[0], zona[3] - zona[1]
    graf = Image.open(ruta_png).convert("RGB")
    graf = _recortar_blanco(graf)        # saca el marco blanco de matplotlib
    graf.thumbnail((cw, ch), Image.LANCZOS)
    gx = zona[0] + (cw - graf.width) // 2
    gy = zona[1] + (ch - graf.height) // 2
    img.paste(graf, (gx, gy))

    if credito:
        texto(d, (W - MARGEN, top + 2), credito.upper(), SANS_SEMI, 15,
              fill=MUTED, anchor="ra", tracking=2)
    y = H - FRANJA_ALTO - 34
    texto(d, (MARGEN, y), HANDLE, SANS_SEMI, 19, fill=NEGRO, anchor="la")
    if nota:
        texto(d, (W - MARGEN, y + 2), nota, SANS_REG, 14, fill=MUTED, anchor="ra")
    return img


def guardar(img, ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    img.save(ruta, "PNG")
    return str(ruta)


def contact_sheet(carpeta, cols=3, lado=300):
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
