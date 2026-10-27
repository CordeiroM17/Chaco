# -*- coding: utf-8 -*-
"""
Generador ESTÁNDAR de carrusel de refuerzo. Las 4 incorporaciones salen con el
mismo formato: se alimenta de la ficha de Transfermarkt que deja el notebook
en outputs/refuerzos/{slug}.json (bio, clubes, carrera, último club).

    python scripts/carrusel_refuerzo.py matias_romero

Estructura fija (6 placas):
  01 Portada con espacio para la foto
  02 La ficha (rol, edad, altura, pie, nacionalidad, valor)
  03 Su trayectoria (clubes)
  04 Su carrera en números
  05 Cómo llega (rendimiento en su último club)
  06 Bienvenida
"""
import sys, re, json
from pathlib import Path
import placas as P
import marca as M
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
PROYECTO = RAIZ.parents[1]
FICHAS = PROYECTO / "outputs" / "refuerzos"
TEMPORADA = "Temporada 2026"

# roles ofensivos: para decidir si el número estrella es goles o partidos
_ATAQUE = ("delanter", "extremo", "mediapunta", "punta", "9", "wing")
_JUVENIL = re.compile(r"\b(II|III|U\d{2}|S\d{2}|Sub|Reserva|Juvenil)\b", re.I)
_NEUTRO = {
    "Titular habitual": "Venía jugando siempre",
    "Rotativo (arranca o entra según el partido)": "Venía entrando y saliendo",
    "Poco rodaje: mayormente suplente": "Venía con pocos minutos",
    "Jugó pocos partidos": "Venía con pocos partidos",
    "No sumó minutos": "Casi no venía jugando",
}


