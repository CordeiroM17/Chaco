# -*- coding: utf-8 -*-
"""
Regenera los gráficos del pipeline que van al carrusel, pero en la paleta de la
marca (fondo negro + dorado) para que se fundan con la placa en vez de quedar
como una tarjeta blanca que choca.

NO toca el pipeline: sobrescribe en caliente las constantes de color del módulo
src.visualization.season y llama a las MISMAS funciones con los datos reales.
Salida en assets/ para que el carrusel las use.

    python scripts/graficos_marca.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PROYECTO = RAIZ.parents[1]
sys.path.insert(0, str(PROYECTO))

ASSETS = RAIZ / "assets"

# --- paleta de la marca (igual que marca.py) ---
NEGRO = "#0E0E0E"
TINTA = "#F5F5F5"
DORADO = "#E8B23A"
LADRILLO = "#C0473F"   # rojo apagado para "en contra" (se distingue del dorado)
GRIS = "#9A9A9A"
GRILLA = "#2E2E2E"

import matplotlib as mpl
mpl.use("Agg")
mpl.rcParams.update({
    "text.color": TINTA, "axes.labelcolor": TINTA,
    "xtick.color": "#CCCCCC", "ytick.color": "#CCCCCC",
    "axes.edgecolor": GRILLA, "figure.facecolor": NEGRO, "axes.facecolor": NEGRO,
})

import src.visualization.season as vs
from src.analysis.season import build_season_table, goals_by_time_window
import config

# sobrescribir las constantes de color del modulo de graficos
vs.BG_COLOR = NEGRO
vs.TEXT_COLOR = TINTA
vs.ACCENT_COLOR = DORADO     # Chaco / "a favor"
vs.RIVAL_COLOR = LADRILLO    # rival / "en contra"
vs.MUTED_COLOR = GRIS
vs.GRID_COLOR = GRILLA


def _match_keys(base_dir):
    """Carpetas de partido con datos, en orden cronológico (nombre = fecha_...)."""
    base = Path(base_dir)
    keys = [p.name for p in base.iterdir()
            if p.is_dir() and (p / "incidents_clean.csv").exists()]
    return sorted(keys)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    season = 2026
    base_dir = config.season_data_dir(season)
    mks = _match_keys(base_dir)
    print(f"{len(mks)} partidos con datos")

    # title=" " suprime el titulo interno del grafico: el titulo lo pone la placa
    season_df = build_season_table(mks, base_dir)
    vs.plot_recent_form(season_df, window=5, season=str(season), title=" ",
                        save_path=str(ASSETS / "forma_reciente_ig.png"))
    print("OK forma_reciente_ig.png")

    win_df = goals_by_time_window(mks, base_dir)
    vs.plot_goals_by_time_window(win_df, season=str(season), title=" ",
                                 save_path=str(ASSETS / "goles_ventana_ig.png"))
    print("OK goles_ventana_ig.png")


if __name__ == "__main__":
    main()
