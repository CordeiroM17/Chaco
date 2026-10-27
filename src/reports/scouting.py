"""Informe de scouting en LaTeX: auditoría del plantel y candidatos por puesto.

Sigue la convención del resto de los informes del proyecto: datos objetivos
primero, interpretación al final en "Nuestra lectura".

Todas las cadenas con LaTeX van como raw strings (r"..."). En una cadena normal
Python interpreta \t y \b, así que `\textbf` se convierte en tabulador y
`\begin` en backspace, y el .tex sale roto sin que nada avise.

Uso:
    from src.reports.scouting import build_scouting_tex, compilar
    tex = build_scouting_tex(pool, sem, titulares, espacios)
    pdf = compilar(tex, out_dir, 'Informe_scouting_chaco')
"""
import os
import subprocess

import pandas as pd

from src.analysis import scouting as SC
from src.analysis import similitud as SIM

LUALATEX = r"C:/Users/luart/AppData/Local/Programs/MiKTeX/miktex/bin/x64/lualatex.exe"

_PREAMBLE = r"""\documentclass[11pt, a4paper]{article}
\usepackage[a4paper, top=2.3cm, bottom=2.3cm, left=1.8cm, right=1.8cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{array}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{lastpage}
\usepackage[hidelinks]{hyperref}
\usepackage[spanish, es-tabla]{babel}
\usepackage{enumitem}
\setlist[itemize]{label=-, leftmargin=*, topsep=2pt, itemsep=1pt}

\definecolor{primary}{HTML}{0F172A}
\definecolor{alertred}{HTML}{DC2626}
\definecolor{accentgreen}{HTML}{0F766E}
\definecolor{warnamber}{HTML}{D97706}
\definecolor{lightgray}{HTML}{F8FAFC}
\definecolor{darkgray}{HTML}{475569}

% Resaltados como TEXTO en color, no colorbox: dentro de una tabla un colorbox
% no corta línea y desborda la columna.
\newcommand{\mR}[1]{\textbf{\color{alertred}#1}}
\newcommand{\mG}[1]{\textbf{\color{accentgreen}#1}}
\newcommand{\mA}[1]{\textbf{\color{warnamber}#1}}

\newcommand{\databox}[2]{%
  \noindent\colorbox{lightgray}{%
    \parbox{\dimexpr\textwidth-2\fboxsep\relax}{%
      \raggedright\smallskip
      \textbf{\color{primary}{#1}}\par\smallskip
      \small #2\par\smallskip}}%
  \par\vspace{3mm}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\renewcommand{\arraystretch}{1.15}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}
\fancyhead[L]{\small\color{darkgray}\textsc{__NAME__} $\bullet$ Scouting de refuerzos}
\fancyhead[R]{\small\color{darkgray}Temporada __SEASON__}
\fancyfoot[L]{\footnotesize\color{darkgray}Preparado por Cordeiro \& Casco $\bullet$ Análisis de datos deportivos}
\fancyfoot[R]{\footnotesize\color{darkgray}Página \thepage\ de \pageref{LastPage}}

\titleformat{\section}{\normalfont\Large\bfseries\color{primary}}{\thesection}{0.6em}{}[\vspace{-2mm}\noindent{\color{accentgreen}\rule{\textwidth}{1.2pt}}]
\titlespacing*{\section}{0pt}{5mm}{3mm}
\titleformat{\subsection}{\normalfont\large\bfseries\color{darkgray}}{\thesubsection}{0.6em}{}
\titlespacing*{\subsection}{0pt}{4mm}{2mm}
"""

_HEADER = r"""\begin{document}
\begin{center}
  \colorbox{primary}{%
    \parbox{\dimexpr\textwidth-2\fboxsep\relax}{%
      \vspace{4mm}\centering\color{white}
      \textsc{\large Análisis de Datos Deportivos} \\ \vspace{1mm}
      \textbf{\Large AUDITORÍA DE PLANTEL Y SCOUTING DE REFUERZOS} \\ \vspace{1mm}
      \textbf{\Large __NAME__} \\ \vspace{1mm}
      \small Temporada __SEASON__ (Primera Nacional) $\bullet$ __NJUG__ jugadores analizados en __NEQ__ equipos
      \vspace{4mm}}}
\end{center}
\vspace{3mm}
\begin{tabular}{ll}
  \textbf{Destinatario:} & __DEST__ \\
  \textbf{Preparado por:} & Cordeiro Mariano Ángel y Casco Tobías Andrés \\
  \textbf{Contacto:} & cordeiromariano17@gmail.com $\bullet$ +54 3644 645142 \\
  \textbf{Universo:} & Primera Nacional __SEASON__, Zona A y Zona B (__NPART__ partidos) \\
\end{tabular}

\vspace{3mm}

\noindent\colorbox{lightgray}{%
  \parbox{\dimexpr\textwidth-2\fboxsep\relax}{%
    \smallskip
    \small Este informe ordena qué puestos conviene reforzar y qué jugadores de la categoría los
    cubren. Presenta primero los \textbf{datos objetivos} (rendimiento del plantel, diagnóstico por
    puesto, candidatos) y reserva la \textbf{interpretación} para el cierre. La lista final es una
    preselección para validar por video, no una recomendación de fichaje cerrada.\smallskip}}
\vspace{2mm}
\hrule
"""

_FIN_FILA = r" \\"


def _esc(s):
    """Escapa lo que LaTeX interpreta. Los acentos van directos (utf8+lualatex)."""
    return (str(s).replace("\\", "")
            .replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
            .replace("#", r"\#").replace("$", r"\$"))


def _valor(v):
    return "s/d" if pd.isna(v) else f"{v / 1000:.0f}k"


def _pctil(p):
    """Percentil coloreado según la franja en la que cae."""
    if pd.isna(p):
        return "s/d"
    t = f"{p:.0f}"
    if p < 35:
        return r"\mR{" + t + "}"
    if p >= 70:
        return r"\mG{" + t + "}"
    return r"\mA{" + t + "}"


def _tabla(cabecera, columnas, filas):
    return ("\n".join([r"\begin{center}\small",
                       r"\begin{tabular}{" + columnas + "}",
                       r"\toprule", cabecera + _FIN_FILA, r"\midrule"]
                      + filas
                      + [r"\bottomrule", r"\end{tabular}", r"\end{center}", ""]))


# ─────────────────────────── secciones objetivas ─────────────────────────────
_COLOR_ESTADO = {
    "PRIORIDAD_RENOVACION": r"\mG",
    "ROTACION_VALIOSA":     r"\mG",
    "PRESCINDIBLE":         r"\mA",
    "BAJA_PRIORITARIA":     r"\mR",
    "SIN_EVALUAR":          "",
}

# Los nombres internos van sin acentos (son claves de dicts); acá se les pone la
# ortografía que corresponde para mostrarlos.
_ESTADO_TEXTO = {
    "PRIORIDAD_RENOVACION": "Renovación",
    "ROTACION_VALIOSA":     "Rotación valiosa",
    "PRESCINDIBLE":         "Prescindible",
    "BAJA_PRIORITARIA":     "Baja prioritaria",
    "SIN_EVALUAR":          "Sin evaluar",
}

_COMPONENTE_TEXTO = {
    "duelo_aereo": "Duelo aéreo", "duelo_suelo": "Duelo terrestre",
    "volumen_def": "Volumen defensivo", "salida": "Salida",
    "duelo_def": "Duelo defensivo", "centro": "Centros",
    "creacion": "Creación", "recuperacion": "Recuperación",
    "pase": "Pase", "bajo_presion": "Pase bajo presión",
    "progresion": "Progresión", "presencia_def": "Presencia defensiva",
    "llegada": "Llegada", "generacion": "Generación",
    "desequilibrio": "Desequilibrio", "amenaza": "Amenaza de gol",
    "duelo": "Duelos", "eficacia": "Eficacia de remate",
    "presencia_area": "Presencia en el área", "juego_aereo": "Juego aéreo",
    "asociacion": "Asociación", "rating": "Rating",
}


