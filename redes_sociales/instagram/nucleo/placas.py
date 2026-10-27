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
                   F_REG, F_COND, W_HISTORIA, H_HISTORIA)

RAIZ = Path(__file__).resolve().parents[1]
EJEMPLOS = RAIZ / "placas" / "ejemplos"

# Colores semanticos fijos (no forman parte de la paleta por tema: un resultado
# es siempre victoria/empate/derrota, no importa si la placa sale en tema
# oscuro, hueso o dorado). Tonos apagados para no chocar con el dorado de marca.
VERDE = (58, 138, 92)      # victoria
ROJO_L = (176, 68, 60)     # derrota

# recuadro de la foto: MISMO tamaño en todas las placas (portada y trayectoria)
FOTO_BOX = (578, 360, W - 66, H - MARGEN - 60)      # 436 x 576


# --------------------------------------------------------------------------
# 1. PORTADA  (tapa de carrusel)
# --------------------------------------------------------------------------
def portada(titulo, subtitulo, etiqueta="ANALISIS", nota=None, centrado=False):
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=None)
    # rayas laterales completas como sello del club
    M.rayas(d, (0, 0, 22, H), n=3)
    M.rayas(d, (W - 22, 0, W, H), n=3)

    palabra_larga = max(titulo.upper().split(), key=len)
    f = M.fit_font(d, palabra_larga, F_BLACK, W - 2 * MARGEN, 128, 66)

    if centrado:
        M.texto(d, (W / 2, 300), etiqueta.upper(), F_SEMI, 26, fill=DORADO,
                tracking=8, anchor="mm")
        M.linea_dorada(d, W / 2 - 45, 326, largo=90, grosor=6)
        y_fin = M.parrafo(d, (W / 2, 388), titulo.upper(), F_BLACK,
                          f.size, fill=TINTA, interlinea=1.02, anchor_x="m")
        M.parrafo(d, (W / 2, y_fin + 44), subtitulo, F_REG, 34, fill=GRIS,
                  interlinea=1.3, anchor_x="m")
    else:
        d.rectangle([MARGEN, 360, MARGEN + 90, 360 + 10], fill=DORADO)
        M.texto(d, (MARGEN, 300), etiqueta.upper(), F_SEMI, 26, fill=DORADO, tracking=8)
        # titulo grande, auto-ajustado por la palabra mas larga
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
    S = 195
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

    # Ojo: los nombres se centran a 150px de cada lado del eje, así que el ancho
    # máximo tiene que ser 280 (140 por lado) o los dos nombres se tocan en el medio.
    # Mismo tamaño para los dos (el más chico de los dos, según cuál nombre sea
    # más largo) para que no queden en fuentes/tamaños distintos entre sí.
    fl = M.fit_font(d, local.upper(), F_BOLD, 280, 40, 20)
    fv = M.fit_font(d, visitante.upper(), F_BOLD, 280, 40, 20)
    f_nombres = fl if fl.size <= fv.size else fv
    d.text((W / 2 - 150, 662), local.upper(), font=f_nombres,
           fill=TINTA if gan_l else GRIS, anchor="mm")
    d.text((W / 2 + 150, 662), visitante.upper(), font=f_nombres,
           fill=TINTA if gan_v else GRIS, anchor="mm")

    if detalle:
        M.parrafo(d, (W / 2, 752), detalle, F_REG, 28, fill=GRIS,
                  interlinea=1.3, anchor_x="m", max_ancho=W - 2 * MARGEN - 40)
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 4b. FICHA  (grilla de estadisticas generales)
# --------------------------------------------------------------------------
def ficha(titulo, subtitulo, filas, nota=None, destacar=None, centrado=False):
    """Grilla de datos generales. filas = [(etiqueta, valor), ...].
    'destacar' = etiqueta cuyo valor va en dorado (ej. la posicion).
    'centrado' = título/subtítulo centrados y cada fila como una sola línea
    'etiqueta   valor' centrada, en vez del layout etiqueta-izq/valor-der."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker="LA FICHA")
    if centrado:
        M.texto(d, (W / 2, 190), titulo.upper(), F_BLACK, 56, fill=TINTA, anchor="mm")
        if subtitulo:
            M.texto(d, (W / 2, 262), subtitulo, F_REG, 27, fill=GRIS, anchor="mm")
        M.linea_dorada(d, W / 2 - 60, 320, largo=120, grosor=6)
    else:
        M.texto(d, (MARGEN, 190), titulo.upper(), F_BLACK, 56, fill=TINTA)
        if subtitulo:
            M.texto(d, (MARGEN, 262), subtitulo, F_REG, 27, fill=GRIS)
        M.linea_dorada(d, MARGEN, 320, largo=120, grosor=6)

    filas = filas[:8]
    y = 380
    alto = (H - MARGEN - 90 - y) / len(filas)
    # Tamaño de fuente UNIFORME para los valores: el más chico que necesite el
    # valor más largo. Así todos los datos de la ficha quedan del mismo tamaño en
    # vez de que los cortos ("3", "0") salgan gigantes y los largos, chicos.
    fsize = min(M.fit_font(d, str(v), F_BLACK, 430, 44, 26).size for _, v in filas)
    fv = M.fuente(F_BLACK, fsize)
    f_lbl = M.fuente(F_SEMI, 30)
    for etiqueta, valor in filas:
        top = (destacar is not None and etiqueta == destacar)
        cy = y + alto / 2
        if centrado:
            lbl = etiqueta + "   "
            val_txt = str(valor)
            w_lbl = d.textlength(lbl, font=f_lbl)
            w_val = d.textlength(val_txt, font=fv)
            x0 = W / 2 - (w_lbl + w_val) / 2
            d.text((x0, cy), lbl, font=f_lbl, fill=GRIS, anchor="lm")
            d.text((x0 + w_lbl, cy), val_txt, font=fv,
                   fill=DORADO if top else TINTA, anchor="lm")
        else:
            M.texto(d, (MARGEN, cy), etiqueta, F_SEMI, 30, fill=GRIS, anchor="lm")
            d.text((W - MARGEN, cy), str(valor), font=fv,
                   fill=DORADO if top else TINTA, anchor="rm")
        d.line([MARGEN, y + alto, W - MARGEN, y + alto], fill=GRIS_OSC, width=2)
        y += alto
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 4c. DATO + COMPARACION  (numero mediano arriba, dos tarjetas enfrentadas)
# --------------------------------------------------------------------------
def _serie_wdl(d, cx, cy, serie, size=78):
    """Dibuja una racha tipo 'WDWWW' (código fuente en inglés: W/D/L) centrada
    en (cx, cy), traducida a la sigla en español (V/E/D) y coloreada letra por
    letra: verde victoria, gris empate, rojo derrota. Se usa dentro de dato_vs
    cuando el 'valor_grande' de una tarjeta es una racha (solo letras W/D/L)."""
    font = M.fuente(F_BLACK, size)
    colores = {"W": VERDE, "D": GRIS, "L": ROJO_L}
    letras = {"W": "V", "D": "E", "L": "D"}
    anchos = [d.textlength(letras.get(ch, ch), font=font) for ch in serie]
    x = cx - sum(anchos) / 2
    for ch, w in zip(serie, anchos):
        d.text((x, cy), letras.get(ch, ch), font=font, fill=colores.get(ch, TINTA), anchor="lm")
        x += w


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
        valor = str(grande)
        if len(valor) >= 2 and set(valor.upper()) <= {"W", "D", "L"}:
            _serie_wdl(d, cx, y0 + 158, valor.upper())
        else:
            d.text((cx, y0 + 158), valor, font=M.fuente(F_BLACK, 78),
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
def cita(frase, autor="", nota=None, centrado=False):
    """Frase grande con comillas doradas. El texto arranca pegado a las comillas y el
    tamaño de letra baja solo (52 -> 38) si la frase es larga, para que entre entera sin
    pisar el autor ni el pie."""
    y_marca = 262 if centrado else 270        # comillas
    y_texto = 332 if centrado else 318        # primera línea de la frase
    limite = H - MARGEN - 150                 # hasta acá puede llegar la línea del autor
    for size in (52, 48, 44, 40, 38):
        img, d = M.lienzo(NEGRO)
        M.cabecera(d, kicker=None)
        if centrado:
            d.text((W / 2, y_marca), "“", font=M.fuente(F_BLACK, 200), fill=DORADO, anchor="mm")
            y = M.parrafo(d, (W / 2, y_texto), frase, F_BLACK, size, fill=TINTA,
                          interlinea=1.16, anchor_x="m")
        else:
            d.text((MARGEN - 6, y_marca), "“", font=M.fuente(F_BLACK, 200),
                   fill=DORADO, anchor="lm")
            y = M.parrafo(d, (MARGEN, y_texto), frase, F_BLACK, size, fill=TINTA,
                          interlinea=1.16)
        if y + (92 if autor else 0) <= limite:
            break
    if autor:
        if centrado:
            M.linea_dorada(d, W / 2 - 45, y + 40, largo=90, grosor=6)
            M.texto(d, (W / 2, y + 66), autor.upper(), F_SEMI, 26, fill=DORADO,
                    tracking=4, anchor="mm")
        else:
            M.linea_dorada(d, MARGEN, y + 40, largo=90, grosor=6)
            M.texto(d, (MARGEN, y + 66), autor.upper(), F_SEMI, 26, fill=DORADO, tracking=4)
    M.pie(d, nota=nota)
    return img


# --------------------------------------------------------------------------
# 5b. JUGADOR POR JUGADOR  (fuerte/flojo en lenguaje simple, sin percentiles)
# --------------------------------------------------------------------------
def jugadores_clave(titulo, jugadores, subtitulo="", nota=None, kicker="ASI LLEGA EL RIVAL"):
    """Fortalezas y debilidades de hasta 3 jugadores, en una frase cada una,
    sin percentiles ni jerga (para que lo entienda cualquier hincha).
    'jugadores' = [(nombre, puesto, fuerte, flojo), ...]."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d, kicker=kicker)
    M.texto(d, (MARGEN, 188), titulo.upper(), F_BLACK, 44, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 244), subtitulo, F_REG, 25, fill=GRIS)
    M.linea_dorada(d, MARGEN, 292, largo=100, grosor=6)

    jugadores = jugadores[:3]
    y0 = 330
    alto = (H - MARGEN - 90 - y0) / len(jugadores)
    ancho_txt = W - 2 * MARGEN - 30

    for i, (nombre, puesto, fuerte, flojo) in enumerate(jugadores):
        y = y0 + i * alto
        M.texto(d, (MARGEN, y), nombre.upper(), F_BLACK, 32, fill=TINTA)
        w_nom = M._ancho(d, nombre.upper(), M.fuente(F_BLACK, 32))
        M.texto(d, (MARGEN + w_nom + 14, y + 6), puesto, F_SEMI, 20, fill=GRIS)

        yy = y + 46
        M.texto(d, (MARGEN, yy), "LO QUE HACE BIEN", F_SEMI, 18, fill=VERDE, tracking=2)
        yy = M.parrafo(d, (MARGEN, yy + 26), fuerte, F_REG, 25, fill=VERDE,
                       interlinea=1.2, max_ancho=ancho_txt)

        yy += 12
        M.texto(d, (MARGEN, yy), "LO QUE LE CUESTA", F_SEMI, 18, fill=ROJO_L, tracking=2)
        yy = M.parrafo(d, (MARGEN, yy + 26), flojo, F_REG, 25, fill=ROJO_L,
                       interlinea=1.2, max_ancho=ancho_txt)

        if i < len(jugadores) - 1:
            d.line([MARGEN, y0 + (i + 1) * alto - 14, W - MARGEN, y0 + (i + 1) * alto - 14],
                  fill=GRIS_OSC, width=2)
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
# 6b. FORMATO HISTORIA (9:16, 1080x1920) — mismos bloques, lienzo mas alto.
# Pensadas para republicar un grafico del informe de partido como historia,
# con mas aire vertical para que entre un plantel completo o el detalle de
# una comparativa sin apretar.
# --------------------------------------------------------------------------
RIVAL_HIST = ROJO_L   # mismo tono que "LADRILLO" del rival en
                      # graficos_partido_marca.py: Chaco siempre dorado, rival
                      # siempre este rojo apagado, en toda la parte oscura.


