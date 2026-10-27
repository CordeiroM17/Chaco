# Handoff: sistema de cuartiles de jugadores, líneas de equipo y cruce táctico

Documento para replicar y extender este análisis sobre el pipeline y los datos generales (multi-temporada / multi-torneo). Lo construido acá es una **muestra**: Primera Nacional 2026, 36 equipos, 520 partidos jugados hasta la fecha 29. El objetivo es que la misma lógica corra sobre el conjunto completo y se combine con el análisis de **estilos de juego** que ya existe del otro lado.

Los scripts de referencia están en `CompletoData/analisis/` (`etapa1_parseo.py` … `etapa9_cruce.py`). Son una implementación de referencia, no un producto; lo importante es la lógica descrita acá.

---

## 1. Qué se quiere lograr

1. Ordenar a cada jugador por cuartiles **dentro de su rol** (Q1 = 25% mejor) en (a) estadísticas individuales y (b) índices agrupados (defensa, construcción, creación, finalización, arquero, global).
2. Agregar por equipo y línea (arquero, zaga, laterales, medio, extremos, delanteros) y cruzar con la posición en la tabla y el rendimiento.
3. **Para un partido concreto:** dados dos equipos, decir dónde está la **brecha de plantel** por línea y **qué jugadores rivales atacar, presionar o vigilar**, y de cuáles cuidarse en el equipo propio. Esto se combina con el **estilo de juego** de ambos equipos.

Uso previsto: preparación de partido y diagnóstico. **No** como pronóstico del resultado (ver sección 6).

---

## 2. Flujo general

```
raw por partido (lineups.json, statistics, event, shotmap) + fixture + standings + roles
  │  Etapa 1  parseo y deduplicación  →  jugador-partido, equipo-partido
  │  Etapa 2  agregado por (jugador, equipo), ajuste por posesión, roles, corte dinámico
  │  Etapa 3  tasas p90 y % con contracción por rol (peso de confianza por estadística)
  │  Etapa 4  z-scores por rol → dimensiones → índice global → cuartiles
  │  Etapa 5  líneas por equipo, cuartiles entre equipos, tabla, cruce con resultados
  │  Etapa 7-8 validación (fuera de muestra, bootstrap, permutaciones, nivel partido)
  ▼  Etapa 9  informe de cruce: plantel + perfil de ocasiones + jugadores a atacar/presionar/vigilar
                 └── + módulo de ESTILOS de juego (ya existente; se integra en la sección 7)
```

---

## 3. Contrato de datos

### 3.1 Entradas mínimas
| Fuente | Campos usados |
|---|---|
| Lineups por partido (raw JSON) | por jugador: `minutesPlayed`, `goals`, `goalAssist`, `expectedGoals`, `expectedAssists`, `totalPass`/`accuratePass`, `totalLongBalls`/`accurateLongBalls`, `totalCross`/`accurateCross`, `totalOppositionHalfPasses`/`accurateOppositionHalfPasses`, `keyPass`, `touches`, `possessionLostCtrl`, `totalContest`/`wonContest`, `totalTackle`/`wonTackle`, `interceptionWon`, `totalClearance`, `ballRecovery`, `outfielderBlock`, `errorLeadToAShot`, `duelWon`/`duelLost`, `aerialWon`/`aerialLost`, `wasFouled`, `fouls`, `totalShots`, `onTargetScoringAttempt`, `saves`, `goodHighClaim`, `totalKeeperSweeper`/`accurateKeeperSweeper`, `rating`, posición (G/D/M/F), `substitute` |
| Estadísticas por partido | posesión, xG, remates, remates al arco (local y visitante) |
| Evento | `event_id`, fecha, ronda, ids y goles de local y visitante |
| Shotmap | `situation`, `bodyPart`, `xg`, `xgot`, `isHome` |
| Fixture | todos los partidos con estado (para tabla y control de cobertura) |
| Roles | rol fino por jugador y equipo: DFC, LAT, MCD, MC, EXT_MP, DC, ARQ (+ banda DER/IZQ) |

### 3.2 Reglas de higiene (cada una fue un error real en esta muestra)
1. **Un partido aparece dos veces** (en la carpeta de cada equipo). Deduplicar por `event_id` conservando la copia con `_scrape_state.updated` más reciente. ~0.5% de las filas difieren entre copias (ratings y algunos conteos se revisan después).
2. **El `teamId` dentro de cada jugador del raw NO es el club.** Asignar el equipo con el lado (local/visitante) y los ids del evento.
3. **Apariciones con minutos pero sin estadísticas (≈2.6%)**: excluirlas del numerador y del denominador de minutos.
4. **Conteos vacíos = 0** solo cuando la aparición tiene estadísticas (`interceptions`, `key_passes`, `saves`, etc. vienen vacíos cuando valen 0). `big_chances_*` y `goals_prevented` vienen vacíos en >97%: no usarlos.
5. **Nombres de equipo inconsistentes** (p. ej. "Gimnasia Jujuy" y "Gimnasia Y Esgrima De Jujuy" con el mismo `team_id`). Unir siempre por `team_id`.
6. **Jugadores que cambian de equipo**: la clave es `(player_id, team_id)`; no se suman minutos entre clubes.
7. **La tabla** se calcula desde el fixture con los partidos jugados al mismo corte que los datos (las tablas oficiales pueden ir una fecha adelante). Desempate: puntos, diferencia de gol, goles a favor, dentro de la zona.
8. **En el pool de scouting previo**, `zona` era "A" para todos, `pos_tabla` estaba mal y los `_p90` no coincidían con `conteo / minutos × 90`. Recalcular todo desde los conteos.
9. Pueden faltar partidos por suspensión o abandono (ej. San Martín SJ 27 partidos vs 29): normalizar por partidos jugados del equipo, no por fechas.

---

## 4. Método

### 4.1 Elegibilidad con corte dinámico
Un jugador entra a los rankings si `minutos ≥ max(180, 0.10 × partidos_del_equipo × 90)`. El piso crece con la temporada. En la muestra: 852 de 1142 jugador-equipo elegibles, que cubren entre 87% y 100% de los minutos de cada equipo (media 95%). Los jugadores no elegibles se conservan en los datos con la marca de tamaño de muestra.

### 4.2 Ajuste por posesión
Solo para acciones defensivas: tackles ganados y totales, intercepciones, despejes, recuperaciones, bloqueos y remates bloqueados.
`factor_partido = 50 / clip(100 − posesión_propia, 25, 75)`; se aplica a cada partido antes de sumar. Si falta la posesión, el factor es 1.

### 4.3 Tasas y contracción por confianza (el "corte dinámico ponderado")
Además del piso, cada estadística se contrae hacia el promedio de su rol según el ruido que tiene con esos minutos. Se hace por rol y por estadística:

