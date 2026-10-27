# -*- coding: utf-8 -*-
"""
Reel 9:16 v2 — "De último a salvado", contado como historia.

    venv/Scripts/python.exe redes_sociales/reels/progreso_puntos_v2.py [--prueba]

Diferencias con la v1:
  - La línea avanza CONTINUA (velocidad suavizada, sin frenar en cada partido) y
    una cámara la sigue con resortes amortiguados: zoom en los momentos clave,
    se aleja en la mala racha, encuadra toda la temporada al final.
  - Un solo texto central por momento (capítulos). El resto se apaga cuando hay
    un hito: la vista va a un único punto.
  - Los números ruedan (el viejo sale, el nuevo entra) en vez de saltar.
  - Desenfoque de movimiento: cada cuadro promedia 3 instantes.

Todos los hitos salen de datos_temporada.serie() y se verifican con asserts.
"""
import sys
import math
import os
import subprocess
import wave
from bisect import bisect_right
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

FPS, SUB = 30, 3
VW, VH = 1080, 1920
NEGRO, TINTA, DORADO, GRIS, GRIS_OSC = M.NEGRO, M.TINTA, M.DORADO, M.GRIS, M.GRIS_OSC
F_BLACK, F_BOLD, F_SEMI, F_COND = M.F_BLACK, M.F_BOLD, M.F_SEMI, M.F_COND

# --------------------------------------------------------------------------
# DATOS (y control de cada hito que se cuenta)
# --------------------------------------------------------------------------
S = datos_temporada.serie()
N = len(S)
PTS = [0] + list(S.pts)
POS = [18] + [int(x) for x in S.pos]
RES = [None] + [int(x) for x in S.p]
assert N == 34 and PTS[34] == 40 and POS[34] == 10
assert PTS[7] == 2 and RES.index(3) == 8                      # 2 pts en 7, 1ª victoria en el 8
assert PTS[18] == 12                                          # 12 pts en 18
assert all(POS[n] == 18 for n in range(7, 21)) and POS[21] == 17   # 14 seguidos último
assert RES[20:23] == [3, 3, 3] and max(                        # 1ª vez 3 seguidas
    sum(1 for _ in g) for k, g in __import__("itertools").groupby(RES[1:20]) if k == 3) == 1
assert RES[23:25] == [0, 0] and POS[24] == 17                 # 2 derrotas, vuelve a la zona
assert all(POS[n] <= 15 for n in range(25, 35))               # de ahí, nunca más
assert 0 not in RES[25:31] and PTS[30] - PTS[24] == 14        # 6 sin perder, 14 de 18
assert PTS[30] == 36 and PTS[29] < 35                         # cruza la línea en el 30

PISO = 35                       # puntos del 16° al cierre (All Boys)
RECESO = 18

CORTOS = {
    "Club Ferro Carril Oeste": "Ferro", "Club Atletico Colón": "Colón",
    "Gimnasia Y Esgrima De Jujuy": "Gimnasia de Jujuy", "Gimnasia Jujuy": "Gimnasia de Jujuy",
    "Estudiantes de Buenos Aires": "Estudiantes", "CA Mitre": "Mitre",
    "Central Norte de Salta": "Central Norte", "Deportivo Morón": "Morón",
    "Deportivo Madryn": "Madryn", "Defensores de Belgrano": "Defensores",
    "Ciudad de Bolivar": "Ciudad de Bolívar",
}


def n_de(g):
    return int(math.floor(g + 1e-6))


# --------------------------------------------------------------------------
# GUIÓN: capítulos. run = la línea avanza; hold = se detiene (hito).
# cap = (título, bajada) o función de g. z = zoom de la cámara. hito = foco.
# --------------------------------------------------------------------------
def c_ultimo(g):
    n = max(7, n_de(g))
    return "ÚLTIMO", f"{min(n, 20) - 6} partidos seguidos en el fondo de la tabla"


def c_suma(g):
    v = PTS[n_de(g)] - 12
    return "VUELVE A SUMAR", f"{v} punto{'s' if v != 1 else ''} después del receso"


def c_invicto(g):
    n = n_de(g)
    return "NO PIERDE", f"{max(2, n - 24)} partidos seguidos sin derrota"


