# -*- coding: utf-8 -*-
"""
transfermarkt_scraper.py
========================
Scraper de Transfermarkt para armar la ficha de un refuerzo: bio, trayectoria
de clubes y rendimiento por competición. Pensado para el notebook de refuerzos.

Reusa el browser real del proyecto (undetected_chromedriver) que ya esquiva el
anti-bot, y respeta los delays de config. Cachea la respuesta cruda por jugador
en data/refuerzos/{id}/ para no volver a pegarle a la web (idempotente).

Uso:
    from src.scraping.transfermarkt_scraper import fetch_player
    ficha = fetch_player("https://www.transfermarkt.com.ar/matias-romero/profil/spieler/853464")

Nota: aunque un jugador ya sea refuerzo confirmado de Chaco For Ever, Transfermarkt
puede todavía mostrarlo como "Sin equipo" o en su club anterior. Eso es normal.
"""
import os
import re
import json
import time
import random

from bs4 import BeautifulSoup

import config
from src.scraping.chaco_scraper import _build_driver

TM_BASE = "https://www.transfermarkt.com.ar"
_CACHE_DIR = os.path.join("data", "refuerzos")


# ─── URLs ────────────────────────────────────────────────────────────────────
def player_id_and_slug(url):
    """Saca (id, slug) de cualquier URL de jugador de Transfermarkt."""
    m = re.search(r"/([^/]+)/[a-z]+/spieler/(\d+)", url)
    if m:
        return m.group(2), m.group(1)
    m = re.search(r"/spieler/(\d+)", url)
    if m:
        return m.group(1), "jugador"
    raise ValueError(f"No pude extraer el id de jugador de: {url}")


def _urls(pid, slug):
    return {
        "profil":         f"{TM_BASE}/{slug}/profil/spieler/{pid}",
        "transfers_json": f"{TM_BASE}/ceapi/transferHistory/list/{pid}",
        "leistung":       f"{TM_BASE}/{slug}/leistungsdaten/spieler/{pid}/plus/1",
        "temporadas":     f"{TM_BASE}/{slug}/leistungsdatendetails/spieler/{pid}/plus/1?saison=ges",
    }


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _int(s):
    s = (s or "").replace(".", "").replace("'", "").strip()
    return int(s) if s.lstrip("-").isdigit() else None


def _get(driver, url, min_d, max_d):
    try:
        driver.get(url)
    except Exception:
        pass
    time.sleep(random.uniform(min_d, max_d))
    return driver.page_source


# ─── Parsers (validados contra el HTML real) ─────────────────────────────────
def _parse_profile(html):
    soup = BeautifulSoup(html, "html.parser")
    bio = {}
    h1 = soup.select_one("h1")
    nombre = h1.get_text(" ", strip=True) if h1 else None
    if nombre:
        nombre = re.sub(r"^#?\s*\d+\s+", "", nombre).strip()   # saca el nº de camiseta del H1
    bio["nombre"] = nombre
    mv = soup.select_one(".data-header__market-value-wrapper")
    if mv:
        txt = mv.get_text(" ", strip=True)
        bio["valor_mercado"] = re.split(r"Última|Last|revisi", txt)[0].strip()
    labels = {
        "Nombre en país de origen": "nombre_completo",
        "F. Nacim./Edad": "nacimiento",
        "Lugar de nac.": "lugar_nacimiento",
        "Altura": "altura",
        "Nacionalidad": "nacionalidad",
        "Posición": "posicion",
        "Pie": "pie",
        "Club actual": "club_actual",
    }
    its = soup.select(".info-table__content")
    for i in range(0, len(its) - 1, 2):
        k = its[i].get_text(" ", strip=True).rstrip(":")
        v = its[i + 1].get_text(" ", strip=True)
        if k in labels:
            bio[labels[k]] = v
    # rol = la posición específica (lo que va después del guion en "Delantero - Delantero centro")
    pos = bio.get("posicion") or ""
    bio["rol"] = pos.split(" - ")[-1].strip() if " - " in pos else (pos or None)
    return bio


def _logo_url(club):
    url = (club or {}).get("clubEmblemMobile") or (club or {}).get("clubEmblem-2x") \
        or (club or {}).get("clubEmblem-1x")
    if not url:
        return None
    return url.replace(".net//", ".net/")   # TM manda un doble slash


