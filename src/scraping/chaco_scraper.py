"""
chaco_scraper.py
================
Scraper de SofaScore para los partidos de Chaco For Ever.
Navega directamente a las URLs de la API interna con un browser real para
esquivar Cloudflare, y lee el JSON del body de la página.

Configuración central en config.py (team_id, season, rutas, delays).

Uso rápido:
    from src.scraping.chaco_scraper import run_all, load_matches
    import config
    run_all(load_matches(season="2026"), season="2026")
"""

import os
import re
import json
import time
import random
import importlib.util
from datetime import datetime, timezone

import pandas as pd

import config

SOFASCORE_BASE = config.SOFASCORE_BASE

ENDPOINTS = {
    "event":             "api/v1/event/{mid}",
    "statistics":        "api/v1/event/{mid}/statistics",
    "lineups":           "api/v1/event/{mid}/lineups",
    "incidents":         "api/v1/event/{mid}/incidents",
    "shotmap":           "api/v1/event/{mid}/shotmap",
    "average_positions": "api/v1/event/{mid}/average-positions",
    "graph":             "api/v1/event/{mid}/graph",
    "best_players":      "api/v1/event/{mid}/best-players",
}
HEATMAP_ENDPOINT = "api/v1/event/{mid}/player/{pid}/heatmap"

PLAYER_STAT_FIELDS = {
    "rating":                 "rating",
    "minutesPlayed":          "minutes_played",
    "goals":                  "goals",
    "goalAssist":             "assists",
    "totalPass":              "total_passes",
    "accuratePass":           "accurate_passes",
    "keyPass":                "key_passes",
    "totalCross":             "total_crosses",
    "accurateCross":          "accurate_crosses",
    "totalLongBalls":         "total_long_balls",
    "accurateLongBalls":      "accurate_long_balls",
    "bigChanceCreated":       "big_chances_created",
    "bigChanceMissed":        "big_chances_missed",
    "expectedGoals":          "xg",
    "expectedAssists":        "xa",
    "touches":                "touches",
    "possessionLostCtrl":     "possession_lost",
    "dispossessed":           "dispossessed",
    "onTargetScoringAttempt": "shots_on_target",
    "shotOffTarget":          "shots_off_target",
    "blockedScoringAttempt":  "shots_blocked",
    "totalContest":           "dribbles_attempted",
    "wonContest":             "dribbles_won",
    "totalTackle":            "tackles",
    "interceptionWon":        "interceptions",
    "totalClearance":         "clearances",
    "duelWon":                "duels_won",
    "duelLost":               "duels_lost",
    "aerialWon":              "aerial_duels_won",
    "aerialLost":             "aerial_duels_lost",
    "wasFouled":              "was_fouled",
    "fouls":                  "fouls",
    "totalOffside":           "offsides",
    "saves":                  "saves",
    "goalsPrevented":         "goals_prevented",
}


# ─── Carga del índice de partidos ────────────────────────────────────────────

def load_matches(season=None, path=None):
    """Carga el dict MATCHES desde el archivo de links de la temporada indicada."""
    s = season or config.CURRENT_SEASON
    p = path or config.MATCHES_FILES.get(s)
    if not p or not os.path.exists(p):
        raise FileNotFoundError(f"No se encontró el archivo de matches para temporada {s}: {p}")
    spec = importlib.util.spec_from_file_location("matches_module", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MATCHES


def event_id_from_url(match_url):
    """Extrae el event_id del final de la URL: ...#id:13396470 → '13396470'."""
    return match_url.split(":")[-1].strip()


def is_home_match(match_key):
    return match_key.endswith("_h")


# ─── Driver ──────────────────────────────────────────────────────────────────

def _chrome_major_version():
    """Devuelve el major de Chrome instalado (ej. 149) o None si no se puede leer.
    undetected_chromedriver necesita esto para bajar el chromedriver que matchea
    y no uno más nuevo (causa 'only supports Chrome version N')."""
    import subprocess
    # Windows: leer la versión del registro
    try:
        out = subprocess.run(
            ["reg", "query",
             r"HKCU\Software\Google\Chrome\BLBeacon", "/v", "version"],
            capture_output=True, text=True, timeout=10,
        ).stdout
        m = re.search(r"version\s+REG_SZ\s+(\d+)\.", out)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    # Fallback: leer el ProductVersion del .exe
    for p in (
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ):
        try:
            if os.path.exists(p):
                out = subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     f"(Get-Item '{p}').VersionInfo.ProductVersion"],
                    capture_output=True, text=True, timeout=10,
                ).stdout.strip()
                m = re.match(r"(\d+)\.", out)
                if m:
                    return int(m.group(1))
        except Exception:
            pass
    return None


