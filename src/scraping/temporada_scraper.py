"""
temporada_scraper.py
====================
Baja una temporada ENTERA de Primera Nacional (los 36 equipos) partiendo del
fixture, no del feed de cada equipo. Pensado para temporadas pasadas.

Por qué no se usa scrape_rival_recent() para esto:
  - El feed `team/{id}/events/last/{page}` va hacia atrás desde HOY y corta
    cuando dos páginas seguidas no traen partidos de la temporada pedida. Para
    una temporada vieja las primeras páginas son todas de la actual, así que
    corta antes de llegar.
  - Cada partido se bajaba dos veces (una por equipo). Acá se baja UNA: el
    fixture trae el event_id de cada partido, y la base de jugadores
    (src/jugadores) usa una sola copia de todos modos. Es la mitad de
    requests, y de riesgo de ban.

Dónde queda cada partido:
  - Si ya hay una copia en disco (en partidos/ de Chaco o en la carpeta de
    cualquier rival), se completa ESA carpeta: no se crea una segunda.
  - Si no, va a rivals/{slug_local}/{fecha}_vs_{slug_visitante}_h/ — la
    carpeta del equipo LOCAL. Para una temporada bajada así, la carpeta de un
    equipo tiene sus partidos de local y no los de visitante.

Es incremental (reusa _scrape_one): lo que ya está completo se saltea sin
llamadas de red, así que si se corta se vuelve a correr y sigue.
"""

import os
import json
import time
import random
from datetime import datetime, timezone

import pandas as pd

import config
from src.scraping.chaco_scraper import SofascoreClient, _scrape_one
from src.scraping.fixture_scraper import fetch_fixture


def _event_ids_en_disco(season):
    """{event_id: carpeta} de todas las copias que ya hay en disco."""
    base = os.path.join(config._ROOT, "data", "temporadas", str(season))
    raices = [os.path.join(base, "partidos")]
    rb = os.path.join(base, "rivals")
    if os.path.isdir(rb):
        raices += [os.path.join(rb, d) for d in sorted(os.listdir(rb))
                   if os.path.isdir(os.path.join(rb, d))]
    out = {}
    for raiz in raices:
        if not os.path.isdir(raiz):
            continue
        for mk in sorted(os.listdir(raiz)):
            p = os.path.join(raiz, mk, "raw", "event.json")
            if not os.path.exists(p):
                continue
            try:
                with open(p, encoding="utf-8") as f:
                    ev = json.load(f)
            except Exception:
                continue
            ev = ev.get("event", ev)
            if ev.get("id") is not None:
                out.setdefault(int(ev["id"]), os.path.join(raiz, mk))
    return out


def plan_temporada(season, refrescar_fixture=False, verbose=True):
    """
    Lista de (base_dir, match_key, event_id) a bajar para completar la
    temporada. No hace llamadas de red salvo para bajar el fixture si no
    existe (o si refrescar_fixture=True).

    Avisa los equipos que no están en config (quedan con un slug armado del
    nombre de SofaScore): conviene registrarlos en RIVALS_<año> ANTES de bajar,
    porque el slug queda en el nombre de las carpetas.
    """
    season = str(season)
    path = config.fixture_file(season)
    if refrescar_fixture or not os.path.exists(path):
        fetch_fixture(season=season, headless=False, verbose=verbose)
    fx = pd.read_csv(path)
    fx = fx[fx["status_type"] == "finished"].drop_duplicates("event_id")

    sin_registrar = {}
    for lado in ("home", "away"):
        for tid, nombre in zip(fx[f"{lado}_team_id"], fx[f"{lado}_team"]):
            if int(tid) not in config.EQUIPOS:
                sin_registrar[int(tid)] = nombre

    en_disco = _event_ids_en_disco(season)
    plan = []
    for r in fx.itertuples():
        eid = int(r.event_id)
        if eid in en_disco:
            carpeta = en_disco[eid]
            plan.append((os.path.dirname(carpeta), os.path.basename(carpeta), eid))
            continue
        fecha = (str(r.start_time_utc) or "")[:10]
        local = config.slug_de(r.home_team_id, r.home_team)
        visita = config.slug_de(r.away_team_id, r.away_team)
        base_dir = os.path.join(config.rivals_dir(season), local)
        plan.append((base_dir, f"{fecha}_vs_{visita}_h", eid))

    if verbose:
        nuevos = sum(1 for _, _, e in plan if e not in en_disco)
        print(f"Temporada {season}: {len(fx)} partidos terminados en el fixture · "
              f"{len(plan) - nuevos} ya tienen carpeta · {nuevos} nuevos")
        if sin_registrar:
            print("OJO, equipos sin registrar en config (slug armado del nombre):")
            for tid, n in sorted(sin_registrar.items(), key=lambda x: x[1]):
                print(f"  {tid:>7}  {n}  ->  {config.slugify_equipo(n)}")
    return plan


def scrape_temporada(season, headless=False, include_heatmaps=False,
                     retry_empty=False, refrescar_fixture=False, limite=None):
    """
    Baja todos los partidos terminados de la temporada que falten o estén
    incompletos. `limite` = cortar después de N partidos con trabajo de red
    (para probar o repartir la bajada en varias tandas).

    include_heatmaps=False por default: los heatmaps son ~22 requests por
    partido (el triple que todo lo demás junto). Se pueden completar después
    corriendo de nuevo con include_heatmaps=True: los partidos ya bajados solo
    piden lo que les falta.
    """
    plan = plan_temporada(season, refrescar_fixture=refrescar_fixture)
    stats = {"done": 0, "scraped": 0, "error": 0}
    errores = []
    inicio = time.time()
    with SofascoreClient(headless=headless) as client:
        for i, (base_dir, mk, eid) in enumerate(plan, 1):
            os.makedirs(base_dir, exist_ok=True)
            equipo = os.path.basename(base_dir)
            outcome = _scrape_one(client, mk, eid, base_dir,
                                  include_heatmaps=include_heatmaps,
                                  retry_empty=retry_empty,
                                  label=f"[{i}/{len(plan)}] {equipo}/")
            stats[outcome] += 1
            if outcome == "error":
                errores.append((equipo, mk))
            if outcome != "done":
                if limite and stats["scraped"] + stats["error"] >= limite:
                    print(f"\nCorte por límite ({limite} partidos).")
                    break
                time.sleep(random.uniform(config.MIN_DELAY, config.MAX_DELAY))

    minutos = (time.time() - inicio) / 60
    print(f"\nTemporada {season}: {stats['scraped']} bajados, {stats['done']} ya estaban, "
          f"{stats['error']} con error · {minutos:.0f} min")
    if errores:
        print("Con error (volvé a correr: retoma donde quedó):")
        for equipo, mk in errores:
            print(f"  · {equipo}/{mk}")
    return stats
