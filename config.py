"""
config.py — Configuración central del proyecto Chaco For Ever.

Todos los módulos importan desde acá. Para cambiar de temporada, actualizar
CURRENT_SEASON y asegurarse de que:
  1. MATCHES_FILES[season] apunta al archivo de URLs correcto
  2. SEASON_IDS[season] tiene el ID de la temporada en SofaScore
  3. El directorio se crea automáticamente al scrapear
"""
import os

# ─── Temporada activa ────────────────────────────────────────────────────────

CURRENT_SEASON = "2026"   # cambiar a "2026" cuando empiece la nueva temporada

# ─── SofaScore IDs ──────────────────────────────────────────────────────────

CHACO_TEAM_ID        = 252726
CHACO_SLUG           = "chaco-for-ever"
UNIQUE_TOURNAMENT_ID = 703        # Primera Nacional (argentina)
SOFASCORE_BASE       = "https://www.sofascore.com/"

SEASON_IDS = {
    "2025": 71009,
    "2026": 87940,
}

# ─── Rutas de datos ──────────────────────────────────────────────────────────

_ROOT = os.path.dirname(os.path.abspath(__file__))


def _load_dotenv(path=None):
    """Carga pares CLAVE=VALOR del archivo .env en os.environ (sin pisar lo ya
    seteado). Dependency-free: no necesita el paquete python-dotenv.
    El .env está en .gitignore, así que las keys no se commitean."""
    path = path or os.path.join(_ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


_load_dotenv()

# Estructura unificada: todo bajo data/temporadas/{season}/ y outputs/temporadas/{season}/
# Los datos de una temporada viven en data/temporadas/{season}/partidos
# Template — usar con .format(season=...) o la función helper season_data_dir()
_SEASON_DATA_DIR = os.path.join(_ROOT, "data", "temporadas", "{season}", "partidos")

MATCHES_FILES = {
    "2025": os.path.join(_ROOT, "data", "Teams links", "Chaco_For_Ever_Matches_Season_2025.py"),
    "2026": os.path.join(_ROOT, "data", "Teams links", "Chaco_For_Ever_Matches_Season_2026.py"),
}

INDEX_FILE = os.path.join(_ROOT, "data", "matches_index.csv")

# Templates de datos — usar con .format(season=...) o la función helper
_RIVALS_DIR    = os.path.join(_ROOT, "data", "temporadas", "{season}", "rivals")
_STANDINGS_FILE = os.path.join(_ROOT, "data", "temporadas", "{season}", "standings.csv")

# Templates de outputs — TODO anidado por temporada, espejando data/temporadas/{season}/
_SEASON_PLOTS_DIR   = os.path.join(_ROOT, "outputs", "temporadas", "{season}", "graficos")
_SEASON_REPORTS_DIR = os.path.join(_ROOT, "outputs", "temporadas", "{season}", "informes")
_MATCH_OUTPUTS_DIR  = os.path.join(_ROOT, "outputs", "temporadas", "{season}", "partidos", "{match_key}")
_PRE_OUTPUTS_DIR    = os.path.join(_ROOT, "outputs", "temporadas", "{season}", "pre_partido", "{rival}")

OUTPUTS_DIR = os.path.join(_ROOT, "outputs")

# ─── Rivales ─────────────────────────────────────────────────────────────────
# Las claves coinciden con el slug que aparece en los match_keys (parte entre _vs_ y _h/_a)

# Los 18 rivales de la temporada 2026 (20 fechas: Acassuso y San Telmo se repiten).
# Slugs e ids tomados de los match_keys y del event.json de cada partido.
RIVALS_2026 = {
    "acassuso":                  {"id": 112491, "name": "Acassuso"},
    "all_boys":                  {"id": 36834,  "name": "All Boys"},
    "almirante_brown":           {"id": 43740,  "name": "Almirante Brown"},
    "central_norte":             {"id": 255426, "name": "Central Norte de Salta"},
    "ciudad_de_bolivar":         {"id": 340432, "name": "Ciudad de Bolívar"},
    "colon":                     {"id": 3207,   "name": "Club Atlético Colón"},
    "defensores_de_belgrano":    {"id": 52215,  "name": "Defensores de Belgrano"},
    "deportivo_madryn":          {"id": 222120, "name": "Deportivo Madryn"},
    "deportivo_moron":           {"id": 93109,  "name": "Deportivo Morón"},
    "estudiantes_caseros":       {"id": 93107,  "name": "Estudiantes de Buenos Aires"},
    "ferro_carril_oeste":        {"id": 36841,  "name": "Club Ferro Carril Oeste"},
    "gimnasia_de_jujuy":         {"id": 5292,   "name": "Gimnasia Jujuy"},
    "godoy_cruz":                {"id": 6074,   "name": "Godoy Cruz"},
    "los_andes":                 {"id": 112497, "name": "Los Andes"},
    "mitre":                     {"id": 255425, "name": "CA Mitre"},
    "racing_de_cordoba":         {"id": 273657, "name": "Racing de Córdoba"},
    "san_miguel":                {"id": 264945, "name": "San Miguel"},
    "san_telmo":                 {"id": 213361, "name": "San Telmo"},
}

# Rivales que solo aparecen en 2025: sus slugs son distintos (ej. 'club_mitre',
# 'gimnasia_jujuy'), así que conviven con los de 2026 sin pisarse.
RIVALS_2025 = {
    "agropecuario":              {"id": 265787, "name": "Agropecuario Argentino"},
    "chacarita":                 {"id": 3214,   "name": "Club Atlético Chacarita Juniors"},
    "club_mitre":                {"id": 255425, "name": "CA Mitre"},
    "defensores_unidos":         {"id": 93515,  "name": "Defensores Unidos"},
    "estudiantes_de_rio_cuarto": {"id": 266694, "name": "Estudiantes de Río Cuarto"},
    "gimnasia_jujuy":            {"id": 5292,   "name": "Gimnasia Jujuy"},
    "gimnasia_y_esgrima_mendoza":{"id": 188441, "name": "Gimnasia y Esgrima Mendoza"},
    "nueva_chicago":             {"id": 3200,   "name": "Nueva Chicago"},
    "talleres_remedios":         {"id": 201162, "name": "Talleres Remedios de Escalada"},
    "temperley":                 {"id": 112499, "name": "Temperley"},
}

# Lookup único por slug: el pipeline resuelve el rival por el match_key, sin
# importar la temporada. 2026 pisa a 2025 si algún slug coincidiera.
RIVALS = {**RIVALS_2025, **RIVALS_2026}

# ─── Jugadores que se fueron del club ────────────────────────────────────────
# Poné acá (uno por línea, entre comillas) a los jugadores de Chaco que dejaron
# el club y NO van a sumar más minutos. Usá el nombre tal como aparece en los
# datos (inicial + apellido, ej. "G. Pacheco" o "M. S. Romero").
#
# Efecto: se EXCLUYEN del pre-partido y del post-partido (no tiene sentido
# analizar a alguien que ya no está). PERO siguen contando en el análisis de
# TEMPORADA, para no perder lo que aportaron mientras estuvieron.
#
# Si un jugador vuelve, borralo (o comentalo con #) de esta lista y vuelve a
# aparecer en todos lados automáticamente.
JUGADORES_FUERA = [
    # "G. Pacheco",
    # "L. Marinucci",
]


def jugadores_fuera():
    """Set en minúsculas de los jugadores dados de baja (para comparar)."""
    return {n.strip().lower() for n in JUGADORES_FUERA if n and n.strip()}


def excluir_jugadores_fuera(df, col="player_name"):
    """
    Devuelve el DataFrame sin las filas de los jugadores que se fueron (matchea
    por nombre, sin distinguir mayúsculas ni espacios de sobra). Si la lista
    está vacía o la columna no existe, devuelve el df sin cambios.

    Usar SOLO en el pre-partido y el post-partido; el análisis de temporada no
    lo llama, así que ahí los jugadores dados de baja siguen contando.
    """
    fuera = jugadores_fuera()
    if df is None or not fuera or getattr(df, "empty", True):
        return df
    if col not in getattr(df, "columns", []):
        return df
    keep = ~df[col].astype(str).str.strip().str.lower().isin(fuera)
    return df[keep].reset_index(drop=True)


# ─── Scraping ────────────────────────────────────────────────────────────────

MIN_DELAY          = 6    # segundos entre requests
MAX_DELAY          = 12
RIVAL_LAST_MATCHES = 3    # mínimo de partidos para considerar "ya scrapeado" un rival
                          # (el scraping en sí baja TODOS los partidos de la temporada,
                          # no solo estos — ver rivals_scraper.scrape_rival_recent)

# ─── Pipeline de video (Fase B) ──────────────────────────────────────────────

MODELS_DIR = os.path.join(_ROOT, "models")

# Backend de modelos:
#   "roboflow" → paquete `inference`, descarga los modelos con la API key (recomendado)
#   "local"    → pesos .pt en MODELS_DIR (entrenados aparte)
VIDEO_MODEL_BACKEND = "roboflow"

# Modelos en Roboflow Universe (backend "roboflow").
# El de jugadores ya incluye la pelota como clase 0, así que con player+pitch
# alcanza. El de pelota es un refinamiento opcional.
# Si una versión deja de existir, ajustar el número acá.
ROBOFLOW_MODELS = {
    "player_detection": "football-players-detection-3zvbc/12",
    "pitch_detection":  "football-field-detection-f07vi/15",
    "ball_detection":   "football-ball-detection-rejhg/4",   # opcional
}

# Pesos locales (backend "local").
VIDEO_MODELS = {
    "player_detection": os.path.join(MODELS_DIR, "football-player-detection.pt"),
    "pitch_detection":  os.path.join(MODELS_DIR, "football-pitch-detection.pt"),
    "ball_detection":   os.path.join(MODELS_DIR, "football-ball-detection.pt"),
}

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov")

# Frames por segundo a procesar (el video corre a ~25-30; muestrear baja el costo)
VIDEO_SAMPLE_FPS = 5


def roboflow_api_key():
    """API key de Roboflow desde la variable de entorno ROBOFLOW_API_KEY.
    En un notebook: os.environ['ROBOFLOW_API_KEY'] = 'tu_key' antes de procesar."""
    return os.environ.get("ROBOFLOW_API_KEY", "").strip()

# ─── Informes narrativos (LLM) ──────────────────────────────────────────────
# Proveedor del modelo de lenguaje para los informes:
#   "nvidia"    -> build.nvidia.com (NIM), GRATIS. Key en NVIDIA_API_KEY.
#                  Endpoint compatible con OpenAI; no requiere tarjeta.
#   "anthropic" -> API de Claude (paga). Key en ANTHROPIC_API_KEY.
REPORT_PROVIDER = "nvidia"

# NVIDIA NIM (gratis). Cambiar NVIDIA_MODEL por cualquiera del catálogo de
# build.nvidia.com (ej. "meta/llama-3.3-70b-instruct",
# "nvidia/llama-3.1-nemotron-70b-instruct", "deepseek-ai/deepseek-r1").
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL    = "meta/llama-3.3-70b-instruct"

# Anthropic (alternativa paga)
ANTHROPIC_MODEL = "claude-sonnet-4-6"


def report_api_key():
    """API key del proveedor de informes activo (REPORT_PROVIDER)."""
    if REPORT_PROVIDER == "anthropic":
        return os.environ.get("ANTHROPIC_API_KEY", "").strip()
    return os.environ.get("NVIDIA_API_KEY", "").strip()

# ─── API-Football (api-sports.io) — fuente alternativa a SofaScore ───────────
# Plan free: 100 requests/día. Key del dashboard de https://www.api-football.com/
# Host directo de API-Sports (header x-apisports-key):
APIFOOTBALL_BASE = "https://v3.football.api-sports.io"
# Alternativa vía RapidAPI: "https://api-football-v1.p.rapidapi.com/v3"
# (en ese caso la auth usa x-rapidapi-key + x-rapidapi-host).

def api_football_key():
    """API key de API-Football desde la variable de entorno API_FOOTBALL_KEY.
    Agregá `API_FOOTBALL_KEY=tu_key` al archivo .env (está en .gitignore)."""
    return os.environ.get("API_FOOTBALL_KEY", "").strip()

# ─── Helpers ─────────────────────────────────────────────────────────────────

def season_from_match_key(match_key):
    """'2025-04-13_vs_gimnasia_jujuy_h'  →  '2025'. Fallback a CURRENT_SEASON."""
    prefix = (match_key or "")[:4]
    return prefix if prefix.isdigit() else CURRENT_SEASON

def season_data_dir(season=None):
    return _SEASON_DATA_DIR.format(season=season or CURRENT_SEASON)

def rivals_dir(season=None):
    return _RIVALS_DIR.format(season=season or CURRENT_SEASON)

def rival_data_dir(rival_slug, season=None):
    """Datos scrapeados de un rival: data/temporadas/{season}/rivals/{slug}/"""
    return os.path.join(rivals_dir(season), rival_slug)

def rival_plots_dir(rival_slug, season=None):
    """Gráficos del análisis de temporada de un rival:
    outputs/temporadas/{season}/rivals/{slug}/graficos/"""
    s = season or CURRENT_SEASON
    return os.path.join(OUTPUTS_DIR, "temporadas", str(s), "rivals", rival_slug, "graficos")

def standings_file(season=None):
    return _STANDINGS_FILE.format(season=season or CURRENT_SEASON)

def season_plots_dir(season=None):
    return _SEASON_PLOTS_DIR.format(season=season or CURRENT_SEASON)

def season_reports_dir(season=None):
    return _SEASON_REPORTS_DIR.format(season=season or CURRENT_SEASON)

def match_outputs_dir(match_key, season=None):
    # Si no se pasa season, se deriva del prefijo del match_key (YYYY-...)
    s = season or season_from_match_key(match_key)
    return _MATCH_OUTPUTS_DIR.format(season=s, match_key=match_key)

def match_video_dir(match_key, season=None):
    """Carpeta del video del partido (Fase B: pipeline de visión por computadora).
    Convención: data/temporadas/{season}/partidos/{match_key}/video/"""
    s = season or season_from_match_key(match_key)
    return os.path.join(season_data_dir(s), match_key, "video")

def match_tracking_dir(match_key, season=None):
    """Datos derivados del video (posiciones, eventos SPADL) — Fase B/C.
    Convención: data/temporadas/{season}/partidos/{match_key}/tracking/"""
    s = season or season_from_match_key(match_key)
    return os.path.join(season_data_dir(s), match_key, "tracking")

def find_match_video(match_key, season=None):
    """Devuelve la ruta del primer video encontrado en la carpeta video/ del
    partido, o None si no hay. Acepta cualquier extensión de VIDEO_EXTENSIONS."""
    vdir = match_video_dir(match_key, season)
    if not os.path.isdir(vdir):
        return None
    for f in sorted(os.listdir(vdir)):
        if f.lower().endswith(VIDEO_EXTENSIONS):
            return os.path.join(vdir, f)
    return None

def pre_outputs_dir(rival, season=None):
    return _PRE_OUTPUTS_DIR.format(season=season or CURRENT_SEASON, rival=rival)

# ─── Análisis global del grupo (zona) ────────────────────────────────────────
def group_outputs_dir(season=None):
    """Carpeta raíz del análisis global del Grupo A de la temporada:
    outputs/temporadas/{season}/global_grupo_a/"""
    s = season or CURRENT_SEASON
    return os.path.join(OUTPUTS_DIR, "temporadas", str(s), "global_grupo_a")

def team_report_dir(team_slug, season=None):
    """Carpeta del informe estándar de un equipo del grupo (para vender a clubes):
    outputs/temporadas/{season}/global_grupo_a/equipos/{slug}/"""
    return os.path.join(group_outputs_dir(season), "equipos", team_slug)

def group_league_dir(season=None):
    """Carpeta de las estadísticas globales de la liga (rankings, mejor 11 por
    fecha, tendencias): outputs/temporadas/{season}/global_grupo_a/liga/"""
    return os.path.join(group_outputs_dir(season), "liga")

def group_season_stats_dir(season=None):
    """Estadísticas de TODA la temporada (rankings, tendencias), separadas de lo
    de cada fecha: .../global_grupo_a/liga/temporada/"""
    return os.path.join(group_league_dir(season), "temporada")

def group_round_dir(round_num, season=None):
    """Carpeta de una fecha puntual: .../global_grupo_a/liga/fechas/fecha_NN/"""
    return os.path.join(group_league_dir(season), "fechas", f"fecha_{int(round_num):02d}")

# Grupo A 2026 = Chaco For Ever + los 18 rivales de la temporada.
def group_a_teams(season="2026"):
    """Dict {slug: {'id':..., 'name':...}} de los 19 equipos del Grupo A.
    Incluye a Chaco For Ever junto a los rivales de la temporada."""
    teams = {"chaco_for_ever": {"id": CHACO_TEAM_ID, "name": "Chaco For Ever"}}
    teams.update(RIVALS_2026 if str(season) == "2026" else {})
    return teams

def rival_slug_from_match_key(match_key):
    """'2025-02-15_vs_defensores_unidos_a'  →  'defensores_unidos'"""
    parts = match_key.split("_vs_", 1)
    if len(parts) < 2:
        return None
    return parts[1].rsplit("_", 1)[0]
