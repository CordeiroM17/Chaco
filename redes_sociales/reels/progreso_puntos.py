# -*- coding: utf-8 -*-
"""
Reel 9:16 — "De ultimo a salvado": los puntos de Chaco For Ever fecha por fecha.

    venv/Scripts/python.exe redes_sociales/reels/progreso_puntos.py [--prueba]

--prueba renderiza solo unos cuadros sueltos a salidas/prueba_*.png (sin video).
Mismo estandar visual de la cuenta (nucleo/marca.py): negro, blanco, UN dorado.
Dato: datos_temporada.serie() (misma reconstruccion que la tabla historica).
Sonido: sintetizado aca (sin musica con derechos); la musica en tendencia se
suma dentro de Instagram al subirlo.
"""
import sys
import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "instagram" / "nucleo"))
import marca as M                     # noqa: E402
import datos_temporada                # noqa: E402  (chdir al proyecto)

OUT = AQUI / "salidas"
OUT.mkdir(exist_ok=True)

FPS = 30
VW, VH = 1080, 1920

NEGRO, TINTA, DORADO, GRIS, GRIS_OSC = M.NEGRO, M.TINTA, M.DORADO, M.GRIS, M.GRIS_OSC
F_BLACK, F_BOLD, F_SEMI, F_REG, F_COND = M.F_BLACK, M.F_BOLD, M.F_SEMI, M.F_REG, M.F_COND

PISO_SALVACION = 35        # puntos del 16 al cierre de las 34 fechas (All Boys)
CORTE_RECESO = 18          # partidos antes del receso (el 18 fue el 20/6)

CORTOS = {
    "Club Ferro Carril Oeste": "Ferro", "Club Atletico Colón": "Colón",
    "Gimnasia Y Esgrima De Jujuy": "Gimnasia de Jujuy", "Gimnasia Jujuy": "Gimnasia de Jujuy",
    "Estudiantes de Buenos Aires": "Estudiantes", "CA Mitre": "Mitre",
    "Central Norte de Salta": "Central Norte", "Deportivo Morón": "Morón",
    "Deportivo Madryn": "Madryn", "Defensores de Belgrano": "Defensores",
    "Ciudad de Bolivar": "Ciudad de Bolívar",
}

# --------------------------------------------------------------------------
# DATOS Y LINEA DE TIEMPO
# --------------------------------------------------------------------------
S = datos_temporada.serie()
N = len(S)
PTS = [0] + list(S.pts)
assert N == 34 and PTS[-1] == 40 and PTS[CORTE_RECESO] == 12, "la serie no es la esperada"

T_HOOK = 2.7
T_WIPE = 0.55
DUR_CARD = 1.9


def dur(n):                       # duracion del partido n (1-based)
    return 0.52 if n <= 8 else 0.34 if n <= CORTE_RECESO else 0.46


T0 = {}                           # inicio de cada partido
t = T_HOOK
for n in range(1, N + 1):
    if n == CORTE_RECESO + 1:
        T_CARD = t                # la tarjeta "que cambio" va entre el 18 y el 19
        t += DUR_CARD
    T0[n] = t
    t += dur(n)
T_FIN = t + 0.25                  # arranca la tarjeta final
T_TOTAL = T_FIN + 4.2
FADE_LOOP = 0.5


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return 3 * x * x - 2 * x ** 3


def pop(x):                       # rebote 1.3 -> 1.0
    x = min(max(x, 0.0), 1.0)
    return 1 + 0.3 * (1 - x) ** 2 * math.cos(x * 6)


def mezcla(c, a):                 # color c sobre fondo negro con opacidad a
    a = min(max(a, 0.0), 1.0)
    return tuple(int(NEGRO[i] + (c[i] - NEGRO[i]) * a) for i in range(3))


