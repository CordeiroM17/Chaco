# -*- coding: utf-8 -*-
"""
Carrusel ÚNICO de "la pelea de abajo", fusiona lo que antes eran dos posteos
sueltos (`carrusel_tabla_fecha29.py` y `carrusel_salvacion_chaco.py`) en un
solo arco narrativo de 4 placas:

  1) Tapa (gancho): ya hay 2 equipos salvados matemáticamente, pero para
     nosotros la pelea sigue hasta el final.
  2) Quiénes son esos 2 equipos salvados.
  3) Cuándo cae el primer descendido (Acassuso).
  4) Cuándo nos salvamos nosotros — y por qué no es un trámite.

Reemplaza a los dos carruseles sueltos anteriores para esta publicación; esos
scripts quedan igual por si hace falta reusar las placas individuales, pero
la salida de referencia para publicar es esta carpeta.

Estética: `estilo_diario.py` (papel + serif), igual que sus predecesores.

    python scripts/carrusel_pelea_permanencia.py

------------------------------------------------------------------------------
DE DÓNDE SALEN LOS NÚMEROS (sin cambios respecto a los scripts que fusiona):

- Tabla y fixture re-scrapeados el 16/09/2026.
- Placa 2: `src/analysis/simulation.points_bounds` — cotas matemáticas puras.
  Únicos 2 equipos con `estado_descenso == 'Matemáticamente salvado'`:
  Deportivo Morón y Ferro Carril Oeste (55 pts cada uno).
- Placa 3: `decision_round_distribution` para Acassuso (team_id=112491),
  Dixon-Coles, 50.000 sims, seed=42. prob_descendido=97.1%, fecha_mediana=34,
  distribución 32->0.1%, 33->18.5%, 34->39.1%, 35->31.2%, 36->11.0%.
- Placa 4: mismo modelo para Chaco (team_id=252726), filtrando el desenlace
  "salvado" (no lo devuelve la función pública, se reprodujo el bucle interno
  a mano). prob_salvado=95.7%, prob_descendido=2.1%, prob_sin_definir=2.2%,
  fecha_mediana_salvado=35, distribución (sobre el 95.7% que se salva):
  33->5.9%, 34->36.6%, 35->36.2%, 36->21.2%.
------------------------------------------------------------------------------
"""
from pathlib import Path
import estilo_diario as D

RAIZ = Path(__file__).resolve().parents[1]
ESCUDOS = RAIZ / "assets" / "escudos"
SALIDA = RAIZ / "placas" / "pelea_permanencia_fecha_29"
NOTA = "Primera Nacional 2026 · Zona A · Fecha 29"


def construir():
    slides = []

    # 01 — Tapa (gancho): ya hay 2 salvados, para nosotros sigue la pelea
    slides.append(D.portada_escudo(
        ESCUDOS / "chaco_for_ever.png",
        "Cómo está la tabla de abajo",
        "Ya hay 2 salvados.\n¿Y nosotros?",
        "*A 7 fechas del final, el campeonato ya tiene* **a los dos primeros **"
        "**equipos que se aseguraron la categoría**. Para el Negro, en cambio, "
        "la salvación todavía se juega partido a partido.",
        nota=NOTA))

    # 02 — Quiénes son los 2 equipos ya salvados
    slides.append(D.dato(
        "2",
        "Equipos ya matemáticamente salvados del descenso",
        "**Deportivo Morón y Ferro Carril Oeste,** *los dos punteros con 55 *"
        "*puntos,* quedaron afuera de la pelea por la permanencia pase lo que "
        "pase en las siete fechas que quedan. El año empieza a cerrarse "
        "también en el fondo de la tabla.",
        kicker="LOS PRIMEROS EN QUEDAR AFUERA", nota=NOTA, centrado=True))

    # 03 — Cuándo cae el primer descendido (Acassuso)
    slides.append(D.dato(
        "Fecha 34",
        "Cuándo el modelo ve el primer descenso cerrado",
        "**Acassuso es 18° con 23 puntos y tiene 98% de chances de descender. **"
        "Simulando 50.000 veces el resto del campeonato, en *4 de cada 10 *"
        "veces su descenso queda matemáticamente confirmado justo en la "
        "fecha 34, a dos fechas del final, y en el 89% de los casos lo "
        "estira para la 35.",
        kicker="EL PRIMER DESCENSO", nota=NOTA, centrado=True))

    # 04 — Cuándo (y con cuánta certeza) se salva Chaco: cierra el arco
    slides.append(D.dato(
        "95,7%",
        "Nuestra probabilidad de cerrar el descenso a favor",
        "El modelo nos da altas chances: *en 4 de cada *"
        "*10 simulaciones nos salvamos recién en la* **fecha 34**, en otras 4 "
        "de cada 10 en la **35**, y hay un 21% en que "
        "no se resuelve hasta la última fecha, la 36. Va a ser una pelea "
        "hasta el final.",
        kicker="Y NOSOTROS, ¿CUÁNDO?", nota=NOTA, centrado=True))

    return slides


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(construir(), 1):
        D.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    print("OK _preview.png ->", D.contact_sheet(SALIDA))


if __name__ == "__main__":
    main()
