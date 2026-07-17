# Roadmap — Chaco For Ever Análisis

*Diagnóstico y plan de acción. Escrito después de revisar el pipeline completo: scraping, análisis (`src/analysis/`), visualización, informes (.md/.tex/.pdf), notebooks, y el módulo de redes sociales.*

---

## 1. Diagnóstico honesto: qué hay realmente

Antes que nada, una corrección a tu propio diagnóstico: dijiste que "no hay muchos datos" pero que la interpretación es buena. Es más que eso. Lo que armaste no es una planilla con gráficos — es un pipeline de analítica deportiva completo, con un nivel de sofisticación que normalmente se ve en consultoras boutique de datos de fútbol, no en un hobby de hincha. Vale que lo veas así para lo que sigue.

**Scraping:** API directa de SofaScore (con Selenium/cloudscraper de respaldo) para partidos propios, más un scraper de rivales que baja la temporada completa del rival (no solo una muestra), más un scraper de Transfermarkt para fichas de jugadores. Con manejo de casos borde: matcheo de rivales por `team_id` estable entre temporadas (no por nombre, que cambia), corrección documentada de un hueco real en los datos de SofaScore.

**Análisis (la parte más fuerte):**
- Cadena de Markov del estado del marcador (propia y del rival) — no es un adorno, es la columna vertebral narrativa de tus informes.
- Modelo de riesgo de colapso defensivo con regresión de Cox (supervivencia), usando fatiga acumulada + momentum.
- Centralidad de eigenvector sobre la red de minutos compartidos, para encontrar el "núcleo" real del equipo.
- Entropía de Shannon sobre la distribución espacial de xG, para medir qué tan "leíble" es el ataque.
- Red de asistencias, calendario de carga, amenaza por tipo de jugada, xG según estado del marcador, goles por ventana de tiempo.
- Todo esto espejado para el rival en el pre-partido (forma, perfil táctico, mejor XI reconstruido, formaciones usadas, timeline de DT, riesgo de sanción, head-to-head histórico).

**Informes:** generados con LLM (NVIDIA gratis o Claude) a partir de los datos, no texto genérico. Leí el informe de la fecha 19 y el de mitad de temporada: son honestamente de nivel publicable. Tienen resumen ejecutivo, hallazgos accionables para el cuerpo técnico, y — esto es lo que más vale — son honestos con las limitaciones (reconocen cuando el modelo de Cox no tiene señal por muestra chica, documentan un hueco de datos de SofaScore y cómo se corrigió). Esa honestidad metodológica es un activo, no una debilidad: es lo que separa un analista serio de alguien que infla conclusiones.

**Redes sociales:** sistema de marca propio (paleta, tipografía), generador de placas (dato, ranking, resultado, cita, portada, enmarcar), scripts de carrusel para post-partido, pre-partido, curiosidades y presentación de refuerzos. Plan de contenido con 4 pilares y cadencia semanal ya definida. Ya se publicaron 3 piezas.

**Scouting de refuerzos:** fichas de Transfermarkt de los 4 incorporados (historial de clubes, minutos, valor de mercado).

**Video:** pipeline de visión por computadora (detección de jugadores, tracking, homografía de cancha) basado en modelos de Roboflow. Está marcado en el propio código como "prototipo Fase B, validar antes de usar" — es el módulo menos maduro, en los hechos todavía no producís nada con esto.

**Volumen de datos:** temporada 2025 completa (~34 partidos) y 2026 en curso (19 de 20 fechas scrapeadas). Contexto importante: Chaco For Ever está último (18°/18) en la Primera Nacional 2026. Esto no es un dato menor para tu propuesta al club — un equipo en ese lugar de la tabla necesita diagnóstico riguroso más que nadie, y tus informes ya están señalando patrones concretos y repetidos (no sostener ventajas, agujero 45'-60', floja como visitante).

---

## 2. Qué falta, separado por objetivo

### A. Contratación en Chaco For Ever