def _parse_transfers(data):
    """data = JSON del endpoint ceapi/transferHistory. Devuelve movimientos, clubes y logos."""
    movimientos = []
    logos = {}
    for t in data.get("transfers", []):
        movimientos.append({
            "temporada": t.get("season"),
            "fecha": t.get("date"),
            "desde": (t.get("from") or {}).get("clubName"),
            "hacia": (t.get("to") or {}).get("clubName"),
            "valor": t.get("fee") or t.get("marketValue"),
        })
        for side in ("from", "to"):
            c = t.get(side) or {}
            nm, u = c.get("clubName"), _logo_url(c)
            if nm and u and nm not in logos:
                logos[nm] = u
    # clubes donde JUGÓ (excluye estados no-club), en orden cronológico
    ignorar = {"sin equipo", "retirado", "sin club", "-", None, ""}
    orden = list(reversed(movimientos))  # antiguo -> reciente
    secuencia = []
    for mv in orden:
        for c in (mv["desde"], mv["hacia"]):
            if c and c.strip().lower() not in ignorar:
                if not secuencia or secuencia[-1] != c:
                    secuencia.append(c)
    clubes_unicos = list(dict.fromkeys(secuencia))
    return movimientos, secuencia, clubes_unicos, logos


def _trayectoria_detallada(movimientos, logos):
    """Reconstruye los pasos por cada club con años (desde las fechas de transferencia).
    Devuelve, en orden cronológico: [{club, desde, hasta, anios, logo_url, es_chaco}]."""
    ignorar = {"sin equipo", "retirado", "sin club", "-", None, ""}
    stints = []
    movs = list(reversed(movimientos))  # antiguo -> reciente
    for i, mv in enumerate(movs):
        frm, to = mv.get("desde"), mv.get("hacia")
        yr = _anio(mv.get("fecha"))
        if i == 0 and frm and frm.strip().lower() not in ignorar:
            stints.append({"club": frm, "desde": None, "hasta": None})
        for s in reversed(stints):                 # cerrar el stint abierto del club que deja
            if s["club"] == frm and s["hasta"] is None:
                s["hasta"] = yr
                break
        if to and to.strip().lower() not in ignorar:
            stints.append({"club": to, "desde": yr, "hasta": None})
    for s in stints:
        d, h = s["desde"], s["hasta"]
        if d and h and d != h:
            s["anios"] = f"{d}–{h}"
        elif d and h:
            s["anios"] = f"{d}"
        elif d and not h:
            s["anios"] = f"{d}–hoy"
        elif h and not d:
            s["anios"] = f"hasta {h}"
        else:
            s["anios"] = ""
        s["logo_url"] = logos.get(s["club"])
        s["es_chaco"] = s["club"] == "Chaco For Ever"
    return stints


def _descargar_logos(trayectoria, cache_dir):
    """Baja los escudos de los clubes al cache (data/refuerzos/{id}/logos/) y guarda
    la ruta local (relativa a la raíz del proyecto) en cada paso."""
    import requests
    ldir = os.path.join(cache_dir, "logos")
    os.makedirs(ldir, exist_ok=True)
    for s in trayectoria:
        url = s.get("logo_url")
        if not url:
            continue
        slug = re.sub(r"[^a-z0-9]+", "_", (s["club"] or "").lower()).strip("_")
        path = os.path.join(ldir, f"{slug}.png")
        if not os.path.exists(path):
            try:
                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
                if r.status_code == 200 and r.content:
                    open(path, "wb").write(r.content)
                    time.sleep(random.uniform(0.4, 1.0))
            except Exception:
                pass
        if os.path.exists(path):
            s["logo"] = path.replace("\\", "/")
    return trayectoria


def _parse_career(html):
    """Rendimiento por competición (PJ, goles, asistencias, minutos) + total."""
    soup = BeautifulSoup(html, "html.parser")
    filas, total = [], None
    for r in soup.select(".grid-row"):
        cells = [c.get_text(" ", strip=True) for c in r.select(".tm-grid__cell")]
        if len(cells) < 5 or not cells[0] or not cells[-1].endswith("'"):
            continue
        fila = {
            "competicion": cells[0].rstrip(":"),
            "partidos": _int(cells[1]),
            "goles": _int(cells[2]),
            "asistencias": _int(cells[3]),
            "minutos": _int(cells[-1]),
        }
        if cells[0].startswith("Total"):
            total = fila
        else:
            filas.append(fila)
    return filas, total


