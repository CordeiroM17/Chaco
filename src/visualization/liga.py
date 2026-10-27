"""Visualizaciones para el análisis global del Grupo A: rankings de barras por
equipo, mejor 11 de la fecha en cancha, origen de los remates y la proyección
Monte Carlo de la tabla (src/analysis/simulation.py). Mismo tema claro que el
resto del proyecto."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

from src.visualization.season import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, RIVAL_COLOR, MUTED_COLOR, GRID_COLOR,
    _fig_style, save_fig, light_pitch,
)

# Paleta de estado (descenso/reducido/neutro), reservada aparte de la
# categórica (ACCENT_COLOR=Chaco, RIVAL_COLOR=resto) — mismos tonos que ya
# usan los informes en LaTeX (alertred/accentgreen/warnamber).
DESCENSO_COLOR = "#DC2626"   # rojo — dato negativo
REDUCIDO_COLOR = "#0F766E"   # verde azulado — dato positivo
NEUTRO_COLOR   = "#8a8a8a"   # gris — resto de la tabla

# Fondo de las 3 figuras de la proyección Monte Carlo: el mismo blanco de las
# placas de Instagram (estilo_riesgo.BLANCO = 250,250,248) en vez del crema del
# resto del proyecto, para que al meterlas en el carrusel no se vea el escalón
# entre el fondo de la figura y el de la placa.
PROY_BG = "#fafaf8"

# Rampa secuencial (crema -> azul pizarra) para el heatmap de probabilidad.
_PROB_CMAP = LinearSegmentedColormap.from_list("prob_cmap", [BG_COLOR, RIVAL_COLOR])
# Misma rampa pero arrancando del fondo de la proyección, así las celdas de
# probabilidad ~0 se funden con el fondo de la figura.
_PROB_CMAP_PROY = LinearSegmentedColormap.from_list("prob_cmap_proy",
                                                    [PROY_BG, RIVAL_COLOR])

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


def _blend(color, background, alpha):
    """Mezcla `color` sobre `background` con opacidad `alpha` y devuelve el hex
    resultante. Sirve para conseguir el tono suave que daría alpha, pero
    pintando opaco (sin los artefactos de transparencia al superponer)."""
    from matplotlib.colors import to_rgb, to_hex
    c, b = np.array(to_rgb(color)), np.array(to_rgb(background))
    return to_hex(c * alpha + b * (1 - alpha))


def _norm_key(s):
    """Clave de comparación sin acentos ni mayúsculas: los nombres llegan
    escritos distinto según la fuente ('Club Atlético Colón' en config vs.
    'Club Atletico Colón' en el fixture de SofaScore), y sin normalizar el
    lookup fallaba y el nombre terminaba truncado ('Club Atletic.')."""
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().split())


_SHORT_NAMES_NORM = {_norm_key(k): v for k, v in SHORT_NAMES.items()}


def _short_team(name):
    name = str(name)
    if name in SHORT_NAMES:
        return SHORT_NAMES[name]
    alt = _SHORT_NAMES_NORM.get(_norm_key(name))
    if alt:
        return alt
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


# Orden lateral dentro de cada fila: negativo = carril DER, positivo = carril
# IZQ, 0 = rol central (se queda en el medio de la fila). `_row_positions`
# reparte de carril bajo (18) a alto (82) en ese orden, así que DER cae en los
# valores bajos y IZQ en los altos — calibrado contra el dorsal de los
# jugadores (3 = lateral izquierdo, 4 = lateral derecho en esta liga, ver
# src/analysis/scouting.py) en la fecha 30 (A. Ojeda, dorsal 3, IZQ).
_LANE_KEY = {"IZQ": 1, "DER": -1}


def _lane_sort(sub):
    """Reordena un grupo de una misma fila (G/D/M/F) para que los roles de
    carril (LAT/EXT_MP) queden en los extremos, del lado real que jugaron
    (banda), y los roles centrales (DFC/MCD/MC/DC/ARQ) en el medio. Dentro de
    un mismo grupo lateral/central, se mantiene el orden de rating (el que ya
    trae `xi_df`)."""
    if "banda" not in sub.columns:
        return sub
    key = sub["banda"].map(_LANE_KEY).fillna(0)
    return sub.assign(_lane=key).sort_values(
        "_lane", kind="stable").drop(columns="_lane").reset_index(drop=True)


def plot_best_xi_pitch(xi_df, bench_df=None, formation=(4, 3, 3),
                       round_num="", season="", save_path=None):
    """Dibuja el mejor 11 de la fecha en una cancha vertical (por posición y
    rating), con el banco ideal listado debajo. Si `xi_df` trae la columna
    `rol`/`banda` (ver src/analysis/liga.py:round_player_ratings), además:
    - acomoda a los jugadores de carril (LAT/EXT_MP) en el extremo del carril
      que jugaron ese partido, y a los de rol central en el medio de la fila,
      en vez de repartirlos por orden de rating sin más;
    - marca el rol fino (Lateral, Central, Volante mixto, etc.) debajo del
      nombre, junto al equipo."""
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
        sub = _lane_sort(xi_df[xi_df["position"] == pos].reset_index(drop=True))
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
            pitch.annotate(_short_team(p["team"]), (L - 7.2, W), ax=axp, va="top",
                           ha="center", color=MUTED_COLOR, fontsize=7.3, zorder=6)
            rol_corto = p.get("rol_corto") if "rol_corto" in sub.columns else None
            if rol_corto:
                # línea aparte (no pegado al equipo con " · "): con 4-5
                # jugadores por fila, el texto combinado se pisaba con el del
                # vecino (ver mejor_11 fecha 29, defensa: "Alte. Brown ·
                # CentraGimnasia Y E. · Lateral").
                pitch.annotate(rol_corto, (L - 9.3, W), ax=axp, va="top",
                               ha="center", color=MUTED_COLOR, fontsize=6.6,
                               style="italic", zorder=6)

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
            axb.text(x, y - 0.245, _short_team(p["team"]), ha="center", va="top",
                     fontsize=6.8, color=MUTED_COLOR)
            rol_corto = p.get("rol_corto") if "rol_corto" in bench.columns else None
            if rol_corto:
                # línea aparte, no pegada al equipo: con 5 columnas el texto
                # combinado se pisaba con el chip vecino.
                axb.text(x, y - 0.325, rol_corto, ha="center", va="top",
                         fontsize=6.2, color=MUTED_COLOR, style="italic")
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


# ─── Proyección Monte Carlo de la tabla (Zona A) ─────────────────────────────
# Ver src/analysis/simulation.py — Fase 1 del plan en PLAN_montecarlo_tabla.md.

def plot_position_heatmap(pos_probs_df, highlight="Chaco For Ever",
                          reducido_range=(2, 8), descenso_from=17,
                          n_sims=None, title="Probabilidad de posición final — Zona A",
                          save_path=None, order=None):
    """Heatmap equipo x posición final con la probabilidad (%) de cada
    casillero. Sombrea las columnas de Reducido y descenso, y resalta la
    fila de `highlight`.

    `order`: lista de `team_name` para fijar el orden de filas de arriba a
    abajo (ej. el orden de la tabla ACTUAL, `standings.csv`) — así el lector
    encuentra cada equipo donde está hoy en vez de tener que buscarlo.
    `order=None` (default) ordena por posición media proyectada."""
    pos_cols = [c for c in pos_probs_df.columns if c.startswith("pos_")]
    n_pos = len(pos_cols)
    d = pos_probs_df.copy()
    if order is not None:
        d = d.set_index("team_name").loc[list(order)].reset_index()
    else:
        d["_pos_media"] = sum((i + 1) * d[c] for i, c in enumerate(pos_cols))
        d = d.sort_values("_pos_media").reset_index(drop=True)
    mat = d[pos_cols].to_numpy() * 100  # % para leer directo

    n_teams = len(d)
    fig, ax = plt.subplots(figsize=(15, max(6.5, n_teams * 0.60 + 2.0)))
    _fig_style(fig, bg=PROY_BG)
    ax.set_facecolor(PROY_BG)

    im = ax.imshow(mat, cmap=_PROB_CMAP_PROY, vmin=0, vmax=max(30, mat.max()),
                    aspect="auto", zorder=2)

    # Bandas de Reducido / descenso: franja de color debajo del eje x.
    for p in range(1, n_pos + 1):
        if reducido_range[0] <= p <= reducido_range[1]:
            c = REDUCIDO_COLOR
        elif p >= descenso_from:
            c = DESCENSO_COLOR
        else:
            c = "none"
        if c != "none":
            ax.add_patch(Rectangle((p - 1.5, n_teams - 0.5), 1, 0.4,
                                   color=c, alpha=0.85, clip_on=False, zorder=4))

    # Etiquetas selectivas: solo celdas con probabilidad relevante (>=8%).
    for i in range(n_teams):
        for j in range(n_pos):
            v = mat[i, j]
            if v >= 8:
                txt_color = PROY_BG if v > mat.max() * 0.55 else TEXT_COLOR
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        fontsize=13, fontweight="bold", color=txt_color, zorder=3)

    # Números de posición (1-18): negrita y negro. Van CORRIDOS PARA ABAJO con
    # `pad` para que queden debajo de las bandas verde/roja y no encima: la
    # banda se dibuja sobre la etiqueta y el negro terminaba leyéndose como
    # verde o rojo oscuro. El pad se calcula a partir del alto real de la banda
    # (0.4 unidades de dato) para que sirva con cualquier cantidad de equipos.
    ax.set_xticks(range(n_pos))
    ax.set_xticklabels(range(1, n_pos + 1), fontsize=13, color=TEXT_COLOR,
                       fontweight="bold")
    alto_ejes_pts = (0.795 * fig.get_size_inches()[1]) * 72
    ax.tick_params(axis="x", pad=int(0.4 / max(n_teams, 1) * alto_ejes_pts) + 6)
    ax.set_xlabel("Posición final de Zona A", fontsize=15, color=TEXT_COLOR, labelpad=14)
    names = [_short_team(n) for n in d["team_name"]]
    ax.set_yticks(range(n_teams))
    # Nombres de club en negrita; el de `highlight` ya venía así, en rojo.
    ax.set_yticklabels(names, fontsize=14, color=TEXT_COLOR, fontweight="bold")

    if highlight in list(d["team_name"]):
        hi = d.index[d["team_name"] == highlight][0]
        ax.get_yticklabels()[hi].set_color(ACCENT_COLOR)
        ax.get_yticklabels()[hi].set_fontweight("bold")
        ax.add_patch(Rectangle((-0.5, hi - 0.5), n_pos, 1, fill=False,
                               edgecolor=ACCENT_COLOR, linewidth=2.4, zorder=5))

    subtitle = "Verde = Reducido por posición (2°-8°) · Rojo = descenso (17°-18°)"
    if n_sims:
        subtitle += f" · {n_sims:,} simulaciones".replace(",", ".")
    # Titulo como suptitle (posicion ABSOLUTA en la figura, no relativa a los
    # ejes) y subtitulo como title normal de los ejes -- así no compiten por
    # el mismo hueco y no hay overlap pase lo que pase con el alto de la
    # figura (que varía con la cantidad de equipos).
    fig.suptitle(title, fontsize=22, color=TEXT_COLOR, fontweight="bold",
                x=0.5, y=0.975, ha="center")
    ax.set_title(subtitle, fontsize=14, color=MUTED_COLOR, loc="center", pad=14)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    # Margen fijo alrededor del heatmap (en vez de tight_layout, que lo estira
    # para llenar toda la figura) -- deja aire real arriba/abajo/costados.
    fig.subplots_adjust(left=0.145, right=0.98, top=0.895, bottom=0.10)
    if save_path:
        # save_fig() comparte bbox_inches="tight" sin pad, que recorta este
        # margen a casi nada -- acá se guarda aparte con pad_inches fijo para
        # que el aire alrededor del heatmap sobreviva al guardado.
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight", pad_inches=0.35,
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        return save_path
    return fig


def plot_points_distribution(final_points, pace_points, team_name="Chaco For Ever",
                             title=None, save_path=None):
    """Distribución de puntos finales simulados para un equipo, con la marca
    del ritmo actual extrapolado a toda la temporada (puntos por partido de
    hoy x partidos totales) y la proyección media del modelo. Comparar contra
    el ritmo actual (no contra los puntos de hoy: los finales siempre son más
    altos por acumulación, esa comparación no dice nada)."""
    fig, ax = plt.subplots(figsize=(11, 6.2))
    _fig_style(fig, bg=PROY_BG)
    ax.set_facecolor(PROY_BG)

    lo, hi = int(final_points.min()), int(final_points.max())
    bins = np.arange(lo, hi + 2) - 0.5
    # histtype="stepfilled" dibuja UN solo polígono en vez de una barra por bin:
    # con barras sueltas, el redondeo a píxel de algún borde compartido dejaba
    # una línea vertical del color del fondo cruzando el histograma. El color va
    # pre-mezclado con el fondo en lugar de usar alpha, por el mismo motivo.
    fill = _blend(ACCENT_COLOR, PROY_BG, 0.75)
    ax.hist(final_points, bins=bins, histtype="stepfilled", color=fill,
            edgecolor=ACCENT_COLOR, linewidth=0.8, zorder=3)

    mean_pts = float(final_points.mean())
    # Aire arriba para que los carteles de las dos líneas no se metan entre las
    # barras (antes quedaban tapados por el histograma).
    top = ax.get_ylim()[1] * 1.22
    ax.set_ylim(0, top)

    ax.axvline(pace_points, color=RIVAL_COLOR, linestyle="--", linewidth=2.0, zorder=4)
    ax.axvline(mean_pts, color=TEXT_COLOR, linestyle=":", linewidth=2.0, zorder=4)

    # Los dos carteles van arriba de todo, en filas distintas, y se van para el
    # lado opuesto al de la otra línea para no solaparse cuando están cerca.
    izq_primero = pace_points <= mean_pts
    for val, txt, color, fila, ha in (
        (pace_points, f"ritmo actual: {pace_points:.1f} pts", RIVAL_COLOR, 0.97,
         "right" if izq_primero else "left"),
        (mean_pts, f"proyección media: {mean_pts:.1f} pts", TEXT_COLOR, 0.885,
         "left" if izq_primero else "right"),
    ):
        pad = " " if ha == "left" else ""
        ax.text(val, top * fila, f"{pad}{txt}{'' if ha == 'left' else ' '}",
                color=color, fontsize=13, fontweight="bold", va="top", ha=ha,
                zorder=6,
                bbox=dict(facecolor=PROY_BG, edgecolor=color, lw=1.1,
                          boxstyle="round,pad=0.35", alpha=0.95))

    ax.set_xlabel("Puntos finales de Zona A (simulados)", color=TEXT_COLOR,
                  fontsize=14, labelpad=10)
    ax.set_ylabel("Simulaciones", color=TEXT_COLOR, fontsize=14, labelpad=10)
    ax.tick_params(labelsize=13)
    ttl = title or f"Distribución de puntos finales — {team_name}"
    fig.suptitle(ttl, fontsize=20, color=TEXT_COLOR, fontweight="bold",
                 x=0.5, y=0.975, ha="center")
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED_COLOR)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    fig.subplots_adjust(left=0.10, right=0.975, top=0.90, bottom=0.13)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight", pad_inches=0.3,
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        return save_path
    return fig


def plot_promotion_relegation_bars(proj_df, highlight="Chaco For Ever",
                                   title="Proyección de zona — Zona A",
                                   label_min_pct=9, save_path=None, order=None):
    """Barra 100% apilada por equipo: probabilidad de Reducido por posición /
    mitad de tabla / descenso.

    Prioriza la legibilidad del texto sobre el grosor de las barras: la barra
    es fina (BAR_HEIGHT) y el aire que sobra se usa para agrandar nombres,
    ejes y leyenda. Cada tramo con al menos `label_min_pct`% lleva su número
    adentro, así el dato se lee sin ir a buscar el eje.

    `order`: lista de `team_name` para fijar el orden de filas de arriba a
    abajo (ej. el orden de la tabla ACTUAL, `standings.csv`). `order=None`
    (default) ordena de mejor a peor posición media proyectada.
    """
    if order is not None:
        d = proj_df.set_index("team_name").loc[list(order)].reset_index()
    else:
        d = proj_df.sort_values("posicion_media").reset_index(drop=True)
    mitad = 1 - d["prob_reducido_por_posicion"] - d["prob_descenso"] - d["prob_puntero_zona_a"]
    puntero = d["prob_puntero_zona_a"]
    reducido = d["prob_reducido_por_posicion"]
    descenso = d["prob_descenso"]

    n = len(d)
    BAR_HEIGHT = 0.66         # alto de la barra dentro de la fila (el resto es aire)
    ROW = 0.60                # alto de fila en pulgadas — manda el tamaño de letra
    fig, ax = plt.subplots(figsize=(13, max(5.5, n * ROW + 2.0)))
    _fig_style(fig, bg=PROY_BG)
    ax.set_facecolor(PROY_BG)
    y = np.arange(n)[::-1]

    left = np.zeros(n)
    for vals, color, label in (
        (puntero, "#1a3d5c", "1° (llega a la final)"),
        (reducido, REDUCIDO_COLOR, "Reducido (2°-8°)"),
        (mitad, NEUTRO_COLOR, "Mitad de tabla"),
        (descenso, DESCENSO_COLOR, "Descenso (17°-18°)"),
    ):
        pcts = vals.to_numpy() * 100
        ax.barh(y, pcts, left=left, height=BAR_HEIGHT, color=color, alpha=0.95,
                zorder=3, label=label)
        # Número dentro del tramo (solo si entra sin pisarse con el de al lado).
        for yi, val, l0 in zip(y, pcts, left):
            if val >= label_min_pct:
                ax.text(l0 + val / 2, yi, f"{val:.0f}", ha="center", va="center",
                        fontsize=14, fontweight="bold", color="white", zorder=5)
        left += pcts

    ax.set_yticks(y)
    names = [_short_team(n_) for n_ in d["team_name"]]
    ax.set_yticklabels(names, fontsize=14, color=TEXT_COLOR)
    ax.set_ylim(-0.65, n - 0.35)
    if highlight in list(d["team_name"]):
        hi = list(d["team_name"]).index(highlight)
        ax.get_yticklabels()[hi].set_color(ACCENT_COLOR)
        ax.get_yticklabels()[hi].set_fontweight("bold")
        ax.get_yticklabels()[hi].set_fontsize(15)

    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 20))
    ax.tick_params(axis="x", labelsize=13)
    ax.set_xlabel("% de las simulaciones", color=TEXT_COLOR, fontsize=14, labelpad=12)
    # Título centrado sobre la figura entera (no sobre el eje, que está corrido
    # a la derecha por los nombres de los equipos).
    fig.suptitle(title, fontsize=21, color=TEXT_COLOR, fontweight="bold",
                 x=0.5, y=0.975, ha="center")
    # Leyenda anclada a la FIGURA (no al eje): así queda siempre a la misma
    # distancia del borde inferior, sin importar cuántos equipos haya.
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center",
               bbox_to_anchor=(0.5, 0.005), ncol=4, frameon=False, fontsize=13,
               labelcolor=TEXT_COLOR, handlelength=1.6, handleheight=1.1,
               columnspacing=2.4)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=TEXT_COLOR, length=0)
    # Márgenes fijos en vez de tight_layout: dejan aire real arriba (título) y
    # abajo (eje + leyenda) sin que el alto de la figura los aplaste.
    fig.subplots_adjust(left=0.135, right=0.98, top=0.935, bottom=0.125)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight", pad_inches=0.3,
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        return save_path
    return fig