def _tabla_plantel(sem):
    filas = []
    for _, r in sem.iterrows():
        texto = _ESTADO_TEXTO.get(r["estado"], r["estado"])
        macro = _COLOR_ESTADO.get(r["estado"], "")
        estado = (macro + "{" + texto + "}") if macro else texto
        rating = "s/d" if pd.isna(r["rating"]) else f"{r['rating']:.2f}"
        filas.append(
            f"{_esc(r['nombre'])} & {_esc(r['rol'])} & {r['edad']:.0f} & "
            f"{r['minutos']:.0f} & {r['pct_minutos_equipo']:.0f}" + r"\%"
            + f" & {rating} & {_pctil(r['score_pct'])} & {estado}" + _FIN_FILA)
    cab = (r"\textbf{Jugador} & \textbf{Puesto} & \textbf{Edad} & \textbf{Min} & "
           r"\textbf{\% min} & \textbf{Rating} & \textbf{Pctil} & \textbf{Clasificación}")
    return _tabla(cab, "lccrrccl", filas)


def _tabla_prioridad(titulares):
    filas = []
    for _, r in titulares.iterrows():
        banda = r["banda"] if pd.notna(r.get("banda")) else "--"
        u = f"{r['urgencia']:.0f}"
        if r["urgencia"] >= 50:
            u = r"\mR{" + u + "}"
        elif r["urgencia"] >= 25:
            u = r"\mA{" + u + "}"
        filas.append(
            f"{_esc(r['nombre'])} & {_esc(r['rol'])} & {banda} & {r['edad']:.0f} & "
            f"{r['pct_minutos_equipo']:.0f}" + r"\%"
            + f" & {_pctil(r['score_pct'])} & {_valor(r['valor_mercado_eur'])} & {u}"
            + _FIN_FILA)
    cab = (r"\textbf{Jugador} & \textbf{Puesto} & \textbf{Banda} & \textbf{Edad} & "
           r"\textbf{\% min} & \textbf{Pctil} & \textbf{Valor} & \textbf{Urgencia}")
    return _tabla(cab, "lcccrccr", filas)


def _tabla_candidatos(m):
    filas = []
    for _, c in m.iterrows():
        banda = c["banda"] if pd.notna(c.get("banda")) else "--"
        tabla = "s/d" if pd.isna(c["pos_tabla"]) else f"{c['pos_tabla']:.0f}"
        filas.append(
            f"{_esc(c['nombre'])} & {_esc(str(c['equipo'])[:24])} & {banda} & "
            f"{c['edad']:.0f} & {c['minutos']:.0f} & {_pctil(c['score_pct'])} & "
            f"{_valor(c['valor_mercado_eur'])} & {tabla} & {c['similitud']:.0f}"
            + _FIN_FILA)
    cab = (r"\textbf{Jugador} & \textbf{Equipo} & \textbf{Bda} & \textbf{Ed} & "
           r"\textbf{Min} & \textbf{Pctil} & \textbf{Valor} & \textbf{Tab} & \textbf{Sim}")
    return _tabla(cab, "llccrccrc", filas)


def _bloque_puesto(pool, espacios, jug, k=6, margen=15):
    """Diagnóstico + candidatos de un titular."""
    rol = jug["rol"]
    if rol not in espacios:
        return ""
    banda = f" ({jug['banda']})" if pd.notna(jug.get("banda")) else ""
    titulo = (r"\subsection*{" + _esc(jug["nombre"])
              + r" \textnormal{\small — " + SC.ROL_NOMBRE[rol] + banda
              + rf" $\bullet$ {jug['edad']:.0f} años $\bullet$ {jug['minutos']:.0f} min "
              + f"({jug['pct_minutos_equipo']:.0f}" + r"\%" + r") $\bullet$ percentil "
              + f"{jug['score_pct']:.0f} del puesto" + r"}}")
    out = [titulo, ""]

    dg = SIM.diagnostico(pool, rol, nombre=jug["nombre"])
    if dg is not None and not dg.empty:
        items = []
        for _, c in dg.iterrows():
            hueco = r" \mR{(agujero)}" if c.percentil < 35 and c.peso >= 0.20 else ""
            items.append(
                r"  \item \textbf{"
                + _COMPONENTE_TEXTO.get(c.componente,
                                        c.componente.replace("_", " ")) + "} "
                + f"(peso {c.peso:.0%}): ".replace("%", r"\%")
                + f"percentil {c.percentil:.0f}" + hueco
                + r" \textit{\small [" + _esc(c.metricas) + "]}")
        out += [r"\textbf{Dónde pierde}", r"\begin{itemize}"] + items \
            + [r"\end{itemize}", ""]

    m = SIM.mejoras(espacios[rol], pool, nombre=jug["nombre"], k=k, margen_pct=margen)
    if m.empty:
        out.append(r"\textit{Ningún jugador de la categoría supera el margen exigido.}")
    else:
        out += [r"\textbf{Candidatos que lo superan}", "", _tabla_candidatos(m)]
    return "\n".join(out)


