# -*- coding: utf-8 -*-
"""
Carrusel ESTÁNDAR de PREVIA (pre-partido) para la cuenta de estadísticas de
Chaco For Ever. Es el gemelo de carrusel_partido.py, pero para ANTES de jugar.

La idea fija del formato (no se toca): contar el partido que viene apoyándose en
dos patas verificables —
  1) CÓMO FUE EL ÚLTIMO CRUCE contra ese mismo rival (resultado + números).
  2) CARACTERÍSTICAS DEL RIVAL (cómo juega, qué le funcionó).
y cerrar con CÓMO LLEGA EL NEGRO y la clave del partido.

Para la próxima previa NO se toca el código: se copian los valores nuevos en el
bloque DATOS, se apunta el escudo del rival y se corre:

    python scripts/carrusel_previa.py

Los tres slots de dato suelto (2, 5 y 6) son genéricos: cada uno trae su propio
kicker, porque lo que define a un rival cambia de fecha en fecha (una baja, un
vicio, un récord).

------------------------------------------------------------------------------
PARTIDO ARMADO ACÁ: Fecha 21 · San Miguel (LOCAL)
Antecedente usado: Fecha 3 · San Miguel 2-0 Chaco For Ever (visitante, 28/02/2026).
Números autoritativos del cruce de ida (data cruda SofaScore):
  data/temporadas/2026/partidos/2026-02-28_vs_san_miguel_a/
Informe base:
  outputs/temporadas/2026/pre_partido/san_miguel_h/Informe_pre_partido_san_miguel.tex
------------------------------------------------------------------------------
"""
from pathlib import Path
import placas as P
import marca as M
import temas

RAIZ = Path(__file__).resolve().parents[1]          # .../redes_sociales/instagram
PROYECTO = RAIZ.parents[1]                           # raíz del proyecto

# ==========================================================================
#  FIJO — no se toca entre previa y previa
# ==========================================================================
CUENTA = "@chacoforever.stats"
COMPETENCIA = "Primera Nacional 2026"
ESCUDOS = RAIZ / "assets" / "escudos"      # escudos reutilizables (uno por club)

# Identidad visual de la PREVIA: tema "hueso" (blanco cálido) para diferenciarla
# de un vistazo del post-partido (oscuro). Ver opciones en temas.py.
TEMA = "hueso"