def _build_driver(headless=True):
    try:
        import undetected_chromedriver as uc
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        version_main = _chrome_major_version()
        driver = uc.Chrome(options=options, version_main=version_main)
        driver.set_page_load_timeout(40)
        return driver, "undetected_chromedriver"
    except Exception as e_uc:
        print(f"  [driver] undetected_chromedriver no disponible ({e_uc}); uso Selenium normal.")
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
        driver.set_page_load_timeout(40)
        return driver, "selenium"


class SofascoreClient:
    """Cliente liviano: navega a una URL de la API y devuelve el JSON parseado."""

    def __init__(self, headless=True, min_delay=2.0, max_delay=4.5):
        self.driver, self.backend = _build_driver(headless=headless)
        self.min_delay = min_delay
        self.max_delay = max_delay

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _read_body_json(self):
        from bs4 import BeautifulSoup
        html = self.driver.page_source
        text = BeautifulSoup(html, "html.parser").get_text().strip()
        if not text:
            return None, "empty"
        low = text[:200].lower()
        if not (text.startswith("{") or text.startswith("[")):
            if "just a moment" in low or "cloudflare" in low or "attention required" in low:
                return None, "blocked"
            return None, "not_json"
        try:
            return json.loads(text), "ok"
        except json.JSONDecodeError:
            return None, "not_json"

    def get_json(self, path, retries=3):
        url = f"{SOFASCORE_BASE}{path}"
        for attempt in range(1, retries + 1):
            try:
                self.driver.get(url)
            except Exception:
                pass
            time.sleep(random.uniform(self.min_delay, self.max_delay))
            data, status = self._read_body_json()
            if status == "ok":
                if isinstance(data, dict) and "error" in data and len(data) == 1:
                    return None
                return data
            if status == "blocked":
                wait = 5 * attempt + random.uniform(0, 3)
                print(f"    [cloudflare] bloqueo, reintento {attempt}/{retries} en {wait:.0f}s...")
                time.sleep(wait)
                continue
            if attempt < retries:
                time.sleep(2)
                continue
            return None
        return None


# ─── Helpers de parseo ───────────────────────────────────────────────────────

def _num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _player_name(player_obj):
    if not isinstance(player_obj, dict):
        return None
    return player_obj.get("shortName") or player_obj.get("name")


# ─── Parsers ────────────────────────────────────────────────────────────────