def _bloque_recortes(pool, espacios, titulares, urgencia_min=25):
    recortes = [("Opciones sub-28 (proyección y reventa)",
                 {"edad_max": 27, "minutos_min": 900}),
                ("Opciones de bajo costo (menos de 120.000 euros, 1.200+ minutos)",
                 {"valor_max_eur": 120000, "minutos_min": 1200})]
    out = []
    for titulo, filtros in recortes:
        out.append(r"\subsection*{" + titulo + "}")
        filas = []
        for _, jug in titulares[titulares.urgencia >= urgencia_min].iterrows():
            rol = jug["rol"]
            if rol not in espacios:
                continue
            m = SIM.mejoras(espacios[rol], pool, nombre=jug["nombre"], k=3,
                            filtros=filtros)
            if m.empty:
                filas.append(_esc(jug["nombre"])
                             + r" & \multicolumn{5}{l}{\textit{sin opciones en ese rango}}"
                             + _FIN_FILA)
            else:
                for i, (_, c) in enumerate(m.iterrows()):
                    quien = _esc(jug["nombre"]) if i == 0 else ""
                    filas.append(
                        f"{quien} & {_esc(c['nombre'])} & {_esc(str(c['equipo'])[:22])} & "
                        f"{c['edad']:.0f} & {c['minutos']:.0f} & "
                        f"{_pctil(c['score_pct'])} & {_valor(c['valor_mercado_eur'])}"
                        + _FIN_FILA)
            filas.append(r"\addlinespace")
        cab = (r"\textbf{Reemplaza a} & \textbf{Candidato} & \textbf{Equipo} & "
               r"\textbf{Ed} & \textbf{Min} & \textbf{Pctil} & \textbf{Valor}")
        out.append(_tabla(cab, "llcccrc", filas))
    return "\n".join(out)


_METODOLOGIA = r"""
\textbf{Universo.} Los 482 partidos de la Primera Nacional 2026 (Zona A y Zona B),
36 equipos. Cada partido se cuenta una sola vez: el mismo encuentro está guardado en la
carpeta de los dos equipos, y sin deduplicar los minutos salen al doble.

\textbf{Puestos.} SofaScore solo distingue arquero, defensor, mediocampista y delantero.
Las demarcaciones finas salen de la posición media en cancha de cada jugador, ponderada por
minutos. La banda se validó contra los números de camiseta de los 108 laterales de la
temporada: de los que usan la 4, ninguno aparece del lado izquierdo.

\textbf{Métricas.} Todo se lleva a valores por 90 minutos. Las defensivas se ajustan por la
posesión del equipo, porque un defensor que se pasa el partido replegado acumula despejes
sin ser mejor. A los jugadores con poca muestra se los corrige hacia la media de su puesto,
para que dos goles en 700 minutos no inflen un ranking.

\textbf{Índices.} Cada puesto tiene su propio índice ponderado. Un central se mide por duelo
aéreo, duelo terrestre, volumen defensivo y salida. Un delantero, por eficacia de remate,
presencia en el área y juego aéreo. El percentil siempre compara dentro del puesto.

\textbf{Corte de muestra.} Entran los jugadores con 600 minutos o más.

\vspace{2mm}
\databox{Lo que estos datos no ven}{SofaScore no publica posicionamiento sin balón ni
presión coordinada. Un lateral que se ubica bien hace menos quites porque no le hacen falta,
y el dato lo castiga igual. Tampoco distingue si un jugador toca poco la pelota por decisión
propia o porque su equipo no lo usa como salida. Por eso esta lista es una preselección: el
paso siguiente es el video.}
"""


# ──────────────────────────── informe completo ───────────────────────────────
def build_scouting_tex(pool, sem, titulares, espacios, equipo="Chaco For Ever",
                       season="2026", destinatario=None, n_partidos=482,
                       urgencia_min=25, lectura=None):
    """Devuelve el .tex completo del informe de scouting."""
    urgentes = titulares[titulares.urgencia >= urgencia_min]

    pre = (_PREAMBLE.replace("__NAME__", _esc(equipo))
           .replace("__SEASON__", str(season)))
    head = (_HEADER.replace("__NAME__", _esc(equipo).upper())
            .replace("__SEASON__", str(season))
            .replace("__NJUG__", str(len(pool)))
            .replace("__NEQ__", str(int(pool["team_id"].nunique())))
            .replace("__NPART__", str(n_partidos))
            .replace("__DEST__", _esc(destinatario or equipo)))

    cuenta = sem["estado"].value_counts()
    partes = [pre, head]

    partes.append(r"\section*{1. Situación del plantel}")
    partes.append(
        r"\databox{Resumen}{De los " + str(len(sem))
        + " jugadores con minutos en la temporada: "
        + f"{cuenta.get('PRIORIDAD_RENOVACION', 0)} de prioridad de renovación, "
        + f"{cuenta.get('ROTACION_VALIOSA', 0)} de rotación valiosa, "
        + f"{cuenta.get('PRESCINDIBLE', 0)} prescindibles y "
        + f"{cuenta.get('BAJA_PRIORITARIA', 0)} con baja recomendada. "
        + "Los arqueros quedan sin evaluar porque SofaScore no publica los datos que "
        + "permitirían puntuarlos.}")
    partes.append(
        "El percentil compara a cada jugador contra el resto de la categoría "
        r"\textbf{en su mismo puesto}. Un percentil 20 significa que 8 de cada 10 "
        "jugadores de esa demarcación rinden mejor según el índice de la posición.")
    partes.append(_tabla_plantel(sem))

    partes.append(r"\section*{2. Prioridades de mercado}")
    partes.append(
        "La urgencia cruza cuánto juega cada uno con cuánto le falta para el nivel del "
        r"puesto: \textit{urgencia = \% de minutos $\times$ (100 $-$ percentil)}. "
        "Un suplente flojo no apura. Un titular flojo cuesta puntos todas las fechas.")
    partes.append(_tabla_prioridad(titulares))
    partes.append(f"Los {len(urgentes)} primeros concentran el problema y son los que "
                  "se desarrollan en la sección siguiente.")

    partes.append(r"\section*{3. Puesto por puesto}")
    partes.append(
        "Para cada titular: en qué componentes del índice pierde, y los jugadores de la "
        "categoría que lo superan por al menos 15 percentiles. En los laterales y extremos "
        r"el listado respeta la \textbf{banda}. \textit{Tab} es la posición del equipo del "
        r"candidato en su zona. \textit{Sim} mide cuánto se parece al actual, o sea qué tan "
        "fácil resulta meterlo sin cambiar el funcionamiento del equipo.")
    for _, jug in urgentes.iterrows():
        partes.append(_bloque_puesto(pool, espacios, jug))

    partes.append(r"\section*{4. Alternativas por edad y por presupuesto}")
    partes.append(_bloque_recortes(pool, espacios, titulares, urgencia_min))

    partes.append(r"\section*{5. Nuestra lectura}")
    partes.append(lectura or r"\textit{[Pendiente de completar]}")

    partes.append(r"\section*{6. Cómo se construyó}")
    partes.append(_METODOLOGIA)
    partes.append(r"\end{document}")
    return "\n\n".join(partes)


def compilar(tex, out_dir, nombre="Informe_scouting", pasadas=2):
    """Escribe el .tex y lo compila con lualatex. Devuelve la ruta del PDF."""
    os.makedirs(out_dir, exist_ok=True)
    tex_path = os.path.join(out_dir, f"{nombre}.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex)
    for _ in range(pasadas):     # dos pasadas por \pageref{LastPage}
        subprocess.run([LUALATEX, "-interaction=nonstopmode", "-halt-on-error",
                        os.path.basename(tex_path)], cwd=out_dir,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = tex_path.replace(".tex", ".pdf")
    return pdf if os.path.exists(pdf) else None
