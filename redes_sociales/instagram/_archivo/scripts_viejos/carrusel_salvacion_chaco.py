# -*- coding: utf-8 -*-
"""
El ESPEJO de `carrusel_tabla_fecha29.py`: en vez de cuándo se confirma el
primer descenso (Acassuso), esto cuenta en qué fecha el modelo ve más
probable que Chaco quede matemáticamente salvado del descenso. Cierra el
arco de la semana: "cuándo baja el primero" + "cuándo se salva el Negro".

Estética: `estilo_diario.py`, igual que el resto de la serie de curiosidad de
tabla. La tapa usa la función nueva `portada_escudo()` (agregada a
estilo_diario.py) para centrar el escudo de Chaco.

    python scripts/carrusel_salvacion_chaco.py

------------------------------------------------------------------------------
DE DÓNDE SALEN LOS NÚMEROS:

Misma lógica que `src/analysis/simulation.decision_round_distribution`
(Dixon-Coles, 50.000 temporadas, seed=42, tabla/fixture re-scrapeados el
16/09/2026), pero mirando el desenlace `tipo==2` (salvado) en vez de
`tipo==1` (descendido) — la función pública solo devuelve la distribución de
descenso, así que estos números salen de reproducir el mismo bucle interno
filtrando por el otro desenlace (ver notas de la conversación, no hay script
de librería separado todavía):

  prob_descendido = 2.1%
  prob_salvado    = 95.7%
  prob_sin_definir = 2.2%   (ninguno de los dos umbrales se cierra en la
                              simulación; residual esperable, no es un bug)
  fecha_mediana_salvado = 35
  distribución (sobre el 95.7% que se salva):
    fecha 33 -> 5.9%
    fecha 34 -> 36.6%
    fecha 35 -> 36.2%
    fecha 36 -> 21.2%   (1 de cada 5 veces se define recién en la última fecha)
------------------------------------------------------------------------------
"""
from pathlib import Path
import estilo_diario as D

RAIZ = Path(__file__).resolve().parents[1]
ESCUDOS = RAIZ / "assets" / "escudos"
SALIDA = RAIZ / "placas" / "salvacion_matematica_chaco"
NOTA = "Primera Nacional 2026 · Zona A · Fecha 29"


def construir():
    slides = []

    # 01 — Tapa con el escudo de Chaco centrado
    slides.append(D.portada_escudo(
        ESCUDOS / "chaco_for_ever.png",
        "La otra mitad del cuento",
        "¿Cuándo se salva\nmatemáticamente\nel Negro?",
        "Ya vimos cuándo cae el primer descendido. Ahora la misma pregunta, "
        "pero para nosotros.",
        nota=NOTA))

    # 02 — El dato: fecha más probable de salvación matemática
    slides.append(D.dato(
        "95,7%",
        "Probabilidad de que el descenso se cierre a nuestro favor",
        "Simulando 50.000 veces lo que queda del campeonato, en 4 de cada 10 "
        "veces quedamos matemáticamente salvados en la **fecha 34** y en "
        "otras 4 de cada 10 recién en la **35**. Pero hay un 21%: 1 de cada 5 "
        "escenarios no se define hasta la última fecha, la 36.",
        kicker="LO QUE DICE EL MODELO", nota=NOTA, centrado=True))

    return slides


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(construir(), 1):
        D.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    print("OK _preview.png ->", D.contact_sheet(SALIDA))


if __name__ == "__main__":
    main()
