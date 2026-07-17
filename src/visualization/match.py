"""
match.py (visualization)
========================
Gráficos específicos para el análisis post-partido:
  - Momentum
  - Posiciones promedio (formación táctica)
  - Grid de heatmaps por jugador
  - Timeline de incidentes
  - Ratings de jugadores
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from mplsoccer import Pitch, VerticalPitch

from src.visualization.season import (
    save_fig, BG_COLOR, TEXT_COLOR, ACCENT_COLOR, RIVAL_COLOR,
    MUTED_COLOR, GRID_COLOR, PITCH_BG, PITCH_LINE, HEAT_CMAP,
)


# ─── Momentum ────────────────────────────────────────────────────────────────

def plot_momentum(df_momentum, is_home=True, match_label="", save_path=None):
    """
    Curva de momentum del partido. Área verde = Chaco dominando.
    df_momentum debe tener columnas 'minute' y 'value'.
    """
    df = df_momentum.copy()
    col_min = "minute" if "minute" in df.columns else df.columns[0]
    col_val = "value"  if "value"  in df.columns else df.columns[1]
    df[col_min] = pd.to_numeric(df[col_min], errors="coerce")
    df[col_val] = pd.to_numeric(df[col_val], errors="coerce")
    df = df.dropna().sort_values(col_min)

    # Si Chaco es visitante, el momentum positivo es del rival → invertimos
    if not is_home:
        df[col_val] = -df[col_val]

    fig, ax = plt.subplots(figsize=(14, 4))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    x = df[col_min].values
    y = df[col_val].values

    ax.fill_between(x, y, 0, where=(y >= 0), alpha=0.85, color=ACCENT_COLOR, label="Chaco For Ever")
    ax.fill_between(x, y, 0, where=(y <  0), alpha=0.85, color=RIVAL_COLOR,  label="Rival")
    ax.axhline(0, color=TEXT_COLOR, linewidth=0.8, alpha=0.6)

    # Rejilla vertical cada 10' + línea de medio tiempo
    for m in range(0, int(x.max()) + 1, 10):
        ax.axvline(m, color=GRID_COLOR, linewidth=0.8, zorder=0)
    if x.max() > 45:
        ax.axvline(45, color=MUTED_COLOR, linewidth=1, linestyle=":", alpha=0.8, label="HT")

    ax.set_xlim(x.min(), x.max())
    ax.set_xlabel("Minuto", color=TEXT_COLOR, fontsize=10)
    ax.set_title(f"Momentum del Partido{' – ' + match_label if match_label else ''}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold")
    ax.tick_params(colors=TEXT_COLOR)
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.legend(facecolor=BG_COLOR, labelcolor=TEXT_COLOR, fontsize=9, loc="upper right")

    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Posiciones promedio (formación) ─────────────────────────────────────────

def _subs_for_side(df_incidents, focus_side):
    """Lista de (entra, sale) de los cambios del equipo en focus_side."""
    if (df_incidents is None or df_incidents.empty
            or "type" not in df_incidents.columns):
        return []
    want_home = (focus_side == "home")
    pairs = []
    for _, r in df_incidents[df_incidents["type"] == "substitution"].iterrows():
        if bool(r.get("is_home", True)) != want_home:
            continue
        pin = str(r.get("player") or "").strip()
        desc = str(r.get("description") or "")
        pout = desc.split("OUT:")[1].strip() if "OUT:" in desc else ""
        if pin:
            pairs.append((pin, pout))
    return pairs


def _plot_avg_positions_single(df_avg_pos, focus_side, focus_color, team_label,
                               df_lineup=None, subs=None, match_label="",
                               save_path=None):
    """
    Posiciones promedio de UN equipo. Titular = círculo lleno; suplente que
    entró = círculo hueco (relleno blanco, borde del color). Flecha punteada
    del que SALE al que ENTRA para ver los cambios. Nombres con fondo para
    reducir el solapamiento (↑ entró, ↓ salió).
    """
    if df_avg_pos is None or df_avg_pos.empty:
        return None

    df = df_avg_pos[df_avg_pos["team_side"] == focus_side].copy()
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(9, 12))
    fig.patch.set_facecolor(BG_COLOR)
    pitch = Pitch(pitch_type="opta", pitch_color=PITCH_BG, line_color=PITCH_LINE,
                  linewidth=1.2)
    pitch.draw(ax=ax)
    ax.set_facecolor(PITCH_BG)

    starters = set()
    if df_lineup is not None and not df_lineup.empty:
        s = df_lineup[(df_lineup["team_side"] == focus_side) &
                      (df_lineup["is_starter"] == True)]
        starters = set(s["player_name"].tolist())

    pos = {}
    for _, row in df.iterrows():
        x = pd.to_numeric(row.get("average_x"), errors="coerce")
        y = pd.to_numeric(row.get("average_y"), errors="coerce")
        name = row.get("player_name", "")
        if pd.notna(x) and pd.notna(y) and name:
            pos[name] = (float(x), float(y))

    subs = subs or []
    sub_in = {pin for pin, _ in subs}
    sub_out = {pout for _, pout in subs if pout}

    # Flechas de cambio: del que SALE → al que ENTRA
    for pin, pout in subs:
        if pin in pos and pout in pos:
            (x0, y0), (x1, y1) = pos[pout], pos[pin]
            ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=3,
                        arrowprops=dict(arrowstyle="-|>", color="#444444",
                                        linestyle=(0, (4, 2)), linewidth=1.7,
                                        shrinkA=10, shrinkB=10, alpha=0.9))

    for name, (x, y) in pos.items():
        entro, salio = name in sub_in, name in sub_out
        if entro:                       # suplente que entró → hueco
            face, edge, size, lw = "white", focus_color, 300, 2.4
        else:                           # titular (o quien terminó) → lleno
            face, edge, size, lw = focus_color, "white", 420, 1.3
        pitch.scatter(x, y, s=size, c=face, edgecolors=edge,
                      linewidth=lw, alpha=0.97, ax=ax, zorder=4)
        short = name.split()[-1] if name else ""
        mark = " ↑" if entro else (" ↓" if salio else "")
        pitch.text(x, y + 4.2, short + mark, ax=ax, color=TEXT_COLOR,
                   fontsize=8, fontweight="bold", ha="center", va="bottom",
                   zorder=6, bbox=dict(boxstyle="round,pad=0.15", fc=BG_COLOR,
                                       ec="none", alpha=0.7))

    legend_handles = [
        Line2D([0], [0], marker="o", color="w", label=f"{team_label} (titular)",
               markerfacecolor=focus_color, markersize=13, markeredgecolor="white"),
        Line2D([0], [0], marker="o", color="w", label="Suplente (entró ↑)",
               markerfacecolor="white", markeredgecolor=focus_color,
               markersize=12, markeredgewidth=2),
        Line2D([0], [0], color="#444444", linestyle=(0, (4, 2)), linewidth=1.7,
               label="Sale → Entra"),
    ]
    ax.legend(handles=legend_handles, facecolor=BG_COLOR, labelcolor=TEXT_COLOR,
              fontsize=9, loc="upper right")
    ax.set_title(f"Posiciones Promedio – {team_label}"
                 f"{'  (' + match_label + ')' if match_label else ''}",
                 color=TEXT_COLOR, fontsize=12, fontweight="bold", pad=8)

    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_average_positions(df_avg_pos, df_lineup=None, is_home=True,
                           chaco_label="Chaco For Ever", match_label="",
                           save_path=None, df_incidents=None):
    """Posiciones promedio SOLO de Chaco For Ever (formación + cambios)."""
    chaco_side = "home" if is_home else "away"
    return _plot_avg_positions_single(
        df_avg_pos, chaco_side, ACCENT_COLOR, chaco_label, df_lineup=df_lineup,
        subs=_subs_for_side(df_incidents, chaco_side),
        match_label=match_label, save_path=save_path)


def plot_average_positions_rival(df_avg_pos, df_lineup=None, is_home=True,
                                 rival_label="Rival", match_label="",
                                 save_path=None, df_incidents=None):
    """Posiciones promedio SOLO del rival (misma estética + cambios)."""
    rival_side = "away" if is_home else "home"
    return _plot_avg_positions_single(
        df_avg_pos, rival_side, RIVAL_COLOR, rival_label, df_lineup=df_lineup,
        subs=_subs_for_side(df_incidents, rival_side),
        match_label=match_label, save_path=save_path)


# ─── Grid de heatmaps ────────────────────────────────────────────────────────

def plot_player_heatmaps_grid(df_heatmaps, players=None, n=6, is_home=True,
                               save_path=None):
    """
    Grid de heatmaps individuales. players = lista de nombres a mostrar.
    Si players=None, toma los n jugadores con más puntos en el heatmap.
    """
    if df_heatmaps is None or df_heatmaps.empty:
        return None

    chaco_side = "home" if is_home else "away"
    df = df_heatmaps[df_heatmaps["team_side"] == chaco_side].copy()
    if df.empty:
        return None

    if players is None:
        counts = df.groupby("player_name").size().nlargest(n)
        players = counts.index.tolist()

    players = players[:n]
    ncols = 3
    nrows = (len(players) + ncols - 1) // ncols
    fig, axs = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 7))
    fig.patch.set_facecolor(BG_COLOR)
    axs = np.array(axs).flatten()

    pitch = Pitch(pitch_type="opta", pitch_color=PITCH_BG, line_color=PITCH_LINE,
                  linewidth=1, line_zorder=2)

    for i, player in enumerate(players):
        ax = axs[i]
        player_data = df[df["player_name"] == player]
        x = pd.to_numeric(player_data["x"], errors="coerce").dropna()
        y = pd.to_numeric(player_data["y"], errors="coerce").dropna()

        pitch.draw(ax=ax)
        ax.set_facecolor(PITCH_BG)

        if not x.empty:
            try:
                pitch.kdeplot(x.values, y.values, ax=ax, cmap=HEAT_CMAP,
                              fill=True, levels=10, alpha=0.85, zorder=1)
            except Exception:
                pitch.scatter(x.values, y.values, s=15, c=ACCENT_COLOR,
                              alpha=0.5, ax=ax, zorder=1)

        short_name = player.split()[-1] if player else player
        ax.set_title(short_name, color=TEXT_COLOR, fontsize=10, fontweight="bold")

    for j in range(len(players), len(axs)):
        axs[j].set_visible(False)

    fig.suptitle("Heatmaps – Chaco For Ever", color=TEXT_COLOR, fontsize=13,
                 fontweight="bold", y=1.01)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Timeline de incidentes ───────────────────────────────────────────────────

def plot_incidents_timeline(df_incidents, home_name="Local", away_name="Visitante",
                             save_path=None):
    """
    Línea de tiempo del partido, estilo "lollipop": eje central de minutos,
    eventos del local arriba y del visitante abajo. Goles con marcador corrido,
    tarjetas como rectángulos (amarilla/roja) y cambios con flecha ⇅.
    """
    if df_incidents is None or df_incidents.empty:
        return None

    df = df_incidents.copy()
    df["minute"] = pd.to_numeric(df["minute"], errors="coerce")
    df = df.dropna(subset=["minute"]).sort_values("minute")
    if df.empty:
        return None

    has_score = "home_score" in df.columns and "away_score" in df.columns
    max_min = max(90, int(np.ceil(df["minute"].max() / 5.0) * 5))

    fig, ax = plt.subplots(figsize=(16, 6.5))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # Rejilla de minutos + eje central + medio tiempo
    for m in range(0, max_min + 1, 15):
        ax.axvline(m, color=GRID_COLOR, linewidth=1, zorder=0)
        ax.text(m, 0, f"{m}'", ha="center", va="center", fontsize=8,
                color=MUTED_COLOR, zorder=2,
                bbox=dict(boxstyle="round,pad=0.15", fc=BG_COLOR, ec="none"))
    ax.axhline(0, color=TEXT_COLOR, linewidth=2, alpha=0.85, zorder=1)
    ax.axvline(45, color=MUTED_COLOR, linewidth=1.2, linestyle=(0, (4, 3)),
               alpha=0.8, zorder=1)

    GOAL_C, YEL_C, RED_C, YR_C, SUB_C = "#2ca02c", "#e8b100", "#d62728", "#e8602c", "#2b6cb0"

    MIN_SEP = 5.0
    last_min = {True: -99.0, False: -99.0}
    level    = {True: 0, False: 0}

    def card(minute, y, face, edge="#333333"):
        ax.add_patch(mpatches.FancyBboxPatch(
            (minute - 0.9, y - 0.13), 1.8, 0.26,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=face, edgecolor=edge, linewidth=0.8, zorder=4,
            mutation_aspect=0.6))

    for _, row in df.iterrows():
        minute  = row["minute"]
        itype   = row.get("type", "")
        is_home = bool(row.get("is_home", True))
        player  = (row.get("player", "") or "").split()[-1] if row.get("player") else ""
        desc    = row.get("description", "") or ""
        sign    = 1 if is_home else -1

        if minute - last_min[is_home] < MIN_SEP:
            level[is_home] += 1
        else:
            level[is_home] = 0
        last_min[is_home] = minute
        y = sign * (0.6 + level[is_home] * 0.66)

        ax.plot([minute, minute], [0, y], color="#c7c7bd", linewidth=1.2, zorder=2)

        if itype == "goal":
            ax.scatter(minute, y, s=360, marker="o", color=GOAL_C,
                       edgecolors="white", linewidths=1.8, zorder=5)
            score = ""
            if has_score and pd.notna(row.get("home_score")):
                score = f"{int(row['home_score'])}-{int(row['away_score'])}  "
            og = " (e/c)" if str(desc).lower().find("owngoal") >= 0 \
                 or str(row.get("situation", "")).lower() == "own-goal" else ""
            lbl = f"{score}{player}{og}"
            lblcolor = GOAL_C
        elif itype in ("yellow", "red", "yellowRed"):
            card(minute, y, YEL_C if itype == "yellow" else
                 (RED_C if itype == "red" else YR_C))
            lbl = player
            lblcolor = TEXT_COLOR
        elif itype == "substitution":
            ax.scatter(minute, y, s=210, marker="o", color="white",
                       edgecolors=SUB_C, linewidths=2, zorder=5)
            ax.text(minute, y, "⇅", ha="center", va="center", fontsize=11,
                    color=SUB_C, fontweight="bold", zorder=6)
            player_out = ""
            if "OUT:" in desc:
                po = desc.replace("OUT: ", "").strip()
                player_out = po.split()[-1] if po else ""
            lbl = f"{player}" + (f"\n↓{player_out}" if player_out else "")
            lblcolor = SUB_C
        else:
            ax.scatter(minute, y, s=90, marker="o", color=MUTED_COLOR, zorder=4)
            lbl, lblcolor = player, TEXT_COLOR

        ax.text(minute, y + sign * 0.20, lbl, ha="center",
                va="bottom" if is_home else "top", color=lblcolor,
                fontsize=8, fontweight="bold", zorder=6, linespacing=0.95)

    top = 0.6 + max(max(level.values()), 0) * 0.66 + 0.95
    ax.set_xlim(-2, max_min + 2)
    ax.set_ylim(-top, top)
    ax.set_yticks([])
    ax.set_xticks([])

    # Nombres de equipo a la izquierda
    ax.text(-1, top * 0.6, home_name, ha="left", va="center", fontsize=12,
            fontweight="bold", color=TEXT_COLOR)
    ax.text(-1, -top * 0.6, away_name, ha="left", va="center", fontsize=12,
            fontweight="bold", color=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_visible(False)

    legend_handles = [
        Line2D([0], [0], marker="o", color="w", label="Gol",
               markerfacecolor=GOAL_C, markersize=12, markeredgecolor="white"),
        mpatches.Patch(facecolor=YEL_C, edgecolor="#333", label="Amarilla"),
        mpatches.Patch(facecolor=RED_C, edgecolor="#333", label="Roja"),
        Line2D([0], [0], marker="o", color="w", label="Cambio",
               markerfacecolor="white", markeredgecolor=SUB_C, markersize=11,
               markeredgewidth=2),
    ]
    ax.legend(handles=legend_handles, loc="lower center",
              bbox_to_anchor=(0.5, -0.06), ncol=4, frameon=False,
              fontsize=10, labelcolor=TEXT_COLOR)

    ax.set_title("Timeline del Partido", color=TEXT_COLOR, fontsize=15,
                 fontweight="bold", pad=14)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Ratings de jugadores ─────────────────────────────────────────────────────

def plot_player_ratings_match(df_player_stats, chaco_label="Chaco For Ever",
                               save_path=None):
    """
    Barras horizontales con el rating SofaScore de cada jugador de Chaco.
    """
    if df_player_stats is None or df_player_stats.empty:
        return None

    df = df_player_stats.copy()
    rating_col = "rating" if "rating" in df.columns else None
    name_col   = "player_name" if "player_name" in df.columns else "player"
    if rating_col is None:
        return None

    df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
    df = df.dropna(subset=[rating_col]).sort_values(rating_col, ascending=True)

    fig, ax = plt.subplots(figsize=(9, max(4, len(df) * 0.5)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    colors = [
        "#2ca02c" if r >= 7.5 else ("#e8a200" if r >= 6.5 else "#d62728")
        for r in df[rating_col]
    ]

    y = range(len(df))
    ax.barh(list(y), df[rating_col].values, color=colors, alpha=0.9, height=0.6)
    ax.set_yticks(list(y))
    ax.set_yticklabels(df[name_col].values, fontsize=10, color=TEXT_COLOR)
    ax.set_xlabel("Rating SofaScore", color=TEXT_COLOR, fontsize=10)
    ax.set_xlim(4, 10.5)
    ax.axvline(6.5, color=MUTED_COLOR, linewidth=0.8, linestyle="--", alpha=0.6)
    ax.axvline(7.5, color=ACCENT_COLOR, linewidth=0.8, linestyle="--", alpha=0.6)
    ax.tick_params(colors=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i, val in enumerate(df[rating_col].values):
        ax.text(val + 0.05, i, f"{val:.1f}", va="center", fontsize=9, color=TEXT_COLOR)

    ax.set_title(f"Ratings del Partido – {chaco_label}",
                 color=TEXT_COLOR, fontsize=12, fontweight="bold")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Heatmap de equipo ────────────────────────────────────────────────────────

def plot_team_heatmap(df_heatmaps, is_home=True, match_label="",
                      rival_label="Rival", save_path=None):
    """
    Mapa de calor de equipo: dos canchas lado a lado (Chaco y rival),
    agregando los puntos de todos los jugadores de cada lado.
    """
    if df_heatmaps is None or df_heatmaps.empty:
        return None

    chaco_side = "home" if is_home else "away"
    rival_side = "away" if is_home else "home"

    fig, axs = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor(BG_COLOR)

    pitch = Pitch(pitch_type="opta", pitch_color=PITCH_BG, line_color=PITCH_LINE,
                  linewidth=1.2, line_zorder=2)

    for ax, side, label, cmap, fallback in [
            (axs[0], chaco_side, "Chaco For Ever", "Reds",  ACCENT_COLOR),
            (axs[1], rival_side, rival_label,      "Blues", RIVAL_COLOR)]:
        team = df_heatmaps[df_heatmaps["team_side"] == side]
        x = pd.to_numeric(team["x"], errors="coerce").dropna()
        y = pd.to_numeric(team["y"], errors="coerce").dropna()

        pitch.draw(ax=ax)
        ax.set_facecolor(PITCH_BG)
        if not x.empty:
            try:
                pitch.kdeplot(x.values, y.values, ax=ax, cmap=cmap,
                              fill=True, levels=12, alpha=0.85, zorder=1)
            except Exception:
                pitch.scatter(x.values, y.values, s=10, c=fallback,
                              alpha=0.4, ax=ax, zorder=1)
        ax.set_title(label, color=TEXT_COLOR, fontsize=12, fontweight="bold")

    fig.suptitle(f"Mapa de Calor de Equipo{' – ' + match_label if match_label else ''}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Heatmap individual (un jugador por imagen) ──────────────────────────────

def plot_player_heatmap(df_heatmaps, player_name, is_home=True,
                        match_label="", save_path=None):
    """
    Mapa de calor de UN jugador de Chaco — para guardar una imagen por jugador.
    """
    if df_heatmaps is None or df_heatmaps.empty:
        return None

    chaco_side = "home" if is_home else "away"
    player_data = df_heatmaps[(df_heatmaps["team_side"] == chaco_side) &
                              (df_heatmaps["player_name"] == player_name)]
    if player_data.empty:
        return None

    x = pd.to_numeric(player_data["x"], errors="coerce").dropna()
    y = pd.to_numeric(player_data["y"], errors="coerce").dropna()
    if x.empty:
        return None

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor(BG_COLOR)

    pitch = Pitch(pitch_type="opta", pitch_color=PITCH_BG, line_color=PITCH_LINE,
                  linewidth=1.2, line_zorder=2)
    pitch.draw(ax=ax)
    ax.set_facecolor(PITCH_BG)

    try:
        pitch.kdeplot(x.values, y.values, ax=ax, cmap=HEAT_CMAP,
                      fill=True, levels=12, alpha=0.85, zorder=1)
    except Exception:
        pitch.scatter(x.values, y.values, s=18, c=ACCENT_COLOR,
                      alpha=0.5, ax=ax, zorder=1)

    title = f"Heatmap – {player_name}"
    if match_label:
        title += f"  ({match_label})"
    ax.set_title(title, color=TEXT_COLOR, fontsize=12, fontweight="bold")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Radios de acción (convex hulls) ─────────────────────────────────────────

def plot_action_radius(df_heatmaps, df_lineup=None, is_home=True,
                       match_label="", max_players=11, save_path=None,
                       focus="chaco", team_label=None):
    """
    Radio de acción de cada titular de un equipo: convex hull del 50% central
    de sus toques + punto en su posición media. focus='chaco' o 'rival'.
    """
    if df_heatmaps is None or df_heatmaps.empty:
        return None

    side, es_chaco = _team_side_focus(is_home, focus)
    team_label = team_label or ("Chaco For Ever" if es_chaco else "Rival")
    df = df_heatmaps[df_heatmaps["team_side"] == side].copy()
    if df.empty:
        return None

    # Titulares primero; si no hay lineup, los de más puntos
    if df_lineup is not None and not df_lineup.empty:
        starters = df_lineup[(df_lineup["team_side"] == side) &
                             (df_lineup["is_starter"] == True)]["player_name"].tolist()
        players = [p for p in starters if p in set(df["player_name"])][:max_players]
    else:
        players = df.groupby("player_name").size().nlargest(max_players).index.tolist()

    if not players:
        return None

    fig, ax = plt.subplots(figsize=(11, 7.5))
    fig.patch.set_facecolor(BG_COLOR)
    pitch = Pitch(pitch_type="opta", pitch_color=PITCH_BG, line_color=PITCH_LINE,
                  linewidth=1.2, line_zorder=2)
    pitch.draw(ax=ax)
    ax.set_facecolor(PITCH_BG)

    cmap = plt.get_cmap("tab10")
    for i, player in enumerate(players):
        pdata = df[df["player_name"] == player]
        x = pd.to_numeric(pdata["x"], errors="coerce")
        y = pd.to_numeric(pdata["y"], errors="coerce")
        pts = pd.DataFrame({"x": x, "y": y}).dropna()
        if len(pts) < 4:
            continue

        # Radio de acción = núcleo donde el jugador actuó la mitad del tiempo:
        # nos quedamos con el 50% de puntos más cercanos al centroide
        cx, cy = pts["x"].mean(), pts["y"].mean()
        dist = np.sqrt((pts["x"] - cx) ** 2 + (pts["y"] - cy) ** 2)
        core = pts[dist <= dist.quantile(0.50)]
        if len(core) < 3:
            core = pts

        color = cmap(i % 10)
        try:
            hull = pitch.convexhull(core["x"].values, core["y"].values)
            pitch.polygon(hull, ax=ax, edgecolor=color, facecolor=color,
                          alpha=0.16, linewidth=1.8, zorder=2)
        except Exception:
            pass

        pitch.scatter(cx, cy, s=220, c=[color], edgecolor="white",
                      linewidth=1.4, alpha=0.95, ax=ax, zorder=4)
        short = player.split()[-1] if player else ""
        pitch.text(cx, cy + 3.5, short, ax=ax, color=TEXT_COLOR, fontsize=8,
                   fontweight="bold", ha="center", va="bottom", zorder=5)

    ax.set_title(f"Radios de Acción – {team_label}"
                 f"{'  (' + match_label + ')' if match_label else ''}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_action_radius_rival(df_heatmaps, df_lineup=None, is_home=True,
                             rival_label="Rival", match_label="",
                             max_players=11, save_path=None):
    """Radios de acción de los titulares del RIVAL (mismo estilo)."""
    return plot_action_radius(df_heatmaps, df_lineup=df_lineup, is_home=is_home,
                              match_label=match_label, max_players=max_players,
                              save_path=save_path, focus="rival",
                              team_label=rival_label)


# ─── xG por tramos ────────────────────────────────────────────────────────────

def plot_xg_phases(df_phases, rival_label="Rival", match_label="", save_path=None):
    """
    Barras de xG por tramo de tiempo (de analysis.post_match.xg_by_phase).
    """
    if df_phases is None or df_phases.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    x = np.arange(len(df_phases))
    w = 0.38
    ax.bar(x - w / 2, df_phases["chaco_xg"], width=w, color=ACCENT_COLOR,
           alpha=0.9, label="Chaco For Ever")
    ax.bar(x + w / 2, df_phases["rival_xg"], width=w, color=RIVAL_COLOR,
           alpha=0.9, label=rival_label)

    for i, row in df_phases.iterrows():
        if row["chaco_xg"] > 0:
            ax.text(i - w / 2, row["chaco_xg"] + 0.01, f"{row['chaco_xg']:.2f}",
                    ha="center", fontsize=8, color=ACCENT_COLOR)
        if row["rival_xg"] > 0:
            ax.text(i + w / 2, row["rival_xg"] + 0.01, f"{row['rival_xg']:.2f}",
                    ha="center", fontsize=8, color=RIVAL_COLOR)

    # Separador de tiempos
    ht_idx = next((i for i, p in enumerate(df_phases["phase_start"]) if p >= 45), None)
    if ht_idx:
        ax.axvline(ht_idx - 0.5, color=MUTED_COLOR, linewidth=1, linestyle=":", alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(df_phases["phase"], color=TEXT_COLOR, fontsize=10)
    ax.set_ylabel("xG", color=TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.legend(facecolor=BG_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    ax.set_title(f"xG por Tramos{' – ' + match_label if match_label else ''}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Acciones defensivas ─────────────────────────────────────────────────────

def plot_defensive_actions(df_def, match_label="", top_n=11, save_path=None):
    """
    Barras apiladas de acciones defensivas por jugador
    (de analysis.post_match.defensive_actions_table).
    """
    if df_def is None or df_def.empty:
        return None

    df = df_def.head(top_n).iloc[::-1]  # invertir para barh
    y = np.arange(len(df))

    fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.55)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    left = np.zeros(len(df))
    for col, label, color in [("tackles",       "Quites",         "#d62728"),
                              ("interceptions", "Intercepciones", "#2b3a67"),
                              ("clearances",    "Despejes",       "#e8a200")]:
        vals = df[col].values
        ax.barh(y, vals, left=left, height=0.6, color=color, alpha=0.9, label=label)
        left += vals

    ax.set_yticks(y)
    labels = [f"{n}  ({p:.0f}% duelos)" for n, p in
              zip(df["player_name"], df["duels_pct"])]
    ax.set_yticklabels(labels, fontsize=9.5, color=TEXT_COLOR)
    ax.set_xlabel("Acciones defensivas", color=TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.legend(facecolor=BG_COLOR, labelcolor=TEXT_COLOR, fontsize=9,
              loc="lower right")

    ax.set_title(f"Patrones Defensivos – Chaco For Ever"
                 f"{'  (' + match_label + ')' if match_label else ''}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Mapa de ataque (concentración de juego por zonas) ───────────────────────

def _team_side_focus(is_home, focus):
    """Devuelve (side, es_chaco) según el foco ('chaco' o 'rival')."""
    chaco_side = "home" if is_home else "away"
    rival_side = "away" if is_home else "home"
    if focus == "rival":
        return rival_side, False
    return chaco_side, True


def _draw_attack_flank_arrows(pitch, ax, x, y):
    """Flechas por franja (abajo/centro/arriba) con longitud ∝ al % de toques
    de la mitad ofensiva en cada franja → muestra por qué banda se ataca más.
    El equipo ataca hacia la derecha (mitad ofensiva = x>50, excluye al arquero)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    att = x > 50
    ax_y = y[att]
    if ax_y.size < 5:
        return
    bands = [(0, 100 / 3, 17.0), (100 / 3, 200 / 3, 50.0), (200 / 3, 100.01, 83.0)]
    counts = [float(((ax_y >= lo) & (ax_y < hi)).sum()) for lo, hi, _ in bands]
    total = sum(counts) or 1.0
    fracs = [c / total for c in counts]
    mx = max(fracs) or 1.0
    for (lo, hi, yc), f in zip(bands, fracs):
        length = 11 + 30 * (f / mx)          # longitud ∝ concentración de ataque
        x1 = min(48 + length, 90)
        pitch.arrows(48, yc, x1, yc, ax=ax, width=4, headwidth=4, headlength=4.5,
                     color="#111111", alpha=0.82, zorder=5)
        ax.text(x1 + 1.5, yc, f"{f * 100:.0f}%", va="center", ha="left",
                fontsize=10.5, fontweight="bold", color="#111111", zorder=6)


