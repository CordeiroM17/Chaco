"""Generador del informe estándar de temporada de un equipo del grupo, en LaTeX,
para vender el servicio a los clubes. Marca de la consultora (Cordeiro & Casco)
con el club destinatario en el título; estructura objetiva primero y espacios de
narrativa (\\slot) para personalizar antes de enviar.

Uso:
    from src.analysis import liga
    from src.reports.liga import build_team_report_tex, compile_tex
    res = liga.generate_team_graphics('san_telmo')
    tex = build_team_report_tex(res, destinatario='Club Atlético San Telmo')
    # se guarda y compila desde el notebook
"""
import os
import pandas as pd

import config

_PREAMBLE = r"""\documentclass[11pt, a4paper]{article}
\usepackage[a4paper, top=2.5cm, bottom=2.5cm, left=2cm, right=2cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{array}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{graphicx}
\graphicspath{{./}{./graficos/}}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{lastpage}
\usepackage[section]{placeins}
\usepackage[hidelinks]{hyperref}
\usepackage[spanish, es-tabla]{babel}
\usepackage{enumitem}
\setlist[itemize]{label=-}

\definecolor{primary}{HTML}{0F172A}
\definecolor{alertred}{HTML}{DC2626}
\definecolor{accentgreen}{HTML}{0F766E}
\definecolor{warnamber}{HTML}{D97706}
\definecolor{lightgray}{HTML}{F8FAFC}
\definecolor{darkgray}{HTML}{475569}
\definecolor{slotgray}{HTML}{EEF2F7}

% Espacio de narrativa editable (se completa a mano antes de enviar).
\newcommand{\slot}[1]{%
  \par\noindent\colorbox{slotgray}{%
    \parbox{\dimexpr\textwidth-2\fboxsep\relax}{%
      \raggedright\smallskip
      \small\textit{\color{darkgray}[ Espacio para análisis — #1 ]}\par\smallskip}}%
  \par\vspace{3mm}}
\newcommand{\databox}[2]{%
  \noindent\colorbox{lightgray}{%
    \parbox{\dimexpr\textwidth-2\fboxsep\relax}{%
      \raggedright\smallskip
      \textbf{\color{primary}{#1}}\par\smallskip
      \small #2\par\smallskip}}%
  \par\vspace{3mm}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}
\fancyhead[L]{\small\color{darkgray}\textsc{__NAME__} $\bullet$ Análisis de Temporada}
\fancyhead[R]{\small\color{darkgray}Temporada __SEASON__}
\fancyfoot[L]{\footnotesize\color{darkgray}Preparado por Cordeiro \& Casco $\bullet$ Análisis de datos deportivos}
\fancyfoot[R]{\footnotesize\color{darkgray}Página \thepage\ de \pageref{LastPage}}

\titleformat{\section}{\normalfont\Large\bfseries\color{primary}}{\thesection}{0.6em}{}[\vspace{-2mm}\noindent{\color{accentgreen}\rule{\textwidth}{1.2pt}}]
\titlespacing*{\section}{0pt}{4mm}{4mm}
\titleformat{\subsection}{\normalfont\large\bfseries\color{darkgray}}{\thesubsection}{0.6em}{}
\titlespacing*{\subsection}{0pt}{3mm}{2mm}
"""

_HEADER = r"""\begin{document}
\begin{center}
  \colorbox{primary}{%
    \parbox{\dimexpr\textwidth-2\fboxsep\relax}{%
      \vspace{4mm}\centering\color{white}
      \textsc{\large Análisis de Datos Deportivos} \\ \vspace{1mm}
      \textbf{\Large ANÁLISIS DE RENDIMIENTO} \\ \vspace{1mm}
      \textbf{\Large __NAME__} \\ \vspace{1mm}
      \small Temporada __SEASON__ (Primera Nacional) $\bullet$ Muestra: __NMATCH__ partidos
      \vspace{4mm}}}
\end{center}
\vspace{3mm}
\begin{tabular}{ll}
  \textbf{Destinatario:} & __DEST__ \\
  \textbf{Preparado por:} & Cordeiro Mariano Ángel y Casco Tobías Andrés \\
  \textbf{Contacto:} & cordeiromariano17@gmail.com $\bullet$ +54 3644 645142 \\
  \textbf{Alcance:} & Rendimiento del equipo en la temporada __SEASON__, con datos y métricas avanzadas \\
\end{tabular}
\vspace{3mm}
\noindent\colorbox{lightgray}{%
  \parbox{\dimexpr\textwidth-2\fboxsep\relax}{%
    \smallskip
    \small Este informe presenta primero los \textbf{datos objetivos} del rendimiento del equipo
    (resultados, ataque, defensa, jugadores) y reserva los espacios de \textbf{interpretación} para el
    cierre. Es una muestra del tipo de análisis que ofrecemos fecha a fecha.\smallskip}}
\vspace{2mm}
\hrule
\vspace{3mm}
"""


