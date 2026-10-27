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
_STANDINGS_ZONA_B_FILE = os.path.join(_ROOT, "data", "temporadas", "{season}", "standings_zona_b.csv")
_FIXTURE_FILE = os.path.join(_ROOT, "data", "temporadas", "{season}", "fixture.csv")

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
    "gimnasia_jujuy":            {"id": 5292,   "name": "Gimnasia Jujuy"},
    "godoy_cruz":                {"id": 6074,   "name": "Godoy Cruz"},
    "los_andes":                 {"id": 112497, "name": "Los Andes"},
    "club_mitre":                {"id": 255425, "name": "CA Mitre"},
    "racing_de_cordoba":         {"id": 273657, "name": "Racing de Córdoba"},
    "san_miguel":                {"id": 264945, "name": "San Miguel"},
    "san_telmo":                 {"id": 213361, "name": "San Telmo"},
}

# Rivales de 2025. Un mismo club usa el MISMO slug todas las temporadas
# (ej. 'club_mitre', 'gimnasia_jujuy'): si repite, aparece en los dos dicts.
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
    # Zona A 2025 que no repitió en 2026 (no fueron rivales de Chaco).
    "alvarado":                  {"id": 273715, "name": "Alvarado"},
    "arsenal_de_sarandi":        {"id": 3221,   "name": "Arsenal de Sarandí"},
}

# Lookup único por slug: el pipeline resuelve el rival por el match_key, sin
# importar la temporada. 2026 pisa a 2025 si algún slug coincidiera.
RIVALS = {**RIVALS_2025, **RIVALS_2026}

# Los 18 equipos de Zona B 2026 (misma Primera Nacional, mismo
# UNIQUE_TOURNAMENT_ID=703 — está en standings[1] del endpoint de posiciones,
# pero standings_scraper.fetch_standings solo lee standings[0]).
# 5 de estos 18 ya existían en RIVALS_2025/2026 bajo otro slug (mismo id de
# SofaScore): se reusan esas claves para no duplicar la carpeta de datos.
RIVALS_ZONA_B_2026 = {
    "gimnasia_jujuy":       RIVALS_2026["gimnasia_jujuy"],      # id 5292
    "tristan_suarez":       {"id": 93513,  "name": "Tristán Suárez"},
    "temperley":            RIVALS_2025["temperley"],            # id 112499
    "atlanta":              {"id": 53799,  "name": "Atlanta"},
    "ferrocarril_midland":  {"id": 270344, "name": "Ferrocarril Midland"},
    "deportivo_maipu":      {"id": 213042, "name": "Deportivo Maipú"},
    "gimnasia_tiro_salta":  {"id": 222126, "name": "Gimnasia y Tiro de Salta"},
    "atletico_rafaela":     {"id": 34976,  "name": "Atlético de Rafaela"},
    "san_martin_tucuman":   {"id": 23950,  "name": "San Martín de Tucumán"},
    "colegiales":           {"id": 112493, "name": "Colegiales"},
    "almagro":              {"id": 4938,   "name": "Almagro"},
    "san_martin_san_juan":  {"id": 7772,   "name": "San Martín de San Juan"},
    "chacarita":            RIVALS_2025["chacarita"],            # id 3214
    "quilmes":              {"id": 4936,   "name": "Quilmes Atlético Club"},
    "patronato":            {"id": 43741,  "name": "Patronato"},
    "agropecuario":         RIVALS_2025["agropecuario"],         # id 265787
    "guemes":               {"id": 224646, "name": "Güemes"},
    "nueva_chicago":        RIVALS_2025["nueva_chicago"],        # id 3200
}

# RIVALS queda con Zona A + Zona B: así scrape_rival_recent() sirve para
# cualquier equipo de la Primera Nacional sin importar la zona.
RIVALS.update(RIVALS_ZONA_B_2026)

