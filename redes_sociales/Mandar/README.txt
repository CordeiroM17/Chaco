REEL FERRO - CHACO FOR EVER
===========================

Video vertical 1080x1920, 30 fps, 30 segundos. Hecho con Remotion (React).

PARA RENDERIZAR
1. Instalar Node.js LTS (https://nodejs.org) si no está.
2. Doble clic en RENDER.bat.
3. El video sale en  out\reel_ferro_oeste.mp4
   (la primera vez instala dependencias y baja Chrome Headless: necesita internet)

PARA VER/AJUSTAR ANTES DE RENDERIZAR
- Doble clic en PREVIEW.bat: abre Remotion Studio en el navegador.

QUÉ EDITAR
- src/data.ts   -> el once, posiciones y textos de las 3 fichas.
- src/theme.ts  -> colores y tiempos de cada parte.
- src/camera.ts -> movimientos de cámara (zooms) y recorrido de la pelota.

GUION (30 s)
 0-4 s     Presentación: la pelota entra rodando y hace de "O" en FERR(O). "El puntero · si nos gana, sale campeón"
 4-8 s     Zoom out desde la pelota: aparece la cancha y el 11 de Ferro (4-1-4-1) con camisetas
 8-20 s    La pelota recorre el circuito con zoom in a cada uno y zoom out en cada pase:
           Hoyos (top 2%) -> González (7 asistencias) -> Parisi (9 goles)
 20-23 s   El remate se congela: "Este es el circuito. Hay que cortarlo."
 23-26 s   "66% de sus goles llegan en el 2° tiempo"
 26-30 s   Cierre: "QUE FESTEJEN OTRO DÍA. · VAMOS CHACO"

Colores: negro y blanco Chaco For Ever + dorado para lo importante (src/theme.ts).
El video no lleva música: agregar el audio en tendencia directamente en Instagram/CapCut.
