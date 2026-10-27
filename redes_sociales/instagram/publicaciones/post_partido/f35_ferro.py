# -*- coding: utf-8 -*-
"""
POST-PARTIDO · Fecha 35 · Ferro Carril Oeste 0-3 Chaco For Ever (visitante)

    python ig.py post_partido f35_ferro

Partido: 2026-10-24_vs_ferro_carril_oeste_a. Romero a los 1' (asistió Díaz Chaves), Díaz Chaves
a los 45'+1 y Romero a los 74' (asistió Fernández). Roja a González (Ferro) a los 44'.
Ferro: 23 remates y 2.33 de xG; Chaco 11 y 1.44, con 3 goles. Caprio atajó los 10 remates al
arco (2.15 de xGOT). Figura: N. Caprio (9.5, puntaje más alto del año).
La placa de tabla cuenta la punta: Ferro 65 y Godoy 63 (3-0 en Mitre, 25/10).
Gráficos de cancha: nucleo/graficos_partido_marca.py (MATCH_KEY = este partido, FIGURA Caprio).
Informe completo: outputs/temporadas/2026/partidos/2026-10-24_vs_ferro_carril_oeste_a/.
La cita ("lectura") es un BORRADOR: editar a gusto.
"""
from plantillas.base import ASSETS, ESCUDOS

ORDEN = [
    "resultado",
    "cita:cierre",            # LECTURA: va 2ª para que se vea sin deslizar
    "ficha_partido",
    "dato:gol",
    "figura",
    "ranking:once",
    "grafico:mapa_asociacion",
    "ficha:tabla",
]

DATOS = {
    # ---- Cabecera / marcador -------------------------------------------------
    "fecha": 35,
    "local": "Ferro Carril Oeste",
    "visitante": "Chaco For Ever",
    "goles_local": 0,
    "goles_visitante": 3,
    "condicion": "visitante",
    "resumen_marcador": (
        "Romero abrió al minuto, Díaz Chaves hizo el 2-0 a los 45'+1 y Romero cerró a los 74'. "
        "A Ferro lo expulsaron a González a los 44' y Caprio atajó los 10 remates al arco."),
    "escudo_local": ESCUDOS / "ferro_carril_oeste.png",
    "escudo_visitante": ESCUDOS / "chaco_for_ever.png",

    # ---- Ficha general (columnas CHACO – RIVAL) ---------------------------------
    "formacion": "3-5-2",
    "formacion_rival": "4-1-4-1",
    "posesion": "38% – 62%",
    "xg": "1.44 – 2.33",
    "tiros": "11 (5) – 23 (10)",
    "corners": "0 – 10",
    "duelos": "44% – 56%",

    # ---- EL DATO -----------------------------------------------------------------
    "gol_kicker": "LA PUNTERÍA",
    "gol_num": "+1.56",
    "gol_lab": "goles por encima del xG: tres goles con 1.44 esperado",
    "gol_ctx": (
        "Ferro hizo 23 remates y 2.33 de xG, y no marcó. Chaco convirtió tres de sus cinco "
        "remates al arco: la mayor diferencia entre goles y xG de su año."),

    # ---- LA FIGURA: Nicolás Caprio -----------------------------------------------
    "figura": "Nicolás Caprio",
    "figura_bajada": (
        "Atajó los 10 remates al arco de Ferro, que valían 2.15 de xGOT. Terminó con 9.5, "
        "el puntaje más alto de un jugador del Negro en 2026."),
    "figura_teaser": "9.5 - El mejor del partido",
    "figura_stats": [
        ("Atajadas", "10"),
        ("Goles recibidos", "0"),
        ("xGOT enfrentado", "2.15"),
        ("Pases", "13 de 15"),
        ("Rating", "9.5"),
    ],
    "figura_destacar": "Atajadas",
    "figura_foto": ASSETS / "Nicolas_Caprio.jpg",
    "figura_foto_focal": (0.5, 0.35),
    "figura_foto_zoom": 1.0,
    "figura_foto_offset": (0, 0),
    "figura_escudo": ESCUDOS / "chaco_for_ever.png",
    "figura_escudo_leyenda": "Rating 9.5",

    # ---- LOS MEJORES DEL NEGRO -------------------------------------------------
    "once_titulo": "Los mejores del Negro",
    "once_sub": "Ratings de SofaScore · Caprio, el mejor del partido",
    "once_filas": [
        ("N. Caprio", 9.5),
        ("M. S. Romero", 8.3),
        ("M. D. Chaves", 8.0),
        ("L. Fernández", 7.8),
        ("E. Gaggi", 7.2),
        ("D. Valdez", 7.1),
    ],
    "once_piso": 7.0,
    "once_destacar": 0,

    # ---- GRÁFICOS DE CANCHA ------------------------------------------------------
    "mapa_asociacion_ruta": ASSETS / "partido/mapa_asociacion_ig.png",
    "mapa_asociacion_titulo": "Cómo jugó el Negro",
    "mapa_asociacion_sub": "38% de la pelota: 366 pases, 81% acertados.",

    # ---- LA PUNTA DE LA ZONA A --------------------------------------------------
    "tabla_titulo": "Arruinamos la fiesta",
    "tabla_sub": "La punta de la Zona A tras la fecha {fecha}",
    "tabla_stats": [
        ("Ferro", "65 pts  ·  perdió 0-3"),
        ("Godoy Cruz", "63 pts  ·  ganó 3-0 en Mitre"),
        ("Diferencia", "5 puntos antes, 2 ahora"),
        ("Si Ferro ganaba", "68 pts: primero con una fecha de sobra"),
        ("Fecha 36", "Acassuso-Ferro y Godoy-Almirante Brown"),
        ("Primer puesto", "Se define en la última fecha"),
    ],
    "tabla_destacar": "Primer puesto",

    # ---- Cierre (BORRADOR de la lectura) ------------------------------------------
    "cierre_autor": "Lectura del partido",
    "cierre_frase": (
        "Ferro tuvo la pelota, 23 remates y 2.33 de xG. Nosotros tuvimos tres goles y a Caprio. "
        "Marcamos al minuto, marcamos otra vez antes del descanso y le arruinamos la fiesta al "
        "puntero. Con Godoy ganando, el primer puesto se define en la última fecha."),
}

# ---- Texto de la publicación (sale en placas/<serie>/texto_publicacion.md) -------------------
# Instagram NO interpreta asteriscos: para resaltar, MAYÚSCULAS. Los hashtags fijos se agregan solos.
TITULO = "Post-partido Fecha 35 vs Ferro Carril Oeste (0-3)"
TEXTO = """🖤🤍 GANAMOS EN LA CANCHA DEL PUNTERO Y LE ARRUINAMOS LA FIESTA

Ferro 0-3 Chaco, de visitante. Matías Romero abrió el marcador al minuto, Díaz Chaves hizo el segundo a los 45'+1 y Romero cerró la cuenta de cabeza a los 74'. A Ferro lo expulsaron a González a los 44'.

Ferro tuvo 62% de la pelota, 23 remates y 2.33 de xG (goles esperados) contra 1.44 del Negro. No pudo marcar: Nicolás Caprio atajó los 10 remates que fueron al arco, que valían 2.15 de xGOT. Su 9.5 en SofaScore es el puntaje más alto que registró un jugador del Negro en 2026. Detrás de Caprio, Romero (8.3), Díaz Chaves (8.0) y Fernández (7.8).

Con una victoria, Ferro llegaba a 68 puntos y era primero con una fecha de sobra. Se quedó en 65. Godoy Cruz ganó 3-0 en Mitre y quedó a dos puntos. El primer puesto de la Zona A se define en la última fecha: Ferro visita a Acassuso y Godoy Cruz recibe a Almirante Brown.

El Negro cierra la fecha 36 de local, contra Racing de Córdoba (31/10)."""
NOTAS = """- 8 placas en `placas/partido_fecha_35_ferro_carril_oeste/`.
- Fuentes: partido 2026-10-24_vs_ferro_carril_oeste_a (shotmap, lineups, incidents) y standings/fixture del 2026-10-26.
- Sin amarillas ni sanciones (convención de la cuenta). El desempate si Ferro y Godoy igualan en puntos no está en los datos: no se menciona.
- Duelos: % de duelos terrestres ganados (39 de 88 contra 50 de 88)."""