# ─── Registro único de equipos (team_id → slug canónico) ────────────────────
# Un club tiene UN slug para todas las temporadas: el de la carpeta en
# rivals/ y el que va en los match_keys (de Chaco y de los rivales). Antes el
# scraper de rivales armaba el match_key con el nombre de SofaScore cortado a
# 25 letras ('club_atletico_colon', 'estudiantes_de_buenos_air', 'g�emes'), y
# el mismo club quedaba con un nombre distinto en cada lado.
EQUIPOS = {CHACO_TEAM_ID: {"slug": CHACO_SLUG.replace("-", "_"),
                           "name": "Chaco For Ever"}}
for _slug, _info in RIVALS.items():
    EQUIPOS.setdefault(_info["id"], {"slug": _slug, "name": _info["name"]})


def slugify_equipo(nombre):
    """Slug a partir de un nombre de SofaScore, para equipos que todavía no
    están en EQUIPOS (temporadas viejas). Saca todos los acentos (ü incluida)
    y no corta el largo."""
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", str(nombre or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "desconocido"


def slug_de(team_id, nombre=None):
    """Slug canónico del equipo. Si el team_id no está registrado, cae al
    nombre normalizado: conviene sumarlo a RIVALS_* para fijarlo."""
    try:
        info = EQUIPOS.get(int(team_id))
    except (TypeError, ValueError):
        info = None
    return info["slug"] if info else slugify_equipo(nombre)

# ─── Liga Profesional Argentina (primera división — torneo APARTE de la
# Primera Nacional donde juega Chaco, no comparte tournament_id ni equipos
# necesariamente) ──────────────────────────────────────────────────────────
# Formato 2026: Apertura + Clausura, cada uno con Zona A/B de 15 equipos,
# más tablas "Anual 2026" (30, todos contra todos acumulado) y "Promedios
# 2026" (30, la que define descenso). Los 6 grupos viven bajo un único
# season_id — no hace falta un season_id distinto por etapa.
UNIQUE_TOURNAMENT_ID_LPF = 155
SEASON_IDS_LPF = {
    "2026": 87913,   # "Primera LPF 2026"
}

# Los 30 equipos de la Liga Profesional 2026 (tabla "Anual 2026").
# Registro separado de RIVALS: aunque algún id coincida con un ex-rival de
# Primera Nacional (ascensos/descensos entre temporadas), los datos de LPF
# viven en su propio árbol (lpf_team_dir), sin pisar nada de Chaco.
LPF_TEAMS_2026 = {
    "independiente_rivadavia": {"id": 36842,  "name": "Independiente Rivadavia"},
    "estudiantes_la_plata":    {"id": 3206,   "name": "Estudiantes de La Plata"},
    "boca_juniors":            {"id": 3202,   "name": "Boca Juniors"},
    "river_plate":             {"id": 3211,   "name": "River Plate"},
    "argentinos_juniors":      {"id": 3216,   "name": "Argentinos Juniors"},
    "velez":                   {"id": 3208,   "name": "Vélez Sarsfield"},
    "rosario_central":         {"id": 3217,   "name": "Rosario Central"},
    "talleres":                {"id": 3210,   "name": "CA Talleres"},
    "belgrano":                {"id": 3203,   "name": "Club Atlético Belgrano"},
    "gimnasia_la_plata":       {"id": 3205,   "name": "Gimnasia y Esgrima"},
    "independiente":           {"id": 3209,   "name": "CA Independiente"},
    "lanus":                   {"id": 3218,   "name": "CA Lanús"},
    "huracan":                 {"id": 7629,   "name": "Huracán"},
    "san_lorenzo":             {"id": 3201,   "name": "San Lorenzo"},
    "union_santa_fe":          {"id": 3204,   "name": "Club Atlético Unión de Santa Fe"},
    "racing_club":             {"id": 3215,   "name": "Racing Club"},
    "instituto":               {"id": 4937,   "name": "Instituto De Córdoba"},
    "barracas_central":        {"id": 65668,  "name": "Barracas Central"},
    "tigre":                   {"id": 7628,   "name": "Tigre"},
    "defensa_y_justicia":      {"id": 36839,  "name": "Defensa y Justicia"},
    "sarmiento":               {"id": 42338,  "name": "Sarmiento"},
    "gimnasia_mendoza":        {"id": 188441, "name": "Gimnasia y Esgrima Mendoza"},
    "banfield":                {"id": 3219,   "name": "Banfield"},
    "platense":                {"id": 36837,  "name": "Club Atlético Platense"},
    "central_cordoba":         {"id": 65676,  "name": "Central Córdoba"},
    "newells":                 {"id": 3212,   "name": "Newell's Old Boys"},
    "atletico_tucuman":        {"id": 36833,  "name": "Atlético Tucumán"},
    "deportivo_riestra":       {"id": 189723, "name": "Deportivo Riestra"},
    "aldosivi":                {"id": 36836,  "name": "Aldosivi"},
    "estudiantes_rio_cuarto":  {"id": 266694, "name": "Estudiantes de Río Cuarto"},
}

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
    "R. Zules",
    "L. Marinucci",
    "I. Enriquez",
    "M. Noble"
]