def _fig(graphics, fname, caption, width=0.9):
    if fname not in graphics:
        return ""
    return (f"\\begin{{figure}}[htbp]\n  \\centering\n"
            f"  \\fbox{{\\includegraphics[width={width}\\textwidth]{{{fname}}}}}\n"
            f"  \\caption{{{caption}}}\n\\end{{figure}}\n\n")


def _tex_escape(s):
    return (str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_"))


def build_team_report_tex(res, destinatario=None):
    """Arma el string LaTeX del informe estándar del equipo a partir del dict
    que devuelve liga.generate_team_graphics()."""
    name = res["name"]; season = str(res["season"])
    st = res["stats"]; pdf = res["player_df"]; g = set(res["graphics"])
    dest = destinatario or f"Cuerpo Técnico y Dirigencia de {name}"

    def s(k, d="N/D"):
        v = st.get(k)
        return d if v is None else v

    pre = (_PREAMBLE.replace("__NAME__", _tex_escape(name)).replace("__SEASON__", season))
    head = (_HEADER.replace("__NAME__", _tex_escape(name)).replace("__SEASON__", season)
            .replace("__NMATCH__", str(res["n_matches"])).replace("__DEST__", _tex_escape(dest)))

    out = [pre, head]

    # ── 1. Resumen ──
    out.append(r"\section*{1. Resumen de la Temporada}" + "\n")
    out.append(
        f"En los {res['n_matches']} partidos analizados, {name} registra "
        f"{s('victorias')}V-{s('empates')}E-{s('derrotas')}D ({s('puntos')} puntos), "
        f"con {s('goles_favor')} goles a favor y {s('goles_contra')} en contra.\n\n")
    out.append(r"\databox{Números de la temporada}{" +
               f"Récord: {s('victorias')}V-{s('empates')}E-{s('derrotas')}D "
               f"({s('puntos')} pts). Goles: {s('goles_favor')} a favor / {s('goles_contra')} en contra. "
               f"xG: {s('xg_favor')} a favor / {s('xg_contra')} en contra. "
               f"Local: {_tex_escape(s('rendimiento_local'))} $\\bullet$ Visitante: {_tex_escape(s('rendimiento_visitante'))}."
               + "}\n\n")
    out.append(_fig(g, "puntos_acumulados.png", f"Puntos acumulados de {_tex_escape(name)} a lo largo de la temporada.", 0.9))
    out.append(_fig(g, "forma_reciente.png", "Forma reciente (media móvil de 5 partidos): rachas por encima y por debajo del promedio.", 0.9))
    out.append(r"\slot{lectura general del momento del equipo}" + "\n\n")

    # ── 2. Ataque ──
    out.append(r"\section*{2. Ataque}" + "\n")
    out.append(
        "Volumen y calidad de las situaciones de gol generadas: de dónde patea, "
        "qué tan variado es su ataque y por qué vías genera peligro.\n\n")
    out.append(_fig(g, "xg_temporada.png", "Goles vs. xG a lo largo de la temporada: eficacia en la definición.", 0.9))
    out.append(_fig(g, "shotmap_temporada.png", "Mapa de tiros de la temporada (gol / atajado / desviado / bloqueado); tamaño del punto según xG.", 0.98))
    out.append(_fig(g, "amenaza_por_jugada.png", "Amenaza por tipo de jugada: goles y xG a favor y en contra según la situación (juego abierto, pelota parada, etc.).", 0.98))
    out.append(_fig(g, "entropia_tiros.png", "Entropía del mapa de tiros: qué tan predecible o variado es el origen del peligro.", 0.6))
    out.append(_fig(g, "toques_ultimo_tercio.png", "Toques en el último tercio / área rival por jugador: participación ofensiva real.", 0.9))
    out.append(r"\slot{fortalezas y vías de peligro del ataque}" + "\n\n")

    # ── 3. Defensa ──
    out.append(r"\section*{3. Defensa y Gestión del Partido}" + "\n")
    out.append(_fig(g, "tiros_concedidos_temporada.png", "Mapa de tiros concedidos: dónde le generan peligro al equipo durante el año.", 0.98))
    out.append(_fig(g, "xg_por_estado_marcador.png", "xG generado y concedido según el estado del marcador: cómo gestiona ir ganando, empatando o perdiendo.", 0.9))
    out.append(_fig(g, "markov_marcador.png", "Cadena de Markov del marcador: probabilidad de mover el resultado gol a gol (madurez para sostener o revertir).", 0.6))
    out.append(_fig(g, "riesgo_defensivo_cox.png", "Modelo de riesgo defensivo (Cox): factores asociados a recibir el primer remate peligroso. Señal direccional.", 0.85))
    out.append(r"\slot{solidez defensiva y momentos de riesgo}" + "\n\n")

    # ── 4. Jugadores y plantel ──
    out.append(r"\section*{4. Jugadores y Plantel}" + "\n")
    if pdf is not None and not pdf.empty:
        # Goleadores
        top = pdf.sort_values("goles", ascending=False).head(5)
        out.append(r"\subsection*{Goleadores}" + "\n")
        out.append(r"\begin{table}[h!]\centering\begin{tabular}{lccc}\toprule" + "\n")
        out.append(r"\textbf{Jugador} & \textbf{Goles} & \textbf{xG} & \textbf{PJ} \\\midrule" + "\n")
        for _, r in top.iterrows():
            out.append(f"{_tex_escape(r['player'])} & {int(r['goles'])} & {r['xg_total']:.2f} & {int(r['partidos'])} \\\\\n")
        out.append(r"\bottomrule\end{tabular}\end{table}" + "\n\n")
        # Mejor rating (min 600')
        rdf = pdf[pdf["minutos"] >= 600].dropna(subset=["rating_promedio"]).sort_values("rating_promedio", ascending=False).head(5)
        if not rdf.empty:
            out.append(r"\subsection*{Mejores promedios (mín. 600')}" + "\n")
            out.append(r"\begin{table}[h!]\centering\begin{tabular}{lccc}\toprule" + "\n")
            out.append(r"\textbf{Jugador} & \textbf{Rating} & \textbf{Min} & \textbf{PJ} \\\midrule" + "\n")
            for _, r in rdf.iterrows():
                out.append(f"{_tex_escape(r['player'])} & {r['rating_promedio']:.2f} & {int(r['minutos'])} & {int(r['partidos'])} \\\\\n")
            out.append(r"\bottomrule\end{tabular}\end{table}" + "\n\n")
    out.append(_fig(g, "top_rating.png", "Jugadores mejor puntuados de la temporada (mínimo 600 minutos).", 0.9))
    out.append(_fig(g, "top_minutos.png", "Jugadores más utilizados por minutos.", 0.9))
    out.append(_fig(g, "disciplina.png", "Disciplina: amarillas y rojas por jugador; marca a los que están al borde de la suspensión.", 0.9))
    out.append(_fig(g, "red_asistencias.png", "Red de asistencias: quién habilita a quién en los goles.", 0.9))
    out.append(_fig(g, "red_minutos_compartidos.png", "Red de minutos compartidos: duplas más frecuentes y rendimiento del equipo con ellas.", 0.9))
    out.append(_fig(g, "nucleo_tactico.png", "Núcleo táctico (centralidad): jugadores que más potencian al equipo, más allá de sus números individuales.", 0.85))
    out.append(_fig(g, "calendario_carga.png", "Calendario de carga: minutos por jugador y descanso entre fechas (para decidir rotaciones).", 0.98))
    out.append(r"\slot{jugadores clave, dependencias y decisiones de plantel}" + "\n\n")

    # ── 5. Local vs Visitante ──
    out.append(r"\section*{5. Local vs. Visitante}" + "\n")
    out.append(_fig(g, "local_vs_visitante.png", "Rendimiento según la condición: puntos, goles y xG por partido de local y de visitante.", 0.85))
    out.append(r"\slot{diferencias de rendimiento según la cancha}" + "\n\n")

    # ── 6. Conclusiones ──
    out.append(r"\section*{6. Conclusiones e Interpretación}" + "\n")
    out.append("Hasta acá, los datos. Este espacio es para nuestra lectura del equipo y las "
               "recomendaciones que surjan del análisis.\n\n")
    out.append(r"\slot{síntesis del rendimiento, fortalezas y áreas de mejora}" + "\n\n")
    out.append(r"\slot{recomendaciones concretas para el cuerpo técnico}" + "\n\n")

    out.append(r"\end{document}" + "\n")
    return "".join(out)


# ─── Sección: Proyección Monte Carlo de la tabla (Fase 1, Zona A) ────────────
# Ver PLAN_montecarlo_tabla.md y src/analysis/simulation.py. Pensada para
# insertarse en un documento que ya cargue el preámbulo de este módulo (mismos
# macros \databox / \slot / colores). Objetividad primero: probabilidades y
# tabla de datos antes que cualquier interpretación, que queda en un \slot.

_PROJECTION_FIGS = ("posicion_probabilidad.png", "distribucion_puntos.png", "proyeccion_zona.png")


def build_projection_section_tex(sims, proj_df, team_name="Chaco For Ever",
                                 section_num="7", graphics=None, graphics_prefix="",
                                 season=None):
    """
    Arma el fragmento LaTeX de la sección de proyección de tabla para
    `team_name`, a partir de:
      - sims: dict que devuelve simulation.simulate_season()
      - proj_df: DataFrame de simulation.promotion_relegation_probabilities()
      - graphics: nombres de PNG realmente generados (ej. las claves de
        `res['graphics']` que devuelve liga.generate_projection_graphics()).
        Si es None, asume que los 3 gráficos estándar existen.
      - season: para buscar la posición ACTUAL de `team_name` en
        `standings.csv` y mostrarla junto a la proyectada — sin esto, el
        lector puede confundir "posición proyectada" (orden final esperado
        a fin de temporada) con la posición de hoy, que suele ser distinta
        porque el modelo reparte los partidos restantes según el nivel
        reciente de cada equipo, no según la tabla actual.
    """
    graphics = set(graphics) if graphics is not None else set(_PROJECTION_FIGS)
    row = proj_df[proj_df["team_name"] == team_name]
    if row.empty:
        raise ValueError(f"'{team_name}' no está en proj_df — revisar el nombre exacto.")
    row = row.iloc[0]
    n_sims = sims["n_sims"]
    n_remaining = sims["n_remaining"]
    n_teams = len(sims["team_ids"])

    actual_txt = ""
    try:
        from src.scraping.standings_scraper import load_standings
        st = load_standings(season or config.CURRENT_SEASON)
        st_row = st[st["team_name"] == team_name]
        if not st_row.empty:
            st_row = st_row.iloc[0]
            deg_ = r"$^\circ$"
            actual_txt = (f"Hoy está \\textbf{{{int(st_row['position'])}{deg_}}} "
                          f"con {int(st_row['points'])} pts en "
                          f"{int(st_row['matches_played'])} PJ. ")
    except Exception:
        pass

    p_desc = row["prob_descenso"] * 100
    p_red  = row["prob_reducido_por_posicion"] * 100
    p_1ro  = row["prob_puntero_zona_a"] * 100
    pos_media = row["posicion_media"]
    pos_mediana = int(row["posicion_mediana"])

    # Resaltado \mR (riesgo) / \mG (positivo) / \mA (neutro/clave), igual que
    # el resto de los informes del repo.
    desc_mark = r"\mR" if p_desc >= 15 else (r"\mA" if p_desc >= 5 else None)
    desc_txt = f"{desc_mark}{{{p_desc:.0f}\\%}}" if desc_mark else f"{p_desc:.0f}\\%"

    n_sims_es = f"{n_sims:,}".replace(",", ".")  # separador de miles en formato es-AR

    out = []
    # OJO: — (em dash) en modo texto también rompe con este preámbulo
    # (mismo bug de fuente que el de °, línea de abajo) — se usa " - " como
    # ya hace el resto de los informes del repo (ej. "9V - 8E - 4D").
    half_life = sims.get("half_life")
    es_dc = sims.get("model") == "dc"
    if es_dc:
        pct_xg = (sims.get("w_xg") or 0) * 100
        ajuste_txt = (
            "por máxima verosimilitud sobre los resultados de las dos zonas, "
            "corrigiendo cada partido por la calidad del rival y midiendo el "
            f"rendimiento sobre todo por xG ({pct_xg:.0f}\\%) más que por el "
            "gol convertido, que es lo que mejor predice fuera de muestra")
    else:
        ajuste_txt = (
            f"pesando los últimos partidos más que los de principios de "
            f"temporada (recencia con vida media de {half_life} partidos, para "
            f"que una racha reciente mueva la proyección)"
            if half_life else
            "con el promedio plano de resultados y xG de toda la temporada")
    out.append(f"\\section*{{{section_num}. Proyección de la Tabla - Zona A}}\n")
    out.append(
        f"Simulación Monte Carlo ({n_sims_es} temporadas simuladas, "
        f"{n_remaining} partidos restantes de Zona A) sobre "
        + ("un modelo Dixon-Coles de ataque/defensa ajustado "
           if es_dc else "un modelo de ataque/defensa tipo Poisson ajustado ")
        + f"{ajuste_txt}. "
        f"\\textbf{{Alcance:}} esto cubre solo la Zona A "
        f"({n_teams} equipos) - no incluye el ascenso directo (final vs. "
        f"Zona B) ni el ganador del Torneo Reducido, que dependen de datos "
        f"de la Zona B que hoy no están cargados (ver "
        f"\\texttt{{PLAN\\_montecarlo\\_tabla.md}}, Fase 2).\n\n")
    # OJO: ° en modo texto se rompe con este preámbulo (babel es-tabla + T1 +
    # lmodern renderiza "3°" como "3ř" — bug preexistente del repo, confirmado
    # también en informes ya compilados como Informe_pre_partido_colon.pdf).
    # Se usa el símbolo de grado en modo matemático ($^\circ$), que no depende
    # de esa fuente y renderiza bien.
    deg = r"$^\circ$"
    out.append(
        r"\databox{Proyección de " + _tex_escape(team_name) + "}{"
        + actual_txt +
        f"Posición final esperada: \\textbf{{{pos_media:.1f}{deg}}} (mediana {pos_mediana}{deg}). "
        f"Probabilidad de descenso (17{deg}-18{deg}): {desc_txt}. "
        f"Probabilidad de entrar al Reducido por posición (2{deg}-8{deg}): {p_red:.0f}\\%. "
        f"Probabilidad de terminar 1{deg} de zona (llegar a la final): {p_1ro:.0f}\\%."
        + "}\n\n")

    def _proj_fig(fname, caption, width):
        if fname not in graphics:
            return ""
        return _fig({graphics_prefix + fname}, graphics_prefix + fname, caption, width)

    out.append(_proj_fig("posicion_probabilidad.png",
                         "Probabilidad de cada posición final de Zona A, por equipo.", 0.98))
    out.append(_proj_fig("distribucion_puntos.png",
                         f"Distribución de puntos finales simulados para {_tex_escape(team_name)}.", 0.85))
    out.append(_proj_fig("proyeccion_zona.png",
                         "Probabilidad de terminar en cada zona de la tabla (Reducido / mitad de tabla / descenso), por equipo.", 0.98))

    if es_dc:
        recencia_nota = (
            " Los hiperparámetros se eligieron por backtesting (cortar el "
            "campeonato en una fecha pasada, proyectar desde ahí y medir "
            "contra lo que después pasó), no a criterio. El modelo pesa igual "
            "todos los partidos de la temporada: en esa validación, castigar "
            "los partidos viejos para seguir las rachas no mejoró el "
            "pronóstico. Por eso la proyección puede diferir de la impresión "
            "que deja el último mes.")
    else:
        recencia_nota = (
            " Al pesar los últimos partidos, un equipo que viene de una racha "
            "puede proyectar bastante mejor (o peor) que su posición de hoy - "
            "eso es lo esperado del método, no un error, pero conviene mirarlo "
            "junto al promedio plano de toda la temporada para no sobreactuar "
            "una racha corta."
            if half_life else "")
    out.append(
        "\\textit{\\small Nota metodológica: modelo ajustado sobre "
        f"{sims['strengths']['pj'].min():.0f}-{sims['strengths']['pj'].max():.0f} "
        "partidos por equipo - confianza media/alta en la posición relativa, "
        "baja en el resultado exacto de un partido individual." + recencia_nota + "}\n\n")
    out.append(r"\slot{lectura de la proyección: qué significa para el objetivo de la temporada}" + "\n\n")
    return "".join(out)