def plot_attack_map(df_heatmaps, is_home=True, focus="chaco", team_label=None,
                    match_label="", save_path=None):
    """
    Mapa de ataque: la cancha se divide en una grilla de zonas (6×3) y cada zona
    se sombrea según la concentración de toques del equipo. Flecha = dirección de
    ataque (hacia la derecha). Verde para Chaco, azul para el rival.
    Se arma con los puntos de toques del heatmap (player_heatmaps_clean.csv).
    """
    if df_heatmaps is None or df_heatmaps.empty:
        return None

    side, es_chaco = _team_side_focus(is_home, focus)
    cmap = "Greens" if es_chaco else "Blues"
    team_label = team_label or ("Chaco For Ever" if es_chaco else "Rival")

    d = df_heatmaps[df_heatmaps["team_side"] == side]
    x = pd.to_numeric(d["x"], errors="coerce")
    y = pd.to_numeric(d["y"], errors="coerce")
    pts = pd.DataFrame({"x": x, "y": y}).dropna()
    if pts.empty:
        return None

    fig, ax = plt.subplots(figsize=(11, 7.5))
    fig.patch.set_facecolor(BG_COLOR)
    pitch = Pitch(pitch_type="opta", pitch_color=PITCH_BG, line_color=PITCH_LINE,
                  linewidth=1.4, line_zorder=3)
    pitch.draw(ax=ax)
    ax.set_facecolor(PITCH_BG)

    bs = pitch.bin_statistic(pts["x"].values, pts["y"].values,
                             statistic="count", bins=(6, 3))
    pcm = pitch.heatmap(bs, ax=ax, cmap=cmap, edgecolor="#f4f4ef",
                        linewidth=1.5, alpha=0.85, zorder=1)

    # Flechas por franja: longitud ∝ por dónde ataca más (mitad ofensiva)
    _draw_attack_flank_arrows(pitch, ax, pts["x"].values, pts["y"].values)

    # Leyenda de gradiente (Mayor / Menor concentración de juego)
    cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal",
                        fraction=0.045, pad=0.05)
    smin = float(np.nanmin(bs["statistic"]))
    smax = float(np.nanmax(bs["statistic"]))
    cbar.set_ticks([smin, smax])
    cbar.set_ticklabels(["Menor concentración de juego",
                         "Mayor concentración de juego"])
    cbar.ax.tick_params(labelsize=9, colors=TEXT_COLOR, length=0)
    cbar.outline.set_visible(False)

    ax.set_title(f"Mapa de Ataque – {team_label}"
                 f"{'  (' + match_label + ')' if match_label else ''}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold", pad=8)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Mapa de pases / juego por tercios ───────────────────────────────────────

