# -*- coding: utf-8 -*-
"""
Gráfico de cancha: el 11 que más usó Cravero en sus 10 fechas, ubicado con la
posición promedio real (SofaScore average_positions) y etiquetado con el nombre
y el número de camiseta que más usó cada uno.

Cancha HORIZONTAL (ataca hacia la derecha). Genera dos temas:
  assets/cravero_once.png         fondo blanco  -> carrusel_cravero_riesgo.py
  assets/cravero_once_papel.png   fondo papel   -> carrusel_cravero.py (estilo diario)

    python scripts/graficos_cravero_marca.py

Números (scratchpad xi_pos.py, sobre los 10 partidos de Cravero):
- Titularidades: los 10 de campo tienen 8-10; el arco lo repartió Canuto (6) y
  Caprio (4). Se muestra a Caprio: le ganó el puesto y viene de 4 vallas
  invictas al hilo.
- Coordenadas afinadas a un 4-4-2 legible a partir del promedio real de
  average_positions (la fecha 25, sin datos de SofaScore, queda afuera).
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from mplsoccer import VerticalPitch

RAIZ = Path(__file__).resolve().parents[1]
ASSETS = RAIZ / "assets"

# tema: (fondo, tinta de las fichas, borde de la ficha, líneas de la cancha)
TEMAS = {
    "blanco": dict(bg="#FAFAF8", tinta="#0F0F0F", borde="#C41E1E",
                   lineas="#B9B8B3", num="#FAFAF8"),
    "papel":  dict(bg="#F4F1E9", tinta="#16140F", borde="#962A22",
                   lineas="#BEB8AA", num="#F4F1E9"),
}

for p in ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/seguibl.ttf",
          "C:/Windows/Fonts/segoeui.ttf"):
    try:
        font_manager.fontManager.addfont(p)
    except Exception:
        pass
plt.rcParams["font.family"] = "Segoe UI"

# nombre, dorsal, x (largo 0-100, ataca hacia arriba), y (ancho 0-100),
# lado etiqueta (-1 = hacia el arco propio / +1 = hacia adelante)
ONCE = [
    ("Caprio",        1, 11, 50, -1),
    ("Ojeda",         3, 34, 14, -1),
    ("Garay",         6, 31, 39, -1),
    ("Valdez",        2, 32, 62, -1),
    ("Luque",         4, 34, 86, -1),
    ("L. Fernández", 10, 56, 16, -1),
    ("Carrizo",       7, 47, 60, -1),
    ("Nievas",        5, 56, 42, -1),
    ("Gaggi",         8, 55, 85, -1),
    ("Romero",        9, 72, 40, -1),
    ("Pacheco",      11, 72, 61, -1),
]


def generar(tema="blanco", salida=None):
    t = TEMAS[tema]
    pitch = VerticalPitch(pitch_type="opta", pitch_color=t["bg"],
                          line_color=t["lineas"], linewidth=2, pad_left=1,
                          pad_right=1, pad_top=2, pad_bottom=1)
    fig, ax = pitch.draw(figsize=(10.0, 7.2))
    fig.set_facecolor(t["bg"])
    # rompe el aspecto cuadrado forzado por mplsoccer y recorta el tercio de
    # ataque vacío: la cancha llena el ancho de la placa (leve estiramiento,
    # aceptable en un pizarrón de formación)
    ax.set_aspect("auto")
    ax.set_xlim(-4, 104)
    ax.set_ylim(-5, 82)

    for nombre, dorsal, x, y, lado in ONCE:
        pitch.scatter(x, y, s=1450, color=t["tinta"], edgecolors=t["borde"],
                      linewidth=2.4, zorder=5, ax=ax)
        pitch.annotate(str(dorsal), (x, y), color=t["num"], va="center",
                       ha="center", fontsize=17, fontweight="bold", zorder=6, ax=ax)
        pitch.annotate(nombre, (x + lado * 5.4, y), color=t["tinta"], va="center",
                       ha="center", fontsize=15, fontweight="bold", zorder=6,
                       ax=ax,
                       bbox=dict(boxstyle="round,pad=0.3", fc=t["bg"],
                                 ec=t["lineas"], lw=1))

    ASSETS.mkdir(parents=True, exist_ok=True)
    out = Path(salida) if salida else ASSETS / (
        "cravero_once.png" if tema == "blanco" else f"cravero_once_{tema}.png")
    fig.savefig(out, dpi=175, bbox_inches="tight", facecolor=t["bg"])
    plt.close(fig)
    print("OK ->", out)
    return out


if __name__ == "__main__":
    generar("blanco")
    generar("papel")
