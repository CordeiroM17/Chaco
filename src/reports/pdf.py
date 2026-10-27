"""
pdf.py (reports)
================
Exportación del informe de partido a PDF A4, generado 100% con matplotlib
(sin HTML ni dependencias nativas). Compone cada página como una figura A4
donde se incrustan los PNG que ya genera `src/visualization/match.py` más
tarjetas de datos, la "lectura en 30 segundos" y las recomendaciones.

Dos salidas:
- `build_match_pdf`   → informe completo de 6 páginas.
- `build_match_ficha` → ficha de 1 página ("ficha de vestuario").

Los textos (lectura y recomendaciones) se derivan de los datos del partido de
forma determinística (Observación → Dato → Acción), y se pueden sobrescribir.
"""

import os
import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

import config
from src.visualization.season import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, RIVAL_COLOR, MUTED_COLOR, GRID_COLOR,
    SHOT_COLORS,
)

GOLD = "#e0a526"
GREEN = SHOT_COLORS["goal"]
CARD_BG = "#ffffff"

A4 = (8.27, 11.69)  # pulgadas, vertical

# Métricas a mostrar en las tarjetas (nombre en el CSV → etiqueta en español)
_STAT_LABELS = [
    ("Ball possession", "Posesión", "%"),
    ("Expected goals", "xG", ""),
    ("Total shots", "Tiros", ""),
    ("Shots on target", "Al arco", ""),
    ("Goalkeeper saves", "Atajadas", ""),
    ("Corner kicks", "Córners", ""),
    ("Fouls", "Faltas", ""),
    ("Passes", "Pases", ""),
    ("Yellow cards", "Amarillas", ""),
    ("Red cards", "Rojas", ""),
]

_SETPIECE = {"corner", "free-kick", "set-piece", "throw-in-set-piece"}


# ─── Recolección de datos ────────────────────────────────────────────────────

def _match_stats(data, chaco_home):
    """dict metric_es -> (chaco_val, rival_val, unidad) respetando la condición."""
    df = data.get("stats")
    out = {}
    if df is None or df.empty:
        return out
    seen = set()
    for metric, es, unit in _STAT_LABELS:
        row = df[df["metric"] == metric]
        if row.empty or es in seen:
            continue
        seen.add(es)
        hv, av = row.iloc[0]["home_val"], row.iloc[0]["away_val"]
        cv, rv = (hv, av) if chaco_home else (av, hv)
        out[es] = (cv, rv, unit)
    return out


def _goals(data, chaco_home):
    """Lista de goles [(minuto, jugador, es_chaco)]."""
    inc = data.get("incidents")
    if inc is None or inc.empty or "type" not in inc.columns:
        return []
    out = []
    for _, r in inc[inc["type"] == "goal"].iterrows():
        es_chaco = bool(r.get("is_home", True)) == chaco_home
        out.append((r.get("minute"), str(r.get("player", "")), es_chaco))
    return sorted(out, key=lambda x: (x[0] if x[0] is not None else 0))