- **Tasas por 90:** `r_i = Σstat / Σmin × 90`.
  - `μ` = media ponderada por minutos del rol (jugadores con ≥90').
  - `σ²` = varianza partido a partido de la tasa por 90, ponderada por minutos y agrupada (jugadores con ≥3 partidos de ≥20').
  - `ruido_i = σ² × 90 / minutos_i`.
  - `τ² = max(var_entre_jugadores − ruido_medio, 0.03 × var_entre_jugadores)`.
  - **Peso de confianza** `w_i = τ² / (τ² + ruido_i)`; valor suavizado `r_i* = μ + w_i × (r_i − μ)`.
- **Porcentajes** (éxitos / intentos): modelo beta-binomial; `k = p̄(1−p̄)/τ² − 1` acotado a [3, 1500] (1500 si τ²≤0); `p* = (éxitos + k·p̄) / (intentos + k)`; `w = intentos / (intentos + k)`.
- **Confianza del jugador** = promedio de sus `w` (0 a 1).

Los cuartiles y los índices usan siempre el valor **suavizado**. El dato crudo se muestra aparte.

Validación de la contracción (partidos pares vs impares): pesos del modelo vs fiabilidad medida → duelos aéreos 0.72 vs 0.74, toques 0.71 vs 0.79, xA 0.26 vs 0.38, tackles 0.29 vs 0.41. Calibración razonable; intercepciones queda algo optimista y xG/remates algo pesimista.

### 4.4 Estadísticas
- **Tasas p90:** tackles ganados (aj.), intercepciones (aj.), despejes (aj.), recuperaciones (aj.), bloqueos (aj.), duelos aéreos ganados, duelos terrestres ganados (`duelWon − aerialWon`), faltas (−), errores que terminan en tiro (−), pases precisos, pelotas largas precisas, pases precisos en campo rival, pérdidas (−), toques, pases clave, xA, asistencias, regates ganados, centros precisos, faltas recibidas, xG, remates, remates al arco, goles, atajadas y salidas altas (arquero).
- **Porcentajes:** pase, pelota larga, centro, pase en campo rival, regate, tackle, duelo aéreo, duelo terrestre, salidas del arquero.
- **Arquero:** goles evitados por partido = `(xGOT enfrentado − goles recibidos) / exposición`, prorrateado por la fracción de minutos del arquero en cada partido; ruido por partido σ²=1.
- (−) = menor es mejor.

### 4.5 Índices por dimensión y rol
z-score de cada columna suavizada contra los elegibles del rol; promedio ponderado por dimensión; luego se re-estandariza.

| Dimensión | Componentes (peso) |
|---|---|
| Defensa | tackles ganados aj. (1), intercepciones aj. (1), recuperaciones aj. (1), despejes aj. (.7), bloqueos aj. (.7), % aéreo (1), % terrestre (1), % tackles (.5), errores→tiro (−1), faltas (−.5) |
| Construcción | % pase (1), pases precisos (.7), pases precisos en campo rival (1), % pelota larga (.5), pérdidas (−.7) |
| Creación | xA (1), pases clave (1), asistencias (.4), regates ganados (.7), % regates (.3), centros precisos (.5), faltas recibidas (.3) |
| Finalización | xG (1), remates al arco (.7), remates (.5), goles (.7) |
| Arquero | goles evitados (1.5), salidas altas (.5), % pase (.5), % pelota larga (.5), % salidas (.5), errores→tiro (−1) |

**Índice global por rol (pesos de las dimensiones):**

| Rol | Pesos |
|---|---|
| DFC | defensa .65, construcción .35 |
| LAT | defensa .35, construcción .20, creación .45 |
| MCD | defensa .40, construcción .40, creación .20 |
| MC | defensa .20, construcción .30, creación .35, finalización .15 |
| EXT_MP | creación .45, finalización .35, construcción .10, defensa .10 |
| DC | finalización .60, creación .20, construcción .10, defensa .10 |
| ARQ | arquero 1.0 |

Los pesos por rol son decisiones de criterio, no estimados. Son parámetros a revisar con más datos.

**Cuartil:** percentil entre los elegibles del rol; `Q = 5 − ceil(percentil × 4)`, así Q1 = 25% mejor. En estadísticas donde menos es mejor se invierte el signo antes.

### 4.6 Líneas de equipo
Promedio del índice global de los jugadores elegibles de la línea, ponderado por minutos, y cuartil entre equipos:

| Línea | Roles |
|---|---|
| Arquero | ARQ |
| Zaga | DFC |
| Laterales | LAT |
| Medio | MCD + MC |
| Extremos | EXT_MP |
| Delanteros | DC |
| Defensa (conjunto) | 0.20 × Arquero + 0.80 × (DFC + LAT) |
| Ataque (conjunto) | MC + EXT_MP + DC |
| Global | .15 Arquero + .35 (DFC+LAT) + .25 (MCD+MC) + .25 Ataque |

También se guarda la composición de cada línea: % de minutos jugados por jugadores Q1, Q2, Q3 y Q4.

### 4.7 Perfil de ocasiones del equipo (desde shotmap)
xG por partido a favor y en contra, sin penales ni autogoles, separado en juego abierto (`regular`), pelota parada (`corner`, `set-piece`, `free-kick`), saque lateral con jugada (`throw-in-set-piece`) y de cabeza. Percentil entre equipos.

---

## 5. Resultados de la muestra y su nivel de confianza

Todo con n = 36 equipos y una sola temporada. IC95% por bootstrap (10 000), p por permutación, Holm por comparaciones múltiples.

### 5.1 Afirmaciones sostenibles
| Afirmación | Evidencia | Confianza |
|---|---|---|
| Mejor plantel (índice global) → más puntos por partido | Temporada completa r = 0.63 (IC 0.37–0.81, p_Holm = 0.001). **Fuera de muestra**: índice con la 1ª mitad predice los puntos de la 2ª, r = 0.51 (IC 0.25–0.71); puntos de la 1ª predicen la 2ª con r = 0.30 | Alta |
| Tamaño del efecto | Tercio de equipos con mejor plantel vs peor: +0.45 pts/partido (IC +0.28 a +0.61), ≈ +13 pts en 29 fechas; 93% de probabilidad de que uno del tercio alto supere a uno del bajo | Media-alta |
| La brecha está sobre todo abajo | Solo 8% del tercio bajo termina en la mitad superior; tercio medio y alto son casi iguales | Media |
| Un hueco en una línea cuesta puntos | 0 líneas en Q4: 1.50 pts/partido; 1 o más: 0.98–1.16 (grupos chicos, agrupación posterior) | Baja (pista) |

### 5.2 Lo que NO se sostiene
- **Qué línea pesa más:** defensa, medio y ataque están correlacionadas (ρ ≈ 0.65–0.67); con 36 equipos no se separan y combinarlas no mejora a la mejor línea en validación cruzada.
- **Zaga o defensa → goles en contra:** IC incluyen el cero (zaga r = −0.18; defensa vs xG en contra r = −0.19).
- **Circularidad:** el r = 0.88 del ataque con el xG a favor y el r = −0.67 del arquero con los goles en contra están inflados por construcción (el índice incluye xG y goles evitados). Sin esos componentes bajan a 0.66 y −0.38; fuera de muestra, ataque → xG a favor r = 0.51 y arquero → goles en contra r = −0.25 (IC incluye 0). Citar solo los valores fuera de muestra.
- **Pronóstico de un partido concreto:** con los 251 partidos de la 2ª mitad y el índice de la 1ª, ningún modelo (localía, tabla, xG, plantel) mejora demostrablemente a la localía sola (acierto 50% vs 51% eligiendo siempre "gana local"; mejora de log-loss 0.022, IC −0.008 a +0.051). Hay señal chica: correlación con la diferencia de goles del partido r = 0.22 (IC 0.11–0.33). Con brecha de plantel grande gana el fuerte 48%, empata 29%, gana el débil 24%.
- **El índice no supera al rendimiento propio del equipo** para predecir la diferencia de xG de la 2ª mitad (29% del xG propio vs 1% del plantel).

### 5.3 Estabilidad de los rasgos (qué se puede usar para preparar un partido)
Correlación entre 1ª y 2ª mitad de la temporada, 36 equipos:

| Rasgo | r | Uso |
|---|---|---|
| xG a favor juego abierto | 0.46 | Sí |
| xG en contra juego abierto | 0.40 | Sí |
| Posesión media | 0.50 | Sí |
| Diferencia de xG total | 0.61 | Sí |
| xG pelota parada a favor / en contra | 0.20 / 0.11 | **No** |
| xG de cabeza a favor | 0.01 | **No** |
| xG saque lateral con jugada | −0.35 / 0.30 | **No** |

A nivel jugador, confianza media (titulares ≥1500'): % pase 0.87, faltas recibidas 0.76, pérdidas 0.71, regates 0.69, % duelos terrestres 0.68, recuperaciones 0.66, despejes 0.56, faltas 0.55, % aéreo 0.53, centros 0.47, pases clave 0.41, intercepciones 0.33, **% tackles 0.08**. Regla de uso: solo estadísticas con confianza ≥ 0.5.

---

## 6. Límites que hay que respetar
1. **Correlación, no causalidad.** Un equipo que gana infla las estadísticas de sus jugadores; el diseño fuera de muestra lo reduce, no lo elimina.
2. **Las estadísticas de ataque y construcción no están ajustadas por estilo** (un medio con mucha posesión acumula más pases). Solo la parte defensiva se ajustó por posesión. Este es uno de los puntos donde el análisis de estilos aporta.
3. **El rol es fijo por temporada** aunque el jugador rote.
4. **No hay alineación confirmada, lesiones ni suspendidos:** por eso no sirve para pronosticar un partido puntual.
5. **No hay pressing, formación ni tracking** en los datos: todo hallazgo es una hipótesis a confirmar con video.
6. Los pesos por rol y por dimensión son criterio, no estimación.

---

## 7. Informe de cruce de partido (lo que se quiere producir)

Entrada: dos equipos (propio y rival). Salida: un documento con:

1. **Panorama:** posición, puntos, GF/GC, xG a favor/en contra, posesión.
2. **Brecha de plantel por línea:** z y cuartil de cada equipo. Se marca ventaja solo si la diferencia supera **0.35 desvíos** (menos es ruido).
3. **Perfil de ocasiones:** juego abierto (usar); pelota parada y cabeza (mostrar con la advertencia de baja estabilidad).
4. **Estilo de juego de ambos equipos** (*módulo existente; ver 7.2*).
5. **Jugadores del rival:**
   - **Atacar / explotar:** titulares (≥700') en Q4 de estadísticas defensivas relevantes con confianza ≥0.5 (duelos aéreos/terrestres, recuperaciones, faltas, errores→tiro).
   - **Presionar:** jugadores de salida (centrales, volante defensivo, arquero) en Q4 de % pase o pérdidas, con alta participación (toques).
   - **Vigilar / cuidarse:** jugadores en Q1 de estadísticas de amenaza (pases clave, xA, regates, faltas recibidas, xG) con confianza ≥0.5.
6. **Jugadores propios:** las mismas listas (fortalezas y puntos a cubrir).
7. **Cruces de banda:** extremo rival por una banda contra el lateral propio del lado opuesto, y a la inversa.
8. **Alerta de desvío:** diferencia entre goles y xG (a favor y en contra) para detectar equipos que rinden por encima o por debajo de lo que generan.

Reglas fijas del informe: titulares ≥700', confianza ≥0.5, tope de 14 ítems por lista, y una nota de estabilidad de cada rasgo.

### 7.1 Ejemplo (muestra)
Chaco For Ever vs Ciudad de Bolívar (26/09, visitante): Chaco supera al rival en zaga, laterales, extremos y delanteros (rival en Q4 en todas); el medio es lo contrario (−0.75, Q4, contra −0.19, Q3). Puntos de presión: Elías Martínez (central, % pase Q4, confianza 0.90) y Nahuel Yeri (volante, pérdidas Q4, 0.77). Alerta: el rival concede 1.26 de xG por partido pero recibe 0.90 goles. Informe completo en `output/cruce_chaco_for_ever_vs_ciudad_de_bolivar.md`.

### 7.2 Integración con el módulo de estilos (a resolver en la implementación)
El análisis de estilos ya existente debe entrar como **contexto que modula las recomendaciones**, no como un tercer índice suelto. Interfaz mínima:

- **Tabla de estilo por equipo**: `team_id` + variables numéricas (posesión, directividad/pelota larga, amplitud/centros, ritmo, intensidad de presión, dependencia de pelota parada, transiciones) + etiqueta de perfil si existe.
- **Control de estabilidad de cada variable de estilo** (correlación 1ª vs 2ª mitad ≥ ~0.4); las que no repitan se marcan y no se usan para recomendar.
- **Reglas de cruce** que combinan estilo y plantel, por ejemplo:
  - Rival de salida corta con central o pivote en Q4 de % pase / pérdidas → **presionar** a esos jugadores.
  - Rival directo (mucha pelota larga) con centrales en Q1 aéreo → no disputar el juego aéreo; con centrales en Q4 → sí buscarlo.
  - Extremo rival en Q1 de regates/faltas recibidas contra lateral propio en Q4 de duelos terrestres → **ayuda** o repliegue por esa banda.
  - Nuestro medio en Q4 contra un medio rival en Q1/Q2 y estilo de posesión alta del rival → **evitar** el duelo en el centro / reforzar la línea.
- Las reglas son **hipótesis** y deben validarse (sección 8.4) antes de darles peso de decisión.

---

## 8. Cómo aplicarlo a los datos generales

### 8.1 Adaptaciones
1. **Fuente de roles:** sustituir el pool de scouting por la clasificación de roles propia. Definir el rol por posición media y zona de juego si no hay una fuente.
2. **Corte dinámico:** el parámetro (10% de minutos posibles, piso de 180') se puede recalibrar por liga; la contracción es la que hace el trabajo fino.
3. **Contracción por liga y por temporada:** estimar `μ`, `σ²`, `τ²` por rol y competencia. Con varias temporadas se pueden estimar también con datos históricos del jugador (prior por jugador, no solo por rol).
4. **Ajuste por posesión:** revisar si se extiende a las acciones de ataque y construcción, o si se sustituye por un control por estilo del análisis existente.
5. **Nombres y ids:** normalizar por `team_id` desde el principio.

### 8.2 Con más temporadas, lo que en esta muestra no se pudo
- **Separar el peso de cada línea** en el resultado (aquí las líneas están colineales con n=36).
- **Estimar los pesos de las dimensiones por rol** en lugar de fijarlos por criterio.
- **Modelo a nivel partido** con brecha de plantel + estilo + localía (aquí 251 partidos no alcanzan para detectar mejoras chicas).
- **Validación fuera de muestra por temporada**, no solo por mitad de temporada.

### 8.3 Salidas esperadas
| Archivo | Contenido |
|---|---|
| `jugadores_temporada_completo` | id, equipo, rol, banda, minutos, elegible, confianza, rating, z e índices por dimensión, percentiles, cuartiles de cada estadística, valores crudos y suavizados |
| `jugadores_ranking_por_rol` | versión compacta de los elegibles: cuartil global y por dimensión |
| `equipos_lineas_cuartiles` | por equipo: tabla, z y cuartil por línea, composición por cuartil, cobertura de minutos |
| `correlaciones_lineas_vs_tabla`, `afirmaciones_...`, `prediccion_1a_a_2a_mitad` | resultados de validación con IC y p |
| `cruce_<equipo>_vs_<rival>.md` | informe de partido (sección 7) |

### 8.4 Pruebas de aceptación (para verificar que la implementación reproduce la muestra)
- 520 de 520 partidos jugados con datos; una sola copia por `event_id`.
- Suma de minutos elegibles por equipo entre 87% y 100% de `partidos × 990`.
- `_p90` = `conteo / minutos × 90` con diferencia máxima ≈ 0.
- Tabla calculada desde el fixture coincide con la oficial en los equipos con los mismos PJ (en la muestra: 20 de 21).
- Correlación del índice global con el rating de la fuente (no entra al índice) por rol: 0.47 a 0.62. Si baja mucho, hay un error de asignación de roles o equipos.
- Índice global (1ª mitad) → puntos de la 2ª mitad: r ≈ 0.5. Si no replica en los datos generales, revisar antes de usar.
- Rasgos de equipo por situación de gol: la pelota parada debe seguir mostrando baja estabilidad; si aparece estable en más datos, se puede incorporar.

### 8.5 Preguntas abiertas para decidir
1. ¿Los estilos existentes se calculan por partido o por temporada? Se necesitan por equipo y por ventana temporal para poder chequear su estabilidad.
2. ¿Hay tracking o datos de pressing? Si existen, permitirían sustituir varias hipótesis del punto 7 por mediciones directas.
3. ¿Se dispone de alineación probable por partido? Sería el mayor salto para pasar de "nivel de plantel" a una comparación de once inicial.
4. ¿Se puede sumar información de lesiones/suspensiones?

---

## 9. Mapa de scripts de referencia
| Script | Función |
|---|---|
| `etapa1_parseo.py` | copia más reciente por partido; tablas jugador-partido y equipo-partido |
| `etapa2_agregado.py` | agregado por (jugador, equipo), posesión, arqueros, roles, corte dinámico |
| `etapa3_indices.py` | tasas p90 y % con contracción por rol; peso de confianza por estadística |
| `etapa4_cuartiles.py` | dimensiones, índice global y cuartiles por rol |
| `etapa5_equipos.py` | líneas, cuartiles entre equipos, tabla y correlaciones |
| `etapa6_export.py` + `plantilla_informe.html` | CSV finales e informe HTML interactivo (pendiente de revisión en navegador) |
| `etapa7_conclusiones.py` | bootstrap, permutaciones, predicción 1ª→2ª mitad |
| `etapa8_partidos.py` | prueba a nivel de partido (modelo multinomial, validación cruzada repetida) |
| `etapa9_cruce.py` | informe de cruce entre dos equipos |