def ranking_historia(titulo, filas, subtitulo="", unidad="", nota=None,
                     destacar=0, piso=0, max_filas=20):
    """Como ranking(), pero en formato historia y sin el tope de 6 filas: para
    un plantel completo (ej. los ~16 que jugaron) en vez de un top chico.
    filas = [(nombre, valor), ...] ya ordenadas de mayor a menor."""
    img, d = M.lienzo(NEGRO, tam=(W_HISTORIA, H_HISTORIA))
    M.cabecera(d, kicker="RANKING")
    M.texto(d, (MARGEN, 200), titulo.upper(), F_BLACK, 56, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 270), subtitulo, F_REG, 28, fill=GRIS)

    filas = filas[:max_filas]
    n = max(len(filas), 1)
    vmax = max((v for _, v in filas), default=1) or 1
    y0, y1 = 350, H_HISTORIA - MARGEN - 110
    alto = (y1 - y0) / n
    nombre_x = MARGEN + 64
    bar_x = 520
    bar_w = W_HISTORIA - MARGEN - bar_x - 130
    barh = min(15, alto * 0.30)
    f_num = int(min(34, alto * 0.42))
    f_nom_ini = int(min(30, alto * 0.38))
    f_val = int(min(30, alto * 0.38))

    y = y0
    for i, (nombre, valor) in enumerate(filas):
        top = (i == destacar)
        cbar = DORADO if top else GRIS_OSC
        ctxt = TINTA if top else GRIS
        cy = y + alto / 2
        M.texto(d, (MARGEN, cy), str(i + 1), F_BLACK, f_num,
                fill=DORADO if top else GRIS_OSC, anchor="lm")
        fn = M.fit_font(d, nombre, F_BOLD, bar_x - nombre_x - 24, f_nom_ini, 16)
        d.text((nombre_x, cy), nombre, font=fn, fill=ctxt, anchor="lm")
        denom = (vmax - piso) or 1
        w = int(bar_w * max(0.08, (valor - piso) / denom))
        d.rounded_rectangle([bar_x, cy - barh, bar_x + max(w, 6), cy + barh],
                            radius=barh * 0.7, fill=cbar)
        vtxt = f"{valor}{unidad}"
        M.texto(d, (W_HISTORIA - MARGEN, cy), vtxt, F_BLACK, f_val,
                fill=ctxt, anchor="rm")
        y += alto
    M.pie(d, nota=nota, alto=H_HISTORIA)
    return img