# ==========================================================================
#  DATOS DE LA PREVIA — esto es lo ÚNICO que cambiás cada fecha
# ==========================================================================
DATOS = {
    # ---- Cabecera / próxima fecha -------------------------------------------
    "fecha": 21,
    "rival": "San Miguel",
    "condicion": "local",                     # 'local' o 'visitante'
    "portada_bajada": (
        "El Negro recibe al equipo que más empata de la liga: un rival de bloque "
        "bajo que afuera casi no gana. Repasamos al rival, la ida y cómo llega "
        "For Ever. Deslizá →"),
    # Escudos: salen de assets/escudos/<archivo>. Si falta el png, la placa no lo dibuja.
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "san_miguel.png",    # ← dejá el png acá para que salga

    # ---- 1) EL RASGO DEL RIVAL: el empate como forma de vida ----------------
    "d1_kicker": "EL RASGO DEL RIVAL",
    "d1_num": "10",
    "d1_lab": "de los 20 partidos de San Miguel terminaron empatados",
    "d1_ctx": (
        "La mitad. Es el equipo que más iguala del torneo: 5V - 10E - 5D, sin una "
        "racha ganadora en todo el año."),

    # ---- 2) SAN MIGUEL DE VISITANTE (que es lo que nos toca) ----------------
    "visit_stats": [
        ("Récord de visitante", "1V - 7E - 2D"),
        ("Puntos por partido", "1.00"),
        ("Goles afuera (a favor - en contra)", "8 - 13"),
        ("Posesión promedio", "46%"),
        ("Pelotazos largos por partido", "24.6"),
    ],

    # ---- 3) SU AMENAZA: NASTA ------------------------------------------------
    "nasta_hero": "5",
    "nasta_hero_sub": "los goles de Nasta, casi un tercio de los 17 de San Miguel",
    "nasta_col_izq": ("xG por partido", "0.436", "el más alto del plantel"),
    "nasta_col_der": ("Amarillas", "6", "+ 1 roja en 16 partidos"),
    "nasta_kicker": "SU AMENAZA",
    "nasta_franja": "Casi todo su peligro pasa por él",

    # ---- 4) EL PUNTO DÉBIL: las dos puntas del partido ----------------------
    "d2_kicker": "EL PUNTO DÉBIL",
    "d2_num": "62%",
    "d2_lab": "de los goles que recibe llegan en los primeros o últimos 15'",
    "d2_ctx": (
        "6 goles en contra en los primeros 15 minutos y 7 en los últimos 15. En el "
        "medio del partido es sólido: se lastima arrancando y cerrando."),

    # ---- 5) EL OTRO PUNTO DÉBIL: no sabe cerrar los partidos ----------------
    "d3_kicker": "NO LO CIERRA",
    "d3_num": "78%",
    "d3_lab": "de las veces que se puso 1-0 arriba, dejó escapar la ventaja",
    "d3_ctx": (
        "7 de 9, y 5 de esas después del minuto 70. Cuando le empatan o le dan "
        "vuelta el partido, no reacciona."),

    # ---- 6) EL ÚLTIMO CRUCE (la ida) ----------------------------------------
    # Ojo: acá se carga tal como se jugó la ida (quién fue local ESA vez).
    "ida_local": "San Miguel",
    "ida_gl": 2,
    "ida_visitante": "Chaco For Ever",
    "ida_gv": 0,
    # Ojo: entra como etiqueta de la placa, se pasa del ancho si es muy largo.
    "ida_fecha_txt": "El antecedente · Fecha 3 · 28/02",
    "ida_detalle": (
        "En su cancha perdimos 2-0, con goles de Delgado (67') y Ferrero (84'). El "
        "resultado no se pareció al partido: el Negro generó más y remató más."),
    # Ficha de la ida (destaca el xG: generamos más y perdimos igual)
    "ida_stats": [
        ("Posesión", "58% – 42%"),
        ("xG (goles esperados)", "0.91 – 1.39"),
        ("Tiros (al arco)", "12 (5) – 14 (4)"),
        ("Córners", "4 – 5"),
        ("Formación", "4-4-2 – 4-1-4-1"),
    ],
    # El dato de la ida: generamos más y perdimos igual
    "ida_dato_num": "1.39",
    "ida_dato_lab": "el xG que generó el Negro en la ida, contra 0.91 de ellos",
    "ida_dato_ctx": (
        "Con menos la pelota, el Negro llegó más y remató más. Terminó 2-0 en "
        "contra: la lección de la ida es la eficacia."),

    # ---- 7) CÓMO LLEGA EL NEGRO ---------------------------------------------
    "llega_hero": "3-1",
    "llega_hero_sub": "viene de ganar en cancha de San Telmo, la primera afuera",
    "llega_col_izq": ("Romero", "2 goles", "más una asistencia"),
    "llega_col_der": ("xG del partido", "1.85", "con apenas 32% de posesión"),
    "llega_kicker": "CÓMO LLEGA",
    "llega_franja": "Se rompió la sequía de visitante",

    # ---- Cierre --------------------------------------------------------------
    "cierre_frase": (
        "En la ida lo superamos en juego y perdimos 2-0. Ahora es en el Gigante, "
        "contra un equipo que viene a empatar, que se lastima en las dos puntas y "
        "que no sabe cerrar los partidos. Falta lo de siempre: meterlas."),
}

# --------------------------------------------------------------------------
SALIDA = RAIZ / "placas" / f"previa_fecha_{DATOS['fecha']}_{DATOS['rival'].lower().replace(' ', '_')}"
NOTA = f"Previa Fecha {DATOS['fecha']} · {COMPETENCIA} · SofaScore"


def _ruta(p):
    """str(p) si el archivo existe; None si no (escudos/gráficos opcionales)."""
    return str(p) if p and Path(p).exists() else None


def _condicion_txt():
    return "de local" if DATOS["condicion"] == "local" else "de visitante"


