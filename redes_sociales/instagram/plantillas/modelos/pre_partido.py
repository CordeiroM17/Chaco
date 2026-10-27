# -*- coding: utf-8 -*-
"""
PREVIA · Fecha NN · RIVAL (local|visitante)

    python ig.py pre_partido <nombre-de-este-archivo>

Copiá/ajustá los valores. Las placas que no quieras: sacalas del ORDEN. Las que quieras
sumar: escribí sus claves en DATOS y agregalas al ORDEN (ver plantillas/base.py para los
tipos: dato, dato_vs, ficha, ranking, grafico, resultado, jugadores, cita).
Cualquier texto acepta {fecha}, {rival} y {rival_corto}.
"""
from plantillas.base import ESCUDOS

ORDEN = [
    "portada",
    "cita:cierre",   # MI LECTURA: va 2ª para que se vea sin deslizar
    "dato:d1",              # el rasgo que define al rival
    "ficha:ficha_rival",    # el rival en la condición que nos toca
    "dato_vs:nasta",        # su amenaza
    "dato:d2",              # dónde lastimarlo / cuidarnos
    "dato:d3",              # cómo ataca
    "resultado:ida",        # el último cruce
    "ficha:ida_ficha",
    "dato:ida_dato",
    "dato:vuelve",          # cómo se mueve el marcador
    "dato:arquero",         # nuestro dato de la semana (arquero, racha, visitante...)
    "dato_vs:llega",        # cómo llega el Negro
    # Más placas disponibles (descomentar y completar sus claves):
    # "jugadores:clave",    # jugador por jugador: clave_titulo/_sub/_kicker/_jugadores
    # "dato:atacar",        # dónde atacar
]

DATOS = {
    # ---- Cabecera -------------------------------------------------------------
    "fecha": 0,
    "rival": "Nombre Completo",
    "rival_corto": "Rival",                    # para el título de tapa ("Ahora,\n{rival_corto}")
    "condicion": "local",                      # 'local' o 'visitante' (el Negro)
    "portada_bajada": "Una o dos frases que enganchen. Deslizá →",
    "escudo_negro": ESCUDOS / "chaco_for_ever.png",
    "escudo_rival": ESCUDOS / "archivo_del_rival.png",   # bajar con herramientas/bajar_escudos.py

    # ---- El rival en la condición que nos toca ---------------------------------
    "ficha_rival_titulo": "Rival, de local",
    "ficha_rival_sub": "Una línea de contexto",
    "ficha_rival_destacar": "Puntos por partido de local",
    "ficha_rival_stats": [
        ("Récord de local", "0V - 0E - 0D"),
        ("Puntos por partido de local", "0.00"),
        ("Goles de local (a favor - en contra)", "0 - 0"),
        ("De visitante baja a", "0.00 pts/pj"),
        ("Dibujo más usado", "4-4-2"),
        ("Últimos 5", "0V - 0E - 0D"),
    ],

    # ---- Datos sueltos (número grande + frase + contexto) ----------------------
    "d1_kicker": "EL RIVAL", "d1_num": "00", "d1_lab": "qué mide el número", "d1_ctx": "Contexto en dos líneas.",
    "d2_kicker": "DÓNDE CUIDARNOS", "d2_num": "00", "d2_lab": "qué mide el número", "d2_ctx": "Contexto.",
    "d3_kicker": "CÓMO ATACA", "d3_num": "00", "d3_lab": "qué mide el número", "d3_ctx": "Contexto.",

    # ---- Su amenaza (número héroe + dos columnas) ---------------------------
    "nasta_kicker": "SU AMENAZA",
    "nasta_hero": "00",
    "nasta_hero_sub": "frase sobre el número",
    "nasta_col_izq": ("Etiqueta", "00", "aclaración"),
    "nasta_col_der": ("Etiqueta", "00", "aclaración"),
    "nasta_franja": "Frase de cierre de la placa",

    # ---- El último cruce (cargar tal como se jugó: quién fue local ESA vez) ----
    "ida_local": "Chaco For Ever", "ida_gl": 0,
    "ida_visitante": "Nombre Completo", "ida_gv": 0,
    "ida_torneo": "El último cruce · Fecha NN",
    "ida_detalle": "Fecha, lugar y cómo se dio.",
    "ida_ficha_titulo": "El último cruce",
    "ida_ficha_sub": "Chaco For Ever vs {rival} · el antecedente",
    "ida_ficha_destacar": "xG (goles esperados)",
    "ida_ficha_stats": [                       # en orden Chaco – rival
        ("Posesión", "00% – 00%"),
        ("xG (goles esperados)", "0.00 – 0.00"),
        ("Remates", "0 – 0"),
        ("Remates al arco", "0 – 0"),
        ("Córners", "0 – 0"),
        ("Resultado", "0 – 0"),
    ],
    "ida_dato_kicker": "EL DATO DEL CRUCE", "ida_dato_num": "00", "ida_dato_lab": "qué mide", "ida_dato_ctx": "Contexto.",

    # ---- Marcador y nuestro momento ----------------------------------------------
    "vuelve_kicker": "CÓMO SE MUEVE EL MARCADOR", "vuelve_num": "00%", "vuelve_lab": "qué mide", "vuelve_ctx": "Contexto.",
    "arquero_kicker": "NUESTRO DATO", "arquero_num": "00", "arquero_lab": "qué mide", "arquero_ctx": "Contexto.",

    "llega_kicker": "CÓMO LLEGA",
    "llega_hero": "0°",
    "llega_hero_sub": "con 00 puntos, a 0 de ...",
    "llega_col_izq": ("Últimos 5", "WDWLD", "0 a favor, 0 en contra"),
    "llega_col_der": ("Prob. de descenso", "0,0%", "aclaración"),
    "llega_franja": "Frase de cierre de la placa",

    # ---- Cierre --------------------------------------------------------------
    "cierre_autor": "La previa",
    "cierre_frase": "La frase que cierra el carrusel.",
}

# ---- Texto de la publicación (sale en placas/<serie>/texto_publicacion.md) ----------------
# Instagram NO interpreta asteriscos: para resaltar, MAYÚSCULAS. Los hashtags fijos se agregan solos.
TITULO = "Previa Fecha NN vs RIVAL (local|visitante)"
TEXTO = """🖤🤍 TITULAR EN MAYÚSCULAS

Párrafo 1: cuándo y dónde se juega, y cómo llega el rival.

Párrafo 2: el dato que lo define.

Párrafo 3: qué cuidar y dónde lastimarlo.

Párrafo 4: el antecedente y lo que se juega el Negro."""
