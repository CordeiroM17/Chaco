"""
pre_match.py (visualization)
=============================
Gráficos de scouting pre-partido:
  - Comparación de forma (últimos N resultados)
  - Tendencia de xG
  - Radar de estadísticas promedio
  - Jugadores clave del rival
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from src.visualization.season import (
    save_fig, BG_COLOR, TEXT_COLOR, ACCENT_COLOR, RIVAL_COLOR,
    MUTED_COLOR, GRID_COLOR,
)


RESULT_COLORS = {"W": "#2ca02c", "D": "#e8a200", "L": "#d62728", "?": "#8a8a8a"}


# ─── Forma comparada (últimos N) ──────────────────────────────────────────────

def plot_form_comparison(chaco_form, rival_form, rival_name="Rival",
                          save_path=None):
    """
    Grilla de resultados: Chaco arriba, Rival abajo.
    chaco_form / rival_form: DataFrames con columna 'result' ('W','D','L').
    """
    fig, axs = plt.subplots(2, 1, figsize=(10, 4), gridspec_kw={"hspace": 0.5})
    fig.patch.set_facecolor(BG_COLOR)

    for ax, df, label in [(axs[0], chaco_form, "Chaco For Ever"),
                           (axs[1], rival_form,  rival_name)]:
        ax.set_facecolor(BG_COLOR)
        ax.set_xlim(-0.5, max(len(df) - 0.5, 4.5))
        ax.set_ylim(-0.6, 0.6)
        ax.axis("off")
        ax.set_title(label, color=TEXT_COLOR, fontsize=11, fontweight="bold", loc="left", pad=3)

        for i, row in df.reset_index(drop=True).iterrows():
            result = row.get("result", "?")
            color  = RESULT_COLORS.get(result, "#888")
            rect   = mpatches.FancyBboxPatch(
                (i - 0.4, -0.4), 0.8, 0.8,
                boxstyle="round,pad=0.05", facecolor=color, edgecolor=BG_COLOR,
                linewidth=1.2, alpha=0.95
            )
            ax.add_patch(rect)
            ax.text(i, 0, result, ha="center", va="center",
                    fontsize=16, fontweight="bold", color="white")

            opponent = str(row.get("opponent", "")).split()[-1][:8]
            venue    = "L" if row.get("venue") == "Local" else "V"
            gf       = row.get("chaco_goals", row.get("goals_for", "?"))
            ga       = row.get("rival_goals", row.get("goals_against", "?"))
            ax.text(i, -0.53, f"{venue} {gf}-{ga}\n{opponent}",
                    ha="center", va="top", fontsize=6.5, color=TEXT_COLOR, alpha=0.8)

    plt.suptitle("Forma Reciente", color=TEXT_COLOR, fontsize=13,
                 fontweight="bold", y=1.02)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Tendencia de xG ──────────────────────────────────────────────────────────

def plot_xg_trend(chaco_form, rival_form, rival_name="Rival", save_path=None):
    """
    Barras de xG a favor y en contra por partido para ambos equipos.
    """
    fig, axs = plt.subplots(1, 2, figsize=(14, 5), sharey=False)
    fig.patch.set_facecolor(BG_COLOR)

    for ax, df, label, xg_col, xga_col in [
        (axs[0], chaco_form, "Chaco For Ever", "chaco_xg",  "rival_xg"),
        (axs[1], rival_form,  rival_name,       "xg_for",    "xg_against"),
    ]:
        ax.set_facecolor(BG_COLOR)
        if df.empty or xg_col not in df.columns:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    color=TEXT_COLOR, transform=ax.transAxes)
            ax.set_title(label, color=TEXT_COLOR, fontsize=11, fontweight="bold")
            continue

        x = range(len(df))
        xg  = pd.to_numeric(df[xg_col],  errors="coerce").fillna(0)
        xga = pd.to_numeric(df[xga_col], errors="coerce").fillna(0)

        ax.bar([i - 0.2 for i in x], xg,  0.35, color=ACCENT_COLOR, alpha=0.9, label="xG favor")
        ax.bar([i + 0.2 for i in x], xga, 0.35, color=RIVAL_COLOR,  alpha=0.9, label="xG contra")

        ax.set_xticks(list(x))
        ax.set_xticklabels([f"P{i+1}" for i in range(len(df))], color=TEXT_COLOR, fontsize=9)
        ax.tick_params(colors=TEXT_COLOR)
        ax.set_ylabel("xG", color=TEXT_COLOR, fontsize=10)
        ax.set_title(label, color=TEXT_COLOR, fontsize=11, fontweight="bold")
        ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
        ax.spines["bottom"].set_color(MUTED_COLOR)
        ax.spines["left"].set_color(MUTED_COLOR)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(facecolor=BG_COLOR, labelcolor=TEXT_COLOR, fontsize=8)

    fig.suptitle("Tendencia de xG – Últimos Partidos",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Radar de estadísticas ────────────────────────────────────────────────────

def plot_stats_radar(chaco_avg_stats, rival_avg_stats, rival_name="Rival",
                     save_path=None):
    """
    Gráfico radar comparando métricas promedio de Chaco vs Rival.
    chaco_avg_stats / rival_avg_stats: dict {metric_name: value}
    """
    RADAR_METRICS = [
        ("Ball possession", 100),
        ("Total shots",      20),
        ("Shots on target",  10),
        ("Expected goals",    3),
        ("Accurate passes", 400),
        ("Corner kicks",     10),
        ("Tackles",          20),
    ]

    labels = []
    chaco_vals = []
    rival_vals = []

    for metric, max_val in RADAR_METRICS:
        c = float(chaco_avg_stats.get(metric, 0) or 0)
        r = float(rival_avg_stats.get(metric, 0) or 0)
        labels.append(metric.replace(" ", "\n"))
        chaco_vals.append(min(c / max_val, 1.0))
        rival_vals.append(min(r / max_val, 1.0))

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    chaco_vals += chaco_vals[:1]
    rival_vals  += rival_vals[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    ax.plot(angles, chaco_vals, color=ACCENT_COLOR, linewidth=2, linestyle="-")
    ax.fill(angles, chaco_vals, color=ACCENT_COLOR, alpha=0.25)

    ax.plot(angles, rival_vals, color=RIVAL_COLOR, linewidth=2, linestyle="-")
    ax.fill(angles, rival_vals, color=RIVAL_COLOR, alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=TEXT_COLOR, fontsize=9)
    ax.set_yticklabels([])
    ax.tick_params(colors=TEXT_COLOR)
    ax.spines["polar"].set_color(GRID_COLOR)
    ax.grid(color=GRID_COLOR, linewidth=0.8)

    chaco_patch = mpatches.Patch(color=ACCENT_COLOR, label="Chaco For Ever", alpha=0.7)
    rival_patch  = mpatches.Patch(color=RIVAL_COLOR,  label=rival_name,       alpha=0.7)
    ax.legend(handles=[chaco_patch, rival_patch], loc="upper right",
              bbox_to_anchor=(1.25, 1.1), facecolor=BG_COLOR, labelcolor=TEXT_COLOR, fontsize=10)

    ax.set_title(f"Radar de Estadísticas\nChaco vs {rival_name}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold", pad=20)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Comparación de equipos (Chaco vs rival) ──────────────────────────────────

def _team_panel(chaco_prof, rival_prof, rows, title, subtitle, rival_name,
                lower_is_better=None, save_path=None, note=None):
    """Arma un panel de barras pareadas a partir de una lista de filas
    (label, clave_perfil, formato)."""
    labels = [r[0] for r in rows]
    cvals  = [float(chaco_prof.get(r[1], 0) or 0) for r in rows]
    rvals  = [float(rival_prof.get(r[1], 0) or 0) for r in rows]
    fmts   = [r[2] for r in rows]

    H = 0.62 * len(rows) + 2.7
    fig, ax = plt.subplots(figsize=(9, H))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # dibujamos fila a fila para respetar el formato de cada métrica
    y = np.arange(len(labels)); h = 0.38
    span = max(cvals + rvals + [1e-6])
    lower_is_better = lower_is_better or set()
    ax.barh(y + h / 2, cvals, height=h, color=ACCENT_COLOR, alpha=0.9, label="Chaco For Ever")
    ax.barh(y - h / 2, rvals, height=h, color=RIVAL_COLOR, alpha=0.9, label=rival_name)
    for yi, cv, rv, f in zip(y, cvals, rvals, fmts):
        ax.text(cv + span * 0.012, yi + h / 2, f.format(cv), va="center", ha="left",
                fontsize=8.5, color=ACCENT_COLOR, fontweight="bold")
        ax.text(rv + span * 0.012, yi - h / 2, f.format(rv), va="center", ha="left",
                fontsize=8.5, color=RIVAL_COLOR, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([(f"{l} *" if l in lower_is_better else l) for l in labels],
                       color=TEXT_COLOR, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, span * 1.16)
    ax.set_xticks([])
    for sp in ("top", "right", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)

    # Encabezado posicionado en pulgadas desde arriba, para que la separación
    # sea constante y no se solape en los paneles con pocas filas.
    y_title = 1 - 0.40 / H
    y_sub   = 1 - 0.74 / H
    y_leg   = 1 - 1.06 / H
    y_top   = 1 - 1.45 / H
    fig.suptitle(title, color=TEXT_COLOR, fontsize=14, fontweight="bold", y=y_title)
    fig.text(0.5, y_sub, subtitle, ha="center", color=MUTED_COLOR, fontsize=9.5)
    # Leyenda de texto con color (no tapa las barras como ax.legend)
    fig.text(0.31, y_leg, "● Chaco For Ever", color=ACCENT_COLOR, fontsize=10,
             fontweight="bold", ha="left")
    fig.text(0.58, y_leg, f"● {rival_name}", color=RIVAL_COLOR, fontsize=10,
             fontweight="bold", ha="left")
    foot = "* menos es mejor" if lower_is_better else ""
    if note:
        foot = (foot + "    " if foot else "") + note
    if foot:
        fig.text(0.5, 0.028, foot, ha="center", color=MUTED_COLOR, fontsize=8.5)
    plt.tight_layout(rect=[0, 0.05, 1, y_top])
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_team_radar_extended(chaco_prof, rival_prof, rival_name="Rival", save_path=None):
    """Radar ampliado (8 métricas por partido) comparando el juego de Chaco y
    del rival: posesión, remates, remates al arco, xG, córners, pases, y dos
    métricas defensivas (entradas, intercepciones). Complementa al radar chico."""
    METRICS = [
        ("Posesión %",       "possession_for", 100),
        ("Remates",          "shots_for",       18),
        ("Remates\nal arco", "sot_for",          8),
        ("xG",               "xg_for",         2.2),
        ("Córners",          "corners_for",      8),
        ("Pases\nprecisos",  "passes_acc_for", 360),
        ("Entradas",         "tackles_for",     12),
        ("Intercep.",        "interceptions_for", 22),
    ]
    labels, cvals, rvals = [], [], []
    for lab, key, mx in METRICS:
        labels.append(lab)
        cvals.append(min(float(chaco_prof.get(key, 0) or 0) / mx, 1.0))
        rvals.append(min(float(rival_prof.get(key, 0) or 0) / mx, 1.0))

    ang = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    ang += ang[:1]; cvals += cvals[:1]; rvals += rvals[:1]

    fig, ax = plt.subplots(figsize=(8.4, 8.4), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG_COLOR); ax.set_facecolor(BG_COLOR)
    ax.plot(ang, cvals, color=ACCENT_COLOR, linewidth=2)
    ax.fill(ang, cvals, color=ACCENT_COLOR, alpha=0.25)
    ax.plot(ang, rvals, color=RIVAL_COLOR, linewidth=2)
    ax.fill(ang, rvals, color=RIVAL_COLOR, alpha=0.25)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels, color=TEXT_COLOR, fontsize=9.5)
    ax.set_yticklabels([]); ax.set_ylim(0, 1)
    ax.tick_params(colors=TEXT_COLOR)
    ax.spines["polar"].set_color(GRID_COLOR)
    ax.grid(color=GRID_COLOR, linewidth=0.8)
    cp = mpatches.Patch(color=ACCENT_COLOR, label="Chaco For Ever", alpha=0.7)
    rp = mpatches.Patch(color=RIVAL_COLOR, label=rival_name, alpha=0.7)
    ax.legend(handles=[cp, rp], loc="upper right", bbox_to_anchor=(1.22, 1.10),
              facecolor=BG_COLOR, labelcolor=TEXT_COLOR, fontsize=10)
    ax.set_title(f"Radar ampliado — promedios por partido\nChaco vs {rival_name}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold", pad=22)
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_offensive_comparison(chaco_prof, rival_prof, rival_name="Rival", save_path=None):
    """Panel ofensivo: qué genera cada equipo por partido."""
    rows = [
        ("Goles",          "goals_for",     "{:.2f}"),
        ("xG (peligro)",   "xg_for",        "{:.2f}"),
        ("Remates",        "shots_for",     "{:.1f}"),
        ("Remates al arco","sot_for",       "{:.1f}"),
        ("Córners",        "corners_for",   "{:.1f}"),
        ("Posesión %",     "possession_for","{:.0f}"),
    ]
    return _team_panel(chaco_prof, rival_prof, rows,
                       "Comparación ofensiva — promedios por partido",
                       "Más alto = genera más. Barras rojas: Chaco · azules: "
                       f"{rival_name}", rival_name, save_path=save_path)


def plot_defensive_comparison(chaco_prof, rival_prof, rival_name="Rival", save_path=None):
    """Panel defensivo: qué concede y cuánto trabajo defensivo hace cada equipo."""
    rows = [
        ("Goles recibidos",        "goals_against",      "{:.2f}"),
        ("xG recibido",            "xg_against",         "{:.2f}"),
        ("Remates recibidos",      "shots_against",      "{:.1f}"),
        ("Rem. al arco recibidos", "sot_against",        "{:.1f}"),
        ("Despejes",               "clearances_for",     "{:.1f}"),
        ("Intercepciones",         "interceptions_for",  "{:.1f}"),
        ("Entradas",               "tackles_for",        "{:.1f}"),
    ]
    lib = {"Goles recibidos", "xG recibido", "Remates recibidos", "Rem. al arco recibidos"}
    return _team_panel(chaco_prof, rival_prof, rows,
                       "Comparación defensiva — promedios por partido",
                       "En las primeras cuatro, menos es mejor.", rival_name,
                       lower_is_better=lib, save_path=save_path)


def plot_shots_comparison(chaco_prof, rival_prof, rival_name="Rival",
                          side="for", save_path=None):
    """Desglose de remates por partido. side='for' = remates realizados;
    side='against' = remates recibidos."""
    suf = side
    rows = [
        ("Totales",    f"shots_{suf}",         "{:.1f}"),
        ("Al arco",    f"sot_{suf}",           "{:.1f}"),
        ("Afuera",     f"shots_off_{suf}",     "{:.1f}"),
        ("Bloqueados", f"shots_blocked_{suf}", "{:.1f}"),
    ]
    if side == "for":
        title = "Remates realizados — desglose por partido"
        xg_c, xg_r = chaco_prof.get("xg_for", 0), rival_prof.get("xg_for", 0)
        sub = "Cuántos remató cada equipo y de qué tipo."
    else:
        title = "Remates recibidos — desglose por partido"
        xg_c, xg_r = chaco_prof.get("xg_against", 0), rival_prof.get("xg_against", 0)
        sub = "Cuántos remates permitió cada equipo (menos es mejor)."
    note = f"xG {'generado' if side=='for' else 'recibido'}:  Chaco {xg_c:.2f}  ·  {rival_name} {xg_r:.2f}"
    return _team_panel(chaco_prof, rival_prof, rows, title, sub, rival_name,
                       save_path=save_path, note=note)


# ─── Jugadores clave del rival ────────────────────────────────────────────────

def plot_rival_players(df_players, rival_name="Rival", save_path=None):
    """
    Barras horizontales con rating promedio de los jugadores clave del rival.
    """
    if df_players is None or df_players.empty:
        return None

    df = df_players.copy().sort_values("avg_rating", ascending=True)
    name_col = "player_name" if "player_name" in df.columns else df.columns[0]

    fig, ax = plt.subplots(figsize=(9, max(4, len(df) * 0.6)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    y = range(len(df))
    colors = [
        "#2b3a67" if r >= 7.5 else ("#5a6fa0" if r >= 7.0 else "#9aa6c4")
        for r in df["avg_rating"]
    ]
    ax.barh(list(y), df["avg_rating"].values, color=colors, alpha=0.85, height=0.6)

    ax.set_yticks(list(y))
    ax.set_yticklabels(df[name_col].values, fontsize=10, color=TEXT_COLOR)
    ax.set_xlabel("Rating Promedio", color=TEXT_COLOR, fontsize=10)
    ax.set_xlim(5, 10)
    ax.tick_params(colors=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i, row in df.reset_index(drop=True).iterrows():
        label = f"{row['avg_rating']:.1f}"
        if row.get("goals", 0) > 0:
            label += f"  {int(row['goals'])}g"
        if row.get("assists", 0) > 0:
            label += f"  {int(row['assists'])}a"
        ax.text(row["avg_rating"] + 0.05, i, label,
                va="center", fontsize=8.5, color=TEXT_COLOR)

    ax.set_title(f"Jugadores Clave – {rival_name}",
                 color=TEXT_COLOR, fontsize=12, fontweight="bold")
    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Cara a cara (Head to Head histórico) ────────────────────────────────────

def plot_head_to_head(h2h_df, chaco_scorers=None, rival_scorers=None,
                      rival_name="Rival", save_path=None,
                      summary=None, manager_note=None):
    """
    Historial completo de Chaco vs el rival (TODAS las temporadas con datos,
    no solo la actual): grilla de resultados en orden cronológico + goleadores
    históricos de cada lado ("quién nos hizo daño antes / a quién le hicimos
    daño"). Sale de analysis.pre_match.head_to_head / head_to_head_goalscorers.

    `summary` (dict de head_to_head_summary) y `manager_note` (str, ej. el DT
    actual del rival) son opcionales y se muestran como panel de contexto a la
    derecha de la grilla — útiles cuando el historial es corto y sobra espacio.
    """
    if h2h_df is None or h2h_df.empty:
        return None

    fig = plt.figure(figsize=(11, 5.8))
    fig.patch.set_facecolor(BG_COLOR)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.6], hspace=0.6, wspace=0.3)

    ax_grid = fig.add_subplot(gs[0, :])
    ax_grid.set_facecolor(BG_COLOR)
    ax_grid.axis("off")
    df = h2h_df.reset_index(drop=True)
    n = len(df)
    ax_grid.set_xlim(-0.5, max(n - 0.5, 4.5))
    ax_grid.set_ylim(-0.65, 0.6)
    for i, row in df.iterrows():
        result = row.get("result", "?")
        color = RESULT_COLORS.get(result, "#888")
        rect = mpatches.FancyBboxPatch(
            (i - 0.4, -0.4), 0.8, 0.8, boxstyle="round,pad=0.05",
            facecolor=color, edgecolor=BG_COLOR, linewidth=1.2, alpha=0.95)
        ax_grid.add_patch(rect)
        ax_grid.text(i, 0, result, ha="center", va="center",
                    fontsize=15, fontweight="bold", color="white")
        venue = "L" if row.get("venue") == "Local" else "V"
        ax_grid.text(i, -0.53,
                    f"{row.get('date','')}\n{venue} {row.get('chaco_goals')}-"
                    f"{row.get('rival_goals')} ({row.get('season')})",
                    ha="center", va="top", fontsize=6.5, color=TEXT_COLOR, alpha=0.85)
    ax_grid.set_title(f"Historial vs {rival_name} — todas las temporadas ({n} partidos)",
                      color=TEXT_COLOR, fontsize=12, fontweight="bold", loc="left")

    # Panel de contexto a la derecha (récord agregado + DT actual del rival).
    # Útil sobre todo cuando el historial es corto y la grilla deja hueco.
    ctx_lines = []
    if summary:
        rec = (f"Récord de Chaco:  {summary.get('victorias',0)}V "
               f"{summary.get('empates',0)}E {summary.get('derrotas',0)}D")
        gls = (f"Goles:  {summary.get('goles_favor',0)} a favor · "
               f"{summary.get('goles_contra',0)} en contra")
        ctx_lines += [rec, gls]
    if manager_note:
        ctx_lines.append(manager_note)
    if ctx_lines:
        x0 = 0.55 if n <= 3 else 0.70
        ax_grid.text(x0, 0.92, "Contexto", transform=ax_grid.transAxes,
                     fontsize=10.5, fontweight="bold", color=TEXT_COLOR, va="top")
        for k, line in enumerate(ctx_lines):
            ax_grid.text(x0, 0.66 - k * 0.28, line, transform=ax_grid.transAxes,
                         fontsize=9, color=TEXT_COLOR, va="top")

    ax_c = fig.add_subplot(gs[1, 0])
    ax_r = fig.add_subplot(gs[1, 1])
    for ax, sdf, label, color in [
        (ax_c, chaco_scorers, "Goleadores de Chaco", ACCENT_COLOR),
        (ax_r, rival_scorers, f"Goleadores de {rival_name}", RIVAL_COLOR),
    ]:
        ax.set_facecolor(BG_COLOR)
        ax.axis("off")
        ax.set_title(label, color=TEXT_COLOR, fontsize=10.5, fontweight="bold", loc="left")
        if sdf is None or sdf.empty:
            ax.text(0.02, 0.85, "Sin goles registrados", fontsize=9,
                    color=MUTED_COLOR, transform=ax.transAxes)
            continue
        for i, r in sdf.head(8).reset_index(drop=True).iterrows():
            y = 0.90 - i * 0.11
            ax.text(0.02, y, str(r["player"]), fontsize=9.5, color=TEXT_COLOR,
                    transform=ax.transAxes)
            ax.text(0.90, y, f"{int(r['goals'])}", fontsize=9.5, fontweight="bold",
                    color=color, ha="right", transform=ax.transAxes)

    fig.suptitle(f"Cara a Cara – Chaco For Ever vs {rival_name}",
                color=TEXT_COLOR, fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Alerta de amonestados ───────────────────────────────────────────────────

def plot_discipline_alert(alert_df, rival_name="Rival", save_path=None):
    """
    Alerta operativa para el próximo partido: jugadores de Chaco a 1 amarilla
    de la suspensión por acumulación. Sale de analysis.pre_match.discipline_alert.
    """
    if alert_df is None or alert_df.empty:
        return None

    n = len(alert_df)
    fig, ax = plt.subplots(figsize=(9, max(2.3, 0.75 * n + 1.2)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")

    ax.text(0.02, 0.95, f"⚠ Riesgo de suspensión — próximo partido vs {rival_name}",
            fontsize=13, fontweight="bold", color=ACCENT_COLOR, transform=ax.transAxes)

    df = alert_df.reset_index(drop=True)
    for i, r in df.iterrows():
        y = 0.78 - i * (0.66 / max(n, 1))
        ax.text(0.03, y, str(r["player"]), fontsize=11, fontweight="bold",
                color=TEXT_COLOR, transform=ax.transAxes)
        ax.text(0.55, y, f"{int(r['amarillas'])} amarillas · {int(r['partidos'])} pj",
                fontsize=9.5, color=MUTED_COLOR, transform=ax.transAxes)
        ax.text(0.97, y, "1 más = SUSPENDIDO", fontsize=9.5, fontweight="bold",
                color=ACCENT_COLOR, ha="right", transform=ax.transAxes)

    plt.tight_layout()
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Mejor once del rival ─────────────────────────────────────────────────────

_POSITION_LABELS = {"G": "Arquero", "D": "Defensor", "M": "Mediocampista", "F": "Delantero"}
_POSITION_COLORS = {"G": "#e8a200", "D": RIVAL_COLOR, "M": "#5a6fa0", "F": ACCENT_COLOR}
_POSITION_ORDER = {"G": 0, "D": 1, "M": 2, "F": 3}


def plot_rival_best_xi(xi_df, rival_name="Rival", save_path=None):
    """
    "Mejor once" del rival: el arquero + los 10 jugadores de campo con más
    titularidades en sus últimos partidos scrapeados (empate por rating).
    No es la alineación oficial confirmada del próximo partido — es la que
    más repitió en la muestra que tenemos descargada.
    Sale de analysis.pre_match.rival_best_xi.
    """
    if xi_df is None or xi_df.empty:
        return None

    df = xi_df.copy()
    df["__ord"] = df["position"].map(_POSITION_ORDER).fillna(9)
    df = df.sort_values(["__ord", "avg_rating"], ascending=[True, True]).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10.5, max(5, 0.55 * len(df) + 1.5)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    y = np.arange(len(df))
    colors = [_POSITION_COLORS.get(p, MUTED_COLOR) for p in df["position"]]
    ax.barh(y, df["avg_rating"], color=colors, alpha=0.88, height=0.62)

    ax.set_yticks(y)
    ax.set_yticklabels(df["player_name"], fontsize=10, color=TEXT_COLOR)
    ax.set_xlim(5, 10)
    ax.set_xlabel("Rating Promedio", color=TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for yi, r in zip(y, df.itertuples()):
        label = f"{r.avg_rating:.2f}  ·  titular {int(r.starts)}/{int(r.matches_played)}"
        if r.goals:
            label += f"  ·  {int(r.goals)}g"
        if r.assists:
            label += f"  {int(r.assists)}a"
        ax.text(r.avg_rating + 0.05, yi, label, va="center", fontsize=8.3, color=TEXT_COLOR)

    handles = [mpatches.Patch(color=c, label=_POSITION_LABELS[p]) for p, c in _POSITION_COLORS.items()]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8.5)

    ax.set_title(f"Mejor Once – {rival_name}", color=TEXT_COLOR, fontsize=13, fontweight="bold")
    fig.text(0.5, 0.01, "Titularidades en sus últimos partidos scrapeados, no la alineación "
             "oficial del próximo partido", ha="center", fontsize=8.3,
             color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Rendimiento local/visitante del rival ────────────────────────────────────

def plot_rival_home_away(split_df, rival_name="Rival", we_are_home=True, save_path=None):
    """
    Compara el rendimiento del rival de Local vs Visitante. Resalta la columna
    que nos importa según dónde se juega el partido: si nosotros somos local,
    el rival viene de VISITANTE. Sale de analysis.pre_match.rival_home_away_split.
    """
    if split_df is None or split_df.empty:
        return None

    df = split_df.set_index("venue")
    order = ["Local", "Visitante"]
    df = df.reindex([v for v in order if v in df.index])

    relevant = "Visitante" if we_are_home else "Local"
    fig, ax = plt.subplots(figsize=(9, 4.6))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    x = np.arange(len(df))
    colors = [ACCENT_COLOR if v == relevant else "#9aa6c4" for v in df.index]
    bars = ax.bar(x, df["pts_pj"], width=0.55, color=colors, alpha=0.9)

    for xi, (venue, r) in zip(x, df.iterrows()):
        txt = (f"{int(r['V'])}V-{int(r['E'])}E-{int(r['D'])}D\n"
               f"{int(r['gf'])} GF · {int(r['gc'])} GC")
        ax.text(xi, r["pts_pj"] + 0.03, f"{r['pts_pj']:.2f} pts/pj",
                ha="center", va="bottom", fontsize=10, fontweight="bold", color=TEXT_COLOR)
        ax.text(xi, 0.04, txt, ha="center", va="bottom", fontsize=9.5,
                color="white", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(df.index, fontsize=11, color=TEXT_COLOR)
    ax.set_ylim(0, max(df["pts_pj"].max() * 1.25, 0.6))
    ax.set_ylabel("Puntos por partido", color=TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=TEXT_COLOR)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.5)

    sub = (f"Nos visita — mirar su forma de VISITANTE (resaltada)" if we_are_home
           else "Jugamos en su cancha — mirar su forma de LOCAL (resaltada)")
    ax.set_title(f"Local vs Visitante – {rival_name}", color=TEXT_COLOR,
                 fontsize=13, fontweight="bold")
    fig.text(0.5, 0.005, sub, ha="center", fontsize=9, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Timeline de DT del rival ─────────────────────────────────────────────────

def plot_rival_managers(timeline_df, rival_name="Rival", save_path=None):
    """
    Línea de tiempo del DT del rival partido a partido, marcando los cambios de
    entrenador. Sale de analysis.pre_match.rival_manager_timeline. Devuelve None
    si todavía no se descargaron los DT (raw/managers.json).
    """
    if timeline_df is None or timeline_df.empty or timeline_df["manager"].dropna().empty:
        return None

    from src.analysis.pre_match import rival_manager_summary
    df = timeline_df.reset_index(drop=True)
    spells = rival_manager_summary(df)

    fig, ax = plt.subplots(figsize=(12, max(2.6, 0.30 * len(df) + 1.6)))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # un color por DT distinto
    managers = list(dict.fromkeys(m for m in df["manager"] if m))
    palette = [RIVAL_COLOR, ACCENT_COLOR, "#e8a200", "#0f766e", "#5a6fa0"]
    cmap = {m: palette[i % len(palette)] for i, m in enumerate(managers)}

    x = np.arange(len(df))
    for xi, r in zip(x, df.itertuples()):
        ax.scatter(xi, 0, s=170, color=cmap.get(r.manager, MUTED_COLOR),
                   zorder=3, edgecolor="white", linewidth=0.8)
        if r.changed:
            ax.axvline(xi, color=ACCENT_COLOR, linewidth=1.4, alpha=0.6, zorder=0)

    ax.plot(x, [0] * len(df), color=GRID_COLOR, linewidth=1.2, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels([f"P{i+1}" for i in range(len(df))], fontsize=8.5, color=TEXT_COLOR)
    ax.set_yticks([])
    ax.set_ylim(-1, 1)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=TEXT_COLOR)

    # etiquetar cada spell con el nombre del DT y su tramo de partidos
    start_idx = 0
    for sp in spells:
        run = sp["matches"]
        mid = start_idx + (run - 1) / 2
        ax.text(mid, 0.45, sp["manager"], ha="center", va="bottom", fontsize=9,
                fontweight="bold", color=cmap.get(sp["manager"], TEXT_COLOR))
        ax.text(mid, -0.5, f"{sp['from_date'][5:]} → {sp['to_date'][5:]}  ({run})",
                ha="center", va="top", fontsize=7.5, color=MUTED_COLOR)
        start_idx += run

    n_changes = int(df["changed"].sum())
    subtitle = ("sin cambios de DT en la muestra" if n_changes == 0
                else f"{n_changes} cambio(s) de DT en la muestra — DT actual: {spells[-1]['manager']}")
    ax.set_title(f"Línea de Tiempo de DT – {rival_name}", color=TEXT_COLOR,
                 fontsize=13, fontweight="bold")
    fig.text(0.5, 0.02, subtitle + "  ·  P1 = más antiguo", ha="center",
             fontsize=8.5, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.05, 1, 1))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Formaciones usadas por el rival ──────────────────────────────────────────

def plot_rival_formations(formations_df, rival_name="Rival", save_path=None):
    """
    Formaciones usadas por el rival en sus últimos partidos scrapeados —
    variedad o preferencia táctica. Sale de analysis.pre_match.rival_formations_used.
    """
    if formations_df is None or formations_df.empty or formations_df["formation"].dropna().empty:
        return None

    counts = formations_df["formation"].dropna().value_counts()
    # La altura la manda la lista cronológica de la derecha (una fila por
    # partido), no la cantidad de formaciones distintas — si no, con muchos
    # partidos las filas quedaban encimadas.
    n_matches = len(formations_df)
    fig_h = max(4.0, 0.34 * n_matches + 1.8)
    fig, axs = plt.subplots(1, 2, figsize=(12, fig_h),
                            gridspec_kw={"width_ratios": [1, 1.3]})
    fig.patch.set_facecolor(BG_COLOR)

    ax_bar = axs[0]
    ax_bar.set_facecolor(BG_COLOR)
    y = np.arange(len(counts))
    vals = counts.values[::-1]
    labels = counts.index[::-1]
    ax_bar.barh(y, vals, color=RIVAL_COLOR, alpha=0.88)
    ax_bar.set_yticks(y)
    ax_bar.set_yticklabels(labels, fontsize=10, color=TEXT_COLOR)
    for yi, v in zip(y, vals):
        ax_bar.text(v + 0.05, yi, str(int(v)), va="center", fontsize=9.5,
                    color=TEXT_COLOR, fontweight="bold")
    ax_bar.set_xlabel("Partidos", color=TEXT_COLOR, fontsize=10)
    for s in ("top", "right"):
        ax_bar.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax_bar.spines[s].set_color(GRID_COLOR)
    ax_bar.tick_params(colors=TEXT_COLOR)
    ax_bar.set_title("Frecuencia", color=TEXT_COLOR, fontsize=11, fontweight="bold")

    ax_txt = axs[1]
    ax_txt.set_facecolor(BG_COLOR)
    ax_txt.axis("off")
    ax_txt.set_title("Por partido (cronológico)", color=TEXT_COLOR, fontsize=11,
                     fontweight="bold", loc="left")
    df = formations_df.reset_index(drop=True)
    for i, r in df.iterrows():
        y_pos = 0.9 - i * (0.8 / max(len(df), 1))
        ax_txt.text(0.02, y_pos, f"{r['date']}  vs {r['opponent']}", fontsize=9,
                    color=TEXT_COLOR, transform=ax_txt.transAxes)
        ax_txt.text(0.98, y_pos, str(r['formation']), fontsize=9.5, fontweight="bold",
                    color=RIVAL_COLOR, ha="right", transform=ax_txt.transAxes)

    fig.suptitle(f"Formaciones Usadas – {rival_name}", color=TEXT_COLOR,
                fontsize=13, fontweight="bold")
    plt.tight_layout(rect=(0, 0, 1, 0.92))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Perfil disciplinario del rival ───────────────────────────────────────────

def plot_rival_discipline(team_df, player_df, rival_name="Rival", save_path=None,
                          suspension_df=None, full_season=False):
    """
    Perfil disciplinario del rival: faltas/amarillas/rojas por partido +
    jugadores más amonestados. Si `full_season=True` (bajamos toda la
    temporada del rival, no una muestra), el acumulado del panel derecho es
    real y `suspension_df` (de rival_suspension_risk) marca a los que están a
    una amarilla de la suspensión. Sale de rival_discipline_profile.
    """
    if team_df is None or team_df.empty:
        return None

    at_risk_names = set()
    if suspension_df is not None and not suspension_df.empty:
        at_risk_names = set(suspension_df["player_name"])

    fig, axs = plt.subplots(1, 2, figsize=(12.5, 5), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.patch.set_facecolor(BG_COLOR)

    ax_l = axs[0]
    ax_l.set_facecolor(BG_COLOR)
    x = np.arange(len(team_df))
    ymax = max(team_df["yellow_cards"].max(), team_df["fouls"].max(), 1)

    # Línea roja vertical en los partidos con expulsión (detrás de las barras)
    red_matches = [xi for xi, r in zip(x, team_df["red_cards"]) if r]
    for j, xi in enumerate(red_matches):
        ax_l.axvline(xi, color=ACCENT_COLOR, linewidth=1.6, alpha=0.55, zorder=0,
                     label="Partido con expulsión" if j == 0 else None)

    ax_l.bar(x - 0.2, team_df["yellow_cards"], 0.35, color="#e8a200",
             label="Amarillas", zorder=3)
    ax_l.bar(x + 0.2, team_df["fouls"], 0.35, color=MUTED_COLOR, alpha=0.6,
             label="Faltas", zorder=3)
    opp = team_df["opponent"].tolist()
    red_idx = [xi for xi, r in zip(x, team_df["red_cards"]) if r]
    for k, xi in enumerate(red_idx):
        # escalonar en dos alturas para que no se pisen las etiquetas cercanas
        dy = 0.4 if k % 2 == 0 else 1.5
        ax_l.text(xi, ymax + dy, f"{int(team_df['red_cards'].iloc[xi])}R vs {opp[xi][:11]}",
                  ha="center", fontsize=7.5, color=ACCENT_COLOR, fontweight="bold", zorder=4)
    ax_l.set_ylim(top=ymax + 2.6)

    # Etiquetas simplificadas P1..Pn (los nombres completos se pisaban)
    ax_l.set_xticks(x)
    ax_l.set_xticklabels([f"P{i+1}" for i in range(len(team_df))],
                         fontsize=9, color=TEXT_COLOR)
    ax_l.tick_params(colors=TEXT_COLOR)
    ax_l.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax_l.set_title("Faltas y amarillas por partido (P1 = más antiguo)",
                   color=TEXT_COLOR, fontsize=11, fontweight="bold")
    for s in ("top", "right"):
        ax_l.spines[s].set_visible(False)
    ax_l.grid(axis="y", color=GRID_COLOR, alpha=0.6)

    ax_r = axs[1]
    ax_r.set_facecolor(BG_COLOR)
    ax_r.axis("off")
    panel_title = "Amonestados (acumulado)" if full_season else "Más amonestados"
    ax_r.set_title(panel_title, color=TEXT_COLOR, fontsize=11,
                   fontweight="bold", loc="left")
    if player_df is not None and not player_df.empty:
        for i, r in player_df.head(6).reset_index(drop=True).iterrows():
            y_pos = 0.85 - i * 0.13
            txt = f"{int(r['yellow_cards'])}A"
            if r["red_cards"]:
                txt += f" {int(r['red_cards'])}R"
            at_risk = str(r["player_name"]) in at_risk_names
            name_txt = str(r["player_name"]) + ("  (a 1 de susp.)" if at_risk else "")
            ax_r.text(0.02, y_pos, name_txt, fontsize=9.5,
                      color=ACCENT_COLOR if at_risk else TEXT_COLOR,
                      fontweight="bold" if at_risk else "normal",
                      transform=ax_r.transAxes)
            ax_r.text(0.97, y_pos, txt, fontsize=9.5, fontweight="bold",
                      color=ACCENT_COLOR, ha="right", transform=ax_r.transAxes)
    else:
        ax_r.text(0.02, 0.8, "Sin datos", fontsize=9, color=MUTED_COLOR,
                  transform=ax_r.transAxes)

    fig.suptitle(f"Perfil Disciplinario – {rival_name}", color=TEXT_COLOR,
                fontsize=13, fontweight="bold")
    caption = ("Acumulado de toda la temporada descargada del rival · rojo = a una "
               "amarilla de la suspensión" if full_season else
               "Tendencia reciente (solo partidos scrapeados) — no refleja el "
               "acumulado real de amarillas en toda la temporada del rival")
    fig.text(0.5, 0.01, caption, ha="center", fontsize=8, color=MUTED_COLOR, style="italic")
    plt.tight_layout(rect=(0, 0.05, 1, 0.90))
    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig
