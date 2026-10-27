# -*- coding: utf-8 -*-
"""
Carrusel de ANÁLISIS DE PARTIDO para la cuenta de estadísticas de Chaco For Ever.

Base reutilizable: todo lo que cambia de un partido a otro está en el bloque
DATOS de acá abajo. Para el próximo partido NO se toca el código: se copian los
valores nuevos en DATOS, se apunta FOTO_FIGURA a la foto del jugador y se corre:

    python scripts/carrusel_partido.py

Lo que sale fijo (la marca, el orden de las placas, los textos guía) ya está
armado. Vos solo cambiás los números.

------------------------------------------------------------------------------
PARTIDO ARMADO ACÁ: Fecha 32 · Chaco For Ever 2-2 Defensores de Belgrano (local)
Notas F32: empate ganando 2-0 al descanso. Figura B. Nievas (2 goles, 9.4, Mejor 11; foto
recortada de assets/BrianNievas.jpg para sacar el marcador de otro partido). Slot 7 = su
lugar en el Mejor 11; slot 10 = el segundo tiempo (arco_kicker). Anterior: F31 1-2 en Bolívar.
Notas F31: derrota. Figura L. Fernández (gol 57', 7.4), sin foto (escudo). Ningún
jugador de Chaco en el Mejor 11: el slot 6 es un ranking de ratings del Negro y el
slot 7 pasó a ser el penal errado por Bolívar (claves slot7_*). Anterior: F30 1-0 a Almirante Brown.
Números autoritativos del pipeline de informes (carpeta del partido):
  outputs/temporadas/2026/partidos/2026-09-20_vs_almirante_brown_h/
  Informe_partido_fecha_30_almirante_brown.pdf
Notas de armado de esta fecha:
  - Gráficos regenerados con graficos_partido_marca.py (MATCH_KEY y FIGURA
    apuntando a este partido; FIGURA = "A. Ojeda").
  - La figura es Agustín Ojeda: hizo el único gol del partido (11', su primer
    gol de la temporada) y terminó siendo el mejor puntuado de Chaco (8.0) y
    el único jugador nuestro en el Mejor 11 de la Fecha 30 de la Zona A —
    cuarta fecha seguida con un jugador de Chaco en el equipo ideal. Foto de
    assets/Agustin_Ojeda.jpg (1080x1351, del post del club del 20/9 en
    Instagram; foto_focal (0.0, 0.18) y zoom 1.0 (sin zoom, entra el
    cuerpo completo) porque Ojeda está del lado izquierdo del original).
  - Ganamos con menos pelota (36%) pero mucho más xG (1.03 a 0.28) y casi el
    doble de remates (13 a 7): un partido de contragolpe que funcionó.
  - Sexta valla invicta seguida (la racha defensiva más larga del año, 0.33
    goles recibidos por partido con Cravero en 9 fechas).
  - El "patrón" de esta fecha (slide 14) usa el número verificado en esta
    sesión a partir del campo `manager` de cada event.json: Daniel Cravero
    asumió recién el 2/8 (vs Deportivo Morón), no antes. En sus 9 partidos
    como DT, Chaco es 5V-0E-0D de local (perfecto) y 0V-2E-2D de visitante.
  - Ojo con la previa: el informe pre-partido daba a Germán Pacheco afuera
    por sanción hasta la fecha 32, pero jugó 89' y fue uno de los más
    determinantes (3 pases clave, 0.39 de xA). No se usa esa data en el
    carrusel por las dudas hasta confirmar con el club; ver el informe de
    partido (sección 6) para el detalle.
------------------------------------------------------------------------------
"""
from pathlib import Path
import placas as P
import marca as M
import temas

RAIZ = Path(__file__).resolve().parents[1]          # .../redes_sociales/instagram
PROYECTO = RAIZ.parents[1]                           # raíz del proyecto

# ==========================================================================
#  FIJO — no se toca entre partido y partido
# ==========================================================================
CUENTA = "@chacoforever.stats"
COMPETENCIA = "Primera Nacional 2026"
ESCUDOS = RAIZ / "assets" / "escudos"      # escudos reutilizables (uno por club)

