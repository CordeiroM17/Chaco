# -*- coding: utf-8 -*-
"""
POST-PARTIDO · Fecha 32 · Chaco For Ever 2-2 Defensores de Belgrano (local)

    python ig.py post_partido f32_defensores

Números autoritativos: carpeta del partido en outputs/temporadas/2026/partidos/
Notas F32: empate ganando 2-0 al descanso. Figura B. Nievas (2 goles, 9.4, Mejor 11; foto
recortada de assets/BrianNievas.jpg para sacar el marcador de otro partido). Slot 7 = su
lugar en el Mejor 11; slot 10 = el segundo tiempo (arco_kicker).
Gráficos de cancha (heatmaps, mapa de asociación): regenerar con
nucleo/graficos_partido_marca.py (MATCH_KEY y FIGURA apuntando a este partido).
"""
from plantillas.base import ASSETS, ESCUDOS

# Carrusel corto: 8 placas. El análisis de "por qué empatamos" (tramos, goles del empate) y los
# gráficos de cancha viven en las historias (publicaciones/historias/f32_defensores.py).
ORDEN = [
    "resultado",
    "cita:cierre",            # MI LECTURA: va 2ª para que se vea sin deslizar
    "ficha_partido",
    "dato:gol",
    "figura",                 # incluye lo que era figura_numeros (en la bajada)
    "ranking:once",           # incluye lo que era slot7 (en el subtítulo)
    "grafico:mapa_asociacion",
    "ficha:tabla",            # dónde queda el Negro + lo que era defensa
    # Opcionales, fuera del carrusel corto (descomentar):
    # "figura_numeros", "dato:slot7", "ficha:defensa",
    # "dato:arco", "ficha:tramos", "dato:quiebre", "ficha:st", "dato_vs:goles", "dato_vs:patron",
    # "grafico:figura_heatmap", "grafico:heatmap_rival", "grafico:heatmap_equipo",
]