- **Falta la capa de "producto" sobre la capa de "análisis".** Todo lo que existe asume que el lector va a leer un informe técnico completo. Un dirigente o el cuerpo técnico necesita un resumen de una página, no un repo. No existe hoy ese one-pager.
- **Falta evidencia de impacto.** ¿Algún informe llegó de verdad a manos del cuerpo técnico? ¿Hubo devolución? Sin eso, el proyecto demuestra capacidad técnica pero no impacto real todavía. Si nunca se lo mandaste a nadie del club, ese es el primer paso concreto, incluso antes de pedir que te contraten.
- **Falta un "historial de acierto".** Guardar por escrito lo que el pre-partido anticipó y chequear después del partido si se cumplió (ya lo hiciste informalmente con lo de Markov y el 45'-60' en la fecha 19 — formalizarlo como práctica sistemática es oro para una entrevista).
- **Falta la propuesta de rol en sí.** El proyecto muestra que sabés hacer análisis. No dice qué harías concretamente como analista contratado: cadencia de entregables, con quién te comunicarías, qué necesitarías del club (acceso a videos propios, planillas de carga física, etc.).
- **Tema de fuente de datos.** Hoy todo es scraping de SofaScore/Transfermarkt, no datos oficiales del club. Para una propuesta formal conviene ser transparente sobre esto y plantear como parte de la propuesta el salto a datos propios si te contratan.

### B. Uso personal, redes sociales, satisfacción propia

- **Todo depende de que vos generes cada pieza a mano.** El plan de contenido es sólido, pero no hay ningún script que, dado un partido nuevo, arme el carrusel post-partido semi-automáticamente a partir de lo que el pipeline ya calculó. Vale la pena cerrar ese último tramo de automatización.
- **Ritmo real todavía bajo.** 3 piezas publicadas. Para crecer una cuenta hace falta constancia sostenida, no picos. Conviene planificar el calendario editorial hasta fin de temporada, no fecha a fecha.
- **No hay medición.** Ninguna métrica de qué contenido funciona (guardados, alcance, comentarios). Aunque sea una planilla simple, ayuda a no publicar a ciegas.
- **46 skills de marketing instaladas en `.claude/skills`, la gran mayoría pensadas para SaaS/e-commerce** (ads, cro, churn-prevention, cold-email, aso, lead-magnets). Son ruido para una cuenta de fan de fútbol. Conviene quedarte con las 6-8 que aplican de verdad: `social`, `content-strategy`, `copywriting`, `image`, `video`, quizás `marketing-plan`.
- **Video es un frente sin arrancar todavía** (lo del pipeline de visión por computadora es otra cosa, es para tracking de datos, no para editar contenido). Acá es donde tu colega con experiencia en edición/fotografía entra directo — ver documento aparte.
- **Falta tu "cara" en el contenido.** El plan está muy centrado en placas de datos. Un video corto tuyo explicando un hallazgo en 60 segundos probablemente rinda más que la placa sola, sobre todo para crecer al principio.

### C. Envío a otros clubes (Federal A, ascenso, exterior)

- **Nada del pipeline es genérico hoy** — `config.py`, `RIVALS`, todo está armado específicamente para Chaco For Ever. Para mostrarlo a otro club hace falta un caso de estudio que explique el método sin depender 100% de ser hincha de Chaco (aunque adaptar el pipeline a otro equipo es, en los hechos, rápido — está bien diseñado para eso).
- **No tenés contactos** (lo charlamos). Ver la estrategia de outreach en la Etapa 1 del roadmap abajo.
- **No hay nada en inglés.** Si el objetivo incluye el exterior, hace falta al menos un one-pager en inglés.
- **No hay un pitch corto.** Todo lo que existe requiere que el otro lea informes largos. Hace falta algo de un párrafo + una imagen, para un primer contacto en frío.
- **Ojo con los términos de uso de SofaScore/Transfermarkt** si en algún momento esto se ofrece como servicio pago a un tercero — repasarlo antes de ese paso, aunque para un club chico probablemente no sea un problema práctico real.

---

## 3. Roadmap por etapas

Como me contaste que hoy el tiempo real es limitado pero estás dispuesto a ir a fondo si aparece una chance concreta, separo el roadmap en dos velocidades: modo sostenible (ahora) y modo full (si un club — Chaco u otro — muestra interés real).

### Etapa 0 — Ahora, 2 a 3 semanas, ritmo hobby: consolidar y empaquetar