def construir():
    d = DATOS
    slides = []

    # 01 — PORTADA: la próxima fecha
    slides.append(P.portada(
        f"Ahora,\n{d['rival']}",
        d["portada_bajada"],
        etiqueta=f"Previa · Fecha {d['fecha']} · {_condicion_txt()}",
        nota="SofaScore"))

    # 02 — EL RASGO DEL RIVAL: el dato que lo define
    slides.append(P.dato(
        d["d1_num"], d["d1_lab"], d["d1_ctx"],
        kicker=d["d1_kicker"], nota=NOTA))

    # 03 — EL RIVAL EN LA CONDICIÓN QUE NOS TOCA
    slides.append(P.ficha(
        "San Miguel de visitante",
        "Nos visita, y afuera gana 1 de cada 10",
        d["visit_stats"],
        nota=NOTA, destacar="Puntos por partido"))

    # 04 — SU AMENAZA: el jugador a controlar
    slides.append(P.dato_vs(
        d["nasta_hero"], d["nasta_hero_sub"],
        col_izq=d["nasta_col_izq"], col_der=d["nasta_col_der"],
        kicker=d["nasta_kicker"], franja=d["nasta_franja"], nota=NOTA))

    # 05 — EL PUNTO DÉBIL: dónde se lo puede lastimar
    slides.append(P.dato(
        d["d2_num"], d["d2_lab"], d["d2_ctx"],
        kicker=d["d2_kicker"], nota=NOTA))

    # 06 — EL SEGUNDO PUNTO DÉBIL
    slides.append(P.dato(
        d["d3_num"], d["d3_lab"], d["d3_ctx"],
        kicker=d["d3_kicker"], nota=NOTA))

    # 07 — EL ÚLTIMO CRUCE: resultado de la ida (con escudos)
    # Los escudos siguen a quién fue local ESA vez, que no siempre somos nosotros.
    negro_de_local = d["ida_local"] == "Chaco For Ever"
    slides.append(P.resultado(
        d["ida_local"], d["ida_gl"], d["ida_visitante"], d["ida_gv"],
        torneo=d["ida_fecha_txt"],
        detalle=d["ida_detalle"],
        nota="SofaScore",
        logo_local=_ruta(d["escudo_negro"] if negro_de_local else d["escudo_rival"]),
        logo_visitante=_ruta(d["escudo_rival"] if negro_de_local else d["escudo_negro"])))

    # 08 — CÓMO FUE LA IDA EN NÚMEROS
    slides.append(P.ficha(
        "La ida, dato por dato",
        f"Chaco For Ever vs {d['rival']} · el último cruce",
        d["ida_stats"],
        nota=NOTA, destacar="xG (goles esperados)"))

    # 09 — EL DATO DE LA IDA (generó mucho, no le alcanzó)
    slides.append(P.dato(
        d["ida_dato_num"], d["ida_dato_lab"], d["ida_dato_ctx"],
        kicker="EL DATO DE LA IDA", nota=NOTA))

    # 10 — CÓMO LLEGA EL NEGRO
    slides.append(P.dato_vs(
        d["llega_hero"], d["llega_hero_sub"],
        col_izq=d["llega_col_izq"], col_der=d["llega_col_der"],
        kicker=d["llega_kicker"], franja=d["llega_franja"], nota=NOTA))

    # 11 — CITA DE CIERRE
    slides.append(P.cita(
        d["cierre_frase"], autor="La previa", nota=None))

    return slides


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    temas.aplicar(TEMA)                 # la previa sale en su tema propio
    imgs = construir()
    for i, img in enumerate(imgs, 1):
        M.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")

    # contact-sheet de vista previa
    from PIL import Image
    files = sorted(SALIDA.glob("[0-9]*.png"))
    th = [Image.open(f).convert("RGB").resize((300, 300)) for f in files]
    cols = 3
    rows = (len(th) + cols - 1) // cols
    s = Image.new("RGB", (cols * 300 + (cols + 1) * 10, rows * 300 + (rows + 1) * 10), (45, 45, 45))
    for i, t in enumerate(th):
        r, c = divmod(i, cols)
        s.paste(t, (10 + c * 310, 10 + r * 310))
    s.save(SALIDA / "_preview.png")
    print("OK _preview.png ->", SALIDA)


if __name__ == "__main__":
    main()
