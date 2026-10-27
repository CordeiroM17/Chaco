REEL DEFENSA - CHACO FOR EVER
=============================

Video vertical 1080x1920, 30 fps, 36 segundos. Hecho con Remotion (React).
Vista 3D liviana (proyección propia en SVG, sin placa de video): renderiza rápido.

PARA RENDERIZAR
1. Instalar Node.js LTS (https://nodejs.org) si no está.
2. Doble clic en RENDER.bat.
3. El video sale en  out\reel_defensa_chaco.mp4
   (la primera vez instala dependencias y baja Chrome Headless: necesita internet)

PARA VER ANTES DE RENDERIZAR
- Doble clic en PREVIEW.bat: abre Remotion Studio en el navegador.

GUION (36 s)
 0-3.5 s   Vista del arquero: tiro libre al ángulo. "NOS PATEARON 279 VECES"
 3.5-16 s  Los 279 remates en contra, en orden, cada vez más rápido (crescendo).
           Cada pelota sale de donde se pateó y va a donde terminó. Goles en dorado.
           La cámara orbita desde atrás del arco hasta la vista aérea. Contador de remates y goles.
 16.5-21 s Dónde entraron: 20 de 26 goles desde adentro del área · 6 de cabeza
 21-26 s   "PERO DESDE AGOSTO..." goles en contra partido a partido: 1.24 -> 0.38 por partido
 26.5-30 s Los 70 remates desde agosto: "nos siguen pateando... pero no entra"
 30-32 s   6 VALLAS INVICTAS en 8 partidos
 32-36 s   "EL ARCO SE CERRÓ." · VAMOS CHACO

DATOS
- src/shots.ts sale de DataM/2026/partidos/*/raw/shotmap.json (28 partidos, 14/02 al 13/09).
- Gimnasia de Jujuy 16/08 no tiene shotmap (perdimos 1-0): cuenta en goles por partido, no en la animación.
- 26 de los 29 goles recibidos tienen remate registrado (falta un gol en contra de Nievas y dos sin remate).

QUÉ EDITAR
- src/theme.ts    -> colores y tiempos de cada parte.
- src/rig.ts      -> movimientos de cámara.
- src/components/Overlays.tsx -> textos.

El video no lleva música: agregar el audio en tendencia directamente en Instagram/CapCut.
