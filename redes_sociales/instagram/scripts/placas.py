# -*- coding: utf-8 -*-
"""
Generador de placas 1080x1080 para la cuenta de estadisticas de Chaco For Ever.

Cada funcion devuelve una imagen PIL lista para publicar. Los carruseles se
arman llamando varias de estas en orden y guardandolas 01, 02, 03...

Ejecutar directamente para regenerar los ejemplos:
    python scripts/placas.py
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw
import marca as M
from marca import (W, H, MARGEN, NEGRO, CARBON, TINTA, BLANCO, DORADO,
                   DORADO_OSC, GRIS, GRIS_OSC, CHIP, F_BLACK, F_BOLD, F_SEMI,
                   F_REG, F_COND)

RAIZ = Path(__file__).resolve().parents[1]
EJEMPLOS = RAIZ / "placas" / "ejemplos"

# recuadro de la foto: MISMO tamaño en todas las placas (portada y trayectoria)
FOTO_BOX = (578, 360, W - 66, H - MARGEN - 60)      # 436 x 576


# --------------------------------------------------------------------------
# 1. PORTADA  (tapa de carrusel)
# --------------------------------------------------------------------------
def portada(titulo, subtitulo, etiqueta="ANALISIS", nota=None):
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=None)
    # rayas laterales completas como sello del club
    M.rayas(d, (0, 0, 22, H), n=3)
    M.rayas(d, (W - 22, 0, W, H), n=3)

    d.rectangle([MARGEN, 360, MARGEN + 90, 360 + 10], fill=DORADO)
    M.texto(d, (MARGEN, 300), etiqueta.upper(), F_SEMI, 26, fill=DORADO, tracking=8)

    # titulo grande, auto-ajustado por la palabra mas larga
    palabra_larga = max(titulo.upper().split(), key=len)
    f = M.fit_font(d, palabra_larga, F_BLACK, W - 2 * MARGEN, 128, 66)
    y_fin = M.parrafo(d, (MARGEN, 388), titulo.upper(), F_BLACK,
                      f.size, fill=TINTA, interlinea=1.02)
    M.parrafo(d, (MARGEN, y_fin + 44), subtitulo, F_REG, 34, fill=GRIS, interlinea=1.3)
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 2. DATO ESTRELLA  (un numero grande)
# --------------------------------------------------------------------------
def dato(numero, etiqueta, contexto="", kicker="EL DATO", nota=None):
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=kicker)
    # numero gigante centrado
    f = M.fit_font(d, str(numero), F_COND, W - 2 * MARGEN, 460, 140)
    d.text((W / 2, 470), str(numero), font=f, fill=DORADO, anchor="mm")
    M.linea_dorada(d, W / 2 - 70, 690, largo=140, grosor=6)
    M.parrafo(d, (W / 2, 730), etiqueta.upper(), F_BLACK, 46,
              fill=TINTA, interlinea=1.05, anchor_x="m")
    if contexto:
        M.parrafo(d, (W / 2, 840), contexto, F_REG, 28,
                  fill=GRIS, interlinea=1.3, anchor_x="m", max_ancho=W - 2 * MARGEN - 40)
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 3. RANKING  (top de jugadores / equipos)
# --------------------------------------------------------------------------
def ranking(titulo, filas, subtitulo="", unidad="", nota=None, destacar=0, piso=0):
    """filas = [(nombre, valor), ...] ya ordenadas de mayor a menor.
    piso: valor base de la barra (para escalas comprimidas como el rating,
    donde 0 aplastaría las diferencias). Por defecto arranca en 0."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker="RANKING")
    M.texto(d, (MARGEN, 190), titulo.upper(), F_BLACK, 54, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 258), subtitulo, F_REG, 26, fill=GRIS)

    filas = filas[:6]
    vmax = max((v for _, v in filas), default=1) or 1
    y = 330
    alto = 96
    nombre_x = MARGEN + 70          # columna de nombres
    bar_x = 560                     # las barras arrancan despues del nombre
    bar_w = W - MARGEN - bar_x - 150  # reserva a la derecha para que la barra no toque el valor
    for i, (nombre, valor) in enumerate(filas):
        top = (i == destacar)
        cbar = DORADO if top else GRIS_OSC
        ctxt = TINTA if top else GRIS
        # posicion
        M.texto(d, (MARGEN, y + alto / 2), str(i + 1), F_BLACK, 46,
                fill=DORADO if top else GRIS_OSC, anchor="lm")
        # nombre (se achica si no entra en su columna)
        fn = M.fit_font(d, nombre, F_BOLD, bar_x - nombre_x - 30, 34, 22)
        d.text((nombre_x, y + alto / 2), nombre, font=fn, fill=ctxt, anchor="lm")
        # barra proporcional (con piso opcional para escalas comprimidas)
        denom = (vmax - piso) or 1
        w = int(bar_w * max(0.08, (valor - piso) / denom))
        d.rounded_rectangle([bar_x, y + alto / 2 - 14, bar_x + max(w, 6),
                             y + alto / 2 + 14], radius=7, fill=cbar)
        # valor
        vtxt = f"{valor}{unidad}"
        M.texto(d, (W - MARGEN, y + alto / 2), vtxt, F_BLACK, 38,
                fill=ctxt, anchor="rm")
        y += alto + 8
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 4. RESULTADO  (marcador de partido)
# --------------------------------------------------------------------------
def resultado(local, gl, visitante, gv, torneo="PRIMERA NACIONAL",
              detalle="", nota=None, logo_local=None, logo_visitante=None):
    """Marcador. Si se pasan 'logo_local'/'logo_visitante' (rutas a PNG de los
    escudos) los dibuja flanqueando el resultado sobre un chip claro (para que
    se lean sobre el fondo negro). El ganador va resaltado en dorado."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=None)
    M.texto(d, (W / 2, 210), torneo.upper(), F_SEMI, 24, fill=DORADO,
            anchor="mm", tracking=6)

    gan_l = gl > gv
    gan_v = gv > gl
    y_mid = 452

    # escudos flanqueando el marcador (chip claro: los escudos oscuros no se
    # perderían sobre el negro). Si no hay logo, no se dibuja nada.
    S = 168
    if logo_local:
        _logo_chip(img, d, logo_local, W / 2 - 330 - S / 2, y_mid - S / 2, S,
                   ring=DORADO if gan_l else None)
    if logo_visitante:
        _logo_chip(img, d, logo_visitante, W / 2 + 330 - S / 2, y_mid - S / 2, S,
                   ring=DORADO if gan_v else None)

    # marcador (un poco más chico que sin escudos, para que respire)
    fnum = 220 if (logo_local or logo_visitante) else 300
    off = 120 if (logo_local or logo_visitante) else 150
    d.text((W / 2 - off, y_mid), str(gl), font=M.fuente(F_COND, fnum),
           fill=DORADO if gan_l else TINTA, anchor="mm")
    d.text((W / 2, y_mid), "-", font=M.fuente(F_BLACK, 90), fill=GRIS_OSC, anchor="mm")
    d.text((W / 2 + off, y_mid), str(gv), font=M.fuente(F_COND, fnum),
           fill=DORADO if gan_v else TINTA, anchor="mm")

    fl = M.fit_font(d, local.upper(), F_BOLD, 380, 40, 22)
    d.text((W / 2 - 150, 662), local.upper(), font=fl,
           fill=TINTA if gan_l else GRIS, anchor="mm")
    fv = M.fit_font(d, visitante.upper(), F_BOLD, 380, 40, 22)
    d.text((W / 2 + 150, 662), visitante.upper(), font=fv,
           fill=TINTA if gan_v else GRIS, anchor="mm")

    if detalle:
        M.parrafo(d, (W / 2, 752), detalle, F_REG, 28, fill=GRIS,
                  interlinea=1.3, anchor_x="m", max_ancho=W - 2 * MARGEN - 40)
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 4b. FICHA  (grilla de estadisticas generales)
# --------------------------------------------------------------------------
def ficha(titulo, subtitulo, filas, nota=None, destacar=None):
    """Grilla de datos generales. filas = [(etiqueta, valor), ...].
    'destacar' = etiqueta cuyo valor va en dorado (ej. la posicion)."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker="LA FICHA")
    M.texto(d, (MARGEN, 190), titulo.upper(), F_BLACK, 56, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 262), subtitulo, F_REG, 27, fill=GRIS)
    M.linea_dorada(d, MARGEN, 320, largo=120, grosor=6)

    filas = filas[:8]
    y = 380
    alto = (H - MARGEN - 90 - y) / len(filas)
    for etiqueta, valor in filas:
        top = (destacar is not None and etiqueta == destacar)
        M.texto(d, (MARGEN, y + alto / 2), etiqueta, F_SEMI, 30, fill=GRIS, anchor="lm")
        fv = M.fit_font(d, str(valor), F_BLACK, 430, 44, 26)
        d.text((W - MARGEN, y + alto / 2), str(valor), font=fv,
               fill=DORADO if top else TINTA, anchor="rm")
        d.line([MARGEN, y + alto, W - MARGEN, y + alto], fill=GRIS_OSC, width=2)
        y += alto
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 4c. DATO + COMPARACION  (numero mediano arriba, dos tarjetas enfrentadas)
# --------------------------------------------------------------------------
def dato_vs(hero, hero_sub, col_izq, col_der, kicker=None, franja=None, nota=None):
    """Numero mediano arriba + dos tarjetas comparadas abajo (visual, sin párrafo).
    col_izq / col_der = (titulo, valor_grande, valor_chico). La izquierda se resalta."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=kicker)

    # numero mediano (mas chico que en 'dato')
    d.text((W / 2, 300), str(hero), font=M.fuente(F_COND, 200), fill=DORADO, anchor="mm")
    M.parrafo(d, (W / 2, 408), hero_sub, F_SEMI, 32, fill=TINTA,
              interlinea=1.2, anchor_x="m", max_ancho=W - 2 * MARGEN - 40)

    # dos tarjetas enfrentadas
    y0, y1, gap = 520, 838, 28
    cw = (W - 2 * MARGEN - gap) / 2
    cajas = [(MARGEN, col_izq, True),
             (MARGEN + cw + gap, col_der, False)]
    for x0, col, top in cajas:
        x1 = x0 + cw
        titulo, grande, chico = col
        d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=CARBON,
                            outline=DORADO if top else GRIS_OSC, width=3 if top else 2)
        cx = (x0 + x1) / 2
        M.texto(d, (cx, y0 + 50), titulo.upper(), F_SEMI, 26,
                fill=DORADO if top else GRIS, anchor="mm", tracking=4)
        d.text((cx, y0 + 158), str(grande), font=M.fuente(F_BLACK, 78),
               fill=DORADO if top else TINTA, anchor="mm")
        M.texto(d, (cx, y0 + 248), chico, F_SEMI, 34, fill=GRIS, anchor="mm")

    if franja:
        M.texto(d, (W / 2, 902), franja.upper(), F_SEMI, 24, fill=DORADO,
                anchor="mm", tracking=3)
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 5. CITA / FRASE  (para storytelling)
# --------------------------------------------------------------------------
def cita(frase, autor="", nota=None):
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=None)
    d.text((MARGEN - 6, 300), "“", font=M.fuente(F_BLACK, 200),
           fill=DORADO, anchor="lm")
    y = M.parrafo(d, (MARGEN, 420), frase, F_BLACK, 52, fill=TINTA, interlinea=1.16)
    if autor:
        M.linea_dorada(d, MARGEN, y + 40, largo=90, grosor=6)
        M.texto(d, (MARGEN, y + 66), autor.upper(), F_SEMI, 26, fill=DORADO, tracking=4)
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 6. ENMARCAR UN GRAFICO EXISTENTE  (reusar los PNG del pipeline)
# --------------------------------------------------------------------------
def enmarcar(ruta_png, titulo, subtitulo="", nota="Fuente: SofaScore"):
    """Mete un grafico ya generado dentro de una placa con la marca."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=None)
    M.texto(d, (MARGEN, 180), titulo.upper(), F_BLACK, 48, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 244), subtitulo, F_REG, 26, fill=GRIS)
    M.linea_dorada(d, MARGEN, 300, largo=120, grosor=6)

    # tarjeta clara para el grafico
    caja = (MARGEN, 340, W - MARGEN, H - MARGEN - 70)
    d.rounded_rectangle(caja, radius=24, fill=(248, 248, 245))
    graf = Image.open(ruta_png).convert("RGB")
    cw, ch = caja[2] - caja[0] - 48, caja[3] - caja[1] - 48
    graf.thumbnail((cw, ch), Image.LANCZOS)
    gx = caja[0] + (caja[2] - caja[0] - graf.width) // 2
    gy = caja[1] + (caja[3] - caja[1] - graf.height) // 2
    img.paste(graf, (gx, gy))
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 8c. RED DE SOCIEDADES  (nodos + flechas asistente→goleador, ego de un jugador)
# --------------------------------------------------------------------------
def _flecha(d, x0, y0, x1, y1, color, width=3, head=16):
    d.line([x0, y0, x1, y1], fill=color, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    for a in (ang + 2.5, ang - 2.5):
        d.line([x1, y1, x1 + head * math.cos(a), y1 + head * math.sin(a)],
               fill=color, width=width)


def red_sociedades(centro, sub_centro, nodos, titulo, subtitulo="",
                   destacados=(), leyenda=None, nota=None, kicker="SOCIEDADES"):
    """Red ego-céntrica: 'centro' al medio, 'nodos' alrededor. Cada nodo puede
    tener in=True (asistió al centro) y/o out=True (el centro lo asistió).
    La flecha siempre apunta al goleador (como red_asistencias)."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=kicker)
    M.texto(d, (MARGEN, 190), titulo.upper(), F_BLACK, 52, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 258), subtitulo, F_REG, 26, fill=GRIS)
    M.linea_dorada(d, MARGEN, 312, largo=120, grosor=6)

    cx, cy, R, rc, rn = W / 2, 594, 218, 84, 60
    dest = set(destacados)
    n = max(len(nodos), 1)
    pos = []
    for i in range(n):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        pos.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
    # tamaño ÚNICO para todos los nombres: el que entra en el apellido más largo
    uni = min(M.fit_font(d, nd["nombre"], F_BOLD, rn * 2 - 18, 30, 16).size
              for nd in nodos)
    uni_font = M.fuente(F_BOLD, uni)

    # aristas (detrás de los nodos)
    for (x, y), nd in zip(pos, nodos):
        ang = math.atan2(y - cy, x - cx)
        cbx, cby = cx + rc * math.cos(ang), cy + rc * math.sin(ang)   # borde del centro
        nbx, nby = x - rn * math.cos(ang), y - rn * math.sin(ang)     # borde del nodo
        if nd.get("in"):
            _flecha(d, nbx, nby, cbx, cby, GRIS)      # nodo -> centro (lo asistió)
        if nd.get("out"):
            _flecha(d, cbx, cby, nbx, nby, GRIS)      # centro -> nodo (lo habilitó)

    # nodos alrededor (todos con el mismo tamaño de nombre)
    for (x, y), nd in zip(pos, nodos):
        top = nd["nombre"] in dest
        d.ellipse([x - rn, y - rn, x + rn, y + rn], fill=CARBON,
                  outline=DORADO if top else GRIS_OSC, width=4)
        d.text((x, y), nd["nombre"], font=uni_font, fill=DORADO if top else TINTA, anchor="mm")

    # nodo central (nombre un poco más chico)
    d.ellipse([cx - rc, cy - rc, cx + rc, cy + rc], fill=DORADO, outline=BLANCO, width=3)
    d.text((cx, cy - 10), centro.upper(), font=M.fuente(F_BLACK, 34), fill=NEGRO, anchor="mm")
    if sub_centro:
        d.text((cx, cy + 26), sub_centro, font=M.fuente(F_SEMI, 23), fill=NEGRO, anchor="mm")

    if leyenda:
        M.texto(d, (MARGEN, H - MARGEN - 104), leyenda, F_SEMI, 22, fill=DORADO, anchor="lm")
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 8b. TRAYECTORIA  (línea de tiempo con escudos, años y flechas)
# --------------------------------------------------------------------------
def _logo_chip(img, d, path, x, y, size, ring=None):
    pad = 8
    # el fondo del chip toma el color CHIP del tema actual: sobre negro es un
    # cuadro claro (contraste); en un tema claro se iguala al fondo y no se ve.
    d.rounded_rectangle([x - pad, y - pad, x + size + pad, y + size + pad],
                        radius=14, fill=CHIP,
                        outline=ring, width=5 if ring else 0)
    try:
        lg = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
        img.paste(lg, (int(x), int(y)), lg)
    except Exception:
        pass


def trayectoria(titulo, subtitulo, entradas, nota=None, kicker="TRAYECTORIA",
                foto_zona=False, foto=None, foto_focal=(0.5, 0.40), foto_zoom=1.28):
    """Línea de tiempo vertical: escudo + club + años, unidos por flechas.
    entradas = [{club, anios, logo(ruta), es_chaco}], en orden cronológico.
    foto_zona=True reserva un recuadro a la derecha (foto real si se pasa 'foto')."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=kicker)
    M.texto(d, (MARGEN, 190), titulo.upper(), F_BLACK, 52, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 258), subtitulo, F_REG, 26, fill=GRIS)
    M.linea_dorada(d, MARGEN, 312, largo=120, grosor=6)

    entradas = entradas[:8]
    n = max(len(entradas), 1)
    top, bot = 372, H - MARGEN - 60
    h = (bot - top) / n
    size = int(min(66, h * 0.60))
    lx = MARGEN + 12
    cxl = lx + size / 2
    tx = lx + size + 42

    # zona de la foto (mismo recuadro FOTO_BOX) + límite de ancho para los nombres
    if foto_zona:
        zona = FOTO_BOX
        if not (foto and _foto_en_zona(img, d, foto, zona, focal=foto_focal, zoom=foto_zoom)):
            _dashed_rect(d, zona, DORADO_OSC, dash=26, gap=16, width=3)
            cxz, cyz = (zona[0] + zona[2]) // 2, (zona[1] + zona[3]) // 2
            M.texto(d, (cxz, cyz - 18), "ESPACIO PARA", F_SEMI, 28, fill=GRIS, anchor="mm", tracking=3)
            M.texto(d, (cxz, cyz + 28), "LA FOTO", F_SEMI, 28, fill=GRIS, anchor="mm", tracking=3)
        nombre_der = zona[0] - 24
    else:
        nombre_der = W - MARGEN - 130

    for i, e in enumerate(entradas):
        cy = top + h * i + h / 2
        es = e.get("es_chaco")
        if i < n - 1:                                  # conector + flecha al siguiente
            y0 = cy + size / 2 + 10
            y1 = top + h * (i + 1) + h / 2 - size / 2 - 16
            if y1 > y0:
                d.line([cxl, y0, cxl, y1], fill=GRIS_OSC, width=3)
                d.polygon([(cxl - 8, y1 - 11), (cxl + 8, y1 - 11), (cxl, y1)], fill=DORADO)
        _logo_chip(img, d, e.get("logo"), lx, cy - size / 2, size,
                   ring=DORADO if es else None)
        fc = M.fit_font(d, e["club"], F_BOLD, nombre_der - tx, 36, 22)
        d.text((tx, cy - 15), e["club"], font=fc, fill=DORADO if es else TINTA, anchor="lm")
        M.texto(d, (tx, cy + 22), e.get("anios", ""), F_SEMI, 25, fill=GRIS, anchor="lm")
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 6b. GRAFICO CON LA MARCA  (grafico ya tematizado en negro/dorado, sin tarjeta)
# --------------------------------------------------------------------------
def grafico_marca(ruta_png, titulo, subtitulo="", nota="Fuente: SofaScore"):
    """Coloca un grafico YA generado en la paleta de la marca (fondo negro)
    directo sobre la placa, sin tarjeta blanca: se funde con el fondo.
    Los graficos los produce scripts/graficos_marca.py."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=None)
    M.texto(d, (MARGEN, 180), titulo.upper(), F_BLACK, 48, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 244), subtitulo, F_REG, 26, fill=GRIS)
    M.linea_dorada(d, MARGEN, 300, largo=120, grosor=6)

    zona = (MARGEN - 20, 350, W - MARGEN + 20, H - MARGEN - 60)
    graf = Image.open(ruta_png).convert("RGB")
    cw, ch = zona[2] - zona[0], zona[3] - zona[1]
    graf.thumbnail((cw, ch), Image.LANCZOS)
    gx = zona[0] + (cw - graf.width) // 2
    gy = zona[1] + (ch - graf.height) // 2
    img.paste(graf, (gx, gy))
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 7. PORTADA DE JUGADOR  (con zona reservada para la foto, a editar luego)
# --------------------------------------------------------------------------
def _foto_en_zona(img, d, ruta, box, radius=18, border=DORADO,
                  focal=(0.5, 0.20), zoom=1.22, offset=(0, 0)):
    """Coloca una foto rellenando el box (cover) con esquinas redondeadas y borde
    dorado. 'focal' = punto (x,y en 0..1) donde centrar el recorte y 'zoom' >1
    acerca: por defecto centra horizontal y sesga hacia arriba (cara/torso), lo
    que deja fuera marcas de agua o carteles que suelen estar abajo.
    'offset' = (dx, dy) en PÍXELES para correr la imagen: dx>0 la mueve a la
    derecha, dy>0 la mueve hacia abajo (útil para nudges finos). True si cargó."""
    x0, y0, x1, y1 = (int(v) for v in box)
    bw, bh = x1 - x0, y1 - y0
    try:
        im = Image.open(ruta).convert("RGB")
    except Exception:
        return False
    scale = max(bw / im.width, bh / im.height) * max(zoom, 1.0)
    im = im.resize((max(bw, round(im.width * scale)), max(bh, round(im.height * scale))),
                   Image.LANCZOS)
    fx, fy = focal
    dx, dy = offset            # mover la imagen: dx→derecha, dy→abajo
    left = min(max(0, round((im.width - bw) * fx) - dx), im.width - bw)
    top = min(max(0, round((im.height - bh) * fy) - dy), im.height - bh)
    im = im.crop((left, top, left + bw, top + bh))
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=radius, fill=255)
    img.paste(im, (x0, y0), mask)
    if border:
        d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=radius, outline=border, width=3)
    return True


def _dashed_rect(d, box, color, dash=26, gap=16, width=3):
    x0, y0, x1, y1 = box
    def line(a, b, horizontal):
        pos = a
        while pos < b:
            end = min(pos + dash, b)
            if horizontal:
                d.line([pos, y0, end, y0], fill=color, width=width)
                d.line([pos, y1, end, y1], fill=color, width=width)
            else:
                d.line([x0, pos, x0, end], fill=color, width=width)
                d.line([x1, pos, x1, end], fill=color, width=width)
            pos += dash + gap
    line(x0, x1, True)
    line(y0, y1, False)


def portada_jugador(nombre, etiqueta, subtitulo, teaser="", nota=None, foto_zona=True,
                    foto=None, foto_focal=(0.5, 0.40), foto_zoom=1.28, foto_offset=(0, 0)):
    """Portada de un jugador. Texto a la izquierda y a la derecha la foto (si se
    pasa 'foto') o una zona reservada con marco punteado para editarla luego.
    El recuadro usa FOTO_BOX (mismo tamaño en todas las placas).
    'foto_offset' = (dx, dy) en píxeles: dx>0 corre la foto a la derecha,
    dy>0 la corre hacia abajo."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d)
    M.rayas(d, (0, 0, 16, H), n=3)

    if foto_zona:
        zona = FOTO_BOX
        if not (foto and _foto_en_zona(img, d, foto, zona, focal=foto_focal,
                                       zoom=foto_zoom, offset=foto_offset)):
            _dashed_rect(d, zona, DORADO_OSC, dash=26, gap=16, width=3)
            cx, cy = (zona[0] + zona[2]) // 2, (zona[1] + zona[3]) // 2
            M.texto(d, (cx, cy - 18), "ESPACIO PARA", F_SEMI, 30, fill=GRIS,
                    anchor="mm", tracking=3)
            M.texto(d, (cx, cy + 30), "LA FOTO", F_SEMI, 30, fill=GRIS,
                    anchor="mm", tracking=3)

    tx, col_w = MARGEN, 470
    M.texto(d, (tx, 300), etiqueta.upper(), F_SEMI, 26, fill=DORADO, tracking=6)
    M.linea_dorada(d, tx, 344, largo=90, grosor=8)
    f = M.fit_font(d, max(nombre.upper().split(), key=len), F_BLACK, col_w, 100, 54)
    y = M.parrafo(d, (tx, 404), nombre.upper(), F_BLACK, f.size,
                  fill=TINTA, interlinea=1.02, max_ancho=col_w + 20)
    M.parrafo(d, (tx, y + 28), subtitulo, F_REG, 30, fill=GRIS,
              interlinea=1.3, max_ancho=col_w)
    if teaser:
        # la última palabra ("carrera") va en el renglón de abajo
        pal = teaser.upper().split()
        l1, l2 = " ".join(pal[:-1]), (pal[-1] if pal else "")
        M.texto(d, (tx, H - MARGEN - 158), l1, F_BLACK, 32, fill=DORADO, tracking=1)
        M.texto(d, (tx, H - MARGEN - 116), l2, F_BLACK, 32, fill=DORADO, tracking=1)
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 8. CHIPS  (grupos de nombres en pastillas — ideal para sociedades)
# --------------------------------------------------------------------------
def _pills(d, x0, y, names, destacados, max_x):
    h, pad, gap, row_gap = 62, 26, 16, 18
    px, py = x0, y
    font = M.fuente(F_SEMI, 30)
    for nm in names:
        w = M._ancho(d, nm, font) + pad * 2
        if px + w > max_x:
            px = x0
            py += h + row_gap
        top = nm in destacados
        d.rounded_rectangle([px, py, px + w, py + h], radius=h // 2,
                            fill=DORADO if top else CARBON,
                            outline=None if top else GRIS_OSC, width=2)
        M.texto(d, (px + w / 2, py + h / 2), nm, F_SEMI, 30,
                fill=NEGRO if top else TINTA, anchor="mm")
        px += w + gap
    return py + h


