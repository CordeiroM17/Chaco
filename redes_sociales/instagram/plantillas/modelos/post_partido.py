# -*- coding: utf-8 -*-
"""
POST-PARTIDO · Fecha NN · LOCAL x-y VISITANTE

    python ig.py post_partido <nombre-de-este-archivo>

Antes de generar: regenerar los gráficos de cancha con nucleo/graficos_partido_marca.py
(MATCH_KEY y FIGURA apuntando a este partido). Los números salen del informe del partido.

Placas que no quieras: sacalas del ORDEN. Las que quieras sumar: escribí sus claves en
DATOS y agregalas al ORDEN (tipos en plantillas/base.py). Los textos aceptan {fecha},
{rival} y {apellido_figura}. Los gráficos con ruta que no exista se saltean avisando.
"""
from plantillas.base import ASSETS, ESCUDOS

ORDEN = [
    "resultado",
    "cita:cierre",   # MI LECTURA: va 2ª para que se vea sin deslizar
    "ficha_partido",
    "dato:gol",
    "figura",
    "figura_numeros",
    "ranking:once",
    "dato:slot7",
    "grafico:mapa_asociacion",
    "grafico:figura_heatmap",
    "ficha:defensa",
    "grafico:heatmap_rival",
    "grafico:heatmap_equipo",
    "ficha:tabla",
    # Opcionales (descomentar y completar sus claves):
    # "dato:arco",          # el ataque
    # "ficha:tramos", "dato:quiebre", "ficha:st", "dato_vs:goles",   # ¿por qué empatamos / perdimos?
    # "dato_vs:patron",     # patrón local vs visitante
]

DATOS = {
    # ---- Cabecera / marcador -------------------------------------------------
    "fecha": 0,
    "local": "Chaco For Ever",
    "visitante": "Rival",
    "goles_local": 0,
    "goles_visitante": 0,
    "condicion": "local",                # 'local' o 'visitante' (el Negro)
    "resumen_marcador": "Dos o tres frases con lo que pasó.",
    "escudo_local": ESCUDOS / "chaco_for_ever.png",
    "escudo_visitante": ESCUDOS / "archivo_del_rival.png",

    # ---- Ficha general (columnas CHACO – RIVAL) -------------------------------
    "formacion": "4-4-2", "formacion_rival": "4-4-2",
    "posesion": "00% – 00%", "xg": "0.00 – 0.00", "tiros": "0 (0) – 0 (0)",
    "corners": "0 – 0", "duelos": "00 – 00",

    # ---- El dato del partido ----------------------------------------------------
    "gol_kicker": "EL GOL", "gol_num": "0", "gol_lab": "qué mide", "gol_ctx": "Contexto.",

    # ---- La figura -------------------------------------------------------------
    "figura": "Nombre Apellido",
    "figura_bajada": "Una frase sobre su partido.",
    "figura_teaser": "0.0 - Su partido, en números",
    "figura_stats": [("Goles", "0"), ("xG", "0.00"), ("Pases", "0 de 0"),
                     ("Duelos ganados", "0"), ("Minutos", "00"), ("Rating", "0.0")],
    "figura_destacar": "Goles",
    "figura_foto": ASSETS / "Foto_del_jugador.jpg",     # None = marco reservado
    "figura_foto_focal": (0.5, 0.5), "figura_foto_zoom": 1.0, "figura_foto_offset": (0, 0),
    "figura_escudo": ESCUDOS / "chaco_for_ever.png",
    "figura_escudo_leyenda": "Rating 0.0",

    # ---- Mejores del Negro / Mejor 11 ---------------------------------------------
    "once_titulo": "Los mejores del Negro",
    "once_sub": "Ratings de SofaScore",
    "once_filas": [("A. Apellido", 7.0), ("B. Apellido", 6.9)],
    "once_piso": 7.0, "once_destacar": 0,
    "slot7_kicker": "EL MEJOR 11", "slot7_num": "0.0", "slot7_lab": "qué mide", "slot7_ctx": "Contexto.",

    # ---- Gráficos de cancha (nucleo/graficos_partido_marca.py) -------------------
    "mapa_asociacion_ruta": ASSETS / "partido/mapa_asociacion_ig.png",
    "mapa_asociacion_titulo": "Cómo salió el Negro",
    "mapa_asociacion_sub": "Frase.",
    "figura_heatmap_ruta": ASSETS / "partido/heatmap_figura_ig.png",
    "figura_heatmap_titulo": "Dónde jugó {apellido_figura}",
    "figura_heatmap_sub": "Frase.",
    "heatmap_rival_ruta": ASSETS / "partido/heatmap_rival_ig.png",
    "heatmap_rival_titulo": "Dónde jugó {rival}",
    "heatmap_rival_sub": "Frase.",
    "heatmap_equipo_ruta": ASSETS / "partido/heatmap_equipo_ig.png",
    "heatmap_equipo_titulo": "Dónde vivió cada equipo",
    "heatmap_equipo_sub": "Frase.",

    # ---- La defensa ----------------------------------------------------------------
    "defensa_titulo": "Título",
    "defensa_sub": "Subtítulo",
    "defensa_stats": [("Goles recibidos", "0"), ("Atajadas", "0"), ("xG concedido", "0.00")],
    "defensa_destacar": "Goles recibidos",

    # ---- Dónde queda el equipo -------------------------------------------------------
    "tabla_titulo": "Dónde queda el Negro",
    "tabla_sub": "Tabla y racha tras la fecha {fecha}",
    "tabla_stats": [("Posición", "0°  ·  00 pts"), ("Diferencia de gol", "0"),
                    ("Prob. de descenso", "0.0%"), ("Lo que viene", "Rival (L)")],
    "tabla_destacar": "Prob. de descenso",

    # ---- Cierre --------------------------------------------------------------
    "cierre_autor": "Lectura del partido",
    "cierre_frase": "La frase que cierra el carrusel.",
}

# ---- Texto de la publicación (sale en placas/<serie>/texto_publicacion.md) ----------------
# Instagram NO interpreta asteriscos: para resaltar, MAYÚSCULAS. Los hashtags fijos se agregan solos.
TITULO = "Post-partido Fecha NN vs RIVAL (x-y)"
TEXTO = """🖤🤍 TITULAR EN MAYÚSCULAS

Párrafo 1: cómo fue el partido y los goles.

Párrafo 2: el dato que lo explica.

Párrafo 3: la figura y los ratings.

Párrafo 4: cómo queda el Negro y lo que viene."""