def parse_event(data, match_key, event_id):
    if not data:
        return None
    ev = data.get("event", data) if isinstance(data, dict) else {}
    home = ev.get("homeTeam", {}) or {}
    away = ev.get("awayTeam", {}) or {}
    hs = ev.get("homeScore", {}) or {}
    aws = ev.get("awayScore", {}) or {}
    tournament = ev.get("tournament", {}) or {}
    unique_t = tournament.get("uniqueTournament", {}) or {}
    season = ev.get("season", {}) or {}
    round_info = ev.get("roundInfo", {}) or {}
    venue = ev.get("venue", {}) or {}
    referee = ev.get("referee", {}) or {}
    status = ev.get("status", {}) or {}

    ts = ev.get("startTimestamp")
    start_iso = (
        datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        if isinstance(ts, (int, float)) else None
    )

    home_score = hs.get("current")
    away_score = aws.get("current")
    chaco_home = is_home_match(match_key)
    chaco_goals = home_score if chaco_home else away_score
    rival_goals = away_score if chaco_home else home_score

    row = {
        "match_key":      match_key,
        "event_id":       event_id,
        "start_time_utc": start_iso,
        "tournament":     unique_t.get("name") or tournament.get("name"),
        "season":         season.get("name") or season.get("year"),
        "round":          round_info.get("round"),
        "status":         status.get("description"),
        "home_team":      home.get("name"),
        "away_team":      away.get("name"),
        "home_team_id":   home.get("id"),
        "away_team_id":   away.get("id"),
        "home_score":     home_score,
        "away_score":     away_score,
        "home_score_ht":  hs.get("period1"),
        "away_score_ht":  aws.get("period1"),
        "chaco_home":     chaco_home,
        "chaco_goals":    chaco_goals,
        "rival_goals":    rival_goals,
        "venue":          venue.get("stadium", {}).get("name") if isinstance(venue.get("stadium"), dict) else None,
        "attendance":     ev.get("attendance"),
        "referee":        referee.get("name"),
    }
    return pd.DataFrame([row])


def parse_statistics(data):
    if not data:
        return None
    periods = data.get("statistics") if isinstance(data, dict) else None
    if not isinstance(periods, list):
        return None
    all_period = next((p for p in periods if p.get("period") == "ALL"), None)
    if all_period is None and periods:
        all_period = periods[0]
    if not all_period:
        return None
    rows = []
    for group in all_period.get("groups", []):
        gname = group.get("groupName")
        for item in group.get("statisticsItems", []):
            rows.append({
                "group":      gname,
                "metric":     item.get("name"),
                "home_val":   _num(item.get("homeValue")),
                "away_val":   _num(item.get("awayValue")),
                "home_total": _num(item.get("homeTotal")),
                "away_total": _num(item.get("awayTotal")),
            })
    return pd.DataFrame(rows) if rows else None


def parse_lineups(data, home_team_name=None, away_team_name=None):
    if not data:
        return None
    names = {"home": home_team_name or "home", "away": away_team_name or "away"}
    formations = {
        "home": (data.get("home", {}) or {}).get("formation"),
        "away": (data.get("away", {}) or {}).get("formation"),
    }
    rows = []
    for side in ("home", "away"):
        team_data = data.get(side, {}) or {}
        for entry in team_data.get("players", []):
            p = entry.get("player", {}) or {}
            stats = entry.get("statistics", {}) or {}
            row = {
                "team_side":     side,
                "team_name":     names[side],
                "formation":     formations[side],
                "player_id":     p.get("id"),
                "player_name":   _player_name(p),
                "full_name":     p.get("name"),
                "position":      entry.get("position") or p.get("position"),
                "jersey_number": entry.get("jerseyNumber") or entry.get("shirtNumber"),
                "is_starter":    not entry.get("substitute", True),
                "is_captain":    entry.get("captain", False),
                "country":       (p.get("country", {}) or {}).get("name"),
                "substitute_in":  None,
                "substitute_out": None,
            }
            for api_key, col in PLAYER_STAT_FIELDS.items():
                row[col] = stats.get(api_key)
            row["yellow_cards"] = None
            row["red_cards"] = None
            rows.append(row)
    return pd.DataFrame(rows) if rows else None


