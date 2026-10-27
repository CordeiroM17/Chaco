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

    python scripts/carrusel_previa_deportivo_madryn.py

------------------------------------------------------------------------------
PARTIDO ARMADO ACÁ: Deportivo Madryn (LOCAL) vs Chaco For Ever (visitante) · fecha 33 ·
domingo 11/10/2026, 15:00 hora Argentina.
Antecedente usado: Chaco For Ever 1-2 Deportivo Madryn (24/05/2026, fecha 15).
Informe base:
  outputs/temporadas/2026/pre_partido/deportivo_madryn_a/Informe_pre_partido_deportivo_madryn.tex
Contexto: Madryn 4° con 53 pts (14V-11E-7D, 46 GF - 28 GC, +18), salvado. xG parejo con
Chaco (1.12/1.12 contra 1.01/0.98) pero 40 goles con 32.55 xG y 26 en contra con 32.37.
De local 2.00 pts/pj (9V-5E-2D, 27-11); de visitante 1.31. Silba 13 goles (28%), Solís 4
asistencias. 18 de 40 goles de pelota parada (45%), 9 de cabeza; 35% de sus goles desde el
75'. Mediocampo 53 contra 13 nuestro (Recalde 96); Corvalán, su mejor central, flojo por
arriba. Markov: golpea primero el 57%; si se pone 1-0, estira el 65%.
Chaco: 10° con 37 pts, visitante 2V-5E-9D (0.69 pts/pj).
Notas de armado de esta fecha:
  - Escudo de Madryn ya estaba en assets/escudos/deportivo_madryn.png.
  - Sin placas de amarillas ni de suspensiones (convención de la cuenta).
  - Slots reasignados: d2 = pelota parada (dónde cuidarnos), d2b = final del partido,
    d3 = el medio; "arquero" = nuestra marca de visitante.
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
    "fecha": 33,
    "rival": "Deportivo Madryn",
    "condicion": "visitante",                  # 'local' o 'visitante' (el Negro)
    "rival_corto": "Madryn",   # solo para el título de tapa
    "portada_bajada": (
        "Visitamos al 4° de la tabla, que suma 2.00 puntos por partido de local. "
        "Genera lo mismo que nosotros, pero convierte más. Deslizá →"),
    # Escudos: salen de assets/escudos/<archivo>. Si falta el png, la placa no lo dibuja.
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "deportivo_madryn.png",

    # ---- Ficha del rival (slide 03): título/bajada según la condición --------
    "ficha_rival_titulo": "Madryn, de local",
    "ficha_rival_sub": "Nos toca su mejor versión",
    "ficha_rival_destacar": "Puntos por partido de local",

    # ---- 1) EL RASGO DEL RIVAL: gana con el mismo xG que nosotros ----------
    "d1_kicker": "EL RIVAL",
    "d1_num": "+18",
    "d1_lab": "la diferencia de gol de Madryn, con un xG parejo al nuestro",
    "d1_ctx": (
        "Genera 1.12 de xG por partido y concede 1.12, casi como el Negro (1.01 y "
        "0.98). Lo suyo es la eficacia: marca más y recibe menos de lo que genera."),

    # ---- 2) MADRYN DE LOCAL (que es lo que nos toca) -----------------------
    "visit_stats": [
        ("Récord de local", "9V - 5E - 2D"),
        ("Puntos por partido de local", "2.00"),
        ("Goles de local (a favor - en contra)", "27 - 11"),
        ("De visitante baja a", "1.31 pts/pj"),
        ("Dibujo más usado", "4-4-2"),
        ("Últimos 5", "3V - 1E - 1D"),
    ],

    # ---- 3) SU AMENAZA: Silba y Solís --------------------------------------
    "nasta_hero": "13",
    "nasta_hero_sub": "Los goles de L. Silba, el 28% de los de todo Madryn",
    "nasta_col_izq": ("Goles de Silba", "13", "Define como pocos"),
    "nasta_col_der": ("Asistencias de Solís", "4", "El que reparte el juego"),
    "nasta_kicker": "SU AMENAZA",
    "nasta_franja": "El gol y la creación pasan por dos nombres",

    # ---- 4) DÓNDE CUIDARNOS: la pelota parada ------------------------------
    "d2_kicker": "DÓNDE CUIDARNOS",
    "d2_num": "18",
    "d2_lab": "de sus 40 goles salieron de pelota parada",
    "d2_ctx": (
        "Córner, lateral, pelota parada y tiro libre: el 45% de sus goles. Sumó "
        "además 9 de cabeza. Hay que marcar bien y evitar faltas cerca del área."),

    # ---- 5) OJO: el final del partido --------------------------------------
    "d2b_kicker": "OJO",
    "d2b_num": "35%",
    "d2b_lab": "de los goles de Madryn llegan desde el minuto 75",
    "d2b_ctx": (
        "16 de sus 46. Cierra los partidos con fuerza: hay que sostener la línea "
        "y planificar los cambios hasta el último minuto."),

    # ---- 6) EL MEDIO ---------------------------------------------------------
    "d3_kicker": "EL MEDIO",
    "d3_num": "53",
    "d3_lab": "el nivel de su mediocampo contra 13 del nuestro",
    "d3_ctx": (
        "Percentil promedio en la categoría, con Recalde en el 96. Es la línea "
        "donde nos supera con claridad: cuidar la salida."),

    # ---- 6b) JUGADOR POR JUGADOR: cómo es cada uno (sin percentiles) -------
    "clave_kicker": "ASÍ LLEGA EL RIVAL",
    "clave_titulo": "Jugador por jugador",
    "clave_sub": "Lo bueno y lo flojo de tres piezas clave, sin vueltas",
    "clave_jugadores": [
        ("L. Silba", "Delantero (el goleador)",
         "Convierte casi todo lo que patea - 13 goles",
         "Toca poco la pelota - Pierde los duelos aéreos"),
        ("F. Recalde", "Volante defensivo (el eje)",
         "Ordena con el pase - Gana los duelos por abajo",
         "Casi no pisa el área rival - Sin goles en el año"),
        ("C. Corvalán", "Central",
         "Gana casi todos los duelos por abajo - Intercepta",
         "Casi no gana por arriba"),
    ],

    # ---- 6c) DÓNDE ATACAR ---------------------------------------------------
    "atacar_kicker": "DÓNDE ATACAR",
    "atacar_num": "2",
    "atacar_lab": "caminos concretos para lastimarlo el domingo",
    "atacar_ctx": (
        "Por arriba, con Pacheco y Romero ante un Corvalán que casi no gana en el "
        "aire. Y por nuestra izquierda: Ojeda contra el costado más flojo de Madryn."),

    # ---- 7) EL ÚLTIMO CRUCE ------------------------------------------------
    # Ojo: acá se carga tal como se jugó, quién fue local ESA vez.
    "ida_local": "Chaco For Ever",
    "ida_gl": 1,
    "ida_visitante": "Deportivo Madryn",
    "ida_gv": 2,
    "ida_fecha_txt": "El último cruce · Fecha 15",
    "ida_detalle": (
        "1-2 en nuestra cancha, el 24 de mayo. Dominamos con 63% de posesión y 13 "
        "remates contra 5, y perdimos."),
    # Ficha del cruce, en orden Chaco - Madryn
    "ida_stats": [
        ("Posesión", "63% – 37%"),
        ("xG (goles esperados)", "0.80 – 0.36"),
        ("Remates", "13 – 5"),
        ("Remates al arco", "3 – 1"),
        ("Córners", "4 – 0"),
        ("Resultado", "1 – 2"),
    ],
    "ida_ficha_titulo": "El último cruce",
    # El dato del cruce
    "ida_dato_num": "63%",
    "ida_dato_lab": "la posesión del Negro en el 1-2 de mayo",
    "ida_dato_ctx": (
        "13 remates contra 5 y 4 córners contra 0. Madryn ganó con un gol en "
        "contra y una definición de Silba. Es una cuenta pendiente."),

    # ---- 8) CÓMO SE MUEVE EL MARCADOR (Markov del rival) -----------------
    "vuelve_kicker": "CÓMO SE MUEVE EL MARCADOR",
    "vuelve_num": "57%",
    "vuelve_lab": "de las veces, Madryn hace el primer gol tras el 0-0",
    "vuelve_ctx": (
        "Y si se pone 1-0, estira la ventaja el 65%. Conviene no recibir primero "
        "y sostener el partido parejo."),

    # ---- 9) DE VISITANTE ----------------------------------------------------
    "arquero_kicker": "DE VISITANTE",
    "arquero_num": "5",
    "arquero_lab": "los empates del Negro de visitante en 16 salidas",
    "arquero_ctx": (
        "Afuera sumamos 2 victorias (3-1 a San Telmo y 1-0 a Colón), 5 empates y "
        "9 derrotas. Un empate en Madryn nos deja en 38 puntos."),

    # ---- 10) CÓMO LLEGA EL NEGRO --------------------------------------------
    "llega_hero": "10°",
    "llega_hero_sub": "con 37 puntos, a 6 de la zona de descenso",
    "llega_col_izq": ("Últimos 5", "WDWLD", "5 a favor, 4 en contra"),
    "llega_col_der": ("Prob. de descenso", "0,17%", "en la fecha 19 era 30%"),
    "llega_kicker": "CÓMO LLEGA",
    "llega_franja": "Un punto en Madryn nos deja en 38",

    # ---- Cierre -------------------------------------------------------------
    "cierre_frase": (
        "Madryn es 4° y fuerte en su cancha, pero su xG es igual al nuestro. "
        "Cuidar el medio y la pelota parada, buscar el juego aéreo y sostener el final."),
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