def comparacion_historia(titulo, subtitulo, filas, home_label, away_label,
                         nota=None):
    """Comparativa de estadisticas de partido en formato historia: una fila
    por metrica, valores a los costados + barra dividida proporcional debajo
    (mismo layout que plot_match_stats pero dibujado en la paleta de marca).

    filas = [(etiqueta, valor_home_fmt, valor_away_fmt, frac_home), ...] con
    frac_home = proporcion 0..1 del segmento home_label en la barra."""
    img, d = M.lienzo(NEGRO, tam=(W_HISTORIA, H_HISTORIA))
    M.cabecera(d, kicker="COMPARATIVA")
    M.texto(d, (MARGEN, 200), titulo.upper(), F_BLACK, 52, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 268), subtitulo, F_REG, 27, fill=GRIS)

    y_eq = 336
    M.texto(d, (MARGEN, y_eq), home_label.upper(), F_SEMI, 24, fill=DORADO, tracking=2)
    M.texto(d, (W_HISTORIA - MARGEN, y_eq), away_label.upper(), F_SEMI, 24,
            fill=RIVAL_HIST, anchor="ra", tracking=2)

    n = max(len(filas), 1)
    y0, y1 = y_eq + 54, H_HISTORIA - MARGEN - 110
    alto = (y1 - y0) / n
    barh = min(14, alto * 0.20)
    f_etq = int(min(26, alto * 0.30))
    f_val = int(min(28, alto * 0.34))

    y = y0
    for etiqueta, vh_txt, va_txt, frac in filas:
        cy_txt = y + alto * 0.36
        cy_bar = y + alto * 0.68
        M.texto(d, (W_HISTORIA / 2, cy_txt), etiqueta, F_SEMI, f_etq,
                fill=TINTA, anchor="mm")
        M.texto(d, (MARGEN, cy_txt), vh_txt, F_BLACK, f_val, fill=DORADO, anchor="lm")
        M.texto(d, (W_HISTORIA - MARGEN, cy_txt), va_txt, F_BLACK, f_val,
                fill=RIVAL_HIST, anchor="rm")
        x0, x1 = MARGEN, W_HISTORIA - MARGEN
        frac = max(0.0, min(1.0, frac))
        d.rounded_rectangle([x0, cy_bar - barh, x1, cy_bar + barh],
                            radius=barh * 0.8, fill=GRIS_OSC)
        xm = x0 + (x1 - x0) * frac
        if frac > 0:
            d.rounded_rectangle([x0, cy_bar - barh, max(xm, x0 + 6), cy_bar + barh],
                                radius=barh * 0.8, fill=DORADO)
        if frac < 1:
            d.rounded_rectangle([min(xm, x1 - 6), cy_bar - barh, x1, cy_bar + barh],
                                radius=barh * 0.8, fill=RIVAL_HIST)
        y += alto
    M.pie(d, nota=nota, alto=H_HISTORIA)
    return img


