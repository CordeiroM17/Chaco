"""
season.py (visualization)
=========================
Gráficos de temporada completa y de partido individual.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from mplsoccer import VerticalPitch, Pitch

# ─── Tema claro estilo "references/" ─────────────────────────────────────────
# Fondo crema, líneas de cancha gris suave, paleta a dos tonos:
# rojo = Chaco For Ever (equipo principal), azul pizarra = rival.
BG_COLOR     = "#f4f4ef"   # crema (fondo de figura y de cancha)
TEXT_COLOR   = "#1a1a1a"   # casi negro
ACCENT_COLOR = "#d62728"   # rojo — Chaco For Ever
RIVAL_COLOR  = "#2b3a67"   # azul pizarra — rival
CHACO_COLOR  = ACCENT_COLOR
MUTED_COLOR  = "#8a8a8a"   # gris para ejes y anotaciones secundarias
GRID_COLOR   = "#d9d9d2"   # gris muy claro para rejillas

PITCH_BG     = "#f4f4ef"   # cancha del mismo crema (look continuo, sin caja)
PITCH_LINE   = "#b3b3aa"   # líneas de cancha gris claro

HEAT_CMAP       = "Reds"   # heatmaps de Chaco
HEAT_CMAP_RIVAL = "Blues"  # heatmaps del rival

SHOT_COLORS = {
    "goal":  "#2ca02c",
    "save":  "#1f77b4",
    "miss":  "#d62728",
    "block": "#e8a200",
}


def _fig_style(fig, bg=BG_COLOR):
    fig.patch.set_facecolor(bg)


def light_pitch(pitch_type="opta", half=False, vertical=False,
                line_color=PITCH_LINE, linewidth=1.2):
    """Cancha con el tema claro de las referencias (crema + líneas gris suave)."""
    cls = VerticalPitch if vertical else Pitch
    return cls(pitch_type=pitch_type, half=half, pitch_color=PITCH_BG,
               line_color=line_color, linewidth=linewidth, line_zorder=2)


def save_fig(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


# ─── Shotmap ─────────────────────────────────────────────────────────────────

def plot_shotmap(df_shots, team_label="Chaco For Ever", title=None, save_path=None):
    df = df_shots.copy().reset_index(drop=True)
    df["x_plot"] = 100 - df["coord_x"]
    df["y_plot"] = 100 - df["coord_y"]

    fig, axs = plt.subplots(1, 2, figsize=(18, 9), gridspec_kw={"width_ratios": [1.4, 1]})
    fig.patch.set_facecolor(BG_COLOR)
    ax_pitch, ax_text = axs

    pitch = VerticalPitch(
        half=True, pitch_type="opta",
        pitch_color=PITCH_BG, linewidth=1.5, line_color="#8f8f86", pad_bottom=0.5
    )
    pitch.draw(ax=ax_pitch)
    ax_pitch.set_facecolor(PITCH_BG)

    TEXT_SHOT_COLORS = {
        "goal":  "#1a7a00",
        "save":  "#0050a0",
        "miss":  "#b30000",
        "block": "#7a5800",
    }

    for i, row in df.iterrows():
        num = i + 1
        s_type = row.get("shotType", "miss")
        color = SHOT_COLORS.get(s_type, "gray")
        xgot_val = row.get("xgot") if pd.notna(row.get("xgot", np.nan)) else 0
        size = max(xgot_val * 800 + 200, 300)
        pitch.scatter(row["x_plot"], row["y_plot"], s=size, c=color,
                      edgecolor="black", linewidth=1.5, alpha=0.9, ax=ax_pitch, zorder=2)
        pitch.text(row["x_plot"], row["y_plot"] - 4, str(num),
                   ax=ax_pitch, color="black", fontsize=10, fontweight="bold",
                   ha="center", va="center", zorder=3)

    legend_handles = [
        Line2D([0], [0], marker="o", color="w", label="Gol",      markerfacecolor=SHOT_COLORS["goal"],  markersize=12, markeredgecolor="black"),
        Line2D([0], [0], marker="o", color="w", label="Atajada",  markerfacecolor=SHOT_COLORS["save"],  markersize=12, markeredgecolor="black"),
        Line2D([0], [0], marker="o", color="w", label="Desviado", markerfacecolor=SHOT_COLORS["miss"],  markersize=12, markeredgecolor="black"),
        Line2D([0], [0], marker="o", color="w", label="Bloqueado",markerfacecolor=SHOT_COLORS["block"], markersize=12, markeredgecolor="black"),
    ]
    ax_pitch.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, 0),
                    ncol=4, fontsize=12, frameon=True, facecolor=BG_COLOR, edgecolor="#cfcfc6", labelcolor=TEXT_COLOR)
    ax_pitch.set_title(title or f"Mapa de Tiros – {team_label}",
                       fontsize=16, fontweight="bold", color=TEXT_COLOR, pad=15)

    ax_text.set_facecolor(BG_COLOR)
    ax_text.axis("off")
    ax_text.set_title("Detalle de Jugadas", fontsize=14, fontweight="bold", color=TEXT_COLOR, pad=10)
    for i, row in df.iterrows():
        num = i + 1
        s_type = row.get("shotType", "miss")
        color = TEXT_SHOT_COLORS.get(s_type, "black")
        xg_str = f"{row.get('xg', 0):.2f}" if pd.notna(row.get("xg", np.nan)) else "N/A"
        minute = int(row.get("time", 0)) if pd.notna(row.get("time", np.nan)) else "?"
        text = f"{num}. {row.get('player_name', '?')} {minute}' ({s_type}) xG:{xg_str}"
        pos_y = 0.97 - (i * 0.053)
        if pos_y < 0.02:
            break
        ax_text.text(0.02, pos_y, text, fontsize=11, fontfamily="monospace",
                     color=color, va="center", transform=ax_text.transAxes)

    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_shotmap_4grid(df_shots, team_label="Chaco For Ever", title=None, save_path=None):
    """
    Cuatro paneles (medio campo cada uno), uno por tipo de tiro: gol, atajada,
    desviado, bloqueado. Sin números ni detalle de jugadas — el tamaño del punto
    es proporcional al xG del tiro (las ocasiones claras resaltan).
    """
    df = df_shots.copy()
    df["x_plot"] = 100 - df["coord_x"]
    df["y_plot"] = 100 - df["coord_y"]
    if "xg" in df.columns:
        df["xg"] = pd.to_numeric(df["xg"], errors="coerce").fillna(0)
    else:
        df["xg"] = 0

    fig, axs = plt.subplots(2, 2, figsize=(13, 13))
    fig.patch.set_facecolor(BG_COLOR)
    axs = axs.flatten()
    pitch = VerticalPitch(half=True, pitch_type="opta", pitch_color=PITCH_BG,
                          linewidth=1.5, line_color="#8f8f86", pad_bottom=0.5)

    panels = [("goal", "Goles"), ("save", "Atajadas"),
              ("miss", "Desviados"), ("block", "Bloqueados")]
    for ax, (s_type, label) in zip(axs, panels):
        pitch.draw(ax=ax)
        ax.set_facecolor(PITCH_BG)
        subset = df[df["shotType"] == s_type]
        if not subset.empty:
            sizes = (subset["xg"] * 900 + 120).clip(120, 1100)
            pitch.scatter(subset["x_plot"], subset["y_plot"], s=sizes,
                          c=SHOT_COLORS[s_type], edgecolor="black", linewidth=1.2,
                          alpha=0.85, ax=ax, zorder=2)
        ax.set_title(f"{label}  ({len(subset)})", fontsize=14,
                     color=TEXT_COLOR, fontweight="bold", pad=6)

    plt.suptitle(title or f"Distribución de Tiros – {team_label}",
                 fontsize=17, color=TEXT_COLOR, fontweight="bold", y=0.995)
    # Nota del tamaño = xG
    fig.text(0.5, 0.02, "Tamaño del punto ∝ xG del tiro", ha="center",
             fontsize=10, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.03, 1, 0.97))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# Tipos de tiro → etiqueta del panel (orden de los 4 cuadrantes)
_SHOT_TYPE_PANELS = [("goal", "Goles"), ("save", "Atajadas"),
                     ("miss", "Desviados"), ("block", "Bloqueados")]
_SHOT_TYPE_ES = {"goal": "Gol", "save": "Atajada", "miss": "Desviado",
                 "block": "Bloqueado"}


def _spread_coincident(xs, ys, min_dist=5.0, radius=3.6):
    """Separa puntos casi superpuestos: los que caen a <min_dist se reparten en
    un pequeño círculo alrededor de su centroide para que los números se lean.
    Devuelve nuevas listas (x, y) del mismo largo/orden."""
    xs = [float(v) for v in xs]
    ys = [float(v) for v in ys]
    n = len(xs)
    out_x, out_y = list(xs), list(ys)
    used = [False] * n
    for i in range(n):
        if used[i]:
            continue
        group = [j for j in range(n) if not used[j] and
                 (xs[j] - xs[i]) ** 2 + (ys[j] - ys[i]) ** 2 < min_dist ** 2]
        if len(group) > 1:
            cx = sum(xs[j] for j in group) / len(group)
            cy = sum(ys[j] for j in group) / len(group)
            k = len(group)
            r = radius * (1.0 if k <= 3 else 1.4)
            for idx, j in enumerate(group):
                ang = 2 * np.pi * idx / k
                out_x[j] = cx + r * np.cos(ang)
                out_y[j] = cy + r * np.sin(ang)
                used[j] = True
        else:
            used[i] = True
    return out_x, out_y


def plot_shotmap_4grid_match(df_shots, is_home=True, chaco_label="Chaco For Ever",
                             rival_label="Rival", match_label="", title=None,
                             save_path=None):
    """
    Shotmap de UN partido en 4 medios-campos por tipo de tiro
    (Goles, Atajadas, Desviados, Bloqueados). En cada panel conviven los tiros
    de ambos equipos: Chaco en rojo, Rival en azul. Cada tiro lleva un número
    (cronológico, único en todo el partido) y a la derecha va la lista
    "Nº. jugador (C/R) min' tipo xG".

    df_shots: shotmap_clean.csv (columnas isHome, shotType, xg, coord_x/y, time...).
    is_home : True si Chaco jugó de local (define qué isHome es Chaco).
    """
    if df_shots is None or len(df_shots) == 0:
        return None

    df = df_shots.copy()
    # Coordenadas al mismo marco que el resto de shotmaps (medio campo, ataca arriba)
    df["x_plot"] = 100 - pd.to_numeric(df["coord_x"], errors="coerce")
    df["y_plot"] = 100 - pd.to_numeric(df["coord_y"], errors="coerce")
    df["xg"] = pd.to_numeric(df.get("xg"), errors="coerce").fillna(0)
    df = df.dropna(subset=["x_plot", "y_plot"])
    if df.empty:
        return None

    # isHome robusto (bool o texto) → bandera de Chaco
    home_flag = df["isHome"].astype(str).str.lower().isin(["true", "1"])
    base_chaco = home_flag if is_home else ~home_flag
    # Gol en contra: lo hace un jugador del rival pero CUENTA para el otro equipo.
    # Invertimos la bandera para que el color/conteo refleje el marcador real.
    if "situation" in df.columns:
        own_goal = df["situation"].astype(str).str.lower().eq("own-goal")
    else:
        own_goal = pd.Series(False, index=df.index)
    df["is_own_goal"] = own_goal
    df["is_chaco"] = base_chaco ^ own_goal

    # Normalizar tipos fuera de los 4 paneles (ej. "post") a "miss"
    df["stype"] = df["shotType"].where(
        df["shotType"].isin([t for t, _ in _SHOT_TYPE_PANELS]), "miss")

    # Numeración cronológica global (1..N)
    df["_t"] = pd.to_numeric(df.get("time"), errors="coerce").fillna(0)
    df["_at"] = pd.to_numeric(df.get("addedTime"), errors="coerce").fillna(0)
    df = df.sort_values(["_t", "_at"]).reset_index(drop=True)
    df["num"] = df.index + 1

    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor(BG_COLOR)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.05], wspace=0.05, hspace=0.16)
    pitch_axes = [fig.add_subplot(gs[r, c]) for r in (0, 1) for c in (0, 1)]
    ax_text = fig.add_subplot(gs[:, 2])

    pitch = VerticalPitch(half=True, pitch_type="opta", pitch_color=PITCH_BG,
                          linewidth=1.5, line_color="#8f8f86", pad_bottom=0.5)

    def team_color(is_chaco):
        return ACCENT_COLOR if is_chaco else RIVAL_COLOR

    for ax, (s_type, label) in zip(pitch_axes, _SHOT_TYPE_PANELS):
        pitch.draw(ax=ax)
        ax.set_facecolor(PITCH_BG)
        subset = df[df["stype"] == s_type].reset_index(drop=True)
        # Separar tiros casi superpuestos para que los números no se pisen
        sx, sy = _spread_coincident(subset["x_plot"], subset["y_plot"])
        for i, row in subset.iterrows():
            color = team_color(row["is_chaco"])
            size = float(np.clip(row["xg"] * 900 + 260, 260, 1100))
            pitch.scatter(sx[i], sy[i], s=size, c=color,
                          edgecolor="black", linewidth=1.2, alpha=0.9,
                          ax=ax, zorder=2)
            pitch.text(sx[i], sy[i], str(int(row["num"])),
                       ax=ax, color="white", fontsize=8.5, fontweight="bold",
                       ha="center", va="center", zorder=3)
        ax.set_title(f"{label}  ({len(subset)})", fontsize=14,
                     color=TEXT_COLOR, fontweight="bold", pad=6)

    # ── Lista cronológica a la derecha (color por equipo) ──
    ax_text.axis("off")
    ax_text.set_facecolor(BG_COLOR)
    ax_text.set_title("Detalle de Tiros", fontsize=14, fontweight="bold",
                      color=TEXT_COLOR, pad=10)
    TEXT_TEAM = {True: "#b30000", False: "#0050a0"}  # rojo Chaco / azul Rival

    # Lista en UNA sola columna (entradas anchas → 2 columnas se encimarían).
    # Fuente y paso se adaptan a la cantidad de tiros para que siempre entren.
    n = len(df)
    step = min(0.045, 0.965 / max(n, 1))
    fs = 11 if n <= 18 else (9 if n <= 26 else (7.5 if n <= 34 else 6.5))

    for i, row in df.iterrows():
        pos_y = 0.975 - i * step
        tag = "C" if row["is_chaco"] else "R"
        minute = f"{int(row['_t'])}'" if row["_t"] else "?'"
        xg_str = f"{row['xg']:.2f}" if row["xg"] else "—"
        og = " (en contra)" if row.get("is_own_goal") else ""
        txt = (f"{int(row['num'])}. {row.get('player_name', '?')}{og} ({tag}) "
               f"{minute} {_SHOT_TYPE_ES.get(row['stype'], row['stype'])} xG:{xg_str}")
        ax_text.text(0.02, pos_y, txt, fontsize=fs, fontfamily="monospace",
                     color=TEXT_TEAM[bool(row["is_chaco"])], va="center",
                     transform=ax_text.transAxes)

    # Leyenda equipos
    legend_handles = [
        Line2D([0], [0], marker="o", color="w", label=chaco_label,
               markerfacecolor=ACCENT_COLOR, markersize=12, markeredgecolor="black"),
        Line2D([0], [0], marker="o", color="w", label=rival_label,
               markerfacecolor=RIVAL_COLOR, markersize=12, markeredgecolor="black"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=2, fontsize=12,
               frameon=True, facecolor=BG_COLOR, edgecolor="#cfcfc6",
               labelcolor=TEXT_COLOR, bbox_to_anchor=(0.5, 0.005))

    default_title = f"Mapa de Tiros por Tipo – {chaco_label} vs {rival_label}"
    if match_label:
        default_title += f"  ({match_label})"
    fig.suptitle(title or default_title, fontsize=17, color=TEXT_COLOR,
                 fontweight="bold", y=0.985)
    fig.text(0.34, 0.02, "Tamaño del punto ∝ xG  ·  número = orden cronológico",
             ha="center", fontsize=10, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.04, 1, 0.96))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Stats partido ────────────────────────────────────────────────────────────

# Orden y etiquetas en español (estilo references/stats_comparation.png)
_STATS_ORDER = [
    "Ball possession", "Expected goals", "Total shots", "Shots on target",
    "Goalkeeper saves", "Corner kicks", "Fouls", "Passes", "Accurate passes",
    "Tackles", "Yellow cards", "Red cards",
]
_STATS_ES = {
    "Ball possession": "Posesión de pelota",
    "Expected goals":  "Goles esperados (xG)",
    "Total shots":     "Tiros totales",
    "Shots on target": "Tiros al arco",
    "Goalkeeper saves": "Atajadas",
    "Corner kicks":    "Córners",
    "Fouls":           "Faltas",
    "Passes":          "Pases",
    "Accurate passes": "Pases precisos",
    "Tackles":         "Entradas",
    "Yellow cards":    "Tarjetas amarillas",
    "Red cards":       "Tarjetas rojas",
}


def _fmt_stat(metric, v):
    if metric == "Ball possession":
        return f"{int(round(v))}%"
    if metric == "Expected goals":
        return f"{v:.2f}"
    return str(int(round(v)))


def plot_match_stats(df_stats, home_label="Local", away_label="Visitante",
                     is_chaco_home=True, save_path=None):
    """
    Resumen del partido estilo SofaScore: una fila por métrica con los dos
    valores (local izquierda, visitante derecha) y una barra dividida en
    proporción debajo. Colores: rojo = Chaco, azul pizarra = rival.
    """
    df = df_stats[df_stats["metric"].isin(_STATS_ORDER)].copy()
    if df.empty:
        df = df_stats.copy()
    # SofaScore repite algunas métricas en varios grupos (ej. "Total shots"):
    # nos quedamos con la primera aparición de cada una.
    df = df.drop_duplicates(subset="metric", keep="first")
    df["_cat"] = pd.Categorical(df["metric"], categories=_STATS_ORDER, ordered=True)
    df = df.sort_values("_cat")

    metrics   = df["metric"].tolist()
    home_vals = pd.to_numeric(df["home_val"], errors="coerce").fillna(0).values
    away_vals = pd.to_numeric(df["away_val"], errors="coerce").fillna(0).values
    n = len(metrics)

    home_color = ACCENT_COLOR if is_chaco_home else RIVAL_COLOR
    away_color = RIVAL_COLOR if is_chaco_home else ACCENT_COLOR

    fig, ax = plt.subplots(figsize=(9, 0.92 * n + 1.2))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n)
    ax.axis("off")

    bar_h     = 0.18      # alto de la barra
    track_col = "#e3e3db" # riel gris claro
    gap       = 0.006     # separación entre los dos segmentos

    for i, (metric, h, a) in enumerate(zip(metrics, home_vals, away_vals)):
        slot = n - 1 - i          # 0 abajo → n-1 arriba
        y_txt = slot + 0.62
        y_bar = slot + 0.28

        # Etiqueta centrada + valores a los costados
        ax.text(0.5, y_txt, _STATS_ES.get(metric, metric), ha="center", va="center",
                fontsize=11, fontweight="bold", color=TEXT_COLOR)
        ax.text(0.0, y_txt, _fmt_stat(metric, h), ha="left", va="center",
                fontsize=12, fontweight="bold", color=home_color)
        ax.text(1.0, y_txt, _fmt_stat(metric, a), ha="right", va="center",
                fontsize=12, fontweight="bold", color=away_color)

        # Barra: riel + dos segmentos proporcionales
        total = h + a
        frac_h = 0.5 if total == 0 else h / total
        ax.barh(y_bar, 1.0, height=bar_h, left=0, color=track_col, zorder=1)
        if frac_h > 0:
            ax.barh(y_bar, max(frac_h - gap, 0), height=bar_h, left=0,
                    color=home_color, zorder=2)
        if frac_h < 1:
            ax.barh(y_bar, max(1 - frac_h - gap, 0), height=bar_h,
                    left=frac_h + gap, color=away_color, zorder=2)

    # Encabezado con los dos equipos
    fig.text(0.5, 0.975, "Resumen del Partido", ha="center",
             fontsize=15, fontweight="bold", color=TEXT_COLOR)
    fig.text(0.06, 0.94, home_label, ha="left", fontsize=12,
             fontweight="bold", color=home_color)
    fig.text(0.94, 0.94, away_label, ha="right", fontsize=12,
             fontweight="bold", color=away_color)

    plt.tight_layout(rect=(0, 0, 1, 0.93))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Gráficos de temporada ────────────────────────────────────────────────────

def plot_season_points(season_df, save_path=None, team_label="Chaco For Ever"):
    fig, ax = plt.subplots(figsize=(14, 5))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)
    x = range(1, len(season_df) + 1)
    ax.plot(x, season_df["points_cumsum"], color=ACCENT_COLOR, linewidth=2.5, marker="o", markersize=6)
    ax.fill_between(x, season_df["points_cumsum"], alpha=0.15, color=ACCENT_COLOR)
    for i, row in season_df.reset_index().iterrows():
        color = {"W": "#2ca02c", "D": "#e8a200", "L": "#d62728"}.get(row["result"], MUTED_COLOR)
        ax.scatter(i + 1, row["points_cumsum"], color=color, s=80, zorder=5, edgecolor="white", linewidth=0.6)
    ax.set_xlabel("Jornada", color=TEXT_COLOR, fontsize=11)
    ax.set_ylabel("Puntos acumulados", color=TEXT_COLOR, fontsize=11)
    ax.set_title(f"Evolución de Puntos – {team_label}", fontsize=14, color=TEXT_COLOR, fontweight="bold")
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.spines["bottom"].set_color(MUTED_COLOR)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    legend = [
        mpatches.Patch(color="#2ca02c", label="Victoria"),
        mpatches.Patch(color="#e8a200", label="Empate"),
        mpatches.Patch(color="#d62728", label="Derrota"),
    ]
    ax.legend(handles=legend, facecolor=BG_COLOR, labelcolor=TEXT_COLOR, fontsize=10)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_cumulative_xg_vs_goals(season_df, save_path=None):
    """Curva acumulada de goles reales (a favor/en contra) vs. xG acumulado,
    fecha a fecha. Muestra visualmente cuánto sobre/sub-rindió la defensa y
    el ataque frente a lo esperado a lo largo de toda la temporada."""
    if "chaco_xg" not in season_df.columns:
        return None
    fig, ax = plt.subplots(figsize=(14, 5.5))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)
    x = range(1, len(season_df) + 1)

    gf_cum = season_df["chaco_goals"].cumsum()
    gc_cum = season_df["rival_goals"].cumsum()
    xgf_cum = season_df["chaco_xg"].cumsum()
    xgc_cum = season_df["rival_xg"].cumsum()

    ax.plot(x, gf_cum, color=ACCENT_COLOR, linewidth=2.5, marker="o", markersize=4,
            label="Goles a favor (real)")
    ax.plot(x, xgf_cum, color=ACCENT_COLOR, linewidth=1.6, linestyle="--", alpha=0.75,
            label="xG a favor (esperado)")
    ax.plot(x, gc_cum, color=RIVAL_COLOR, linewidth=2.5, marker="o", markersize=4,
            label="Goles en contra (real)")
    ax.plot(x, xgc_cum, color=RIVAL_COLOR, linewidth=1.6, linestyle="--", alpha=0.75,
            label="xG en contra (esperado)")

    ax.fill_between(x, gc_cum, xgc_cum, where=(gc_cum >= xgc_cum),
                     color=RIVAL_COLOR, alpha=0.12, interpolate=True)

    labels = [f"J{i+1}" for i in range(len(season_df))]
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45, fontsize=8, color=TEXT_COLOR)
    ax.set_ylabel("Acumulado", color=TEXT_COLOR, fontsize=11)
    ax.set_xlabel("Jornada", color=TEXT_COLOR, fontsize=11)
    ax.set_title("Goles Reales vs. xG Acumulado — Temporada 2026", fontsize=14,
                 color=TEXT_COLOR, fontweight="bold")
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.spines["bottom"].set_color(MUTED_COLOR)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(facecolor=BG_COLOR, labelcolor=TEXT_COLOR, fontsize=9, loc="upper left")

    diff = gc_cum.iloc[-1] - xgc_cum.iloc[-1]
    ax.annotate(f"+{diff:.2f} goles concedidos\npor encima del xG",
                xy=(x[-1], gc_cum.iloc[-1]), xytext=(-95, -35),
                textcoords="offset points", fontsize=8.5, color=RIVAL_COLOR,
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RIVAL_COLOR, lw=1))

    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_xpoints_season(season_xp_df, save_path=None, team_label="Chaco For Ever"):
    """Puntos reales acumulados vs. puntos esperados (xPoints) acumulados,
    fecha a fecha — de analysis.season.season_xpoints_table(). Distinto de
    plot_cumulative_xg_vs_goals (que compara goles, no puntos): acá el eje es
    directamente "cuánto merecía sacar el equipo según su xG de cada partido"."""
    if "xpoints_cumsum" not in season_xp_df.columns:
        return None
    df = season_xp_df.dropna(subset=["xpoints_cumsum"]).reset_index(drop=True)
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(14, 5))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)
    x = range(1, len(df) + 1)

    ax.plot(x, df["points_cumsum"], color=ACCENT_COLOR, linewidth=2.5,
            marker="o", markersize=5, label="Puntos reales", zorder=3)
    ax.plot(x, df["xpoints_cumsum"], color=TEXT_COLOR, linewidth=1.8,
            linestyle="--", alpha=0.8, label="Puntos esperados (xPoints)", zorder=3)
    ax.fill_between(x, df["points_cumsum"], df["xpoints_cumsum"],
                     where=(df["points_cumsum"] >= df["xpoints_cumsum"]),
                     color="#2ca02c", alpha=0.12, interpolate=True)
    ax.fill_between(x, df["points_cumsum"], df["xpoints_cumsum"],
                     where=(df["points_cumsum"] < df["xpoints_cumsum"]),
                     color=ACCENT_COLOR, alpha=0.12, interpolate=True)

    diff = df["points_cumsum"].iloc[-1] - df["xpoints_cumsum"].iloc[-1]
    signo = "+" if diff >= 0 else ""
    color_diff = "#2ca02c" if diff >= 0 else ACCENT_COLOR
    ax.annotate(f"{signo}{diff:.1f} pts vs. lo esperado",
                xy=(x[-1], df["points_cumsum"].iloc[-1]), xytext=(-100, 15),
                textcoords="offset points", fontsize=9, color=color_diff,
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=color_diff, lw=1))

    ax.set_xlabel("Jornada", color=TEXT_COLOR, fontsize=11)
    ax.set_ylabel("Puntos acumulados", color=TEXT_COLOR, fontsize=11)
    ax.set_title(f"Puntos Reales vs. Esperados (xPoints) – {team_label}",
                 fontsize=14, color=TEXT_COLOR, fontweight="bold")
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.spines["bottom"].set_color(MUTED_COLOR)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(facecolor=BG_COLOR, labelcolor=TEXT_COLOR, fontsize=10, loc="upper left")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_xg_season(season_df, save_path=None, team_label="Chaco For Ever"):
    if "chaco_xg" not in season_df.columns:
        return None
    fig, ax = plt.subplots(figsize=(14, 5))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)
    x = range(len(season_df))
    ax.bar([i - 0.2 for i in x], season_df["chaco_xg"], 0.4, color=ACCENT_COLOR, alpha=0.9, label=f"xG {team_label}")
    ax.bar([i + 0.2 for i in x], season_df["rival_xg"],  0.4, color=RIVAL_COLOR,  alpha=0.9, label="xG Rival")
    labels = [f"J{i+1}" for i in range(len(season_df))]
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45, fontsize=8, color=TEXT_COLOR)
    ax.set_ylabel("xG", color=TEXT_COLOR)
    ax.set_title("Expected Goals por Partido", fontsize=14, color=TEXT_COLOR, fontweight="bold")
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.spines["bottom"].set_color(MUTED_COLOR)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(facecolor=BG_COLOR, labelcolor=TEXT_COLOR)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_top_players(season_player_df, metric="minutos", top_n=15,
                     xmin=None, save_path=None):
    """
    Barras horizontales del top N en una métrica.

    xmin: dónde arranca el eje X. Para métricas comprimidas (ej. rating, ~6-8)
    conviene arrancar cerca del mínimo para que se note la diferencia entre
    barras; para conteos (minutos, goles) dejar None (arranca en 0).
    """
    df = season_player_df.nlargest(top_n, metric)[["player", metric]].copy()
    fig, ax = plt.subplots(figsize=(10, 7))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)

    vals = df[metric].values
    vmax = float(np.nanmax(vals)) if len(vals) else 1.0
    if xmin is None:
        xmin = 0.0
    span = max(vmax - xmin, 1e-6)
    offset = span * 0.015

    y = range(len(df))
    ax.barh(list(y), vals, color=ACCENT_COLOR, alpha=0.9, zorder=2)
    ax.set_yticks(list(y))
    ax.set_yticklabels(df["player"].values, fontsize=11, color=TEXT_COLOR)
    ax.tick_params(axis="x", colors=TEXT_COLOR)
    ax.set_xlim(xmin, vmax + offset * 5)
    ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8, zorder=0)

    label = metric.replace("_", " ").capitalize()
    ax.set_xlabel(label, color=TEXT_COLOR)
    ax.set_title(f"Top {top_n} Jugadores – {label}", fontsize=13,
                 color=TEXT_COLOR, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)
    # Para conteos mostramos entero; para rating, un decimal.
    is_rating = "rating" in metric
    for i, val in enumerate(vals):
        txt = f"{val:.1f}" if is_rating else f"{val:.0f}"
        ax.text(val + offset, i, txt, va="center", ha="left",
                fontsize=10, color=TEXT_COLOR, fontweight="bold")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Red de minutos compartidos (grafo de relaciones) ────────────────────────

def plot_shared_minutes_network(nodes_df, edges_df, season="", min_edge_minutes=180,
                                top_edges=22, title=None, save_path=None):
    """
    Grafo circular de relaciones: los jugadores se ubican en un círculo (ordenados
    por minutos) y SOLO se dibujan las `top_edges` duplas más fuertes (más minutos
    juntos) como cuerdas que cruzan el centro. Así se evita la "madeja" de un grafo
    casi completo. Nodo ∝ minutos totales; grosor de la cuerda ∝ minutos juntos;
    color = diferencia de gol/90' del equipo con esa dupla (verde +/ rojo −).
    Sale de analysis.season.shared_minutes_network.
    """
    import networkx as nx
    from matplotlib.colors import TwoSlopeNorm

    if nodes_df is None or nodes_df.empty:
        return None

    mins = dict(zip(nodes_df["player_name"], nodes_df["minutes"]))
    by_min = list(nodes_df.sort_values("minutes", ascending=False)["player_name"])

    # Selección de duplas: primero por umbral de minutos, luego las top por minutos juntos
    ed = edges_df
    if ed is not None and not ed.empty:
        ed = ed[(ed["minutes_together"] >= min_edge_minutes)
                & ed["p1"].isin(mins) & ed["p2"].isin(mins)]
        ed = ed.sort_values("minutes_together", ascending=False).head(top_edges)
    else:
        ed = pd.DataFrame(columns=["p1", "p2", "minutes_together", "gd_per90"])

    # Orden alrededor del círculo: repartimos los jugadores CON duplas de forma
    # pareja para que las cuerdas crucen todo el círculo (y no se amontonen en
    # una mitad); los que no tienen duplas rellenan los huecos.
    connected = [p for p in by_min if p in set(ed["p1"]) | set(ed["p2"])]
    rest = [p for p in by_min if p not in connected]
    n = len(by_min)
    order = [None] * n
    if connected:
        for k, p in enumerate(connected):
            order[round(k * n / len(connected)) % n] = p
    ri = iter(rest)
    for i in range(n):
        if order[i] is None:
            order[i] = next(ri)

    G = nx.Graph()
    G.add_nodes_from(order)
    for _, r in ed.iterrows():
        G.add_edge(r["p1"], r["p2"], minutes=r["minutes_together"], gd=r["gd_per90"])

    fig, ax = plt.subplots(figsize=(13, 12))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")

    # Layout circular manual siguiendo `order` (12 en punto, sentido horario)
    n = len(order)
    ang = {p: (np.pi / 2 - 2 * np.pi * i / n) for i, p in enumerate(order)}
    pos = {p: (np.cos(a), np.sin(a)) for p, a in ang.items()}
    maxmin = max(mins.values()) or 1

    if G.number_of_edges():
        e_min = np.array([G[u][v]["minutes"] for u, v in G.edges()], dtype=float)
        e_gd = np.array([G[u][v]["gd"] for u, v in G.edges()], dtype=float)
        widths = 1.2 + 6.0 * (e_min / (e_min.max() or 1))
        lim = max(float(np.abs(e_gd).max()), 0.1)
        norm = TwoSlopeNorm(vmin=-lim, vcenter=0.0, vmax=lim)
        cmap = plt.get_cmap("RdYlGn")
        nx.draw_networkx_edges(
            G, pos, ax=ax, width=widths,
            edge_color=[cmap(norm(g)) for g in e_gd], alpha=0.80,
            connectionstyle="arc3,rad=0.12")

    node_sizes = [500 + 3000 * (mins[p] / maxmin) for p in order]
    nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=order, node_size=node_sizes,
                           node_color=ACCENT_COLOR, edgecolors="white",
                           linewidths=1.8, alpha=0.97)

    # Etiquetas por fuera del círculo, alineadas radialmente
    for p in order:
        a = ang[p]
        x, y = 1.14 * np.cos(a), 1.14 * np.sin(a)
        ha = "left" if np.cos(a) > 0.1 else ("right" if np.cos(a) < -0.1 else "center")
        ax.text(x, y, p.split()[-1], fontsize=9.5, fontweight="bold",
                color=TEXT_COLOR, ha=ha, va="center")

    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.3, 1.3)

    # Barra de color para la diferencia de gol/90'
    if G.number_of_edges():
        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, shrink=0.6)
        cbar.set_label("Dif. de gol/90' de la dupla", color=TEXT_COLOR, fontsize=9)
        cbar.ax.tick_params(colors=TEXT_COLOR)

    ax.set_title(title or f"Red de Minutos Compartidos – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=16)
    fig.text(0.5, 0.03, f"Nodo ∝ minutos jugados  ·  se muestran solo las "
             f"{len(ed)} duplas con más minutos juntos (cuerda ∝ minutos)  ·  "
             "color = rinde la dupla (verde + / rojo −)",
             ha="center", fontsize=9, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Duplas asociativas (posición + volumen de pases) ────────────────────────

def plot_pass_association_network(nodes_df, edges_df, season="", min_edge_matches=5,
                                   top_edges=22, title=None, save_path=None):
    """
    Mismo estilo circular que plot_shared_minutes_network, pero la dupla se
    arma por CERCANÍA EN CANCHA + VOLUMEN DE PASES (avg_score de
    analysis.season.pass_association_network), no por minutos compartidos.
    Nodo ∝ pases acertados totales de la temporada; grosor de la cuerda ∝
    fuerza de la asociación; color = volumen de pases combinado promedio
    (más oscuro = pasan más entre los dos).
    """
    import networkx as nx

    if nodes_df is None or nodes_df.empty:
        return None

    passes = dict(zip(nodes_df["player_name"], nodes_df["passes"]))
    by_passes = list(nodes_df.sort_values("passes", ascending=False)["player_name"])

    ed = edges_df
    if ed is not None and not ed.empty:
        ed = ed[(ed["matches_together"] >= min_edge_matches)
                & ed["p1"].isin(passes) & ed["p2"].isin(passes)]
        ed = ed.sort_values("avg_score", ascending=False).head(top_edges)
    else:
        ed = pd.DataFrame(columns=["p1", "p2", "matches_together", "avg_score",
                                    "avg_combined_passes"])

    connected = [p for p in by_passes if p in set(ed["p1"]) | set(ed["p2"])]
    rest = [p for p in by_passes if p not in connected]
    n = len(by_passes)
    order = [None] * n
    if connected:
        for k, p in enumerate(connected):
            order[round(k * n / len(connected)) % n] = p
    ri = iter(rest)
    for i in range(n):
        if order[i] is None:
            order[i] = next(ri)

    G = nx.Graph()
    G.add_nodes_from(order)
    for _, r in ed.iterrows():
        G.add_edge(r["p1"], r["p2"], score=r["avg_score"], passes=r["avg_combined_passes"])

    fig, ax = plt.subplots(figsize=(13, 12))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")

    n = len(order)
    ang = {p: (np.pi / 2 - 2 * np.pi * i / n) for i, p in enumerate(order)}
    pos = {p: (np.cos(a), np.sin(a)) for p, a in ang.items()}
    maxpass = max(passes.values()) or 1

    if G.number_of_edges():
        e_score = np.array([G[u][v]["score"] for u, v in G.edges()], dtype=float)
        e_pass = np.array([G[u][v]["passes"] for u, v in G.edges()], dtype=float)
        widths = 1.2 + 6.0 * (e_score / (e_score.max() or 1))
        cmap = plt.get_cmap("YlOrRd")
        norm = plt.Normalize(vmin=0, vmax=e_pass.max() or 1)
        nx.draw_networkx_edges(
            G, pos, ax=ax, width=widths,
            edge_color=[cmap(norm(p)) for p in e_pass], alpha=0.85,
            connectionstyle="arc3,rad=0.12")

    node_sizes = [500 + 3000 * (passes[p] / maxpass) for p in order]
    nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=order, node_size=node_sizes,
                           node_color=ACCENT_COLOR, edgecolors="white",
                           linewidths=1.8, alpha=0.97)

    for p in order:
        a = ang[p]
        x, y = 1.14 * np.cos(a), 1.14 * np.sin(a)
        ha = "left" if np.cos(a) > 0.1 else ("right" if np.cos(a) < -0.1 else "center")
        ax.text(x, y, p.split()[-1], fontsize=9.5, fontweight="bold",
                color=TEXT_COLOR, ha=ha, va="center")

    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.3, 1.3)

    if G.number_of_edges():
        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, shrink=0.6)
        cbar.set_label("Pases combinados promedio", color=TEXT_COLOR, fontsize=9)
        cbar.ax.tick_params(colors=TEXT_COLOR)

    ax.set_title(title or f"Duplas Asociativas – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=16)
    fig.text(0.5, 0.03, f"Nodo ∝ pases acertados de la temporada  ·  se muestran solo las "
             f"{len(ed)} duplas más asociadas (cuerda ∝ cercanía × pases)  ·  "
             "color = volumen de pases combinado",
             ha="center", fontsize=9, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Forma reciente (rolling) ────────────────────────────────────────────────

def plot_recent_form(season_df, window=5, season="", title=None, save_path=None):
    """
    Media móvil de puntos por partido en las últimas `window` fechas. Muestra
    rachas (a diferencia del acumulado de toda la temporada). Espera las columnas
    'points' y 'result' (de build_season_table), en orden cronológico.
    """
    if season_df is None or season_df.empty or "points" not in season_df.columns:
        return None
    df = season_df.reset_index(drop=True).copy()
    x = np.arange(1, len(df) + 1)
    roll = df["points"].rolling(window, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    res_color = {"W": SHOT_COLORS["goal"], "D": "#e8a200", "L": ACCENT_COLOR}
    ax.bar(x, df["points"], color=[res_color.get(r, MUTED_COLOR) for r in df["result"]],
           alpha=0.35, width=0.7, zorder=1)
    ax.plot(x, roll, color=TEXT_COLOR, lw=2.6, zorder=3,
            label=f"Media móvil {window} partidos")
    ax.scatter(x, roll, color=TEXT_COLOR, s=28, zorder=4)
    ax.axhline(1.0, color=MUTED_COLOR, ls=":", lw=1, zorder=0)

    labels = [f"{r.opponent[:9]}\n{'L' if r.venue == 'Local' else 'V'} "
              f"{int(r.chaco_goals)}-{int(r.rival_goals)}"
              for r in df.itertuples()]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=6.5, color=TEXT_COLOR)
    ax.set_ylim(0, 3.2)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_ylabel("Puntos por partido", color=TEXT_COLOR)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.6, zorder=0)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.set_title(title or f"Forma Reciente (rolling {window}) – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=12)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Local vs Visitante ──────────────────────────────────────────────────────

def plot_home_away_panel(season_df, season="", title=None, save_path=None):
    """
    Panel comparado Local vs Visitante: puntos por partido, goles a favor/contra
    por partido y xG a favor/contra por partido. Espera columnas de
    build_season_table + match_summary (points, chaco_goals, rival_goals, xg).
    """
    if season_df is None or season_df.empty or "venue" not in season_df.columns:
        return None
    df = season_df.copy()

    def agg(v):
        s = df[df["venue"] == v]
        n = max(len(s), 1)
        d = {"n": len(s),
             "pts": s["points"].sum() / n,
             "gf": s["chaco_goals"].sum() / n,
             "ga": s["rival_goals"].sum() / n,
             "rec": _venue_record_str(s)}
        d["xgf"] = s["chaco_xg"].sum() / n if "chaco_xg" in s else None
        d["xga"] = s["rival_xg"].sum() / n if "rival_xg" in s else None
        return d

    L, V = agg("Local"), agg("Visitante")
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.5))
    fig.patch.set_facecolor(BG_COLOR)

    def _bars(ax, title_txt, pairs, colors):
        xpos = np.arange(len(pairs))
        vals = [p[1] for p in pairs]
        bars = ax.bar(xpos, vals, color=colors, width=0.6, alpha=0.9)
        ax.set_xticks(xpos)
        ax.set_xticklabels([p[0] for p in pairs], fontsize=9, color=TEXT_COLOR)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}",
                    ha="center", va="bottom", fontsize=9, color=TEXT_COLOR,
                    fontweight="bold")
        ax.set_facecolor(BG_COLOR)
        ax.set_title(title_txt, color=TEXT_COLOR, fontsize=11, fontweight="bold")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRID_COLOR)
        ax.tick_params(colors=TEXT_COLOR)
        ax.grid(axis="y", color=GRID_COLOR, alpha=0.6)
        ax.margins(y=0.18)

    _bars(axes[0], "Puntos por partido",
          [(f"Local\n{L['rec']}", L["pts"]), (f"Visitante\n{V['rec']}", V["pts"])],
          [ACCENT_COLOR, RIVAL_COLOR])
    _bars(axes[1], "Goles por partido",
          [("GF Local", L["gf"]), ("GC Local", L["ga"]),
           ("GF Visit.", V["gf"]), ("GC Visit.", V["ga"])],
          [SHOT_COLORS["goal"], ACCENT_COLOR, SHOT_COLORS["goal"], ACCENT_COLOR])
    if L["xgf"] is not None:
        _bars(axes[2], "xG por partido",
              [("xGF Local", L["xgf"]), ("xGC Local", L["xga"]),
               ("xGF Visit.", V["xgf"]), ("xGC Visit.", V["xga"])],
              [SHOT_COLORS["goal"], ACCENT_COLOR, SHOT_COLORS["goal"], ACCENT_COLOR])
    else:
        axes[2].axis("off")

    fig.suptitle(title or f"Local vs Visitante – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold")
    plt.tight_layout(rect=(0, 0, 1, 0.95))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def _venue_record_str(sub):
    if sub is None or sub.empty:
        return "0-0-0"
    w = (sub["result"] == "W").sum()
    d = (sub["result"] == "D").sum()
    l = (sub["result"] == "L").sum()
    return f"{w}-{d}-{l}"


# ─── Disciplina acumulada ────────────────────────────────────────────────────

def plot_discipline(player_df, season="", suspension_at=5, title=None, save_path=None):
    """
    Disciplina acumulada: amarillas y rojas por jugador. Marca a los que están
    cerca de la suspensión por acumulación (a 1 amarilla del corte). Espera el df
    de season_player_stats (columnas 'player', 'amarillas', 'rojas', 'partidos').
    """
    if player_df is None or player_df.empty or "amarillas" not in player_df.columns:
        return None
    df = player_df.copy()
    df["amarillas"] = pd.to_numeric(df["amarillas"], errors="coerce").fillna(0)
    df["rojas"] = pd.to_numeric(df["rojas"], errors="coerce").fillna(0)
    df["carga"] = df["amarillas"] + df["rojas"] * 3
    df = df[df["carga"] > 0].sort_values("carga").reset_index(drop=True)
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(11, max(4, 0.42 * len(df) + 1.5)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    y = np.arange(len(df))

    ax.barh(y, df["amarillas"], color="#e8a200", alpha=0.9, label="Amarillas")
    ax.barh(y, df["rojas"], left=df["amarillas"], color=ACCENT_COLOR, alpha=0.95,
            label="Rojas")

    near = suspension_at - 1
    for yi, r in zip(y, df.itertuples()):
        txt = f"{int(r.amarillas)}A"
        if r.rojas:
            txt += f" · {int(r.rojas)}R"
        risk = r.amarillas >= near and r.amarillas % suspension_at == near
        if risk:
            txt += "  ⚠ a 1 de suspensión"
        ax.text(r.amarillas + r.rojas + 0.08, yi, txt, va="center",
                fontsize=8.5, color=ACCENT_COLOR if risk else TEXT_COLOR,
                fontweight="bold" if risk else "normal")

    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.player}  ({int(r.partidos)}pj)" for r in df.itertuples()],
                       fontsize=8.5, color=TEXT_COLOR)
    ax.set_xlabel("Tarjetas", color=TEXT_COLOR)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(axis="x", color=GRID_COLOR, alpha=0.6)
    ax.margins(x=0.18)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    ax.set_title(title or f"Disciplina Acumulada – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=12)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Calendario de carga (minutos + descanso) ────────────────────────────────

def plot_load_calendar(matrix_df, meta_df, season="", title=None, save_path=None):
    """
    Mapa de calor de minutos por jugador a lo largo del calendario. Fila superior
    con los días de descanso entre fechas (rojo = poco descanso). Espera la salida
    de analysis.season.load_calendar.
    """
    if matrix_df is None or matrix_df.empty:
        return None
    data = matrix_df.values
    players = matrix_df.index.tolist()
    labels = matrix_df.columns.tolist()

    fig, ax = plt.subplots(figsize=(max(11, 0.62 * len(labels) + 3),
                                    max(5, 0.42 * len(players) + 2)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    cmap = plt.get_cmap("Reds")
    im = ax.imshow(data, aspect="auto", cmap=cmap, vmin=0, vmax=90)
    for i in range(len(players)):
        for j in range(len(labels)):
            v = data[i, j]
            if v > 0:
                ax.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=6.5,
                        color="white" if v > 55 else TEXT_COLOR)

    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=90, fontsize=6.5, color=TEXT_COLOR)
    ax.set_yticks(np.arange(len(players)))
    ax.set_yticklabels(players, fontsize=8, color=TEXT_COLOR)
    ax.set_xticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(players), 1), minor=True)
    ax.grid(which="minor", color=BG_COLOR, linewidth=2)
    ax.tick_params(which="minor", length=0)

    # Días de descanso arriba de cada columna
    if meta_df is not None and "rest_days" in meta_df.columns:
        rest = dict(zip(meta_df["label"], meta_df["rest_days"]))
        for j, lab in enumerate(labels):
            rd = rest.get(lab)
            if rd is not None and not pd.isna(rd):
                col = ACCENT_COLOR if rd <= 3 else (MUTED_COLOR if rd <= 5 else SHOT_COLORS["goal"])
                ax.text(j, -0.75, f"{int(rd)}d", ha="center", va="center",
                        fontsize=6.5, color=col, fontweight="bold")
        ax.text(-0.6, -0.75, "descanso:", ha="right", va="center", fontsize=7,
                color=TEXT_COLOR, style="italic")

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Minutos jugados", color=TEXT_COLOR, fontsize=9)
    cbar.ax.tick_params(colors=TEXT_COLOR)
    ax.set_title(title or f"Calendario de Carga – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=22)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Red de asistencias ──────────────────────────────────────────────────────

def plot_assists_network(nodes_df, edges_df, season="", title=None, save_path=None):
    """
    Red de asistencias dirigida: asistente → goleador. Nodo ∝ participación en
    goles (goles + asistencias), grosor de la flecha = cantidad de goles
    conectados por esa dupla. Sale de analysis.season.assists_network.
    """
    import networkx as nx

    if nodes_df is None or nodes_df.empty:
        return None
    part = {r["player"]: r["goals"] + r["assists"] for _, r in nodes_df.iterrows()}
    G = nx.DiGraph()
    G.add_nodes_from(part.keys())
    if edges_df is not None and not edges_df.empty:
        for _, r in edges_df.iterrows():
            if r["assister"] in part and r["scorer"] in part:
                G.add_edge(r["assister"], r["scorer"], count=r["count"])

    fig, ax = plt.subplots(figsize=(12, 11))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")
    ax.set_aspect("equal")

    # Layout circular con ORDEN que reduce cruces: dentro de cada componente
    # conexa se usa ordenamiento espectral (nodos conectados quedan contiguos),
    # y las componentes se disponen una al lado de la otra sobre el círculo.
    UG = G.to_undirected()
    order = []
    for comp in sorted(nx.connected_components(UG), key=len, reverse=True):
        sub = UG.subgraph(comp)
        if len(comp) > 2 and sub.number_of_edges():
            try:
                order += list(nx.spectral_ordering(sub))
            except Exception:
                order += list(comp)
        else:
            order += list(comp)
    n = len(order)
    ang = {node: (np.pi / 2 - i * 2 * np.pi / n) for i, node in enumerate(order)}
    pos = {node: (np.cos(a), np.sin(a)) for node, a in ang.items()}

    maxpart = max(part.values()) or 1
    goals = dict(zip(nodes_df["player"], nodes_df["goals"]))
    node_sizes = [900 + 3400 * (part[node] / maxpart) for node in G.nodes()]

    if G.number_of_edges():
        cnt = np.array([G[u][v]["count"] for u, v in G.edges()], dtype=float)
        widths = 1.4 + 4.2 * (cnt / (cnt.max() or 1))
        nx.draw_networkx_edges(
            G, pos, ax=ax, width=widths, edge_color=RIVAL_COLOR, alpha=0.5,
            arrows=True, arrowstyle="-|>", arrowsize=15,
            connectionstyle="arc3,rad=0.13", node_size=node_sizes)

    # color por goles: quien más convierte, más rojo
    maxg = max(goals.values()) or 1
    cmap = plt.get_cmap("YlOrRd")
    node_colors = [cmap(0.25 + 0.7 * goals.get(node, 0) / maxg) for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                           node_color=node_colors, edgecolors="white",
                           linewidths=1.6, alpha=0.97)

    # Etiquetas radiales, por fuera del círculo (no tapan los nodos ni las flechas)
    for node in G.nodes():
        a = ang[node]
        ca, sa = np.cos(a), np.sin(a)
        ha = "left" if ca > 0.25 else ("right" if ca < -0.25 else "center")
        va = "bottom" if sa > 0.25 else ("top" if sa < -0.25 else "center")
        g_ = int(goals.get(node, 0))
        ax.text(1.28 * ca, 1.28 * sa,
                f"{node.split()[-1]}\n{g_}G·{part[node] - g_}A",
                ha=ha, va=va, fontsize=8.5, fontweight="bold", color=TEXT_COLOR,
                linespacing=1.1)

    ax.set_xlim(-2.0, 2.0)
    ax.set_ylim(-1.8, 1.8)
    ax.set_title(title or f"Red de Asistencias – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold")
    fig.text(0.5, 0.02, "Flecha: asistente → goleador (grosor ∝ nº de goles)  ·  "
             "nodo ∝ participación en goles  ·  color ∝ goles convertidos",
             ha="center", fontsize=9, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Amenaza por tipo de jugada ──────────────────────────────────────────────

def plot_threat_by_situation(df, season="", title=None, save_path=None):
    """
    xG y goles a favor vs en contra según el tipo de jugada (juego abierto,
    pelota parada, córner...). Dos paneles: xG (izq) y goles (der). Verde =
    a favor, rojo = en contra. Sale de analysis.season.threat_by_situation.
    """
    if df is None or df.empty:
        return None
    d = df.copy()
    cats = d["situation"].tolist()
    y = np.arange(len(cats))
    fig, axes = plt.subplots(1, 2, figsize=(14, max(4, 0.6 * len(cats) + 2)),
                             sharey=True)
    fig.patch.set_facecolor(BG_COLOR)
    h = 0.38

    def _panel(ax, col_for, col_against, ttl, fmt):
        ax.set_facecolor(BG_COLOR)
        ax.barh(y + h / 2, d[col_for], height=h, color=SHOT_COLORS["goal"],
                label="A favor", alpha=0.9)
        ax.barh(y - h / 2, d[col_against], height=h, color=ACCENT_COLOR,
                label="En contra", alpha=0.9)
        for yi, (vf, va) in enumerate(zip(d[col_for], d[col_against])):
            if vf:
                ax.text(vf, yi + h / 2, " " + fmt(vf), va="center", fontsize=8,
                        color=TEXT_COLOR)
            if va:
                ax.text(va, yi - h / 2, " " + fmt(va), va="center", fontsize=8,
                        color=TEXT_COLOR)
        ax.set_title(ttl, color=TEXT_COLOR, fontsize=12, fontweight="bold")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRID_COLOR)
        ax.tick_params(colors=TEXT_COLOR)
        ax.grid(axis="x", color=GRID_COLOR, alpha=0.6)
        ax.margins(x=0.15)

    _panel(axes[0], "xg_for", "xg_against", "xG por tipo de jugada",
           lambda v: f"{v:.1f}")
    _panel(axes[1], "goals_for", "goals_against", "Goles por tipo de jugada",
           lambda v: f"{int(v)}")
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(cats, fontsize=9.5, color=TEXT_COLOR)
    axes[0].invert_yaxis()
    axes[1].legend(loc="lower right", frameon=False, fontsize=9)

    fig.suptitle(title or f"Amenaza por Tipo de Jugada – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold")
    plt.tight_layout(rect=(0, 0, 1, 0.95))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── xG según estado del marcador ────────────────────────────────────────────

def plot_xg_by_score_state(df, season="", title=None, save_path=None):
    """
    xG por 90' a favor vs en contra según el estado del marcador (ganando /
    empatando / perdiendo), con los minutos jugados en cada estado. Sale de
    analysis.season.xg_by_score_state.
    """
    if df is None or df.empty:
        return None
    d = df.copy()
    x = np.arange(len(d))
    w = 0.38
    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    b1 = ax.bar(x - w / 2, d["xg_for_p90"], width=w, color=SHOT_COLORS["goal"],
                label="xG generado /90'", alpha=0.9)
    b2 = ax.bar(x + w / 2, d["xg_against_p90"], width=w, color=ACCENT_COLOR,
                label="xG concedido /90'", alpha=0.9)
    for b in list(b1) + list(b2):
        v = b.get_height()
        if v:
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}", ha="center",
                    va="bottom", fontsize=9, color=TEXT_COLOR, fontweight="bold")

    labels = [f"{r.state}\n({r.minutes:.0f}′  ·  {int(r.goals_for)}-{int(r.goals_against)})"
              for r in d.itertuples()]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, color=TEXT_COLOR)
    ax.set_ylabel("xG por 90'", color=TEXT_COLOR)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.6)
    ax.margins(y=0.15)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.set_title(title or f"xG según Estado del Marcador – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=12)
    fig.text(0.5, 0.005, "Minutos en cada estado y goles a favor-en contra entre "
             "paréntesis", ha="center", fontsize=8.5, color=MUTED_COLOR,
             style="italic")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Toques en último tercio / área rival ────────────────────────────────────

def plot_final_third_touches(df, season="", title=None, save_path=None):
    """
    Toques por jugador de Chaco en el último tercio, separando los que caen dentro
    del área rival. Barra apilada horizontal con el % del total de toques del
    jugador que llegan al último tercio. Sale de analysis.season.final_third_touches.
    """
    if df is None or df.empty:
        return None
    d = df.iloc[::-1].reset_index(drop=True)  # el mayor arriba
    y = np.arange(len(d))
    resto = (d["final_third"] - d["box"]).clip(lower=0)
    fig, ax = plt.subplots(figsize=(11, max(4, 0.5 * len(d) + 1.5)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    ax.barh(y, resto, color="#f0a58a", label="Último tercio (fuera del área)",
            alpha=0.95)
    ax.barh(y, d["box"], left=resto, color=ACCENT_COLOR, label="Dentro del área",
            alpha=0.95)
    for yi, r in zip(y, d.itertuples()):
        ax.text(r.final_third, yi, f"  {int(r.final_third)}  ·  {r.pct_final_third:.0f}% de sus toques",
                va="center", fontsize=8.5, color=TEXT_COLOR)

    ax.set_yticks(y)
    ax.set_yticklabels(d["player"], fontsize=9, color=TEXT_COLOR)
    ax.set_xlabel("Toques en el último tercio", color=TEXT_COLOR)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(axis="x", color=GRID_COLOR, alpha=0.6)
    ax.margins(x=0.22)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    ax.set_title(title or f"Participación en Último Tercio – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=12)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Cadena de Markov del estado del marcador ────────────────────────────────

def plot_markov_transitions(matrix_df, transitions_df=None, season="",
                            late_minute=70, title=None, save_path=None):
    """
    Matriz de transición de la cadena de Markov del estado del marcador:
    P[i,j] = probabilidad de que, la próxima vez que se mueva el marcador,
    se pase del estado i al j. Fila = estado de partida (normalizada a que
    sume 1; fila vacía = nunca se salió de ese estado en la temporada).
    Sale de analysis.season.markov_game_state.
    """
    order = ["S--", "S-", "S0", "S+", "S++"]
    m = matrix_df.reindex(index=order, columns=order).fillna(0.0)

    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    fig.patch.set_facecolor(BG_COLOR)
    im = ax.imshow(m.values, cmap="YlOrRd", vmin=0, vmax=1)

    ax.set_xticks(range(len(order)))
    ax.set_yticks(range(len(order)))
    ax.set_xticklabels(order, color=TEXT_COLOR, fontsize=11)
    ax.set_yticklabels(order, color=TEXT_COLOR, fontsize=11)
    ax.set_xlabel("Estado siguiente", color=TEXT_COLOR, fontsize=10)
    ax.set_ylabel("Estado de partida", color=TEXT_COLOR, fontsize=10)

    for i in range(len(order)):
        for j in range(len(order)):
            v = m.values[i, j]
            if v <= 0:
                continue
            ax.text(j, i, f"{v:.0%}", ha="center", va="center",
                    color="white" if v > 0.55 else TEXT_COLOR,
                    fontsize=11, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Probabilidad", color=TEXT_COLOR, fontsize=9)
    cbar.ax.tick_params(colors=TEXT_COLOR)

    ax.set_title(title or f"Cadena de Markov del Marcador – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=14)

    caption = "Cada celda = prob. de pasar de un estado a otro en el próximo gol del partido"
    if transitions_df is not None and not transitions_df.empty:
        leads = transitions_df[transitions_df["from_state"] == "S+"]
        if len(leads):
            blown = leads[leads["to_state"] == "S0"]
            late_blown = blown[blown["minute"] >= late_minute]
            caption += (f"  ·  yendo ganando x1: se diluyó {len(blown)}/{len(leads)} veces "
                       f"({100*len(blown)/len(leads):.0f}%), {len(late_blown)} después del "
                       f"{int(late_minute)}'")
    fig.text(0.5, 0.015, caption, ha="center", fontsize=8.5, color=MUTED_COLOR,
             style="italic", wrap=True)
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Núcleo táctico (centralidad de eigenvector) ─────────────────────────────

def plot_eigen_centrality(nodes_df, season="", top_n=20, title=None, save_path=None):
    """
    Minutos vs. centralidad de eigenvector: identifica el "núcleo táctico"
    del plantel. Un jugador arriba-izquierda (pocos minutos, alta
    centralidad) potencia mucho al equipo cada vez que juega, aunque no sea
    titular fijo — "inamovible táctico" aunque su estadística tradicional no
    lo muestre. Sale de analysis.season.eigenvector_centrality_network.
    """
    df = nodes_df[nodes_df["eigen_centrality"] > 0].sort_values(
        "eigen_centrality", ascending=False).head(top_n).copy()
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    ax.scatter(df["minutes"], df["eigen_centrality"], s=190, color=ACCENT_COLOR,
              edgecolors="white", linewidths=1.4, alpha=0.92, zorder=3)
    for _, r in df.iterrows():
        ax.annotate(r["player_name"].split()[-1], (r["minutes"], r["eigen_centrality"]),
                    fontsize=8.8, color=TEXT_COLOR, xytext=(6, 5),
                    textcoords="offset points", fontweight="bold")

    ax.set_xlabel("Minutos jugados en la temporada", color=TEXT_COLOR, fontsize=10)
    ax.set_ylabel("Centralidad de eigenvector (núcleo del equipo)", color=TEXT_COLOR, fontsize=10)
    ax.grid(True, color=GRID_COLOR, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.margins(x=0.12, y=0.12)

    ax.set_title(title or f"Núcleo Táctico del Plantel – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=14)
    fig.text(0.5, 0.01, "Arriba-izquierda = rinde muy por encima de sus minutos "
             "(potencia al equipo cuando juega, aunque sume pocos partidos)",
             ha="center", fontsize=9, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Entropía espacial de Shannon del shotmap ────────────────────────────────

def plot_shot_entropy(entropy_stats, season="", team_label="Chaco For Ever",
                      title=None, save_path=None):
    """
    Grilla de concentración de peligro (% del xG total) en el último tercio,
    con la entropía de Shannon como resumen: alta = ataque repartido e
    impredecible; baja = el equipo siempre genera desde el mismo sector, algo
    que el técnico rival neutraliza rápido. Sale de analysis.season.shot_entropy.
    """
    zone_xg = entropy_stats.get("zone_xg")
    if zone_xg is None or zone_xg.empty:
        return None

    bins = entropy_stats["bins"]
    x_min = entropy_stats["x_min"]
    x_edges = np.linspace(x_min, 100.0, bins + 1)
    y_edges = np.linspace(0.0, 100.0, bins + 1)

    x_plot_vals = [100 - (x_edges[int(r.x_bin)] + x_edges[int(r.x_bin) + 1]) / 2
                  for r in zone_xg.itertuples()]
    y_lo = max(0.0, min(x_plot_vals) - 9) if x_plot_vals else 0.0

    fig, ax_pitch = plt.subplots(figsize=(8, 10))
    fig.patch.set_facecolor(BG_COLOR)
    # Pitch completo (no half=True): coord_x mide distancia AL ARCO, así que
    # tiros lejanos caen bien por debajo de x=50 y half=True los recortaría.
    pitch = VerticalPitch(pitch_type="opta", pitch_color=PITCH_BG,
                          linewidth=1.5, line_color="#8f8f86")
    pitch.draw(ax=ax_pitch)
    ax_pitch.set_facecolor(PITCH_BG)
    ax_pitch.set_ylim(y_lo, 103)

    cmap = plt.get_cmap("Reds")
    max_pct = float(zone_xg["pct"].max())
    for _, r in zone_xg.iterrows():
        xb, yb, pct = int(r["x_bin"]), int(r["y_bin"]), float(r["pct"])
        xc = (x_edges[xb] + x_edges[xb + 1]) / 2
        yc = (y_edges[yb] + y_edges[yb + 1]) / 2
        x_plot, y_plot = 100 - xc, 100 - yc
        frac = (pct / max_pct) if max_pct else 0.0
        color = cmap(0.25 + 0.75 * frac)
        size = 700 + 5000 * frac
        pitch.scatter(x_plot, y_plot, s=size, c=[color], edgecolor="white",
                      linewidth=1.2, alpha=0.92, ax=ax_pitch, zorder=2)
        if pct * 100 >= 1:
            pitch.text(x_plot, y_plot, f"{pct * 100:.0f}%", ax=ax_pitch,
                       color="white" if frac > 0.4 else TEXT_COLOR,
                       fontsize=9.5, fontweight="bold", ha="center", va="center", zorder=3)

    ent = entropy_stats["entropy"]
    pct_max = entropy_stats["pct_of_max"]
    if pct_max >= 65:
        lectura = "ataque repartido e impredecible"
    elif pct_max < 45:
        lectura = "ataque leíble, concentrado en pocos sectores"
    else:
        lectura = "hay sectores preferidos, pero no exclusivos"

    ax_pitch.set_title(title or f"Entropía Espacial del Ataque – {team_label}"
                       f"{'  ' + str(season) if season else ''}",
                       fontsize=15, fontweight="bold", color=TEXT_COLOR, pad=14)
    fig.text(0.5, 0.02, f"Entropía de Shannon: {ent} / {entropy_stats['max_entropy']} bits "
             f"({pct_max}% del máximo) — {lectura}  ·  n={entropy_stats['n_shots']} tiros",
             ha="center", fontsize=9.5, color=MUTED_COLOR, style="italic", wrap=True)
    plt.tight_layout(rect=(0, 0.05, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Riesgo de colapso defensivo (Cox Proportional Hazards) ──────────────────

def plot_defensive_hazard(cph, season="", title=None, save_path=None):
    """
    Forest plot de los Hazard Ratios (exp(coef)) del modelo de riesgo de
    colapso defensivo: HR > 1 = a más [covariable], más rápido llega el
    primer remate rival peligroso (xG alto). Sale de
    analysis.season.fit_defensive_hazard_model.
    """
    summ = cph.summary.copy()
    labels_map = {
        "defensive_fatigue": "Fatiga defensiva\n(min. últimos 14 días)",
        "momentum_at_risk": "Momentum del rival\nen el instante de riesgo",
    }
    summ = summ.rename(index=labels_map)

    fig, ax = plt.subplots(figsize=(8.5, 3.5 + 0.9 * len(summ)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    y = np.arange(len(summ))
    hr = summ["exp(coef)"].values
    lo = summ["exp(coef) lower 95%"].values
    hi = summ["exp(coef) upper 95%"].values

    ax.errorbar(hr, y, xerr=[hr - lo, hi - hr], fmt="o", color=ACCENT_COLOR,
               ecolor=MUTED_COLOR, elinewidth=2, capsize=4, markersize=9, zorder=3)
    ax.axvline(1.0, color=TEXT_COLOR, linestyle="--", linewidth=1, alpha=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(summ.index, color=TEXT_COLOR, fontsize=10)
    ax.set_xlabel("Hazard Ratio (exp(coef))", color=TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(True, axis="x", color=GRID_COLOR, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.margins(y=0.35)

    for i, (h, p) in enumerate(zip(hr, summ["p"])):
        sig = "*" if p < 0.05 else ""
        ax.text(h, i + 0.22, f"HR={h:.2f}{sig}  p={p:.3f}", ha="center",
                fontsize=8.5, color=TEXT_COLOR)

    ax.set_title(title or f"Riesgo de Colapso Defensivo (Cox PH) – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=14, fontweight="bold", pad=14)
    fig.text(0.5, 0.01, "HR > 1 = acelera el primer remate rival peligroso (xG≥0.15)  ·  "
             "* = significativo (p<0.05)  ·  muestra chica: leer como señal, no certeza",
             ha="center", fontsize=8.3, color=MUTED_COLOR, style="italic", wrap=True)
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Goles por ventana de tiempo ─────────────────────────────────────────────

def plot_goals_by_time_window(df, season="", title=None, save_path=None):
    """
    Goles a favor y en contra de Chaco por ventana de tiempo del partido:
    en qué minutos el equipo convierte y en cuáles le hacen goles. Complementa
    la cadena de Markov del marcador (esa mide el ESTADO; esta mide el
    MOMENTO). Sale de analysis.season.goals_by_time_window.
    """
    if df is None or df.empty or (df["goals_for"].sum() + df["goals_against"].sum()) == 0:
        return None

    x = np.arange(len(df))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    b1 = ax.bar(x - width / 2, df["goals_for"], width, color=ACCENT_COLOR, label="A favor")
    b2 = ax.bar(x + width / 2, df["goals_against"], width, color=RIVAL_COLOR, label="En contra")

    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.05, f"{int(h)}",
                        ha="center", fontsize=9.5, fontweight="bold", color=TEXT_COLOR)

    ax.set_xticks(x)
    ax.set_xticklabels(df["window"], color=TEXT_COLOR, fontsize=10)
    ax.set_ylabel("Goles", color=TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=TEXT_COLOR)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.6)
    ax.margins(y=0.15)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)

    ax.set_title(title or f"Goles por Ventana de Tiempo – Chaco For Ever"
                 f"{'  ' + str(season) if season else ''}",
                 color=TEXT_COLOR, fontsize=15, fontweight="bold", pad=14)

    cap = "En qué minutos convierte y en cuáles recibe el equipo"
    if df["goals_for"].sum() > 0:
        peak_for = df.loc[df["goals_for"].idxmax()]
        cap += f"  ·  hace más goles en {peak_for['window']} ({int(peak_for['goals_for'])})"
    if df["goals_against"].sum() > 0:
        peak_against = df.loc[df["goals_against"].idxmax()]
        cap += f"  ·  recibe más en {peak_against['window']} ({int(peak_against['goals_against'])})"
    fig.text(0.5, 0.01, cap, ha="center", fontsize=9, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.05, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig
