# -*- coding: utf-8 -*-
"""
POST-PARTIDO · Fecha 33 · Deportivo Madryn 1-2 Chaco For Ever (visitante)

    python ig.py post_partido f33_madryn

Partido: 2026-10-11_vs_deportivo_madryn_a. Silba abrió a los 6', Nievas empató a los 14' y
Fernández lo dio vuelta a los 90+2' (falló un penal en el mismo minuto; asistió Pacheco).
Primera victoria de 2026 yendo abajo en el marcador (33 partidos). xG 1.90 - 1.92, pero 1.53
del xG del Negro llegó desde el 89'; hasta ahí Madryn 1.91 contra 0.36.
Figura: L. Fernández (8.0, el mejor del partido; Silba 7.8). Gráficos de cancha generados con
nucleo/graficos_partido_marca.py (MATCH_KEY de este partido, FIGURA = "L. Fernandez").
Sin Mejor 11 de la fecha: solo está scrapeado este partido.
La cita ("mi lectura") es un BORRADOR: editar a gusto.
"""
from plantillas.base import ASSETS, ESCUDOS

# Carrusel corto: 8 placas. Las historias (publicaciones/historias/f33_madryn.py) llevan el
# detalle por tramos, los ratings completos y el mapa de tiros.
ORDEN = [
    "resultado",
    "cita:cierre",            # MI LECTURA: va 2ª para que se vea sin deslizar
    "ficha_partido",
    "dato:gol",
    "figura",
    "ranking:once",
    "grafico:mapa_asociacion",
    "ficha:tabla",
    # Opcionales (descomentar):
    # "figura_numeros", "grafico:figura_heatmap", "grafico:heatmap_rival", "grafico:heatmap_equipo",
]

DATOS = {
    # ---- Cabecera / marcador -------------------------------------------------
    "fecha": 33,
    "local": "Deportivo Madryn",
    "visitante": "Chaco For Ever",
    "goles_local": 1,
    "goles_visitante": 2,
    "condicion": "visitante",
    "resumen_marcador": (
        "Silba abrió a los 6', Nievas empató a los 14' y Fernández lo dio vuelta a los "
        "90+2', después de fallar un penal. El Negro ganó de visitante yendo abajo en el marcador."),
    "escudo_local": ESCUDOS / "deportivo_madryn.png",
    "escudo_visitante": ESCUDOS / "chaco_for_ever.png",

    # ---- Ficha general (columnas CHACO – RIVAL) ---------------------------------
    "formacion": "4-1-4-1",
    "formacion_rival": "3-5-2",
    "posesion": "36% – 64%",
    "xg": "1.90 – 1.92",
    "tiros": "13 (5) – 15 (5)",
    "corners": "0 – 5",
    "duelos": "60% – 40%",

    # ---- EL DATO -----------------------------------------------------------------
    "gol_kicker": "EL GOL",
    "gol_num": "90+2'",
    "gol_lab": "el minuto en que Fernández dio vuelta el partido",
    "gol_ctx": (
        "Falló un penal y, en el mismo minuto, marcó el 2-1 con asistencia de Pacheco. "
        "Es la primera victoria del Negro en 2026 yendo abajo en el marcador."),

    # ---- LA FIGURA: Leandro Fernández ------------------------------------------
    "figura": "Leandro Fernández",
    "figura_bajada": (
        "Hizo el gol de la victoria a los 90+2'. Fue el mejor del partido: 8.0, "
        "con 3 pases clave y 8 duelos ganados."),
    "figura_teaser": "8.0 - El mejor del partido",
    "figura_stats": [
        ("Goles", "1  (90+2')"),
        ("xG", "1.38  (con el penal)"),
        ("Pases", "30 de 45"),
        ("Pases clave", "3"),
        ("Duelos ganados", "8 de 16"),
        ("Rating", "8.0"),
    ],
    "figura_destacar": "Goles",
    "figura_foto": ASSETS / "Leandro_Fernandez.jpg",
    "figura_foto_focal": (0.5, 0.35),
    "figura_foto_zoom": 1.0,
    "figura_foto_offset": (0, 0),
    "figura_escudo": ESCUDOS / "chaco_for_ever.png",
    "figura_escudo_leyenda": "Rating 8.0",

    # ---- LOS MEJORES DEL NEGRO -------------------------------------------------
    "once_titulo": "Los mejores del Negro",
    "once_sub": "Ratings de SofaScore · Fernández (8.0) fue el mejor de los dos equipos",
    "once_filas": [
        ("L. Fernández", 8.0),
        ("B. Nievas", 7.5),
        ("N. Caprio", 7.3),
        ("E. Pacheco", 7.3),
        ("A. Ojeda", 7.2),
        ("A. Lioi", 7.1),
    ],
    "once_piso": 7.0,
    "once_destacar": 0,

    # ---- GRÁFICOS DE CANCHA ------------------------------------------------------
    "mapa_asociacion_ruta": ASSETS / "partido/mapa_asociacion_ig.png",
    "mapa_asociacion_titulo": "Cómo salió el Negro",
    "mapa_asociacion_sub": "Con 36% de la pelota, la dupla más conectada fue Nievas-Fernández.",
    "figura_heatmap_ruta": ASSETS / "partido/heatmap_figura_ig.png",
    "figura_heatmap_titulo": "Dónde jugó {apellido_figura}",
    "figura_heatmap_sub": "Volante con llegada al área en el final.",
    "heatmap_rival_ruta": ASSETS / "partido/heatmap_rival_ig.png",
    "heatmap_rival_titulo": "Dónde jugó Madryn",
    "heatmap_rival_sub": "64% de pelota y 9 de sus 15 remates dentro del área.",
    "heatmap_equipo_ruta": ASSETS / "partido/heatmap_equipo_ig.png",
    "heatmap_equipo_titulo": "Dónde vivió cada equipo",
    "heatmap_equipo_sub": "Madryn con la pelota; el Negro, atrás y rápido al final.",

    # ---- DÓNDE QUEDA EL EQUIPO -------------------------------------------------
    "tabla_titulo": "Dónde queda el Negro",
    "tabla_sub": "Tabla y racha tras la fecha {fecha}",
    "tabla_stats": [
        ("Posición", "10°  ·  40 pts"),
        ("Diferencia de gol", "-2"),
        ("Sobre el descenso", "+8 sobre Acassuso (17°)"),
        ("Últimos 6 partidos", "3V-2E-1D  ·  11 pts"),
        ("Prob. de descenso", "0%"),
        ("Visitante en 2026", "3V-5E-9D"),
        ("Lo que viene", "Central Norte (L)"),
    ],
    "tabla_destacar": "Prob. de descenso",

    # ---- Cierre (BORRADOR de la lectura) ------------------------------------------
    "cierre_autor": "Lectura del partido",
    "cierre_frase": (
        "Lo ganamos con el 80% de nuestro xG en los últimos diez minutos. Hasta el 89', "
        "Madryn había generado mucho más que nosotros. Es un triunfo de carácter y de Fernández/Nievas, "
        "no de dominio: 40 puntos y a un paso de la permanencia."),
}

