# -*- coding: utf-8 -*-
"""
Carrusel Cravero — VERSIÓN estilo_diario (papel + serif + filetes).

Es el MISMO contenido que `carrusel_cravero_riesgo.py` (el efecto Cravero: su
cosecha, la defensa, el once más usado, y lo que dice la simulación —descenso,
permanencia, Reducido— más los 3 gráficos del modelo), pero volcado a la
estética de recorte de diario en vez de la de "peligro de descenso". Así queda
la misma historia en las dos identidades de la cuenta.

    python scripts/graficos_cravero_marca.py     # genera la cancha (tema papel)
    python scripts/carrusel_cravero.py

------------------------------------------------------------------------------
DE DÓNDE SALEN LOS NÚMEROS (verificados, no de memoria):

TRAYECTORIA (prensa + Wikipedia):
- Jugador surgido de For Ever (1985-1991); campeón del Nacional B 1988/89 con el
  club. Después Platense, Lanús (Copa Conmebol 1996) y Gimnasia de Jujuy.
- DT del ascenso 2021: For Ever venció 1-0 a Gimnasia y Tiro en la final del
  Federal A en Santiago del Estero y volvió a la Primera Nacional tras 23 años
  (1998-2021). En ese playoff eliminó a Cipolletti en cuartos, por penales.
- Primer ciclo como DT terminó en 2022. Pasó por Guemes, Central Norte,
  Cipolletti (2025).
- 2026: cirugia a corazon abierto (~7 horas, Leben Salud, Neuquen). Dejo
  Cipolletti para operarse. Tras el alta, For Ever -ultimo- lo llamo.
  Anunciado el 16/17 de junio de 2026, en reemplazo de Pedro Llorens (que se
  fue tras la fecha 18, con el equipo ultimo). Debut: fecha 19, 5/7 vs Acassuso.

NUMEROS DEL CICLO (data/temporadas/2026/fixture.csv + lineups_clean.csv de los
28 partidos; scripts scratchpad cravero.py / xi.py):
- Antes de Cravero (fechas 1-18): 2-6-10, 12 pts, 0.67 ppg. GF 0.72/PJ,
  GA 1.33/PJ. 4 vallas invictas en 18. Visitante: 0 triunfos en 9 (3 pts/27).
  Ultimo del Grupo A.
- Con Cravero (10 fechas: 19, 20, 22, 23, 24, 25, 26, 21, 27, 28): 6-2-2,
  20 pts de 30, 2.00 ppg. GF 1.30/PJ, GA 0.50/PJ. 6 vallas invictas en 10.
  Local 4-1-0. Visitante 2-1-2 (las dos primeras de visitante del ano,
  seguidas: 3-1 a San Telmo y 1-0 a Colon).
- Con las ultimas 10 fechas solas, For Ever seria puntero del Grupo A.
- Puesto: 18/ultimo (fecha 18) -> 11, +4 sobre el descenso (fecha 28).
- Descenso Monte Carlo (Dixon-Coles, src/analysis/simulation.py): rondaba el
  30% cuando llego -> 1.8% tras la fecha 28.
- xG del pipeline: antes 0.75 xGF / 0.98 xGA por PJ; con Cravero 1.34 / 0.83
  (incluye la fecha 25 sin shotmap; sobre los 9 con datos ~1.49 xGF).

A QUIENES HACE JUGAR (xi.py, titularidades en sus 10 fechas):
- Once que mas se repite (4-4-2): Caprio; Luque, Valdez, Garay, Ojeda; Gaggi,
  Carrizo, Nievas, L. Fernandez; M. Romero, Pacheco.
- Del banco con peso: Cerrudo (asistencia + figura vs Estudiantes), Lioi,
  Diaz Chaves.
- Matias Romero volvio al club en el mercado de invierno: 6 goles en 8
  partidos, goleador y mejor promedio del ciclo (7.63).
- Ricardo Garay: de suplente (42 min/PJ antes) a titular fijo (86 min/PJ).
- Refuerzos de invierno que entraron de una: Enzo Gaggi (venia de una lesion)
  y Leandro Fernandez (10 titularidades, 2 asistencias).
- Caprio le gano el arco a Canuto desde la fecha 24: 4 partidos, 4 vallas
  invictas.
- Perdio lugar: Mathias Silvera (de 75 a 6 min/PJ).
- En la primera rueda For Ever probo 6 formaciones distintas; Cravero paro
  4-4-2 en 8 de 10.
------------------------------------------------------------------------------
"""
from pathlib import Path
import estilo_diario as D

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "placas" / "cravero_fecha_28"
NOTA = "Primera Nacional 2026 · Grupo A · fecha 28"
PROYECTO = RAIZ.parents[1]
ASSETS = RAIZ / "assets"
PROYECCION = PROYECTO / "outputs/temporadas/2026/global_grupo_a/liga/proyeccion"
NOTA_SIM = "Simulación Monte Carlo · 100.000 temporadas · Zona A"


