# -*- coding: utf-8 -*-
"""
Pone una foto en un slide de un refuerzo y regenera su carrusel, todo en un
comando. No hace falta tocar carpetas ni nombres a mano.

    python poner_foto.py <jugador> <slide> <ruta_a_la_imagen>

Ejemplos:
    python poner_foto.py federico_moreno 1 "C:/fotos/fede.jpg"
    python poner_foto.py mauricio_tevez 3 D:/tevez.png

- <jugador>: la carpeta en placas/refuerzos/ (matias_romero, leandro_fernandez,
             federico_moreno, mauricio_tevez)
- <slide>:   1 (portada) o 3 (trayectoria) — los slides con foto
- La imagen se copia como imagen_0<slide> y se regeneran las 6 placas.

Consejo: si la foto trae texto o marca de agua, recortala antes en cualquier
editor (Paint, Fotos, Canva…) para que quede solo el jugador; la placa la centra.
"""
import sys
import shutil
from pathlib import Path

import carrusel_refuerzo as CR

RAIZ = Path(__file__).resolve().parents[1]
REFU = RAIZ / "placas" / "partido_fecha_20_san_telmo"


def _jugadores():
    return sorted(p.name for p in REFU.iterdir() if p.is_dir())


def main():
    if len(sys.argv) != 4 or sys.argv[2] not in ("1", "3"):
        print(__doc__)
        print("Jugadores disponibles:", ", ".join(_jugadores()))
        raise SystemExit(1)

    jugador, slide, ruta = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    carpeta = REFU / jugador
    if not carpeta.exists():
        raise SystemExit(f"No existe '{jugador}'. Jugadores: " + ", ".join(_jugadores()))
    if not ruta.exists():
        raise SystemExit(f"No encuentro la imagen: {ruta}")

    src = ruta.resolve()
    ext = ruta.suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    destino = carpeta / f"imagen_{slide:02d}{ext}"
    # borrar imagen_0N previas (menos si la fuente ya es esa misma)
    for viejo in carpeta.glob(f"imagen_{slide:02d}.*"):
        if viejo.resolve() != src:
            viejo.unlink()
    if src != destino.resolve():
        shutil.copy(src, destino)
    print(f"OK · foto puesta como {destino.name}")

    CR.main(jugador)
    print(f"OK · carrusel de {jugador} regenerado en {carpeta}")


if __name__ == "__main__":
    main()