def gather_context(match_key, season=None):
    """Reúne todo lo necesario para el PDF desde los CSV + gráficos del partido."""
    from src.analysis.post_match import (
        load_match_data, xg_analysis, player_performance_table, match_expected_points)
    from src.analysis.season import (
        get_opponent, get_match_date, is_home_match)

    data = load_match_data(match_key, season)
    ev = None
    if data.get("event") is not None and not data["event"].empty:
        ev = data["event"].iloc[0]

    chaco_home = bool(ev.get("chaco_home")) if ev is not None else is_home_match(match_key)
    if ev is not None:
        rival = ev.get("away_team") if chaco_home else ev.get("home_team")
        fecha = str(ev.get("start_time_utc", ""))[:10]
        venue = ev.get("venue", "")
        referee = ev.get("referee", "")
        ronda = ev.get("round", "")
        torneo = ev.get("tournament", "Primera Nacional")
        chaco_g = ev.get("chaco_goals")
        rival_g = ev.get("rival_goals")
    else:
        rival = get_opponent(match_key)
        fecha = get_match_date(match_key)
        venue = referee = ronda = ""
        torneo = "Primera Nacional"
        chaco_g = rival_g = None

    xg = xg_analysis(match_key, data, season) or {}
    if chaco_g is None:
        chaco_g, rival_g = xg.get("chaco_goals"), xg.get("rival_goals")
    xpoints = match_expected_points(match_key, data, season)

    perf = player_performance_table(match_key, data, season)
    figura = None
    if perf is not None and not perf.empty:
        top = perf.dropna(subset=["rating"]).head(1)
        if not top.empty:
            figura = (top.iloc[0]["player_name"], top.iloc[0]["rating"])

    ctx = {
        "match_key": match_key,
        "rival": rival,
        "fecha": fecha,
        "condicion": "Local" if chaco_home else "Visitante",
        "chaco_home": chaco_home,
        "venue": venue,
        "referee": referee,
        "ronda": ronda,
        "torneo": torneo,
        "chaco_goals": chaco_g,
        "rival_goals": rival_g,
        "xg": xg,
        "xpoints": xpoints,
        "stats": _match_stats(data, chaco_home),
        "goals": _goals(data, chaco_home),
        "figura": figura,
        "shotmap": data.get("shotmap"),
        "graphics_dir": config.match_outputs_dir(match_key, season),
    }
    ctx["reading"] = auto_reading(ctx)
    ctx["recs"] = auto_recommendations(ctx)
    return ctx


# ─── Generación de texto (determinística) ────────────────────────────────────

def _result_word(cg, rg):
    if cg is None or rg is None:
        return "jugó"
    return "ganó" if cg > rg else ("empató" if cg == rg else "perdió")


def auto_reading(ctx):
    """3-4 frases de 'lectura en 30 segundos' derivadas de los datos."""
    cg, rg = ctx["chaco_goals"], ctx["rival_goals"]
    st = ctx["stats"]
    xg = ctx["xg"]
    frases = []

    res = _result_word(cg, rg)
    marcador = f"{cg}-{rg}" if cg is not None else ""
    frases.append(f"Chaco {res} {marcador} como {ctx['condicion'].lower()} ante {ctx['rival']}.")

    xpts = ctx.get("xpoints")
    if xpts:
        frases.append(f"{xg['chaco_xg']:.2f} xG a favor, {xg['rival_xg']:.2f} en contra "
                      f"→ mereció {xpts['xpoints']:.1f} pts, sacó {xpts['real_points']}.")
    elif xg.get("chaco_xg") is not None:
        frases.append(f"En xG fue {xg['chaco_xg']:.2f} a favor y {xg['rival_xg']:.2f} en contra: "
                      + ("dominó las situaciones claras." if xg["chaco_xg"] > xg["rival_xg"] + 0.3
                         else "el rival generó tanto o más peligro." if xg["rival_xg"] > xg["chaco_xg"] + 0.3
                         else "partido parejo en generación."))

    if "Tiros" in st:
        cv, rv, _ = st["Tiros"]
        frases.append(f"Remates: {int(cv)} de Chaco vs {int(rv)} del rival"
                      + (f", con {int(st['Al arco'][1])} llegando al arco propio." if "Al arco" in st else "."))

    if "Posesión" in st:
        cv, _, _ = st["Posesión"]
        frases.append(f"Tuvo el {int(cv)}% de la pelota.")

    if ctx["figura"]:
        frases.append(f"Figura de Chaco: {ctx['figura'][0]} (rating {ctx['figura'][1]}).")

    return frases[:4]