def jugadores_fuera():
    """Set en minúsculas de los jugadores dados de baja (para comparar)."""
    return {n.strip().lower() for n in JUGADORES_FUERA if n and n.strip()}


# ─── Corrección de identidad: SofaScore mezcla el bio de "G. Pacheco" ───────
# El delantero de Chaco For Ever (player_id 83700 en SofaScore, el que juega
# todos los partidos y va a las estadísticas de todos nuestros informes) es en
# realidad Ezequiel Pacheco (23 años, nacido el 16/12/2002, 1.90m). SofaScore
# le carga por error el bio de OTRO jugador homónimo que no juega en Chaco:
# Germán Ezequiel Pacheco González (35 años, nacido el 19/05/1991, 1.76m,
# sofascore id 2468554 es el perfil correcto de Ezequiel).
#
# Esto NO afecta los datos DENTRO del partido (goles, pases, minutos, tarjetas:
# esos SÍ son del jugador real, solo el bio está mal cargado). El único lugar
# donde el error se nota es en scouting (edad, nombre completo), así que la
# corrección se aplica ahí nomás — ver src/analysis/scouting.py:_stats_del_raw.
CORRECCIONES_BIO_JUGADORES = {
    83700: {
        "nombre_completo": "Ezequiel Pacheco",
        "nacimiento": 1039996800,  # 16/12/2002 UTC
        "altura": 190,
    },
}