def _parse_por_temporada(html):
    """Rendimiento por temporada (año) y competición. Página de detalle saison=ges.
    Columnas verificadas por posición: partidos=col3, goles=col5, asist=col6, minutos=última."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for r in soup.select(".grid-row"):
        c = [x.get_text(" ", strip=True) for x in r.select(".tm-grid__cell")]
        if len(c) < 16 or not c[0].isdigit() or not c[-1].endswith("'"):
            continue
        out.append({
            "anio": int(c[0]),
            "competicion": c[1],
            "partidos": _int(c[3]),
            "goles": _int(c[5]),
            "asistencias": _int(c[6]),
            "minutos": _int(c[-1]),
        })
    return out


def _carrera_desde_temporadas(por_temporada):
    """Carrera por competición + total, sumando la tabla por temporada (fuente
    confiable). Evita la página resumen de TM que a veces trae datos parciales."""
    from collections import defaultdict
    agg = defaultdict(lambda: {"partidos": 0, "goles": 0, "asistencias": 0, "minutos": 0})
    tot = {"partidos": 0, "goles": 0, "asistencias": 0, "minutos": 0}
    for t in por_temporada:
        for k in ("partidos", "goles", "asistencias", "minutos"):
            v = t.get(k) or 0
            agg[t["competicion"]][k] += v
            tot[k] += v
    carrera = [{"competicion": c, **v} for c, v in agg.items()]
    carrera.sort(key=lambda x: -x["partidos"])
    return carrera, (tot if por_temporada else None)


def _anio(fecha):
    m = re.search(r"(\d{4})", fecha or "")
    return int(m.group(1)) if m else None


def es_retorno(ficha):
    """True si el jugador YA jugó en Chaco For Ever antes de esta llegada
    (Chaco aparece en un paso que no es el último de su trayectoria)."""
    td = ficha.get("trayectoria_detallada") or []
    idx = [i for i, s in enumerate(td) if s["club"] == "Chaco For Ever"]
    return bool(idx) and any(i != len(td) - 1 for i in idx)


def rendimiento_ultimo_club(ficha):
    """Cómo le fue en el club de DONDE VIENE (el último donde REALMENTE jugó).
    Descarta del final el destino Chaco y una vuelta de préstamo (club que ya
    figuraba antes en la carrera). Devuelve None si no hay datos."""
    td = ficha.get("trayectoria_detallada") or []
    pasos = list(td)
    while pasos:                                    # limpiar la cola redundante
        ult = pasos[-1]
        previos = {s["club"] for s in pasos[:-1]}
        es_hoy = str(ult.get("anios", "")).endswith("hoy")
        if ult["club"] == "Chaco For Ever" or (es_hoy and ult["club"] in previos):
            pasos = pasos[:-1]
        else:
            break
    stint = next((s for s in reversed(pasos) if s["club"] != "Chaco For Ever"), None)
    if stint:
        club = stint["club"]
        de, ha = stint.get("desde"), stint.get("hasta")
        anios = set(range(de, (ha or de) + 1)) if de else ({ha} if ha else None)
    else:
        club = ficha["trayectoria"][-1] if ficha.get("trayectoria") else None
        anios = None
    if not club:
        return None
    filas = [t for t in ficha.get("por_temporada", [])
             if anios is None or t["anio"] in anios]
    pj = sum(f["partidos"] or 0 for f in filas)
    g = sum(f["goles"] or 0 for f in filas)
    a = sum(f["asistencias"] or 0 for f in filas)
    mins = sum(f["minutos"] or 0 for f in filas)
    mpp = round(mins / pj, 1) if pj else 0
    if pj == 0:
        veredicto = "No sumó minutos"
    elif pj <= 5:                       # muestra chica: jugó pocos partidos
        veredicto = "Jugó pocos partidos"
    elif mpp >= 70:
        veredicto = "Titular habitual"
    elif mpp >= 45:
        veredicto = "Rotativo (arranca o entra según el partido)"
    else:
        veredicto = "Poco rodaje: mayormente suplente"
    return {
        "club": club,
        "anios": sorted({f["anio"] for f in filas}),
        "partidos": pj, "goles": g, "asistencias": a, "minutos": mins,
        "min_por_partido": mpp, "veredicto": veredicto,
    }


# ─── API principal ───────────────────────────────────────────────────────────
def fetch_player(url, headless=True, driver=None, use_cache=True,
                 min_delay=None, max_delay=None):
    """Devuelve la ficha completa del jugador. Cachea el crudo en data/refuerzos/{id}/."""
    pid, slug = player_id_and_slug(url)
    min_d = min_delay if min_delay is not None else config.MIN_DELAY
    max_d = max_delay if max_delay is not None else config.MAX_DELAY
    cache = os.path.join(_CACHE_DIR, pid)
    os.makedirs(cache, exist_ok=True)
    fp = {
        "profil": os.path.join(cache, "profil.html"),
        "transfers_json": os.path.join(cache, "transfers.json"),
        "leistung": os.path.join(cache, "leistung.html"),
        "temporadas": os.path.join(cache, "temporadas.html"),
    }
    urls = _urls(pid, slug)

    need = (not use_cache) or any(not os.path.exists(p) for p in fp.values())
    own_driver = False
    if need:
        if driver is None:
            driver, _ = _build_driver(headless=headless)
            own_driver = True
        try:
            if not use_cache or not os.path.exists(fp["profil"]):
                open(fp["profil"], "w", encoding="utf-8").write(_get(driver, urls["profil"], min_d, max_d))
            if not use_cache or not os.path.exists(fp["transfers_json"]):
                body = BeautifulSoup(_get(driver, urls["transfers_json"], min_d, max_d), "html.parser").get_text().strip()
                open(fp["transfers_json"], "w", encoding="utf-8").write(body)
            if not use_cache or not os.path.exists(fp["leistung"]):
                open(fp["leistung"], "w", encoding="utf-8").write(_get(driver, urls["leistung"], min_d, max_d))
            if not use_cache or not os.path.exists(fp["temporadas"]):
                open(fp["temporadas"], "w", encoding="utf-8").write(_get(driver, urls["temporadas"], min_d, max_d))
        finally:
            if own_driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    bio = _parse_profile(open(fp["profil"], encoding="utf-8").read())
    try:
        tj = json.loads(open(fp["transfers_json"], encoding="utf-8").read())
    except Exception:
        tj = {"transfers": []}
    movimientos, secuencia, clubes, logos = _parse_transfers(tj)
    por_temporada = _parse_por_temporada(open(fp["temporadas"], encoding="utf-8").read())
    carrera, total = _carrera_desde_temporadas(por_temporada)
    trayectoria_det = _trayectoria_detallada(movimientos, logos)
    _descargar_logos(trayectoria_det, cache)   # idempotente: no re-baja lo cacheado

    ficha = {
        "id": pid,
        "url": url,
        "bio": bio,
        "movimientos": movimientos,       # cada transferencia
        "trayectoria": secuencia,          # clubes en orden cronológico (con repeticiones de vuelta)
        "trayectoria_detallada": trayectoria_det,  # pasos con años + logo local
        "clubes": clubes,                  # clubes únicos donde jugó
        "carrera": carrera,                # rendimiento por competición
        "carrera_total": total,            # fila Total
        "por_temporada": por_temporada,    # rendimiento por temporada+competición
    }
    ficha["ultimo_club"] = rendimiento_ultimo_club(ficha)
    ficha["es_retorno"] = es_retorno(ficha)
    return ficha


def resumen_texto(ficha):
    """Resumen legible de una ficha (para pegar o revisar rápido)."""
    b, t = ficha["bio"], ficha["carrera_total"] or {}
    uc = ficha.get("ultimo_club") or {}
    L = []
    L.append(f"# {b.get('nombre','?')}  ({b.get('nombre_completo','')})")
    L.append(f"- **Rol:** {b.get('rol','?')}  (ficha: {b.get('posicion','?')})")
    L.append(f"- Pie: {b.get('pie','?')} · Altura: {b.get('altura','?')}")
    L.append(f"- Nacimiento: {b.get('nacimiento','?')} · {b.get('lugar_nacimiento','')} ({b.get('nacionalidad','')})")
    L.append(f"- Valor de mercado: {b.get('valor_mercado','?')} · Club en TM: {b.get('club_actual','?')}")
    if ficha["clubes"]:
        L.append(f"- Clubes: {' → '.join(ficha['clubes'])}")
    if t:
        L.append(f"- Carrera: {t.get('partidos')} PJ · {t.get('goles')} goles · "
                 f"{t.get('asistencias')} asistencias · {t.get('minutos')} min")
    if uc and uc.get("club"):
        anios = "-".join(str(a) for a in (uc["anios"][:1] + (uc["anios"][-1:] if len(uc["anios"]) > 1 else [])))
        L.append(f"- **Último club — {uc['club']} ({anios}):** {uc['partidos']} PJ · "
                 f"{uc['minutos']} min · {uc['min_por_partido']}′/PJ · {uc['goles']} goles "
                 f"→ **{uc['veredicto']}**")
    L.append("")
    L.append("| Competición | PJ | Goles | Asist. | Minutos |")
    L.append("|---|---:|---:|---:|---:|")
    d = lambda v: "-" if v is None else v
    for c in ficha["carrera"]:
        L.append(f"| {c['competicion']} | {d(c['partidos'])} | {d(c['goles'])} | {d(c['asistencias'])} | {d(c['minutos'])} |")
    pt = ficha.get("por_temporada") or []
    if pt:
        L.append("")
        L.append("**Últimas temporadas** (año · competición):")
        L.append("")
        L.append("| Año | Competición | PJ | Goles | Asist. | Minutos |")
        L.append("|---|---|---:|---:|---:|---:|")
        for c in pt[:6]:
            L.append(f"| {c['anio']} | {c['competicion']} | {d(c['partidos'])} | "
                     f"{d(c['goles'])} | {d(c['asistencias'])} | {d(c['minutos'])} |")
    return "\n".join(L)
