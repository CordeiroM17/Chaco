# -*- coding: utf-8 -*-
"""
Carrusel: "Vuelve Matías Romero" — el goleador del Negro en 2025 está de vuelta.

Números autoritativos del pipeline (temporada 2025 de Chaco For Ever):
  season_player_stats + assists_network sobre data/temporadas/2025.
  Matías Sebastián Romero (short 'M. S. Romero'):
    32 PJ (29 titular), 2404 min, 9 goles, 2 asist, rating 6.95,
    49 tiros (20 al arco), xG 6.70, 1 gol de penal. Goleador del equipo (2° hizo 3).
    Lo asistieron 8 jugadores distintos; él asistió a Valenzuela y Úbeda.

La placa principal (01) deja un espacio reservado para la foto.

    python scripts/carrusel_vuelve_romero.py
"""
from pathlib import Path
import placas as P
import marca as M

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "placas" / "vuelve_matias_romero"
NOTA = "Temporada 2025 · Chaco For Ever · SofaScore"


def construir():
    slides = []

    # 01 — Portada con espacio para la foto (a editar por el usuario)
    slides.append(P.portada_jugador(
        "Matías Romero",
        etiqueta="Vuelve al Negro",
        subtitulo="El goleador de For Ever en 2025 está de vuelta.",
        teaser="9 goles la última temporada",
        nota="SofaScore"))

    # 02 — El goleador
    slides.append(P.dato(
        "9", "goles: fue el goleador del Negro en 2025",
        "Casi el triple que el segundo artillero del equipo (3). Nadie hizo más goles con la camiseta de For Ever.",
        kicker="EL GOLEADOR", nota=NOTA))

    # 03 — Su 2025 en números
    slides.append(P.ficha(
        "Su 2025 en números",
        "Chaco For Ever · Primera Nacional",
        [("Partidos (de titular)", "32 (29)"),
         ("Minutos", "2404"),
         ("Goles", "9"),
         ("Asistencias", "2"),
         ("Rating promedio", "6.95"),
         ("Tiros (al arco)", "49 (20)"),
         ("xG (goles esperados)", "6.70")],
        nota=NOTA, destacar="Goles"))

    # 04 — Definidor: convirtió por encima de su xG
    slides.append(P.dato_vs(
        "+2.3", "goles por encima de lo esperado",
        col_izq=("Goles", "9", "lo que marcó"),
        col_der=("xG", "6.7", "lo esperado"),
        kicker="DEFINIDOR",
        franja="Convierte más de lo que la chance dice",
        nota=NOTA))

    # 05 — Sus sociedades (red de nodos, estilo red_asistencias)
    slides.append(P.red_sociedades(
        "Romero", "9 goles",
        nodos=[
            {"nombre": "Marinucci", "in": True},
            {"nombre": "Luque", "in": True},
            {"nombre": "Valenzuela", "in": True, "out": True},
            {"nombre": "Enríquez", "in": True},
            {"nombre": "Obregón", "in": True},
            {"nombre": "Chaves", "in": True},
            {"nombre": "Seratto", "in": True},
            {"nombre": "Perinciolo", "in": True},
            {"nombre": "Úbeda", "out": True},
        ],
        titulo="Sus sociedades",
        subtitulo="Temporada 2025 · la flecha va del asistente al goleador",
        destacados=["Luque", "Enríquez", "Valenzuela"],
        leyenda="En dorado: siguen en el plantel 2026",
        nota=NOTA, kicker="SOCIEDADES · 2025"))

    # 06 — Bienvenida (cierre)
    slides.append(P.portada(
        "Bienvenido,\nMatías",
        "El Negro recupera a su goleador para la segunda mitad de la temporada. Jerarquía y gol de arranque.",
        etiqueta="Temporada 2026",
        nota="SofaScore"))

    return slides


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    imgs = construir()
    for i, img in enumerate(imgs, 1):
        M.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    # preview
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
    print("OK _preview.png")


if __name__ == "__main__":
    main()
