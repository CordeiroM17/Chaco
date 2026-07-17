# Informe de Temporada 2026 — Chaco For Ever

**Corte de datos:** 18 de 18 fechas jugadas y scrapeadas al 2026-07-01 (Primera Nacional, en curso).
**Alcance:** este informe analiza **exclusivamente la temporada 2026** — no se mezclan datos de 2025.

---

## 0. Nota metodológica (leer antes que el resto)

Al armar este informe se detectó una diferencia de un gol entre nuestros datos de eventos
(`incidents_clean`/`shotmap_clean`) y el resultado oficial en **un partido**:

> **27/03 vs Gimnasia de Jujuy (Local):** nuestros incidentes registraban originalmente 2 goles
> (Pacheco 79′ por Chaco, Gallardo 43′ por Gimnasia) → 1-1. El marcador oficial del evento dice
> **1-2** (derrota).

Se re-scrapeó este partido puntual y el hueco persistió en la fuente: se confirmó que **no es un
bug de nuestro scraper, sino un hueco en la fuente cruda de SofaScore** para ese partido en
particular (el JSON crudo de incidentes solo trae 2 goles, y las estadísticas oficiales del propio
partido muestran 4 tiros totales de Gimnasia, mientras que el shotmap solo tenía 3 cargados — a
SofaScore le falta un tiro/gol completo en su propio feed). No había más nada que bajar por esa vía.

**Corregido (2026-07-02):** ante la imposibilidad de obtener el evento real (jugador y minuto
exacto desconocidos), se agregó manualmente el gol faltante a `incidents_clean.csv` de ese
partido como evento **reconstruido y marcado explícitamente** (`incident_class="inferred_gap"`,
jugador "Desconocido", minuto estimado 85′ — entre el gol de Pacheco a los 79′ y el final del
partido, el único tramo posible dado el desglose oficial por período). Con este ajuste, el
pipeline recalcula automáticamente **2V-6E-10D, 12 pts, 13GF-24GC**, igual al `standings.csv`
oficial — ya no hace falta ninguna corrección manual en este informe. El shotmap de ese partido
sigue sin el tiro real (no se fabricó una ubicación en cancha inventada), así que las métricas
espaciales de xG/entropía de tiros de ese partido puntual subestiman levemente el volumen de
Gimnasia (1 tiro sobre el total de la temporada) — efecto marginal, documentado por transparencia.

---

## 1. Resumen ejecutivo

| | |
|---|---|
| Posición en la tabla | **18° de 18** (último) |
| Puntos | **12** en 18 fechas |
| Récord | 2 Victorias – 6 Empates – 10 Derrotas |
| Goles | 13 a favor – 24 en contra (diferencia **-11**) |
| xG (creado / concedido) | 13.59 a favor – 17.61 en contra |
| Local (9 pj) | 2V-3E-4D |
| Visitante (9 pj) | 0V-3E-6D — **no ganó ni un solo partido afuera** |

**La foto de la temporada en una frase:** Chaco genera casi tanto peligro como recibe en xG
(13.6 vs 17.6, no es una diferencia abismal), pero **no cierra partidos cuando se pone en
ventaja, se hunde en los primeros 15 minutos del segundo tiempo, y como visitante no gana
nunca** — el problema es tanto de gestión del partido como de nivel puro.

---

## 2. Tabla de resultados del análisis de datos

| Categoría | Hallazgo | Dato concreto | Lectura |
|---|---|---|---|
| **Gestión de ventajas** (cadena de Markov del marcador) | Ninguna ventaja se sostiene | Yendo ganando por 1: se diluyó el **100%** de las veces (3/3). Yendo ganando por 2+: el próximo gol del partido **siempre** fue del rival (100%, 1/1) | El equipo no tiene problema para ponerse arriba, tiene problema para **quedarse** arriba |
| **Momento del partido más peligroso** (goles por ventana de 15′) | El arranque del complemento es un agujero | **45′-60′: 8 goles en contra, 0 a favor** (34.8% de todo lo recibido en el año cae en esa ventana) | Algo pasa saliendo del entretiempo — concentración, ajuste rival, o arranque físico flojo |
| **Mejor ventana propia** | 60′-75′ es la mejor franja ofensiva | 4 goles a favor, solo 1 en contra en esa ventana | Coincide con el ingreso de suplentes / desgaste rival — la ventana a explotar con cambios |
| **De dónde vienen los goles en contra** (amenaza por tipo de jugada) | El grueso es en juego abierto, pero la pelota parada pesa | Juego abierto: 15 goles en contra / 10 a favor (11.3 vs 8.3 xG). Córner: 4 en contra, 0 a favor | Se concede desproporcionadamente en córners (0 goles propios de córner en toda la temporada) |
| **xG según estado del marcador** | Cuando va ganando, defiende mal la ventaja | Ganando: solo 79′ totales jugados en ese estado en TODA la temporada, y ya recibió 3 goles ahí (0.96 xG en contra en menos de un partido completo) | Muestra chica pero contundente — cada vez que se pone arriba, sufre casi de inmediato |
| **Entropía espacial del ataque** | Ataque bastante leíble | 1.655 / 4.644 bits (35.6% del máximo), n=171 tiros | El rival puede anticipar de dónde sale el peligro — no hay variedad de zonas de generación |
| **Núcleo táctico** (centralidad de eigenvector) | Sin sorpresas — el rendimiento sigue a los minutos | D. Valdez, A. Luque y M. Silvera lideran tanto minutos como centralidad | No hay ningún "diamante en bruto" que rinda muy por encima de sus minutos esta temporada |
| **Riesgo de colapso defensivo** (Cox, fatiga + momentum) | Sin señal estadística | HR≈1.00 en fatiga defensiva y en momentum rival (p>0.8 ambos) | Con 18 partidos la muestra es chica — no hay evidencia de que la fatiga acumulada acelere los goles en contra, al menos todavía |
| **Goleador y goles esperados** | Marinucci el goleador, pero sobre-rindiendo levemente | L. Marinucci: 4 goles / 2.47 xG. G. Pacheco: 3 goles / 2.93 xG | Marinucci convierte por encima de lo esperado; Pacheco rinde en línea con su xG |
| **Participación ofensiva** (toques en último tercio) | Pacheco y Marinucci concentran el circuito ofensivo | G. Pacheco: 64% de sus toques en el último tercio (130 dentro del área). Marinucci: 54.5% | El circuito ofensivo pasa mucho por dos jugadores — poca generación desde otras posiciones |
| **Disciplina** | Plantel con tarjetas altas en varios jugadores | L. Pruzzo (7A 1R en 13pj), B. Nievas (5A), D. Valdez (5A 1R) | Varios titulares habituales (Valdez, Nievas) rondan zona de riesgo de suspensión constantemente |
| **Descanso entre partidos** | Calendario sin sobrecargas evidentes | Descanso típico 6-7 días entre fechas, sin tramos de doble fecha semanal | La fatiga por calendario no parece ser un factor agravante (consistente con el Cox sin señal) |