GUION = [
    dict(k="hold", d=0.9, z=2.6, cap=("ARRANCA LA TEMPORADA", "Primera Nacional 2026 · Grupo A")),
    dict(k="run", g=(0, 7), d=4.9, z=2.4, cap=("ARRANCA DE ATRÁS", "2 puntos en los primeros 7 partidos")),
    dict(k="run", g=(7, 8), d=0.9, z=3.0, cap=("ARRANCA DE ATRÁS", "2 puntos en los primeros 7 partidos")),
    dict(k="hold", d=2.0, z=3.4, hito=1, cap=("PARTIDO 8", "Llega la primera victoria: 2-0 a All Boys")),
    dict(k="run", g=(8, 18), d=5.6, z=1.6, cap=c_ultimo),
    dict(k="hold", d=2.4, z=2.0, hito=1, cap=("12 PUNTOS EN 18 PARTIDOS", "0,67 por partido · último")),
    dict(k="hold", d=3.2, z=2.6, hito=1, receso=1, cap=("RECESO", "Se corta el torneo. Vuelve el 5 de julio")),
    dict(k="run", g=(18, 20), d=1.8, z=2.6, cap=c_suma),
    dict(k="run", g=(20, 21), d=0.8, z=3.0, cap=c_suma),
    dict(k="hold", d=1.9, z=3.3, hito=1, cap=("DEJA EL ÚLTIMO LUGAR", "Después de 14 partidos")),
    dict(k="run", g=(21, 22), d=0.8, z=3.0, cap=("DEJA EL ÚLTIMO LUGAR", "Después de 14 partidos")),
    dict(k="hold", d=2.0, z=3.3, hito=1, cap=("3 VICTORIAS SEGUIDAS", "La primera vez en el año")),
    dict(k="run", g=(22, 24), d=1.8, z=2.8, cap=("DOS GOLPES", "Pierde con Godoy Cruz y con Gimnasia")),
    dict(k="hold", d=1.6, z=3.2, hito=1, cap=("VUELVE A LA ZONA", "17° otra vez")),
    dict(k="run", g=(24, 26), d=1.8, z=2.8, cap=("PERO REACCIONA", "Le gana a Los Andes y a San Miguel")),
    dict(k="hold", d=1.9, z=3.2, hito=1, cap=("Y ESTA VEZ, PARA QUEDARSE", "Nunca más volvió a la zona")),
    dict(k="run", g=(26, 30), d=3.2, z=2.6, cap=c_invicto),
    dict(k="hold", d=2.6, z=3.2, hito=1, cruce=1,
         cap=("36 PUNTOS", "Pasa la línea de salvación · 14 de 18 en 6 partidos")),
    dict(k="run", g=(30, 34), d=2.6, z=2.4, cap=("LA RECTA FINAL", "4 partidos más")),
    dict(k="hold", d=0.4, z=2.4, cap=("LA RECTA FINAL", "4 partidos más")),
]

T_TR0, T_TR1 = 2.9, 4.1          # transición portada -> gráfico
T_START = T_TR1
t = T_START
for s in GUION:
    s["t0"], s["t1"] = t, t + s["d"]
    t += s["d"]
T_FIN = t                         # arranca el cierre (cámara se aleja)
T_TOTAL = T_FIN + 7.2
FADE_LOOP = 0.6
SEG_T0 = [s["t0"] for s in GUION]


def seg_en(tt):
    if tt < T_START:
        return -1
    i = bisect_right(SEG_T0, tt) - 1
    return min(i, len(GUION) - 1)


# --------------------------------------------------------------------------
# SIMULACIÓN: avance de la línea + cámara con resortes (determinística)
# --------------------------------------------------------------------------
HZ = 240
NS = int((T_TOTAL + 0.5) * HZ)
TS = np.arange(NS) / HZ

vel = np.zeros(NS)
for s in GUION:
    if s["k"] == "run":
        a, b = s["g"]
        vel[(TS >= s["t0"]) & (TS < s["t1"])] = (b - a) / s["d"]
sig = 0.20 * HZ
ker = np.exp(-0.5 * (np.arange(-int(4 * sig), int(4 * sig) + 1) / sig) ** 2)
ker /= ker.sum()
vel = np.convolve(vel, ker, mode="same")
G = np.cumsum(vel) / HZ
G *= N / G[-1]                                    # cierra exacto en 34
HY = np.interp(G, np.arange(N + 1), PTS)

# objetivos de cámara
tz = np.full(NS, 2.6)
tcx, tcy, tax = G.copy(), HY.copy(), np.full(NS, 0.60)
tspot = np.zeros(NS)
for s in GUION:
    m = (TS >= s["t0"]) & (TS < s["t1"])
    tz[m] = s["z"]
    tspot[m] = s.get("hito", 0)
m = TS >= T_FIN
tz[m], tcx[m], tcy[m], tax[m] = 1.0, N / 2, 20.5, 0.5


def resorte(obj, w, x0):
    x, v = x0, 0.0
    out = np.empty(NS)
    dt = 1 / HZ
    for i in range(NS):
        v += (w * w * (obj[i] - x) - 2 * w * v) * dt
        x += v * dt
        out[i] = x
    return out


