# -*- coding: utf-8 -*-
"""
Carrusel de CURIOSIDAD: qué dice la simulación Monte Carlo sobre el riesgo de
descenso de Chaco For Ever (cierre Fecha 24, agosto 2026).

Primer post del tipo "curiosidad de alerta": mismo espíritu que
carrusel_sale_del_descenso.py (solo datos, sin análisis de partido, para
publicar entre fechas), pero con la estética NUEVA `estilo_riesgo.py`
(fondo blanco, franjas tipo cinta de peligro, rojo de alerta) en vez de la
de diario — se reserva para cuando el dato central es una alerta/riesgo.
Para el próximo post de este tipo: copiar este script, cambiar los números.

    python scripts/carrusel_curiosidad_montecarlo.py

------------------------------------------------------------------------------
DE DÓNDE SALEN LOS NÚMEROS:

Sección 7 (Proyección de la Tabla - Zona A) del informe de temporada,
outputs/temporadas/2026/global_grupo_a/liga/proyeccion/seccion_proyeccion.tex,
generada por el modelo de simulación de src/analysis/simulation.py:

  - 100.000 temporadas simuladas, 131 partidos restantes de Zona A.
  - Modelo de ataque/defensa tipo Poisson ajustado con los resultados y el xG
    de cada equipo en lo que va de 2026.
  - Posición final esperada de Chaco: 14.5° (mediana 15°).
  - Probabilidad de descenso (17°-18°): 23%.
  - Probabilidad de entrar al Reducido por posición (2°-8°): 1%.
  - Probabilidad de terminar 1° de zona (llegar a la final): 0%.
  - Probabilidad de mantener la categoría = 100% - 23% = 77% (complemento del
    descenso, no sale directo del modelo, se calculó a mano para la placa).

Alcance/límites (documentados en la fuente, van en la placa de explicación):
  - Solo cubre Zona A (18 equipos) — no incluye ascenso directo (final vs.
    Zona B) ni el ganador del Reducido, que dependen de datos de Zona B que
    hoy no están cargados (PLAN_montecarlo_tabla.md, Fase 2).
  - Confianza media/alta en la posición relativa, baja en el resultado exacto
    de un partido individual.
  - Rivales interzonales sin datos propios de Zona B se simulan con fuerza
    promedio de liga (aproximado).
------------------------------------------------------------------------------
"""
from pathlib import Path
import estilo_riesgo as R

RAIZ = Path(__file__).resolve().parents[1]
PROYECTO = RAIZ.parents[1]
PROYECCION = PROYECTO / "outputs/temporadas/2026/global_grupo_a/liga/proyeccion"
SALIDA = RAIZ / "placas" / "curiosidad_montecarlo_fecha24"
NOTA = "Simulación Monte Carlo · 100.000 temporadas · Zona A"


def construir():
    slides = []

    # 01 — Tapa: título de alerta con "DESCENSO" en rojo, sin bajada (más grande)
    slides.append(R.portada(
        "Lo que dice la simulación",
        [
            [("CHACO FOR EVER", R.NEGRO)],
            [("EN PELIGRO DE", R.NEGRO)],
            [("DESCENSO", R.ROJO)],
        ],
        nota=NOTA, centrado=True))

    # 02 — Explicación de la metodología, para el público general
    slides.append(R.explicacion(
        "¿Cómo se hizo esta proyección?",
        [
            "Un modelo estadístico simuló 100.000 veces todo lo que queda "
            "del campeonato: los 131 partidos que faltan de la Zona A.",
            "En cada simulación, cada partido se resuelve según qué tan bien "
            "ataca y defiende cada equipo esta temporada — con los goles y "
            "el xG (peligro generado) reales de 2026, no al azar.",
            "Con esas 100.000 tablas finales se cuenta en cuántas Chaco "
            "terminó descendido, en cuántas se salvó, y así con cada "
            "resultado posible. Eso es lo que ves en los próximos números.",
        ],
        nota=NOTA, centrado=True))

    # 03 — Posición final esperada
    slides.append(R.dato(
        "14.5°",
        "La posición final esperada de Chaco",
        "Es el resultado promedio de todo el modelo, no un pronóstico "
        "puntual de un solo escenario. La mediana da 15° — la mitad de los "
        "casos lo dejan en ese puesto o peor. Hoy está en la zona roja.",
        kicker="LA TENDENCIA", nota=NOTA, centrado=True))

    # 04 — Probabilidad de descenso (la de alerta)
    slides.append(R.dato(
        "23%",
        "Probabilidad de descenso",
        "Cerca de 1 de cada 4 escenarios termina con Chaco descendiendo — "
        "17° o 18° de la Zona A. Es más alto que al "
        "cierre de la Fecha 23, cuando el riesgo estaba en 22%.",
        kicker="EL RIESGO", alerta=True, nota=NOTA, centrado=True))

    # 05 — Probabilidad de mantener la categoría
    slides.append(R.dato(
        "77%",
        "Probabilidad de mantener la categoría",
        "Es el complemento directo del riesgo de descenso: en 77 de cada 100 "
        "casos, Chaco se queda en Primera Nacional. La ventaja todavía es clara",
        kicker="LO QUE QUEDA A FAVOR", nota=NOTA, centrado=True))

    # 06 — Probabilidad de entrar al Reducido
    slides.append(R.dato(
        "1%",
        "Probabilidad de entrar al Reducido",
        "Para pelearlo hace falta terminar entre 2° y 8° de la zona — una "
        "escalada de al menos nueve puestos desde donde está hoy. El "
        "modelo lo trata como un escenario marginal, casi de excepción.",
        kicker="EL SUEÑO LEJANO", nota=NOTA, centrado=True))

    # 07 — Probabilidad de ser 1° de zona
    slides.append(R.dato(
        "0%",
        "Probabilidad de terminar 1° de la Zona A",
        "Ni un solo escenario del modelo lo tuvo peleando el objetivo máximo "
        "de la zona. Con el arranque de temporada que tuvo, la distancia con "
        "la punta de la tabla es, hoy, insalvable.",
        kicker="DESCARTADO", nota=NOTA, centrado=True))

    # 08 — Cierre (da pie a los gráficos del modelo completo que siguen)
    slides.append(R.cierre(
        "Todavía quedan 131 partidos de la Zona A — la tabla se puede "
        "torcer. Pero hoy la simulación es clara: cada punto que se pierde "
        "de acá a fin de año pesa el doble. Después de esto, el modelo "
        "completo: probabilidad por equipo, distribución de puntos y "
        "proyección por zona",
        nota=NOTA, centrado=True))

    # 09-11 — Apéndice: las 3 figuras completas del modelo, tal cual salen del
    # pipeline (sin re-diagramar, el usuario las va a retocar aparte)
    apendice = [
        ("posicion_probabilidad.png"),
        ("distribucion_puntos.png"),
        ("proyeccion_zona.png"),
    ]
    for archivo in apendice:
        ruta = PROYECCION / archivo
        if ruta.exists():
            slides.append(R.grafico(
                str(ruta),
                kicker="EL MODELO COMPLETO", nota=NOTA, centrado=True))
        else:
            print(f"!! no encontrado: {ruta}")

    return slides


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    imgs = construir()
    for i, img in enumerate(imgs, 1):
        R.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    R.contact_sheet(SALIDA)
    print("OK _preview.png ->", SALIDA)


if __name__ == "__main__":
    main()
