# -*- coding: utf-8 -*-
"""
POST-PARTIDO · Fecha 34 · Chaco For Ever 1-2 Central Norte de Salta (local)

    python ig.py post_partido f34_central_norte

Partido: 2026-10-18_vs_central_norte_h. Felissia abrió a los 36' (córner de Vedoya),
Fernández empató a los 45'+2 y Mateo lo ganó a los 88'. Luque, expulsado a los 75'.
Hasta el 75' Chaco llevaba 2.43 de xG contra 0.90; del 75' al final Central Norte hizo
2.47 de xG en 11 remates y Chaco 0.00. Chaco quedó matemáticamente salvado (10°, 40 pts).
Figura: L. Fernández (7.8, único de Chaco en el Mejor 11 de la fecha). Gráficos de cancha
generados con nucleo/graficos_partido_marca.py (MATCH_KEY de este partido).
Informe completo: outputs/temporadas/2026/partidos/2026-10-18_vs_central_norte_h/.
La cita ("mi lectura") es un BORRADOR: editar a gusto.
"""
from plantillas.base import ASSETS, ESCUDOS

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
    "fecha": 34,
    "local": "Chaco For Ever",
    "visitante": "Central Norte de Salta",
    "goles_local": 1,
    "goles_visitante": 2,
    "condicion": "local",
    "resumen_marcador": (
        "Felissia abrió a los 36', Fernández empató a los 45'+2 y Mateo lo ganó a los 88'. "
        "Luque fue expulsado a los 75' y Central Norte hizo 11 remates desde los 80'."),
    "escudo_local": ESCUDOS / "chaco_for_ever.png",
    "escudo_visitante": ESCUDOS / "central_norte_de_salta.png",

    # ---- Ficha general (columnas CHACO – RIVAL) ---------------------------------
    "formacion": "4-4-2",
    "formacion_rival": "4-4-2",
    "posesion": "57% – 43%",
    "xg": "2.44 – 3.36",
    "tiros": "20 (9) – 21 (8)",
    "corners": "3 – 9",
    "duelos": "41% – 59%",

    # ---- EL DATO -----------------------------------------------------------------
    "gol_kicker": "EL FINAL",
    "gol_num": "2.47",
    "gol_lab": "el xG de Central Norte del 75' al final",
    "gol_ctx": (
        "Hasta la roja a Luque (75') el Negro llevaba 2.43 de xG contra 0.90. "
        "Desde el 80' Central Norte hizo 11 remates y el 1-2 llegó en el minuto 88."),

    # ---- LA FIGURA: Leandro Fernández ------------------------------------------
    "figura": "Leandro Fernández",
    "figura_bajada": (
        "Marcó el empate a los 45'+2 con 0.84 de xG. Fue el mejor de Chaco: 7.8, "
        "con 3 pases clave. Es el único del Negro en el Mejor 11 de la fecha."),
    "figura_teaser": "7.8 - El mejor de Chaco",
    "figura_stats": [
        ("Goles", "1  (45'+2)"),
        ("xG", "0.84"),
        ("Pases", "39 de 52"),
        ("Pases clave", "3"),
        ("xA", "0.41"),
        ("Rating", "7.8"),
    ],
    "figura_destacar": "Goles",
    "figura_foto": ASSETS / "Leandro_Fernandez.jpg",
    "figura_foto_focal": (0.5, 0.35),
    "figura_foto_zoom": 1.0,
    "figura_foto_offset": (0, 0),
    "figura_escudo": ESCUDOS / "chaco_for_ever.png",
    "figura_escudo_leyenda": "Rating 7.8",

    # ---- LOS MEJORES DEL NEGRO -------------------------------------------------
    "once_titulo": "Los mejores del Negro",
    "once_sub": "Ratings de SofaScore · Fernández, en el Mejor 11 de la fecha",
    "once_filas": [
        ("L. Fernández", 7.8),
        ("N. Caprio", 7.6),
        ("E. Pacheco", 7.3),
        ("E. Gaggi", 7.3),
        ("D. Valdez", 7.2),
        ("M. S. Romero", 7.0),
    ],
    "once_piso": 7.0,
    "once_destacar": 0,

    # ---- GRÁFICOS DE CANCHA ------------------------------------------------------
    "mapa_asociacion_ruta": ASSETS / "partido/mapa_asociacion_ig.png",
    "mapa_asociacion_titulo": "Cómo salió el Negro",
    "mapa_asociacion_sub": "57% de la pelota: 408 pases, 81% acertados.",
    "figura_heatmap_ruta": ASSETS / "partido/heatmap_figura_ig.png",
    "figura_heatmap_titulo": "Dónde jugó {apellido_figura}",
    "figura_heatmap_sub": "Partió por la izquierda y llegó al área para el 1-1.",
    "heatmap_rival_ruta": ASSETS / "partido/heatmap_rival_ig.png",
    "heatmap_rival_titulo": "Dónde jugó Central Norte",
    "heatmap_rival_sub": "14 de sus 21 remates dentro del área.",
    "heatmap_equipo_ruta": ASSETS / "partido/heatmap_equipo_ig.png",
    "heatmap_equipo_titulo": "Dónde vivió cada equipo",
    "heatmap_equipo_sub": "Chaco con la pelota; Central Norte, a la ráfaga final.",

    # ---- DÓNDE QUEDA EL EQUIPO -------------------------------------------------
    "tabla_titulo": "Dónde queda el Negro",
    "tabla_sub": "Tabla y racha tras la fecha {fecha}",
    "tabla_stats": [
        ("Posición", "10°  ·  40 pts"),
        ("Diferencia de gol", "-3"),
        ("Sobre el descenso", "+7 sobre Acassuso (17°)"),
        ("Últimos 6 partidos", "2V-2E-2D  ·  8 pts"),
        ("Descenso", "Matemáticamente salvado"),
        ("Local en 2026", "7V-5E-5D"),
        ("Lo que viene", "Ferro (V)"),
    ],
    "tabla_destacar": "Descenso",

    # ---- Cierre (BORRADOR de la lectura) ------------------------------------------
    "cierre_autor": "Lectura del partido",
    "cierre_frase": (
        "Hasta la roja el partido era nuestro: 2.43 de xG contra 0.90. Con diez, Central Norte "
        "hizo 2.47 en los últimos 15. Perdimos el partido, pero la permanencia ya es matemática: "
        "40 puntos y el peor puesto posible es el 16°."),
}

