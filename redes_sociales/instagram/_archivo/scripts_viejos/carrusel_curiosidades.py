# -*- coding: utf-8 -*-
"""
Carrusel de CURIOSIDADES (post "de relleno", tono liviano) para @chacoforever.stats.

No es análisis pesado: son datos sueltos que sorprenden y se comparten, para
mantener la cuenta viva entre el post-partido y la previa. Todos los números
salen del informe de temporada (corte fecha 18/18):
  outputs/temporadas/2026/informes/informe_temporada_fecha_18.md

    python scripts/carrusel_curiosidades.py
"""
from pathlib import Path
import placas as P
import marca as M

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "placas" / "curiosidades_mitad_temporada"
NOTA = "Primera mitad 2026 · 18 fechas · SofaScore"


def construir():
    slides = []

    # 01 — Portada (hook liviano)
    slides.append(P.portada(
        "¿Sabías\nque...?",
        "4 datos curiosos del Negro en la primera mitad de la temporada. Nada "
        "de análisis pesado: para compartir y etiquetar. Deslizá →",
        etiqueta="Curiosidades 2026",
        nota="SofaScore"))

    # 02 — Rey de su casa
    slides.append(P.dato(
        "75%", "de sus puntos los sacó de local",
        "9 de sus 12 puntos los hizo en el Gigante. Cuando juega en casa, es otro equipo.",
        kicker="CURIOSIDAD 1", nota=NOTA))

    # 03 — Su mejor cuarto de hora
    slides.append(P.dato(
        "60'-75'", "su mejor cuarto de hora",
        "En esa franja metió 4 goles y recibió solo 1. Cuando entran los cambios, "
        "el Negro aparece.",
        kicker="CURIOSIDAD 2", nota=NOTA))

    # 04 — El más frío
    slides.append(P.dato(
        "4", "goles de Marinucci cuando se esperaban 2.5",
        "Es el goleador del equipo y el más eficiente: convierte por encima de lo "
        "que dicen sus chances (xG).",
        kicker="CURIOSIDAD 3", nota=NOTA))

    # 05 — Vive en el área
    slides.append(P.dato(
        "130", "toques de Pacheco dentro del área rival",
        "Nadie pisa tanto el área como él: el 64% de sus toques son en el último "
        "tercio de la cancha.",
        kicker="CURIOSIDAD 4", nota=NOTA))

    # 06 — Cierre liviano
    slides.append(P.cita(
        "Manda de local, golpea con los cambios y tiene un killer que rinde de más. "
        "Materia prima para la segunda mitad hay.",
        autor="Datos sueltos", nota=NOTA))

    return slides


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    imgs = construir()
    for i, img in enumerate(imgs, 1):
        M.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")

    from PIL import Image
    files = sorted(SALIDA.glob("[0-9]*.png"))
    th = [Image.open(f).convert("RGB").resize((300, 300)) for f in files]
    cols = 3
    rows = (len(th) + cols - 1) // cols
    s = Image.new("RGB", (cols * 300 + (cols + 1) * 10, rows * 300 + (rows + 1) * 10), (45, 45, 45))
    for i, t in enumerate(th):
        r, c = divmod(i, cols)
        s.paste(t, (10 + c * 310, 10 + r * 310))
    s.save(SALIDA / "_preview.png")
    print("OK _preview.png ->", SALIDA)


if __name__ == "__main__":
    main()
