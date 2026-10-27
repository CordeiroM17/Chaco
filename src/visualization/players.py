"""
players.py (visualization)
==========================
Gráficos individuales de jugador:
  - Radar de pizza (percentiles vs pool de la Primera Nacional scrapeada)
  - Radar clásico comparando dos jugadores (valores por-90)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mplsoccer import PyPizza, Radar

from src.visualization.season import (
    save_fig, BG_COLOR, TEXT_COLOR, ACCENT_COLOR, RIVAL_COLOR, MUTED_COLOR,
)
from src.analysis.players import PIZZA_GROUP_COLORS


# ─── Radar de pizza ──────────────────────────────────────────────────────────

def _fmt_val(v):
    """Formatea el valor por-90: entero si es redondo, si no 2 decimales."""
    if v is None:
        return "-"
    return f"{v:.0f}" if abs(v - round(v)) < 1e-9 else f"{v:.2f}"


def _sample_tier(minutes):
    """
    Clasifica el tamaño de muestra por minutos jugados. Devuelve
    (etiqueta, color_texto, color_fondo).

    Existe para poder hacerle pizza a TODOS los jugadores sin que se lea mal:
    en vez de esconder al que jugó poco, se le pone el cartel de cuánta muestra
    hay detrás de esos percentiles.
    """
    if minutes is None:
        return ("", TEXT_COLOR, "#ecece4")
    if minutes >= 900:
        return ("muestra amplia", "#1d6b3f", "#dff0e4")
    if minutes >= 450:
        return ("muestra media", "#8a6100", "#fbeecd")
    if minutes >= 180:
        return ("MUESTRA CHICA – leer con cuidado", "#9c4a12", "#fbe0cb")
    return ("MUESTRA MUY CHICA – no concluyente", "#96201f", "#f7d4d3")


def plot_player_pizza(player_name, percentiles, team_label="Chaco For Ever",
                      context_label="", minutes=None, matches=None,
                      sample_note="", save_path=None):
    """
    Pizza de percentiles del jugador (de analysis.players.player_percentiles).

    OJO con la lectura: el número grande de cada gajo es el PERCENTIL (0-100)
    frente al resto de la liga, NO el valor bruto. Ej.: 92 en Goles = mejor que
    el 92% de los jugadores en goles por 90', no "92 goles". El valor real por
    90 minutos va entre paréntesis en la etiqueta de cada gajo.

    `minutes` y `matches`: si se pasan, se dibuja arriba un cartel con los
    minutos jugados, los partidos y qué tan confiable es la muestra (ver
    _sample_tier). Con eso se le puede generar pizza a todo el plantel —
    incluidos los refuerzos y los suplentes — sin que un percentil alto sacado
    de 90 minutos se lea igual que uno de una temporada entera.

    `sample_note`: línea extra debajo del cartel (p.ej. "debutó el 07/07 —
    95% de los minutos disponibles desde entonces").

    percentiles: dict {grupo: [(etiqueta, percentil, valor_p90), ...]}
    """
    if not percentiles:
        return None

    params, values, slice_colors = [], [], []
    for group, entries in percentiles.items():
        color = PIZZA_GROUP_COLORS.get(group, ACCENT_COLOR)
        for label, pct, val in entries:
            # La etiqueta del gajo muestra la métrica + su valor real por-90,
            # para que no se confunda con el percentil que va adentro.
            params.append(f"{label}\n({_fmt_val(val)} p90)")
            values.append(pct)
            slice_colors.append(color)

    baker = PyPizza(
        params=params,
        background_color=BG_COLOR,
        straight_line_color="#cfcfc6",
        straight_line_lw=1,
        last_circle_color="#b3b3aa",
        last_circle_lw=1.2,
        other_circle_lw=0,
        inner_circle_size=12,
    )

    fig, ax = baker.make_pizza(
        values,
        figsize=(9, 9.5),
        color_blank_space="same",
        slice_colors=slice_colors,
        value_colors=["white"] * len(params),
        value_bck_colors=slice_colors,
        blank_alpha=0.35,
        kwargs_slices=dict(edgecolor=BG_COLOR, zorder=2, linewidth=1.5),
        kwargs_params=dict(color=TEXT_COLOR, fontsize=10, va="center"),
        kwargs_values=dict(color="white", fontsize=10, zorder=3,
                           bbox=dict(edgecolor="white", boxstyle="round,pad=0.2", lw=1)),
    )

    # Encabezado apilado de arriba hacia abajo. Se lleva la cuenta de la altura
    # consumida para después bajar el eje polar y que nada se superponga con
    # las etiquetas del pizza (el bloque crece o se achica según haya cartel de
    # muestra y nota al pie).
    y = 0.980
    fig.text(0.5, y, player_name, size=17, ha="center",
             color=TEXT_COLOR, fontweight="bold")
    y -= 0.026

    team_line = f"{team_label}"
    if context_label:
        team_line += f"  ·  {context_label}"
    fig.text(0.5, y, team_line, size=10, ha="center",
             color=TEXT_COLOR, fontweight="bold")
    y -= 0.028

    # Cartel de muestra: minutos y partidos SIEMPRE visibles, con el aviso de
    # qué tan sólido es lo que se está leyendo. Es lo que permite graficar a
    # todo el plantel sin filtrar por minutos.
    if minutes is not None:
        tier, tier_fg, tier_bg = _sample_tier(minutes)
        partes = [f"{minutes:,.0f}′ jugados".replace(",", ".")]
        if matches is not None:
            partes.append(f"{int(matches)} partido{'s' if int(matches) != 1 else ''}")
        if tier:
            partes.append(tier)
        fig.text(0.5, y, "   ·   ".join(partes), size=10.5, ha="center",
                 va="center", color=tier_fg, fontweight="bold",
                 bbox=dict(facecolor=tier_bg, edgecolor=tier_fg, lw=1.1,
                           boxstyle="round,pad=0.45"))
        y -= 0.026
    if sample_note:
        fig.text(0.5, y, sample_note, size=8.5, ha="center",
                 color=MUTED_COLOR, style="italic")
        y -= 0.020

    # Aclaración clave: el número de cada gajo es un PERCENTIL, no el valor bruto.
    fig.text(0.5, y,
             "Cada número = percentil 0–100 vs jugadores de la Primera Nacional "
             "(100 = el mejor de la liga)",
             size=9, ha="center", color=TEXT_COLOR)
    y -= 0.019
    fig.text(0.5, y,
             "Entre paréntesis, el valor real por 90 minutos",
             size=8.5, ha="center", color=MUTED_COLOR, style="italic")
    y -= 0.014

    # El eje polar arranca debajo del encabezado. El margen extra de 0.03 es
    # porque mplsoccer dibuja las etiquetas de cada gajo POR FUERA del círculo,
    # sobresaliendo del eje: sin ese aire, la etiqueta de arriba se pisa con la
    # última línea del encabezado. El 0.045 de abajo es para la leyenda.
    ax.set_position([0.10, 0.075, 0.80, max(0.5, y - 0.105)])

    # Leyenda de grupos
    x0 = 0.30
    for group, color in PIZZA_GROUP_COLORS.items():
        fig.text(x0, 0.015, f"■ {group.capitalize()}", size=10,
                 color=color, fontweight="bold")
        x0 += 0.15

    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


# ─── Radar clásico (comparación de dos jugadores) ────────────────────────────

def plot_players_radar(comparison, color_a=ACCENT_COLOR, color_b=RIVAL_COLOR,
                       save_path=None):
    """
    Radar clásico comparando DOS jugadores en sus 12 métricas por 90 minutos
    (de analysis.players.compare_players).

    Cómo se lee: cada vértice es una métrica (goles, pases, quites...). Cuanto
    más lejos del centro llega el área de un jugador, más alto es su valor en
    esa métrica. Los ejes están escalados al percentil 5–95 de la Primera
    Nacional, así que el borde exterior ≈ lo mejor de la liga.
    Conviene comparar jugadores de rol parecido (no un arquero con un delantero).
    """
    if not comparison:
        return None

    labels  = comparison["labels"]
    lows    = [r[0] for r in comparison["ranges"]]
    highs   = [r[1] for r in comparison["ranges"]]

    radar = Radar(labels, lows, highs,
                  round_int=[False] * len(labels),
                  num_rings=4, ring_width=1, center_circle_radius=1)

    fig, ax = radar.setup_axis(figsize=(9, 9.6), facecolor=BG_COLOR)
    fig.patch.set_facecolor(BG_COLOR)

    radar.draw_circles(ax=ax, facecolor="#ecece3", edgecolor="#cfcfc6")
    radar.draw_radar_compare(
        comparison["values_a"], comparison["values_b"], ax=ax,
        kwargs_radar={"facecolor": color_a, "alpha": 0.55},
        kwargs_compare={"facecolor": color_b, "alpha": 0.55},
    )
    radar.draw_range_labels(ax=ax, fontsize=8, color=MUTED_COLOR)
    radar.draw_param_labels(ax=ax, fontsize=10, color=TEXT_COLOR)

    fig.text(0.5, 0.965, "Comparación de jugadores — métricas por 90 minutos",
             ha="center", color=TEXT_COLOR, fontsize=14, fontweight="bold")
    fig.text(0.5, 0.938,
             "Más lejos del centro = valor más alto · escala: percentil 5–95 de la liga",
             ha="center", color=TEXT_COLOR, fontsize=9)

    # Leyenda clara con el nombre de cada jugador y su color
    fig.text(0.27, 0.045, f"● {comparison['player_a']}", size=12,
             color=color_a, fontweight="bold", ha="left")
    fig.text(0.60, 0.045, f"● {comparison['player_b']}", size=12,
             color=color_b, fontweight="bold", ha="left")

    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig
