# Recomendaciones para el informe por partido — Chaco For Ever

Guía para construir un informe individual de partido (1 rival, 1 fecha) orientado al **cuerpo técnico**, usando la data y los gráficos que ya genera tu pipeline. Pensado para imprimirse/exportarse a **PDF A4 vertical**.

Acompaña a esta guía un **prototipo real** armado con el partido vs Chacarita (04/05/2025):
`outputs/temporadas/2025/partidos/2025-05-04_vs_chacarita_a/informe_Chaco_vs_Chacarita.html`

---

## 1. Idea rectora

Un informe de partido para cuerpo técnico tiene que responder, en este orden:

1. **¿Qué pasó?** (marcador, goles, figura) — 10 segundos.
2. **¿Cómo pasó?** (relato: momentum, xG por tramos, tiros) — el "por qué" del resultado.
3. **¿Quién lo sostuvo?** (estructura, territorio, rendimiento individual).
4. **¿Qué hacemos con esto?** (recomendaciones accionables).

Regla de oro: **una idea por bloque** y **cada gráfico con una línea que diga qué leer en él**. El gráfico sin lectura no sirve al cuerpo técnico.

---

## 2. Estructura recomendada (6 páginas A4)

**Página 1 — Portada + resumen.** Encabezado con el marcador grande (como tus referencias estilo "Sevilla 1–2 Barcelona"), competición, fecha, sede. Debajo: goles, figura del partido y un bloque **"La lectura en 30 segundos"** (3–4 frases con la conclusión). Al costado, la comparación general de estadísticas (`stats_comparacion.png`).

**Página 2 — Relato del partido.** `momentum.png` + `xg_tramos.png` + `timeline.png`. Juntos cuentan la película temporal: quién dominó, cuándo hubo peligro real y qué pasó con goles/cambios/tarjetas.

**Página 3 — Ocasiones.** `shotmap_chaco.png` + `shotmap_rival.png`. La calidad de las ocasiones de cada lado.

**Página 4 — Estructura y territorio.** `posiciones_promedio.png` + `heatmap_equipo.png` + `radios_accion.png`. Cómo se paró el equipo y por dónde se jugó.

**Página 5 — Rendimiento individual.** `ratings_jugadores.png` + `defensivo.png`. Opcional: heatmaps individuales (`heatmap/*.png`) y pizzas de las figuras (`graficos/jugadores/pizza_*.png`).

**Página 6 — Recomendaciones post-partido.** El cierre accionable (ver sección 4).

> Si el informe tiene que ser más corto (1–2 páginas), quedate con **Página 1 + Página 6** y un solo gráfico de relato (momentum). El resto pasa a anexo.

---

## 3. Qué gráfico responde qué pregunta

| Pregunta del cuerpo técnico | Gráfico |
|---|---|
| ¿Ganamos merecido o nos salvamos? | `xg_tramos` + `stats_comparacion` (xG) |
| ¿Cuándo sufrimos / cuándo fuimos dominantes? | `momentum` + `xg_tramos` |
| ¿Generamos ocasiones claras o tiros de afuera? | `shotmap_chaco` (tamaño = xG) |
| ¿Cuánto y desde dónde nos remataron? | `shotmap_rival` |
| ¿Cómo nos paramos? ¿Bloque alto o bajo? | `posiciones_promedio` + `heatmap_equipo` |
| ¿Por qué carril nos jugaron? | `heatmap_equipo` |
| ¿Quién rindió y quién no? | `ratings_jugadores` |
| ¿Quién sostuvo la defensa? | `defensivo` |
| ¿Qué pasó después de cada gol/cambio? | `timeline` |

---

## 4. Cómo redactar las "recomendaciones post-partido"

Es la parte que más valor agrega y la que el cuerpo técnico realmente usa. Tres principios:

**a) Siempre con evidencia del propio informe.** Cada recomendación se apoya en un dato o gráfico que está en las páginas anteriores. Nada de impresiones sueltas.

**b) Formato fijo: Observación → Dato → Acción.**
- *Observación:* la conclusión en una frase ("Se conceden demasiados remates").
- *Dato:* el número/gráfico que lo respalda ("18 tiros, 8 al arco, 1.05 xG en contra").
- *Acción:* qué hacer en la semana ("cerrar el carril central para bajar el volumen de tiro").

**c) Separar lo corregible de lo coyuntural.** Dividir en **"A favor / a sostener"** y **"A corregir"**. Y distinguir lo táctico (depende de nosotros) de lo del contexto (rival, árbitro, expulsión), que se menciona pero no se "corrige".

Mantené entre **4 y 6 recomendaciones**. Más que eso, se diluye el foco.

**Ejemplo aplicado (vs Chacarita, ya volcado en el prototipo):**
- *A sostener:* pelota parada ofensiva (2 de 3 goles) y solidez del arquero/área chica (8 atajadas, valla invicta).
- *A corregir:* volumen de remates concedidos (18), gestión del tramo 30'–60' (picos de xG rival), disciplina (17 faltas / 7 amarillas / 1 roja) y poca tenencia para administrar la ventaja (31% de pases).

---

## 5. Formato y estilo del PDF

- **A4 vertical**, márgenes de ~12 mm, un encabezado de sección por página.
- **Paleta consistente** (la que ya usan tus gráficos): fondo crema `#F3F0E7`, **rojo Chaco `#C62B2B`**, **azul rival `#2C3C5F`**, acento dorado `#E0A526`, verde positivo `#3FA93F`.
- Marcador grande arriba (estilo scoreboard), tipografía sans-serif, negritas solo para lo importante.
- **Cada gráfico dentro de una tarjeta** con su caption de 1 línea.
- **Pie de página** con "Fuente: SofaScore" + fecha de generación + número de página.
- Cómo exportar: abrir el HTML en el navegador → **Ctrl/Cmd + P → Guardar como PDF → Vertical**. El prototipo ya trae los saltos de página y estilos de impresión listos.

---

## 6. Control de calidad de datos (revisar antes de publicar)

Detecté inconsistencias entre los CSV crudos y los gráficos que conviene unificar:

1. **"Posesión" ≠ posesión oficial.** En `stats_comparacion.png` la posesión figura **69/31**, pero es el **reparto de pases** (474 / (474+214) ≈ 69%). La posesión real de SofaScore en `statistics.csv` es **49/51**. Hay que decidir cuál mostrar y **etiquetarla correctamente** (o mostrar las dos como métricas distintas: "Posesión" vs "Volumen de pases").
2. **Tiros: 18 vs 16.** El gráfico recomputa los tiros desde el shotmap (18); `statistics.csv` trae 16. Elegir una única fuente para todo el informe.
3. **Goles y marcador:** validados para este partido (Chacarita 0–3, goles de Andueza e/c 18', Silvera 31', Mateo 79'), pero conviene cruzar siempre `incidents` + `lineups` + `shotmap` automáticamente para evitar errores en partidos futuros.

---

## 7. Próximos pasos

- **Reusar la plantilla** para cada partido: misma estructura, sólo cambian la carpeta de gráficos y los textos de resumen/recomendaciones.
- **Automatizar la exportación a PDF** cuando el entorno Python esté disponible (hoy se generó como HTML imprimible porque el sandbox de ejecución no estaba activo). El mismo layout se puede renderizar a PDF directo desde los CSV + PNG.
- **Plantilla de texto** para las páginas 1 y 6 (resumen y recomendaciones), que es lo único que se escribe a mano por partido.
