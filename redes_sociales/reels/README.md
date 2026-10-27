# redes_sociales / reels

Reels 9:16 (1080x1920, 30 fps) con el estándar de la cuenta: negro, blanco, un dorado (#E8B23A),
Segoe UI Black / Segoe UI / Bahnschrift, cabecera con rayas y @chacoforever.stats.

## Motor: Remotion (`remotion/`), renderiza con la placa de video
Chrome dibuja con la GPU (`--gl=angle`, ya está en `remotion.config.ts`). 31 s de video ≈ 45 s de render.

```bash
# 1) datos (tabla del Grupo A después de cada partido de Chaco, validada contra la oficial)
venv/Scripts/python.exe redes_sociales/reels/exportar_tabla.py
# 1b) remates a favor para el reel de ataque (escribe remotion/src/ataque/shots.ts; --resumen imprime las cifras)
venv/Scripts/python.exe redes_sociales/reels/exportar_remates.py
# 2) video
cd redes_sociales/reels/remotion
npx remotion studio                                   # ver y ajustar en el navegador
npx remotion render src/index.ts TablaReel ../salidas/chaco_de_ultimo_a_10.mp4
```

| Reel | Composición | Salida |
|------|-------------|--------|
| De último a 10° (tabla con escudos) | `remotion/src/TablaReel.tsx` | `salidas/chaco_de_ultimo_a_10.mp4` |
| Cómo pateamos (3D, 314 remates) | `remotion/src/ataque/` (`AtaqueReel`) | `salidas/chaco_como_pateamos.mp4` |
| Previa Ferro F35 (proyecto aparte) | `../Mandar/` (`FerroReel`) | `salidas/ferro_previa_f35.mp4` |

Música: `public/musica.mp3` = `recording-00_42.mp3` sin los 2,45 s de silencio inicial, normalizada a -14 LUFS (40 s).
Cada composición la apaga en los últimos 2,5 s y funde a negro en el último segundo.

El reel de ataque reusa el motor 3D en SVG de `../Mandar2/` (reel de defensa).

Las fuentes de la marca van en `public/fuentes/` y se cargan en `src/theme.ts` (también en `Mandar/`).
Escudos: `public/escudos/<team_id>.png`, los copia `exportar_tabla.py` desde `instagram/assets/escudos/`.

## Versiones viejas (Python + PIL, solo CPU)
`progreso_puntos.py` (v1) y `progreso_puntos_v2.py` (línea de puntos con cámara). Quedaron como
referencia: el usuario las descartó porque la línea de puntos sola no transmitía el mensaje.
