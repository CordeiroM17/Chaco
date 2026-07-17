  # Ideas nuevas: gráficos, informe PDF y grafo de relaciones — Chaco For Ever

Complementa (no repite) lo ya definido en `RECOMENDACIONES_INFORME_PARTIDO.md`, `DISENO_eventos_desde_tracking.md` y `SPRINT_2026-06-23.md`. Esos tres documentos ya resuelven bien la estructura del informe y el plan de la red de pases vía video — los doy por buenos y construyo arriba.

---

## 1. Informe de partido — ajustes al plan ya armado

La estructura de 6 páginas de `RECOMENDACIONES_INFORME_PARTIDO.md` está bien pensada (responde qué/cómo/quién/qué hacer). Dos sumas:

- **Versión de 1 página ("ficha de vestuario")** además de la de 6: marcador grande, xG, 3 frases de lectura, 4 recomendaciones, foto-resumen de posiciones. Para pegar en el vestuario o mandar por WhatsApp al cuerpo técnico el mismo día — la de 6 páginas para el análisis semanal.
- **Automatizar la exportación real a PDF.** El prototipo HTML que menciona el doc no quedó guardado en el repo (lo busqué, no está). En vez de Ctrl+P manual, conviene generar el PDF directo desde Python con **WeasyPrint** (`pip install weasyprint`): toma el mismo HTML/CSS que ya diseñaron (paleta, cards, saltos de página) y lo renderiza a PDF sin abrir navegador — `HTML(string=html).write_pdf(path)`. Encaja en `src/reports/post_match.py` como un paso final después del informe narrativo. Si prefieren no depender de un motor HTML, la alternativa más liviana es **ReportLab Platypus** (control más manual, sin CSS) directo sobre los PNG que ya genera `src/visualization/match.py`.

---

## 2. Gráficos nuevos — factibles HOY con lo que ya tienen (sin tocar video)

Todos usan datos que ya están bajados (`statistics`, `shotmap`, `lineups`, `incidents`, `heatmaps`, `average_positions`) en los 34 partidos de 2025. Ninguno inventa datos.

| Gráfico | De dónde sale | Por qué sirve |
|---|---|---|
| **Red de minutos compartidos** (ver sección 4) | `lineups` + `incidents` (subs/expulsiones) | Es el "grafo de relaciones" que pediste, real, disponible ya |
| **Mapa de tiros concedidos — temporada completa** | `shotmap` de los 34 partidos (lado rival) agregado en una sola cancha | Muestra desde dónde nos generan peligro todo el año: ¿por afuera del área o por dentro? ¿por una banda? Es el complemento defensivo del `shotmap_temporada.png` que ya tienen (ese es solo ofensivo) |
| **Amenaza por tipo de jugada** (`situation`: regular / set-piece / throw-in-set-piece / fast-break / penalty) | `shotmap.situation` (confirmé que el campo existe y tiene esos valores) | Cuántos goles/xG propios y en contra vienen de pelota parada vs juego abierto — accionable para entrenamientos de la semana |
| **Toques en último tercio / área rival por jugador** | `heatmaps` (x,y de cada toque, ya en coords OPTA 0-100) | No hace falta dato de pases para esto: contás qué % de los toques de cada jugador caen en x>66 (último tercio) o dentro del área rival. Mide participación ofensiva real sin necesitar la red de pases |
| **xG según estado del marcador** (ganando / igualando / perdiendo) | `shotmap.time` cruzado con goles de `incidents` | Responde "¿generamos cuando vamos arriba o nos replegamos de más?" — patrón de gestión de ventaja, algo que ya marcaron como problema en el partido vs Chacarita |
| **Forma reciente (rolling 5 partidos)** | `matches_index.csv` | El `puntos_acumulados.png` actual es acumulado de toda la temporada; un rolling de 5 muestra rachas — más útil para el cuerpo técnico semana a semana |
| **Local vs Visitante — panel comparado** | `matches_index.csv` + `statistics` | Puntos, xG a favor/contra, posesión, goles por condición — un patrón clásico que el cuerpo técnico siempre pregunta |
| **Disciplina acumulada** | `lineups` (tarjetas por jugador) | Quién está a una amarilla de suspensión, tendencia de faltas/tarjetas por partido — alerta operativa, no solo estético |
| **Calendario de carga (minutos + días de descanso)** | `event_clean` (fechas) + `lineups` (minutos) | Para preparador físico: quién acumula minutos sin descanso, candidatos a rotar |
| **Red de asistencias de temporada** (ya planeada como T4) | `incidents.assist1` | La sumo a la lista para que quede junto al resto: confirmo que `assist1` existe en los JSON crudos, el dato es real |