DATOS = {
    # ---- Cabecera / marcador -------------------------------------------------
    "fecha": 32,
    "local": "Chaco For Ever",
    "visitante": "Defensores de Belgrano",
    "goles_local": 2,
    "goles_visitante": 2,
    "condicion": "local",                # 'local' o 'visitante' (el Negro)
    "resumen_marcador": "Nievas marcó dos veces antes del descanso. Benítez descontó a los 63' y Aguirre empató a los 85'. Defensores ganó el xG por poco (1.80 a 1.60) pero lo dio vuelta en el segundo tiempo.",
    "escudo_local": ESCUDOS / "chaco_for_ever.png",
    "escudo_visitante": ESCUDOS / "defensores_de_belgrano.png",

    # ---- Ficha general del partido -------------------------------------------
    # Las columnas de la ficha van CHACO – RIVAL.
    "formacion": "4-4-2",
    "formacion_rival": "4-4-2",
    "posesion": "49% – 51%",
    "xg": "1.60 – 1.80",
    "tiros": "15 (7) – 15 (5)",
    "corners": "3 – 5",
    "duelos": "53 – 46",

    # ---- EL DATO: los goles de Nievas ----------------------------------------
    "gol_kicker": "EL GOL",
    "gol_num": "2",
    "gol_lab": "goles de Nievas antes del descanso (5' y 45'+3)",
    "gol_ctx": (
        "Un cabezazo tras centro de Ojeda y un remate de derecha después de un "
        "pase entre líneas. El Negro se fue 2-0 arriba, con 1.26 de xG contra 0.63."
    ),

    # ---- LA FIGURA: Brian Nievas -------------------------------------------
    "figura": "Brian Nievas",
    "figura_bajada": "Dos goles (5' y 45'+3), 8 duelos ganados y 36 pases de 46. El puntaje más alto del año para un jugador de Chaco.",
    "figura_teaser": "9.4 - El mejor rating del año",
    "figura_stats": [
        ("Goles", "2  (5' y 45'+3)"),
        ("xG", "0.60"),
        ("Pases", "36 de 46"),
        ("Duelos ganados", "8"),
        ("Minutos", "73"),
        ("Rating", "9.4"),
    ],
    "figura_destacar": "Goles",
    # Foto completa, sin recorte: 1ª imagen de la publicación abierta en Nievas2.html
    # (instagram.com/chinonievas/p/DcZisEIj0X_, .heic convertido); la 2ª (blanco y negro)
    # es Nievas2_b.jpg. Con None se dibuja el marco reservado.
    "figura_foto": ASSETS / "Nievas2.jpg",
    "figura_foto_focal": (0.5, 0.5),
    "figura_foto_zoom": 1.0,
    "figura_foto_offset": (0, 0),
    "figura_escudo": ESCUDOS / "chaco_for_ever.png",
    "figura_escudo_leyenda": "Rating 9.4",

    # ---- LOS MEJORES DEL NEGRO / MEJOR 11 -------------------------------------
    "once_titulo": "Los mejores del Negro",
    "once_sub": "Ratings de SofaScore · Nievas (9.4) entró al Mejor 11 de la fecha",
    "once_filas": [
        ("B. Nievas", 9.4),
        ("A. Ojeda", 7.3),
        ("E. Gaggi", 7.0),
        ("M. S. Romero", 7.0),
        ("E. Pacheco", 6.9),
        ("J. Carrizo", 6.9),
    ],
    "once_piso": 7.0,
    "once_destacar": 0,
    "slot7_kicker": "EL MEJOR 11",
    "slot7_num": "9.4",
    "slot7_lab": "el puntaje más alto de toda la Zona A en la fecha 32",
    "slot7_ctx": (
        "Nievas entró al Mejor 11 de la fecha. Es el rating más alto de un "
        "jugador de Chaco en 2026 y llega a 5 goles, segundo del plantel."
    ),

    # ---- GRÁFICOS DE CANCHA --------------------------------------------------
    "mapa_asociacion_ruta": ASSETS / "partido/mapa_asociacion_ig.png",
    "mapa_asociacion_titulo": "Cómo salió el Negro",
    "mapa_asociacion_sub": "Con 49% de la pelota, el Negro hizo 15 remates y 2 goles.",

    "figura_heatmap_ruta": ASSETS / "partido/heatmap_figura_ig.png",
    "figura_heatmap_titulo": "Dónde jugó {apellido_figura}",
    "figura_heatmap_sub": "Volante por el centro de la cancha, con llegada al área en sus dos goles.",

    "heatmap_rival_ruta": ASSETS / "partido/heatmap_rival_ig.png",
    "heatmap_rival_titulo": "Dónde jugó Defensores",
    "heatmap_rival_sub": "51% de pelota y 9 de sus 15 remates desde adentro del área.",

    "heatmap_equipo_ruta": ASSETS / "partido/heatmap_equipo_ig.png",
    "heatmap_equipo_titulo": "Dónde vivió cada equipo",
    "heatmap_equipo_sub": "Un partido parejo en la cancha: 49% de pelota para el Negro, 51% para Defensores.",

    # ---- ANÁLISIS: ¿por qué empatamos? ---------------------------------------
    # Los números salen del shotmap del partido (xG por tramo, remates en el área con
    # coord_x <= 15). Si una fecha no lo necesita, se saca del ORDEN.
    "tramos_titulo": "¿Qué pasó en el 2-2?",
    "tramos_sub": "xG por tramo · Negro – Rival",
    "tramos_stats": [
        ("0' – 45'", "1.26 – 0.63"),
        ("45' – 60'", "0.11 – 0.22"),
        ("60' – 69'", "0.08 – 0.09"),
        ("69' – 90'", "0.14 – 0.86"),
    ],
    "tramos_destacar": "69' – 90'",

    "quiebre_kicker": "EL QUIEBRE",
    "quiebre_num": "69'",
    "quiebre_lab": "el minuto en que se inclinó el partido",
    "quiebre_ctx": (
        "Hasta ahí estaba parejo: 0.08 – 0.09 de xG desde los 60'. Del 69' al final, "
        "Defensores sumó 0.86 y el Negro 0.14, con nuestros cinco cambios en el medio."
    ),

    "st_titulo": "El segundo tiempo",
    "st_sub": "Negro – Rival · del 46' al final",
    "st_stats": [
        ("Goles", "0 – 2"),
        ("xG", "0.33 – 1.17"),
        ("Remates", "6 – 9"),
        ("Remates al arco", "3 – 4"),
        ("Remates en el área", "0 – 5"),
        ("xG por remate", "0.06 – 0.13"),
    ],
    "st_destacar": "Remates en el área",

    "goles_kicker": "LOS GOLES DEL EMPATE",
    "goles_hero": "0.05",
    "goles_hero_sub": "el xG del remate del 2-1: Benítez, a unos 22 metros (63')",
    "goles_col_izq": ("El 2-1", "Benítez", "Había entrado a los 60'"),
    "goles_col_der": ("El 2-2", "0.36 de xG", "Aguirre, 85', en el área"),
    "goles_franja": "Defensores terminó con 1.80 de xG; el Negro, con 1.60",

    # ---- LA DEFENSA ---------------------------------------------------------
    "defensa_titulo": "Dos goles en casa",
    "defensa_sub": "Los primeros de local con Cravero en el banco",
    "defensa_stats": [
        ("Goles recibidos", "2"),
        ("Atajadas de Caprio", "3"),
        ("xG concedido", "1.80"),
        ("Remates recibidos", "15  (5 al arco)"),
        ("Desde adentro del área", "9 de 15"),
        ("Vallas invictas en 2026", "12"),
    ],
    "defensa_destacar": "Goles recibidos",

    # ---- FICHA: dónde queda el equipo --------------------------------------
    "tabla_titulo": "Dónde queda el Negro",
    "tabla_sub": "Tabla y racha tras la fecha 32",
    "tabla_stats": [
        ("Posición", "10°  ·  37 pts"),
        ("Sobre el descenso", "+6 sobre San Miguel (17°)"),
        ("Prob. de descenso", "0.17%"),
        ("Goles recibidos", "2  (1.80 de xG)"),
        ("Vallas invictas en 2026", "12"),
        ("Últimos 6 partidos", "2V-3E-1D  ·  9 pts"),
        ("Lo que viene", "Deportivo Madryn (V)"),
    ],
    "tabla_destacar": "Prob. de descenso",

    # ---- Cierre --------------------------------------------------------------
    "cierre_autor": "Lectura del partido",
    "cierre_frase": (
        "Ganamos el primer tiempo y llegamos a estar 2-0, pero el segundo "
        "se nos fue. Sumamos un punto que nos acerca a la permanencia: "
        "quedan cuatro fechas para cerrarla."
    ),
}
