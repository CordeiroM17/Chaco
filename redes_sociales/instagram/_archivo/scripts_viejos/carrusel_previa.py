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
PARTIDO ARMADO ACÁ: CA Mitre (LOCAL, en Santiago del Estero) · fecha 29 ·
domingo 13/09 16:00.
Antecedente usado: Chaco For Ever 1-1 Mitre (la ida, en el Coloso, 26/04/2026,
fecha 11).
Informe base:
  outputs/temporadas/2026/pre_partido/mitre_a/Informe_pre_partido_mitre.tex
Contexto: Mitre es 12° con 31 puntos (6V-13E-9D, 27 GF - 35 GC). Es el equipo
que más empata de la categoría (13 de 28). Tres DT en el año; Claudio Biaggio
dirige desde julio. De local rinde 1.43 pts/pj (5-5-4) y de visitante 0.79
(1 solo triunfo afuera): nos toca su versión de local. Juega 4-4-2 (16/28) o
4-2-3-1. Marcos Machado hizo 11 de sus 27 goles (41%), titular en los 28
partidos; detrás nadie pasa de 2. Concede más que nosotros (1.25 gol / 1.20
xGA) y sufre la pelota parada: 5 goles de saque de banda en contra (sobre 1.9
de xG), 5 de córner, 4 penales. Ataque muy central (66% de los remates de
frente al arco, entropía 34%). Markov: desde el 0-0 el próximo gol es en contra
suya el 64% (n=28); ganando 1-0 lo empatan el 50% (n=8).
Historial: 3 cruces, Chaco 0V-1E-2D (nunca le ganó). La ida de este año
(1-1 en el Coloso) la dominamos: xG 1.47-0.61, 17-12 remates, 8-2 córners;
nos pusimos 1-0 a los 5' y nos empataron a los 55'.
Chaco: 11° con 32 pts, 4 fechas sin perder, ciclo Cravero 20/30. Caprio con el
arco en cero en sus últimos 4 partidos.
Notas de armado de esta fecha:
  - Sin placas de amarillas ni de riesgo de suspensión (convención de la cuenta).
  - Sin lesiones ni bajas propias en las placas (la previa no anticipa ausencias
    nuestras) — Pacheco está suspendido pero eso no va acá.
  - Escudo de Mitre bajado con scripts/bajar_escudos.py -> assets/escudos/ca_mitre.png.
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
    "fecha": 29,
    "rival": "Mitre",
    "condicion": "visitante",                  # 'local' o 'visitante'
    "portada_bajada": (
        "Visitamos a un rival directo que nos saca apenas un punto. Es el "
        "equipo que más empata del torneo y nunca le ganamos, pero en abril lo "
        "dominamos y se nos escapó 1-1. "
        "Deslizá →"),
    # Escudos: salen de assets/escudos/<archivo>. Si falta el png, la placa no lo dibuja.
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "ca_mitre.png",

    # ---- Ficha del rival (slide 03): título/bajada según la condición --------
    "ficha_rival_titulo": "Mitre de local",
    "ficha_rival_sub": "Nos toca su mejor versión: en su cancha no pierde hace cuatro fechas",

    # ---- 1) EL RASGO DEL RIVAL: el rey del empate --------------------------
    "d1_kicker": "EL RIVAL",
    "d1_num": "13",
    "d1_lab": "los empates de Mitre en 28 fechas",
    "d1_ctx": (
        "Casi uno de cada dos partidos. Es, por lejos, el equipo que más iguala "
        "del torneo. Llega 12° con 31 puntos, uno menos que nosotros, peleando "
        "lo mismo: despegarse del fondo."),

    # ---- 2) MITRE DE LOCAL (que es lo que nos toca) -----------------------
    "visit_stats": [
        ("Récord de local", "5V - 5E - 4D"),
        ("Puntos por partido en casa", "1.43"),
        ("Goles de local (a favor - en contra)", "17 - 16"),
        ("De visitante baja a", "0.79 pts/pj"),
        ("Dibujo", "4-4-2"),
        ("DT", "Claudio Biaggio"),
    ],

    # ---- 3) SU AMENAZA: Machado -------------------------------------------
    "nasta_hero": "11",
    "nasta_hero_sub": "los goles de Marcos Machado, el 41% de los de todo Mitre",
    "nasta_col_izq": ("Goles", "11", "nadie más pasa de 2"),
    "nasta_col_der": ("Titular", "28 de 28", "no faltó nunca"),
    "nasta_kicker": "SU AMENAZA",
    "nasta_franja": "Si se apaga Machado, se apaga casi la mitad del ataque de Mitre",

    # ---- 4) DÓNDE LASTIMARLO: la pelota parada -----------------------------
    "d2_kicker": "DÓNDE LASTIMARLO",
    "d2_num": "5",
    "d2_lab": "los goles que Mitre recibió de saque de banda",
    "d2_ctx": (
        "Más del doble de lo que esa jugada vale: apenas 1.9 de xG en contra de "
        "lateral en toda la temporada. Suma otros 5 de córner y regaló 4 penales: "
        "sufre con la pelota detenida cerca de su área."),

    # ---- 5) CÓMO ATACA: directo y previsible ------------------------------
    "d3_kicker": "CÓMO ATACA",
    "d3_num": "66%",
    "d3_lab": "de los remates de Mitre salen de la zona central",
    "d3_ctx": (
        "Un ataque directo y previsible: dos tercios de sus tiros salen del "
        "mismo lugar, de frente al arco. Genera poco (0.94 de xG por partido, "
        "de los más flojos de la zona) y siempre por el mismo lado."),

    # ---- 6) EL ÚLTIMO CRUCE (la ida) -------------------------------------
    # Ojo: acá se carga tal como se jugó la ida (quién fue local ESA vez).
    "ida_local": "Chaco For Ever",
    "ida_gl": 1,
    "ida_visitante": "Mitre",
    "ida_gv": 1,
    "ida_fecha_txt": "El antecedente · la ida · Fecha 11",
    "ida_detalle": (
        "1-1 en el gigante, el 26 de abril. Nos pusimos 1-0 a los 5 minutos y "
        "nos empataron a los 55."),
    # Ficha de la ida, en orden Chaco - Mitre
    "ida_stats": [
        ("Posesión", "50% – 50%"),
        ("xG (goles esperados)", "1.47 – 0.61"),
        ("Remates", "17 – 12"),
        ("Remates al arco", "5 – 5"),
        ("Córners", "8 – 2"),
        ("Resultado", "1 – 1"),
    ],
    # El dato de la ida: lo dominamos y no lo ganamos
    "ida_dato_num": "8",
    "ida_dato_lab": "los córners que tiró el Negro en la ida, contra 2 de Mitre",
    "ida_dato_ctx": (
        "Dominamos de principio a fin —17 remates a 12, 1.47 de xG a 0.61— y no "
        "lo pudimos ganar. El empate es la marca registrada de Mitre."),

    # ---- 7) CÓMO SE MUEVE EL MARCADOR (Markov del rival) -----------------
    "vuelve_kicker": "CÓMO SE MUEVE EL MARCADOR",
    "vuelve_num": "64%",
    "vuelve_lab": "desde el 0-0, el próximo gol de Mitre suele ser en contra",
    "vuelve_ctx": (
        "Le cuesta romper el empate más que a ningún rival del año. Y si igual "
        "se pone 1-0, lo empatan el 50% de las veces: consigue la ventaja pero "
        "no la sostiene."),

    # ---- 8) EL ARQUERO: Caprio en su mejor momento --------------------------
    "arquero_kicker": "EL ARQUERO",
    "arquero_num": "4",
    "arquero_lab": "los arcos en cero al hilo de N. Caprio",
    "arquero_ctx": (
        "No recibió goles en ninguno de sus últimos cuatro partidos. Bajo el "
        "ciclo de Cravero el Negro concede 0.50 gol por partido y lleva seis "
        "vallas invictas en diez."),

    # ---- 9) CÓMO LLEGA EL NEGRO ---------------------------------------------
    "llega_hero": "11°",
    "llega_hero_sub": "con 32 puntos, uno más que Mitre y con cuatro fechas sin perder",
    "llega_col_izq": ("Últimos 5", "LWWDW", "5 goles a favor, 1 en contra"),
    "llega_col_der": ("Porcentaje de descenso", "1,8%", "en la fecha 19 era 30%"),
    "llega_kicker": "CÓMO LLEGA",
    "llega_franja": "Con Cravero, 20 puntos de 30 en diez fechas",

    # ---- Cierre -------------------------------------------------------------
    "cierre_frase": (
        "Mitre es el equipo que más empata del torneo y aun no le ganamos. Pero "
        "en abril los dominamos, hoy llegamos más arriba en la tabla. Con una "
        "racha defensiva y seguridad atras. La cuenta pendiente se resuelve visitandolos."),
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
        d["ficha_rival_titulo"],
        d["ficha_rival_sub"],
        d["visit_stats"],
        nota=NOTA, destacar="Puntos por partido afuera"))

    # 04 — SU AMENAZA: el jugador a controlar
    slides.append(P.dato_vs(
        d["nasta_hero"], d["nasta_hero_sub"],
        col_izq=d["nasta_col_izq"], col_der=d["nasta_col_der"],
        kicker=d["nasta_kicker"], franja=d["nasta_franja"], nota=NOTA))

    # 05 — DÓNDE LASTIMARLO: la pelota parada
    slides.append(P.dato(
        d["d2_num"], d["d2_lab"], d["d2_ctx"],
        kicker=d["d2_kicker"], nota=NOTA))

    # 06 — CÓMO ATACA: por juego abierto
    slides.append(P.dato(
        d["d3_num"], d["d3_lab"], d["d3_ctx"],
        kicker=d["d3_kicker"], nota=NOTA))

    # 07 — EL ÚLTIMO CRUCE: resultado de la ida (con escudos)
    # Los escudos siguen a quién fue local ESA vez, que no siempre somos nosotros.
    negro_de_local = d["ida_local"] == "Chaco For Ever"
    esc_negro, esc_rival = _ruta(d["escudo_negro"]), _ruta(d["escudo_rival"])
    # o van los dos escudos o no va ninguno: con uno solo la placa queda torcida
    if not (esc_negro and esc_rival):
        esc_negro = esc_rival = None
    slides.append(P.resultado(
        d["ida_local"], d["ida_gl"], d["ida_visitante"], d["ida_gv"],
        torneo=d["ida_fecha_txt"],
        detalle=d["ida_detalle"],
        nota="SofaScore",
        logo_local=esc_negro if negro_de_local else esc_rival,
        logo_visitante=esc_rival if negro_de_local else esc_negro))

    # 08 — CÓMO FUE LA IDA EN NÚMEROS
    slides.append(P.ficha(
        "La ida, dato por dato",
        f"Chaco For Ever vs {d['rival']} · el último cruce",
        d["ida_stats"],
        nota=NOTA, destacar="xG (goles esperados)"))

    # 09 — EL DATO DE LA IDA
    slides.append(P.dato(
        d["ida_dato_num"], d["ida_dato_lab"], d["ida_dato_ctx"],
        kicker="EL DATO DE LA IDA", nota=NOTA))

    # 10 — EL TRAMO CLAVE
    slides.append(P.dato(
        d["vuelve_num"], d["vuelve_lab"], d["vuelve_ctx"],
        kicker=d["vuelve_kicker"], nota=NOTA))

    # 11 — EL ARQUERO
    slides.append(P.dato(
        d["arquero_num"], d["arquero_lab"], d["arquero_ctx"],
        kicker=d["arquero_kicker"], nota=NOTA))

    # 12 — CÓMO LLEGA EL NEGRO
    slides.append(P.dato_vs(
        d["llega_hero"], d["llega_hero_sub"],
        col_izq=d["llega_col_izq"], col_der=d["llega_col_der"],
        kicker=d["llega_kicker"], franja=d["llega_franja"], nota=NOTA))

    # 13 — CITA DE CIERRE
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