def auto_recommendations(ctx):
    """Recomendaciones Observación→Dato→Acción, separadas en sostener/corregir."""
    st = ctx["stats"]
    xg = ctx["xg"]
    cg, rg = ctx["chaco_goals"], ctx["rival_goals"]
    sostener, corregir = [], []

    def rec(obs, dato, accion):
        return {"obs": obs, "dato": dato, "accion": accion}

    # xG a favor alto
    if xg.get("chaco_xg", 0) >= 1.2:
        sostener.append(rec("Buen volumen de generación ofensiva",
                            f"{xg['chaco_xg']:.2f} xG a favor",
                            "sostener los circuitos que llevan al remate claro"))
    # Arquero / atajadas
    if "Atajadas" in st and st["Atajadas"][0] >= 5:
        sostener.append(rec("Respuesta sólida del arco",
                            f"{int(st['Atajadas'][0])} atajadas",
                            "mantener la figura y la cobertura del área chica"))
    # Pelota parada a favor
    sp_goals = 0
    sm = ctx.get("shotmap")
    if sm is not None and not sm.empty and "situation" in sm.columns:
        chaco_goals_df = sm[(sm["shotType"] == "goal") & (sm["isHome"] == ctx["chaco_home"])]
        sp_goals = int(chaco_goals_df["situation"].astype(str).str.lower().isin(_SETPIECE).sum())
    if sp_goals >= 1:
        sostener.append(rec("Peligro real desde pelota parada",
                            f"{sp_goals} gol(es) de jugada preparada",
                            "seguir trabajando las variantes de ABP"))

    # Tiros concedidos
    if "Tiros" in st and st["Tiros"][1] >= 14:
        corregir.append(rec("Se conceden demasiados remates",
                            f"{int(st['Tiros'][1])} tiros del rival"
                            + (f", {int(st['Al arco'][1])} al arco" if 'Al arco' in st else ""),
                            "cerrar el carril central para bajar el volumen de tiro"))
    # xG en contra alto
    if xg.get("rival_xg", 0) >= 1.2:
        corregir.append(rec("Se concede peligro de calidad",
                            f"{xg['rival_xg']:.2f} xG en contra",
                            "revisar las coberturas en los tramos de más xG rival"))
    # Disciplina
    if "Amarillas" in st and (st["Amarillas"][0] >= 4 or st.get("Rojas", (0, 0, 0))[0] >= 1):
        corregir.append(rec("Alerta de disciplina",
                            f"{int(st['Amarillas'][0])} amarillas"
                            + (f" y {int(st['Rojas'][0])} roja" if st.get('Rojas', (0, 0, 0))[0] >= 1 else ""),
                            "cuidar las faltas evitables y las tarjetas por protesta"))
    # Tenencia baja yendo arriba
    if "Posesión" in st and st["Posesión"][0] <= 40 and cg is not None and rg is not None and cg >= rg:
        corregir.append(rec("Poca tenencia para administrar",
                            f"{int(st['Posesión'][0])}% de posesión",
                            "mejorar la circulación para descansar con pelota cuando se está arriba"))

    if not sostener:
        sostener.append(rec("Actitud competitiva", "partido disputado",
                            "sostener la intensidad como base"))
    if not corregir:
        corregir.append(rec("Margen de mejora ofensiva", "pocas situaciones claras",
                            "buscar más volumen de llegada al área rival"))
    return {"sostener": sostener[:3], "corregir": corregir[:3]}


# ─── Primitivas de dibujo ────────────────────────────────────────────────────

def _new_page():
    fig = plt.figure(figsize=A4)
    fig.patch.set_facecolor(BG_COLOR)
    return fig


def _header(fig, title, subtitle=""):
    fig.patches.append(Rectangle((0, 0.945), 1, 0.055, transform=fig.transFigure,
                                 color=ACCENT_COLOR, zorder=1))
    fig.text(0.055, 0.9725, title, color="white", fontsize=15, fontweight="bold",
             va="center", zorder=2)
    if subtitle:
        fig.text(0.945, 0.9725, subtitle, color="white", fontsize=9.5,
                 va="center", ha="right", zorder=2, alpha=0.9)