def parse_incidents(data):
    if not data:
        return None
    incidents = data.get("incidents") if isinstance(data, dict) else data
    if not isinstance(incidents, list) or not incidents:
        return None
    rows = []
    for inc in incidents:
        itype = inc.get("incidentType")
        iclass = inc.get("incidentClass")
        is_home = inc.get("isHome")
        minute = inc.get("time")
        added = inc.get("addedTime")
        player = _player_name(inc.get("player")) or inc.get("playerName")
        assist = _player_name(inc.get("assist1"))
        description = ""

        if itype == "card":
            type_out = iclass or "card"
            description = inc.get("reason", "") or ""
        elif itype == "goal":
            type_out = "goal"
            description = iclass or "regular"
        elif itype == "substitution":
            type_out = "substitution"
            player = _player_name(inc.get("playerIn"))
            player_out = _player_name(inc.get("playerOut"))
            description = f"OUT: {player_out}" if player_out else ""
        else:
            type_out = itype
            description = inc.get("text", "") or ""

        rows.append({
            "type":           type_out,
            "minute":         minute,
            "added_time":     added,
            "is_home":        is_home,
            "player":         player,
            "assist":         assist,
            "incident_class": iclass,
            "home_score":     inc.get("homeScore"),
            "away_score":     inc.get("awayScore"),
            "description":    description,
        })
    return pd.DataFrame(rows) if rows else None


def parse_shotmap(data):
    if not data:
        return None
    shots = data.get("shotmap") if isinstance(data, dict) else data
    if not isinstance(shots, list) or not shots:
        return None
    rows = []
    for s in shots:
        coords = s.get("playerCoordinates", {}) or {}
        gmouth = s.get("goalMouthCoordinates", {}) or {}
        p = s.get("player", {}) or {}
        rows.append({
            "time":         s.get("time"),
            "addedTime":    s.get("addedTime"),
            "player_id":    p.get("id"),
            "player_name":  _player_name(p),
            "isHome":       s.get("isHome"),
            "shotType":     s.get("shotType"),
            "situation":    s.get("situation"),
            "bodyPart":     s.get("bodyPart"),
            "xg":           _num(s.get("xg")),
            "xgot":         _num(s.get("xgot")),
            "coord_x":      coords.get("x"),
            "coord_y":      coords.get("y"),
            "goal_mouth_x": gmouth.get("y"),
            "goal_mouth_z": gmouth.get("z"),
        })
    return pd.DataFrame(rows)


def parse_average_positions(data, home_team_name=None, away_team_name=None):
    if not data:
        return None
    names = {"home": home_team_name or "home", "away": away_team_name or "away"}
    rows = []
    for side in ("home", "away"):
        for item in data.get(side, []) or []:
            p = item.get("player", {}) or {}
            rows.append({
                "team_side":    side,
                "team_name":    names[side],
                "player_id":    p.get("id"),
                "player_name":  _player_name(p),
                "average_x":    item.get("averageX"),
                "average_y":    item.get("averageY"),
                "points_count": item.get("pointsCount"),
            })
    return pd.DataFrame(rows) if rows else None


def parse_graph(data):
    if not data:
        return None
    points = data.get("graphPoints") if isinstance(data, dict) else None
    if not isinstance(points, list) or not points:
        return None
    return pd.DataFrame(points)


def parse_best_players(data):
    if not isinstance(data, dict):
        return None
    rows = []
    for key, side in (("bestHomeTeamPlayer", "home"), ("bestAwayTeamPlayer", "away")):
        item = data.get(key)
        if not isinstance(item, dict):
            continue
        p = item.get("player", {}) or {}
        rows.append({
            "team_side":   side,
            "player_id":   p.get("id"),
            "player_name": _player_name(p),
            "value":       item.get("value"),
            "label":       item.get("label"),
        })
    for key, side in (("bestHomePlayers", "home"), ("bestAwayPlayers", "away")):
        for item in data.get(key, []) or []:
            p = item.get("player", {}) or {}
            rows.append({
                "team_side":   side,
                "player_id":   p.get("id"),
                "player_name": _player_name(p),
                "value":       item.get("value"),
                "label":       item.get("label"),
            })
    return pd.DataFrame(rows) if rows else None


