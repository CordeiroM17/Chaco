# Especificación Técnica: Sistema de Análisis de Plantel y Scouting para Primera B (Sofascore Data)

Este documento detalla la lógica de negocio, arquitectura de datos, métricas calculadas y algoritmos de clasificación para que un sistema de análisis deportivo evalúe el rendimiento de un plantel actual, determine renovaciones/bajas y recomiende fichajes contextualizados en la categoría **Primera B**.

---

## 1. Arquitectura de Datos de Entrada (Sofascore Ingestion)

El sistema debe procesar datasets provenientes de eventos/partidos de Sofascore con granularidad por partido y agregada por temporada:

```
Inputs Requeridos:
- player_id, player_name, team_id, position, age, minutes_played, appearances
- sofascore_rating (promedio y serie temporal por partido)
- Métricas ofensivas: goals, assists, key_passes, big_chances_created, shots_total, shots_on_target, successful_dribbles, touches_in_box
- Métricas de creación/circulación: accurate_passes, pass_accuracy_pct, passes_final_third, long_balls_accuracy_pct, crosses_accuracy_pct
- Métricas defensivas: tackles, interceptions, clearances, blocked_shots, ground_duels_won, ground_duels_pct, aerial_duels_won, aerial_duels_pct, fouls_committed, errors_leading_to_shot
- Métricas de equipo (Contexto): team_possession_avg, team_goals_scored, team_goals_conceded, team_table_position
```

---

## 2. Normalizaciones y Métricas Derivadas

### 2.1. Métricas por 90 Minutos (p90)
Todas las métricas de volumen deben normalizarse obligatoriamente por 90 minutos de juego efectivo:
$$\text{Métrica}_{p90} = \frac{\text{Métrica Total}}{\text{Minutos Jugados}} \times 90$$

*Filtro de fiabilidad muestral:* Excluir o marcar con etiqueta de advertencia (`sample_size_warning = True`) a jugadores con menos de 600 minutos acumulados.

### 2.2. Ajuste por Posesión (PAdj)
En la Primera B, defensores de equipos que pelean abajo inflan despejes/intercepciones por pasar 70 minutos defendiendo. Para métricas defensivas (intercepciones, recuperaciones, quites), aplicar ajuste por posesión:
$$\text{Métrica}_{PAdj} = \text{Métrica}_{p90} \times \left( \frac{50}{100 - \text{Posesión Promedio del Equipo}} \right)$$

### 2.3. Cálculo de Percentiles por Posición
Para cada métrica calculada, computar el rango percentil dentro del universo de la liga para la misma posición o rol:
$$Percentil(x) = \frac{\text{Cantidad de jugadores con valor} < x}{\text{Total de jugadores en la posición}} \times 100$$

---

## 3. Índices Compuestos por Rol (Scoring Model)

Generar un puntaje ponderado de 0 a 100 para evaluar idoneidad según la demarcación funcional:

### 3.1. Defensor Central (CB Score)
* $30\%$ Porcentaje de duelos aéreos ganados (`aerial_duels_pct`)
* $25\%$ Duelos terrestres ganados % (`ground_duels_pct`)
* $20\%$ Despejes + Intercepciones PAdj (`clearances_padj` + `interceptions_padj`)
* $15\%$ Pases progresivos/hacia adelante completados
* $10\%$ Calificación promedio Sofascore

### 3.2. Lateral / Carrilero (FB/WB Score)
* $25\%$ Duelos individuales defensivos ganados %
* $25\%$ Centros precisos p90 + porcentaje de acierto
* $25\%$ Pases clave p90 + toques en último tercio p90
* $15\%$ Recuperaciones de pelota p90
* $10\%$ Calificación promedio Sofascore

### 3.3. Mediocampista Central Defensivo / 5 Posicional (DM Score)
* $30\%$ Recuperaciones + Intercepciones PAdj
* $25\%$ Porcentaje de acierto de pase global
* $25\%$ Duelos terrestres ganados %
* $10\%$ Eficiencia de pase bajo presión (pérdidas reducidas en campo propio)
* $10\%$ Calificación promedio Sofascore

### 3.4. Mediocampista Mixto / Volante Interno (CM/Box-to-Box Score)
* $25\%$ Progresión con pelota (regates exitosos p90 + pases al último tercio)
* $25\%$ Pases clave p90
* $25\%$ Presencia defensiva (quites + intercepciones p90)
* $15\%$ Toques en el área rival p90
* $10\%$ Calificación promedio Sofascore