def _footer(fig, page, total):
    hoy = datetime.date.today().isoformat()
    fig.text(0.055, 0.02, "Fuente: SofaScore", color=MUTED_COLOR, fontsize=7.5,
             va="center")
    fig.text(0.5, 0.02, f"Generado {hoy}", color=MUTED_COLOR, fontsize=7.5,
             va="center", ha="center")
    fig.text(0.945, 0.02, f"{page}/{total}", color=MUTED_COLOR, fontsize=7.5,
             va="center", ha="right")


def _card(fig, rect, facecolor=CARD_BG, edgecolor=GRID_COLOR, lw=1.0):
    x, y, w, h = rect
    fig.patches.append(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
        transform=fig.transFigure, facecolor=facecolor, edgecolor=edgecolor,
        lw=lw, zorder=0.5, mutation_aspect=A4[0] / A4[1]))


def _place_image(fig, path, rect):
    """Incrusta un PNG dentro de `rect` (fracción de figura) manteniendo aspecto."""
    if not path or not os.path.exists(path):
        x, y, w, h = rect
        fig.text(x + w / 2, y + h / 2, "(gráfico no disponible)", ha="center",
                 va="center", color=MUTED_COLOR, fontsize=8, style="italic")
        return None
    img = mpimg.imread(path)
    ih, iw = img.shape[0], img.shape[1]
    x, y, w, h = rect
    figW, figH = fig.get_size_inches()
    img_aspect = iw / ih
    box_aspect = (w * figW) / (h * figH)
    if img_aspect > box_aspect:
        nw = w
        nh = (w * figW / img_aspect) / figH
    else:
        nh = h
        nw = (h * figH * img_aspect) / figW
    ax = fig.add_axes([x + (w - nw) / 2, y + (h - nh) / 2, nw, nh])
    ax.set_zorder(2)  # por encima de las tarjetas (FancyBboxPatch zorder 0.5)
    ax.imshow(img)
    ax.axis("off")
    return ax


def _caption(fig, rect, text):
    x, y, w, h = rect
    fig.text(x + w / 2, y - 0.006, text, ha="center", va="top", fontsize=7.5,
             color=MUTED_COLOR, style="italic", wrap=True)


def _g(ctx, name):
    return os.path.join(ctx["graphics_dir"], name)


# ─── Bloques compuestos ──────────────────────────────────────────────────────

def _short_rival(name):
    """Acorta el nombre del rival para el scoreboard (saca 'Club Atlético', etc.)."""
    s = str(name).strip()
    for pre in ("Club Atlético ", "Club Atletico ", "Atlético ", "Atletico ",
                "Asociación ", "Asociacion ", "Club "):
        if s.startswith(pre):
            s = s[len(pre):]
    s = s.replace(" Juniors", "")
    return s.strip()


def _scoreboard(fig, ctx, y=0.80, h=0.10):
    cg = ctx["chaco_goals"] if ctx["chaco_goals"] is not None else "?"
    rg = ctx["rival_goals"] if ctx["rival_goals"] is not None else "?"
    _card(fig, (0.055, y, 0.89, h), facecolor=CARD_BG)
    cy = y + h / 2
    rival = _short_rival(ctx["rival"]).upper()
    rsize = 13 if len(rival) <= 16 else (11 if len(rival) <= 24 else 9)
    # Nombres alineados hacia afuera para no pisar el marcador central
    fig.text(0.44, cy, "CHACO FOR EVER", ha="right", va="center",
             fontsize=13, fontweight="bold", color=ACCENT_COLOR)
    fig.text(0.56, cy, rival, ha="left", va="center",
             fontsize=rsize, fontweight="bold", color=RIVAL_COLOR)
    fig.text(0.50, cy, f"{cg} - {rg}", ha="center", va="center",
             fontsize=26, fontweight="bold", color=TEXT_COLOR)
    parts = [str(ctx["torneo"])]
    if ctx["ronda"] and str(ctx["ronda"]).lower() != "nan":
        parts.append(f"Fecha {ctx['ronda']}")
    parts += [str(ctx["fecha"]), ctx["condicion"]]
    if ctx["venue"] and str(ctx["venue"]).lower() != "nan":
        parts.append(str(ctx["venue"]))
    fig.text(0.50, y - 0.018, "  ·  ".join(parts), ha="center", va="top",
             fontsize=8.5, color=MUTED_COLOR)


