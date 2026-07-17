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
PARTIDO ARMADO ACÁ: Fecha 20 · San Telmo 1-3 Chaco For Ever (visitante)
Figura de la cancha: Matías Romero (rating 9.0, participó en los tres goles).
Números autoritativos del pipeline de informes (carpeta del partido):
  outputs/temporadas/2026/partidos/2026-07-11_vs_san_telmo_a/
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
    "fecha": 20,
    "local": "San Telmo",
    "visitante": "Chaco For Ever",
    "goles_local": 1,
    "goles_visitante": 3,
    "condicion": "visitante",                # 'local' o 'visitante'
    "resumen_marcador": "Tres goles en la Isla Maciel con el 32% de la pelota. Deslizá para el análisis.",
    # Escudos: por defecto salen de assets/escudos/<archivo>. Poné None para ocultar.
    "escudo_local": ESCUDOS / "san_telmo.png",
    "escudo_visitante": ESCUDOS / "chaco_for_ever.png",

    # ---- Ficha general del partido (destaca la FORMACIÓN) --------------------
    # Las columnas de la ficha van CHACO – RIVAL (aunque el Negro haya sido visitante).
    "formacion": "4-4-2",
    "formacion_rival": "4-3-3",
    "posesion": "32% – 68%",
    "xg": "1.85 – 0.76",
    "tiros": "12 (4) – 18 (6)",
    "corners": "4 – 4",
    "amarillas": "3 – 2",

    # ---- Figura de la cancha -------------------------------------------------
    "figura": "Matías Romero",
    "figura_rating": "9.0",
    "figura_bajada": "Metió dos goles y asistió el otro: los tres del Negro pasaron por él.",
    "figura_teaser": "tocó los 3 goles",
    # Ficha del jugador (etiqueta, valor). El rating se resalta en dorado.
    "figura_stats": [
        ("Rating (figura)", "9.0"),
        ("Goles", "2  ·  9′ y 89′ (penal)"),
        ("Asistencia", "1  ·  el 2-0 de Gaggi"),
        ("xG generado", "1.37"),
        ("Tiros al arco", "2"),
        ("Duelos aéreos ganados", "5"),
    ],
    # Heatmap de la figura, ya tematizado en la marca (fondo negro/dorado).
    # Lo genera scripts/graficos_partido_marca.py. None = se saltea la placa.
    "figura_heatmap": RAIZ / "assets/partido/heatmap_figura_ig.png",
    # Encuadre: Romero está en el centro-izquierda de la foto (cara en x≈0.49),
    # así que el recorte se centra en ese punto para que quede en el medio del marco.
    "figura_foto_focal": (0.47, 0.56),  # encuadre de la foto (x, y en 0..1)
    "figura_foto_zoom": 1.45,
    "figura_foto_offset": (-34, 18),    # correr la foto en píxeles: dx>0 derecha, dy>0 abajo

    # ---- El que lo habilitó: Leandro Fernández ------------------------------
    "refuerzo2": "Leandro Fernández",
    "refuerzo2_bajada": "Le puso el 1-0 a Romero: el que más generó con pelota",
    "refuerzo2_stats": [
        ("Asistencia", "1  ·  el 1-0 al 9′"),
        ("Rating", "7.0"),
        ("xA (asistencias esperadas)", "0.74"),
        ("Pases clave", "3"),
        ("Ocasiones claras creadas", "1"),
        ("Minutos", "69"),
    ],

    # ---- El arco: Canuto sostuvo el resultado --------------------------------
    "arquero": "Gaston Canuto",
    "arquero_bajada": "San Telmo remató 18 veces. Solo una terminó adentro",
    "arquero_stats": [
        ("Atajadas", "5"),
        ("Rating", "7.8"),
        ("Remates del rival", "18  ·  6 al arco"),
        ("Goles recibidos", "1"),
    ],

    # ---- Eficacia: menos pelota, mejores situaciones -------------------------
    "duo_hero": "1.85",
    "duo_hero_sub": "de xG con apenas el 32% de la pelota",
    "duo_franja": "Menos remates, muchísimo más peligro",

    # ---- El plan de San Telmo: tener la pelota y rematar de lejos ------------
    # Heatmap del rival tematizado (se genera con graficos_partido_marca.py).
    "heatmap_rival": RAIZ / "assets/partido/heatmap_rival_ig.png",
    "rival_tiros_lejos": "13 de los 18 remates de San Telmo salieron de afuera del área",

    # ---- El dato Markov: el gol en contra, otra vez en la misma franja -------
    "minuto_gol_contra": "46'",   # apóstrofo ASCII: la fuente del número gigante no tiene la prima ′
    "ventana_fragil": "45′–60′",
    "goles_ventana": 10,
    "markov_contexto": (
        "El modelo viene marcando la franja 45′–60′ como el agujero negro del equipo. "
        "San Telmo descontó al minuto de arrancar el segundo tiempo, otra vez ahí. "
        "Ya son 10 goles en contra en esa franja: el 38% de todo lo que For Ever recibió "
        "en el año. La diferencia es que esta vez el golpe no costó puntos."
    ),
    # Gráfico de goles por ventana, ya tematizado (scripts/graficos_marca.py).
    "grafico_ventana": RAIZ / "assets/goles_ventana_ig.png",

    # ---- Cierre --------------------------------------------------------------
    "cierre_frase": (
        "Ganó sin la pelota y ganó afuera. Cedió el balón, esperó y fue letal cuando llegó: "
        "tres goles con doce remates. La franja del segundo tiempo sigue abierta, pero esta vez "
        "el Negro la aguantó y se trajo los tres puntos."
    ),
}

# ==========================================================================
#  FOTO de la figura — dejá la ruta a la imagen o None para el marco reservado
# ==========================================================================
# Ej: FOTO_FIGURA = "C:/fotos/romero.jpg"
FOTO_FIGURA = None      # ← ponés acá la ruta a la foto del jugador del partido

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
    if FOTO_FIGURA:
        return FOTO_FIGURA
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

    # 02 — FICHA DEL PARTIDO (con la FORMACIÓN destacada)
    slides.append(P.ficha(
        "La ficha del partido",
        f"Chaco For Ever vs {RIVAL} · {_condicion_txt()}",
        [("Formación", d["formacion"]),
         ("Formación rival", d["formacion_rival"]),
         ("Posesión", d["posesion"]),
         ("xG (goles esperados)", d["xg"]),
         ("Tiros (al arco)", d["tiros"]),
         ("Córners", d["corners"]),
         ("Amarillas", d["amarillas"])],
        nota=NOTA, destacar="xG (goles esperados)"))

    # 03 — FIGURA DE LA CANCHA (portada del jugador con espacio para la foto)
    slides.append(P.portada_jugador(
        d["figura"],
        etiqueta="Figura de la cancha",
        subtitulo=d["figura_bajada"],
        teaser=d["figura_teaser"],
        nota=NOTA,
        foto=_resolver_foto(),
        foto_focal=d.get("figura_foto_focal", (0.8, 0.6)),
        foto_zoom=d.get("figura_foto_zoom", 1),
        foto_offset=d.get("figura_foto_offset", (1,9, 0))))

    # 04 — LA FIGURA EN NÚMEROS
    slides.append(P.ficha(
        f"{d['figura'].split()[-1]} en números",
        "Su partido, dato por dato",
        d["figura_stats"],
        nota=NOTA, destacar="Rating (figura)"))

    # 05 — HEATMAP DE LA FIGURA (gráfico con la marca, fondo negro)
    if _ruta(d.get("figura_heatmap")):
        slides.append(P.grafico_marca(
            _ruta(d["figura_heatmap"]),
            "Dónde jugó la figura",
            f"Mapa de calor de {d['figura'].split()[-1]}: vivió entre los centrales de San Telmo",
            nota="Fuente: SofaScore"))

    # 06 — EL QUE LO HABILITÓ: Leandro Fernández (asistió el 1-0)
    slides.append(P.ficha(
        d["refuerzo2"],
        d["refuerzo2_bajada"],
        d["refuerzo2_stats"],
        nota=NOTA, destacar="Asistencia"))

    # 07 — EL ARCO: Canuto sostuvo el 3-1
    slides.append(P.ficha(
        d["arquero"],
        d["arquero_bajada"],
        d["arquero_stats"],
        nota=NOTA, destacar="Atajadas"))

    # 08 — EFICACIA: menos pelota y menos remates, pero mucho más peligro
    slides.append(P.dato_vs(
        d["duo_hero"], d["duo_hero_sub"],
        col_izq=("Chaco", "12", "remates  ·  1.85 xG"),
        col_der=("San Telmo", "18", "remates  ·  0.76 xG"),
        kicker="EFICACIA",
        franja=d["duo_franja"],
        nota=NOTA))

    # 09 — EL PLAN DE SAN TELMO: tuvo la pelota, pero remató de lejos
    if _ruta(d.get("heatmap_rival")):
        slides.append(P.grafico_marca(
            _ruta(d["heatmap_rival"]),
            "El plan de San Telmo",
            d["rival_tiros_lejos"],
            nota="Fuente: SofaScore"))

    # 10 — EL DATO MARKOV: el descuento cayó otra vez en la franja frágil
    slides.append(P.dato(
        d["minuto_gol_contra"], "el minuto del descuento",
        f"El gol en contra volvió a caer en la franja {d['ventana_fragil']}, "
        f"la más frágil del equipo en todo el año.",
        kicker="EL DATO", nota=NOTA))

    # 11 — LA VENTANA NEGRA (gráfico de goles por ventana, Markov explicado)
    if _ruta(d.get("grafico_ventana")):
        slides.append(P.grafico_marca(
            _ruta(d["grafico_ventana"]),
            f"El agujero del {d['ventana_fragil']}",
            f"{d['goles_ventana']} goles recibidos ahí: el 38% de todo lo que recibió en el año",
            nota="Fuente: SofaScore"))

    # 12 — CITA DE CIERRE
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