def _fmt(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(n)


def _edad(nacimiento):
    m = re.search(r"\((\d+)\)", nacimiento or "")
    return m.group(1) if m else None


def _es_ataque(rol):
    r = (rol or "").lower()
    return any(k in r for k in _ATAQUE)


def _buscar_foto(carpeta, n):
    """Busca imagen_{NN}.(jpg/png/…) en la carpeta del refuerzo para ese slide."""
    for ext in ("jpg", "jpeg", "png", "webp", "JPG", "JPEG", "PNG"):
        p = carpeta / f"imagen_{n:02d}.{ext}"
        if p.exists():
            return str(p)
    return None


# Encuadre de la foto por slide. Por defecto va algo arriba (cara/torso), que
# deja fuera marcas de agua o carteles del PIE. Para fotos con texto ARRIBA
# (placas de bienvenida, fondos de entrevista) se centra/baja el encuadre.
_FOTO_DEF = {1: ((0.5, 0.32), 1.32), 3: ((0.5, 0.34), 1.30)}
_FOTO_AJUSTE = {
    "matias_romero":     {1: ((0.45, 0.8), 1.40)},                      # 01 la persona un poco más arriba
    "leandro_fernandez": {1: ((0.64, 0.15), 1.32), 3: ((0.50, 0.18), 1.30)},  # 01 a la izq · 03 más arriba
    "federico_moreno":   {1: ((0.80, 0.15), 1.32), 3: ((0.45, 1), 1.30)},  # 01 a la izq · 03 más arriba
    # tevez slide 3: imagen recuperada del placa (ya recortada) -> centrado en él.
    "mauricio_tevez":    {1: ((0.70, 0.30), 1.32),3: ((0, 0.45), 1.14)},
}


def _foto_args(fotos, n):
    f = fotos.get(n)
    if not f:
        return {"foto": None}
    return {"foto": f[0], "foto_focal": f[1], "foto_zoom": f[2]}


def construir(ficha, fotos=None):
    fotos = fotos or {}
    b = ficha["bio"]
    t = ficha.get("carrera_total") or {}
    uc = ficha.get("ultimo_club") or {}
    clubes = ficha.get("clubes") or []
    vuelve = ficha.get("es_retorno", False)
    ataque = _es_ataque(b.get("rol") or b.get("posicion"))
    nombre = b.get("nombre", "Refuerzo")
    primer = nombre.split()[0]
    rol = b.get("rol") or b.get("posicion") or "Jugador"

    goles = t.get("goles") or 0
    partidos = t.get("partidos") or 0
    asist = t.get("asistencias") or 0
    minutos = t.get("minutos") or 0

    goleador = ataque and goles >= 15      # el número estrella es 'goles' solo si convierte seguido
    slides = []

    # 01 — Portada con espacio para la foto
    teaser = (f"{goles} goles en su carrera" if goleador
              else f"{partidos} partidos en su carrera")
    slides.append(P.portada_jugador(
        nombre,
        etiqueta=("Vuelve al Negro" if vuelve else "Nuevo refuerzo"),
        subtitulo=(f"El {rol.lower()} {'vuelve a vestir' if vuelve else 'se suma a'} "
                   f"la camiseta de Chaco For Ever."),
        teaser=teaser,
        nota="Datos: Transfermarkt",
        **_foto_args(fotos, 1)))

    # 02 — La ficha
    filas = [("Rol", rol)]
    if _edad(b.get("nacimiento")):
        filas.append(("Edad", f"{_edad(b['nacimiento'])} años"))
    if b.get("altura"):
        filas.append(("Altura", b["altura"]))
    if b.get("pie"):
        filas.append(("Pie", b["pie"]))
    if b.get("nacionalidad"):
        filas.append(("Nacionalidad", b["nacionalidad"]))
    if b.get("valor_mercado"):
        filas.append(("Valor de mercado", b["valor_mercado"]))
    slides.append(P.ficha("La ficha", b.get("nombre_completo", nombre),
                          filas, nota="Transfermarkt", destacar="Rol"))

    # 03 — Su trayectoria (línea de tiempo con escudos, años y flechas)
    todas = []
    for s in ficha.get("trayectoria_detallada", []):
        logo = s.get("logo")
        todas.append({
            "club": s["club"],
            "anios": s.get("anios", ""),
            "es_chaco": s.get("es_chaco", False),
            "logo": str(PROYECTO / logo) if logo else None,
        })
    # sacar el club actual redundante al final: el destino (Chaco) o la vuelta
    # de un préstamo (mismo club "…-hoy" que ya figuraba antes en la carrera)
    if todas:
        ult = todas[-1]
        previos = {e["club"] for e in todas[:-1]}
        es_hoy = str(ult.get("anios", "")).endswith("hoy")
        if ult["club"] == "Chaco For Ever" or (es_hoy and ult["club"] in previos):
            todas = todas[:-1]
    # SIEMPRE 7 clubes: preferir senior; si hay menos de 7, completar con el resto
    senior = [e for e in todas if not _JUVENIL.search(e["club"] or "")]
    entradas = (senior if len(senior) >= 7 else todas)[-7:]
    if entradas:
        slides.append(P.trayectoria(
            "Su trayectoria", "Los clubes por los que pasó",
            entradas, nota="Transfermarkt", foto_zona=True, **_foto_args(fotos, 3)))
    else:  # respaldo si no hay trayectoria detallada
        slides.append(P.chips(
            "Su trayectoria", "Los clubes por los que pasó",
            grupos=[("Clubes", clubes)],
            destacados=(["Chaco For Ever"] if vuelve else []),
            nota="Transfermarkt", kicker="TRAYECTORIA"))

    # 04 — Su carrera en números
    if goleador:
        slides.append(P.dato(
            str(goles), "goles en su carrera",
            f"{partidos} partidos oficiales, {asist} asistencias y {_fmt(minutos)} minutos jugados.",
            kicker="SU CARRERA", nota="Transfermarkt"))
    else:
        slides.append(P.dato(
            str(partidos), "partidos en su carrera",
            f"{goles} goles, {asist} asistencias y {_fmt(minutos)} minutos jugados.",
            kicker="SU CARRERA", nota="Transfermarkt"))

    # 05 — Cómo llega (rendimiento en su último club)
    if uc and uc.get("club"):
        anios = uc.get("anios") or []
        anio_str = (str(anios[0]) if len(anios) == 1 else
                    (f"{anios[0]}-{anios[-1]}" if anios else ""))
        franja = _NEUTRO.get(uc.get("veredicto", ""), uc.get("veredicto", ""))
        slides.append(P.dato_vs(
            str(uc.get("minutos", 0)),
            f"minutos en su último club: {uc['club']} ({anio_str})",
            col_izq=("Partidos", str(uc.get("partidos", 0)), "jugados"),
            col_der=("Min/partido", f"{uc.get('min_por_partido', 0)}′", "promedio"),
            kicker="CÓMO LLEGA",
            franja=franja,
            nota="Transfermarkt"))

    # 06 — Bienvenida
    slides.append(P.portada(
        ("Bienvenido\nde vuelta" if vuelve else f"Bienvenido,\n{primer}"),
        (f"El Negro suma jerarquía y {'gol' if ataque else 'oficio'} para la "
         f"segunda mitad de la temporada."),
        etiqueta=TEMPORADA, nota="chacoforever.stats"))

    return slides


def _texto_publicacion(ficha):
    b = ficha["bio"]
    t = ficha.get("carrera_total") or {}
    uc = ficha.get("ultimo_club") or {}
    vuelve = "Chaco For Ever" in (ficha.get("clubes") or [])
    nombre = b.get("nombre", "El refuerzo")
    rol = (b.get("rol") or "").lower()
    L = []
    L.append(f"# Publicación — {'Vuelve' if vuelve else 'Refuerzo'}: {nombre}\n")
    L.append(f"**Formato:** carrusel estándar de refuerzo. En la placa 01, poné la foto en el recuadro.\n")
    L.append("## Texto del posteo\n")
    L.append(f"{'Vuelve al Negro. ' if vuelve else 'Nuevo refuerzo. '}🖤💛\n")
    L.append(f"{nombre}, {rol}, {'vuelve a' if vuelve else 'llega a'} For Ever. "
             f"Repasamos su ficha 👇\n")
    if t:
        L.append(f"📊 En su carrera: {t.get('partidos')} partidos, {t.get('goles')} goles "
                 f"y {t.get('asistencias')} asistencias.")
    if uc and uc.get("club"):
        L.append(f"⏱️ En {uc['club']}, su último club: {uc.get('partidos')} partidos "
                 f"y {uc.get('minutos')} minutos.")
    L.append("\n¿Qué esperás de él en el Negro? 👇\n")
    L.append("—\n📊 Datos: Transfermarkt\nCuenta de estadísticas hecha por hinchas. No oficial.\n")
    L.append("## Hashtags\n")
    L.append("#ChacoForEver #ElNegro #ForEver #Refuerzo #PrimeraNacional #Ascenso #Resistencia #Chaco")
    return "\n".join(L)


def main(slug):
    fp = FICHAS / f"{slug}.json"
    if not fp.exists():
        raise SystemExit(f"No encontré {fp}. Corré primero el notebook de refuerzos.")
    ficha = json.loads(fp.read_text(encoding="utf-8"))
    salida = RAIZ / "placas" / "refuerzos" / slug
    salida.mkdir(parents=True, exist_ok=True)
    fotos = {}
    for n in (1, 3):
        p = _buscar_foto(salida, n)
        if p:
            focal, zoom = _FOTO_AJUSTE.get(slug, {}).get(n, _FOTO_DEF[n])
            fotos[n] = (p, focal, zoom)
    imgs = construir(ficha, fotos)
    for i, img in enumerate(imgs, 1):
        M.guardar(img, salida / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    (salida / "texto_publicacion.md").write_text(_texto_publicacion(ficha), encoding="utf-8")
    # preview
    files = sorted(salida.glob("[0-9]*.png"))
    th = [Image.open(f).convert("RGB").resize((300, 300)) for f in files]
    cols = 3
    rows = (len(th) + cols - 1) // cols
    s = Image.new("RGB", (cols * 300 + (cols + 1) * 10, rows * 300 + (rows + 1) * 10), (45, 45, 45))
    for i, im in enumerate(th):
        r, c = divmod(i, cols)
        s.paste(im, (10 + c * 310, 10 + r * 310))
    s.save(salida / "_preview.png")
    print("OK _preview.png ·", salida)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "matias_romero")