# ---- Texto de la publicación (sale en placas/<serie>/texto_publicacion.md) -------------------
# Instagram NO interpreta asteriscos: para resaltar, MAYÚSCULAS. Los hashtags fijos se agregan solos.
TITULO = "Post-partido Fecha 33 vs Deportivo Madryn (1-2)"
TEXTO = """🖤🤍 ¡LO DIMOS VUELTA EN MADRYN!

Ganamos 2-1 de visitante y llegamos a 40 puntos. Silba abrió a los 6', Nievas empató a los 14' y Leandro Fernández la dio vuelta a los 90+2', en el mismo minuto en que había fallado un penal. Asistió Ezequiel Pacheco. Es la primera victoria del Negro en 2026 yendo abajo en el marcador.

Fue un triunfo de carácter, no de dominio. Madryn tuvo el 64% de la pelota y hasta el 89' había generado 1.91 de xG (goles esperados) contra 0.36 nuestro. En los últimos minutos el Negro sumó 1.53, más del 80% de todo lo que generó en el partido. Caprio hizo cuatro atajadas.

Leandro Fernández fue el mejor de la cancha: 8.0 en SofaScore, con 3 pases clave y 8 duelos ganados. Después, Nievas (7.5), Caprio y Pacheco (7.3).

El Negro es 10° con 40 puntos, a 8 de la zona de descenso. Con 9 puntos en juego, ganar el domingo 18/10 ante Central Norte, de local, lo deja salvado matemáticamente."""
NOTAS = """- 8 placas en `placas/partido_fecha_33_deportivo_madryn/`; historias en `placas/historias_fecha_33_deportivo_madryn/`
  (ratings, mapa de tiros, por tramos), `historias_fecha_33_express/` y `historias_proyeccion_fecha_33/`.
- Fuentes: partido 2026-10-11_vs_deportivo_madryn_a (shotmap, lineups, incidents) y standings/fixture del 2026-10-13.
- Sin Mejor 11 de la fecha (solo está scrapeado este partido). Sin amarillas (convención de la cuenta)."""
