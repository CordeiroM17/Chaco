"""Visualizaciones para el análisis global del Grupo A: rankings de barras por
equipo, mejor 11 de la fecha en cancha y origen de los remates. Mismo tema claro
que el resto del proyecto."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.visualization.season import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, RIVAL_COLOR, MUTED_COLOR, GRID_COLOR,
    _fig_style, save_fig, light_pitch,
)

POS_COLOR = {"G": "#e8a200", "D": "#2b3a67", "M": "#6b7db3", "F": "#d62728"}

# Nombres cortos de club para que las etiquetas no se pisen.
SHORT_NAMES = {
    "Chaco For Ever": "Chaco", "Acassuso": "Acassuso", "All Boys": "All Boys",
    "Almirante Brown": "Alte. Brown", "Central Norte de Salta": "Central Norte",
    "Ciudad de Bolívar": "Ciudad Bolívar", "Club Atlético Colón": "Colón",
    "Defensores de Belgrano": "Def. Belgrano", "Deportivo Madryn": "Dep. Madryn",
    "Deportivo Morón": "Dep. Morón", "Estudiantes de Buenos Aires": "Estud. (BA)",
    "Club Ferro Carril Oeste": "Ferro", "Gimnasia Jujuy": "Gimnasia (J)",
    "Godoy Cruz": "Godoy Cruz", "Los Andes": "Los Andes", "CA Mitre": "Mitre",
    "Racing de Córdoba": "Racing (C)", "San Miguel": "San Miguel", "San Telmo": "San Telmo",
}


def _short_team(name):
    name = str(name)
    if name in SHORT_NAMES:
        return SHORT_NAMES[name]
    return name if len(name) <= 13 else name[:12] + "."


def plot_ranking_bars(df, value_col, label_col="equipo", title="", subtitle="",
                      highlight="Chaco For Ever", ascending=False, fmt="{:.2f}",
                      save_path=None):
    """Ranking horizontal de equipos por una métrica; resalta a `highlight`."""
    d = df.dropna(subset=[value_col]).sort_values(value_col, ascending=ascending)
    n = len(d)
    fig, ax = plt.subplots(figsize=(10, max(4, n * 0.42)))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)
    colors = [ACCENT_COLOR if str(t) == highlight else RIVAL_COLOR for t in d[label_col]]
    y = np.arange(n)[::-1]
    ax.barh(y, d[value_col], color=colors, alpha=0.92, zorder=3)
    for yi, v in zip(y, d[value_col]):
        ax.text(v, yi, "  " + fmt.format(v), va="center", ha="left",
                fontsize=9, color=TEXT_COLOR)
    ax.set_yticks(y)
    ax.set_yticklabels(d[label_col], fontsize=9, color=TEXT_COLOR)
    ax.set_xlabel(value_col, color=TEXT_COLOR)
    ttl = title or value_col
    ax.set_title(ttl, fontsize=14, color=TEXT_COLOR, fontweight="bold", loc="left")
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9,
                color=MUTED_COLOR, ha="left")
    ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED_COLOR)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.margins(x=0.12)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def _row_positions(k):
    return np.linspace(18, 82, k) if k > 1 else np.array([50.0])


def plot_best_xi_pitch(xi_df, bench_df=None, formation=(4, 3, 3),
                       round_num="", season="", save_path=None):
    """Dibuja el mejor 11 de la fecha en una cancha vertical (por posición y
    rating), con el banco ideal listado debajo."""
    fig = plt.figure(figsize=(9, 13.5))
    fig.patch.set_facecolor(BG_COLOR)
    gs = fig.add_gridspec(2, 1, height_ratios=[5.4, 1.35], hspace=0.04)
    axp = fig.add_subplot(gs[0])
    axb = fig.add_subplot(gs[1])

    pitch = light_pitch(vertical=True, half=False)
    pitch.draw(ax=axp)
    axp.set_facecolor(BG_COLOR)

    # En mplsoccer las coords son (x=largo 0..100, y=ancho 0..100); VerticalPitch
    # solo rota el dibujo. Ubicamos por "fila" = largo y "carril" = ancho.
    rows = {"G": 15, "D": 34, "M": 55, "F": 80}
    for pos in ("G", "D", "M", "F"):
        sub = xi_df[xi_df["position"] == pos].reset_index(drop=True)
        carriles = _row_positions(len(sub))
        L = rows[pos]
        for i, (_, p) in enumerate(sub.iterrows()):
            W = carriles[i]
            pitch.scatter(L, W, ax=axp, s=760, color=POS_COLOR.get(pos, RIVAL_COLOR),
                          edgecolors="white", linewidth=1.6, zorder=5)
            pitch.annotate(f"{p['rating']:.1f}", (L, W), ax=axp, va="center",
                           ha="center", color="white", fontsize=9.5, fontweight="bold", zorder=6)
            pitch.annotate(str(p["player"]), (L - 4.6, W), ax=axp, va="top", ha="center",
                           color=TEXT_COLOR, fontsize=9, fontweight="bold", zorder=6)
            pitch.annotate(_short_team(p["team"]), (L - 7.4, W), ax=axp, va="top",
                           ha="center", color=MUTED_COLOR, fontsize=7.3, zorder=6)

    ttl = f"Mejor 11 de la Fecha {round_num}" if round_num else "Mejor 11 de la Fecha"
    axp.set_title(f"{ttl} — Grupo A {season}", fontsize=16, color=TEXT_COLOR,
                  fontweight="bold", pad=10)

    # ── Banco ideal: tira de chips 2×5 debajo de la cancha ──
    axb.set_xlim(0, 1); axb.set_ylim(0, 1); axb.axis("off")
    axb.axhline(0.99, color=GRID_COLOR, linewidth=1.0)
    axb.text(0.5, 0.92, "BANCO IDEAL", ha="center", va="top", fontsize=12,
             color=TEXT_COLOR, fontweight="bold")
    if bench_df is not None and not bench_df.empty:
        bench = bench_df.head(10).reset_index(drop=True)
        ncol = 5
        row_y = [0.58, 0.14]
        for i, (_, p) in enumerate(bench.iterrows()):
            col, row = i % ncol, i // ncol
            x, y = (col + 0.5) / ncol, row_y[row if row < len(row_y) else -1]
            axb.scatter([x], [y], s=470, color=POS_COLOR.get(p["position"], RIVAL_COLOR),
                        edgecolors="white", linewidth=1.4, zorder=5)
            axb.text(x, y, f"{p['rating']:.1f}", ha="center", va="center", color="white",
                     fontsize=8.5, fontweight="bold", zorder=6)
            axb.text(x, y - 0.145, str(p["player"]), ha="center", va="top", fontsize=8,
                     color=TEXT_COLOR, fontweight="bold")
            axb.text(x, y - 0.255, _short_team(p["team"]), ha="center", va="top",
                     fontsize=6.8, color=MUTED_COLOR)
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


_ZONE_LABEL = {
    "area_centro": "Área · centro", "area_lateral": "Área · lateral",
    "fuera_centro": "Afuera · centro", "fuera_lateral": "Afuera · lateral",
}
_ZONE_ORDER = ["area_centro", "area_lateral", "fuera_centro", "fuera_lateral"]


def plot_shot_origin(origin_df, title="Origen de los remates", season="",
                     save_path=None):
    """Barras del % de remates por zona de origen (agregado 'LIGA')."""
    d = origin_df[origin_df["equipo"] == "LIGA"].set_index("zona").reindex(_ZONE_ORDER).dropna()
    fig, ax = plt.subplots(figsize=(9, 5))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)
    labels = [_ZONE_LABEL[z] for z in d.index]
    colors = [ACCENT_COLOR if "centro" in z else RIVAL_COLOR for z in d.index]
    ax.bar(labels, d["pct"], color=colors, alpha=0.92, zorder=3)
    for i, v in enumerate(d["pct"]):
        ax.text(i, v, f"{v:.1f}%", ha="center", va="bottom", fontsize=10, color=TEXT_COLOR)
    central = round(d.loc[[z for z in d.index if "centro" in z], "pct"].sum(), 1)
    ax.set_ylabel("% de remates", color=TEXT_COLOR)
    ax.set_title(f"{title} — Grupo A {season}", fontsize=14, color=TEXT_COLOR,
                 fontweight="bold", loc="left")
    ax.text(0, 1.02, f"Por el centro: {central}% de los remates", transform=ax.transAxes,
            fontsize=10, color=MUTED_COLOR, ha="left")
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED_COLOR)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig
