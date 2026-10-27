# -*- coding: utf-8 -*-
"""
PREVIA · Fecha 34 · Chaco For Ever (LOCAL) vs Central Norte de Salta (visitante)
domingo 18/10/2026, 17:00 hora Argentina.

    python ig.py pre_partido f34_central_norte

Antecedente usado: Central Norte 1-1 Chaco For Ever (31/05/2026, fecha 16, en Salta).
Informe base:
  outputs/temporadas/2026/pre_partido/central_norte_h/Informe_pre_partido_central_norte.tex
Contexto: Central Norte 15° con 34 pts (6V-16E-11D, 21 GF - 30 GC), 17% de descenso. xG 0.89/0.91
por partido, pero 21 goles con 29.27 xG (-8.3). De visitante 0.75 pts/pj (2V-6E-8D, 9-19).
8 empates en los últimos 10. Recibió 12 de sus 30 goles de pelota parada. Vedoya (percentil 88)
es su mejor jugador; Lamosa (central, percentil 1) el punto débil. Chaco 10° con 40 pts, de
local 1.62 pts/pj; con Cravero en casa 5V-1E-0D. Ganar = salvación matemática.
Notas de armado:
  - Sin placas de amarillas ni de suspensiones (convención de la cuenta). La posible
    suspensión de Calderón (5ª amarilla desde la fecha 19) queda solo en el informe.
  - "arquero" = nuestra marca de local con Cravero.
"""
from plantillas.base import ESCUDOS

# Carrusel corto: 8 placas. Lo demás va en las historias de la previa
# (publicaciones/historias/f34_central_norte_previa.py).
ORDEN = [
    "portada",
    "cita:cierre",          # MI LECTURA: va 2ª para que se vea sin deslizar
    "ficha:ficha_rival",    # el rival en una mirada (de visitante)
    "dato_vs:nasta",        # su amenaza
    "ficha:cuidarnos",      # dónde cuidarnos
    "dato:atacar",          # dónde atacar
    "resultado:ida",        # el último cruce
    "dato_vs:llega",        # cómo llega el Negro (y la cuenta de la salvación)
    # Opcionales (descomentar): "dato:d1", "dato:d2", "dato:d3", "dato:arquero", "dato:vuelve",
    # "ficha:ida_ficha", "dato:ida_dato",
]