---

## 3. Qué información sumarle al entrenador / analista (no solo gráficos)

- **Alertas de amonestados** antes de cada partido (a una tarjeta de la suspensión).
- **Reporte de minutos/carga** semanal, no solo post-partido — ayuda a decidir rotaciones antes de que aparezca la lesión.
- **Ficha de pelota parada del próximo rival**: lado de los corners, quién pega los libres, % de goles de su equipo que vienen de ABP (ya scrapean rivales en `rivals_scraper.py`, el dato está a un paso).
- **"Qué cambiamos y qué pasó"**: cuando se prueba una formación o un cambio táctico distinto al partido anterior, comparar `posiciones_promedio` y `xg_tramos` de ambos partidos lado a lado — mide si el ajuste funcionó, no solo el resultado.
- **Patrón agregado de vulnerabilidad por tramos** (no solo por partido): si across los 34 partidos el rival genera más xG en el tramo 60'-75', por ejemplo, es una conclusión de temporada, no de un rival puntual — se arma agregando `xg_by_phase` de todos los partidos.

---

## 4. El grafo de pases / relaciones

### 4.1 Lo que ya está bien decidido (no lo toco)

Confirmé en los datos crudos lo mismo que ya concluyeron en `SPRINT_2026-06-23.md`: SofaScore no trae pases jugador→jugador (ni en `statistics`, ni en `average_positions`, ni en `graph.json` — este último es el momentum, no pases). La única red de pases **real** sale del tracking de video (plan T1→T6 ya armado, con `pass_events.csv` como contrato). Ese plan está bien armado, no le cambiaría nada.

### 4.2 Algo nuevo que pueden armar HOY: red de minutos compartidos

Un "grafo de relaciones" real y distinto a la red de asistencias, que no necesita pases ni video — mide con quién juega más tiempo cada jugador y si esas duplas rinden:

- **Nodos:** los 25-30 jugadores del plantel 2025. Tamaño = minutos totales en la temporada.
- **Aristas:** entre cada par de jugadores, minutos que estuvieron juntos en cancha simultáneamente (se calcula con `lineups.minutes_played` + horarios de entrada/salida que ya está en `incidents` para cambios y expulsiones — sin dato nuevo).
- **Color/grosor de la arista:** puntos por 90' (o diferencia de gol) del equipo en los minutos que esa dupla compartió cancha. Así no solo ves quién juega junto, ves qué duplas "rinden" cuando están juntas.
- **Librería:** `networkx` (ya está instalado en el venv) + `matplotlib` con la paleta `season.py` (`ACCENT_COLOR`/`RIVAL_COLOR`/`BG_COLOR`), layout `spring_layout` o posicionado por línea (defensa/medio/ataque) para que se lea como cancha.
- Encaja en `src/analysis/season.py` (cálculo) + `src/visualization/season.py` (dibujo), mismo patrón que ya usan.

Con esto tienen, sin esperar al tracking: **red de asistencias** (quién conecta con gol) + **red de minutos compartidos** (quién rinde junto). Cuando el pipeline de video cierre F1-F3, se suma la **red de pases real** como tercera capa — son complementarias, no se pisan.

---

## 5. Orden sugerido

1. Red de minutos compartidos + mapa de tiros concedidos de temporada (más rápido, mayor impacto, cero dependencias nuevas).
2. Amenaza por tipo de jugada + xG por estado del marcador (mismo nivel de esfuerzo, responden preguntas tácticas concretas).
3. WeasyPrint para automatizar el PDF del informe de partido.
4. Seguir el plan ya trazado de tracking → `pass_events.csv` (T1-T6) para la red de pases real.