# ---- Texto de la publicación (sale en placas/<serie>/texto_publicacion.md) -------------------
# Instagram NO interpreta asteriscos: para resaltar, MAYÚSCULAS. Los hashtags fijos se agregan solos.
TITULO = "Post-partido Fecha 34 vs Central Norte de Salta (1-2)"
TEXTO = """🖤🤍 PERDIMOS EL PARTIDO, PERO ESTAMOS SALVADOS

Chaco 1-2 Central Norte, de local. Felissia abrió a los 36', Leandro Fernández empató a los 45'+2 y Joaquín Mateo ganó el partido a los 88'. Alan Luque fue expulsado a los 75'.

Hasta la expulsión el Negro llevaba 2.43 de xG (goles esperados) contra 0.90 y 18 remates contra 10. Del 75' al final, con diez, Central Norte hizo 11 remates y 2.47 de xG; Chaco, 0.00. En todo el partido el Negro remató 20 veces, la cifra más alta de sus 33 partidos con registro de remates en 2026.

Fernández fue el mejor del Negro: 7.8 en SofaScore, con gol y 3 pases clave. Es el único jugador de Chaco en el Mejor 11 de la fecha. Después, Caprio (7.6, seis atajadas), Pacheco y Gaggi (7.3).

Con el empate de Acassuso y la derrota de San Miguel, el Negro es 10° con 40 puntos y queda matemáticamente salvado: el peor puesto al que puede caer es el 16°. Quedan Ferro de visitante (24/10) y Racing de Córdoba de local (31/10)."""
NOTAS = """- 8 placas en `placas/partido_fecha_34_central_norte/`.
- Fuentes: partido 2026-10-18_vs_central_norte_h (shotmap, lineups, incidents) y standings/fixture del 2026-10-19.
- La sanción de Luque para Ferro está sin confirmar (no figura en el texto). Sin amarillas (convención de la cuenta).
- Duelos: % de duelos terrestres ganados (43 de 104 contra 61 de 105)."""
