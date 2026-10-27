# -*- coding: utf-8 -*-
"""
PREVIA · Fecha 35 · Ferro Carril Oeste (LOCAL) vs Chaco For Ever (visitante)
sábado 24/10/2026, 16:00 hora Argentina.

    python ig.py pre_partido f35_ferro

Antecedente usado: Chaco 1-2 Ferro (07/06/2026, fecha 17, en Resistencia).
Informe base:
  outputs/temporadas/2026/pre_partido/ferro_carril_oeste_a/Informe_pre_partido_ferro_carril_oeste.tex
Contexto: Ferro 1° con 65 pts (19V-8E-7D, 38 GF - 28 GC), xG 1.36/0.81 por partido pero 38 goles
con 46.3 xG. De local 10V-2E-5D (1.88 pts/pj). Chaco 10° con 40 pts, ya salvado y sin Reducido;
de visitante 0.82 pts/pj (3V-5E-9D).
Notas de armado:
  - Sin placas de amarillas ni de suspensiones (convención de la cuenta): las bajas de Luque
    (roja) y Carrizo (5ª amarilla) quedan solo en el informe.
  - Escudo de Ferro: assets/escudos/ferro_carril_oeste.png (img.sofascore.com/api/v1/team/36841/image).
"""
from plantillas.base import ESCUDOS

ORDEN = [
    "portada",
    "cita:cierre",          # MI LECTURA
    "ficha:ficha_rival",    # el rival en su cancha
    "dato_vs:nasta",        # su amenaza
    "ficha:cuidarnos",      # dónde cuidarnos
    "dato:atacar",          # dónde atacar
    "resultado:ida",        # el último cruce
    "dato_vs:llega",        # cómo llega el Negro
]

DATOS = {
    "fecha": 35,
    "rival": "Ferro",
    "rival_corto": "Ferro",
    "condicion": "visitante",
    "portada_bajada": (
        "Visitamos al puntero de la zona. Si nos gana, queda primero "
        "por aritmética. Deslizá →"),
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "ferro_carril_oeste.png",

    # ---- Ficha del rival: en su cancha ------------------------------------------
    "ficha_rival_titulo": "Ferro, en su cancha",
    "ficha_rival_sub": "El puntero, fuerte en Caballito y con la mejor defensa de local",
    "ficha_rival_destacar": "Puntos por partido de local",
    "ficha_rival_stats": [
        ("Récord de local", "10V - 2E - 5D"),
        ("Puntos por partido de local", "1.88"),
        ("xG de local (a favor - en contra)", "1.61 - 0.60"),
        ("Partidos sin recibir gol", "16 de 34"),
        ("Goles con 46.3 de xG", "38"),
        ("Últimos 10", "5V - 4E - 1D"),
    ],

    # ---- Su amenaza: Hoyos y Parisi ------------------------------------------
    "nasta_hero": "3°",
    "nasta_hero_sub": "E. Hoyos, entre 111 volantes de la categoría: el motor de Ferro",
    "nasta_col_izq": ("Hoyos", "3G 5A", "El volante que arma todo"),
    "nasta_col_der": ("Parisi", "9 goles", "El goleador, por izquierda"),
    "nasta_kicker": "SU AMENAZA",
    "nasta_franja": "Arma por el medio y llega por las bandas",

    # ---- Dónde cuidarnos ---------------------------------------------------------
    "cuidarnos_titulo": "Dónde cuidarnos",
    "cuidarnos_sub": "Tres cosas que Ferro hace bien",
    "cuidarnos_destacar": "El medio de Ferro",
    "cuidarnos_stats": [
        ("Hoyos entre 111 volantes de la categoría", "3°"),
        ("Parisi por su izquierda", "nuestra derecha"),
        ("Goles en el segundo tiempo", "25 de sus 38"),
        ("Penales convertidos", "4 de 5"),
    ],

    # ---- Dónde atacar -----------------------------------------------------
    "atacar_kicker": "DÓNDE ATACAR",
    "atacar_num": "146°",
    "atacar_lab": "de 151 centrales en duelo aéreo: Orellana, de Ferro; Tévez, 121°",
    "atacar_ctx": (
        "Pacheco es el 1° de 144 delanteros en duelos aéreos ganados y Romero el 3° "
        "en duelo aéreo. Centros y segundas pelotas, con Ojeda por izquierda."),

    # ---- El último cruce ----------------------------------------------------
    "ida_local": "Chaco For Ever",
    "ida_gl": 1,
    "ida_visitante": "Ferro",
    "ida_gv": 2,
    "ida_torneo": "El último cruce · Fecha 17",
    "ida_detalle": (
        "1-2 en Resistencia, el 7 de junio. Hoyos a los 59' y Canto a los 79', "
        "los dos de cabeza con xG de 0.03 y 0.05. Empató Enriquez a los 62'."),
    "ida_ficha_titulo": "El último cruce",
    "ida_ficha_sub": "Chaco 1-2 Ferro · fecha 17",
    "ida_ficha_destacar": "Remates al arco",
    "ida_ficha_stats": [
        ("Posesión", "47% – 53%"),
        ("xG (goles esperados)", "0.44 – 0.90"),
        ("Remates", "5 – 12"),
        ("Remates al arco", "1 – 8"),
        ("Córners", "5 – 6"),
        ("Resultado", "1 – 2"),
    ],
    "ida_dato_kicker": "EL HISTORIAL",
    "ida_dato_num": "1",
    "ida_dato_lab": "antecedente en la base: la derrota de junio",
    "ida_dato_ctx": "Chaco 1-2 Ferro en Resistencia, por la fecha 17.",

    # ---- Cómo llega el Negro --------------------------------------------
    "llega_hero": "10°",
    "llega_hero_sub": "con 40 puntos · salvados desde la fecha 34",
    "llega_col_izq": ("De visitante", "0.82", "por partido, 3V-5E-9D"),
    "llega_col_der": ("Ferro", "65 pts", "el puntero, 19V-8E-7D"),
    "llega_kicker": "CÓMO LLEGA",
    "llega_franja": "Ya salvados: vamos a competir, sin nada que perder",

    # ---- Cierre ---------------------------------------------------------------
    "cierre_autor": "La previa",
    "cierre_frase": (
        "Ferro llega a cerrar el primer puesto y juega fuerte en su cancha. "
        "Nos conviene llegar rápido, ganar por arriba y no perder temprano: "
        "cuando se pone 1-0, lo alcanzan el 60% de las veces."),
}