CZ = resorte(tz, 2.2, 2.6)
CX = resorte(tcx, 3.2, 0.0)
CY = resorte(tcy, 2.6, 0.0)
CAX = resorte(tax, 2.0, 0.6)
SPOT = resorte(tspot, 4.0, 0.0)

# instante en que la cabeza llega a cada partido
TG = [T_START] + [float(TS[np.argmax(G >= n - 1e-4)]) for n in range(1, N + 1)]


def sim(tt):
    i = min(max(int(tt * HZ), 0), NS - 2)
    f = tt * HZ - i
    return {k: A[i] * (1 - f) + A[i + 1] * f for k, A in
            (("g", G), ("hy", HY), ("z", CZ), ("cx", CX), ("cy", CY), ("ax", CAX), ("spot", SPOT))}


def n_hasta(tt):
    return max(0, bisect_right(TG[1:], tt))


# --------------------------------------------------------------------------
# PRIMITIVAS
# --------------------------------------------------------------------------
def cl(x):
    return min(max(x, 0.0), 1.0)


def ease_out(x):
    return 1 - (1 - cl(x)) ** 3


def ease_io(x):
    x = cl(x)
    return x * x * (3 - 2 * x)


def mezcla(c, a):
    a = cl(a)
    return tuple(int(NEGRO[i] + (c[i] - NEGRO[i]) * a) for i in range(3))


def lerp(a, b, k):
    return a + (b - a) * k


_DUMMY = ImageDraw.Draw(Image.new("L", (1, 1)))


def ancho(s, fpath, size, tracking=0):
    return M._ancho(_DUMMY, s, M.fuente(fpath, size), tracking)


def texto_esc(img, centro, s, fpath, size, fill, escala=1.0, tracking=0):
    """Texto centrado con escala arbitraria (se dibuja al tamaño final: nítido)."""
    size_r = max(6, int(round(size * escala)))
    d = ImageDraw.Draw(img)
    M.texto(d, centro, s, fpath, size_r, fill=fill, anchor="mm", tracking=int(tracking * escala))


def cortar(s, fpath, size, maxw):
    pal, lineas, cur = s.split(), [], ""
    for p in pal:
        prueba = (cur + " " + p).strip()
        if ancho(prueba, fpath, size) <= maxw or not cur:
            cur = prueba
        else:
            lineas.append(cur)
            cur = p
    lineas.append(cur)
    return lineas


# --------------------------------------------------------------------------
# CAPAS
# --------------------------------------------------------------------------
Y_CAP = 505                     # centro del bloque de texto
VX0, VY0, VW_, VH_ = 60, 660, 960, 630      # visor del gráfico
SX0, SY0 = VW_ / 37.0, VH_ / 46.0
Y_HUD = 1478
Y_TICK = 1590


def cabecera(d, a=1.0):
    x, y = 100, 292
    M.rayas(d, (x, y, x + 56, y + 36), colores=(mezcla(M.BLANCO, a), NEGRO), n=5)
    M.texto(d, (x + 74, y), "CHACO FOR EVER", F_BLACK, 26, fill=mezcla(TINTA, a), tracking=2)
    M.texto(d, (x + 74, y + 33), "ESTADISTICAS", F_SEMI, 15, fill=mezcla(DORADO, a), tracking=6)
    M.texto(d, (VW - 100, y + 10), "PRIMERA NACIONAL 2026", F_BOLD, 18, fill=mezcla(GRIS, a),
            anchor="ra", tracking=3)


