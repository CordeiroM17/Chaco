# -*- coding: utf-8 -*-
"""
PORTADAS de ejemplo para el post de Cravero, usando su foto.

Genera varias tapas 1080x1080 con la misma foto (assets/Daniel_Cravero.jpg,
1260x706, Cravero centrado con la campera del club en el entrenamiento) y el
texto acomodado a la imagen en cada una. Es solo para elegir: no arma el
carrusel.

    python scripts/portadas_cravero.py   ->  placas/cravero_portadas/

Foto: entrenamiento de junio 2026, tomada de EcoDeportivo
(ecodeportivo.com.ar/img/2026/06/cravero-for-ever-1.jpg). Tiene marca de agua
"ECO DEPORTIVO" abajo a la derecha -> todas las tapas la tapan con un degradado
o la recortan.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter

RAIZ = Path(__file__).resolve().parents[1]
FOTO = RAIZ / "assets" / "Daniel_Cravero.jpg"
FOTO_PAPEL = RAIZ / "assets" / "Cravero_Macius.png"   # Cravero color + borde, fondo sepia
FOTO_BN = RAIZ / "assets" / "cravero_destacado_riesgo.png"     # idem, fondo B/N
SALIDA = RAIZ / "placas" / "cravero_portadas"
W = H = 1080
FN = "C:/Windows/Fonts"
HANDLE = "@chacoforever.stats"

# paletas de las tres identidades de la cuenta
PAPEL, TINTA_D, ACENTO_D = (244, 241, 233), (22, 20, 15), (150, 42, 34)
BLANCO_R, NEGRO_R, ROJO_R = (250, 250, 248), (15, 15, 15), (196, 30, 30)
NEGRO_M, DORADO_M, TINTA_M = (14, 14, 14), (232, 178, 58), (245, 245, 245)

_c = {}
def F(path, size):
    k = (path, size)
    if k not in _c:
        _c[k] = ImageFont.truetype(path, size)
    return _c[k]

GEO   = f"{FN}/georgia.ttf"
GEO_B = f"{FN}/georgiab.ttf"
GEO_I = f"{FN}/georgiai.ttf"
SEG_BL = f"{FN}/seguibl.ttf"
SEG_B  = f"{FN}/segoeuib.ttf"
SEG_SB = f"{FN}/seguisb.ttf"
SEG_R  = f"{FN}/segoeui.ttf"
BAHN   = f"{FN}/bahnschrift.ttf"


# ---------------------------------------------------------------- utilidades
def crop_to(img, bw, bh, fx=0.5, fy=0.5, zoom=1.0):
    """Recorta `img` al aspecto bw:bh centrando en la fracción (fx, fy) y la
    devuelve escalada a (bw, bh). `zoom>1` recorta más chico (acerca)."""
    iw, ih = img.size
    target = bw / bh
    if iw / ih > target:                     # sobra ancho
        nw = int(ih * target); nh = ih
    else:                                    # sobra alto
        nw = iw; nh = int(iw / target)
    nw = int(nw / zoom); nh = int(nh / zoom)
    x = int((iw - nw) * fx); y = int((ih - nh) * fy)
    x = max(0, min(x, iw - nw)); y = max(0, min(y, ih - nh))
    return img.crop((x, y, x + nw, y + nh)).resize((bw, bh), Image.LANCZOS)


def duotone(img, dark, light):
    g = ImageOps.grayscale(ImageOps.autocontrast(img, cutoff=1))
    return ImageOps.colorize(g, black=dark, white=light, mid=None)


def vgrad(size, color, top_a, bot_a):
    """Degradado vertical de `color` con alpha de top_a (arriba) a bot_a."""
    w, h = size
    base = Image.new("RGBA", size, (0, 0, 0, 0))
    px = base.load()
    for yy in range(h):
        a = int(top_a + (bot_a - top_a) * yy / (h - 1))
        for xx in range(w):
            px[xx, yy] = (color[0], color[1], color[2], a)
    return base


def hgrad(size, color, left_a, right_a):
    w, h = size
    base = Image.new("RGBA", size, (0, 0, 0, 0))
    px = base.load()
    for xx in range(w):
        a = int(left_a + (right_a - left_a) * xx / (w - 1))
        for yy in range(h):
            px[xx, yy] = (color[0], color[1], color[2], a)
    return base


def cinta_peligro(d, y0, y1, raya=22, paso=44, color=(15, 15, 15)):
    alto = y1 - y0
    x = -alto
    while x < W + alto:
        d.polygon([(x, y1), (x + raya, y1),
                   (x + raya + alto, y0), (x + alto, y0)], fill=color)
        x += paso


def text_tracking(d, xy, s, font, fill, tracking=0, anchor_h="l"):
    total = sum(d.textbbox((0, 0), c, font=font)[2] for c in s) + tracking * (len(s) - 1)
    x, y = xy
    if anchor_h == "m":
        x -= total / 2
    elif anchor_h == "r":
        x -= total
    for c in s:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textbbox((0, 0), c, font=font)[2] + tracking
    return total


def guardar(img, n):
    SALIDA.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(SALIDA / n, "PNG")
    print("OK", n)


# ============================================================= LAS PORTADAS
def portada_diario():
    """Recorte de diario: foto duotono papel/tinta en la mitad de abajo, texto
    en la banda de papel de arriba."""
    img = Image.new("RGB", (W, H), PAPEL)
    d = ImageDraw.Draw(img)
    corte = 430
    # foto con Cravero resaltado (color + borde), fondo sepia
    foto = crop_to(Image.open(FOTO_PAPEL).convert("RGB"), W, H - corte,
                   fx=0.46, fy=0.20, zoom=1.06)
    img.paste(foto, (0, corte))
    d.rectangle([64, corte - 2, W - 64, corte + 3], fill=TINTA_D)

    d.rectangle([64, 92, 64 + 150, 96], fill=TINTA_D)
    text_tracking(d, (64, 116), 'DANIEL "EL CHANGO" CRAVERO', F(GEO_B, 24), ACENTO_D, tracking=6)
    d.text((60, 158), 'El salvavidas', font=F(GEO_B, 110), fill=TINTA_D)
    d.text((60, 274), "de For ever", font=F(GEO_B, 110), fill=TINTA_D)
    # handle sobre la foto, en un chip de papel
    tag = "  " + HANDLE + "  "
    tw = d.textbbox((0, 0), tag, font=F(GEO_I, 22))[2]
    d.rectangle([64, H - 72, 64 + tw, H - 32], fill=PAPEL)
    d.text((64, H - 68), tag, font=F(GEO_I, 22), fill=TINTA_D)
    return img


def portada_riesgo():
    """Full-bleed, cinta de peligro, título abajo a la izquierda con una
    palabra en rojo."""
    foto = crop_to(Image.open(FOTO_BN).convert("RGB"), W, H, fx=0.52, fy=0.24, zoom=1.03)
    img = foto
    ov = vgrad((W, H), (12, 12, 12), 0, 215)
    img.paste(ov, (0, 0), ov)
    d = ImageDraw.Draw(img)
    cinta_peligro(d, 0, 20)
    cinta_peligro(d, H - 20, H)

    y = H - 336
    text_tracking(d, (72, y), "EL EFECTO CRAVERO", F(SEG_B, 24), ROJO_R, tracking=3)
    y += 52
    d.text((68, y), "DE LA ", font=F(SEG_BL, 84), fill=BLANCO_R)
    wsd = d.textbbox((0, 0), "DE LA ", font=F(SEG_BL, 84))[2]
    d.text((68 + wsd, y), "ZONA ROJA", font=F(SEG_BL, 84), fill=ROJO_R)
    y += 94
    d.text((68, y), "AL RESPIRO", font=F(SEG_BL, 84), fill=BLANCO_R)
    d.text((72, H - 58), HANDLE, font=F(SEG_SB, 23), fill=(225, 225, 225))
    return img


def portada_marca():
    """Identidad negra/dorada: foto en blanco y negro, degradado negro, acento
    dorado y el apellido gigante en condensada."""
    foto = crop_to(Image.open(FOTO_BN).convert("RGB"), W, H, fx=0.55, fy=0.22, zoom=1.03)
    img = foto
    img.paste(vgrad((W, H), NEGRO_M, 30, 240), (0, 0), vgrad((W, H), NEGRO_M, 30, 240))
    img.paste(hgrad((W, H), NEGRO_M, 150, 0), (0, 0), hgrad((W, H), NEGRO_M, 150, 0))
    d = ImageDraw.Draw(img)
    # rayas del club arriba
    for i in range(6):
        x0 = 84 + i * 26
        d.rectangle([x0, 74, x0 + 12, 110], fill=BLANCO_R if i % 2 else DORADO_M)
    text_tracking(d, (84, 128), "ESTADÍSTICAS DEL NEGRO", F(SEG_SB, 18),
                  (170, 170, 170), tracking=3)

    d.text((78, H - 348), "EL HOMBRE DEL ÚLTIMO ASCENSO,",
           font=F(SEG_B, 27), fill=DORADO_M)
    d.text((78, H - 312), "DE NUEVO EN CASA", font=F(SEG_B, 27), fill=DORADO_M)
    d.text((72, H - 268), "CRAVERO", font=F(BAHN, 150), fill=TINTA_M)
    d.rectangle([84, H - 96, 84 + 120, H - 90], fill=DORADO_M)
    d.text((84, H - 78), HANDLE, font=F(SEG_SB, 23), fill=(235, 235, 235))
    return img


def portada_split():
    """Bloque de papel a la izquierda con el título, foto a la derecha."""
    img = Image.new("RGB", (W, H), PAPEL)
    panel = 556
    foto = crop_to(Image.open(FOTO_PAPEL).convert("RGB"), W - panel, H, fx=0.60, fy=0.20, zoom=1.02)
    img.paste(foto, (panel, 0))
    ov = hgrad((150, H), PAPEL, 255, 0)
    img.paste(ov, (panel, 0), ov)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, panel, H], fill=PAPEL)

    mx = 60
    lineas = ["De", "ídolo", "a", "salvavidas"]
    fnt = F(GEO_B, 86)
    while max(d.textbbox((0, 0), s, font=fnt)[2] for s in lineas) > panel - mx - 24 and fnt.size > 50:
        fnt = F(GEO_B, fnt.size - 3)
    d.rectangle([mx + 4, 168, mx + 4 + 130, 172], fill=TINTA_D)
    text_tracking(d, (mx + 4, 194), "EL CHANGO", F(GEO_B, 23), ACENTO_D, tracking=5)
    y = 250
    for ln in lineas:
        d.text((mx, y), ln, font=fnt, fill=TINTA_D)
        y += int(fnt.size * 1.06)
    d.text((mx + 4, y + 22), "20 puntos de 30 en diez\nfechas con Cravero",
           font=F(GEO_I, 26), fill=(110, 103, 91), spacing=8)
    d.text((mx + 4, H - 84), HANDLE, font=F(GEO_I, 22), fill=TINTA_D)
    return img


def portada_retrato():
    """Foto casi entera, franja inferior sólida con el texto (no tapa la cara)."""
    banda = 300
    foto = crop_to(Image.open(FOTO_BN).convert("RGB"), W, H - banda + 40, fx=0.46, fy=0.20, zoom=1.05)
    img = Image.new("RGB", (W, H), NEGRO_R)
    img.paste(foto, (0, 0))
    d = ImageDraw.Draw(img)
    img.paste(vgrad((W, 240), (15, 15, 15), 0, 255), (0, H - banda - 200),
              vgrad((W, 240), (15, 15, 15), 0, 255))
    d.rectangle([0, H - banda, W, H], fill=NEGRO_R)
    cinta_peligro(d, H - banda - 12, H - banda + 8)

    text_tracking(d, (W / 2, H - banda + 46), "PRIMERA NACIONAL 2026",
                  F(SEG_B, 20), ROJO_R, tracking=3, anchor_h="m")
    d.text((W / 2, H - banda + 92), "El giro de Cravero", font=F(SEG_BL, 66),
           fill=BLANCO_R, anchor="ma")
    d.text((W / 2, H - banda + 176),
           "De último en el Grupo A a cuatro puntos del respiro",
           font=F(SEG_R, 24), fill=(210, 210, 210), anchor="ma")
    d.text((W / 2, H - 54), HANDLE, font=F(SEG_SB, 22), fill=(235, 235, 235),
           anchor="ma")
    return img


def main():
    guardar(portada_diario(),  "01_diario.png")
    guardar(portada_riesgo(),  "02_riesgo.png")
    guardar(portada_marca(),   "03_marca.png")
    guardar(portada_split(),   "04_split.png")
    guardar(portada_retrato(), "05_retrato.png")

    # contact sheet
    files = sorted(SALIDA.glob("0*.png"))
    lado = 360
    s = Image.new("RGB", (3 * lado + 40, 2 * lado + 30), (40, 40, 40))
    for i, f in enumerate(files):
        t = Image.open(f).resize((lado, lado))
        r, c = divmod(i, 3)
        s.paste(t, (10 + c * (lado + 10), 10 + r * (lado + 10)))
    s.save(SALIDA / "_preview.png")
    print("OK _preview.png")


if __name__ == "__main__":
    main()