# ==========================================================================
#  DATOS DEL PARTIDO — esto es lo ÚNICO que cambiás cada fecha
# ==========================================================================
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
    "gol_num": "2",
    "gol_lab": "goles de Nievas antes del descanso (5' y 45'+3)",
    "gol_ctx": (
        "Un cabezazo tras centro de Ojeda y un remate de derecha después de un "
        "pase entre líneas. El Negro se fue 2-0 arriba, con 1.26 de xG contra 0.63."
    ),

    # ---- ANÁLISIS: ¿por qué empatamos? (placas opcionales, ver construir) -----------------
    # Los números salen del shotmap del partido (xG por tramo, remates en el área con
    # coord_x <= 15). Si una fecha no lo necesita, se borran estas claves.
    "tramos_titulo": "¿Qué pasó en el 2-2?",
    "tramos_sub": "xG por tramo · Negro – Rival",
    "tramos_filas": [
        ("0' – 45'", "1.26 – 0.63"),
        ("45' – 60'", "0.11 – 0.22"),
        ("60' – 69'", "0.08 – 0.09"),
        ("69' – 90'", "0.14 – 0.86"),
    ],
    "tramos_destacar": "69' – 90'",

    "quiebre_num": "69'",
    "quiebre_lab": "el minuto en que se inclinó el partido",
    "quiebre_ctx": (
        "Hasta ahí estaba parejo: 0.08 – 0.09 de xG desde los 60'. Del 69' al final, "
        "Defensores sumó 0.86 y el Negro 0.14, con nuestros cinco cambios en el medio."
    ),
    "quiebre_kicker": "EL QUIEBRE",

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

    "goles_hero": "0.05",
    "goles_hero_sub": "el xG del remate del 2-1: Benítez, a unos 22 metros (63')",
    "goles_izq": ("El 2-1", "Benítez", "Había entrado a los 60'"),
    "goles_der": ("El 2-2", "0.36 de xG", "Aguirre, 85', en el área"),
    "goles_franja": "Defensores terminó con 1.80 de xG; el Negro, con 1.60",

    # ---- LA FIGURA: Brian Nievas -------------------------------------------
    "figura": "Brian Nievas",
    "figura_bajada": "Dos goles y el puntaje más alto del año para un jugador de Chaco.",
    "figura_teaser": "9.4 - Sus dos goles, en números",
    "figura_stats": [
        ("Goles", "2  (5' y 45'+3)"),
        ("xG", "0.60"),
        ("Pases", "36 de 46"),
        ("Duelos ganados", "8"),
        ("Minutos", "73"),
        ("Rating", "9.4"),
    ],
    "figura_destacar": "Goles",
    "figura_heatmap": RAIZ / "assets/partido/heatmap_figura_ig.png",
    "figura_heatmap_sub": "Volante por el centro de la cancha, con llegada al área en sus dos goles.",
    "figura_escudo": ESCUDOS / "chaco_for_ever.png",
    "figura_escudo_leyenda": "Rating 9.4",
    "figura_foto_focal": (0.5, 0.5),
    "figura_foto_zoom": 1.0,
    "figura_foto_offset": (0, 0),

    # ---- LOS MEJORES DEL NEGRO / MEJOR 11 -------------------------------------
    "once_titulo": "Los mejores del Negro",
    "once_sub": "Ratings de SofaScore · Chaco 2-2 Defensores",
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
    "slot7_num": "9.4",
    "slot7_lab": "el puntaje más alto de toda la Zona A en la fecha 32",
    "slot7_ctx": (
        "Nievas entró al Mejor 11 de la fecha. Es el rating más alto de un "
        "jugador de Chaco en 2026 y llega a 5 goles, segundo del plantel."
    ),
    "slot7_kicker": "EL MEJOR 11",

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

    # ---- EL RIVAL -----------------------------------------------------------
    "heatmap_rival": RAIZ / "assets/partido/heatmap_rival_ig.png",
    "rival_titulo": "Dónde jugó Defensores",
    "rival_tiros_lejos": "51% de pelota y 9 de sus 15 remates desde adentro del área.",

    # ---- CÓMO SALIMOS JUGANDO: mapa de asociación -----------------------
    "mapa_asociacion": RAIZ / "assets/partido/mapa_asociacion_ig.png",
    "mapa_asociacion_sub": "Con 49% de la pelota, el Negro hizo 15 remates y 2 goles.",

    # ---- DÓNDE VIVIÓ CADA EQUIPO ---------------------------------------
    "heatmap_equipo": RAIZ / "assets/partido/heatmap_equipo_ig.png",
    "heatmap_equipo_sub": "Un partido parejo en la cancha: 49% de pelota para el Negro, 51% para Defensores.",

    # ---- FICHA: dónde queda el equipo --------------------------------------
    "tabla_titulo": "Dónde queda el Negro",
    "tabla_sub": "Tabla y racha tras la fecha 32",
    "tabla_stats": [
        ("Posición", "10°  ·  37 pts"),
        ("Diferencia de gol", "-3"),
        ("Sobre el descenso", "+6 sobre San Miguel (17°)"),
        ("Últimos 6 partidos", "2V-3E-1D  ·  9 pts"),
        ("Prob. de descenso", "0.17%"),
        ("Lo que viene", "Deportivo Madryn (V)"),
    ],

    # ---- Cierre --------------------------------------------------------------
    "cierre_frase": (
        "Ganamos el primer tiempo y llegamos a estar 2-0, pero el segundo "
        "se nos fue. Sumamos un punto que nos acerca a la permanencia: "
        "quedan cuatro fechas para cerrarla."
    ),
}