*(Fuente de cada fila: `markov_marcador.png`, `goles_por_ventana_tiempo.png`, `amenaza_por_jugada.png`,
`xg_por_estado_marcador.png`, `entropia_tiros.png`, `nucleo_tactico.png`, `riesgo_defensivo_cox.png`,
`top_rating.png`/`top_minutos.png`, `toques_ultimo_tercio.png`, `disciplina.png`, `calendario_carga.png`
en `outputs/temporadas/2026/graficos/`.)*

---

## 3. Conclusiones e ideas para el cuerpo técnico

### Gestión del resultado (lo más urgente)
- **Trabajar específicamente el "cómo jugar arriba en el marcador"** en la semana: la cadena de
  Markov y el xG por estado del marcador cuentan la misma historia desde dos ángulos distintos —
  el equipo no sabe administrar una ventaja. Sugerencia concreta: ensayar en entrenamiento un
  cambio de estructura explícito al ponerse arriba (quién repliega, quién sostiene la pelota),
  no dejarlo librado a la lectura individual del partido.
- **Foco especial en los primeros 15 minutos del segundo tiempo.** Con 8 goles en contra y 0 a
  favor en el 45′-60′, esto no es casualidad — revisar en video qué instrucciones se dan en el
  entretiempo y cómo arranca físicamente el equipo esa franja. Vale la pena un protocolo de
  calentamiento/activación específico para la salida del vestuario.
- **Explotar el 60′-75′ con los cambios.** Es la mejor ventana ofensiva del año — tiene sentido
  planificar los ingresos de suplentes pensando en golpear justo ahí, en vez de esperar los
  últimos 10 minutos.

### Estilo ofensivo
- **Diversificar las zonas de generación.** La entropía de tiros (35.6% del máximo) confirma que
  el ataque es leíble. Sumado a que Pacheco y Marinucci concentran el grueso de los toques en
  el último tercio, el equipo depende de dos jugadores en circuitos parecidos. Trabajar
  variantes de ataque que no pasen siempre por las mismas zonas/jugadores.
- **Pelota parada defensiva es un problema puntual.** Se recibieron 4 goles de córner (0
  convertidos) — desproporcionado frente al resto de situaciones. Revisar marcas en córner en
  video antes de cada rival.
- **Marinucci sostiene el nivel goleador por encima de su xG** — vale la pena protegerlo de
  sobrecarga (ya acumula 4 amarillas en 15 partidos) porque es el jugador que más está
  convirtiendo por encima de lo esperado.

### Plantel y disciplina
- **Vigilar de cerca a Pruzzo, Nievas y Valdez** — los tres con acumulación alta de amarillas.
  Con Valdez además como uno de los jugadores con más minutos y mayor centralidad táctica
  (según el análisis de eigenvector), una suspensión suya pesaría más que la de otros.
- **No hay un "jugador oculto" para promover.** El análisis de núcleo táctico no encontró a
  nadie con bajo protagonismo y alto impacto — el rendimiento sigue de cerca a los minutos
  jugados. Esto sugiere que la rotación actual ya está usando a los jugadores más determinantes;
  el margen de mejora está más en el plan de juego que en cambios de nombres.

### Localía
- **Como visitante, el equipo no ganó ni un partido en 9 salidas** (0V-3E-6D) contra un
  2V-3E-4D de local. Esta brecha es más marcada que el diferencial de gol general — sugiere
  revisar específicamente el plan de juego de visitante (¿se juega distinto de local que de
  visitante? ¿el equipo necesita un enfoque más conservador/de contragolpe afuera?).

### Dato a seguir de cerca (no concluyente todavía)
- El modelo de riesgo defensivo (fatiga + momentum) no arrojó señal estadística — con 18
  partidos la muestra es chica. Vale la pena recalcular este modelo cuando la temporada tenga
  más fechas jugadas, porque si aparece una señal más adelante, sería un argumento objetivo
  para el preparador físico sobre rotaciones.

---

*Informe generado a partir del pipeline de análisis de datos de Chaco For Ever
(`notebooks/analisis_temporada.ipynb`), temporada 2026. Los gráficos de respaldo de cada
hallazgo están en `outputs/temporadas/2026/graficos/`.*