def _reading_box(fig, ctx, rect):
    x, y, w, h = rect
    _card(fig, rect, facecolor=CARD_BG, edgecolor=GOLD, lw=1.4)
    fig.text(x + 0.02, y + h - 0.022, "LA LECTURA EN 30 SEGUNDOS",
             fontsize=10, fontweight="bold", color=GOLD, va="center")
    ty = y + h - 0.05
    for frase in ctx["reading"]:
        fig.text(x + 0.02, ty, "•  " + frase, fontsize=9, color=TEXT_COLOR,
                 va="top", wrap=True)
        ty -= 0.032


def _stats_cards(fig, ctx, rect):
    """Grilla compacta de tarjetas de estadística Chaco vs rival."""
    x, y, w, h = rect
    st = ctx["stats"]
    items = [(es, v) for es, v in st.items()]
    if not items:
        return
    n = len(items)
    cols = 2
    rows = (n + cols - 1) // cols
    cw = w / cols
    ch = h / rows
    for i, (es, (cv, rv, unit)) in enumerate(items):
        r, c = divmod(i, cols)
        cx = x + c * cw
        cy = y + h - (r + 1) * ch
        _card(fig, (cx + 0.006, cy + 0.004, cw - 0.012, ch - 0.008))
        fig.text(cx + cw / 2, cy + ch - 0.016, es, ha="center", va="center",
                 fontsize=8, color=MUTED_COLOR)
        def fmt(v):
            return f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)
        fig.text(cx + cw * 0.30, cy + 0.012, fmt(cv), ha="center", va="center",
                 fontsize=12.5, fontweight="bold", color=ACCENT_COLOR)
        fig.text(cx + cw * 0.70, cy + 0.012, fmt(rv), ha="center", va="center",
                 fontsize=12.5, fontweight="bold", color=RIVAL_COLOR)


def _recs_block(fig, ctx, rect):
    import textwrap
    x, y, w, h = rect
    recs = ctx["recs"]
    colw = w / 2

    def _lines(fig, tx, ty, text, width, fontsize, color, weight="normal"):
        for ln in textwrap.wrap(text, width=width):
            fig.text(tx, ty, ln, fontsize=fontsize, color=color,
                     fontweight=weight, va="top")
            ty -= 0.020
        return ty

    def col(cx, titulo, items, color):
        fig.text(cx + 0.02, y + h - 0.025, titulo, fontsize=11, fontweight="bold",
                 color=color, va="center")
        ty = y + h - 0.06
        for it in items:
            ty = _lines(fig, cx + 0.02, ty, f"▸ {it['obs']}", 40, 9,
                        TEXT_COLOR, "bold")
            ty -= 0.004
            ty = _lines(fig, cx + 0.035, ty, f"Dato: {it['dato']}", 50, 8,
                        MUTED_COLOR)
            ty = _lines(fig, cx + 0.035, ty, f"Acción: {it['accion']}", 50, 8,
                        color)
            ty -= 0.018

    _card(fig, (x, y, colw - 0.01, h), edgecolor=GREEN, lw=1.3)
    _card(fig, (x + colw + 0.01, y, colw - 0.01, h), edgecolor=ACCENT_COLOR, lw=1.3)
    col(x, "A FAVOR / A SOSTENER", recs["sostener"], GREEN)
    col(x + colw + 0.01, "A CORREGIR", recs["corregir"], ACCENT_COLOR)


# ─── Páginas del informe completo ────────────────────────────────────────────

