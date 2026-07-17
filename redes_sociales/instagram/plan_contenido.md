# Plan de contenido — @chacoforever.stats

Cuenta de estadísticas de Chaco For Ever, hecha por fanáticos y para fanáticos. El
objetivo no es vender nada: es que el hincha entienda mejor a su equipo y comparta.
Lo que mueve una cuenta así son datos que sorprenden y placas lindas de compartir.

## Los 4 pilares

Todo post cae en uno de estos cuatro. Si una idea no entra en ninguno, no va.

1. **El dato** — un número que sorprende, en una placa. (Formato: `dato`)
   Ej: "6.4 goles concedidos por encima del xG". El pan de cada semana.
2. **Ranking** — top de goleadores, de puntaje, de rating, de minutos. (Formato: `ranking`)
   Genera debate y guardados. La gente compara y etiqueta.
3. **El partido** — antes y después de cada fecha: resultado, xG, mapa de tiros, figura.
   (Formatos: `resultado`, `enmarcar`, carrusel)
4. **Historia / contexto** — el cruce con el rival, rachas, comparación entre temporadas,
   una frase táctica. (Formatos: `cita`, `enmarcar`)

## Cadencia sugerida (realista para una cuenta hobby)

No hace falta postear todos los días. Mejor pocas placas buenas que muchas flojas.

| Momento | Post | Pilar |
|---------|------|-------|
| Martes | Un dato de la semana | El dato |
| Jueves | Un ranking | Ranking |
| Día del partido | Placa de "cómo llega" (previa) | El partido |
| Post-partido | Carrusel del partido (3-5 placas) | El partido |
| Fin de semana libre | Dato histórico o comparación | Historia |

En semana sin partido, con el martes y el jueves alcanza.

## El carrusel post-partido (la pieza estrella)

Es el formato que más rinde. Plantilla de 5 placas:

1. **Portada** — resultado + "Chaco X - Y Rival" (`resultado` o `portada`)
2. **xG del partido** — quién mereció ganar (`dato` o `enmarcar` del gráfico de xG)
3. **Mapa de tiros** — dónde se generó el peligro (`enmarcar` del shotmap)
4. **La figura** — mejor rating del partido, con su número (`dato`)
5. **Cierre** — una lectura en una frase (`cita`)

## El carrusel de previa (estándar pre-partido)

El gemelo del post-partido, pero para ANTES de jugar. Es un formato **fijo y
reutilizable**: para cada fecha solo se cambian los datos del rival, no el diseño.
Lo genera `scripts/carrusel_previa.py` (bloque `DATOS` arriba de todo). Se apoya
en dos patas verificables — **cómo fue el último cruce** contra ese mismo rival y
**cómo juega el rival** — y cierra con cómo llega el Negro. Plantilla de 8 placas:

1. **Portada** — "Ahora, [Rival]", la próxima fecha y la condición (local/visitante)
2. **El antecedente** — resultado del último cruce con escudos (`resultado`)
3. **La ida en números** — posesión, xG, tiros, córners, formaciones (`ficha`)
4. **El dato de la ida** — el número que resume ese cruce (`dato`)
5. **Así juega el rival** — su característica saliente, en comparación (`dato_vs`)
6. **La cuenta pendiente** — un contexto del propio Negro que pesa en este partido (`dato`)
7. **Cómo llega** — de qué viene For Ever, la señal a favor (`dato_vs`)
8. **Cierre** — la clave del partido en una frase (`cita`)

De dónde salen los números del rival: del **último cruce ya scrapeado** en
`data/temporadas/2026/partidos/`. Si al rival le falta el escudo, dejalo en
`assets/escudos/<rival>.png` y la placa 02 lo dibuja sola; si no está, simplemente
no lo muestra (no rompe).

**Identidad visual propia:** la previa NO va en el negro del post-partido. Usa el
tema **hueso** (blanco cálido, texto negro, dorado de acento) para que el hincha
reconozca de un vistazo que es una previa. El cambio de paleta lo maneja
`scripts/temas.py` (reasigna los colores en runtime, sin duplicar `placas.py`);
`carrusel_previa.py` ya trae `TEMA = "hueso"`. Otros temas listos para probar:
`blanco` (blanco puro) y `dorada` (fondo dorado, matchday). Para cambiarlo, se
toca esa única línea.

## Backlog listo para producir (con datos que ya tenemos, temporada 2026)

Estos salen directo de lo que hay en `outputs/` y del análisis ya hecho:

