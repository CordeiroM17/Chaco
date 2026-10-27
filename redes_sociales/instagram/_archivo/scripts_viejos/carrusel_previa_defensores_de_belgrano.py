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

    python scripts/carrusel_previa_defensores_de_belgrano.py

------------------------------------------------------------------------------
PARTIDO ARMADO ACÁ: Chaco For Ever (LOCAL) vs Defensores de Belgrano · fecha 32 ·
domingo 04/10/2026, 17:00 hora Argentina.
Antecedente usado: Defensores de Belgrano 0-0 Chaco For Ever (18/05/2026, fecha 14).
Informe base:
  outputs/temporadas/2026/pre_partido/defensores_de_belgrano_h/Informe_pre_partido_defensores_de_belgrano.tex
Contexto: rival directo, 11° con 36 puntos (8V-12E-11D, 23 GF - 27 GC), igualado
con Chaco (10°, 36). Genera 1.08 de xG por partido y marca 0.74 (unos 10 goles
menos de lo esperado en 31 fechas); en defensa recibe lo esperado, así que NO lo
sostiene el arquero (a diferencia de Almirante Brown y Bolívar). De visitante
suma 1.07 pts/pj (4V-4E-7D). Mediocampo muy superior al nuestro (73 contra 21
de percentil promedio, Tomasso en el 99); zaga floja (25) y delanteros por debajo
de los nuestros (51 contra 80). Goleador E. González (8), creador E. Aguirre
(5 asistencias). Concede 4 goles en 27 remates de pelota parada y 3 en 42 de
lateral. 5 penales a favor (4 convertidos). Markov: el próximo gol tras el 0-0
es en contra suya el 57%; si se pone 1-0 lo alcanzan el 50%.
Notas de armado de esta fecha:
  - Escudo de Defensores de Belgrano bajado de TheSportsDB (SofaScore no lo dio)
    -> assets/escudos/defensores_de_belgrano.png.
  - Slot "OJO" (d2b) usado para el mediocampo rival en vez de la pelota parada.
  - "ficha_rival_destacar" nuevo en DATOS: la fila que se resalta de la ficha del
    rival (antes fija en "Puntos por partido de local").
  - Sin placas de amarillas ni de suspensiones (convención de la cuenta): la
    baja de Luque no va en las placas.
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
    "fecha": 32,
    "rival": "Defensores de Belgrano",
    "condicion": "local",                  # 'local' o 'visitante' (el Negro)
    "rival_corto": "Defensores",   # solo para el título de tapa (nombre largo no entra en 2 líneas)
    "portada_bajada": (
        "Recibimos a un rival directo, con los mismos 36 puntos, que genera "
        "más de lo que convierte. Deslizá →"),
    # Escudos: salen de assets/escudos/<archivo>. Si falta el png, la placa no lo dibuja.
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "defensores_de_belgrano.png",

    # ---- Ficha del rival (slide 03): título/bajada según la condición --------
    "ficha_rival_titulo": "Defensores, de visitante",
    "ficha_rival_sub": "Rinde menos que de local",
    "ficha_rival_destacar": "Puntos por partido de visitante",

    # ---- 1) EL RASGO DEL RIVAL: genera y no convierte ----------------------
    "d1_kicker": "EL RIVAL",
    "d1_num": "10",
    "d1_lab": "los goles que Defensores no convirtió en 31 fechas",
    "d1_ctx": (
        "Genera 1.08 de xG por partido y marca 0.74. Su problema no es el "
        "arquero: es la definición."),

    # ---- 2) DEFENSORES DE VISITANTE (que es lo que nos toca) ---------------
    "visit_stats": [
        ("Récord de visitante", "4V - 4E - 7D"),
        ("Puntos por partido de visitante", "1.07"),
        ("Goles de visitante (a favor - en contra)", "10 - 13"),
        ("De local sube a", "1.25 pts/pj"),
        ("Dibujo más usado", "4-4-2"),
        ("Últimos 5", "3V - 1E - 1D"),
    ],

    # ---- 3) SU AMENAZA: González y Aguirre ---------------------------------
    "nasta_hero": "8",
    "nasta_hero_sub": "Los goles de E. González, más del doble que cualquier compañero",
    "nasta_col_izq": ("Goles de González", "8", "Gana casi todo por arriba"),
    "nasta_col_der": ("Asistencias de Aguirre", "5", "El que crea el ataque"),
    "nasta_kicker": "SU AMENAZA",
    "nasta_franja": "El gol y la creación dependen de dos nombres",

    # ---- 4) DÓNDE LASTIMARLO: la pelota parada -----------------------------
    "d2_kicker": "DÓNDE LASTIMARLO",
    "d2_num": "4",
    "d2_lab": "los goles que recibió de pelota parada en 27 remates",
    "d2_ctx": (
        "Y otros 3 de lateral en 42 remates. De córner casi no sufre: 1 gol "
        "en 37 remates. El lateral es la vía."),

    # ---- 5) CÓMO ATACA: los penales ----------------------------------------
    "d3_kicker": "CÓMO ATACA",
    "d3_num": "5",
    "d3_lab": "los penales a favor que tuvo Defensores, 4 convertidos",
    "d3_ctx": (
        "Cerca del 11% de su xG del año viene del punto penal. Hay que "
        "evitar las faltas dentro del área."),

    # ---- 5b) JUGADOR POR JUGADOR: cómo es cada uno (sin percentiles) -------
    "clave_kicker": "ASÍ LLEGA EL RIVAL",
    "clave_titulo": "Jugador por jugador",
    "clave_sub": "Lo bueno y lo flojo de tres piezas clave, sin vueltas",
    "clave_jugadores": [
        ("E. González", "Delantero (el goleador)",
         "Gana casi todo por arriba - Es el goleador del equipo",
         "Casi no asiste - Poco juego asociativo"),
        ("E. Aguirre", "Delantero (el que crea)",
         "Cinco asistencias - Entre los que más crean de la liga",
         "Casi no gana por arriba - Pocos goles"),
        ("A. Pérez", "Central",
         "Lanza pelotas largas mejor que casi nadie",
         "Casi no despeja - Pierde duelos aéreos y por abajo"),
    ],

    # ---- 5c) DÓNDE ATACAR ---------------------------------------------------
    "atacar_kicker": "DÓNDE ATACAR",
    "atacar_num": "2",
    "atacar_lab": "vías concretas para lastimarlo el domingo",
    "atacar_ctx": (
        "La pelota aérea, con Pacheco, Garay y Silvera ante una zaga floja "
        "por arriba. Y el lateral: ahí es donde más goles recibe."),

    # ---- 5d) OJO: el mediocampo --------------------------------------------
    "d2b_kicker": "OJO",
    "d2b_num": "73",
    "d2b_lab": "el nivel de su mediocampo contra 21 del nuestro",
    "d2b_ctx": (
        "Percentil promedio en la categoría. Es la única línea donde nos "
        "supera con claridad, con Tomasso en el 99. Cuidar la salida."),

    # ---- 6) EL ÚLTIMO CRUCE ------------------------------------------------
    # Ojo: acá se carga tal como se jugó, quién fue local ESA vez.
    "ida_local": "Defensores de Belgrano",
    "ida_gl": 0,
    "ida_visitante": "Chaco For Ever",
    "ida_gv": 0,
    "ida_fecha_txt": "El último cruce · Fecha 14",
    "ida_detalle": (
        "0-0 en la cancha de Defensores, el 18 de mayo. Perdimos el duelo de "
        "xG (0.33 a 0.65) y nos sostuvo Caprio, la figura con 8.7."),
    # Ficha del cruce, en orden Chaco - Defensores
    "ida_stats": [
        ("Posesión", "40% – 60%"),
        ("xG (goles esperados)", "0.33 – 0.65"),
        ("Remates", "9 – 13"),
        ("Remates al arco", "3 – 6"),
        ("Córners", "3 – 2"),
        ("Resultado", "0 – 0"),
    ],
    "ida_ficha_titulo": "El último cruce",
    # El dato del cruce
    "ida_dato_num": "8.7",
    "ida_dato_lab": "el rating de Caprio en el 0-0 de mayo",
    "ida_dato_ctx": (
        "Defensores tuvo el doble de xG (0.65 a 0.33) y no pudo convertir. "
        "En tres cruces, nunca nos hizo un gol."),

    # ---- 7) CÓMO SE MUEVE EL MARCADOR (Markov del rival) -----------------
    "vuelve_kicker": "CÓMO SE MUEVE EL MARCADOR",
    "vuelve_num": "57%",
    "vuelve_lab": "de las veces, el primer gol tras el 0-0 es en contra de Defensores",
    "vuelve_ctx": (
        "Le cuesta imponerse desde el empate. Si se pone 1-0, se lo "
        "alcanzan la mitad de las veces: no cierra los partidos."),

    # ---- 8) NUESTRA CASA ----------------------------------------------------
    "arquero_kicker": "NUESTRA CASA",
    "arquero_num": "5",
    "arquero_lab": "victorias en 5 partidos de local con Cravero",
    "arquero_ctx": (
        "Sin recibir un solo gol en casa. Venimos de perder en Bolívar, que "
        "cortó seis partidos sin derrota."),

    # ---- 9) CÓMO LLEGA EL NEGRO ---------------------------------------------
    "llega_hero": "10°",
    "llega_hero_sub": "con 36 puntos, los mismos que Defensores (11°)",
    "llega_col_izq": ("Últimos 5", "2V-2E-1D", "3 a favor, 2 en contra"),
    "llega_col_der": ("De local sumamos", "1.67", "pts por partido"),
    "llega_kicker": "CÓMO LLEGA",
    "llega_franja": "Con Cravero de local: 5 de 5 y 0 goles en contra",

    # ---- Cierre -------------------------------------------------------------
    "cierre_frase": (
        "Es un rival directo con los mismos 36 puntos. Cuidar el mediocampo, "
        "buscar la pelota aérea y jugar sin apuro: en casa ganamos 5 de 5."),
}

