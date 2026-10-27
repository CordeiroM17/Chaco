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

    python scripts/carrusel_previa_almirante_brown.py

Los tres slots de dato suelto (2, 5 y 6) son genéricos: cada uno trae su propio
kicker, porque lo que define a un rival cambia de fecha en fecha (una baja, un
vicio, un récord).

------------------------------------------------------------------------------
PARTIDO ARMADO ACÁ: Almirante Brown (VISITANTE, jugamos de LOCAL) · fecha 30 ·
sábado 19/09, horario a confirmar en SofaScore al momento de armar esto.
Antecedente usado: Almirante Brown 1-0 Chaco For Ever (la ida, en Isidro
Casanova, 03/05/2026, fecha 12).
Informe base:
  outputs/temporadas/2026/pre_partido/almirante_brown_h/Informe_pre_partido_almirante_brown.tex
Contexto: Almirante es 5° con 46 puntos (12V-10E-7D, 30 GF - 23 GC), candidato
firme al Reducido (99.8% en la simulación Dixon-Coles). DT Andrés Montenegro
desde el 19/04. De visitante rinde la mitad que de local (1.07 vs 2.07 pts/pj,
8 GF - 10 GC en 14 partidos afuera): nos toca justo esa versión, y en nuestra
cancha. En xG genera y concede casi lo mismo que nosotros (0.95/0.97), pero
recibió muchos menos goles reales de los esperados (0.55 sobre 0.97 de xGA,
~12 goles de diferencia en 29 fechas) — se explica por el arquero B. Galván
sobre-rindiendo, no por una defensa objetivamente mejor. Ataque repartido: el
goleador del año tiene apenas 3 goles; M. Abreliano es el más asociado (2
goles, 4 asistencias). Sufre la pelota parada: de córner recibió 46 remates y
5.30 de xG en contra (el doble de lo que generó él, 29 remates/3.68 xG) pero
solo le convirtieron 2 — otra vez, mérito del arquero. Markov: desde el 0-0
rompe el cero a su favor el 72% de las veces (n=25, la más alta de los rivales
scouteados); si se pone 1-0, lo empatan el 60% (n=10).
Historial: 3 cruces, Chaco 1V-1E-1D. La ida de este año (3/05, Isidro Casanova)
la perdimos 0-1 pese a ganar el xG (0.83-0.62, 11-7 remates, 6-3 córners a
nuestro favor): dominamos hasta el gol de S. Vera al 84', y ya con el resultado
en contra M. Silvera vio la roja en el último minuto (no fue la causa de la
derrota, llegó después del gol).
Chaco: 11° con 33 puntos, últimos 5 WWDWD sin recibir goles, invictos de local
bajo Cravero (4V-1E-0D en 5). Descenso: 2,2% (bajó del 30% cuando llegó
Cravero).
Notas de armado de esta fecha:
  - Sin placas de amarillas ni de riesgo de suspensión (convención de la cuenta).
  - Sin lesiones ni bajas propias en las placas (la previa no anticipa ausencias
    nuestras) — Pacheco sigue suspendido pero eso no va acá.
  - Escudo de Almirante Brown bajado con scripts/bajar_escudos.py ->
    assets/escudos/almirante_brown.png.
  - El ángulo de "fiesta de local" (jugamos en casa contra su peor versión, más
    la baja de categoría de Sarmiento de Resistencia en el Federal A) va en el
    texto de publicación (texto_publicacion.md), no en las placas: son datos
    de otro torneo / contexto editorial, no estadística propia del rival.
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
    "fecha": 30,
    "rival": "Almirante Brown",
    "condicion": "local",                  # 'local' o 'visitante'
    "rival_corto": "Almirante",   # solo para el título de tapa (nombre largo no entra en 2 líneas)
    "portada_bajada": (
        "Nos visita un candidato al Reducido. No perdimos en casa con "
        "Cravero. Que sea una fiesta. "
        "Deslizá →"),
    # Escudos: salen de assets/escudos/<archivo>. Si falta el png, la placa no lo dibuja.
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "almirante_brown.png",

    # ---- Ficha del rival (slide 03): título/bajada según la condición --------
    "ficha_rival_titulo": "Almirante, de visitante",
    "ficha_rival_sub": "Rinde la mitad que de local",

    # ---- 1) EL RASGO DEL RIVAL: su arquero sobre-rindiendo -----------------
    "d1_kicker": "EL RIVAL",
    "d1_num": "12",
    "d1_lab": "los goles que el arquero de Almirante evitó de más",
    "d1_ctx": (
        "En xG, Almirante rinde exactamente igual que nosotros (0.95 contra "
        "0.97 por partido). Lo que lo tiene 5° es que Galván, su arquero, "
        "atajó unos 12 goles más de los que el modelo esperaba en 29 fechas."),

    # ---- 2) ALMIRANTE DE VISITANTE (que es lo que nos toca) -----------------
    "visit_stats": [
        ("Récord de visitante", "3V - 6E - 5D"),
        ("Puntos por partido afuera", "1.07"),
        ("Goles de visitante (a favor - en contra)", "8 - 10"),
        ("De local sube a", "2.07 pts/pj"),
        ("Dibujo más usado", "4-2-3-1 / 3-4-3"),
        ("DT", "Andrés Montenegro"),
    ],

    # ---- 3) SU AMENAZA: Abreliano, no un solo delantero --------------------
    "nasta_hero": "4",
    "nasta_hero_sub": "las asistencias de M. Abreliano, el más asociado del equipo",
    "nasta_col_izq": ("Asistencias", "4", "el que más reparte"),
    "nasta_col_der": ("Goles", "2", "también aporta gol"),
    "nasta_kicker": "SU AMENAZA",
    "nasta_franja": "No hay un solo delantero que apagar: el peligro pasa por él",

    # ---- 4) DÓNDE LASTIMARLO: la pelota parada -----------------------------
    "d2_kicker": "DÓNDE LASTIMARLO",
    "d2_num": "46",
    "d2_lab": "los remates que recibió Almirante de córner en la temporada",
    "d2_ctx": (
        "Más del doble de lo que generó él mismo de esa jugada (29 remates). "
        "Le tiraron 5.30 de xG en contra por córner y solo le convirtieron 2: "
        "la pelota parada es un punto débil real, disimulado por su arquero."),

    # ---- 5) CÓMO ATACA: repartido, sin un nombre propio --------------------
    "d3_kicker": "CÓMO ATACA",
    "d3_num": "7",
    "d3_lab": "jugadores distintos anotaron 2 goles o más para Almirante",
    "d3_ctx": (
        "Nadie concentra sus goles: el goleador del equipo tiene apenas "
        "3 goles en toda la temporada. Un ataque repartido, sin una figura "
        "individual para anular con marca personal."),

    # ---- 6) EL ÚLTIMO CRUCE (la ida) -------------------------------------
    # Ojo: acá se carga tal como se jugó la ida (quién fue local ESA vez).
    "ida_local": "Almirante Brown",
    "ida_gl": 1,
    "ida_visitante": "Chaco For Ever",
    "ida_gv": 0,
    "ida_fecha_txt": "El antecedente · la ida · Fecha 12",
    "ida_detalle": (
        "1-0 en Isidro Casanova, el 3 de mayo. Ganamos el duelo de xG (0.83 a "
        "0.62) y dominamos hasta el gol de S. Vera al 84'."),
    # Ficha de la ida, en orden Chaco - Almirante Brown
    "ida_stats": [
        ("Posesión", "41% – 59%"),
        ("xG (goles esperados)", "0.83 – 0.62"),
        ("Remates", "11 – 7"),
        ("Remates al arco", "4 – 5"),
        ("Córners", "6 – 3"),
        ("Resultado", "0 – 1"),
    ],
    # El dato de la ida: dominamos y no alcanzó
    "ida_dato_num": "6",
    "ida_dato_lab": "los córners que tiró el Negro en la ida",
    "ida_dato_ctx": (
        "11 remates a 7, 0.83 de xG a 0.62 y "
        "aun así perdimos con un gol sobre el final. Recién en el último minuto, ya "
        "en contra en el marcador, M. Silvera se fue expulsado."),

    # ---- 7) CÓMO SE MUEVE EL MARCADOR (Markov del rival) -----------------
    "vuelve_kicker": "CÓMO SE MUEVE EL MARCADOR",
    "vuelve_num": "72%",
    "vuelve_lab": "desde el 0-0, Almirante suele romper el cero a su favor",
    "vuelve_ctx": (
        "Es el rival que más rápido se pone en ventaja de toda la temporada. "
        "En la ida fue así: recién nos rompió el "
        "empate al 84'. Pero si se pone 1-0, lo empatan el 60% de las veces: "
        "no cierra los partidos."),

    # ---- 8) EL ARQUERO / LA RACHA PROPIA --------------------------------
    "arquero_kicker": "NUESTRA RACHA",
    "arquero_num": "5",
    "arquero_lab": "los partidos seguidos de N. Caprio sin recibir goles",
    "arquero_ctx": (
        "La mejor racha defensiva del año. Bajo el ciclo de Cravero, el "
        "equipo recibe 0.45 goles por partido y ya lleva 7 vallas invictas "
        "en 11 fechas."),

    # ---- 9) CÓMO LLEGA EL NEGRO ---------------------------------------------
    "llega_hero": "11°",
    "llega_hero_sub": "con 33 puntos, invictos en las últimas 5 de local con Cravero",
    "llega_col_izq": ("Últimos 5", "WWDWD", "5 goles a favor, 0 en contra"),
    "llega_col_der": ("Porcentaje de descenso", "2,2%", "en la fecha 19 era 30%"),
    "llega_kicker": "CÓMO LLEGA",
    "llega_franja": "De local con Cravero: 4V - 1E - 0D, invictos",

    # ---- Cierre -------------------------------------------------------------
    "cierre_frase": (
        "Recibimos a un candidato al Reducido. Su ataque se encuentra repartido y muy abierto. "
        "No perdimos de local con Cravero. Que sea una fiesta."),
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
        f"Ahora,\n{d['rival_corto']}",
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

    # 06 — CÓMO ATACA: repartido
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

    # 11 — NUESTRA RACHA
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
