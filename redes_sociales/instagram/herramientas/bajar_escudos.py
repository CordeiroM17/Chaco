# -*- coding: utf-8 -*-
"""
Baja escudos de clubes a assets/escudos/<slug>.png para usarlos en las placas.

Los toma de SofaScore (la misma fuente del pipeline) usando el navegador del
scraper, porque la API rechaza un `requests` pelado con 403. Los team_id salen
del fixture de la temporada, así que alcanza con pasar el nombre del club como
aparece ahí (o un pedazo del nombre).

    python bajar_escudos.py "Los Andes"
    python bajar_escudos.py "Los Andes" "San Miguel" "All Boys"
    python bajar_escudos.py --listar            # qué clubes hay en el fixture

Es idempotente: si el png ya está, no lo vuelve a bajar (pasar --forzar para
rehacerlo).
"""
import base64
import os
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]        # .../redes_sociales/instagram
PROYECTO = RAIZ.parents[1]                        # raíz del proyecto
ESCUDOS = RAIZ / "assets" / "escudos"
FIXTURE = PROYECTO / "data" / "temporadas" / "2026" / "fixture.csv"

sys.path.insert(0, str(PROYECTO))


def slug(nombre):
    return re.sub(r"[^a-z0-9]+", "_", nombre.lower()).strip("_")


def equipos_del_fixture():
    """{nombre_del_club: team_id} a partir del fixture de la temporada."""
    import pandas as pd
    f = pd.read_csv(FIXTURE)
    eq = {}
    for lado in ("home", "away"):
        for nombre, tid in zip(f[f"{lado}_team"], f[f"{lado}_team_id"]):
            if isinstance(nombre, str) and nombre not in eq:
                eq[nombre] = int(tid)
    return dict(sorted(eq.items()))


def resolver(pedido, equipos):
    """Match exacto o, si no, por coincidencia parcial sin distinguir mayúsculas."""
    if pedido in equipos:
        return pedido, equipos[pedido]
    cands = [n for n in equipos if pedido.lower() in n.lower()]
    if len(cands) == 1:
        return cands[0], equipos[cands[0]]
    if not cands:
        raise SystemExit(f"No encontré '{pedido}' en el fixture. Probá con --listar.")
    raise SystemExit(f"'{pedido}' es ambiguo: {', '.join(cands)}")


def bajar(driver, team_id):
    """Trae la imagen como bytes.

    Se navega directo a la URL de la imagen (así el origen de la página ES el de
    la API y no hay CORS) y se pasa el <img> renderizado por un canvas para
    recuperar los bytes en base64."""
    url = f"https://api.sofascore.com/api/v1/team/{team_id}/image"
    driver.get(url)
    time.sleep(2.5)
    js = """
    const img = document.querySelector('img');
    if (!img || !img.naturalWidth) return 'ERROR:sin imagen';
    const c = document.createElement('canvas');
    c.width = img.naturalWidth; c.height = img.naturalHeight;
    c.getContext('2d').drawImage(img, 0, 0);
    try { return c.toDataURL('image/png'); }
    catch (e) { return 'ERROR:' + e; }
    """
    out = driver.execute_script(js)
    if not out or str(out).startswith("ERROR:"):
        print("   ", out)
        return None
    return base64.b64decode(str(out).split(",", 1)[1])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    forzar = "--forzar" in sys.argv
    equipos = equipos_del_fixture()

    if "--listar" in sys.argv or not args:
        print("Clubes en el fixture 2026:")
        for n, t in equipos.items():
            marca = "  (ya está)" if (ESCUDOS / f"{slug(n)}.png").exists() else ""
            print(f"  {n}  [{t}]{marca}")
        return

    objetivos = []
    for pedido in args:
        nombre, tid = resolver(pedido, equipos)
        destino = ESCUDOS / f"{slug(nombre)}.png"
        if destino.exists() and not forzar:
            print(f"ya estaba: {destino.name}")
            continue
        objetivos.append((nombre, tid, destino))

    if not objetivos:
        return

    ESCUDOS.mkdir(parents=True, exist_ok=True)
    from src.scraping.chaco_scraper import _build_driver
    driver, backend = _build_driver(headless=True)
    print(f"[driver] {backend}")
    try:
        # una visita al sitio para tomar cookies antes de pegarle a la API
        driver.get("https://www.sofascore.com/")
        time.sleep(3)
        for nombre, tid, destino in objetivos:
            data = bajar(driver, tid)
            if data:
                destino.write_bytes(data)
                print(f"OK {nombre} -> {destino.name} ({len(data)} bytes)")
            else:
                print(f"FALLO {nombre} [{tid}]")
            time.sleep(1.5)
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