# --------------------------------------------------------------------------
SALIDA = RAIZ / "placas" / f"previa_fecha_{DATOS['fecha']}_{DATOS['rival'].lower().replace(' ', '_').replace('í', 'i')}"
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
        nota=NOTA, destacar=d.get("ficha_rival_destacar", "Puntos por partido de local")))

    # 04 — SU AMENAZA: el jugador a controlar
    slides.append(P.dato_vs(
        d["nasta_hero"], d["nasta_hero_sub"],
        col_izq=d["nasta_col_izq"], col_der=d["nasta_col_der"],
        kicker=d["nasta_kicker"], franja=d["nasta_franja"], nota=NOTA))

    # 05 — DÓNDE LASTIMARLO: la pelota parada
    slides.append(P.dato(
        d["d2_num"], d["d2_lab"], d["d2_ctx"],
        kicker=d["d2_kicker"], nota=NOTA))

    # 05b — OJO: esa vulnerabilidad viene achicándose en sus últimos partidos
    slides.append(P.dato(
        d["d2b_num"], d["d2b_lab"], d["d2b_ctx"],
        kicker=d["d2b_kicker"], nota=NOTA))

    # 06 — CÓMO ATACA: repartido
    slides.append(P.dato(
        d["d3_num"], d["d3_lab"], d["d3_ctx"],
        kicker=d["d3_kicker"], nota=NOTA))

    # 06b — JUGADOR POR JUGADOR: lo bueno y lo flojo, sin percentiles
    slides.append(P.jugadores_clave(
        d["clave_titulo"], d["clave_jugadores"],
        subtitulo=d["clave_sub"], nota=NOTA, kicker=d["clave_kicker"]))

    # 06c — DÓNDE ATACAR: los dos costados
    slides.append(P.dato(
        d["atacar_num"], d["atacar_lab"], d["atacar_ctx"],
        kicker=d["atacar_kicker"], nota=NOTA))

    # 07 — EL ÚLTIMO CRUCE: resultado del único antecedente (con escudos)
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

    # 08 — CÓMO FUE EL CRUCE EN NÚMEROS
    slides.append(P.ficha(
        d.get("ida_ficha_titulo", "El único cruce, dato por dato"),
        f"Chaco For Ever vs {d['rival']} · el antecedente",
        d["ida_stats"],
        nota=NOTA, destacar="xG (goles esperados)"))

    # 09 — EL DATO DEL CRUCE
    slides.append(P.dato(
        d["ida_dato_num"], d["ida_dato_lab"], d["ida_dato_ctx"],
        kicker="EL DATO DEL CRUCE", nota=NOTA))

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