DATOS = {
    # ---- Cabecera / próxima fecha -------------------------------------------
    "fecha": 34,
    "rival": "Central Norte",
    "rival_corto": "Central Norte",
    "condicion": "local",
    "portada_bajada": (
        "Recibimos al 15° de la tabla, que pelea por no descender. Si ganamos, "
        "nos salvamos matemáticamente. Deslizá →"),
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "central_norte_de_salta.png",

    # ---- Ficha del rival: de visitante -------------------------------------
    "ficha_rival_titulo": "Central Norte, de visitante",
    "ficha_rival_sub": "Un equipo de empates que afuera pierde la mitad de sus partidos",
    "ficha_rival_destacar": "Puntos por partido de visitante",
    "ficha_rival_stats": [
        ("Récord de visitante", "2V - 6E - 8D"),
        ("Puntos por partido de visitante", "0.75"),
        ("Goles de visitante (a favor - en contra)", "9 - 19"),
        ("Empates en la temporada", "16 de 33"),
        ("Goles con 29.3 de xG", "21"),
        ("Últimos 10", "1V - 8E - 1D"),
    ],

    # ---- (opcional) El rasgo: define por debajo de lo que genera ----------
    "d1_kicker": "EL RIVAL",
    "d1_num": "-8",
    "d1_lab": "goles por debajo de lo que esperaba el modelo",
    "d1_ctx": (
        "Central Norte hizo 21 goles con 29.3 de xG. Genera casi lo mismo que "
        "concede, pero le cuesta mucho convertir."),

    # ---- Su amenaza: Vedoya y Borda ----------------------------------------
    "nasta_hero": "88",
    "nasta_hero_sub": "El nivel de F. Vedoya en la categoría: el mejor de Central Norte",
    "nasta_col_izq": ("Vedoya", "2G 2A", "Por la izquierda"),
    "nasta_col_der": ("Borda", "4 goles", "El 9, fuerte por arriba"),
    "nasta_kicker": "SU AMENAZA",
    "nasta_franja": "El peligro viene por su izquierda y por arriba",

    # ---- Dónde cuidarnos ------------------------------------------------------
    "cuidarnos_titulo": "Dónde cuidarnos",
    "cuidarnos_sub": "Tres cosas que Central Norte hace bien",
    "cuidarnos_destacar": "Vedoya por su izquierda",
    "cuidarnos_stats": [
        ("Vedoya por su izquierda", "nuestra derecha"),
        ("Borda de cabeza", "14 remates"),
        ("Primeros 15 minutos", "6 de sus 21 goles"),
        ("Si se pone arriba", "se cierra atrás"),
    ],

    # ---- Dónde atacar ---------------------------------------------------
    "atacar_kicker": "DÓNDE ATACAR",
    "atacar_num": "12",
    "atacar_lab": "de los 30 goles que recibió fueron de pelota parada",
    "atacar_ctx": (
        "Laterales, córners y centros. Pacheco y Romero ganan casi todo por arriba, "
        "y Ojeda puede cargar por izquierda, el costado que menos recupera."),

    # ---- El último cruce ----------------------------------------------------
    "ida_local": "Central Norte",
    "ida_gl": 1,
    "ida_visitante": "Chaco For Ever",
    "ida_gv": 1,
    "ida_torneo": "El último cruce · Fecha 16",
    "ida_detalle": (
        "1-1 en Salta, el 31 de mayo. Gol de Alvez a los 12', roja a Mancuso a los 19' "
        "y empate de Gaggi a los 70'. Tuvimos 70% de la pelota."),
    "ida_ficha_titulo": "El último cruce",
    "ida_ficha_sub": "Central Norte 1-1 Chaco · fecha 16",
    "ida_ficha_destacar": "Posesión",
    "ida_ficha_stats": [
        ("Posesión", "70% – 30%"),
        ("xG (goles esperados)", "0.41 – 0.08"),
        ("Remates", "10 – 3"),
        ("Remates al arco", "3 – 1"),
        ("Córners", "4 – 0"),
        ("Resultado", "1 – 1"),
    ],
    "ida_dato_kicker": "EL HISTORIAL",
    "ida_dato_num": "0",
    "ida_dato_lab": "derrotas del Negro contra Central Norte",
    "ida_dato_ctx": "Tres partidos: 1-0 y 1-0 en 2025, y el 1-1 de mayo en Salta.",

    # ---- (opcional) Cómo se mueve el marcador -----------------------------
    "vuelve_kicker": "CÓMO SE MUEVE EL MARCADOR",
    "vuelve_num": "10 de 10",
    "vuelve_lab": "veces que, ganando 1-0, el gol siguiente fue del rival",
    "vuelve_ctx": (
        "Cuando Central Norte se pone arriba y hay otro gol, siempre se lo empatan. "
        "Pero 4 de sus 6 victorias fueron 1-0."),

    # ---- (opcional) Nuestra marca de local -----------------------------------
    "arquero_kicker": "DE LOCAL",
    "arquero_num": "5V 1E",
    "arquero_lab": "el Negro en casa desde que llegó Cravero",
    "arquero_ctx": "Seis partidos sin perder, 10 goles a favor y 2 en contra.",

    # ---- Cómo llega el Negro --------------------------------------------
    "llega_hero": "10°",
    "llega_hero_sub": "con 40 puntos · de local, 1.62 por partido",
    "llega_col_izq": ("Con Cravero en casa", "5V 1E", "10 goles a favor, 2 en contra"),
    "llega_col_der": ("Si ganamos", "Salvados", "pase lo que pase en el resto"),
    "llega_kicker": "CÓMO LLEGA",
    "llega_franja": "El empate también sirve si San Miguel no gana",

    # ---- Cierre ---------------------------------------------------------------
    "cierre_autor": "La previa",
    "cierre_frase": (
        "Central Norte llega a esperar, pero si el domingo se le complica la tabla "
        "o se pone abajo, va a salir a buscarlo. Paciencia, centros al área y "
        "golpear primero. Ganar es la salvación."),
}
