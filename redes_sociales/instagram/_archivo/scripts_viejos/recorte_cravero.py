# -*- coding: utf-8 -*-
"""
Resalta a Cravero (la persona del medio) en assets/Daniel_Cravero.jpg: su
figura queda EN COLOR y el resto de la foto va en blanco y negro (o sepia),
apagado y desenfocado. Sin borde: el contraste color / gris hace el trabajo.

La silueta es un polígono trazado a mano sobre la foto (1260x706) — más
confiable que segmentar, porque los ayudantes están pegados a él. Si la foto
cambia hay que reajustar `SILUETA`.

También tapa la marca de agua "ECO DEPORTIVO" de la esquina inferior derecha.

Genera en assets/:
  cravero_destacado_riesgo.png   fondo B/N apagado + Cravero color
  cravero_destacado_papel.png    idem con fondo sepia (para el estilo diario)
  Daniel_Cravero_recorte.png     RGBA: solo Cravero, transparente

    python scripts/recorte_cravero.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance

RAIZ = Path(__file__).resolve().parents[1]
FOTO = RAIZ / "assets" / "Daniel_Cravero.jpg"
ASSETS = RAIZ / "assets"

# polígono de la silueta de Cravero en coordenadas de la foto original (1260x706),
# en sentido horario desde la coronilla. La zona de la cabeza/pelo está trazada
# fina para que el corte quede limpio en el nacimiento del pelo.
SILUETA = [
    # coronilla — trazado fino pegado al nacimiento del pelo (arriba a la
    # derecha está la estructura clara del fondo: no pasarse ni 5 px)
    (538, 100), (550, 90), (562, 83), (576, 79), (590, 78), (604, 81),
    (618, 87), (632, 96), (645, 108), (658, 122),
    # lado derecho: pelo y después el pómulo iluminado (va MÁS afuera, la cara
    # llega hasta ~x748) y vuelve a entrar en la mandíbula/barba
    (672, 138), (690, 152), (708, 168), (726, 184), (742, 202),
    (748, 226), (742, 256), (728, 286), (714, 314), (704, 342), (702, 366),
    # hombro / campera lado derecho bajando
    (722, 396), (744, 448), (752, 536), (744, 646), (738, 706),
    # base
    (430, 706),
    # campera lado izquierdo subiendo
    (418, 620), (414, 520), (420, 452), (438, 380), (458, 358),
    # pelo largo del lado izquierdo — MÁS ADENTRO (antes agarraba al ayudante
    # borroso de atrás); el pelo de Cravero arranca en ~x490
    (470, 344), (482, 308), (492, 272), (494, 236), (492, 200),
    (492, 172), (498, 146), (508, 124), (522, 108),
]

# rectángulo (con margen) donde está la marca de agua, sobre la foto original
MARCA_AGUA = (858, 470, 1260, 706)


def _mascara(size):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(SILUETA, fill=255)
    return m


def _tapar_marca(base):
    """Oscurece a negro la esquina de la marca de agua, con un degradado suave
    para que se funda con el fondo (ya oscuro)."""
    x0, y0, x1, y1 = MARCA_AGUA
    capa = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rectangle([x0, y0, x1, y1], fill=(8, 8, 8, 255))
    capa = capa.filter(ImageFilter.GaussianBlur(40))
    return Image.alpha_composite(base.convert("RGBA"), capa).convert("RGB")


def _fondo(src, modo):
    g = ImageOps.grayscale(src)
    if modo == "sepia":
        base = ImageOps.colorize(ImageOps.autocontrast(g, 1), black=(30, 24, 18),
                                 white=(232, 226, 214))
    else:
        base = g.convert("RGB")
    base = ImageEnhance.Brightness(base).enhance(0.6)
    base = ImageEnhance.Contrast(base).enhance(1.06)
    base = base.filter(ImageFilter.GaussianBlur(2.6))
    return _tapar_marca(base)


def _cravero_color(src):
    c = ImageEnhance.Color(src).enhance(1.45)
    c = ImageEnhance.Contrast(c).enhance(1.07)
    c = ImageEnhance.Brightness(c).enhance(1.04)
    return c


def generar():
    src = Image.open(FOTO).convert("RGB")
    # erosiona ~2 px: el borde queda por dentro de la silueta, así cualquier
    # imprecisión se come un pelo en vez de mostrar fondo
    mask = _mascara(src.size).filter(ImageFilter.MinFilter(5))
    mask = mask.filter(ImageFilter.GaussianBlur(1.0))
    cravero = _cravero_color(src)

    for modo, nombre in (("bn", "cravero_destacado_riesgo.png"),
                         ("sepia", "cravero_destacado_papel.png")):
        out = _fondo(src, modo)
        out.paste(cravero, (0, 0), mask)
        out.save(ASSETS / nombre)
        print("OK", nombre)

    rec = cravero.convert("RGBA")
    rec.putalpha(mask)
    rec.save(ASSETS / "Daniel_Cravero_recorte.png")
    print("OK Daniel_Cravero_recorte.png")


if __name__ == "__main__":
    generar()
