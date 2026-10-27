# -*- coding: utf-8 -*-
"""
Dos placas SUELTAS de CURIOSIDAD DE TABLA para la semana de la fecha 30
(previa vs Almirante Brown). No es un carrusel de partido: son los dos hitos
de fondo de tabla que dejó la fecha 29, para publicar junto con (o cerca de)
la previa del rival.

Estética: `estilo_diario.py` (papel + serif), igual que
`carrusel_sale_del_descenso.py` y `carrusel_curiosidad_montecarlo.py` — así
no se confunde con la previa del partido (que usa el tema "hueso" de
placas.py/marca.py).

    python scripts/carrusel_tabla_fecha29.py

------------------------------------------------------------------------------
DE DÓNDE SALEN LOS NÚMEROS (todos verificados, no de memoria):

- Tabla y fixture re-scrapeados el 16/09/2026 (`fetch_standings` +
  `fetch_fixture`), después de la fecha 29 completa.

- Placa 1 (matemáticamente salvados): `src/analysis/simulation.points_bounds`
  con cotas matemáticas puras (piso/techo, independiente de la simulación).
  A esta altura (29 jugados, 7 por jugar) los únicos dos equipos con
  `estado_descenso == 'Matemáticamente salvado'` son Deportivo Morón y Ferro
  Carril Oeste, ambos con 55 puntos (1° y 2° de la Zona A).

- Placa 2 (primer descenso): `src/analysis/simulation.decision_round_distribution`
  para Acassuso (team_id=112491), modelo Dixon-Coles, 50.000 temporadas
  simuladas, seed=42. No es la probabilidad de descenso a fin de año (esa
  es ~97-98%, ya usada en otras placas) sino EN QUÉ FECHA se confirma
  matemáticamente. Resultado:
    prob_descendido=0.9706, prob_salvado=0.0153, prob_sin_definir=0.0141
    fecha_mediana=34
    distribución: 32->0.09%, 33->18.5%, 34->39.1%, 35->31.2%, 36->11.0%
  Es decir: la fecha más probable de confirmación matemática es la 34 (39%
  de las simulaciones), y para la fecha 35 ya está resuelto en el 89% de los
  casos acumulados.
------------------------------------------------------------------------------
"""
from pathlib import Path
import estilo_diario as D

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "placas" / "tabla_fecha_29_descenso"
NOTA = "Primera Nacional 2026 · Zona A · Fecha 29"


def construir():
    slides = []

    # 01 — Ya hay 2 equipos matemáticamente salvados del descenso
    slides.append(D.dato(
        "2",
        "Equipos ya matemáticamente salvados del descenso",
        "Deportivo Morón y Ferro Carril Oeste, los dos punteros con 55 "
        "puntos, quedaron afuera de la pelea por la permanencia pase lo que "
        "pase en las siete fechas que quedan. Con la fecha 29 jugada, el año "
        "empieza a cerrarse también en el fondo de la tabla.",
        kicker="LA TABLA SE CIERRA", nota=NOTA, centrado=True))

    # 02 — Cuándo se ve al primer descendido (probablemente Acassuso)
    slides.append(D.dato(
        "Fecha 34",
        "Cuándo el modelo ve el primer descenso ya sellado",
        "Acassuso es 18° con 23 puntos y tiene 98% de chances de descender. "
        "Simulando 50.000 veces el resto del campeonato, en 4 de cada 10 "
        "veces su descenso queda matemáticamente confirmado justo en la "
        "fecha 34 — a dos fechas del final — y en el 89% de los casos ya "
        "está sellado para la 35.",
        kicker="EL PRIMER DESCENSO", nota=NOTA, centrado=True))

    return slides


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(construir(), 1):
        D.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    print("OK _preview.png ->", D.contact_sheet(SALIDA))


if __name__ == "__main__":
    main()