def _page_portada(fig, ctx, page, total):
    _header(fig, "Informe de Partido", "Chaco For Ever")
    _scoreboard(fig, ctx, y=0.82, h=0.095)

    # goles
    goles = ctx["goals"]
    if goles:
        txt = "Goles:   " + "    ·    ".join(
            f"{p} {int(m)}'" + ("" if es else " (riv)")
            for m, p, es in goles if p)
        fig.text(0.5, 0.775, txt, ha="center", va="center", fontsize=8.5,
                 color=TEXT_COLOR)

    _reading_box(fig, ctx, (0.055, 0.50, 0.52, 0.24))
    # figura
    if ctx["figura"]:
        _card(fig, (0.055, 0.40, 0.52, 0.08), facecolor=CARD_BG)
        fig.text(0.075, 0.455, "FIGURA DE CHACO", fontsize=9, color=MUTED_COLOR,
                 va="center")
        fig.text(0.075, 0.425, f"{ctx['figura'][0]}", fontsize=13,
                 fontweight="bold", color=ACCENT_COLOR, va="center")
        fig.text(0.55, 0.44, f"{ctx['figura'][1]}", fontsize=20,
                 fontweight="bold", color=TEXT_COLOR, va="center", ha="right")

    # comparación de estadísticas (imagen) al costado
    _card(fig, (0.60, 0.40, 0.345, 0.34))
    fig.text(0.7725, 0.715, "ESTADÍSTICAS", ha="center", fontsize=9,
             color=MUTED_COLOR)
    _place_image(fig, _g(ctx, "stats_comparacion.png"), (0.61, 0.41, 0.325, 0.30))

    # tarjetas de stats abajo
    _stats_cards(fig, ctx, (0.055, 0.08, 0.89, 0.28))
    _footer(fig, page, total)


def _page_relato(fig, ctx, page, total):
    _header(fig, "Relato del Partido", "momentum · xG acumulado · timeline")
    _place_image(fig, _g(ctx, "momentum.png"), (0.06, 0.66, 0.88, 0.24))
    _caption(fig, (0.06, 0.66, 0.88, 0.24), "Dominio territorial minuto a minuto")
    _place_image(fig, _g(ctx, "xg_acumulado.png"), (0.06, 0.37, 0.88, 0.24))
    _caption(fig, (0.06, 0.37, 0.88, 0.24), "Carrera de xG: peligro real acumulado minuto a minuto")
    _place_image(fig, _g(ctx, "timeline.png"), (0.06, 0.08, 0.88, 0.24))
    _caption(fig, (0.06, 0.08, 0.88, 0.24), "Goles, cambios y tarjetas en el tiempo")
    _footer(fig, page, total)


def _page_ocasiones(fig, ctx, page, total):
    _header(fig, "Ocasiones", "calidad de las situaciones de cada lado")
    _place_image(fig, _g(ctx, "shotmap_chaco.png"), (0.06, 0.50, 0.88, 0.40))
    _caption(fig, (0.06, 0.50, 0.88, 0.40), "Remates de Chaco (tamaño = xG)")
    _place_image(fig, _g(ctx, "shotmap_rival.png"), (0.06, 0.09, 0.88, 0.40))
    _caption(fig, (0.06, 0.09, 0.88, 0.40), "Remates del rival (tamaño = xG)")
    _footer(fig, page, total)


def _page_estructura(fig, ctx, page, total):
    _header(fig, "Estructura y Territorio", "cómo se paró y por dónde jugó")
    _place_image(fig, _g(ctx, "posiciones_promedio.png"), (0.06, 0.60, 0.44, 0.30))
    _caption(fig, (0.06, 0.60, 0.44, 0.30), "Posiciones promedio de Chaco")
    _place_image(fig, _g(ctx, "heatmap_equipo.png"), (0.52, 0.60, 0.44, 0.30))
    _caption(fig, (0.52, 0.60, 0.44, 0.30), "Territorio (mapa de calor)")
    _place_image(fig, _g(ctx, "radios_accion.png"), (0.06, 0.14, 0.44, 0.40))
    _caption(fig, (0.06, 0.14, 0.44, 0.40), "Radio de acción de Chaco")
    _place_image(fig, _g(ctx, "radios_accion_rival.png"), (0.52, 0.14, 0.44, 0.40))
    _caption(fig, (0.52, 0.14, 0.44, 0.40), "Radio de acción del rival")
    _footer(fig, page, total)