- [ ] **Dato:** 6.4 goles recibidos por encima del xG → el problema está atrás.
- [ ] **Dato:** 3 de 13 goles fueron de penal → la dependencia del punto de penal.
- [ ] **Dato:** 0 goles de pelota parada a favor / 6 en contra → la asignatura pendiente.
- [ ] **Dato:** 130 toques en el área de Pacheco, pero el gol llega de afuera.
- [ ] **Ranking:** goleadores 2026 (Pacheco, Silvera, Nievas...).
- [ ] **Ranking:** top rating del plantel (SofaScore).
- [ ] **Ranking:** minutos jugados / los más usados por el DT.
- [ ] **Enmarcar:** puntos acumulados fecha a fecha (`puntos_acumulados.png`).
- [ ] **Enmarcar:** rendimiento local vs visitante (`local_vs_visitante.png`).
- [ ] **Enmarcar:** red de asistencias (`red_asistencias.png`) — quién habilita a quién.
- [ ] **Comparación:** 2025 vs 2026 en puntos por fecha.
- [ ] **Pizza de jugador:** una placa por figura (reusar `graficos/jugadores/pizza_*.png`).

## Qué gráficos del pipeline sirven para Instagram (y cuáles no)

Los informes técnicos tienen gráficos densos. Para el feed sirven los que se leen de un
vistazo. Guía rápida:

**Van directo (enmarcados):** puntos acumulados, xG temporada, local vs visitante,
red de asistencias, pizzas de jugador, shotmap del partido.

**Mejor convertirlos a placa `dato` o `ranking`** (el gráfico original es muy técnico):
entropía de tiros, Markov de marcador, riesgo defensivo Cox, toques por tercio.
El número sí sirve; el gráfico académico no.

**No van al feed:** tablas largas, radares de comparación con muchos ejes, cualquier
cosa que necesite leer una leyenda para entenderse.

## Histórico de publicaciones

Lo que ya salió y lo que está armado esperando su día. Cada entrada apunta a la
carpeta de placas y, cuando corresponde, al texto del posteo.

### Ya publicado

1. **Presentación de los 4 refuerzos** — un carrusel por incorporación (Romero,
   L. Fernández, Moreno, Tevez), formato estándar de 6 placas.
   `scripts/carrusel_refuerzo.py` · placas en `placas/refuerzos/<slug>/`.
2. **Cómo llega el Negro a la mitad de la temporada** — radiografía del corte a
   la fecha 18/18 (posición, forma, rankings, el agujero del 45'-60').
   `scripts/carrusel_mitad_temporada.py` · placas en `placas/carrusel_mitad_temporada/`.
3. **Post-partido Fecha 19** — Chaco For Ever 1-1 Acassuso, con Romero de figura.
   Primer uso del estándar post-partido. `scripts/carrusel_partido.py` ·
   placas en `placas/partido_fecha_19_acassuso/`.

### Armado, listo para publicar (secuencia hacia la Fecha 20)

Entre el post-partido de la F19 y la previa de la F20, dos posteos para mantener
la cuenta viva. Orden sugerido:

4. **Curiosidades (relleno, tono liviano)** — 4 datos sueltos de la primera mitad
   para compartir y etiquetar. Es el post de "menos importancia", pensado para
   mitad de semana. `scripts/carrusel_curiosidades.py` ·
   placas + texto en `placas/curiosidades_mitad_temporada/`.
5. **Previa Fecha 20 vs San Telmo (visitante)** — primer uso del **estándar
   pre-partido**: cómo fue la ida (2-2, el Negro lo dominó y se le escapó), cómo
   juega San Telmo y cómo llega For Ever. Va el día previo al partido.
   `scripts/carrusel_previa.py` · placas + texto en `placas/previa_fecha_20_san_telmo/`.

> **Verificar antes de publicar la previa:** el rival de la F20 se dedujo del
> fixture espejo (la F19 fue Acassuso, revancha de la F1; la F20 espeja a la F2 =
> San Telmo, ahora de visitante). Confirmar día y sede oficiales, y dejar
> `assets/escudos/san_telmo.png` para que salga el escudo en la placa 02.

## Notas de arranque

- Reservar el usuario `@chacoforever.stats` (o el que se elija) y cargarlo en `marca.py`.
- Cerrar y reabrir Claude Code para que tome las 46 skills de marketing recién instaladas.
  Con `/social` y `/content-strategy` se piden ideas y calendarios sobre este plan.
- No es una cuenta oficial del club: aclararlo en la bio para evitar malentendidos.