# ─── Jugadores con dos player_id en SofaScore ───────────────────────────────
# SofaScore a veces le crea un perfil nuevo a un jugador que ya tenía uno (o
# fusiona dos perfiles), y el mismo partido scrapeado dos veces trae ids
# distintos. La base de jugadores (src/jugadores) reemplaza cada id duplicado
# por el real al leer los partidos. Candidatos para revisar a mano:
#     from src.jugadores import construir as C; C.posibles_duplicados()
# Formato: {id_duplicado: id_real}. Solo cargar los confirmados (misma
# persona: mismo nombre completo y fecha de nacimiento compatible).
# Criterio para confirmar (2026-10-27): mismo equipo, nunca juntos en cancha,
# un id reemplaza al otro en el tiempo, y mismo nacimiento o mismo dorsal y
# puesto. Se unifica en el id que SofaScore usa ahora (o el de más historia).
ALIAS_JUGADORES = {
    83700:   2468554,   # E. Pacheco (Chaco): 83700 tenía la bio de un homónimo
    2159514: 2484722,   # J. Bustos (Almagro 2026): mismo nacimiento y dorsal
    1087036: 1183703,   # M. González (Los Andes): 1183703 es su id de 2025
    1598435: 1627979,   # L. Pascual (Almirante 2026): dorsal 10, cambio el 26/9
    2159501: 1388632,   # J. Camaño (Midland 2026): dorsal 8, cambio el 7/8
    2048159: 1184980,   # M. D. Echeverría (Temperley 2026): dorsal 9, cambio el 6/9
    941488:  2087705,   # L. Rodríguez (Central Norte 2025): arquero, dorsal 1
    # Evidencia de shotmap: en un mismo partido el shotmap y el lineup le dan
    # ids distintos al mismo jugador (mismo equipo, nombre y nacimiento). Se
    # unifica en el id con más partidos.
    2047512: 1217999,   # T. Silva (Maipú)
    1819575: 1901985,   # R. Juárez (Defensores Unidos 2025)
    2059699: 1546505,   # S. Villalba (Almirante / Chaco)
    1525748: 1605509,   # N. Medina (Atlanta 2025)
    2118524: 1394198,   # J. Barolín (Patronato)
    2060467: 941539,    # G. Pugliese (Defensores de Belgrano / Güemes)
    1654537: 1199249,   # T. Rambert (Los Andes / Ciudad de Bolívar)
    2054529: 1875390,   # R. Sosa (San Telmo / Atlanta)
    1887616: 1485593,   # R. Rodríguez (Estudiantes de Caseros)
    1904638: 2437593,   # T. Jerez (San Miguel)
}


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

MIN_DELAY          = 4    # segundos entre partidos/equipos (bajado de 6-12s el 2026-08-05
MAX_DELAY          = 8    # para acelerar la corrida overnight de Zona B + LPF)
MIN_DELAY_EP       = 1.5  # segundos entre endpoints del MISMO partido (event, statistics,
MAX_DELAY_EP       = 3.0  # lineups, ...) y entre requests de heatmap. Más corto que el
                          # delay entre partidos: son requests a la misma /event/{id}.
RIVAL_LAST_MATCHES = 3    # mínimo de partidos para considerar "ya scrapeado" un rival
                          # (el scraping en sí baja TODOS los partidos de la temporada,
                          # no solo estos — ver rivals_scraper.scrape_rival_recent)

# ─── Modelo de la tabla (Dixon-Coles + Monte Carlo) ──────────────────────────
# Hiperparámetros elegidos por backtesting con origen móvil (cortes en las
# fechas 14, 16, 18, 20 y 22 de 2026), no a ojo. Ver src/analysis/backtest.py
# y EXPLICACION_montecarlo.md.

DC_XI        = 0.0   # decaimiento temporal por día del ajuste: exp(-XI*días).
                     # 0 = todos los partidos de la temporada pesan igual.
                     # El backtest no encuentra ninguna ganancia en ponderar
                     # por recencia (la curva es plana entre 0 y 0.003/día, y
                     # empeora de ahí en adelante). El modelo anterior usaba
                     # medio-vida de 6 PARTIDOS (~0.0165/día): reaccionaba a
                     # las rachas mucho más de lo que la predicción justifica.
DC_W_XG      = 0.8   # peso del xG en el rating; los goles observados pesan
                     # 0.2. Antes estaba en 0.4 por un t≈1 sobre log-loss,
                     # pero ese test estaba SIN parear. Pareando por corte
                     # (mismo corte, misma semilla, misma ventana), 0.8 le
                     # gana a 0.4 en 6/6 cortes en log-loss (t=2.72, p=0.042)
                     # y RPS, y en 30/30 corridas en MAE de puntos de la
                     # proyección (t=11.7). Ver backtest.position_backtest().
                     # Ojo: w_xg NO borra los goles — los partidos sin xG
                     # (18 de 453) mantienen peso completo de goles, y ρ/τ se
                     # estima SIEMPRE con goles reales. La escala de goles
                     # también se calibra contra goles reales (`level`).
DC_MAX_GOALS = 12    # techo de la grilla de resultados exactos por partido

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

