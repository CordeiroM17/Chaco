# -*- coding: utf-8 -*-
"""
Carrusel PERMANENCIA — post de festejo y agradecimiento, armado por adelantado
para publicarlo el día que Chaco For Ever quede matemáticamente salvado.

Estética `estilo_fiesta.py` (la de diario del carrusel de Cravero + bastones,
papel picado y tapa con fotos). Los números de la campaña se calculan EN EL
MOMENTO desde los CSV de partidos, así que alcanza con re-scrapear el partido
que da la permanencia (y refrescar standings/fixture) y volver a correr:

    python ig.py editable permanencia_2026

Lo único que se edita a mano es el dict DATOS de abajo (en qué fecha y contra
quién se confirmó). El script avisa si según standings.csv + fixture.csv la
permanencia todavía NO es matemática.

------------------------------------------------------------------------------
NÚMEROS FIJOS (historia, no cambian):
- Tabla reconstruida jornada a jornada (tabla_historica_grupo_a.py): 19
  jornadas seguidas en zona de descenso (28/02 al 26/07), 15 jornadas último
  en toda la temporada. Último después de la fecha 18 con 12 puntos.
- Cravero dirige desde la fecha 23 (2/8 vs Deportivo Morón, confirmado por el
  usuario). Quién dirigió las fechas 19-21 NO está confirmado: el texto no
  habla de ese tramo.
NÚMEROS QUE SE RECALCULAN: puntos, récord, goles, vallas invictas, ciclo
Cravero (desde 2026-08-02), minutos y goles por jugador, posición actual.
------------------------------------------------------------------------------
"""
import os

from plantillas.base import PROYECTO, ASSETS

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
import estilo_fiesta as F          # lo usan también las funciones auxiliares de abajo
import tabla_historica_grupo_a as TH

ESTILO = "fiesta"                       # diario + bastones y papel picado
CARPETA = "permanencia_2026"            # sale en placas/permanencia_2026/

# ---------------------------------------------------------------- EDITAR ACÁ
DATOS = {
    "fecha_confirmacion": None,     # ej. 33  (None = todavía no confirmada)
    "rival_confirmacion": None,     # ej. "Deportivo Madryn"
}
# ----------------------------------------------------------------------------

SEASON = "2026"
CHACO_ID = 252726
DEBUT_CRAVERO = "2026-08-02"
PARTIDOS = PROYECTO / "data" / "temporadas" / SEASON / "partidos"
GRAF = ASSETS / "permanencia_posiciones.png"


def nf(x, dec=2):
    return f"{x:.{dec}f}".replace(".", ",")


# ---------------------------------------------------------------- datos
def campania():
    rows, jug = [], []
    for d in sorted(os.listdir(PARTIDOS)):
        carp = PARTIDOS / d
        if not (carp / "lineups_clean.csv").exists():
            continue
        lu = pd.read_csv(carp / "lineups_clean.csv", encoding="utf-8")
        ch = lu[lu.team_name == "Chaco For Ever"]
        side = ch.team_side.iloc[0]
        inc = pd.read_csv(carp / "incidents_clean.csv", encoding="utf-8")
        ft = inc[inc.type == "period"].iloc[0]
        gf, ga = (ft.home_score, ft.away_score) if side == "home" else (ft.away_score, ft.home_score)
        rows.append(dict(fecha=d[:10], gf=int(gf), ga=int(ga)))
        for _, r in ch.iterrows():
            jug.append(dict(n=r.player_name, min=r.minutes_played or 0,
                            tit=bool(r.is_starter), g=r.goals or 0))
    df = pd.DataFrame(rows)
    df["pts"] = (df.gf > df.ga) * 3 + (df.gf == df.ga) * 1
    p = pd.DataFrame(jug).fillna(0)
    p = p.groupby("n").agg(pj=("min", lambda x: (x > 0).sum()), min=("min", "sum"),
                           tit=("tit", "sum"), g=("g", "sum")).reset_index()
    return df, p[p.pj > 0]


def resumen(df):
    return dict(pj=len(df), v=int((df.gf > df.ga).sum()), e=int((df.gf == df.ga).sum()),
                d=int((df.gf < df.ga).sum()), pts=int(df.pts.sum()),
                gf=int(df.gf.sum()), ga=int(df.ga.sum()), vi=int((df.ga == 0).sum()),
                ppg=df.pts.mean(), gapg=df.ga.mean())


def chequear_permanencia():
    """Salvado matemáticamente si el 17° no nos alcanza ni ganando todo lo que
    le queda (desempate ignorado: pedimos ventaja estricta)."""
    st = pd.read_csv(PROYECTO / "data/temporadas" / SEASON / "standings.csv")
    fx = pd.read_csv(PROYECTO / "data/temporadas" / SEASON / "fixture.csv")
    pend = fx[fx.status_type == "notstarted"]
    ch = st[st.team_id == CHACO_ID].iloc[0]
    techo = []
    for _, r in st.iterrows():
        if r.team_id == CHACO_ID:
            continue
        q = ((pend.home_team_id == r.team_id) | (pend.away_team_id == r.team_id)).sum()
        techo.append(r.points + 3 * q)
    techo.sort(reverse=True)
    # para bajar hay que quedar 17° o peor: tienen que pasarnos 16 equipos
    salvado = techo[15] < ch.points
    return salvado, int(ch.position), int(ch.points), techo[15]


def historia_posiciones():
    ev = TH.cargar_partidos()
    fechas = sorted(ev[(ev.home_team_id == CHACO_ID) | (ev.away_team_id == CHACO_ID)].date.unique())
    return [(f, int(TH.tabla_hasta(ev, f).query("team_id == @CHACO_ID").iloc[0].pos))
            for f in fechas]


MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def grafico_posiciones(hist, pts_hoy=None):
    """La línea que sale del pozo: posición partido a partido en tema papel.
    La línea es ROJA mientras Chaco está en zona de descenso (17° o 18°) y de tinta cuando
    sale; tres cartelitos cuentan la historia (cuántos partidos último, cuándo llega
    Cravero, cuándo salimos de la zona roja) y el eje de abajo marca los meses."""
    import datetime as dt
    from matplotlib.collections import LineCollection

    pap = tuple(c / 255 for c in F.PAPEL)
    tin = tuple(c / 255 for c in F.TINTA)
    roj = tuple(c / 255 for c in F.ACENTO)
    dor = tuple(c / 255 for c in F.DORADO)
    mut = tuple(c / 255 for c in F.MUTED)
    plt.rcParams["font.family"] = "Georgia"
    fig, ax = plt.subplots(figsize=(8, 6.9), dpi=150)
    fig.patch.set_facecolor(pap)
    ax.set_facecolor(pap)
    xs = list(range(1, len(hist) + 1))
    ys = [p for _, p in hist]
    n = len(xs)
    peor, techo = 18.7, 0.4

    # zona de descenso + equipos que quedaron atrás (relleno suave bajo la línea)
    ax.axhspan(16.5, peor, color=roj, alpha=0.12, lw=0, zorder=0)
    ax.fill_between(xs, ys, peor, color=tin, alpha=0.05, lw=0, zorder=1)
    ax.text(n + 0.4, 17.6, "zona de descenso", color=roj, fontsize=17, ha="right",
            va="center", style="italic", zorder=6)

    # línea por tramos: roja en descenso, tinta fuera
    pts = list(zip(xs, ys))
    segs = [[pts[i], pts[i + 1]] for i in range(n - 1)]
    cols = [roj if min(ys[i], ys[i + 1]) >= 17 and max(ys[i], ys[i + 1]) >= 17 and
            (ys[i] >= 17 and ys[i + 1] >= 17) else tin for i in range(n - 1)]
    ax.add_collection(LineCollection(segs, colors=cols, linewidths=4.2, capstyle="round",
                                     zorder=3))
    ax.scatter(xs[:-1], ys[:-1], s=34, c=[roj if y >= 17 else tin for y in ys[:-1]], zorder=4)

    # 1) cuántos partidos último
    n_ult = sum(1 for y in ys if y == 18)
    ix_ult = [i + 1 for i, y in enumerate(ys) if y == 18]
    ax.text((ix_ult[1] + ix_ult[-1]) / 2, 14.9, f"último en\n{n_ult} partidos", color=roj,
            fontsize=19, ha="center", va="center", style="italic", linespacing=1.15,
            zorder=6)

    # 2) llega Cravero
    i_crav = next(i for i, (f, _) in enumerate(hist) if str(f) >= DEBUT_CRAVERO) + 1
    ax.axvline(i_crav, color=mut, lw=1.3, ls=(0, (3, 3)), zorder=2)
    ax.text(i_crav - 0.5, 2.3, "llega\nCravero", color=tin, fontsize=19, style="italic",
            ha="right", va="center", linespacing=1.15, zorder=6)

    # 3) salimos de la zona roja para siempre
    ult_rojo = max(i for i, y in enumerate(ys) if y >= 17)
    if ult_rojo + 1 < n:
        xo, yo = xs[ult_rojo + 1], ys[ult_rojo + 1]
        ax.annotate("salimos de\nla zona roja", (xo, yo), xytext=(xo + 4.6, yo + 1.1),
                    fontsize=18, color=tin, ha="center", va="center", style="italic",
                    linespacing=1.15, zorder=6,
                    arrowprops=dict(arrowstyle="-|>", color=tin, lw=1.6,
                                    shrinkA=4, shrinkB=6, connectionstyle="arc3,rad=-0.25"))

    # hoy
    ax.scatter([xs[-1]], [ys[-1]], s=1000, marker="*", color=dor, edgecolor=tin,
               linewidth=1.2, zorder=7)
    et = f"{ys[-1]}°" + (f"  ·  {pts_hoy} pts" if pts_hoy else "")
    ax.annotate(et, (xs[-1], ys[-1]), xytext=(8, 34), textcoords="offset points",
                ha="right", fontsize=24, fontweight="bold", color=tin, zorder=7)

    ax.set_ylim(peor, techo)
    ax.set_yticks([1, 6, 12, 18])
    ax.set_yticklabels(["1°", "6°", "12°", "18°"])
    ax.set_xlim(0.3, n + 0.8)
    # eje de abajo: meses (marca el primer partido de cada mes)
    marcas, ult = [], None
    for i, (f, _) in enumerate(hist):
        d = f if isinstance(f, dt.date) else dt.date.fromisoformat(str(f)[:10])
        if d.month != ult:
            marcas.append((i + 1, MESES[d.month - 1]))
            ult = d.month
    marcas = [m for k, m in enumerate(marcas) if k == 0 or m[0] - marcas[k - 1][0] >= 3]
    ax.set_xticks([m[0] for m in marcas])
    ax.set_xticklabels([m[1] for m in marcas])
    ax.set_ylabel("Puesto en la Zona A", color=mut, fontsize=19)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(mut)
    ax.tick_params(colors=mut, labelsize=18, length=0)
    ax.tick_params(axis="x", length=5)
    ax.grid(axis="y", color=mut, alpha=0.2, lw=0.8)
    fig.tight_layout()
    fig.savefig(GRAF, facecolor=pap)
    plt.close(fig)


# ---------------------------------------------------------------- placas
def construir(F):
    # F = estilo_fiesta (las placas: F.portada_foto, F.dato, F.tabla, F.nombres, F.foto_texto...)
    df, pl = campania()
    tot = resumen(df)
    pre = resumen(df[df.fecha < DEBUT_CRAVERO])
    crv = resumen(df[df.fecha >= DEBUT_CRAVERO])
    hist = historia_posiciones()
    pos_hoy = hist[-1][1]
    grafico_posiciones(hist, pts_hoy=tot["pts"])

    fuera = config.jugadores_fuera_set() if hasattr(config, "jugadores_fuera_set") else \
        {n.strip().lower() for n in config.JUGADORES_FUERA}
    pl = pl[~pl.n.str.lower().isin(fuera)]
    goleador = pl.sort_values(["g", "min"], ascending=False).iloc[0]
    fijos = pl.sort_values("min", ascending=False).head(3)

    fc, rc = DATOS["fecha_confirmacion"], DATOS["rival_confirmacion"]
    nota = f"Primera Nacional 2026 · Zona A · fecha {fc}" if fc else \
        "Primera Nacional 2026 · Zona A"
    cuando = f" La permanencia llegó en la fecha {fc} ante {rc}." if fc and rc else ""

    s = []

    # 01 — Tapa con fotos
    s.append(F.portada_foto(
        [(ASSETS / "Nievas2.jpg", 0.5, 0.25, 1.2),
         (ASSETS / "Leandro_Fernandez.jpg", 0.55, 0.35, 1.25),
         (ASSETS / "Agustin_Ojeda.jpg", 0.2, 0.05, 1.5),
         (ASSETS / "Mathias_Silvera.jpg", 0.5, 0.3, 1.0)],
        "Permanencia confirmada"))

    # 02 — La frase, de entrada (antes era el cierre)
    s.append(F.remate(
        "Fuimos últimos, nos dieron por muertos y nos levantamos. "
        "El año que viene, el Negro sigue jugando la Primera Nacional.",
        firma="Gracias, hinchada, cuerpo técnico y jugadores", nota=nota))

    # 03 — De dónde venimos
    s.append(F.dato(
        "19",
        "Jornadas seguidas en zona de descenso",
        "Del 28 de febrero al 26 de julio, el Negro no salió nunca de la zona "
        "roja. *Quince fechas fue último*, y después de la fecha 18 tenía "
        "**12 puntos**. Nadie se bajó del barco.",
        kicker="De dónde venimos", nota=nota, centrado=True))

    # 04 — El gráfico
    s.append(F.grafico(
        str(GRAF),
        titulo="Del fondo a la mitad de la tabla",
        subtitulo=f"Puesto de Chaco partido a partido · hoy **{pos_hoy}°** con **{tot['pts']} puntos**",
        kicker="La remontada", nota=nota))

    # 05 — El cambio con Cravero
    s.append(F.tabla(
        "Antes y con Cravero",
        f"Sus {crv['pj']} partidos contra los {pre['pj']} anteriores",
        [("Puntos por partido", f"de {nf(pre['ppg'])} a {nf(crv['ppg'])}"),
         ("Goles en contra por partido", f"de {nf(pre['gapg'])} a {nf(crv['gapg'])}"),
         ("Vallas invictas", f"de {pre['vi']} en {pre['pj']} a {crv['vi']} en {crv['pj']}"),
         ("Partidos ganados", f"de {pre['v']} en {pre['pj']} a {crv['v']} en {crv['pj']}")],
        kicker="El cambio", nota=nota, destacar="Puntos por partido", centrado=True))

    # 06 — Gracias al cuerpo técnico
    s.append(F.foto_texto(
        ASSETS / "Cravero_Macius.png",
        "Gracias, Chango y cuerpo técnico",
        "Volvió a la casa donde se crió y donde ya había hecho historia en "
        "2021. Ordenó al equipo desde atrás: **"
        f"{crv['vi']} vallas invictas en {crv['pj']} partidos**. A él y a todo "
        "su cuerpo técnico, que laburó en silencio: *gracias*.",
        kicker="Gracias", nota=nota, fx=0.5, fy=0.3, zoom=1.15, alto_foto=440))

    # 07 — Gracias al plantel
    orden = pl.sort_values("min", ascending=False).n.tolist()
    s.append(F.nombres(
        "Gracias, muchachos",
        f"Los {len(orden)} que se pusieron la camiseta este año",
        orden, destacados=set(fijos.n), kicker="El plantel", nota=nota))

    # 08 — Los que sostuvieron
    filas = [(f"{r.n}", f"{int(r.pj)} partidos · {int(r.min)} min") for r in fijos.itertuples()]
    filas.append((f"{goleador.n}, goleador", f"{int(goleador.g)} goles"))
    s.append(F.tabla(
        "Los que estuvieron siempre",
        "Los que más jugaron y el que más la metió",
        filas, kicker="Los de siempre", nota=nota,
        destacar=f"{goleador.n}, goleador", centrado=True))

    # 09 — La campaña en un número
    s.append(F.dato(
        str(tot["pts"]),
        "Puntos en la temporada",
        f"*{tot['v']} triunfos, {tot['e']} empates y {tot['d']} derrotas.* "
        f"Con Cravero sumó **{crv['pts']} de {crv['pj'] * 3}**."
        + cuando,
        kicker="La campaña", nota=nota, centrado=True))

    # orden final: la 06 pasa a 03 y la 07 a 04 (índices 0-based: 5 y 6 al lugar 2)
    s = s[:2] + [s[5], s[6]] + s[2:5] + s[7:]
    return s



TITULO = "Permanencia 2026"
AVISO = ("BORRADOR armado por adelantado. Publicar recién cuando la permanencia sea matemática: "
         "refrescar standings.csv y fixture.csv, completar DATOS (fecha y rival) y correr de nuevo; "
         "ya no tiene que avisar 'todavía NO es matemático'.")
NOTAS = """- 9 placas en `placas/permanencia_2026/`. Estilo fiesta (diario + bastones). Los números del caption y de
  las placas se recalculan solos desde los CSV de partidos. Fijos: 19 jornadas en descenso y 15 como último.
- El ciclo Cravero se cuenta desde el 2/8 (fecha 23). No se habla de quién dirigió las fechas 19-21.
- Las placas nombran a todos los que jugaron, menos `config.JUGADORES_FUERA`. Sin amarillas (convención)."""


def texto():
    """Caption: sin asteriscos (Instagram no los interpreta), énfasis en MAYÚSCULAS. Usa los
    mismos números que las placas; si DATOS tiene fecha y rival de la confirmación, los nombra."""
    from plantillas.base import apellido
    df, pl = campania()
    tot, pre = resumen(df), resumen(df[df.fecha < DEBUT_CRAVERO])
    crv = resumen(df[df.fecha >= DEBUT_CRAVERO])
    pos = historia_posiciones()[-1][1]
    fuera = {n.strip().lower() for n in config.JUGADORES_FUERA}
    pl = pl[~pl.n.str.lower().isin(fuera)]
    gol = pl.sort_values(["g", "min"], ascending=False).iloc[0]
    fijos = pl.sort_values("min", ascending=False).head(3)
    fn = fijos.n.tolist()
    nombres = ", ".join(apellido(n) for n in fn[:-1]) + " y " + apellido(fn[-1])
    pjs = set(int(x) for x in fijos.pj)
    jugaron = (f"que jugaron {pjs.pop()} partidos cada uno" if len(pjs) == 1
               else "que fueron los que más jugaron")
    fc, rc = DATOS["fecha_confirmacion"], DATOS["rival_confirmacion"]
    cuando = (f"Con el resultado ante {rc} en la fecha {fc}, Chaco For Ever se aseguró la permanencia."
              if fc and rc else "Chaco For Ever se aseguró la permanencia en la Primera Nacional.")
    return f"""🖤🤍 ¡EL NEGRO SIGUE EN LA PRIMERA NACIONAL!

{cuando}

Hay que acordarse de dónde veníamos. Estuvimos 19 jornadas seguidas en zona de descenso, del 28 de febrero al 26 de julio, y quince fechas últimos. Después de la fecha 18 teníamos 12 puntos.

Hoy estamos {pos}° con {tot['pts']} puntos.

GRACIAS, CHANGO. Volvió a la casa donde se crió y donde ya había hecho historia en 2021. Con él el equipo pasó de {nf(pre['ppg'])} a {nf(crv['ppg'])} puntos por partido y de {nf(pre['gapg'])} a {nf(crv['gapg'])} goles en contra por partido, con {crv['vi']} vallas invictas en {crv['pj']} partidos. Gracias también a todo su cuerpo técnico.

GRACIAS, MUCHACHOS. A los {len(pl)} que se pusieron la camiseta este año. A {nombres}, {jugaron}. A {apellido(gol.n)} y sus {int(gol.g)} goles. Y a los que entraron cinco minutos y también dejaron todo.

Fuimos últimos, nos dieron por muertos y nos levantamos. El año que viene seguimos acá."""


def previo():
    """Se corre antes de armar las placas: avisa, no frena."""
    salvado, pos, pts, techo17 = chequear_permanencia()
    if not salvado:
        print(f"!! OJO: todavía NO es matemático. Chaco {pos}° con {pts} pts; "
              f"el 17° puede llegar a {techo17}. Esto es un borrador.")
    if DATOS["fecha_confirmacion"] is None:
        print("!! Falta completar DATOS (fecha y rival de la confirmación).")
