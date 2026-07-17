# Informe de Partido — Fecha 19 · Chaco For Ever 1-1 Acassuso

**Competencia:** Primera Nacional 2026 · Fecha 19 · Estadio Juan Alberto García (local)
**Resultado:** Chaco For Ever 1 – 1 Acassuso (entretiempo 1-0)
**Figura de la cancha:** Matías Romero (rating 8.1)

Este informe lee el partido con las dos lupas que veníamos usando toda la temporada: la cadena de Markov del marcador y el reparto de goles por ventana de tiempo. Los dos avisos que el modelo repetía fecha tras fecha se cumplieron acá casi al pie de la letra.

---

## 0. Ficha del partido

| | |
|---|---|
| Goles Chaco | **Matías Romero (26′)**, de cabeza |
| Goles Acassuso | A. Hermoso (56′) |
| Formación Chaco | 4-4-2 |
| Formación Acassuso | 4-3-3 |
| Posesión | 58% – 42% |
| xG | **1.86 – 1.22** |
| Tiros (al arco) | 16 (6) – 10 (4) |
| Córners | 7 – 5 |
| Amarillas | 3 – 3 |

---

## 1. Resumen ejecutivo

Chaco hizo el partido que quería y no le alcanzó. Manejó la pelota (58%), pegó primero con Romero, generó más y mejor (1.86 de xG contra 1.22), y aun así se volvió a casa con un punto. Acassuso empató con su única jugada realmente clara del partido, y la metió en el minuto exacto donde Chaco viene siendo más frágil todo el año.

**La foto del partido en una frase:** el equipo jugó bien, se puso en ventaja y volvió a no sostenerla, con el gol en contra cayendo apenas arrancado el segundo tiempo. No fue un mal partido. Fue el patrón de siempre.

---

## 2. La profecía de Markov, cumplida

Los dos hallazgos que el análisis de temporada venía marcando como los problemas de fondo del equipo aparecieron los dos en el mismo partido.

### 2.1 Otra vez el empate yendo ganando

La cadena de Markov del marcador ya decía que Chaco no sabe quedarse arriba: yendo ganando por uno, la ventaja se le diluía el 100% de las veces. Acassuso sumó un caso más a esa lista. El equipo se fue al descanso 1-0, controlando, y terminó 1-1.

No es un dato aislado de este partido. Es la cuarta vez en la temporada que se le escapa una ventaja de un gol. El problema no es ponerse arriba, que lo hace seguido. El problema es lo que pasa después.

### 2.2 El gol en contra, en el minuto que veníamos marcando

El reparto de goles por ventana de tiempo señalaba la franja **45′-60′** como el agujero negro del equipo: ahí se le juntaban 8 goles en contra en toda la temporada. Hermoso empató al **56′**. Con ese gol, la ventana 45′-60′ ahora acumula **9 goles en contra**, el 36% de todo lo que Chaco recibió en el año, la franja más castigada por lejos.

Once minutos después del entretiempo, con el partido controlado, Acassuso encontró el empate. Es exactamente el guion que el modelo venía anticipando: algo le pasa a Chaco al salir del vestuario. Vale volver a mirar en video qué se dice en el descanso y cómo arranca físicamente esa franja, porque ya no es casualidad estadística, es una regularidad de 19 fechas.

*(Respaldo: `timeline.png`, `momentum.png`, `xg_tramos.png` en la carpeta del partido; `markov_marcador.png` y `goles_por_ventana_tiempo.png` en `graficos/`.)*

---

## 3. Tabla de hallazgos del partido

| Categoría | Hallazgo | Dato concreto | Lectura |
|---|---|---|---|
| **Dominio** | Chaco fue el equipo más peligroso | 58% de posesión, 16 tiros a 10, 1.86 xG a 1.22 | Mereció más que un punto por volumen y calidad de juego |
| **Eficiencia rival** | Acassuso convirtió su única chance clara | El gol de Hermoso valía 0.56 de xG (0.74 de xGOT); casi la mitad del xG visitante salió de esa sola jugada | Sin ese remate, Acassuso apenas generó |
| **Gestión de la ventaja** | Se repitió el patrón de temporada | 1-0 al descanso, 1-1 final | Cuarto partido del año en que se diluye una ventaja de un gol |
| **Momento del gol en contra** | Cayó en la franja más frágil | Empate al 56′, dentro del 45′-60′ | Confirma el agujero del arranque del complemento |
| **Pelota parada ofensiva** | Chaco insistió por arriba sin premio | 7 córners, cabezazos de Romero (58′) y Garay (24′) que no entraron | Sigue sin convertir de córner, cuenta pendiente del año |
| **Refuerzos** | Romero y Fernández entre los mejores | Romero 8.1 y gol; L. Fernández 7.4 con 0.42 de xA y 5 centros buenos | Las incorporaciones respondieron en su presentación |

---

## 4. Romero, el regreso con gol

El que volvió y marcó fue **Matías Romero**. A los 26′ ganó de cabeza dentro del área y puso el 1-0, en su primer partido de vuelta en Chaco. Terminó como la figura de la cancha (8.1) y el más determinante del ataque: 0.94 de xG generado, tres remates al arco, 12 duelos ganados y cuatro de arriba.

No fue solo el gol. Fue el jugador alrededor del cual pasó el peligro de Chaco todo el partido. Tuvo el 1-0, un mano a mano al 60′ que le tapó el arquero y dos cabezazos más que se fueron cerca. Si el equipo hubiera cerrado el partido, la tarde era redonda para él.

Al lado, el otro refuerzo que arrancó de titular, **Leandro Fernández**, fue el más participativo del circuito ofensivo por afuera: 0.42 de xA, cinco centros al área que llegaron y tres pases clave. Las dos caras nuevas del plantel se hicieron sentir de entrada.

*(Respaldo: `ratings_jugadores.png`, `shotmap_chaco.png`, `heatmap/M_S_Romero.png` en la carpeta del partido.)*

---

## 5. Conclusiones para el cuerpo técnico

- **El partido valida el diagnóstico, no lo cambia.** Chaco jugó bien y perdió dos puntos por lo mismo de siempre: no sostiene la ventaja y se le rompe el partido entre el 45′ y el 60′. Es el mejor argumento para trabajar esas dos cosas puntuales en la semana, porque el nivel de juego alcanza; lo que falla es la gestión.
- **Arranque del segundo tiempo, prioridad uno.** Con el empate al 56′ ya son 9 goles en contra en esa franja en el año. Vale un protocolo de activación específico para la salida del vestuario y revisar en video los primeros diez minutos del complemento.
- **Aprovechar que el equipo genera.** 1.86 de xG y 16 tiros de local es una buena base. El problema no fue crear, fue defender una ventaja y definir las que tuvo Romero. La materia prima ofensiva está.
- **Romero y Fernández, para sostener.** Los dos refuerzos rindieron en su debut. Romero además carga el gol y la referencia de área que al equipo le venía faltando. Conviene darles rodaje y construir alrededor de ellos.
- **Córner, otra vez la cuenta pendiente.** Siete córners, cabezazos claros, cero goles. Es un recurso que Chaco tiene (juega bien por arriba) y que todavía no capitaliza. Trabajar variantes ofensivas de pelota parada.

---

*Informe generado a partir del pipeline de análisis de Chaco For Ever, temporada 2026, Fecha 19 vs Acassuso. Gráficos de respaldo en `outputs/temporadas/2026/partidos/2026-07-07_vs_acassuso_h/` y `outputs/temporadas/2026/graficos/`.*