def standings_zona_b_file(season=None):
    return _STANDINGS_ZONA_B_FILE.format(season=season or CURRENT_SEASON)

def fixture_file(season=None):
    return _FIXTURE_FILE.format(season=season or CURRENT_SEASON)

# ─── Liga Profesional Argentina — rutas (árbol separado de temporadas/) ──────
_LPF_TEAM_DIR      = os.path.join(_ROOT, "data", "liga_profesional", "{season}", "equipos", "{slug}")
_LPF_STANDINGS_DIR = os.path.join(_ROOT, "data", "liga_profesional", "{season}", "standings")
_LPF_FIXTURE_FILE  = os.path.join(_ROOT, "data", "liga_profesional", "{season}", "fixture.csv")
_LPF_OUTPUTS_DIR   = os.path.join(_ROOT, "outputs", "liga_profesional", "{season}")

def lpf_team_dir(slug, season=None):
    """Datos scrapeados de un equipo de LPF: data/liga_profesional/{season}/equipos/{slug}/"""
    return _LPF_TEAM_DIR.format(season=season or CURRENT_SEASON, slug=slug)

def lpf_standings_dir(season=None):
    return _LPF_STANDINGS_DIR.format(season=season or CURRENT_SEASON)

def lpf_fixture_file(season=None):
    return _LPF_FIXTURE_FILE.format(season=season or CURRENT_SEASON)

def lpf_outputs_dir(season=None):
    return _LPF_OUTPUTS_DIR.format(season=season or CURRENT_SEASON)

def lpf_team_plots_dir(slug, season=None):
    """Gráficos del análisis de temporada de un equipo de LPF (mismo criterio
    que rival_plots_dir, pero bajo el árbol propio de LPF):
    outputs/liga_profesional/{season}/equipos/{slug}/graficos/"""
    return os.path.join(lpf_outputs_dir(season), "equipos", slug, "graficos")

def season_plots_dir(season=None):
    return _SEASON_PLOTS_DIR.format(season=season or CURRENT_SEASON)

def season_reports_dir(season=None):
    return _SEASON_REPORTS_DIR.format(season=season or CURRENT_SEASON)

def match_outputs_dir(match_key, season=None):
    # Si no se pasa season, se deriva del prefijo del match_key (YYYY-...)
    s = season or season_from_match_key(match_key)
    return _MATCH_OUTPUTS_DIR.format(season=s, match_key=match_key)

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

def scouting_dir(season=None):
    """Salidas del recomendador de jugadores (k-NN) y de la auditoría del
    plantel: outputs/temporadas/{season}/scouting/"""
    s = season or CURRENT_SEASON
    return os.path.join(OUTPUTS_DIR, "temporadas", str(s), "scouting")

def group_projection_dir(season=None):
    """Gráficos de la proyección Monte Carlo de la tabla (Fase 1, Zona A):
    .../global_grupo_a/liga/proyeccion/"""
    return os.path.join(group_league_dir(season), "proyeccion")

# Grupo A 2026 = Chaco For Ever + los 18 rivales de la temporada.
def group_a_teams(season="2026"):
    """Dict {slug: {'id':..., 'name':...}} de los 19 equipos del Grupo A.
    Incluye a Chaco For Ever junto a los rivales de la temporada."""
    teams = {"chaco_for_ever": {"id": CHACO_TEAM_ID, "name": "Chaco For Ever"}}
    teams.update(RIVALS_2026 if str(season) == "2026" else {})
    return teams

def group_b_teams(season="2026"):
    """Dict {slug: {'id':..., 'name':...}} de los 18 equipos de la Zona B."""
    return dict(RIVALS_ZONA_B_2026 if str(season) == "2026" else {})

def rival_slug_from_match_key(match_key):
    """'2025-02-15_vs_defensores_unidos_a'  →  'defensores_unidos'"""
    parts = match_key.split("_vs_", 1)
    if len(parts) < 2:
        return None
    return parts[1].rsplit("_", 1)[0]
