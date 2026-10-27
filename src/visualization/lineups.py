"""
lineups.py (visualization)
==========================
Gráficos del impacto de duplas y tríos de mediocampo (src/analysis/lineups.py).

Mismo tema claro que el resto de visualization/: crema + rojo Chaco.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.visualization.season import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, RIVAL_COLOR, MUTED_COLOR, GRID_COLOR,
    save_fig,
)

POS_COLOR = "#2ca02c"   # verde — el equipo genera más de lo que concede
NEG_COLOR = "#d62728"   # rojo — al revés


def _combo_short(s, maxlen=44):
    return s if len(s) <= maxlen else s[:maxlen - 1] + "…"


def plot_combo_ranking(df, top=8, con="xgdiff_p90_con", ctrl="xgdiff_p90_sin_mp",
                       title=None, save_path=None):
    """Dumbbell: por combo, xGdiff/90 del equipo CON el combo en cancha vs SIN
    (en los mismos partidos). La distancia entre puntos es el aporte neto."""
    d = df.head(top).iloc[::-1].reset_index(drop=True)
    if d.empty:
        return None
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(11, 0.62 * len(d) + 1.6))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    for yi, (_, r) in zip(y, d.iterrows()):
        a, b = r[ctrl], r[con]
        ax.plot([a, b], [yi, yi], color=MUTED_COLOR, lw=2, zorder=1)
        ax.scatter(a, yi, s=70, color="white", edgecolor=MUTED_COLOR,
                   lw=1.6, zorder=2)
        ax.scatter(b, yi, s=130, zorder=3,
                   color=POS_COLOR if b >= a else NEG_COLOR,
                   edgecolor=TEXT_COLOR, lw=0.6)
        ax.annotate(f"{b:+.2f}", (b, yi), xytext=(8 if b >= a else -8, 0),
                    textcoords="offset points", va="center",
                    ha="left" if b >= a else "right",
                    fontsize=9, color=TEXT_COLOR)

    ax.axvline(0, color=TEXT_COLOR, lw=0.8, alpha=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels([
        f"{_combo_short(r['combo'])}\n{int(r['minutos_juntos'])}′ · {int(r['partidos_juntos'])} PJ"
        for _, r in d.iterrows()], fontsize=9)
    ax.set_xlabel("xG a favor − en contra por 90′  (equipo, con la combinación en cancha)",
                  fontsize=10, color=TEXT_COLOR)
    ax.set_title(title or "Impacto de la combinación de mediocampo",
                 fontsize=13, color=TEXT_COLOR, pad=14, loc="left", weight="bold")
    ax.tick_params(colors=MUTED_COLOR)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.grid(axis="x", color=GRID_COLOR, lw=0.6)

    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               markeredgecolor=MUTED_COLOR, markersize=9, label="sin la combinación (mismos partidos)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=POS_COLOR,
               markeredgecolor=TEXT_COLOR, markersize=11, label="con la combinación"),
    ], loc="upper left", fontsize=8, frameon=False)

    fig.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return None
    return fig


def plot_combo_scatter(df, x="minutos_juntos", y="xgdiff_p90_con",
                       size="partidos_juntos", title=None, save_path=None,
                       label_top=12):
    """Minutos juntos (x) vs xGdiff/90 con la combinación (y). Separa
    'la que más juega' de 'la que mejor le rinde al equipo'."""
    d = df.copy()
    if d.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    delta = d.get("delta_xgdiff", pd.Series(0, index=d.index))
    colors = [POS_COLOR if v >= 0 else NEG_COLOR for v in delta]
    ax.scatter(d[x], d[y], s=30 + 14 * d[size], c=colors, alpha=0.75,
               edgecolor=TEXT_COLOR, lw=0.5)

    xmed, ymed = d[x].median(), d[y].median()
    ax.axhline(ymed, color=MUTED_COLOR, lw=0.8, ls="--", alpha=0.7)
    ax.axvline(xmed, color=MUTED_COLOR, lw=0.8, ls="--", alpha=0.7)
    ax.axhline(0, color=TEXT_COLOR, lw=0.8, alpha=0.4)

    lab = d.sort_values(y, ascending=False).head(label_top).reset_index(drop=True)
    for k, r in lab.iterrows():
        dy = 9 if k % 2 == 0 else -14
        ax.annotate(_combo_short(r["combo"], 28), (r[x], r[y]),
                    xytext=(6, dy), textcoords="offset points",
                    fontsize=7.5, color=TEXT_COLOR)

    ax.set_xlabel("Minutos que jugaron juntos", fontsize=10, color=TEXT_COLOR)
    ax.set_ylabel("xG a favor − en contra por 90′  (con la combinación)",
                  fontsize=10, color=TEXT_COLOR)
    ax.set_title(title or "Mediocampo: cuánto juega cada combinación vs cuánto rinde",
                 fontsize=13, color=TEXT_COLOR, pad=14, loc="left", weight="bold")
    ax.tick_params(colors=MUTED_COLOR)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID_COLOR)
    ax.grid(color=GRID_COLOR, lw=0.5)
    fig.text(0.99, 0.01, "verde = aporta sobre el resto del equipo · rojo = no",
             ha="right", fontsize=8, color=MUTED_COLOR)

    fig.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return None
    return fig


UNIT_LABELS = {
    "zaga": "Zaga central", "banda_der": "Banda derecha", "banda_izq": "Banda izquierda",
    "medio": "Mediocampo", "ataque": "Ataque (dupla)", "ataque_trio": "Ataque (trío)",
}


def plot_units_summary(report, top=1, con="xgdiff_p90_con", ctrl="xgdiff_p90_sin_mp",
                       title=None, save_path=None):
    """Una fila por línea del equipo con su(s) mejor(es) combinación(es):
    dumbbell con la combinación en cancha vs el resto de esos mismos partidos."""
    rows = []
    for unit, df in report.items():
        if df is None or df.empty:
            continue
        for _, r in df.head(top).iterrows():
            rows.append((UNIT_LABELS.get(unit, unit), r["combo"],
                         r["minutos_juntos"], r["partidos_juntos"],
                         r[ctrl], r[con]))
    if not rows:
        return None
    rows = rows[::-1]
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(11, 0.72 * len(rows) + 1.6))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    for yi, (_, combo, mins, pj, a, b) in zip(y, rows):
        ax.plot([a, b], [yi, yi], color=MUTED_COLOR, lw=2, zorder=1)
        ax.scatter(a, yi, s=70, color="white", edgecolor=MUTED_COLOR, lw=1.6, zorder=2)
        ax.scatter(b, yi, s=140, zorder=3,
                   color=POS_COLOR if b >= a else NEG_COLOR,
                   edgecolor=TEXT_COLOR, lw=0.6)
        ax.annotate(f"{b:+.2f}", (b, yi), xytext=(9 if b >= a else -9, 0),
                    textcoords="offset points", va="center",
                    ha="left" if b >= a else "right", fontsize=9.5,
                    color=TEXT_COLOR, weight="bold")

    ax.axvline(0, color=TEXT_COLOR, lw=0.8, alpha=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels([
        f"{unit}\n{_combo_short(combo, 40)}  ·  {int(mins)}′ / {int(pj)} PJ"
        for (unit, combo, mins, pj, _, _) in rows], fontsize=9)
    ax.set_xlabel("xG a favor − en contra por 90′  (equipo, con la combinación en cancha)",
                  fontsize=10, color=TEXT_COLOR)
    ax.set_title(title or "La mejor combinación de cada línea — Chaco For Ever",
                 fontsize=13, color=TEXT_COLOR, pad=14, loc="left", weight="bold")
    ax.tick_params(colors=MUTED_COLOR)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.grid(axis="x", color=GRID_COLOR, lw=0.6)

    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
               markeredgecolor=MUTED_COLOR, markersize=9, label="sin (mismos partidos)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=POS_COLOR,
               markeredgecolor=TEXT_COLOR, markersize=11, label="con la combinación"),
    ], loc="lower center", bbox_to_anchor=(0.5, -0.02),
       ncol=2, fontsize=8, frameon=False,
       bbox_transform=fig.transFigure)

    fig.tight_layout(rect=(0, 0.06, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return None
    return fig


def plot_pair_matrix(df_pairs, df_solo, players=None, title=None, save_path=None,
                     min_minutes_color=300):
    """Matriz jugador × jugador. Celda = xGdiff/90 del equipo con esa dupla en
    cancha; diagonal = con ese jugador solo. El número chico es minutos juntos."""
    solo = df_solo.set_index("combo")
    if players is None:
        players = list(solo.sort_values("minutos_juntos", ascending=False).index)
    n = len(players)
    idx = {p: i for i, p in enumerate(players)}

    M = np.full((n, n), np.nan)
    Mmin = np.zeros((n, n))
    for p, i in idx.items():
        if p in solo.index:
            M[i, i] = solo.loc[p, "xgdiff_p90_con"]
            Mmin[i, i] = solo.loc[p, "minutos_juntos"]
    for _, r in df_pairs.iterrows():
        a, b = r["jugadores"]
        if a in idx and b in idx:
            i, j = idx[a], idx[b]
            M[i, j] = M[j, i] = r["xgdiff_p90_con"]
            Mmin[i, j] = Mmin[j, i] = r["minutos_juntos"]

    # Escala de color acotada a las celdas con muestra decente, para que una
    # dupla de 150' con un valor extremo no aplaste el resto de la paleta.
    solid = np.abs(M[Mmin >= min_minutes_color])
    lim = float(np.nanmax(solid)) if solid.size and np.isfinite(np.nanmax(solid)) \
        else (np.nanmax(np.abs(M)) or 1.0)
    lim = max(lim, 0.3)
    fig, ax = plt.subplots(figsize=(1.1 * n + 2.5, 1.1 * n + 1.8))
    fig.patch.set_facecolor(BG_COLOR)
    im = ax.imshow(np.clip(M, -lim, lim), cmap="RdYlGn", vmin=-lim, vmax=lim)

    for i in range(n):
        for j in range(n):
            if np.isnan(M[i, j]):
                continue
            ax.text(j, i - 0.12, f"{M[i, j]:+.2f}", ha="center", va="center",
                    fontsize=9, color=TEXT_COLOR,
                    weight="bold" if i == j else "normal")
            if Mmin[i, j]:
                ax.text(j, i + 0.24, f"{int(Mmin[i, j])}′", ha="center", va="center",
                        fontsize=7, color=MUTED_COLOR)

    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(players, rotation=40, ha="right", fontsize=9, color=TEXT_COLOR)
    ax.set_yticklabels(players, fontsize=9, color=TEXT_COLOR)
    ax.set_title(title or "xGdiff/90 del equipo por dupla de mediocampo\n(diagonal = jugador solo)",
                 fontsize=12, color=TEXT_COLOR, pad=14, loc="left", weight="bold")
    ax.set_xticks(np.arange(-.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-.5, n, 1), minor=True)
    ax.grid(which="minor", color=BG_COLOR, lw=2)
    ax.tick_params(which="minor", length=0)
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03).set_label(
        "xG a favor − en contra / 90′", color=TEXT_COLOR)

    fig.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return None
    return fig
