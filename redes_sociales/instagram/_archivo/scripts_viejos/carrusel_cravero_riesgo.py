# -*- coding: utf-8 -*-
"""
Carrusel Cravero — VERSIÓN estilo_riesgo (fondo blanco, cinta de peligro, rojo).
Es la misma idea que `carrusel_cravero.py` (estilo diario) pero probada con la
estética de la placa de "peligro de descenso", más el gráfico de cancha con el
11 más usado y las probabilidades de la simulación.

    python scripts/graficos_cravero_marca.py     # primero: genera la cancha
    python scripts/carrusel_cravero_riesgo.py

------------------------------------------------------------------------------
NÚMEROS (verificados):

Ciclo Cravero (fixture.csv + lineups de los 28 partidos; scratchpad cravero.py):
- 10 fechas (19, 20, 22, 23, 24, 25, 26, 21, 27, 28): 6-2-2, 20 pts de 30.
  Antes (fechas 1-18): 2-6-10, 12 pts (0.67 ppg).
- Goles en contra por partido: 1.33 antes -> 0.50 con Cravero.
- Vallas invictas: 4 en 18 -> 6 en 10.
- Puesto: 18/ultimo (fecha 18) -> 11, +4 sobre San Telmo (1er equipo bajo la
  linea) tras la fecha 28.
- Con las ultimas 10 fechas solas, For Ever seria puntero del Grupo A.

Once mas usado (scratchpad xi_pos.py): grafico assets/cravero_once.png,
generado por graficos_cravero_marca.py.

Simulacion Monte Carlo (src/analysis/simulation.py, Dixon-Coles, 100.000
temporadas, corrida el 2026-09-08 tras la fecha 28):
- Descenso (17-18 de Zona A):           1.83%  -> se muestra 1,8%
- Permanencia (complemento):            98,2%
- Reducido por posicion (2-8 de zona):  10,06% -> se muestra 10%
- Posicion media 11.8, mediana 12.
- A mediados de agosto (fecha 24) el descenso daba ~23-30% y el Reducido ~1%.
ALCANCE: cubre solo la Zona A; "Reducido" aca es terminar 2-8 por posicion, no
simula el cuadro del Reducido ni el ascenso directo (Fase 2).
------------------------------------------------------------------------------
"""
from pathlib import Path
import estilo_riesgo as R

RAIZ = Path(__file__).resolve().parents[1]
PROYECTO = RAIZ.parents[1]
ASSETS = RAIZ / "assets"
PROYECCION = PROYECTO / "outputs/temporadas/2026/global_grupo_a/liga/proyeccion"
SALIDA = RAIZ / "placas" / "cravero_fecha_28_riesgo"
NOTA = "Primera Nacional 2026 · Grupo A · fecha 28"
NOTA_SIM = "Simulación Monte Carlo · 100.000 temporadas · Zona A"


def construir():
    s = []

    # 01 — Tapa
    s.append(R.portada(
        "El efecto Cravero",
        [[("DE LA ", R.NEGRO), ("ZONA ROJA", R.ROJO)],
         [("AL RESPIRO", R.NEGRO)]],
        "El técnico del último ascenso volvió operado del corazón, agarró al "
        "Negro último y en diez fechas lo sacó de la pelea de abajo. Los "
        "números del giro.",
        nota=NOTA, centrado=True))

    # 02 — La cosecha
    s.append(R.dato(
        "20 de 30",
        "Los puntos de Cravero en diez fechas",
        "Seis triunfos, dos empates, dos derrotas. Llegó con el equipo último "
        "del Grupo A; hoy está 11°, cuatro puntos arriba del descenso. Si el "
        "torneo se contara solo desde que asumió, For Ever sería puntero de "
        "la zona.",
        kicker="El ciclo", nota=NOTA, centrado=True))

    # 03 — La defensa
    s.append(R.dato(
        "0,50",
        "Goles en contra por partido con Cravero",
        "Antes de que llegara, el Negro recibía 1,33 por partido. Con él, la "
        "mitad de eso: seis vallas invictas en diez fechas, cuando en las "
        "primeras dieciocho había sumado cuatro.",
        kicker="La defensa", nota=NOTA, centrado=True))

    # 04 — El once (gráfico de cancha)
    s.append(R.grafico(
        str(ASSETS / "cravero_once.png"),
        titulo="El once que más usó",
        subtitulo="Los 10 de campo que más repitió, en su posición promedio "
                  "real y con su dorsal · en el arco, Caprio le ganó el puesto "
                  "a Canuto",
        kicker="La formación", nota=NOTA, centrado=True))

    # 05 — Metodología de la simulación
    s.append(R.explicacion(
        "¿Qué dice la simulación?",
        [
            "Un modelo Dixon-Coles simuló 100.000 veces todo lo que queda del "
            "campeonato en la Zona A.",
            "Cada partido se resuelve según cuánto ataca y defiende cada equipo "
            "en 2026 —midiendo sobre todo por xG, el peligro generado, que es "
            "lo que mejor anticipa lo que viene—, no al azar.",
            "Con esas 100.000 tablas finales se cuenta en cuántas Chaco "
            "descendió, en cuántas se salvó y en cuántas llegó al Reducido.",
        ],
        kicker="La proyección", nota=NOTA_SIM, centrado=True))

    # 06 — Descenso
    s.append(R.dato(
        "1,8%",
        "Probabilidad de descenso",
        "Termina 17° o 18° de la Zona A en menos de 2 de cada 100 "
        "simulaciones. Cuando Cravero asumió, con el equipo último, ese "
        "riesgo rondaba el 30%.",
        kicker="El riesgo", alerta=True, nota=NOTA_SIM, centrado=True))

    # 07 — Permanencia
    s.append(R.dato(
        "98,2%",
        "Probabilidad de mantener la categoría",
        "Es el complemento del descenso. Faltan ocho fechas y la tabla se "
        "puede torcer, pero la ventaja es clara: San Telmo, el primero abajo "
        "de la línea, está cuatro puntos atrás.",
        kicker="La permanencia", nota=NOTA_SIM, centrado=True))

    # 08 — Reducido
    s.append(R.dato(
        "10%",
        "Probabilidad de entrar al Reducido",
        "Para meterse en la postemporada por posición hay que terminar entre "
        "2° y 8° de la zona. El modelo le da una chance de 1 en 10 — a "
        "mediados de agosto era del 1%.",
        kicker="El sueño", nota=NOTA_SIM, centrado=True))

    # 09 — Cierre
    s.append(R.cierre(
        "Lo trajeron para no descender. Diez fechas después, la simulación lo "
        "pone a pelear por otra cosa.",
        nota=NOTA, centrado=True))

    # 10-12 — Apéndice: los 3 gráficos del modelo completo, a pantalla casi
    # entera (sin cabezal, para que la imagen ocupe más). Regenerados tras la
    # fecha 28 con `liga.generate_projection_graphics('2026', n_sims=100000)`.
    for archivo in ("posicion_probabilidad.png", "distribucion_puntos.png",
                    "proyeccion_zona.png"):
        ruta = PROYECCION / archivo
        if ruta.exists():
            s.append(R.grafico_full(str(ruta), nota=NOTA_SIM))
        else:
            print(f"!! falta {ruta} — corré primero generate_projection_graphics")

    return s


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(construir(), 1):
        R.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    print("OK _preview.png ->", R.contact_sheet(SALIDA))


if __name__ == "__main__":
    main()