# ─── Guardado ────────────────────────────────────────────────────────────────

def _save_raw(match_dir, name, data):
    raw_dir = os.path.join(match_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    with open(os.path.join(raw_dir, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _save_csv(match_dir, filename, df):
    if df is None or df.empty:
        return False
    df.to_csv(os.path.join(match_dir, filename), index=False, encoding="utf-8")
    return True


# ─── Pipeline por partido ────────────────────────────────────────────────────

def fetch_match(client, match_key, match_url, base_dir=None,
                include_heatmaps=True, max_heatmap_players=40):
    """
    Baja todos los endpoints de un partido, guarda raw JSON + clean CSV.
    Devuelve dict {endpoint: bool} indicando qué se obtuvo.
    """
    if base_dir is None:
        base_dir = config.season_data_dir()

    mid = event_id_from_url(match_url)
    match_dir = os.path.join(base_dir, match_key)
    os.makedirs(match_dir, exist_ok=True)
    results = {}

    raw = {}
    for ep, tmpl in ENDPOINTS.items():
        data = client.get_json(tmpl.format(mid=mid))
        raw[ep] = data
        if data is not None:
            _save_raw(match_dir, ep, data)
        results[ep] = data is not None

    home_name = away_name = None
    ev = raw.get("event")
    if isinstance(ev, dict):
        e = ev.get("event", ev)
        home_name = (e.get("homeTeam", {}) or {}).get("name")
        away_name = (e.get("awayTeam", {}) or {}).get("name")

    df_event    = parse_event(raw.get("event"), match_key, mid)
    df_stats    = parse_statistics(raw.get("statistics"))
    df_lineups  = parse_lineups(raw.get("lineups"), home_name, away_name)
    df_incidents= parse_incidents(raw.get("incidents"))
    df_shotmap  = parse_shotmap(raw.get("shotmap"))
    df_avgpos   = parse_average_positions(raw.get("average_positions"), home_name, away_name)
    df_graph    = parse_graph(raw.get("graph"))
    df_best     = parse_best_players(raw.get("best_players"))

    if df_lineups is not None and df_incidents is not None:
        df_lineups = _enrich_lineups_from_incidents(df_lineups, df_incidents)

    _save_csv(match_dir, "event_clean.csv",             df_event)
    _save_csv(match_dir, "statistics_clean.csv",        df_stats)
    _save_csv(match_dir, "lineups_clean.csv",           df_lineups)
    _save_csv(match_dir, "incidents_clean.csv",         df_incidents)
    _save_csv(match_dir, "shotmap_clean.csv",           df_shotmap)
    _save_csv(match_dir, "average_positions_clean.csv", df_avgpos)
    _save_csv(match_dir, "momentum_clean.csv",          df_graph)
    _save_csv(match_dir, "best_players_clean.csv",      df_best)

    if include_heatmaps and df_lineups is not None:
        hm_rows, hm_raw = [], {}
        mins = pd.to_numeric(df_lineups["minutes_played"], errors="coerce").fillna(0)
        played = df_lineups[mins > 0]
        for _, pl in played.head(max_heatmap_players).iterrows():
            pid = pl.get("player_id")
            if not pid:
                continue
            hm = client.get_json(HEATMAP_ENDPOINT.format(mid=mid, pid=int(pid)))
            if not hm:
                continue
            hm_raw[str(int(pid))] = hm
            for pt in hm.get("heatmap", []) or []:
                hm_rows.append({
                    "player_id":   int(pid),
                    "player_name": pl.get("player_name"),
                    "team_side":   pl.get("team_side"),
                    "team_name":   pl.get("team_name"),
                    "x":           pt.get("x"),
                    "y":           pt.get("y"),
                })
        if hm_raw:
            _save_raw(match_dir, "heatmaps", hm_raw)
        if hm_rows:
            _save_csv(match_dir, "player_heatmaps_clean.csv", pd.DataFrame(hm_rows))
            results["heatmaps"] = True
        else:
            results["heatmaps"] = False

    return results


def _enrich_lineups_from_incidents(df_lineups, df_incidents):
    subs = df_incidents[df_incidents["type"] == "substitution"]
    in_min, out_min = {}, {}
    for _, s in subs.iterrows():
        m = s.get("minute")
        player_in = s.get("player")
        if player_in:
            in_min[player_in] = m
        desc = str(s.get("description", ""))
        if desc.startswith("OUT: "):
            out_min[desc[5:]] = m

    cards = df_incidents[df_incidents["type"].isin(["yellow", "red", "yellowRed"])]
    yellow, red = {}, {}
    for _, c in cards.iterrows():
        name = c.get("player")
        if not name:
            continue
        if c.get("type") == "yellow":
            yellow[name] = yellow.get(name, 0) + 1
        else:
            red[name] = red.get(name, 0) + 1

    df = df_lineups.copy()
    df["substitute_in"]  = df["player_name"].map(in_min)
    df["substitute_out"] = df["player_name"].map(out_min)
    df["yellow_cards"]   = df["player_name"].map(yellow)
    df["red_cards"]      = df["player_name"].map(red)
    return df


# ─── Índice maestro ──────────────────────────────────────────────────────────

def build_matches_index(match_keys=None, base_dir=None, out=None):
    base_dir = base_dir or config.season_data_dir()
    out = out or config.INDEX_FILE
    if match_keys is None:
        match_keys = sorted(d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)))
    rows = []
    for mk in match_keys:
        ev_path = os.path.join(base_dir, mk, "event_clean.csv")
        if os.path.exists(ev_path):
            rows.append(pd.read_csv(ev_path).iloc[0].to_dict())
        else:
            m = re.match(r"(\d{4}-\d{2}-\d{2})", mk)
            rows.append({"match_key": mk, "start_time_utc": m.group(1) if m else None,
                         "chaco_home": is_home_match(mk)})
    df = pd.DataFrame(rows)
    if "start_time_utc" in df.columns:
        df = df.sort_values("start_time_utc")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"Índice maestro guardado: {out}  ({len(df)} partidos)")
    return df


