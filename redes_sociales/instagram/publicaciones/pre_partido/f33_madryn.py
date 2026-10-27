# -*- coding: utf-8 -*-
"""
PREVIA · Fecha 33 · Deportivo Madryn (LOCAL) vs Chaco For Ever (visitante)
domingo 11/10/2026, 15:00 hora Argentina.

    python ig.py pre_partido f33_madryn

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
Notas de armado:
  - Sin placas de amarillas ni de suspensiones (convención de la cuenta).
  - Slots: d2 = pelota parada (dónde cuidarnos), d2b = final del partido, d3 = el medio;
    "arquero" = nuestra marca de visitante.
"""
from plantillas.base import ESCUDOS

# Carrusel corto: 8 placas. Lo que salió de acá vive en las historias de la previa
# (publicaciones/historias/f33_madryn_previa.py) o queda como opcional abajo.
ORDEN = [
    "portada",
    "cita:cierre",          # MI LECTURA: va 2ª para que se vea sin deslizar
    "ficha:ficha_rival",    # el rival en una mirada (incluye lo que era d1: el +18 con xG parejo)
    "dato_vs:nasta",        # su amenaza
    "ficha:cuidarnos",      # dónde cuidarnos: pelota parada + final + medio (eran d2, d2b y d3)
    "dato:atacar",          # dónde atacar
    "resultado:ida",        # el último cruce (el detalle completo va en historias)
    "dato_vs:llega",        # cómo llega el Negro (incluye nuestra marca de visitante)
    # Opcionales, fuera del carrusel corto (descomentar):
    # "dato:d1", "dato:d2", "dato:d2b", "dato:d3",       # versión de una placa por idea
    # "jugadores:clave", "ficha:ida_ficha", "dato:ida_dato", "dato:vuelve", "dato:arquero",
]

