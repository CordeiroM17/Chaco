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