def construir():
    s = []

    # 01 — Tapa
    s.append(D.portada(
        "El efecto Cravero",
        "De la zona roja\nal respiro",
        "El técnico del último ascenso volvió operado del corazón, agarró al "
        "Negro último y en diez fechas lo sacó de la pelea de abajo. Los "
        "números del giro.",
        nota=NOTA, centrado=True))

    # 02 — La trayectoria con el club
    s.append(D.tabla(
        "Toda una vida de Negro",
        "El técnico del último ascenso volvió y esta es su trayectoria",
        [("Debutó como jugador acá", "1985"),
         ("Campeón del Nacional B", "1988/89"),
         ("Volvió como DT y lo ascendió", "2021"),
         ("Fin del primer ciclo", "2022"),
         ("Cirugía a corazón abierto", "2026"),
         ("“Bienvenido a casa”", "jun. 2026")],
        kicker="La trayectoria", nota=NOTA,
        destacar="Volvió como DT y lo ascendió", centrado=True))

    # 03 — El ascenso
    s.append(D.dato(
        "23",
        "Los años que For Ever estuvo afuera de la Primera Nacional",
        "*De 1998 a 2021.* Cravero fue el DT que cortó esa espera: **1-0 a "
        "Gimnasia y Tiro** en la final del Federal A. En ese playoff, "
        "eliminó por penales a Cipolletti, el club que años después dirigiría.",
        kicker="El ascenso", nota=NOTA, centrado=True))

    # 04 — La vuelta
    s.append(D.dato(
        "7 horas",
        "Lo que duró la operación de corazón antes de volver",
        "A principios de 2026 dejó Cipolletti para operarse a corazón abierto. "
        "Apenas tuvo el alta, For Ever, **último en la tabla, sin técnico tras la "
        "salida de Pedro Llorens.** Debutó en la fecha 19.",
        kicker="La vuelta", nota=NOTA, centrado=True))

    # 05 — La cosecha
    #   resaltado inline: **frase** = negrita + rojo · *frase* = negrita sola
    s.append(D.dato(
        "20 de 30",
        "Los puntos de Cravero en diez fechas",
        "**Seis triunfos, dos empates, dos derrotas.** Llegó con el equipo último "
        "del Grupo A; hoy está **11°, cuatro puntos arriba del descenso**. Si "
        "el torneo se contara solo desde que asumió, For Ever *sería puntero "
        "de la zona*.",
        kicker="El ciclo", nota=NOTA, centrado=True))

    # 03 — La defensa
    s.append(D.dato(
        "0,50",
        "Goles en contra por partido",
        "Antes de que llegara, el Negro recibía *1,33* por partido: "
        "con él, la mitad de eso. *Seis vallas invictas en diez fechas*, cuando en "
        "las primeras dieciocho había sumado cuatro.",
        kicker="La defensa", nota=NOTA, centrado=True))

    # 04 — El once (gráfico de cancha, tema papel)
    s.append(D.grafico(
        str(ASSETS / "cravero_once_papel.png"),
        titulo="El once que más usó",
        subtitulo="*Los 11 que más repitió*, en su posición promedio "
                  "· en el arco, **Caprio por Canuto**",
        kicker="La formación", nota=NOTA))

    # 05 — Metodología de la simulación
    s.append(D.columna(
        "El Chango esta remontando",
        [
            "Nuestro modelo simuló 100.000 veces todo lo que queda del "
            "campeonato en la Zona A.",
            "Cada partido se resuelve según cuánto ataca y defiende cada equipo "
            "en 2026 —midiendo sobre todo por xG, el peligro generado, que es lo "
            "que mejor anticipa lo que viene—, no al azar.",
            "**Con esas 100.000 tablas finales se cuenta en cuántas Chaco "
            "descendió, en cuántas se salvó y en cuántas llegó al Reducido.**",
        ],
        kicker="La proyección", nota=NOTA_SIM, centrado=True))

    # 06 — Descenso
    s.append(D.dato(
        "1,8%",
        "Probabilidad de descenso",
        "Termina 17° o 18° de la Zona A en menos de 2 de cada 100 simulaciones. "
        "*Cuando Cravero asumió,* con el equipo último, ese riesgo rondaba el **30%.**",
        kicker="El riesgo", nota=NOTA_SIM, centrado=True))

    # 07 — Permanencia
    s.append(D.dato(
        "98,2%",
        "Probabilidad de mantener la categoría",
        "Es el complemento del descenso. **Faltan ocho fechas y la tabla se puede "
        "torcer**, pero la ventaja es clara: San Telmo, el primero abajo de la "
        "línea, está cuatro puntos atrás.",
        kicker="La permanencia", nota=NOTA_SIM, centrado=True))

    # 08 — Reducido
    s.append(D.dato(
        "10%",
        "Probabilidad de entrar al Reducido",
        "Para meterse en playoffs hay que terminar entre *2° "
        "y 8° de la zona*. El modelo le da una chance de **1 en 10** — a mediados de "
        "agosto era del **1%.**",
        kicker="El sueño", nota=NOTA_SIM, centrado=True))

    # 09 — Remate
    s.append(D.remate(
        "Lo trajeron para no descender. Diez fechas después, le cambio la cara al equipo y transmitió tranquilidad al hincha. Si se despega de la zona de descenso, "
        "el negro podria comenzar a mirar para arriba y soñar con el reducido.",
        firma="El Negro, fecha 28", nota=NOTA))

    # 10-12 — Los 3 gráficos del modelo, a pantalla casi entera (sin cabezal)
    for archivo in ("posicion_probabilidad.png", "distribucion_puntos.png",
                    "proyeccion_zona.png"):
        ruta = PROYECCION / archivo
        if ruta.exists():
            s.append(D.grafico_full(str(ruta), nota=NOTA_SIM,
                                    credito="El modelo completo"))
        else:
            print(f"!! falta {ruta} — corré primero generate_projection_graphics")

    return s


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(construir(), 1):
        D.guardar(img, SALIDA / f"{i:02d}.png")
        print("OK", f"{i:02d}.png")
    print("OK _preview.png ->", D.contact_sheet(SALIDA))


if __name__ == "__main__":
    main()
