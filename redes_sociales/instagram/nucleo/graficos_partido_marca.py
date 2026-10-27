# -*- coding: utf-8 -*-
"""
Gráficos de CANCHA de un partido, tematizados con la marca (fondo negro + heat
dorado) para el carrusel de Instagram. Se funden con la placa en vez de entrar
como una tarjeta blanca que choca.

Genera, para un match_key dado:
  - heatmap_figura_ig.png    : mapa de calor de un jugador (la figura)
  - heatmap_rival_ig.png     : mapa de calor del equipo rival (para mostrar cómo
                               se replegó / dónde vivió en la cancha)
  - heatmap_equipo_ig.png    : heatmap comparado, Chaco (oro) y rival (rojo)
                               lado a lado en una sola cancha oscura
  - mapa_asociacion_ig.png   : mapa de asociación de Chaco (posición real +
                               pases reales, mismo cálculo que
                               src/visualization/match.py:plot_pass_association)
                               pero en la paleta oscura

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
from matplotlib.lines import Line2D
from mplsoccer import Pitch, VerticalPitch

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
MATCH_KEY = "2026-10-24_vs_ferro_carril_oeste_a"
SEASON = 2026
FIGURA = "N. Caprio"    # nombre tal cual figura en los heatmaps


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


def heatmap_equipo_comparado(hm, chaco_side, rival_side, save):
    """Heatmap de los DOS equipos lado a lado, una sola cancha oscura partida
    al medio — Chaco en oro (izquierda), rival en rojo (derecha). Version
    oscura de plot_team_heatmap (src/visualization/match.py), para la placa
    'Dónde vivió cada equipo'."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(NEGRO)
    for ax, side, cmap, fallback, label in [
        (axes[0], chaco_side, CMAP_ORO, DORADO, "Chaco For Ever"),
        (axes[1], rival_side, CMAP_ROJO, LADRILLO, "Rival"),
    ]:
        d = hm[hm["team_side"] == side]
        x, y = _xy(d)
        p = _pitch(); p.draw(ax=ax); ax.set_facecolor(NEGRO)
        _heat(ax, p, x, y, cmap, fallback)
        ax.set_title(label, color=TINTA, fontsize=14, fontweight="bold", pad=10)
    plt.tight_layout(pad=0.6)
    fig.savefig(save, dpi=200, facecolor=NEGRO, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("OK", save)


def mapa_asociacion_marca(df_avg_pos, df_lineup, side, save, k_vecinos=3):
    """Mapa de asociación de UN equipo (posición promedio real + volumen de
    pases real, conectando companeros cercanos), version oscura de
    src/visualization/match.py:plot_pass_association para la placa
    'Cómo salimos jugando'. Mismo calculo, otra paleta."""
    df = df_avg_pos[df_avg_pos["team_side"] == side].copy()
    if df.empty:
        print("Sin average_positions para", side)
        return
    df = df.merge(df_lineup[["player_name", "is_starter", "accurate_passes"]],
                  on="player_name", how="left")
    df = df[df["is_starter"] == True].reset_index(drop=True)
    if df.empty:
        print("Sin titulares para", side)
        return
    df["accurate_passes"] = pd.to_numeric(df["accurate_passes"], errors="coerce").fillna(0)

    pos = df[["average_x", "average_y"]].values
    n = len(df)
    dist = np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=2)
    np.fill_diagonal(dist, np.inf)
    edges = set()
    for i in range(n):
        for j in np.argsort(dist[i])[:k_vecinos]:
            edges.add((min(i, int(j)), max(i, int(j))))

    fig, ax = plt.subplots(figsize=(9, 12))
    fig.patch.set_facecolor(NEGRO)
    p = _pitch(); p.draw(ax=ax); ax.set_facecolor(NEGRO)

    # zorder > 2 (line_zorder de _pitch()) para que las conexiones y los nodos
    # queden POR ENCIMA de las líneas de la cancha, no tapados por ellas.
    max_pass = max(df["accurate_passes"].max(), 1)
    for i, j in edges:
        w = np.sqrt(df["accurate_passes"].iloc[i] * df["accurate_passes"].iloc[j]) / max_pass
        p.lines(df["average_x"].iloc[i], df["average_y"].iloc[i],
                df["average_x"].iloc[j], df["average_y"].iloc[j],
                lw=0.8 + w * 5, color=DORADO, alpha=0.30 + w * 0.5, zorder=3, ax=ax)

    sizes = 260 + (df["accurate_passes"] / max_pass) * 700
    p.scatter(df["average_x"], df["average_y"], s=sizes, c=DORADO,
             edgecolors=NEGRO, linewidth=1.6, zorder=4, ax=ax)
    for _, r in df.iterrows():
        short = r["player_name"].split()[-1] if r["player_name"] else ""
        p.annotate(short, (r["average_x"], r["average_y"] + 4.2), ax=ax,
                   color=TINTA, fontsize=9, fontweight="bold",
                   ha="center", va="bottom", zorder=5)

    plt.tight_layout(pad=0.4)
    fig.savefig(save, dpi=200, facecolor=NEGRO, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("OK", save)


_SHOT_PANELS = [("goal", "Goles"), ("save", "Atajadas"),
                ("miss", "Desviados"), ("block", "Bloqueados")]


def shotmap_historia(match_key, season, save):
    """Version oscura y en 2x2 (sin la lista cronologica del costado, muy densa
    para una historia) de plot_shotmap_4grid_match (src/visualization/season.py)
    — pensada para historias de Instagram (se embebe con
    placas.grafico_marca_historia). Chaco siempre dorado, rival siempre este
    rojo apagado (LADRILLO), igual que el resto de esta paleta."""
    data = load_match_data(match_key, season)
    df = data["shotmap"]
    if df is None or df.empty:
        print("Sin shotmap para", match_key)
        return None
    home = is_home_match(match_key)

    d = df.copy()
    d["x_plot"] = 100 - pd.to_numeric(d["coord_x"], errors="coerce")
    d["y_plot"] = 100 - pd.to_numeric(d["coord_y"], errors="coerce")
    d["xg"] = pd.to_numeric(d.get("xg"), errors="coerce").fillna(0)
    d = d.dropna(subset=["x_plot", "y_plot"])

    home_flag = d["isHome"].astype(str).str.lower().isin(["true", "1"])
    base_chaco = home_flag if home else ~home_flag
    if "situation" in d.columns:
        own_goal = d["situation"].astype(str).str.lower().eq("own-goal")
    else:
        own_goal = pd.Series(False, index=d.index)
    d["is_chaco"] = base_chaco ^ own_goal
    d["stype"] = d["shotType"].where(
        d["shotType"].isin([t for t, _ in _SHOT_PANELS]), "miss")

    # Cada media cancha vertical (opta, half=True) sale ANCHA (ancho:alto ≈
    # 2:1, no cuadrada). Un 2x2 clásico queda muy bajo y ancho -> al insertarlo
    # en un lienzo 9:16 sobra muchísimo alto. Apilar las 4 en UNA columna usa
    # el formato vertical de la historia mucho mejor (paneles más grandes,
    # nada de aire de más al pegarlo en placas.grafico_marca_historia).
    fig, axes = plt.subplots(4, 1, figsize=(6.4, 13.4))
    fig.patch.set_facecolor(NEGRO)
    pitch = VerticalPitch(half=True, pitch_type="opta", pitch_color=NEGRO,
                          line_color=PITCH_LINE, linewidth=1.5, pad_bottom=0.5)
    for ax, (s_type, label) in zip(axes.flat, _SHOT_PANELS):
        pitch.draw(ax=ax)
        ax.set_facecolor(NEGRO)
        sub = d[d["stype"] == s_type]
        for _, row in sub.iterrows():
            color = DORADO if row["is_chaco"] else LADRILLO
            size = float(np.clip(row["xg"] * 900 + 240, 240, 1100))
            pitch.scatter(row["x_plot"], row["y_plot"], s=size, c=color,
                          edgecolor=NEGRO, linewidth=1.2, alpha=0.92,
                          ax=ax, zorder=2)
        ax.set_title(f"{label}  ({len(sub)})", fontsize=18, color=TINTA,
                     fontweight="bold", pad=10)

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", label="Chaco For Ever",
              markerfacecolor=DORADO, markersize=15),
        Line2D([0], [0], marker="o", color="none", label="Rival",
              markerfacecolor=LADRILLO, markersize=15),
    ]
    leg = fig.legend(handles=legend_handles, loc="lower center", ncol=2,
                     fontsize=15, frameon=False, bbox_to_anchor=(0.5, 0.0))
    for txt in leg.get_texts():
        txt.set_color(TINTA)
    fig.text(0.5, 0.978, "Tamaño del punto ∝ xG", ha="center", fontsize=13,
             color="#9a9a9a", style="italic")
    plt.tight_layout(rect=(0, 0.028, 1, 0.955), h_pad=1.6)
    fig.savefig(save, dpi=200, facecolor=NEGRO, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("OK", save)
    return save


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
    heatmap_equipo_comparado(hm, chaco_side, rival_side, ASSETS / "heatmap_equipo_ig.png")

    df_avg = data.get("avg_positions")
    df_lin = data.get("lineups")
    if df_avg is not None and not df_avg.empty and df_lin is not None and not df_lin.empty:
        mapa_asociacion_marca(df_avg, df_lin, chaco_side, ASSETS / "mapa_asociacion_ig.png")
    else:
        print("Sin average_positions/lineups — se salta mapa_asociacion_ig.png")


if __name__ == "__main__":
    main()