def texto_cap(img, cap, a, dy):
    if a <= 0.01:
        return
    tit, baj = cap
    for size in (96, 86, 76):
        lin = cortar(tit, F_BLACK, size, 940)
        if len(lin) <= 2:
            break
    lh = int(size * 1.08)
    alto = len(lin) * lh + 64
    y = Y_CAP - alto / 2 + dy
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lin):
        M.texto(d, (VW // 2, y + i * lh + lh / 2), l, F_BLACK, size, fill=mezcla(TINTA, a), anchor="mm")
    sb = 34
    while ancho(baj, F_SEMI, sb) > 940 and sb > 24:
        sb -= 2
    M.texto(d, (VW // 2, y + len(lin) * lh + 36), baj, F_SEMI, sb, fill=mezcla(GRIS, a * 1.15), anchor="mm")


def captions(img, tt, g):
    i = seg_en(tt)
    if i < 0:
        return
    s = GUION[i]

    def val(cap, gg):
        return cap(gg) if callable(cap) else cap

    cur = val(s["cap"], g)
    # el cambio de capítulo se reconoce por el título
    prev = None
    if i > 0:
        p = GUION[i - 1]
        prev = val(p["cap"], p["g"][1] if p["k"] == "run" else g)
    if tt >= T_FIN:
        return
    a_in = ease_out((tt - T_START) / 0.6) if i == 0 else 1.0
    if prev and prev[0] != cur[0] and tt - s["t0"] < 0.6:
        k = ease_io((tt - s["t0"]) / 0.6)
        texto_cap(img, prev, 1 - k, -36 * k)
        texto_cap(img, cur, k, 36 * (1 - k))
    else:
        texto_cap(img, cur, a_in, 30 * (1 - a_in))


def a_pantalla(wx, wy, c, k=1):
    sx, sy = SX0 * c["z"], SY0 * c["z"]
    return ((c["ax"] * VW_ + (wx - c["cx"]) * sx) * k,
            (0.5 * VH_ - (wy - c["cy"]) * sy) * k)


def grafico(tt, c, alpha=1.0):
    """Devuelve el visor (VW_ x VH_) ya reducido desde 2x."""
    k = 2
    capa = Image.new("RGB", (VW_ * k, VH_ * k), NEGRO)
    d = ImageDraw.Draw(capa)
    P = lambda x, y: a_pantalla(x, y, c, k)                       # noqa: E731
    sx = SX0 * c["z"]

    # grilla horizontal
    paso = 10 if c["z"] < 1.8 else 5
    x_ini, _ = P(0, 0)
    x_fin, _ = P(N, 0)
    for v in range(0, 45, paso):
        _, y = P(0, v)
        if -20 < y < VH_ * k + 20:
            d.line([(max(x_ini, 0), y), (min(x_fin, VW_ * k), y)], fill=mezcla(GRIS_OSC, alpha), width=2)
            M.texto(d, (max(x_ini, 0) - 14 if x_ini > 60 else 50, y), str(v), F_SEMI, 40,
                    fill=mezcla(GRIS, alpha), anchor="rm")
    # partidos en el eje x
    step = 1 if sx >= 52 else 5
    _, y0 = P(0, 0)
    for n in [1] + list(range(step, N + 1, step)) + [N]:
        x, _ = P(n, 0)
        if 30 < x < VW_ * k - 30:
            M.texto(d, (x, y0 + 26), str(n), F_SEMI, 36, fill=mezcla(GRIS, alpha), anchor="mt")
    # línea de salvación
    _, ys = P(0, PISO)
    if -20 < ys < VH_ * k:
        x = max(x_ini, 0)
        while x < min(x_fin, VW_ * k):
            d.line([(x, ys), (x + 24, ys)], fill=mezcla(TINTA, 0.75 * alpha), width=4)
            x += 42
        M.texto(d, (VW_ * k - 24, ys - 16), "SALVACIÓN · 35 PTS", F_BOLD, 34,
                fill=mezcla(TINTA, 0.85 * alpha), anchor="rb", tracking=5)
    # marca del receso
    if tt >= GUION[6]["t0"]:
        a_r = ease_out((tt - GUION[6]["t0"]) / 0.8) * alpha
        xr, _ = P(RECESO + 0.5, 0)
        _, ytop = P(0, 44)
        yy = y0
        while yy > ytop:
            d.line([(xr, yy), (xr, yy - 14)], fill=mezcla(GRIS, 0.8 * a_r), width=3)
            yy -= 28
        M.texto(d, (xr + 14, max(ytop, 30)), "RECESO", F_BOLD, 30, fill=mezcla(GRIS, a_r), tracking=5)

    # línea de puntos
    g = c["g"]
    nv = n_de(g)
    pts = [(n, PTS[n]) for n in range(0, nv + 1)]
    if g - nv > 1e-4:
        pts.append((g, c["hy"]))
    W = 18
    for j in range(1, len(pts)):
        (a, pa), (b, pb) = pts[j - 1], pts[j]
        col = mezcla(DORADO if b > RECESO + 1e-6 else TINTA, alpha)
        d.line([P(a, pa), P(b, pb)], fill=col, width=W)
        for q in (P(a, pa), P(b, pb)):
            d.ellipse([q[0] - W / 2, q[1] - W / 2, q[0] + W / 2, q[1] + W / 2], fill=col)
    # vértices = resultado (lleno ganó, hueco empató, oscuro perdió)
    r = 15 if c["z"] > 1.5 else 11
    for n in range(1, nv + 1):
        x, y = P(n, PTS[n])
        if not (-30 < x < VW_ * k + 30):
            continue
        col = mezcla(DORADO if n > RECESO else TINTA, alpha)
        if RES[n] == 3:
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        elif RES[n] == 1:
            d.ellipse([x - r, y - r, x + r, y + r], fill=NEGRO, outline=col, width=6)
        else:
            d.ellipse([x - r, y - r, x + r, y + r], fill=mezcla(GRIS_OSC, alpha), outline=col, width=5)
    # cabeza + ondas en los hitos
    hx, hy = P(g, c["hy"])
    col = DORADO if g > RECESO + 1e-6 else TINTA
    for s in GUION:
        if s.get("hito") and s["t0"] <= tt < s["t0"] + 1.6 and tt < T_FIN:
            for dl in (0.0, 0.35):
                q = (tt - s["t0"] - dl) / 1.1
                if 0 < q < 1:
                    rr = (30 + 150 * ease_out(q)) * k
                    d.ellipse([hx - rr, hy - rr, hx + rr, hy + rr], outline=mezcla(col, (1 - q) * 0.9 * alpha),
                              width=int(5 * k * (1 - q) + 2))
    pul = 1 + 0.10 * math.sin(tt * 7)
    rr = 17 * k * pul
    d.ellipse([hx - rr * 2.1, hy - rr * 2.1, hx + rr * 2.1, hy + rr * 2.1], fill=mezcla(col, 0.18 * alpha))
    d.ellipse([hx - rr, hy - rr, hx + rr, hy + rr], fill=mezcla(col, alpha))

    vis = capa.resize((VW_, VH_), Image.LANCZOS)

    # foco: se oscurece todo menos alrededor de la cabeza; bordes del visor se funden
    arr = np.asarray(vis).astype(np.float32)
    yy, xx = np.mgrid[0:VH_, 0:VW_]
    dist = np.hypot(xx - hx / k, yy - hy / k)
    foco = 1 - 0.62 * c["spot"] * np.clip((dist - 110) / 330, 0, 1)
    borde = np.minimum(np.clip(xx / 40, 0, 1), np.clip((VW_ - 1 - xx) / 40, 0, 1))
    borde = np.minimum(borde, np.minimum(np.clip(yy / 30, 0, 1), np.clip((VH_ - 1 - yy) / 30, 0, 1)))
    f = (foco * borde)[..., None]
    bg = np.array(NEGRO, np.float32)
    arr = bg + (arr - bg) * f
    return Image.fromarray(arr.astype(np.uint8))


def leyenda(d, a):
    items = (("GANÓ", 3), ("EMPATÓ", 1), ("PERDIÓ", 0))
    anchos = [24 + ancho(l, F_BOLD, 17, 3) + 34 for l, _ in items]
    x = VW // 2 - sum(anchos) / 2
    y = VY0 + VH_ + 22
    for (lab, kk), w in zip(items, anchos):
        r = 8
        cx = x + r
        if kk == 3:
            d.ellipse([cx - r, y - r, cx + r, y + r], fill=mezcla(TINTA, a))
        elif kk == 1:
            d.ellipse([cx - r, y - r, cx + r, y + r], outline=mezcla(TINTA, a), width=3)
        else:
            d.ellipse([cx - r, y - r, cx + r, y + r], fill=mezcla(GRIS_OSC, a * 1.5), outline=mezcla(TINTA, a), width=2)
        M.texto(d, (x + 24, y), lab, F_BOLD, 17, fill=mezcla(GRIS, a), anchor="lm", tracking=3)
        x += w


def rodar(img, centro, nuevo, viejo, q, fpath, size, color, a, tracking=0):
    """El valor viejo sube y se va; el nuevo entra desde abajo."""
    if viejo is None or q >= 1:
        texto_esc(img, centro, nuevo, fpath, size, mezcla(color, a), tracking=tracking)
        return
    e = ease_io(q)
    h = size * 0.55
    if a * (1 - e) ** 2 < 0.03:
        texto_esc(img, (centro[0], centro[1] + h * (1 - e)), nuevo, fpath, size, mezcla(color, a * e ** 2),
                  tracking=tracking)
        return
    texto_esc(img, (centro[0], centro[1] - h * e), viejo, fpath, size, mezcla(color, a * (1 - e) ** 2), tracking=tracking)
    texto_esc(img, (centro[0], centro[1] + h * (1 - e)), nuevo, fpath, size, mezcla(color, a * e ** 2), tracking=tracking)


def hud(img, tt, a, morph=None):
    d = ImageDraw.Draw(img)
    n = n_hasta(tt)
    q = (tt - TG[n]) / 0.45 if n else 1
    if morph is None:
        rodar(img, (290, Y_HUD), f"{POS[n]}°", f"{POS[n-1]}°" if n and POS[n - 1] != POS[n] else None,
              q, F_COND, 160, TINTA, a)
    rodar(img, (790, Y_HUD), str(PTS[n]), str(PTS[n - 1]) if n and PTS[n - 1] != PTS[n] else None,
          q, F_COND, 160, TINTA, a)
    # partido actual
    m = n_hasta(tt + 0.25)                         # se anuncia un poco antes de llegar
    if m:
        r = S.iloc[m - 1]
        txt = (f"PARTIDO {m}  ·  {'vs' if r.local else 'en'} {CORTOS.get(r.rival, r.rival)}"
               f"  ·  {r.gf}-{r.gc}")
        qq = (tt + 0.25 - TG[m]) / 0.4
        viejo = None
        if m > 1:
            rv = S.iloc[m - 2]
            viejo = (f"PARTIDO {m-1}  ·  {'vs' if rv.local else 'en'} {CORTOS.get(rv.rival, rv.rival)}"
                     f"  ·  {rv.gf}-{rv.gc}")
        size = 30
        while max(ancho(txt, F_BOLD, size, 2), ancho(viejo or "", F_BOLD, size, 2)) > 960:
            size -= 1
        rodar(img, (VW // 2, Y_TICK), txt, viejo, qq, F_BOLD, size, TINTA, a * 0.92, tracking=2)
    # etiquetas al final: lo que rueda nunca las tapa
    d.rectangle([0, Y_HUD - 112, VW, Y_HUD - 74], fill=NEGRO)
    for x, lab in ((290, "POSICIÓN"), (790, "PUNTOS")):
        M.texto(d, (x, Y_HUD - 92), lab, F_BOLD, 21, fill=mezcla(GRIS, a), anchor="mm", tracking=6)
    d.line([(VW // 2, Y_HUD - 70), (VW // 2, Y_HUD + 60)], fill=mezcla(GRIS_OSC, a), width=2)


# --------------------------------------------------------------------------
# PORTADA y CIERRE
# --------------------------------------------------------------------------
HOOK_18 = (VW // 2 - 190, 1190, 190)


def portada(img, tt, a_tit=1.0, a_fila=1.0, dy=0.0, con18=True):
    d = ImageDraw.Draw(img)
    deriva = 1 + 0.025 * ease_io(tt / 3.0)
    x0 = 100
    M.rayas(d, (x0, 520 + dy, x0 + 88, 580 + dy), colores=(mezcla(M.BLANCO, a_tit), NEGRO), n=5)
    M.texto(d, (x0 + 112, 526 + dy), "CHACO FOR EVER", F_BLACK, 40, fill=mezcla(TINTA, a_tit), tracking=3)
    M.texto(d, (x0 + 112, 574 + dy), "TEMPORADA 2026", F_SEMI, 22, fill=mezcla(GRIS, a_tit), tracking=6)
    texto_esc(img, (VW // 2, 840 + dy), "DE ÚLTIMO", F_BLACK, 150, mezcla(TINTA, a_tit), deriva)
    texto_esc(img, (VW // 2, 1010 + dy), "A SALVADO", F_BLACK, 150, mezcla(DORADO, a_tit), deriva)
    b = 0.55 + 0.45 * ease_out((tt - 0.3) / 0.5)
    if con18:
        M.texto(d, (HOOK_18[0], HOOK_18[1]), "18°", F_COND, 190, fill=mezcla(TINTA, b * a_fila), anchor="mm")
    M.texto(d, (VW // 2, 1190), "→", F_BOLD, 110, fill=mezcla(GRIS, b * a_fila), anchor="mm")
    M.texto(d, (VW // 2 + 190, 1190), "10°", F_COND, 190, fill=mezcla(TINTA, b * a_fila), anchor="mm")
    c = ease_out((tt - 0.6) / 0.5)
    M.texto(d, (VW // 2, 1350 + dy), "CÓMO SE SALVÓ, PARTIDO A PARTIDO", F_BOLD, 28,
            fill=mezcla(GRIS, c * a_fila), anchor="mm", tracking=4)


def cierre(img, tt):
    x = tt - T_FIN
    d = ImageDraw.Draw(img)
    a = ease_out((x - 0.7) / 0.7)
    texto_esc(img, (VW // 2, 440), "10°", F_COND, 250, mezcla(DORADO, a), 1 + 0.15 * (1 - ease_out((x - 0.7) / 0.9)))
    M.texto(d, (VW // 2, 590), "40 PUNTOS  ·  SALVADOS", F_BLACK, 50, fill=mezcla(TINTA, a), anchor="mm")
    # ritmo antes / después del receso (reemplaza al marcador)
    filas = [("PARTIDOS 1 AL 18", 12 / 18, "0,67", GRIS_OSC), ("PARTIDOS 19 AL 34", 28 / 16, "1,75", TINTA)]
    for i, (lab, v, txt, col) in enumerate(filas):
        y = 1360 + i * 100
        p = ease_out((x - 1.8 - i * 0.5) / 0.9)
        al = ease_out((x - 1.6 - i * 0.5) / 0.4)
        M.texto(d, (120, y), lab, F_BOLD, 22, fill=mezcla(GRIS, al), tracking=4)
        bw = int(500 * v / 1.75 * p)
        if bw > 2:
            d.rectangle([120, y + 34, 120 + bw, y + 64], fill=mezcla(col, al * (1.6 if i == 0 else 1)))
        M.texto(d, (120 + bw + 22, y + 49), f"{txt} por partido", F_BLACK, 32, fill=mezcla(TINTA, al * p),
                anchor="lm")
    qq = ease_out((x - 3.4) / 0.6)
    M.texto(d, (VW // 2, 1592), "¿EN QUÉ PARTIDO SENTISTE QUE SE SALVABA?", F_BLACK, 36,
            fill=mezcla(TINTA, qq), anchor="mm")


# --------------------------------------------------------------------------
# CUADRO
# --------------------------------------------------------------------------
_PORTADA0 = None


def escena(tt):
    img, d = M.lienzo(NEGRO, (VW, VH))
    if tt < T_TR0:
        portada(img, tt)
        return img

    c = sim(max(tt, T_START))
    k = ease_io((tt - T_TR0) / (T_TR1 - T_TR0))      # transición 0..1
    fin = ease_io((tt - T_FIN - 0.2) / 0.8) if tt >= T_FIN else 0.0

    cabecera(d, k)
    if k < 1:
        portada(img, tt, a_tit=1 - k, a_fila=1 - ease_out(k * 1.6), dy=-90 * k, con18=False)
    captions(img, tt, c["g"])
    if tt >= T_FIN:
        cierre(img, tt)

    vis = grafico(tt, c, alpha=k)
    img.paste(vis, (VX0, VY0))
    leyenda(d, k * (1 - fin))

    a_hud = k * (1 - 0.6 * c["spot"]) * (1 - fin)
    if k < 1:                                        # el 18° de la portada viaja al marcador
        hud(img, tt, a_hud, morph=True)
        x = lerp(HOOK_18[0], 290, k)
        y = lerp(HOOK_18[1], Y_HUD, k)
        texto_esc(img, (x, y), "18°", F_COND, 160, mezcla(TINTA, lerp(1.0, a_hud, k)), lerp(190 / 160, 1, k))
    elif a_hud > 0.01:
        hud(img, tt, a_hud)
    return img


def cuadro(tt):
    """Promedia SUB instantes dentro de medio cuadro (desenfoque de movimiento)."""
    global _PORTADA0
    if _PORTADA0 is None:
        _PORTADA0 = np.asarray(escena(0.0)).astype(np.float32)
    acc = None
    for j in range(SUB):
        ts = tt + (j - (SUB - 1) / 2) * (0.5 / FPS) / max(SUB - 1, 1)
        a = np.asarray(escena(max(ts, 0.0))).astype(np.float32)
        acc = a if acc is None else acc + a
    acc /= SUB
    if tt > T_TOTAL - FADE_LOOP:                     # loop limpio al cuadro 0
        kk = ease_io((tt - (T_TOTAL - FADE_LOOP)) / FADE_LOOP)
        acc = acc * (1 - kk) + _PORTADA0 * kk
    return acc.astype(np.uint8)


# --------------------------------------------------------------------------
# SONIDO
# --------------------------------------------------------------------------
SR = 44100


def _env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / r)


def nota(f, d=0.3, vol=0.3, tipo="sin", r=0.15):
    n = int(SR * d)
    t = np.arange(n) / SR
    w = (2 * np.abs(2 * ((t * f) % 1) - 1) - 1) if tipo == "tri" else np.sin(2 * np.pi * f * t)
    return w * _env(n, 0.006, r) * vol


def poner(buf, t0, s):
    i = int(t0 * SR)
    j = min(len(buf), i + len(s))
    if 0 <= i < len(buf):
        buf[i:j] += s[: j - i]


def boom(vol=0.8, d=1.0):
    n = int(SR * d)
    t = np.arange(n) / SR
    f = 110 * np.exp(-t * 6) + 40
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.8) * vol


def ruido_filtrado(d, abre=True, vol=0.2, seed=3):
    n = int(SR * d)
    x = np.random.default_rng(seed).standard_normal(n)
    out = np.empty(n)
    acc = 0.0
    for i in range(n):
        c = 0.01 + 0.45 * ((i / n) if abre else (1 - i / n)) ** 2
        acc += c * (x[i] - acc)
        out[i] = acc
    out /= np.abs(out).max() + 1e-9
    env = (np.arange(n) / n) ** 1.6 if abre else np.sin(np.pi * np.arange(n) / n)
    return out * env * vol


def reverb(x, mix=0.3):
    out = x.copy()
    for dl, g in ((0.037, 0.5), (0.061, 0.42), (0.097, 0.33), (0.149, 0.25), (0.211, 0.18)):
        k = int(dl * SR)
        out[k:] += x[:-k] * g * mix * 2
    return out


def audio():
    L = int(SR * T_TOTAL)
    buf = np.zeros(L + SR)
    td = np.arange(len(buf)) / SR
    poner(buf, 0.0, boom(0.8))
    poner(buf, T_TR0 - 0.2, ruido_filtrado(0.9, abre=False, vol=0.18))      # barrido de transición
    # cama: pulso grave hasta el receso, acorde que respira después
    rec0, rec1 = GUION[6]["t0"], GUION[6]["t1"]
    m1 = (td > T_START) & (td < rec0)
    buf += np.where(m1, np.sin(2 * np.pi * 55 * td) * 0.05 * (0.6 + 0.4 * np.sin(2 * np.pi * 1.0 * td)), 0)
    m2 = (td > rec1) & (td < T_FIN + 6)
    sube = np.clip((td - rec1) / 6, 0, 1)
    for f in (130.8, 196.0, 261.6):
        buf += np.where(m2, np.sin(2 * np.pi * f * td) * 0.022 * sube, 0)
    escala = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26]
    for n in range(1, N + 1):
        t0 = TG[n]
        f2 = n > RECESO
        if RES[n] == 3:
            base = 440 * 2 ** (escala[min(len(escala) - 1, (n - 18) // 2 if f2 else 0)] / 12)
            poner(buf, t0, nota(base, 0.5, 0.24, r=0.2))
            poner(buf, t0 + 0.06, nota(base * 1.5, 0.55, 0.2, r=0.25))
        elif RES[n] == 1:
            poner(buf, t0, nota(392 if f2 else 330, 0.3, 0.18, "tri", r=0.12))
        else:
            poner(buf, t0, nota(92, 0.35, 0.34, r=0.12))
    for s in GUION:
        if s.get("hito"):
            poner(buf, s["t0"], boom(0.32, 0.6))
            poner(buf, s["t0"], nota(880, 1.0, 0.06, r=0.5))
    # receso: silencio, subida y golpe al volver
    poner(buf, rec1 - 1.6, ruido_filtrado(1.6, abre=True, vol=0.22))
    poner(buf, rec1, boom(0.6, 0.8))
    # cruce de la línea y cierre
    s_cr = next(s for s in GUION if s.get("cruce"))
    for f in (523.3, 659.3, 784.0):
        poner(buf, s_cr["t0"], nota(f, 1.4, 0.07, r=0.6))
    poner(buf, T_FIN + 0.7, boom(0.75, 1.2))
    for f in (261.6, 329.6, 392.0, 523.3):
        poner(buf, T_FIN + 0.7, nota(f, 4.5, 0.13, r=1.6))
    buf = reverb(buf, 0.35)[:L]
    nf = int(SR * FADE_LOOP)
    buf[-nf:] *= np.linspace(1, 0, nf)
    buf = buf / (np.abs(buf).max() + 1e-9) * 0.89
    return (buf * 32767).astype(np.int16)


# --------------------------------------------------------------------------
# RENDER (en paralelo, en orden)
# --------------------------------------------------------------------------
def _trabajo(i):
    return cuadro(i / FPS).tobytes()


def render(destino):
    import imageio_ffmpeg
    from multiprocessing import Pool
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    wav = OUT / "_audio_v2.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(audio().tobytes())
    total = int(round(T_TOTAL * FPS))
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
           "-r", str(FPS), "-i", "-", "-i", str(wav),
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "192k", "-shortest", str(destino)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(max(1, min(12, (os.cpu_count() or 4) - 2))) as pool:
        for i, fr in enumerate(pool.imap(_trabajo, range(total), chunksize=4)):
            p.stdin.write(fr)
            if i % 150 == 0:
                print(f"  cuadro {i}/{total}", flush=True)
    p.stdin.close()
    p.wait()
    wav.unlink(missing_ok=True)
    print("listo:", destino, f"({T_TOTAL:.1f}s)")


if __name__ == "__main__":
    if "--prueba" in sys.argv:
        marcas = [("00_portada", 0.0), ("01_trans", (T_TR0 + T_TR1) / 2)]
        for i, s in enumerate(GUION):
            marcas.append((f"{i+2:02d}_seg{i}", s["t0"] + min(s["d"] * 0.6, 1.0)))
        marcas += [("98_cierre_a", T_FIN + 1.5), ("99_cierre", T_FIN + 5.5)]
        dest = OUT / "prueba_v2"
        dest.mkdir(exist_ok=True)
        for nom, tt in marcas:
            Image.fromarray(cuadro(tt)).save(dest / f"{nom}.png")
        print("pruebas en", dest, f"· total {T_TOTAL:.1f}s")
    else:
        render(OUT / "chaco_progreso_puntos_2026_v2.mp4")
