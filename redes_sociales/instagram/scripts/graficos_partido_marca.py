# -*- coding: utf-8 -*-
"""
Gráficos de CANCHA de un partido, tematizados con la marca (fondo negro + heat
dorado) para el carrusel de Instagram. Se funden con la placa en vez de entrar
como una tarjeta blanca que choca.

Genera, para un match_key dado:
  - heatmap_figura_ig.png  : mapa de calor de un jugador (la figura)
  - heatmap_rival_ig.png   : mapa de calor del equipo rival (para mostrar cómo
                             se replegó / dónde vivió en la cancha)

No toca el pipeline: usa load_match_data y dibuja con mplsoccer en la paleta de
la marca. Reutilizable: cambiás MATCH_KEY y FIGURA y listo.

    python scripts/graficos_partido_marca.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch

RAIZ = Path(__file__).resolve().parents[1]
PROYECTO = RAIZ.parents[1]
sys.path.insert(0, str(PROYECTO))
ASSETS = RAIZ / "assets" / "partido"

from src.analysis.post_match import load_match_data
from src.analysis.season import is_home_match

# --- paleta de la marca ---
NEGRO = "#0E0E0E"
PITCH_LINE = "#3A3A3A"
TINTA = "#F5F5F5"
DORADO = "#E8B23A"
LADRILLO = "#C0473F"

# heat en dorado sobre negro (Chaco) y en rojo apagado (rival)
CMAP_ORO = LinearSegmentedColormap.from_list(
    "oro", ["#0E0E0E", "#5A4415", "#B7822A", "#E8B23A", "#F7E7B0"])
CMAP_ROJO = LinearSegmentedColormap.from_list(
    "rojo", ["#0E0E0E", "#4A1E1B", "#8E322C", "#C0473F", "#E8A59F"])

# ==========================================================================
#  QUÉ GENERAR — lo único que cambiás por partido
# ==========================================================================
MATCH_KEY = "2026-07-11_vs_san_telmo_a"
SEASON = 2026
FIGURA = "M. S. Romero"          # nombre tal cual figura en los heatmaps


def _pitch():
    return Pitch(pitch_type="opta", pitch_color=NEGRO, line_color=PITCH_LINE,
                 linewidth=1.4, line_zorder=2)


def _heat(ax, pitch, x, y, cmap, fallback):
    if len(x) == 0:
        return
    try:
        pitch.kdeplot(x, y, ax=ax, cmap=cmap, fill=True, levels=14,
                      alpha=0.92, thresh=0.05, zorder=1)
    except Exception:
        pitch.scatter(x, y, s=16, c=fallback, alpha=0.5, ax=ax, zorder=1)


def _xy(df):
    x = pd.to_numeric(df["x"], errors="coerce")
    y = pd.to_numeric(df["y"], errors="coerce")
    ok = x.notna() & y.notna()
    return x[ok].values, y[ok].values


def heatmap_jugador(hm, side, player, save):
    d = hm[(hm["team_side"] == side) & (hm["player_name"] == player)]
    x, y = _xy(d)
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor(NEGRO)
    p = _pitch(); p.draw(ax=ax); ax.set_facecolor(NEGRO)
    _heat(ax, p, x, y, CMAP_ORO, DORADO)
    plt.tight_layout(pad=0.4)
    fig.savefig(save, dpi=200, facecolor=NEGRO, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("OK", save)


def heatmap_equipo(hm, side, save, cmap=CMAP_ROJO, fallback=LADRILLO):
    d = hm[hm["team_side"] == side]
    x, y = _xy(d)
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor(NEGRO)
    p = _pitch(); p.draw(ax=ax); ax.set_facecolor(NEGRO)
    _heat(ax, p, x, y, cmap, fallback)
    plt.tight_layout(pad=0.4)
    fig.savefig(save, dpi=200, facecolor=NEGRO, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("OK", save)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    data = load_match_data(MATCH_KEY, SEASON)
    hm = data["heatmaps"]
    if hm is None or hm.empty:
        raise SystemExit("Sin heatmaps para " + MATCH_KEY)
    home = is_home_match(MATCH_KEY)
    chaco_side = "home" if home else "away"
    rival_side = "away" if home else "home"

    heatmap_jugador(hm, chaco_side, FIGURA, ASSETS / "heatmap_figura_ig.png")
    heatmap_equipo(hm, rival_side, ASSETS / "heatmap_rival_ig.png")


if __name__ == "__main__":
    main()