# --------------------------------------------------------------------------
# PRIMITIVAS
# --------------------------------------------------------------------------
def texto_escalado(img, centro, s, fpath, size, fill, escala=1.0, tracking=0):
    """Texto centrado en `centro`, con escala (para los 'pops')."""
    tmp = Image.new("L", (1, 1))
    d = ImageDraw.Draw(tmp)
    f = M.fuente(fpath, size)
    w = int(M._ancho(d, s, f, tracking)) + 40
    h = int(size * 1.5)
    capa = Image.new("L", (w, h), 0)
    M.texto(ImageDraw.Draw(capa), (w // 2, h // 2), s, fpath, size, fill=255, anchor="mm", tracking=tracking)
    if abs(escala - 1) > 0.005:
        capa = capa.resize((max(1, int(w * escala)), max(1, int(h * escala))), Image.BICUBIC)
    color = Image.new("RGB", capa.size, fill)
    img.paste(color, (int(centro[0] - capa.size[0] / 2), int(centro[1] - capa.size[1] / 2)), capa)


def rayas_marca(d, x, y, w=66, h=44, n=5):
    M.rayas(d, (x, y, x + w, y + h), n=n)


def cabecera(d, y=300):
    x = 100
    rayas_marca(d, x, y)
    M.texto(d, (x + 88, y + 2), "CHACO FOR EVER", F_BLACK, 30, fill=TINTA, tracking=2)
    M.texto(d, (x + 88, y + 40), "ESTADISTICAS", F_SEMI, 17, fill=DORADO, tracking=6)
    M.texto(d, (VW - 100, y + 14), "PRIMERA NACIONAL 2026", F_BOLD, 20, fill=GRIS, anchor="ra", tracking=3)


# --------------------------------------------------------------------------
# GRAFICO
# --------------------------------------------------------------------------
CX0, CX1 = 130, 940
CY0, CY1 = 790, 1250
YMAX = 42
LX0, LY0, LX1, LY1 = 40, 730, 1040, 1290          # capa del grafico (se dibuja a 2x)


def px(i, p):
    return CX0 + (CX1 - CX0) * i / N, CY1 - (CY1 - CY0) * p / YMAX


def estado(tt):
    """(partidos terminados, posicion fraccional de la cabeza (i, pts), progreso del ultimo)"""
    done = 0
    cabeza = (0.0, 0.0)
    for n in range(1, N + 1):
        if tt >= T0[n]:
            x = ease_out((tt - T0[n]) / (dur(n) * 0.72))
            cabeza = ((n - 1) + x, PTS[n - 1] + (PTS[n] - PTS[n - 1]) * x)
            if x >= 1:
                done = n
        else:
            break
    return done, cabeza


def grafico(img, tt, dim=1.0):
    k = 2
    capa = Image.new("RGB", ((LX1 - LX0) * k, (LY1 - LY0) * k), NEGRO)
    d = ImageDraw.Draw(capa)

    def L(x, y):
        return ((x - LX0) * k, (y - LY0) * k)

    # grilla
    for v in (0, 10, 20, 30, 40):
        x0, y = px(0, v)
        x1, _ = px(N, v)
        d.line([L(x0, y), L(x1, y)], fill=mezcla(GRIS_OSC, dim * (1 if v else 1.4)), width=2 * k // 2 + 1)
    # piso de la salvacion (punteado)
    _, ys = px(0, PISO_SALVACION)
    x = CX0
    while x < CX1:
        d.line([L(x, ys), L(min(x + 16, CX1), ys)], fill=mezcla(TINTA, 0.8 * dim), width=3 * k // 2)
        x += 28

    done, (hi, hp) = estado(tt)
    # polilinea
    pts = [(0, 0)]
    for n in range(1, int(hi) + 1):
        pts.append((n, PTS[n]))
    if hi > int(hi) or not pts or pts[-1][0] != hi:
        pts.append((hi, hp))
    for j in range(1, len(pts)):
        (a, pa), (b, pb) = pts[j - 1], pts[j]
        fase2 = b > CORTE_RECESO
        col = mezcla(DORADO if fase2 else TINTA, dim)
        p0, p1 = px(a, pa), px(b, pb)
        d.line([L(*p0), L(*p1)], fill=col, width=9 * k // 2 + 3)
        r = 4.5 * k
        for q in (p0, p1):
            cx, cy = L(*q)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # cabeza
    if tt >= T0[1] and hi > 0:
        hx, hy = L(*px(hi, hp))
        col = mezcla(DORADO if hi > CORTE_RECESO else TINTA, dim)
        pul = 1 + 0.12 * math.sin(tt * 14)
        r = 13 * k * pul
        halo = mezcla(col, 0.25)
        d.ellipse([hx - r * 1.9, hy - r * 1.9, hx + r * 1.9, hy + r * 1.9], fill=halo)
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=col)

    capa = capa.resize((LX1 - LX0, LY1 - LY0), Image.LANCZOS)
    img.paste(capa, (LX0, LY0))

    # textos del eje (nitidos, 1x)
    dd = ImageDraw.Draw(img)
    for v in (0, 10, 20, 30, 40):
        M.texto(dd, (CX0 - 18, px(0, v)[1]), str(v), F_SEMI, 22, fill=mezcla(GRIS, dim), anchor="rm")
    for f in (1, 10, 20, 30, 34):
        M.texto(dd, (px(f, 0)[0], CY1 + 18), str(f), F_SEMI, 22, fill=mezcla(GRIS, dim), anchor="mt")
    M.texto(dd, (CX0, CY1 + 52), "FECHA", F_BOLD, 18, fill=mezcla(GRIS, dim), tracking=4)
    M.texto(dd, (CX0, CY0 - 50), "PUNTOS ACUMULADOS", F_BOLD, 20, fill=mezcla(GRIS, dim), tracking=4)
    M.texto(dd, (CX0 + 8, ys - 12), "SALVACIÓN: 35 PTS", F_BOLD, 19, fill=mezcla(TINTA, 0.85 * dim),
            anchor="lb", tracking=3)


# --------------------------------------------------------------------------
# HUD, FICHAS Y TICKER
# --------------------------------------------------------------------------
def pos_actual(done):
    return 18 if done == 0 else int(S.pos[done - 1])


def etiqueta_pos(p):
    if p == 18:
        return "ÚLTIMO"
    if p == 17:
        return "ZONA DE DESCENSO"
    return "FUERA DEL DESCENSO"


def hud(img, tt, dim=1.0):
    dd = ImageDraw.Draw(img)
    done, _ = estado(tt)
    pos = pos_actual(done)
    pts = PTS[done]
    t_ult = T0[done] + dur(done) * 0.72 if done else 0
    esc = pop((tt - t_ult) / 0.3) if done else 1

    M.texto(dd, (100, 390), "POSICIÓN", F_BOLD, 22, fill=mezcla(GRIS, dim), tracking=5)
    texto_escalado(img, (100 + 150, 530), f"{pos}°", F_COND, 250, mezcla(TINTA, dim), esc)
    M.texto(dd, (100, 676), etiqueta_pos(pos), F_BOLD, 26,
            fill=mezcla(GRIS if pos >= 17 else TINTA, dim), tracking=3)

    M.texto(dd, (VW - 100, 390), "PUNTOS", F_BOLD, 22, fill=mezcla(GRIS, dim), anchor="ra", tracking=5)
    texto_escalado(img, (VW - 100 - 100, 530), str(pts), F_COND, 250, mezcla(TINTA, dim), esc)
    M.texto(dd, (VW - 100, 676), f"FECHA {done} DE {N}", F_BOLD, 26, fill=mezcla(GRIS, dim), anchor="ra",
            tracking=3)


def fichas(img, tt, dim=1.0):
    """Una ficha por partido: llena = ganó, hueca = empató, apagada = perdió."""
    d = ImageDraw.Draw(img)
    y = 1342
    for n in range(1, N + 1):
        if tt < T0[n] + dur(n) * 0.72:
            continue
        x, _ = px(n, 0)
        esc = pop((tt - (T0[n] + dur(n) * 0.72)) / 0.3)
        r = 9 * esc
        p = int(S.p[n - 1])
        if p == 3:
            d.ellipse([x - r, y - r, x + r, y + r], fill=mezcla(TINTA, dim))
        elif p == 1:
            d.ellipse([x - r, y - r, x + r, y + r], outline=mezcla(TINTA, dim), width=3)
        else:
            d.ellipse([x - r, y - r, x + r, y + r], fill=mezcla(GRIS_OSC, dim * 1.6))
    lx = CX0
    for lab, kind in (("GANÓ", 3), ("EMPATÓ", 1), ("PERDIÓ", 0)):
        r = 9
        cy = y + 46
        if kind == 3:
            d.ellipse([lx - r, cy - r, lx + r, cy + r], fill=mezcla(TINTA, dim))
        elif kind == 1:
            d.ellipse([lx - r, cy - r, lx + r, cy + r], outline=mezcla(TINTA, dim), width=3)
        else:
            d.ellipse([lx - r, cy - r, lx + r, cy + r], fill=mezcla(GRIS_OSC, dim * 1.6))
        M.texto(d, (lx + 20, cy), lab, F_BOLD, 18, fill=mezcla(GRIS, dim), anchor="lm", tracking=3)
        lx += 20 + int(len(lab) * 15) + 36


def ticker(img, tt, dim=1.0):
    done, _ = estado(tt)
    # el partido "actual" es el ultimo que ya empezo
    n = 0
    for k in range(1, N + 1):
        if tt >= T0[k]:
            n = k
    if n == 0:
        return
    a = ease_out((tt - T0[n]) / 0.18)
    dy = int((1 - a) * 26)
    r = S.iloc[n - 1]
    rival = CORTOS.get(r.rival, r.rival)
    res = {3: "VICTORIA", 1: "EMPATE", 0: "DERROTA"}[int(r.p)]
    d = ImageDraw.Draw(img)
    base = 1478 + dy
    M.texto(d, (100, base), f"FECHA {n}  ·  {'LOCAL' if r.local else 'VISITANTE'}", F_BOLD, 22,
            fill=mezcla(GRIS, a * dim), tracking=4)
    M.texto(d, (100, base + 40), f"vs {rival}", F_BLACK, 52, fill=mezcla(TINTA, a * dim))
    M.texto(d, (VW - 100, base + 40), f"{r.gf}-{r.gc}", F_COND, 72, fill=mezcla(TINTA, a * dim), anchor="ra")
    M.texto(d, (VW - 100, base), res, F_BOLD, 22, fill=mezcla(GRIS, a * dim), anchor="ra", tracking=4)


# --------------------------------------------------------------------------
# ESCENAS
# --------------------------------------------------------------------------
def escena_hook(tt):
    img, d = M.lienzo(NEGRO, (VW, VH))
    a = ease_out(tt / 0.30)
    esc = 1.0 + 0.05 * (1 - a)                 # ya visible en el cuadro 0 (es la portada)
    rayas_marca(d, 100, 520, 88, 60, 5)
    M.texto(d, (212, 526), "CHACO FOR EVER", F_BLACK, 40, fill=TINTA, tracking=3)
    M.texto(d, (212, 574), "TEMPORADA 2026", F_SEMI, 22, fill=GRIS, tracking=6)
    texto_escalado(img, (VW // 2, 840), "DE ÚLTIMO", F_BLACK, 150, TINTA, esc)
    texto_escalado(img, (VW // 2, 1010), "A SALVADO", F_BLACK, 150, DORADO, esc)
    # 18° -> 10°
    b = ease_out((tt - 0.25) / 0.35)
    if tt > 0.25 or True:
        col = mezcla(TINTA, 0.55 + 0.45 * max(b, 0.0))
        M.texto(d, (VW // 2 - 190, 1190), "18°", F_COND, 190, fill=col, anchor="mm")
        M.texto(d, (VW // 2, 1190), "→", F_BOLD, 110, fill=mezcla(GRIS, 0.55 + 0.45 * max(b, 0.0)), anchor="mm")
        M.texto(d, (VW // 2 + 190, 1190), "10°", F_COND, 190, fill=col, anchor="mm")
    c = ease_out((tt - 0.5) / 0.4)
    M.texto(d, (VW // 2, 1350), "ASÍ FUE, FECHA POR FECHA", F_BOLD, 30, fill=mezcla(GRIS, max(c, 0.0)),
            anchor="mm", tracking=5)
    return img


def escena_grafico(tt, dim=1.0):
    img, d = M.lienzo(NEGRO, (VW, VH))
    cabecera(d)
    hud(img, tt, dim)
    grafico(img, tt, dim)
    fichas(img, tt, dim)
    ticker(img, tt, dim)
    return img


def tarjeta_receso(img, tt):
    """Entre el 18 y el 19: 12 puntos en 18 fechas, ultimo. Gancho: que cambio?"""
    x = (tt - T_CARD) / DUR_CARD
    a = ease_out(x / 0.12) * (1 - ease_out((x - 0.88) / 0.12))
    ov = Image.new("RGB", (VW, VH), NEGRO)
    img.paste(Image.blend(img, ov, 0.86 * a), (0, 0))
    d = ImageDraw.Draw(img)
    esc = 1 + 0.12 * (1 - ease_out(x / 0.2))
    texto_escalado(img, (VW // 2, 700), "12 PUNTOS", F_BLACK, 148, mezcla(TINTA, a), esc)
    M.texto(d, (VW // 2, 820), "EN 18 FECHAS", F_BLACK, 76, fill=mezcla(TINTA, a), anchor="mm")
    M.texto(d, (VW // 2, 930), "0,67 por partido  ·  último desde la fecha 7", F_BOLD, 30,
            fill=mezcla(GRIS, a), anchor="mm", tracking=1)
    b = ease_out((x - 0.45) / 0.2)
    texto_escalado(img, (VW // 2, 1090), "¿QUÉ CAMBIÓ?", F_BLACK, 110, mezcla(DORADO, b),
                   1 + 0.1 * (1 - b))
    M.texto(d, (VW // 2, 1190), "DESPUÉS DEL RECESO", F_BOLD, 28, fill=mezcla(GRIS, b), anchor="mm", tracking=6)


def tarjeta_final(img, tt):
    x = tt - T_FIN
    a = ease_out(x / 0.35)
    ov = Image.new("RGB", (VW, VH), NEGRO)
    img.paste(Image.blend(img, ov, 0.97 * a), (0, 0))
    d = ImageDraw.Draw(img)
    M.texto(d, (VW // 2, 400), "TRAS 34 FECHAS", F_BOLD, 28, fill=mezcla(GRIS, a), anchor="mm", tracking=7)
    esc = pop(x / 0.55)
    texto_escalado(img, (VW // 2, 690), "10°", F_COND, 420, mezcla(DORADO, a), esc)
    M.texto(d, (VW // 2, 925), "40 PUNTOS  ·  SALVADOS", F_BLACK, 54, fill=mezcla(TINTA, a), anchor="mm")

    # dos barras: ritmo por partido antes y despues del receso
    filas = [("FECHAS 1–18", 12 / 18, "0,67"), ("FECHAS 19–34", 28 / 16, "1,75")]
    for i, (lab, v, txt) in enumerate(filas):
        y = 1040 + i * 118
        p = ease_out((x - 0.5 - i * 0.35) / 0.7)
        M.texto(d, (130, y), lab, F_BOLD, 24, fill=mezcla(GRIS, a), tracking=4)
        bw = int(420 * v / 1.75 * p)
        d.rectangle([130, y + 40, 130 + max(bw, 4), y + 72], fill=mezcla(TINTA if i else GRIS_OSC, a * 1.0 if i else a * 2))
        M.texto(d, (130 + max(bw, 4) + 20, y + 56), f"{txt} por partido", F_BLACK, 32,
                fill=mezcla(TINTA, a * p), anchor="lm")
    q = ease_out((x - 1.6) / 0.4)
    M.texto(d, (VW // 2, 1330), "¿EN QUÉ FECHA SENTISTE", F_BLACK, 44, fill=mezcla(TINTA, q), anchor="mm")
    M.texto(d, (VW // 2, 1388), "QUE SE SALVABA?", F_BLACK, 44, fill=mezcla(TINTA, q), anchor="mm")
    M.texto(d, (VW // 2, 1460), "Dejala en los comentarios", F_SEMI, 26, fill=mezcla(GRIS, q), anchor="mm",
            tracking=2)
    M.texto(d, (VW // 2, 1540), M.HANDLE, F_BOLD, 28, fill=mezcla(TINTA, q), anchor="mm", tracking=1)


_HOOK0 = None


def wipe(a_img, b_img, tt, t0):
    """Las rayas del club: columnas de A salen hacia arriba, escalonadas."""
    out = b_img.copy()
    n = 9
    cw = VW / n
    for i in range(n):
        p = ease_io((tt - t0 - i * 0.035) / (T_WIPE - 0.3))
        x0, x1 = int(i * cw), int((i + 1) * cw)
        sh = int(p * VH)
        if sh >= VH:
            continue
        col = a_img.crop((x0, sh, x1, VH))
        out.paste(col, (x0, 0))
        if p > 0:                                   # filo de la raya
            ImageDraw.Draw(out).rectangle([x0, VH - sh - 0, x1, VH - sh + 0], fill=NEGRO)
    return out


def cuadro(tt):
    global _HOOK0
    if _HOOK0 is None:
        _HOOK0 = escena_hook(0.0)
    if tt < T_HOOK - 0.1 + T_WIPE:
        a = escena_hook(min(tt, T_HOOK))
        if tt < T_HOOK - 0.1:
            return a
        b = escena_grafico(T_HOOK + 0.0)
        return wipe(a, b, tt, T_HOOK - 0.1)
    img = escena_grafico(tt)
    if T_CARD <= tt < T_CARD + DUR_CARD:
        tarjeta_receso(img, tt)
    if tt >= T_FIN:
        tarjeta_final(img, tt)
    if tt > T_TOTAL - FADE_LOOP:                    # vuelve al cuadro 0: el reel hace loop limpio
        k = ease_io((tt - (T_TOTAL - FADE_LOOP)) / FADE_LOOP)
        img = Image.blend(img, _HOOK0, k)
    return img


# --------------------------------------------------------------------------
# SONIDO (sintetizado)
# --------------------------------------------------------------------------
SR = 44100


def _env(n, a=0.005, r=0.3):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / r)


def nota(f, d=0.25, vol=0.3, tipo="sin", r=0.12):
    n = int(SR * d)
    t = np.arange(n) / SR
    if tipo == "tri":
        w = 2 * np.abs(2 * ((t * f) % 1) - 1) - 1
    else:
        w = np.sin(2 * np.pi * f * t)
    return w * _env(n, 0.004, r) * vol


def poner(buf, t0, s):
    i = int(t0 * SR)
    j = min(len(buf), i + len(s))
    if i < len(buf):
        buf[i:j] += s[: j - i]


def boom(vol=0.8, d=0.9):
    n = int(SR * d)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t * 6) + 38
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.2) * vol


def riser(d, vol=0.2):
    n = int(SR * d)
    t = np.arange(n) / SR
    rng = np.random.default_rng(3)
    ruido = rng.standard_normal(n)
    # filtro pasa-bajo que se abre
    out = np.zeros(n)
    acc = 0.0
    for i in range(n):
        c = 0.02 + 0.5 * (i / n) ** 2
        acc += c * (ruido[i] - acc)
        out[i] = acc
    return out / (np.abs(out).max() + 1e-9) * (t / d) ** 1.5 * vol


def reverb(x, mix=0.25):
    out = x.copy()
    for d, g in ((0.043, 0.5), (0.071, 0.4), (0.113, 0.3), (0.167, 0.2)):
        k = int(d * SR)
        out[k:] += x[:-k] * g * mix * 2
    return out


def audio():
    buf = np.zeros(int(SR * (T_TOTAL + 1.0)))
    poner(buf, 0.0, boom())
    poner(buf, 0.0, riser(0.5, 0.15)[::-1] * 0.8)
    # zumbido grave que tensa la racha mala
    td = np.arange(len(buf)) / SR
    zona = (td > T_HOOK) & (td < T_CARD + DUR_CARD)
    buf += np.where(zona, np.sin(2 * np.pi * 55 * td) * 0.06 * np.clip((td - T_HOOK) / 3, 0, 1), 0)

    escala = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24]            # pentatonica mayor
    for n in range(1, N + 1):
        t0 = T0[n] + dur(n) * 0.70
        p = int(S.p[n - 1])
        fase2 = n > CORTE_RECESO
        if p == 3:
            base = 440 * 2 ** (escala[min(len(escala) - 1, max(0, (PTS[n] - 12) // 3 if fase2 else 0))] / 12)
            poner(buf, t0, nota(base, 0.4, 0.28, r=0.18))
            poner(buf, t0 + 0.07, nota(base * 1.5, 0.45, 0.24, r=0.22))
            if fase2:
                poner(buf, t0, nota(base * 2, 0.5, 0.1, r=0.3))
        elif p == 1:
            poner(buf, t0, nota(392 if fase2 else 330, 0.28, 0.22, "tri", r=0.12))
        else:
            poner(buf, t0, nota(98, 0.3, 0.38, r=0.1))
            poner(buf, t0, nota(147, 0.2, 0.12, "tri", r=0.06))
    # tarjeta del receso: subida + golpe
    poner(buf, T_CARD, riser(DUR_CARD * 0.75, 0.22))
    poner(buf, T_CARD + DUR_CARD * 0.74, boom(0.55, 0.7))
    # cierre: acorde mayor con cola
    for k, f in enumerate((261.6, 329.6, 392.0, 523.3)):
        poner(buf, T_FIN, nota(f, 3.5, 0.17, r=1.2))
    poner(buf, T_FIN, boom(0.7, 1.0))
    buf = reverb(buf, 0.35)
    # fade para el loop
    n_f = int(SR * FADE_LOOP)
    fin = int(SR * T_TOTAL)
    buf[fin - n_f:fin] *= np.linspace(1, 0, n_f)
    buf = buf[:fin]
    buf = buf / (np.abs(buf).max() + 1e-9) * 0.89
    return (buf * 32767).astype(np.int16)


def guardar_wav(ruta, x):
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(x.tobytes())


# --------------------------------------------------------------------------
# RENDER
# --------------------------------------------------------------------------
def render(destino):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    wav = OUT / "_audio.wav"
    guardar_wav(wav, audio())
    total = int(round(T_TOTAL * FPS))
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
           "-r", str(FPS), "-i", "-", "-i", str(wav),
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", str(destino)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(total):
        p.stdin.write(cuadro(i / FPS).tobytes())
        if i % 60 == 0:
            print(f"  cuadro {i}/{total}", flush=True)
    p.stdin.close()
    p.wait()
    wav.unlink(missing_ok=True)
    print("listo:", destino, f"({T_TOTAL:.1f}s)")


if __name__ == "__main__":
    if "--prueba" in sys.argv:
        for nombre, tt in (("hook", 0.0), ("hook_mid", 1.5), ("wipe", T_HOOK + 0.2), ("g8", T0[8] + 0.45),
                           ("g17", T0[17] + 0.3), ("card", T_CARD + 1.1), ("g22", T0[22] + 0.4),
                           ("g30", T0[30] + 0.4), ("final", T_FIN + 3.0)):
            cuadro(tt).save(OUT / f"prueba_{nombre}.png")
        print("pruebas en", OUT, f"total {T_TOTAL:.1f}s")
    else:
        render(OUT / "chaco_progreso_puntos_2026.mp4")