### 3.5. Extremo / Mediapunta (W/AM Score)
* $30\%$ Generación directa: Pases clave p90 + Asistencias p90 + Grandes chances creadas
* $25\%$ Capacidad de desequilibrio: Regates exitosos p90 + toques en área rival
* $25\%$ Amenaza de gol: Disparos a puerta p90 + Tasa de conversión (Goles / Disparos)
* $10\%$ Trabajo sin pelota (duelos ganados en último tercio)
* $10\%$ Calificación promedio Sofascore

### 3.6. Delantero Centro (ST Score)
* $35\%$ Eficacia de remate: Goles p90 y ratio (Goles / Disparos al arco)
* $25\%$ Toques en el área penal p90 + Disparos al arco p90
* $20\%$ Duelos aéreos ganados p90 (fijación de centrales)
* $10\%$ Grandes chances creadas p90 / Asistencias p90
* $10\%$ Calificación promedio Sofascore

---

## 4. Clasificador del Plantel Actual (Semáforo de Continuidad)

Para cada jugador del plantel analizado, el sistema debe asignarle un estatus de retención/renovación basado en reglas multicriterio:

```python
def classify_current_squad_player(player, team_stats):
    pct_minutes = (player.minutes_played / team_stats.max_available_minutes) * 100
    pos_percentile = player.composite_score_percentile
    rating_variance = player.sofascore_rating_std_dev
    
    # 1. Intransferible / Prioridad de Renovación
    if pct_minutes >= 65 and pos_percentile >= 70 and rating_variance <= 0.65:
        return {
            "status": "PRIORIDAD_RENOVACION",
            "tier": 1,
            "action": "Asegurar renovación de contrato. Columna vertebral del equipo."
        }
        
    # 2. Rotación Valiosa (Role Player)
    elif (pos_percentile >= 60 and pct_minutes < 65) or (pct_minutes >= 50 and pos_percentile >= 50 and rating_variance <= 0.55):
        return {
            "status": "ROTACION_VALIOSA",
            "tier": 2,
            "action": "Mantener con tope salarial de rol secundario. Aporte costo-efectivo."
        }
        
    # 3. Prescindible / "Da Igual"
    elif 40 <= pos_percentile < 60:
        return {
            "status": "PRESCINDIBLE",
            "tier": 3,
            "action": "No comprometer presupuesto de aumento. Reemplazable fácilmente en mercado libre."
        }
        
    # 4. Baja Recomendada
    else:
        return {
            "status": "BAJA_PRIORITARIA",
            "tier": 4,
            "action": "Liberar masa salarial o cupo de plantilla. Rendimiento por debajo del percentil 40."
        }
```

---

## 5. Módulo de Scouting y Reemplazos (Terna de Fichajes)

Para cada posición donde un jugador sea clasificado como `BAJA_PRIORITARIA` o `PRESCINDIBLE`, el algoritmo debe buscar en la base de la liga y recomendar una **Terna de Alternativas**:

1. **Perfil Rendimiento Inmediato (Top Performer):**
   * Filtro: `composite_score_percentile >= 80`, `appearances >= 20`.
   * Jugador ya probado, rendimiento dominante en la divisional.
2. **Perfil Eficiencia de Costo (Under-the-radar / Moneyball):**
   * Filtro: `composite_score_percentile >= 70`, pero jugando en equipos de los puestos inferiores de la tabla o con bajo cartel mediático. Alta relación rendimiento/exposición.
3. **Perfil Apuesta / Desarrollo:**
   * Filtro: `age <= 23`, `composite_score_percentile >= 65`, métricas de desequilibrio específicas en el percentil superior (ej. top 10% en regates o top 10% en duelos ganados).

---

## 6. Generación del Informe para Dirigencia y DT (Estructura de Salida)

El pipeline debe exportar un informe estructurado (formato Markdown, PDF o Dashboard) con las siguientes secciones:

1. **Executive Summary:**
   * Total de jugadores analizados.
   * Cantidad por estatus: [X Prioridad, Y Rotación, Z Prescindibles, W Bajas].
   * Resumen de masa salarial recomendada a liberar.
2. **Auditoría Puesto por Puesto:**
   * Tabla con: Jugador | Minutos (%) | Rating Sofascore | Score Puesto | Percentil Liga | Clasificación | Recomendación.
3. **Sugerencias de Mercado (Terna por Posición Débil):**
   * Tarjetas de scouting comparativas con métricas cara a cara (Jugador actual vs. Opciones A, B y C).
