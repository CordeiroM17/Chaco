# -*- coding: utf-8 -*-
"""
Carrusel: "Asi llega el Negro a la mitad de la temporada 2026" (previa vs Acassuso).

Todos los numeros salen del informe de temporada (corte fecha 18/18):
outputs/temporadas/2026/informes/informe_temporada_fecha_18.md
Fuente de datos: SofaScore.

Genera las placas numeradas en placas/carrusel_mitad_temporada/.
    python scripts/carrusel_mitad_temporada.py
"""
from pathlib import Path
import placas as P
import marca as M

RAIZ = Path(__file__).resolve().parents[1]
PROYECTO = RAIZ.parents[1]
SALIDA = RAIZ / "placas" / "carrusel_mitad_temporada"
# graficos re-tematizados en la paleta de la marca (generados por graficos_marca.py)
FORMA = RAIZ / "assets" / "forma_reciente_ig.png"
VENTANA = RAIZ / "assets" / "goles_ventana_ig.png"
NOTA = "Temporada 2026 · 18 fechas · SofaScore"


def construir():
    slides = []

    # 01 — Portada (hook)
    slides.append(P.portada(
        "Así llega\nel Negro",
        "18 fechas jugadas. La radiografía de la primera mitad de la temporada, número por número. Deslizá →",
        etiqueta="Mitad de temporada 2026",
        nota="SofaScore"))

    # 02 — Ficha de estadísticas generales
    slides.append(P.ficha(
        "El Negro en números",
        "Corte a 18 de 18 fechas de la Primera Nacional",
        [("Posición", "18° de 18"),
         ("Puntos", "12"),
         ("Récord (V-E-D)", "2 - 6 - 10"),
         ("Goles (a favor - contra)", "13 - 24"),
         ("Diferencia de gol", "-11"),
         ("xG (creado - concedido)", "13.6 - 17.6")],
        nota=NOTA, destacar="Posición"))

    # 03 — forma reciente (tematizada en la marca, pedido del usuario)
    slides.append(P.grafico_marca(
        str(FORMA),
        "La forma, fecha a fecha",
        "Media móvil de puntos por partido a lo largo del año",
        nota=NOTA))

    # 04 — Los que más jugaron (minutos)
    slides.append(P.ranking(
        "Los que más jugaron",
        [("D. Valdez", 1505), ("A. Luque", 1465), ("M. Silvera", 1350),
         ("N. Caprio", 1214), ("G. Pacheco", 1207), ("B. Nievas", 1139)],
        subtitulo="Minutos jugados en la temporada",
        unidad="'", nota=NOTA, destacar=0))

    # 05 — Los mejor puntuados (rating)
    slides.append(P.ranking(
        "Los mejor puntuados",
        [("N. Caprio", 7.2), ("L. Marinucci", 7.1), ("A. Ojeda", 7.0),
         ("M. Silvera", 6.9), ("A. Lioi", 6.9), ("G. Pacheco", 6.9)],
        subtitulo="Rating promedio · mínimo de minutos jugados",
        nota=NOTA, destacar=0, piso=6.5))

    # 06 — En casa es otra cosa (el proximo partido es de local)
    slides.append(P.dato_vs(
        "75%", "de sus puntos los sacó de local",
        col_izq=("Local", "9 pts", "2-3-4"),
        col_der=("Visitante", "3 pts", "0-3-6"),
        kicker="EN CASA",
        franja="Y el próximo lo juega de local",
        nota=NOTA))

    # 07 — En qué minutos se define (primero la estadística, tematizado)
    slides.append(P.grafico_marca(
        str(VENTANA),
        "¿En qué minutos se define?",
        "Goles a favor y en contra por ventana de 15 minutos",
        nota=NOTA))

    # 08 — Lo que significa: el agujero del complemento
    slides.append(P.dato(
        "8", "goles recibidos entre el minuto 45 y 60",
        "Es el 35% de todo lo que recibió el Negro en el año. El arranque del segundo tiempo es el punto débil.",
        kicker="EL AGUJERO", nota=NOTA))

    # 09 — La lectura (cierre analítico)
    slides.append(P.cita(
        "Genera casi tanto peligro como recibe. Lo que le cuesta es aguantar: se le complica el arranque del segundo tiempo, no sostiene ventajas y de visitante no gana.",
        autor="La lectura", nota=NOTA))

    # 10 — Próxima fecha: Acassuso en casa (viene de ganar de local)
    slides.append(P.portada(
        "Ahora,\nAcassuso",
        "For Ever viene de ganar su último partido de local (1-0 a Colón) y ahora recibe a uno de los más flojos como visitante. A seguir la racha en casa.",
        etiqueta="Próxima fecha",
        nota="SofaScore"))

    return slides


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(construir(), 1):
        ruta = SALIDA / f"{i:02d}.png"
        M.guardar(img, ruta)
        print("OK", ruta.name)


if __name__ == "__main__":
    main()
