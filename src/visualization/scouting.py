"""
scouting.py (visualization)
===========================
Gráficos del recomendador de jugadores: semáforo del plantel, ranking de
gemelos y mapa 2D del rol.

Mismo tema claro que el resto del proyecto (crema + rojo Chaco / azul rival) y
el mismo contrato: si se pasa `save_path` guarda y devuelve el path; si no,
devuelve la figura.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.visualization.season import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, RIVAL_COLOR, MUTED_COLOR, GRID_COLOR,
    save_fig, _fig_style,
)

# Un color por estado del semáforo, de verde (retener) a rojo (liberar).
COLOR_ESTADO = {
    "PRIORIDAD_RENOVACION": "#0F766E",
    "ROTACION_VALIOSA":     "#0EA5A0",
    "PRESCINDIBLE":         "#D97706",
    "BAJA_PRIORITARIA":     "#DC2626",
    "SIN_EVALUAR":          "#8a8a8a",
}


def _limpiar(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED_COLOR)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.tick_params(colors=TEXT_COLOR)


def plot_semaforo(semaforo_df, title="Auditoría del plantel",
                  subtitle="", save_path=None):
    """Barras horizontales de minutos jugados, coloreadas por estado.

    El eje es el % de minutos del equipo y el color la recomendación: se ve de
    un vistazo si los que más juegan son los que peor rinden."""
    d = semaforo_df.sort_values("pct_minutos_equipo", ascending=True)
    n = len(d)
    fig, ax = plt.subplots(figsize=(10, max(4, n * 0.42)))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)

    y = np.arange(n)
    colores = [COLOR_ESTADO.get(e, MUTED_COLOR) for e in d["estado"]]
    ax.barh(y, d["pct_minutos_equipo"], color=colores, alpha=0.92, zorder=3)

    for yi, (_, r) in zip(y, d.iterrows()):
        pct = r.get("score_pct")
        etiqueta = f"  {r['pct_minutos_equipo']:.0f}%"
        if pd.notna(pct):
            etiqueta += f"  ·  pct rol {pct:.0f}"
        ax.text(r["pct_minutos_equipo"], yi, etiqueta, va="center", ha="left",
                fontsize=8, color=TEXT_COLOR)

    ax.set_yticks(y)
    ax.set_yticklabels([f"{r['nombre']}  ({r['rol']})" for _, r in d.iterrows()],
                       fontsize=9, color=TEXT_COLOR)
    ax.set_xlabel("% de los minutos del equipo", color=TEXT_COLOR)
    # El subtítulo va justo encima del eje y el título más arriba todavía, si no
    # se pisan cuando la figura es alta.
    ax.set_title(title, fontsize=14, color=TEXT_COLOR, fontweight="bold",
                 loc="left", pad=24)
    if subtitle:
        ax.text(0, 1.012, subtitle, transform=ax.transAxes, fontsize=9,
                color=MUTED_COLOR, ha="left", va="bottom")
    ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8, zorder=0)
    _limpiar(ax)
    ax.margins(x=0.16)

    presentes = [e for e in COLOR_ESTADO if e in set(d["estado"])]
    ax.legend(handles=[plt.Line2D([], [], marker="s", linestyle="",
                                  markersize=9, color=COLOR_ESTADO[e],
                                  label=e.replace("_", " ").title())
                       for e in presentes],
              loc="lower right", frameon=False, fontsize=8)
    plt.tight_layout()

    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_gemelos(vecinos_df, jugador, rol="", save_path=None):
    """Ranking de similitud (lollipop). El color marca el percentil del score
    dentro del rol: verde = además de parecido, rinde mejor."""
    d = vecinos_df.dropna(subset=["similitud"]).iloc[::-1]
    n = len(d)
    if n == 0:
        raise ValueError("No hay vecinos para graficar.")

    fig, ax = plt.subplots(figsize=(9, max(3.2, n * 0.45)))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)

    y = np.arange(n)
    pct = d["score_pct"].fillna(50).to_numpy()
    colores = ["#0F766E" if p >= 70 else ("#D97706" if p >= 45 else "#DC2626")
               for p in pct]

    ax.hlines(y, 0, d["similitud"], color=GRID_COLOR, linewidth=2, zorder=2)
    ax.scatter(d["similitud"], y, s=90, color=colores, zorder=3)

    for yi, (_, r) in zip(y, d.iterrows()):
        extra = f"pct {r['score_pct']:.0f}" if pd.notna(r.get("score_pct")) else "s/score"
        ax.annotate(extra, (r["similitud"], yi), textcoords="offset points",
                    xytext=(11, 0), va="center", ha="left",
                    fontsize=8, color=MUTED_COLOR)

    ax.set_yticks(y)
    ax.set_yticklabels([f"{r['nombre']}  ·  {r['equipo']}" for _, r in d.iterrows()],
                       fontsize=9, color=TEXT_COLOR)
    ax.set_xlabel("Similitud (100 = idéntico)", color=TEXT_COLOR)
    titulo = f"Gemelos estadísticos de {jugador}"
    if rol:
        titulo += f"  ·  {rol}"
    ax.set_title(titulo, fontsize=13, color=TEXT_COLOR, fontweight="bold",
                 loc="left", pad=24)
    ax.text(0, 1.012, "Verde = además rinde en el percentil 70+ del puesto",
            transform=ax.transAxes, fontsize=8, color=MUTED_COLOR,
            ha="left", va="bottom")
    ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8, zorder=0)
    _limpiar(ax)
    # Las líneas del lollipop arrancan en 0, así que el eje también: con
    # márgenes automáticos quedaba espacio negativo a la izquierda.
    ax.set_xlim(0, float(d["similitud"].max()) * 1.22)
    plt.tight_layout()

    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig


def plot_mapa_rol(mapa_df, destacar=(), etiquetar_top=0, rol="",
                  save_path=None):
    """
    Nube 2D (PCA) de todos los jugadores del rol.

    Sirve para dos cosas: ver dónde cae el jugador propio respecto de la
    categoría, y detectar roles mal asignados (el que queda solo en un rincón
    suele estar mal etiquetado).
    """
    d = mapa_df.copy()
    fig, ax = plt.subplots(figsize=(9, 7))
    _fig_style(fig)
    ax.set_facecolor(BG_COLOR)

    es_destacado = d["nombre"].isin(destacar)
    resto = d[~es_destacado]
    ax.scatter(resto["pc1"], resto["pc2"], s=46, color=RIVAL_COLOR, alpha=0.38,
               zorder=2, edgecolors="none")

    marcados = d[es_destacado]
    if not marcados.empty:
        ax.scatter(marcados["pc1"], marcados["pc2"], s=150, color=ACCENT_COLOR,
                   zorder=4, edgecolors="white", linewidth=1.4)
        for _, r in marcados.iterrows():
            ax.annotate(r["nombre"], (r["pc1"], r["pc2"]),
                        textcoords="offset points", xytext=(8, 6),
                        fontsize=9, color=ACCENT_COLOR, fontweight="bold")

    if etiquetar_top:
        for _, r in d.nlargest(etiquetar_top, "score_rol").iterrows():
            if r["nombre"] in destacar:
                continue
            ax.annotate(r["nombre"], (r["pc1"], r["pc2"]),
                        textcoords="offset points", xytext=(6, 4),
                        fontsize=7.5, color=MUTED_COLOR)

    var = mapa_df.attrs.get("varianza")
    if var is not None and len(var) >= 2:
        ax.set_xlabel(f"PC1 ({var[0]:.0%} de la varianza)", color=TEXT_COLOR)
        ax.set_ylabel(f"PC2 ({var[1]:.0%})", color=TEXT_COLOR)
    else:
        ax.set_xlabel("PC1", color=TEXT_COLOR)
        ax.set_ylabel("PC2", color=TEXT_COLOR)

    titulo = f"Mapa del puesto — {rol}" if rol else "Mapa del puesto"
    ax.set_title(titulo, fontsize=13, color=TEXT_COLOR, fontweight="bold",
                 loc="left", pad=24)
    ax.text(0, 1.012, f"{len(d)} jugadores de la categoría · cada punto es un jugador",
            transform=ax.transAxes, fontsize=8, color=MUTED_COLOR,
            ha="left", va="bottom")
    ax.grid(color=GRID_COLOR, linewidth=0.7, zorder=0)
    _limpiar(ax)
    plt.tight_layout()

    if save_path:
        save_fig(fig, save_path)
        return save_path
    return fig