def grafico_marca_historia(ruta_png, titulo, subtitulo="", nota="Fuente: SofaScore"):
    """Version historia de grafico_marca(): encabezado + un grafico YA generado
    en la paleta oscura (ver graficos_partido_marca.py) + pie, con mas aire
    vertical para canchas que en el feed cuadrado quedarian chicas."""
    img, d = M.lienzo(NEGRO, tam=(W_HISTORIA, H_HISTORIA))
    M.cabecera(d, kicker=None)
    M.texto(d, (MARGEN, 200), titulo.upper(), F_BLACK, 52, fill=TINTA)
    if subtitulo:
        M.texto(d, (MARGEN, 268), subtitulo, F_REG, 27, fill=GRIS)
    M.linea_dorada(d, MARGEN, 328, largo=120, grosor=6)

    zona = (MARGEN - 20, 378, W_HISTORIA - MARGEN + 20, H_HISTORIA - MARGEN - 110)
    graf = Image.open(ruta_png).convert("RGB")
    cw, ch = zona[2] - zona[0], zona[3] - zona[1]
    graf.thumbnail((cw, ch), Image.LANCZOS)
    # Alineado arriba (no centrado): los graficos de cancha suelen salir mas
    # anchos que altos, y centrar verticalmente partia el espacio sobrante en
    # dos franjas raras (una debajo del subtitulo, otra encima del pie). Mejor
    # pegado al subtitulo y el sobrante como aire libre abajo, mas prolijo.
    gx = zona[0] + (cw - graf.width) // 2
    gy = zona[1]
    img.paste(graf, (gx, gy))
    M.pie(d, nota=nota, alto=H_HISTORIA)
    return img


def salvados_historia(titulo, subtitulo, equipos, pie_texto="", nota=None):
    """Historia (9:16) de equipos matematicamente salvados: una tarjeta por
    equipo con escudo en chip, nombre, puntos/posicion y una tilde dorada.
    equipos = [(nombre, ruta_escudo, "53 puntos  ·  3° en la tabla"), ...]
    pie_texto = linea chica debajo de las tarjetas (ej. otros equipos a salvo)."""
    img, d = M.lienzo(NEGRO, tam=(W_HISTORIA, H_HISTORIA))
    M.cabecera(d, kicker="LA TABLA")
    y = 215
    for linea, color in titulo:
        M.texto(d, (MARGEN, y), linea, F_BLACK, 72, fill=color)
        y += 88
    M.texto(d, (MARGEN, y + 10), subtitulo, F_REG, 30, fill=GRIS)
    M.linea_dorada(d, MARGEN, y + 68, largo=120, grosor=6)

    n = max(len(equipos), 1)
    y0 = y + 130
    y1 = H_HISTORIA - MARGEN - (170 if pie_texto else 110)
    gap = 28
    alto = int((y1 - y0 - gap * (n - 1)) / n)
    alto = min(alto, 330)
    x0, x1 = MARGEN, W_HISTORIA - MARGEN
    cy0 = y0
    for nombre, escudo, detalle in equipos:
        d.rounded_rectangle([x0, cy0, x1, cy0 + alto], radius=26, fill=CARBON,
                            outline=DORADO, width=3)
        size = min(200, alto - 70)
        _logo_chip(img, d, escudo, x0 + 44, cy0 + (alto - size) // 2, size)
        tx = x0 + 44 + size + 56
        cy = cy0 + alto / 2
        fn = M.fit_font(d, nombre.upper(), F_BLACK, x1 - 150 - tx, 54, 30)
        d.text((tx, cy - 20), nombre.upper(), font=fn, fill=TINTA, anchor="ls")
        M.texto(d, (tx, cy + 14), detalle, F_REG, 30, fill=GRIS, anchor="la")
        # tilde dorada en circulo, a la derecha
        r = 42
        cx = x1 - 30 - r
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DORADO)
        d.line([(cx - 20, cy + 2), (cx - 5, cy + 18), (cx + 22, cy - 16)],
               fill=NEGRO, width=10, joint="curve")
        cy0 += alto + gap
    if pie_texto:
        M.parrafo(d, (W_HISTORIA / 2, y1 + 34), pie_texto, F_SEMI, 28, fill=TINTA,
                  max_ancho=W_HISTORIA - 2 * MARGEN, interlinea=1.3, anchor_x="m")
    M.pie(d, nota=nota, alto=H_HISTORIA)
    return img