def plot_passing_thirds_map(df_heatmaps, is_home=True, focus="chaco",
                            team_label=None, match_label="", save_path=None):
    """
    Mapa de pases por tercios: divide la cancha en tercio defensivo / medio /
    ofensivo (el equipo ataca hacia la derecha) y muestra el % de presencia del
    equipo en cada tercio. NOTA: SofaScore no entrega pases, así que el % se
    calcula sobre los toques del heatmap (presencia territorial).
    """
    if df_heatmaps is None or df_heatmaps.empty:
        return None

    side, es_chaco = _team_side_focus(is_home, focus)
    team_label = team_label or ("Chaco For Ever" if es_chaco else "Rival")

    d = df_heatmaps[df_heatmaps["team_side"] == side]
    x = pd.to_numeric(d["x"], errors="coerce").dropna()
    if x.empty:
        return None

    edges = [0, 100 / 3, 200 / 3, 100]
    labels = ["Defensivo", "Medio", "Ofensivo"]
    counts = [((x >= edges[i]) & (x < edges[i + 1] if i < 2 else x <= edges[i + 1])).sum()
              for i in range(3)]
    total = sum(counts) or 1
    pct = [100 * c / total for c in counts]

    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(BG_COLOR)
    pitch = Pitch(pitch_type="opta", pitch_color=PITCH_BG, line_color=PITCH_LINE,
                  linewidth=1.4, line_zorder=3)
    pitch.draw(ax=ax)
    ax.set_facecolor(PITCH_BG)

    GOLD = (0.71, 0.62, 0.20)  # oro oliva, como la referencia
    pmax = max(pct) or 1
    for i in range(3):
        lo, hi = edges[i], edges[i + 1]
        alpha = 0.35 + 0.55 * (pct[i] / pmax)
        ax.add_patch(mpatches.Rectangle((lo, 0), hi - lo, 100, facecolor=GOLD,
                                        alpha=alpha, edgecolor="none", zorder=1))
        cx = (lo + hi) / 2
        ax.text(cx, 50, f"{pct[i]:.0f}%", ha="center", va="center",
                fontsize=26, fontweight="bold", color="white", zorder=5,
                bbox=dict(boxstyle="round,pad=0.45", facecolor="#22304e",
                          edgecolor="none"))
        ax.text(cx, 6, labels[i], ha="center", va="center", fontsize=11,
                color=TEXT_COLOR, fontweight="bold", zorder=5)

    ax.set_title(f"Mapa de Pases por Tercios – {team_label}"
                 f"{'  (' + match_label + ')' if match_label else ''}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold", pad=8)
    fig.text(0.5, 0.015, "% de presencia por tercio (basado en toques; "
             "SofaScore no provee pases)", ha="center", fontsize=9,
             color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig
