# -*- coding: utf-8 -*-
"""
Carrusel PERMANENCIA — post de festejo y agradecimiento, armado por adelantado
para publicarlo el día que Chaco For Ever quede matemáticamente salvado.

Estética `estilo_fiesta.py` (la de diario del carrusel de Cravero + bastones,
papel picado y tapa con fotos). Los números de la campaña se calculan EN EL
MOMENTO desde los CSV de partidos, así que alcanza con re-scrapear el partido
que da la permanencia (y refrescar standings/fixture) y volver a correr:

    python scripts/carrusel_permanencia.py

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
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PROYECTO = RAIZ.parents[1]
sys.path.insert(0, str(PROYECTO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
import estilo_fiesta as F
import tabla_historica_grupo_a as TH

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
ASSETS = RAIZ / "assets"
SALIDA = RAIZ / "placas" / "permanencia_2026"
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


def grafico_posiciones(hist):
    """La línea que sale del pozo: posición jornada a jornada en tema papel."""
    pap = tuple(c / 255 for c in F.PAPEL)
    tin = tuple(c / 255 for c in F.TINTA)
    roj = tuple(c / 255 for c in F.ACENTO)
    dor = tuple(c / 255 for c in F.DORADO)
    mut = tuple(c / 255 for c in F.MUTED)
    plt.rcParams["font.family"] = "Georgia"
    fig, ax = plt.subplots(figsize=(8, 6.6), dpi=150)
    fig.patch.set_facecolor(pap)
    ax.set_facecolor(pap)
    xs = list(range(1, len(hist) + 1))
    ys = [p for _, p in hist]
    ax.axhspan(16.5, 18.6, color=roj, alpha=0.13, lw=0)
    ax.text(len(xs) + 0.4, 17.55, "zona de descenso", color=roj, fontsize=19,
            ha="right", va="center", style="italic")
    i_crav = next(i for i, (f, _) in enumerate(hist) if str(f) >= DEBUT_CRAVERO)
    ax.axvline(i_crav + 1, color=mut, lw=1, ls=(0, (3, 3)))
    ax.text(i_crav + 0.6, 2.2, "llega Cravero", color=mut, fontsize=19,
            style="italic", va="center", ha="right")
    ax.plot(xs, ys, color=tin, lw=4, solid_capstyle="round", zorder=3)
    ax.scatter(xs[:-1], ys[:-1], s=40, color=tin, zorder=4)
    ax.scatter([xs[-1]], [ys[-1]], s=900, marker="*", color=dor,
               edgecolor=tin, linewidth=1.2, zorder=5)
    ax.annotate(f"{ys[-1]}°", (xs[-1], ys[-1]), xytext=(0, 18),
                textcoords="offset points", ha="center", fontsize=24,
                fontweight="bold", color=tin)
    ax.set_ylim(18.6, 0.6)
    ax.set_yticks([1, 6, 12, 18])
    ax.set_xlim(0.3, len(xs) + 0.7)
    ax.set_xticks([1, 10, 20, 30] + ([len(xs)] if len(xs) % 10 > 2 else []))
    ax.set_xlabel("Partidos jugados", color=mut, fontsize=19)
    ax.set_ylabel("Posición en la Zona A", color=mut, fontsize=19)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(mut)
    ax.tick_params(colors=mut, labelsize=17)
    ax.grid(axis="y", color=mut, alpha=0.18, lw=0.8)
    fig.tight_layout()
    fig.savefig(GRAF, facecolor=pap)
    plt.close(fig)


# ---------------------------------------------------------------- placas
def construir():
    df, pl = campania()
    tot = resumen(df)
    pre = resumen(df[df.fecha < DEBUT_CRAVERO])
    crv = resumen(df[df.fecha >= DEBUT_CRAVERO])
    hist = historia_posiciones()
    pos_hoy = hist[-1][1]
    grafico_posiciones(hist)

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
        subtitulo=f"Posición de Chaco jornada a jornada · hoy **{pos_hoy}°**",
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


def main():
    salvado, pos, pts, techo17 = chequear_permanencia()
    if not salvado:
        print(f"!! OJO: todavía NO es matemático. Chaco {pos}° con {pts} pts; "
              f"el 17° puede llegar a {techo17}. Esto es un borrador.")
    if DATOS["fecha_confirmacion"] is None:
        print("!! Falta completar DATOS (fecha y rival de la confirmación).")
    SALIDA.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(construir(), 1):
        F.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    print("OK _preview.png ->", F.contact_sheet(SALIDA))


if __name__ == "__main__":
    main()