def _page_individual(fig, ctx, page, total):
    _header(fig, "Rendimiento Individual", "ratings y acciones defensivas")
    _place_image(fig, _g(ctx, "ratings_jugadores.png"), (0.06, 0.50, 0.88, 0.40))
    _caption(fig, (0.06, 0.50, 0.88, 0.40), "Puntajes de los jugadores de Chaco")
    _place_image(fig, _g(ctx, "defensivo.png"), (0.06, 0.09, 0.88, 0.40))
    _caption(fig, (0.06, 0.09, 0.88, 0.40), "Acciones defensivas por jugador")
    _footer(fig, page, total)


def _page_recomendaciones(fig, ctx, page, total):
    _header(fig, "Recomendaciones Post-Partido", "Observación → Dato → Acción")
    _recs_block(fig, ctx, (0.055, 0.30, 0.89, 0.60))
    fig.text(0.5, 0.25, "Cada recomendación se apoya en un dato o gráfico de las "
             "páginas anteriores.", ha="center", fontsize=8.5, color=MUTED_COLOR,
             style="italic")
    _footer(fig, page, total)


# ─── API pública ─────────────────────────────────────────────────────────────

def build_match_pdf(match_key, season=None, ctx=None, out_path=None):
    """
    Informe completo de 6 páginas en PDF A4. Devuelve la ruta del PDF.
    """
    ctx = ctx or gather_context(match_key, season)
    if out_path is None:
        out_path = os.path.join(ctx["graphics_dir"], "informe_partido.pdf")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    pages = [_page_portada, _page_relato, _page_ocasiones,
             _page_estructura, _page_individual, _page_recomendaciones]
    total = len(pages)
    with PdfPages(out_path) as pdf:
        for i, page_fn in enumerate(pages, start=1):
            fig = _new_page()
            page_fn(fig, ctx, i, total)
            pdf.savefig(fig, facecolor=fig.get_facecolor())
            plt.close(fig)
    print(f"[OK] PDF de 6 páginas: {out_path}")
    return out_path


def build_match_ficha(match_key, season=None, ctx=None, out_path=None):
    """
    Ficha de 1 página ("ficha de vestuario"): marcador, xG, lectura, 4
    recomendaciones y foto-resumen de posiciones. Devuelve la ruta del PDF.
    """
    ctx = ctx or gather_context(match_key, season)
    if out_path is None:
        out_path = os.path.join(ctx["graphics_dir"], "ficha_partido.pdf")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with PdfPages(out_path) as pdf:
        fig = _new_page()
        _header(fig, "Ficha de Partido", "Chaco For Ever")
        _scoreboard(fig, ctx, y=0.83, h=0.095)

        # xG destacado
        xg = ctx["xg"]
        if xg.get("chaco_xg") is not None:
            _card(fig, (0.055, 0.745, 0.89, 0.055))
            fig.text(0.5, 0.7725, f"xG   {xg['chaco_xg']:.2f}  –  {xg['rival_xg']:.2f}   "
                     f"·   {xg.get('verdict', '')}", ha="center", va="center",
                     fontsize=10, color=TEXT_COLOR)

        _reading_box(fig, ctx, (0.055, 0.50, 0.52, 0.225))
        _place_image(fig, _g(ctx, "posiciones_promedio.png"), (0.60, 0.485, 0.345, 0.245))
        _caption(fig, (0.60, 0.485, 0.345, 0.245), "Posiciones promedio")

        # recomendaciones (4, condensadas)
        _recs_block(fig, ctx, (0.055, 0.07, 0.89, 0.40))
        _footer(fig, 1, 1)
        pdf.savefig(fig, facecolor=fig.get_facecolor())
        plt.close(fig)
    print(f"[OK] Ficha de 1 página: {out_path}")
    return out_path