def combinacion_historia(titulo, subtitulo, condiciones, resultado_texto="",
                         pie_texto="", nota=None, kicker="LA COMBINACIÓN"):
    """Historia (9:16) con la combinacion de resultados que se tiene que dar.
    Una tarjeta por condicion: escudo en chip, titulo corto, detalle (los
    partidos) y un numero de paso en circulo dorado a la derecha.
    condiciones = [(titulo_card, detalle, ruta_escudo), ...]
    resultado_texto = recuadro dorado con la conclusion (qué pasa si se da todo)
    pie_texto = linea chica de aclaracion al pie."""
    img, d = M.lienzo(NEGRO, tam=(W_HISTORIA, H_HISTORIA))
    M.cabecera(d, kicker=kicker)
    y = 215
    for linea, color in titulo:
        M.texto(d, (MARGEN, y), linea, F_BLACK, 72, fill=color)
        y += 88
    M.texto(d, (MARGEN, y + 10), subtitulo, F_REG, 30, fill=GRIS)
    M.linea_dorada(d, MARGEN, y + 68, largo=120, grosor=6)

    n = max(len(condiciones), 1)
    y0 = y + 124
    reserva = (230 if resultado_texto else 0) + (110 if pie_texto else 0)
    y1 = H_HISTORIA - MARGEN - 110 - reserva
    gap = 24
    alto = min(int((y1 - y0 - gap * (n - 1)) / n), 290)
    x0, x1 = MARGEN, W_HISTORIA - MARGEN
    cy0 = y0
    for i, item in enumerate(condiciones, 1):
        tit, detalle, escudo = item[:3]
        badge = item[3] if len(item) > 3 else str(i)     # texto del circulo (default: nro de paso)
        d.rounded_rectangle([x0, cy0, x1, cy0 + alto], radius=26, fill=CARBON,
                            outline=DORADO_OSC, width=3)
        size = min(170, alto - 60)
        _logo_chip(img, d, escudo, x0 + 40, cy0 + (alto - size) // 2, size)
        tx = x0 + 40 + size + 48
        cy = cy0 + alto / 2
        r = 38
        cxn = x1 - 30 - r
        fn = M.fit_font(d, tit.upper(), F_BLACK, cxn - r - 30 - tx, 46, 26)
        d.text((tx, cy - 14), tit.upper(), font=fn, fill=TINTA, anchor="ls")
        M.parrafo(d, (tx, cy + 12), detalle, F_REG, 28, fill=GRIS,
                  max_ancho=cxn - r - 30 - tx, interlinea=1.25)
        d.ellipse([cxn - r, cy - r, cxn + r, cy + r], fill=DORADO)
        M.texto(d, (cxn, cy + 2), badge, F_BLACK, 44 if len(badge) <= 2 else 30,
                fill=NEGRO, anchor="mm")
        cy0 += alto + gap

    yb = cy0 - gap + 34
    if resultado_texto:
        hb = 190
        d.rounded_rectangle([x0, yb, x1, yb + hb], radius=26, fill=NEGRO,
                            outline=DORADO, width=4)
        M.parrafo(d, (W_HISTORIA / 2, yb + 30), resultado_texto, F_SEMI, 31,
                  fill=TINTA, max_ancho=W_HISTORIA - 2 * MARGEN - 90, interlinea=1.3,
                  anchor_x="m")
        yb += hb + 30
    if pie_texto:
        M.parrafo(d, (W_HISTORIA / 2, yb), pie_texto, F_REG, 24, fill=GRIS,
                  max_ancho=W_HISTORIA - 2 * MARGEN, interlinea=1.3, anchor_x="m")
    M.pie(d, nota=nota, alto=H_HISTORIA)
    return img


def tramos_historia(titulo, subtitulo, tramos, resultado_texto="", pie_texto="",
                    nota=None, kicker="EL PARTIDO", leyenda_xg="xG  Negro – Rival"):
    """Historia (9:16) con el partido partido en tramos de tiempo. Cada tarjeta:
    rango de minutos + nombre a la izquierda, xG de cada equipo a la derecha
    (Chaco dorado, rival rojo) y debajo los hechos del tramo, uno por linea.
    tramos = [{"rango": "69' – 90'", "nombre": "...", "xg": (0.14, 0.86),
               "eventos": ["85'  Gol de ...", ...], "destacar": True}, ...]
    resultado_texto = recuadro dorado con la conclusion; pie_texto = aclaracion."""
    img, d = M.lienzo(NEGRO, tam=(W_HISTORIA, H_HISTORIA))
    M.cabecera(d, kicker=kicker)
    y = 215
    for linea, color in titulo:
        M.texto(d, (MARGEN, y), linea, F_BLACK, 66, fill=color)
        y += 80
    M.texto(d, (MARGEN, y + 6), subtitulo, F_REG, 28, fill=GRIS)
    M.linea_dorada(d, MARGEN, y + 62, largo=120, grosor=6)

    n = max(len(tramos), 1)
    y0 = y + 132
    reserva = (200 if resultado_texto else 0) + (96 if pie_texto else 0)
    y1 = H_HISTORIA - MARGEN - 110 - reserva
    gap = 18
    alto = min(int((y1 - y0 - gap * (n - 1)) / n), 250)
    x0, x1 = MARGEN, W_HISTORIA - MARGEN
    M.texto(d, (x1 - 34, y0 - 14), leyenda_xg, F_REG, 21, fill=GRIS, anchor="rd")
    cy0 = y0
    for t in tramos:
        dest = t.get("destacar")
        d.rounded_rectangle([x0, cy0, x1, cy0 + alto], radius=24, fill=CARBON,
                            outline=DORADO if dest else DORADO_OSC, width=4 if dest else 2)
        px = x0 + 34
        M.texto(d, (px, cy0 + 28), t["rango"], F_BLACK, 40,
                fill=DORADO if dest else TINTA)
        M.texto(d, (px, cy0 + 78), t.get("nombre", "").upper(), F_SEMI, 21,
                fill=GRIS, tracking=2)
        gc, gr = t["xg"]
        # xG de cada equipo, alineado a la derecha: "0.14 – 0.86"
        xr = x1 - 34
        M.texto(d, (xr, cy0 + 24), f"{gr:.2f}", F_BLACK, 44, fill=RIVAL_HIST, anchor="ra")
        wr = d.textlength(f"{gr:.2f}", font=M.fuente(F_BLACK, 44))
        M.texto(d, (xr - wr - 18, cy0 + 24), "–", F_BLACK, 44, fill=GRIS, anchor="ra")
        M.texto(d, (xr - wr - 56, cy0 + 24), f"{gc:.2f}", F_BLACK, 44, fill=DORADO, anchor="ra")
        ey = cy0 + 112
        paso = (alto - 112 - 16) / max(len(t.get("eventos", [])), 1)
        paso = min(paso, 38)
        for ev in t.get("eventos", []):
            fe = M.fit_font(d, ev, F_REG, x1 - px - 34, 27, 18)
            d.text((px, ey), ev, font=fe, fill=TINTA if dest else GRIS, anchor="la")
            ey += paso
        cy0 += alto + gap

    yb = cy0 - gap + 30
    if resultado_texto:
        hb = 170
        d.rounded_rectangle([x0, yb, x1, yb + hb], radius=24, fill=NEGRO,
                            outline=DORADO, width=4)
        M.parrafo(d, (W_HISTORIA / 2, yb + 26), resultado_texto, F_SEMI, 28,
                  fill=TINTA, max_ancho=W_HISTORIA - 2 * MARGEN - 80, interlinea=1.3,
                  anchor_x="m")
        yb += hb + 26
    if pie_texto:
        M.parrafo(d, (W_HISTORIA / 2, yb), pie_texto, F_REG, 23, fill=GRIS,
                  max_ancho=W_HISTORIA - 2 * MARGEN, interlinea=1.3, anchor_x="m")
    M.pie(d, nota=nota, alto=H_HISTORIA)
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


def _escudo_en_zona(img, d, ruta, box, radius=18, border=DORADO, escudo_px=200,
                    leyenda=None):
    """Rellena la zona de la foto con un panel del club cuando NO hay foto del
    jugador: rayas verticales sutiles + el escudo centrado en un chip claro.

    Por qué no se estira el escudo a todo el panel: el PNG del escudo es de
    70x70, así que agrandarlo mucho lo deja borroso. Se lo deja chico y nítido
    sobre un fondo dibujado (las rayas son vectoriales, entran sin perder
    definición a cualquier tamaño). Devuelve True si pudo cargar el escudo."""
    x0, y0, x1, y1 = (int(v) for v in box)
    bw, bh = x1 - x0, y1 - y0

    # panel con rayas del club en tono bajo (no blanco/negro puro: a este tamaño
    # el contraste pleno se come la placa)
    panel = Image.new("RGB", (bw, bh), CARBON)
    pd = ImageDraw.Draw(panel)
    n = 7
    ancho = bw / n
    for i in range(n):
        if i % 2:
            pd.rectangle([i * ancho, 0, (i + 1) * ancho, bh], fill=GRIS_OSC)
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=radius, fill=255)
    img.paste(panel, (x0, y0), mask)

    cx, cy = x0 + bw // 2, y0 + bh // 2
    ok = False
    try:
        lg = Image.open(ruta).convert("RGBA").resize((escudo_px, escudo_px), Image.LANCZOS)
        pad = 22
        d.rounded_rectangle([cx - escudo_px / 2 - pad, cy - escudo_px / 2 - pad - 20,
                             cx + escudo_px / 2 + pad, cy + escudo_px / 2 + pad - 20],
                            radius=18, fill=CHIP)
        img.paste(lg, (int(cx - escudo_px / 2), int(cy - escudo_px / 2 - 20)), lg)
        ok = True
    except Exception:
        pass

    if leyenda:
        # misma tipografía que el nombre del jugador (F_BLACK) para que el panel
        # se lea como parte del bloque y no como un caption suelto
        M.parrafo(d, (cx, cy + escudo_px / 2 + 34), leyenda, F_BLACK, 30,
                  fill=TINTA, interlinea=1.2, anchor_x="m", max_ancho=bw - 60)

    if border:
        d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=radius,
                            outline=border, width=3)
    return ok


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
                    foto=None, foto_focal=(0.5, 0.40), foto_zoom=1.28, foto_offset=(0, 0),
                    escudo=None, escudo_leyenda=None):
    """Portada de un jugador. Texto a la izquierda y a la derecha la foto (si se
    pasa 'foto'). El recuadro usa FOTO_BOX (mismo tamaño en todas las placas).
    'foto_offset' = (dx, dy) en píxeles: dx>0 corre la foto a la derecha,
    dy>0 la corre hacia abajo.

    Si no hay foto del jugador, en orden: si se pasa 'escudo' se dibuja el panel
    del club (rayas + escudo centrado, ver _escudo_en_zona); si no, queda el
    marco punteado de 'espacio para la foto' para editar después."""
    img, d = M.lienzo(NEGRO)
    M.cabecera(d)
    M.rayas(d, (0, 0, 16, H), n=3)

    if foto_zona:
        zona = FOTO_BOX
        puesto = foto and _foto_en_zona(img, d, foto, zona, focal=foto_focal,
                                        zoom=foto_zoom, offset=foto_offset)
        if not puesto and escudo:
            puesto = _escudo_en_zona(img, d, escudo, zona, leyenda=escudo_leyenda)
        if not puesto:
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