# ==========================================================================
#  FOTO de la figura — dejá la ruta a la imagen o None para el marco reservado
# ==========================================================================
# Foto de Agustín Ojeda, assets/Agustin_Ojeda.jpg.
FOTO_FIGURA = RAIZ / "assets" / "Nievas2.jpg"   # foto completa, sin recorte: 1ª imagen de la publicación abierta en Nievas2.html (instagram.com/chinonievas/p/DcZisEIj0X_, .heic convertido); la 2ª (blanco y negro) es Nievas2_b.jpg

# --------------------------------------------------------------------------
# El rival es el otro equipo del marcador: sirve para los títulos y la carpeta
# de salida, sin importar si el Negro jugó de local o de visitante.
RIVAL = DATOS["local"] if DATOS["condicion"] == "visitante" else DATOS["visitante"]

SALIDA = RAIZ / "placas" / f"partido_fecha_{DATOS['fecha']}_{RIVAL.lower().replace(' ', '_')}"
NOTA = f"Fecha {DATOS['fecha']} · {COMPETENCIA} · SofaScore"


def _ruta(p):
    """str(p) si el archivo existe; None si no. Sirve para escudos/gráficos
    opcionales: si falta el archivo, la placa simplemente no lo dibuja."""
    return str(p) if p and Path(p).exists() else None


def _resolver_foto():
    """Devuelve la ruta de la foto de la figura. Prioridad:
    1) FOTO_FIGURA si está seteada. 2) un archivo 'foto_figura.*' que dejes
    en la carpeta de salida del partido. 3) None -> se dibuja el marco reservado."""
    if FOTO_FIGURA and Path(FOTO_FIGURA).exists():
        return str(FOTO_FIGURA)
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        cand = SALIDA / f"foto_figura{ext}"
        if cand.exists():
            return str(cand)
    return None


def _condicion_txt():
    return "de local" if DATOS["condicion"] == "local" else "de visitante"


def construir():
    d = DATOS
    slides = []

    # 01 — RESULTADO con escudos (portada del carrusel)
    slides.append(P.resultado(
        d["local"], d["goles_local"], d["visitante"], d["goles_visitante"],
        torneo=f"{COMPETENCIA} · Fecha {d['fecha']}",
        detalle=d["resumen_marcador"],
        nota="SofaScore",
        logo_local=_ruta(d.get("escudo_local")),
        logo_visitante=_ruta(d.get("escudo_visitante"))))

    # 02 — FICHA DEL PARTIDO (destacado el xG: 1.03 contra 0.28)
    slides.append(P.ficha(
        "La ficha del partido",
        f"Chaco For Ever vs {RIVAL} · {_condicion_txt()}",
        [("Formación", d["formacion"]),
         ("Formación rival", d["formacion_rival"]),
         ("Posesión", d["posesion"]),
         ("xG (goles esperados)", d["xg"]),
         ("Tiros (al arco)", d["tiros"]),
         ("Córners", d["corners"]),
         ("Duelos ganados", d["duelos"])],
        nota=NOTA, destacar="xG (goles esperados)"))

    # 03 — EL DATO: el gol del partido
    slides.append(P.dato(
        d["gol_num"], d["gol_lab"], d["gol_ctx"],
        kicker="EL GOL", nota=NOTA))

    # 04 — LA FIGURA: Agustín Ojeda (portada del jugador)
    slides.append(P.portada_jugador(
        d["figura"],
        etiqueta="El jugador del partido",
        subtitulo=d["figura_bajada"],
        teaser=d["figura_teaser"],
        nota=NOTA,
        foto=_resolver_foto(),
        foto_focal=d.get("figura_foto_focal", (0.8, 0.6)),
        foto_zoom=d.get("figura_foto_zoom", 1),
        foto_offset=d.get("figura_foto_offset", (0, 0)),
        escudo=_ruta(d.get("figura_escudo")),
        escudo_leyenda=d.get("figura_escudo_leyenda")))

    # 05 — LA FIGURA EN NÚMEROS
    slides.append(P.ficha(
        f"{d['figura'].split()[-1]} en números",
        "Su partido, dato por dato",
        d["figura_stats"],
        nota=NOTA, destacar=d.get("figura_destacar", "Gol")))

    # 06 — EL MEJOR 11 DE LA FECHA
    slides.append(P.ranking(
        d["once_titulo"], d["once_filas"],
        subtitulo=d["once_sub"], unidad="",
        nota=NOTA, destacar=d.get("once_destacar", 1), piso=d.get("once_piso", 7.0)))

    # 07 — EL MEJOR 11: el contexto
    if d.get("slot7_num"):
        slides.append(P.dato(
            d["slot7_num"], d["slot7_lab"], d["slot7_ctx"],
            kicker=d.get("slot7_kicker", "EL DATO"), nota=NOTA))
    else:
        slides.append(P.dato(
            "1", f"el jugador de Chaco en el Mejor 11 de la Fecha {d['fecha']} de la zona",
            d["once_ctx"], kicker="EL MEJOR 11", nota=NOTA))

    # 08 — CÓMO SALIÓ JUGANDO EL NEGRO: mapa de asociación
    if _ruta(d.get("mapa_asociacion")):
        slides.append(P.grafico_marca(
            _ruta(d["mapa_asociacion"]),
            "Cómo salió el Negro",
            d.get("mapa_asociacion_sub"),
            nota="Fuente: SofaScore"))

    # 09 — DÓNDE JUGÓ LA FIGURA
    if _ruta(d.get("figura_heatmap")):
        slides.append(P.grafico_marca(
            _ruta(d["figura_heatmap"]),
            f"Dónde jugó {d['figura'].split()[-1]}",
            d.get("figura_heatmap_sub"),
            nota="Fuente: SofaScore"))

    # 10 — EL ATAQUE: mucho más volumen que el rival (opcional)
    if d.get("arco_num"):
        slides.append(P.dato(
            d["arco_num"], d["arco_lab"], d["arco_ctx"],
            kicker=d.get("arco_kicker", "EL ATAQUE"), nota=NOTA))

    # 10b — ANÁLISIS: ¿por qué empatamos? (opcional: tramos, quiebre, segundo tiempo, goles)
    if d.get("tramos_filas"):
        slides.append(P.ficha(
            d["tramos_titulo"], d["tramos_sub"], d["tramos_filas"],
            nota=NOTA, destacar=d.get("tramos_destacar")))
    if d.get("quiebre_num"):
        slides.append(P.dato(
            d["quiebre_num"], d["quiebre_lab"], d["quiebre_ctx"],
            kicker=d.get("quiebre_kicker", "EL QUIEBRE"), nota=NOTA))
    if d.get("st_stats"):
        slides.append(P.ficha(
            d["st_titulo"], d["st_sub"], d["st_stats"],
            nota=NOTA, destacar=d.get("st_destacar")))
    if d.get("goles_hero"):
        slides.append(P.dato_vs(
            d["goles_hero"], d["goles_hero_sub"],
            col_izq=d["goles_izq"], col_der=d["goles_der"],
            kicker="LOS GOLES DEL EMPATE", franja=d.get("goles_franja"), nota=NOTA))

    # 11 — LA VALLA EN CERO
    slides.append(P.ficha(
        d["defensa_titulo"], d["defensa_sub"],
        d["defensa_stats"],
        nota=NOTA, destacar="Goles recibidos"))

    # 12 — EL PLAN DEL RIVAL
    if _ruta(d.get("heatmap_rival")):
        slides.append(P.grafico_marca(
            _ruta(d["heatmap_rival"]),
            d.get("rival_titulo", "El rival no pudo"),
            d["rival_tiros_lejos"],
            nota="Fuente: SofaScore"))

    # 13 — DÓNDE VIVIÓ CADA EQUIPO
    if _ruta(d.get("heatmap_equipo")):
        slides.append(P.grafico_marca(
            _ruta(d["heatmap_equipo"]),
            "Dónde vivió cada equipo",
            d.get("heatmap_equipo_sub"),
            nota="Fuente: SofaScore"))

    # 14 — EL PATRÓN: local vs visitante con Cravero (opcional)
    if d.get("patron_hero"):
        slides.append(P.dato_vs(
            d["patron_hero"], d["patron_hero_sub"],
            col_izq=d["patron_izq"],
            col_der=d["patron_der"],
            kicker="EL PATRÓN",
            franja=d["patron_franja"],
            nota=NOTA))

    # 15 — FICHA: dónde queda el equipo
    slides.append(P.ficha(
        d["tabla_titulo"], d["tabla_sub"],
        d["tabla_stats"],
        nota=NOTA, destacar="Prob. de descenso"))

    # 16 — CITA DE CIERRE
    slides.append(P.cita(
        d["cierre_frase"],
        autor="Lectura del partido", nota=None))

    return slides


def main():
    temas.aplicar("oscuro")     # post-partido: negro + dorado (la previa usa otra paleta)
    SALIDA.mkdir(parents=True, exist_ok=True)
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