DATOS = {
    # ---- Cabecera / próxima fecha -------------------------------------------
    "fecha": 33,
    "rival": "Deportivo Madryn",
    "rival_corto": "Madryn",                   # solo para el título de tapa
    "condicion": "visitante",                  # 'local' o 'visitante' (el Negro)
    "portada_bajada": (
        "Visitamos al 4° de la tabla, que suma 2.00 puntos por partido de local. "
        "Genera lo mismo que nosotros, pero convierte más. Deslizá →"),
    # Escudos: salen de assets/escudos/<archivo>. Si falta el png, la placa no lo dibuja.
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "deportivo_madryn.png",

    # ---- Ficha del rival: título/bajada según la condición -------------------
    "ficha_rival_titulo": "Madryn, de local",
    "ficha_rival_sub": "Nos toca su mejor versión: gana lo mismo que genera, pero convierte más",
    "ficha_rival_destacar": "Puntos por partido de local",
    "ficha_rival_stats": [
        ("Récord de local", "9V - 5E - 2D"),
        ("Puntos por partido de local", "2.00"),
        ("Goles de local (a favor - en contra)", "27 - 11"),
        ("De visitante baja a", "1.31 pts/pj"),
        ("Diferencia de gol, con xG igual al nuestro", "+18"),
        ("Últimos 5", "3V - 1E - 1D"),
    ],

    # ---- 1) EL RASGO DEL RIVAL: gana con el mismo xG que nosotros ----------
    "d1_kicker": "EL RIVAL",
    "d1_num": "+18",
    "d1_lab": "la diferencia de gol de Madryn, con un xG parejo al nuestro",
    "d1_ctx": (
        "Genera 1.12 de xG por partido y concede 1.12, casi como el Negro (1.01 y "
        "0.98). Lo suyo es la eficacia: marca más y recibe menos de lo que genera."),

    # ---- 2) SU AMENAZA: Silba y Solís --------------------------------------
    "nasta_hero": "13",
    "nasta_hero_sub": "Los goles de L. Silba, el 28% de los de todo Madryn",
    "nasta_col_izq": ("Goles de Silba", "13", "Define como pocos"),
    "nasta_col_der": ("Asistencias de Solís", "4", "El que reparte el juego"),
    "nasta_kicker": "SU AMENAZA",
    "nasta_franja": "El gol y la creación pasan por dos nombres",

    # ---- 3) DÓNDE CUIDARNOS: pelota parada + final del partido + el medio (fusión) -------
    "cuidarnos_titulo": "Dónde cuidarnos",
    "cuidarnos_sub": "Tres frentes donde Madryn lastima",
    "cuidarnos_destacar": "Pelota parada",
    "cuidarnos_stats": [
        ("Pelota parada", "18 de 40 goles (45%)"),
        ("De cabeza", "9 goles"),
        ("Desde el minuto 75", "35% de sus goles"),
        ("Nivel del mediocampo", "53 contra 13 nuestro"),
    ],

    # ---- (opcional) versión de una placa por idea ----------------------------------------
    # ---- 3a) DÓNDE CUIDARNOS: la pelota parada ------------------------------
    "d2_kicker": "DÓNDE CUIDARNOS",
    "d2_num": "18",
    "d2_lab": "de sus 40 goles salieron de pelota parada",
    "d2_ctx": (
        "Córner, lateral, pelota parada y tiro libre: el 45% de sus goles. Sumó "
        "además 9 de cabeza. Hay que marcar bien y evitar faltas cerca del área."),

    # ---- 4) OJO: el final del partido --------------------------------------
    "d2b_kicker": "OJO",
    "d2b_num": "35%",
    "d2b_lab": "de los goles de Madryn llegan desde el minuto 75",
    "d2b_ctx": (
        "16 de sus 46. Cierra los partidos con fuerza: hay que sostener la línea "
        "y planificar los cambios hasta el último minuto."),

    # ---- 5) EL MEDIO ---------------------------------------------------------
    "d3_kicker": "EL MEDIO",
    "d3_num": "53",
    "d3_lab": "el nivel de su mediocampo contra 13 del nuestro",
    "d3_ctx": (
        "Percentil promedio en la categoría, con Recalde en el 96. Es la línea "
        "donde nos supera con claridad: cuidar la salida."),

    # ---- 6) JUGADOR POR JUGADOR: cómo es cada uno (sin percentiles) -------
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

    # ---- 7) DÓNDE ATACAR ---------------------------------------------------
    "atacar_kicker": "DÓNDE ATACAR",
    "atacar_num": "2",
    "atacar_lab": "caminos concretos para lastimarlo el domingo",
    "atacar_ctx": (
        "Por arriba, con Pacheco y Romero ante un Corvalán que casi no gana en el "
        "aire. Y por nuestra izquierda: Ojeda contra el costado más flojo de Madryn."),

    # ---- 8) EL ÚLTIMO CRUCE ------------------------------------------------
    # Ojo: acá se carga tal como se jugó, quién fue local ESA vez.
    "ida_local": "Chaco For Ever",
    "ida_gl": 1,
    "ida_visitante": "Deportivo Madryn",
    "ida_gv": 2,
    "ida_torneo": "El último cruce · Fecha 15",
    "ida_detalle": (
        "1-2 en nuestra cancha, el 24 de mayo. Dominamos con 63% de posesión y 13 "
        "remates contra 5, y perdimos."),
    # Ficha del cruce, en orden Chaco - Madryn
    "ida_ficha_titulo": "El último cruce",
    "ida_ficha_sub": "Chaco For Ever vs {rival} · el antecedente",
    "ida_ficha_destacar": "xG (goles esperados)",
    "ida_ficha_stats": [
        ("Posesión", "63% – 37%"),
        ("xG (goles esperados)", "0.80 – 0.36"),
        ("Remates", "13 – 5"),
        ("Remates al arco", "3 – 1"),
        ("Córners", "4 – 0"),
        ("Resultado", "1 – 2"),
    ],
    # El dato del cruce
    "ida_dato_kicker": "EL DATO DEL CRUCE",
    "ida_dato_num": "63%",
    "ida_dato_lab": "la posesión del Negro en el 1-2 de mayo",
    "ida_dato_ctx": (
        "13 remates contra 5 y 4 córners contra 0. Madryn ganó con un gol en "
        "contra y una definición de Silba. Es una cuenta pendiente."),

    # ---- 9) CÓMO SE MUEVE EL MARCADOR (Markov del rival) -----------------
    "vuelve_kicker": "CÓMO SE MUEVE EL MARCADOR",
    "vuelve_num": "57%",
    "vuelve_lab": "de las veces, Madryn hace el primer gol tras el 0-0",
    "vuelve_ctx": (
        "Y si se pone 1-0, estira la ventaja el 65%. Conviene no recibir primero "
        "y sostener el partido parejo."),

    # ---- 10) NUESTRA MARCA DE VISITANTE ---------------------------------------
    "arquero_kicker": "DE VISITANTE",
    "arquero_num": "5",
    "arquero_lab": "los empates del Negro de visitante en 16 salidas",
    "arquero_ctx": (
        "Afuera sumamos 2 victorias (3-1 a San Telmo y 1-0 a Colón), 5 empates y "
        "9 derrotas. Un empate en Madryn nos deja en 38 puntos."),

    # ---- 11) CÓMO LLEGA EL NEGRO --------------------------------------------
    "llega_hero": "10°",
    "llega_hero_sub": "con 37 puntos · de visitante, 2V-5E-9D (0.69 por partido)",
    "llega_col_izq": ("Últimos 5", "WDWLD", "5 a favor, 4 en contra"),
    "llega_col_der": ("Prob. de descenso", "0,17%", "en la fecha 19 era 30%"),
    "llega_kicker": "CÓMO LLEGA",
    "llega_franja": "Un punto en Madryn nos deja en 38",

    # ---- Cierre -------------------------------------------------------------
    "cierre_autor": "La previa",
    "cierre_frase": (
        "Madryn es 4° y fuerte en su cancha, pero su xG es igual al nuestro. "
        "Cuidar el medio y la pelota parada, buscar el juego aéreo y sostener el final."),
}