1. Armar un one-pager (PDF de 1-2 páginas): quién sos, por qué hacés esto, 3 hallazgos reales explicados en una frase cada uno (el de Markov y el de la ventana 45'-60' son los más fuertes), y qué podrías aportar como analista. Este es el documento que se manda, no el repo completo.
2. Curar 5-6 piezas "vidriera": el mejor informe de partido, el de mitad de temporada, un ejemplo de pre-partido, un carrusel de Instagram, y si te animás, una explicación de una página de "cómo uso Markov para esto" en criollo.
3. Si `@chacoforever.stats` no está lanzada todavía, lanzarla ya con la tanda de contenido que ya tenés armada (refuerzos, mitad de temporada, fecha 19).
4. Podar las skills de marketing a las que realmente aplican.

### Etapa 1 — 1 a 2 meses, en paralelo a que se juega la temporada: rutina y evidencia

1. Instaurar la rutina fecha a fecha sin salteos: pre-partido antes del partido, post-partido a las 24-48h, reflejado en redes cada semana.
2. Empezar a guardar por escrito las lecturas del pre-partido (ej. "le cuesta cerrar arriba en el marcador") y marcar después del partido si se cumplieron. Es tu historial de acierto — el argumento más fuerte que podés llevar a una entrevista.
3. Sentarte con tu colega para que revise 2-3 informes en cuanto a redacción y claridad (no la estadística) — el resultado retroalimenta directo el one-pager de la Etapa 0.
4. Armar la lista de outreach: 15-20 clubes objetivo (Federal A regional, equipos de Primera Nacional sin área de datos conocida, 2-3 clubes del exterior donde el idioma no sea barrera), mensaje corto + one-pager adjunto, sin pedir nada a cambio la primera vez.
5. Sumarle una capa interpretativa al análisis de refuerzos: hoy es solo la ficha de Transfermarkt. Falta cruzarlo con lo que el equipo necesita en esa posición según el propio análisis de temporada.

### Etapa 2 — Si hay interés real (de Chaco For Ever o de otro club): modo full

1. Reunión formal con el one-pager + un informe real + una propuesta de rol concreta (cadencia, entregables, qué necesitarías del club).
2. Si te contratan en Chaco: encarar la migración progresiva de datos de terceros a datos propios/oficiales del club — es un salto de calidad y también un tema a resolver formalmente con el club.
3. Si es otro club: adaptar el pipeline (`config.py` ya está pensado para esto) — probablemente 1-2 semanas de trabajo para tener el mismo nivel andando para otro equipo.
4. Retomar en serio el pipeline de video — hoy es prototipo sin validar. Con más tiempo disponible se vuelve viable, y sería un diferencial fuerte frente a otros analistas de ligas chicas.

### Etapa 3 — Mediano plazo, con o sin contratación: escalar el contenido

1. Formato video: guiones cortos (60-90 seg) explicando un hallazgo por semana, editados con tu colega.
2. Si el interés crece, considerar un blog o newsletter con los informes de temporada completos, para el público que quiera más profundidad que un carrusel de Instagram.
3. Medir y ajustar el plan de contenido cada 1-2 meses según lo que realmente funcione.

---

## 4. Precauciones honestas

- La fuente de datos es scraping de SofaScore/Transfermarkt, no una API oficial. Está bien para uso de hincha; para una propuesta formal (sobre todo afuera) conviene ser transparente sobre el origen y sus límites.
- Varios hallazgos son "señal direccional", no verdad estadística absoluta (los propios informes lo dicen: el modelo de Cox no tiene señal todavía con 18 partidos, algunos estados de la matriz de Markov tienen muestra chica). Mantené esa honestidad en todo lo que mandes afuera — es un plus de credibilidad, no algo para esconder.
- El pipeline de video es un prototipo sin validar. No lo presentes como funcional todavía.
- Todo el proyecto depende de vos como único mantenedor. Vale pensarlo de antemano: si te contratan, ¿el club se queda con el pipeline tal cual, lo adaptás, o lo separás de tu proyecto personal?

---

*Documento de trabajo, para iterar. Decime si querés que profundice alguna etapa (por ejemplo, redactar ya el one-pager, o armar la lista concreta de clubes para el outreach).*
