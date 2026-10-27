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

    python scripts/carrusel_previa_ciudad_de_bolivar.py

------------------------------------------------------------------------------
PARTIDO ARMADO ACÁ: Ciudad de Bolívar (LOCAL, jugamos de VISITANTE) · fecha 31 ·
sábado 26/09/2026, 16:00 hora Argentina.
Antecedente usado: Chaco For Ever 0-1 Ciudad de Bolívar (único cruce, en
nuestra cancha, 10/05/2026, fecha 13).
Informe base:
  outputs/temporadas/2026/pre_partido/ciudad_de_bolivar_a/Informe_pre_partido_ciudad_de_bolivar.tex
Contexto: Ciudad de Bolívar es 8° con 39 puntos (9V-12E-9D, 24 GF - 27 GC),
un equipo de mitad de tabla que empata muchísimo (12 de 30, 40%). Un solo DT
en toda la temporada, Diego Funes, sin cambios. De local rinde incluso menos
que de visitante (1.27 vs 1.33 pts/pj): la localidad no le suma. En xG genera
poco (0.82/pj, nosotros 0.97) y concede mucho (1.28/pj, nosotros 0.93) — la
brecha de xG combinada más amplia que tenemos contra un rival esta temporada
(+0.50 a favor nuestro) — pero solo recibe 0.90 goles reales por partido
(~11 goles menos de los esperados en 30 fechas): mismo patrón que Almirante
Brown la fecha pasada, sostenido por su arquero A. Rufinetti (7.26 de rating,
el mejor del plantel, titular en los 30 partidos). Su gol está repartido
(G. Sánchez el goleador con apenas 5, pero peor percentil de su puesto en la
categoría; A. Gonzalez el más completo con 4 goles/1 asistencia y 7.04 de
rating). Sufre mucho la pelota parada (córner y lateral: recibe casi el doble
de remates de los que genera). Markov: le cuesta romper el 0-0 a su favor
(el próximo gol es en contra suya el 52% de las veces) y no sostiene bien una
ventaja mínima (lo empatan el 62% si se pone 1-0).
Historial: 1 solo cruce, 0V-0E-1D. Lo perdimos 0-1 en nuestra cancha (10/05,
fecha 13) dominando posesión (60%) y córners (9-7) pero sin un solo remate al
arco en 12 intentos — y también perdimos el duelo de xG (0.49 a 1.40), así
que a diferencia de otras derrotas del año esta la avala el modelo. Caprio
(8.4) y Ojeda (7.9) fueron los mejores esa tarde pese a la derrota.
Chaco: 10° con 36 puntos, últimos 5 con 3V-2E sin recibir goles, 6 fechas
seguidas con la valla en cero (la racha más larga del año, 0.33 goles
recibidos por partido con Cravero). Descenso: 0.25% (última simulación,
corrida tras la fecha 30, no repetida para esta previa).
Notas de armado de esta fecha:
  - Slide 05b (OJO, -52%) agregado después de armar el informe: la pelota
    parada del rival (córner + lateral) es una debilidad de la temporada
    completa, pero en sus últimos 10 partidos el xG que reciben por esa vía
    cayó a la mitad (0.29 -> 0.14/partido) y los remates concedidos también
    bajaron (3.90 -> 2.70/partido); de los 9 goles no relacionados con juego
    abierto en toda la temporada, solo 3 fueron en esos últimos 10 partidos.
    El juego abierto se mantuvo estable (0.94 vs 0.97 de xG recibido), así
    que la mejora es específica de la pelota parada, no una mejora general.
    Mismo ajuste hecho en el informe (secciones 3 y 8).
  - Sin placas de amarillas ni de riesgo de suspensión (convención de la
    cuenta). El informe base sí trae la alerta y pide confirmar con el club
    antes de publicarla en cualquier lado.
  - Sin lesiones ni bajas propias en las placas (la previa no anticipa
    ausencias nuestras).
  - Escudo de Ciudad de Bolívar bajado con scripts/bajar_escudos.py ->
    assets/escudos/ciudad_de_bolivar.png.
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
    "fecha": 31,
    "rival": "Ciudad de Bolívar",
    "condicion": "visitante",              # 'local' o 'visitante'
    "rival_corto": "Bolívar",     # solo para el título de tapa (nombre largo no entra en 2 líneas)
    "portada_bajada": (
        "Visitamos a un equipo de mitad de tabla que empata mucho y sostiene "
        "el resultado gracias a su arquero. Deslizá →"),
    # Escudos: salen de assets/escudos/<archivo>. Si falta el png, la placa no lo dibuja.
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "ciudad_de_bolivar.png",

    # ---- Ficha del rival (slide 03): título/bajada según la condición --------
    "ficha_rival_titulo": "Ciudad de Bolívar, de local",
    "ficha_rival_sub": "Rinde incluso menos que de visitante",

    # ---- 1) EL RASGO DEL RIVAL: su arquero sobre-rindiendo -----------------
    "d1_kicker": "EL RIVAL",
    "d1_num": "11",
    "d1_lab": "los goles que el arquero de Bolívar evitó de más",
    "d1_ctx": (
        "Concede 1.28 de xG por partido pero recibe solo 0.90 goles: 11 de "
        "menos en 30 fechas, sostenido por A. Rufinetti."),

    # ---- 2) CIUDAD DE BOLÍVAR DE LOCAL (que es lo que nos toca) -----------------
    "visit_stats": [
        ("Récord de local", "4V - 7E - 4D"),
        ("Puntos por partido de local", "1.27"),
        ("Goles de local (a favor - en contra)", "13 - 14"),
        ("De visitante sube a", "1.33 pts/pj"),
        ("Dibujo más usado", "4-4-2 / 4-2-3-1"),
        ("DT", "Diego Funes"),
    ],

    # ---- 3) SU AMENAZA: el gol, repartido -------------------------------
    "nasta_hero": "5",
    "nasta_hero_sub": "Los goles de G. Sánchez",
    "nasta_col_izq": ("Goles de Sánchez", "5", "El goleador del equipo"),
    "nasta_col_der": ("Rating de Gonzalez", "7.04", "4 goles, 1 asistencia"),
    "nasta_kicker": "SU AMENAZA",
    "nasta_franja": "El gol se reparte: nadie es una referencia dominante",

    # ---- 4) DÓNDE LASTIMARLO: la pelota parada -----------------------------
    "d2_kicker": "DÓNDE LASTIMARLO",
    "d2_num": "41",
    "d2_lab": "los remates que recibió Bolívar de córner en la temporada",
    "d2_ctx": (
        "Casi el doble de los 29 que generó. De lateral recibió 64 contra "
        "35 propios: volumen sobra, nos falta convertirlo."),

    # ---- 5) CÓMO ATACA: repartido, sin un nombre propio --------------------
    "d3_kicker": "CÓMO ATACA",
    "d3_num": "4",
    "d3_lab": "jugadores distintos hicieron 3 goles o más para Bolívar",
    "d3_ctx": (
        "Su goleador, G. Sánchez, tiene apenas 5 goles y ni es de los "
        "mejor puntuados. El gol está repartido."),

    # ---- 5b) JUGADOR POR JUGADOR: cómo es cada uno (sin percentiles) -------
    "clave_kicker": "ASÍ LLEGA EL RIVAL",
    "clave_titulo": "Jugador por jugador",
    "clave_sub": "Lo bueno y lo flojo de tres piezas clave, sin vueltas",
    "clave_jugadores": [
        ("A. Paredes", "Lateral derecho",
         "Casi no pierde la pelota",
         "Participa poco del ataque - Pocos pases clave"),
        ("F. Peralta", "Lateral izquierdo",
         "Recupera muchísimas pelotas - Cuesta ganarle el duelo individual",
         "Casi no ayuda cuando el equipo ataca - Centros imprecisos - Pocos pases clave"),
        ("G. Sánchez", "Delantero (el goleador)",
         "Es el goleador del equipo",
         "Fuera del gol, aporta poco - Poco juego asociativo"),
    ],

    # ---- 5c) DÓNDE ATACAR: los dos costados -------------------------------
    "atacar_kicker": "DÓNDE ATACAR",
    "atacar_num": "2",
    "atacar_lab": "costados para buscarlo el sabado",
    "atacar_ctx": (
        "Por la izquierda, Ojeda le gana el mano a mano a su marcador. Por "
        "la derecha, el lateral rival defiende solo, sin ayuda de un "
        "volante hay que forzarlo a construir bajo presión."),

    # ---- 5b) OJO: la pelota parada viene mejorando -------------------------
    "d2b_kicker": "OJO",
    "d2b_num": "-52%",
    "d2b_lab": "cayó el xG que recibe Bolívar de pelota parada",
    "d2b_ctx": (
        "De 0.29 a 0.14 por partido en sus últimos 10 juegos, a la mitad "
        "los remates: la vulnerabilidad de la temporada se atenuó justo ahora. Hicieron ajustes."),

    # ---- 6) EL ÚLTIMO CRUCE (el único antecedente) -------------------------
    # Ojo: acá se carga tal como se jugó, quién fue local ESA vez.
    "ida_local": "Chaco For Ever",
    "ida_gl": 0,
    "ida_visitante": "Ciudad de Bolívar",
    "ida_gv": 1,
    "ida_fecha_txt": "El antecedente · el único cruce · Fecha 13",
    "ida_detalle": (
        "0-1 en nuestra cancha, el 10 de mayo. También perdimos el duelo de "
        "xG (0.49 a 1.40): a diferencia de otras derrotas del año, esta la "
        "avala también el modelo."),
    # Ficha del cruce, en orden Chaco - Ciudad de Bolívar
    "ida_stats": [
        ("Posesión", "60% – 40%"),
        ("xG (goles esperados)", "0.49 – 1.40"),
        ("Remates", "12 – 13"),
        ("Remates al arco", "0 – 8"),
        ("Córners", "9 – 7"),
        ("Resultado", "0 – 1"),
    ],
    # El dato del cruce: dominamos y no alcanzó
    "ida_dato_num": "0",
    "ida_dato_lab": "los remates al arco que tuvo Chaco, pese a generar 12",
    "ida_dato_ctx": (
        "Dominamos posesión (60%) y córners (9-7), pero ningún remate "
        "entró. Bolívar ganó con solo 8 al arco de 13."),

    # ---- 7) CÓMO SE MUEVE EL MARCADOR (Markov del rival) -----------------
    "vuelve_kicker": "CÓMO SE MUEVE EL MARCADOR",
    "vuelve_num": "52%",
    "vuelve_lab": "de las veces, el primer gol tras el 0-0 es en contra de Bolívar",
    "vuelve_ctx": (
        "Le cuesta imponerse desde el empate. Si se pone 1-0, se lo "
        "empatan el 62% de las veces: no cierra los partidos."),

    # ---- 8) NUESTRA RACHA --------------------------------
    "arquero_kicker": "NUESTRA RACHA",
    "arquero_num": "6",
    "arquero_lab": "los partidos seguidos de Chaco sin recibir goles",
    "arquero_ctx": (
        "La mejor racha del año. Con Cravero recibimos 0.33 goles por "
        "partido y venimos de 3 victorias y 2 empates."),

    # ---- 9) CÓMO LLEGA EL NEGRO ---------------------------------------------
    "llega_hero": "10°",
    "llega_hero_sub": "con 36 puntos, a 5 del descenso y a 3 de Bolívar",
    "llega_col_izq": ("Últimos 5", "3V-2E", "5 a favor, 0 en contra"),
    "llega_col_der": ("Diferencia de xG del cruce", "+0.50", "la más amplia del año"),
    "llega_kicker": "CÓMO LLEGA",
    "llega_franja": "Con Cravero: 0.33 goles recibidos por partido",

    # ---- Cierre -------------------------------------------------------------
    "cierre_frase": (
        "Visitamos a un equipo que genera poco y concede mucho. "
        "Atacar por afuera, los dos costados. "
        "Ganar el mediocampo. Es la única linea donde el rival nos supera. Cuidar la salida y no quedar en inferioridad ahí."),
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
        nota=NOTA, destacar="Puntos por partido de local"))

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
        "El único cruce, dato por dato",
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