def _match_done(match_dir):
    needed = ["event_clean.csv", "statistics_clean.csv",
              "lineups_clean.csv", "incidents_clean.csv", "shotmap_clean.csv"]
    return all(os.path.exists(os.path.join(match_dir, f)) for f in needed)


def run_all(match_urls, season=None, skip_existing=True, headless=True,
            include_heatmaps=True, rebuild_index=True):
    """
    Baja todos los partidos del dict {match_key: url}.
    skip_existing=True saltea los que ya tienen los archivos clave.
    """
    base_dir = config.season_data_dir(season)
    client = SofascoreClient(headless=headless)
    print(f"Backend: {client.backend} | Temporada: {season or config.CURRENT_SEASON}\n")
    try:
        for match_key, match_url in match_urls.items():
            match_dir = os.path.join(base_dir, match_key)
            if skip_existing and _match_done(match_dir):
                print(f"-- Saltando (ya existe): {match_key}")
                continue
            print(f"\n== {match_key} ==  (id {event_id_from_url(match_url)})")
            try:
                res = fetch_match(client, match_key, match_url, base_dir,
                                  include_heatmaps=include_heatmaps)
                for ep, ok in res.items():
                    print(f"   {ep:<18}: {'OK' if ok else 'sin datos'}")
            except Exception as e:
                print(f"   ERROR: {e}")
            time.sleep(random.uniform(config.MIN_DELAY, config.MAX_DELAY))
    finally:
        client.close()
    if rebuild_index:
        build_matches_index(list(match_urls.keys()), base_dir)
    print("\nScraping completado.")


if __name__ == "__main__":
    matches = load_matches()
    run_all(matches)