def chips(titulo, subtitulo, grupos, destacados=(), leyenda=None, nota=None,
          kicker="SOCIEDADES"):
    """grupos = [(titulo_grupo, [nombres]), ...]. destacados van en dorado."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=kicker)
    M.texto(d, (MARGEN, 190), titulo.upper(), F_BLACK, 52, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 260), subtitulo, F_REG, 26, fill=GRIS)
    M.linea_dorada(d, MARGEN, 314, largo=120, grosor=6)

    dest = set(destacados)
    y = 382
    for gl, names in grupos:
        M.texto(d, (MARGEN, y), gl.upper(), F_SEMI, 26, fill=GRIS, tracking=4)
        y += 46
        y = _pills(d, MARGEN, y, names, dest, W - MARGEN)
        y += 44
    if leyenda:
        M.texto(d, (MARGEN, H - MARGEN - 104), leyenda, F_SEMI, 24,
                fill=DORADO, anchor="lm")
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# DEMO: genera un juego de ejemplos con datos reales de la temporada 2026
# --------------------------------------------------------------------------
def _demo():
    EJEMPLOS.mkdir(parents=True, exist_ok=True)
    hechas = []

    hechas.append(M.guardar(portada(
        "Chaco For Ever\nFecha 18",
        "El resumen de la temporada en numeros. Desliza para ver como llega el Negro.",
        etiqueta="Resumen temporada 2026",
        nota="Datos: SofaScore"), EJEMPLOS / "01_portada.png"))

    hechas.append(M.guardar(dato(
        "6.4", "goles concedidos por encima del xG",
        "El Negro recibio muchos mas goles de los que las chances rivales anticipaban. El foco esta atras.",
        kicker="EL DATO", nota="Temporada 2026 - SofaScore"),
        EJEMPLOS / "02_dato.png"))

    hechas.append(M.guardar(ranking(
        "Goleadores 2026",
        [("G. Pacheco", 6), ("M. Silvera", 4), ("B. Nievas", 3),
         ("A. Luque", 2), ("G. Melgarejo", 2)],
        subtitulo="Goles en la Primera Nacional", unidad="",
        nota="SofaScore", destacar=0), EJEMPLOS / "03_ranking.png"))

    hechas.append(M.guardar(resultado(
        "Acassuso", 0, "Chaco For Ever", 2,
        torneo="Primera Nacional - Fecha 1",
        detalle="Doblete de Romero. El Negro se lo llevo de visitante.",
        nota="SofaScore"), EJEMPLOS / "04_resultado.png"))

    hechas.append(M.guardar(cita(
        "Cuando patea al arco, patea de lejos: 130 toques en el area de Pacheco y aun asi el gol llega desde afuera.",
        autor="Lectura tactica", nota=None), EJEMPLOS / "05_cita.png"))

    # enmarcar un grafico real si existe (RAIZ = .../instagram ; el proyecto esta 2 niveles arriba)
    proyecto = RAIZ.parents[1]
    candidatos = [
        proyecto / "outputs/temporadas/2026/graficos/puntos_acumulados.png",
        proyecto / "outputs/temporadas/2026/graficos/xg_temporada.png",
    ]
    for c in candidatos:
        if c.exists():
            hechas.append(M.guardar(enmarcar(
                str(c), "Puntos acumulados", "Como se movio el Negro fecha a fecha",
                nota="Fuente: SofaScore"), EJEMPLOS / "06_grafico_enmarcado.png"))
            break

    return hechas


if __name__ == "__main__":
    for r in _demo():
        print("OK", r)
