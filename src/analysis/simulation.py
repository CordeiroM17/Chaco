"""
simulation.py
==============
Simulación Monte Carlo de la tabla de la Zona A (Primera Nacional 2026):
toma la tabla de hoy, simula miles de veces el fixture restante y cuenta en
qué posición terminó cada equipo.

El modelo de partido vive en `src/analysis/dixon_coles.py` (Dixon-Coles 1997
ajustado por máxima verosimilitud, con corrección τ, localía y escala de
goles estimadas en el mismo ajuste). Acá se lo usa con los ratings
ESTÁTICOS: se ajustan una vez con todo lo jugado y no se actualizan dentro de
la simulación. Los hiperparámetros salen del backtesting
(`src/analysis/backtest.py`, valores en `config.py`).

`model="legacy"` mantiene el modelo anterior (promedios de goles y xG
normalizados contra el promedio de la liga, Poisson independiente, recencia
por vida media en partidos) para poder comparar; el backtest muestra que
predice peor.

Alcance (Fase 1, ver `PLAN_montecarlo_tabla.md`): probabilidad de posición
final, de descenso (últimos 2 de Zona A) y de entrar al Reducido por posición
de zona (2°-8°). NO calcula ascenso directo ni ganador del Reducido completo,
que dependen de simular el reglamento con la Zona B (Fase 2) — los ratings de
los 36 equipos del torneo ya están.

Uso:
    from src.analysis import simulation as SIM
    strengths = SIM.fit_dc_strengths(season="2026")
    sims = SIM.simulate_season(season="2026", n_sims=100000, seed=42)
    pos_probs = SIM.position_probabilities(sims)
    proj = SIM.promotion_relegation_probabilities(sims)
    bounds = SIM.points_bounds(season="2026")
"""
import numpy as np
import pandas as pd

import os

import config
from src.analysis import liga as L
from src.analysis import season as S
from src.analysis import pre_match as PM
from src.scraping.standings_scraper import load_standings
from src.scraping.fixture_scraper import remaining_fixture_zona_a, zona_a_team_ids
from src.analysis import dixon_coles as DC

DESCENSO_DESDE = 17     # 17° y 18° de Zona A descienden
REDUCIDO_DESDE = 2      # 2° a 8° de Zona A entran al Reducido por posición
REDUCIDO_HASTA = 8


# ─────────────────────────── ajuste del modelo ──────────────────────────────
def _weighted_match_stats(sdf, half_life):
    """Promedios ponderados de gf/gc/xgf/xgc de un equipo a partir de su
    tabla de partidos (`build_season_table`), con decaimiento exponencial:
    el partido más reciente pesa 1, cada `half_life` partidos hacia atrás el
    peso se reduce a la mitad. Cada métrica promedia solo sobre los partidos
    donde hay dato (por ej. si falta el shotmap de un partido, ese partido no
    diluye xgf_pp/xgc_pp — a diferencia de `season_stats().sum()/pj`, que sí
    lo hace porque `.sum()` ignora NaN pero divide por el total de partidos)."""
    empty = dict(pj=0, gf_pp=None, gc_pp=None, xgf_pp=None, xgc_pp=None)
    if sdf is None or sdf.empty or "chaco_goals" not in sdf.columns:
        return empty
    d = sdf.sort_values("date").reset_index(drop=True)
    n = len(d)
    if n == 0:
        return empty
    age = (n - 1) - np.arange(n)              # partido más nuevo -> age 0
    w = 0.5 ** (age / half_life)

    def wavg(col):
        if col not in d.columns:
            return None
        vals = pd.to_numeric(d[col], errors="coerce")
        mask = vals.notna()
        if not mask.any():
            return None
        return float((vals[mask] * w[mask]).sum() / w[mask].sum())

    return dict(pj=n, gf_pp=wavg("chaco_goals"), gc_pp=wavg("rival_goals"),
                xgf_pp=wavg("chaco_xg"), xgc_pp=wavg("rival_xg"))


def _team_match_keys_for_ratings(slug, season):
    """Como `liga.team_context()` pero SIN exigir `shotmap_clean.csv`
    (`liga.CORE_CSVS`) — alcanza con poder calcular el resultado real
    (`incidents_clean.csv`, o `shotmap_clean.csv` si falta incidents).

    Importa porque a veces SofaScore no publica la capa de análisis de un
    partido (sin shotmap/xG/momentum, pero CON resultado — ver memoria
    'partidos sin análisis de SofaScore'). `team_context()` descarta esos
    partidos enteros, lo cual en el modelo PLANO apenas mueve el promedio,
    pero en el modelo PONDERADO por recencia es grave si el partido faltante
    es justo el más reciente: el fit nunca se entera de él, aunque sea el
    que más debería pesar."""
    if slug in ("chaco_for_ever", "chaco-for-ever", "chaco"):
        base_dir = config.season_data_dir(season)
        all_mks = list(S.load_matches(season))
    else:
        base_dir = config.rival_data_dir(slug, season)
        all_mks = PM.rival_match_keys(slug, season) if os.path.isdir(base_dir) else []

    def _has_score(mk):
        d = os.path.join(base_dir, mk)
        return (os.path.exists(os.path.join(d, "incidents_clean.csv"))
                or os.path.exists(os.path.join(d, "shotmap_clean.csv")))

    mks = [mk for mk in all_mks if _has_score(mk)]
    return base_dir, mks, L.team_name(slug, season)


def _team_summary_table_weighted(season, half_life):
    """Igual que `liga.team_summary_table()` pero con `gf_pp/gc_pp/xgf_pp/
    xgc_pp` ponderados por recencia en vez de promedio plano de temporada."""
    rows = []
    for slug in config.group_a_teams(season):
        base_dir, mks, name = _team_match_keys_for_ratings(slug, season)
        if not mks:
            continue
        sdf = S.build_season_table(mks, base_dir)
        st = _weighted_match_stats(sdf, half_life)
        rows.append({"slug": slug, "equipo": name, **st})
    return pd.DataFrame(rows)


def fit_team_strengths(season=None, w_xg=0.5, half_life=None):
    """
    Ataque/defensa por equipo de Zona A, normalizado contra el promedio de la
    zona. Mezcla goles reales y xG (w_xg = peso del xG, 0.5 = mitad y mitad)
    para amortiguar la varianza de la finalización sobre ~22-23 partidos.

    `half_life` (en cantidad de partidos): si se pasa, cada partido se pesa
    con decaimiento exponencial en vez de promediarse plano sobre toda la
    temporada — el partido más reciente pesa 1, uno jugado `half_life`
    partidos atrás pesa 0.5, dos `half_life` atrás 0.25, etc. Así una racha
    de caída o subida mueve el rating del equipo antes de que se note en la
    tabla real. `half_life=None` (default) mantiene el promedio plano
    original — útil para comparar contra el modelo ponderado.

    Devuelve DataFrame indexado por team_id: attack, defense, gf_pp, gc_pp,
    xgf_pp, xgc_pp, pj (para poder etiquetar confianza por muestra).
    """
    season = season or config.CURRENT_SEASON
    if half_life:
        resumen = _team_summary_table_weighted(season, half_life)
    else:
        resumen = L.team_summary_table(season)
    if resumen is None or resumen.empty:
        raise RuntimeError(
            f"team_summary_table('{season}') vino vacío — no hay datos de "
            f"Zona A para ajustar el modelo.")

    ids_por_slug = {slug: info["id"] for slug, info in config.group_a_teams(season).items()}
    resumen = resumen.copy()
    resumen["team_id"] = resumen["slug"].map(ids_por_slug)
    faltantes = resumen[resumen["team_id"].isna()]
    if not faltantes.empty:
        raise RuntimeError(
            f"No se pudo mapear team_id para: {faltantes['slug'].tolist()} — "
            f"revisar config.group_a_teams().")
    resumen["team_id"] = resumen["team_id"].astype(int)

    # Si a un equipo le falta el xG de TODOS sus partidos ponderados (caso
    # límite, no debería pasar con datos reales), cae 100% a goles reales en
    # vez de reventar con NaN.
    resumen["xgf_pp"] = resumen["xgf_pp"].fillna(resumen["gf_pp"])
    resumen["xgc_pp"] = resumen["xgc_pp"].fillna(resumen["gc_pp"])

    resumen["blend_gf"] = w_xg * resumen["xgf_pp"] + (1 - w_xg) * resumen["gf_pp"]
    resumen["blend_gc"] = w_xg * resumen["xgc_pp"] + (1 - w_xg) * resumen["gc_pp"]

    # team_summary_table() recorre TODOS los slugs de group_a_teams(), que
    # incluye a Gimnasia de Jujuy (rival interzonal, en realidad de Zona B —
    # ver PLAN_montecarlo_tabla.md sección 1). Se mantiene su fila (da un
    # ataque/defensa real para ese partido puntual si queda pendiente), pero
    # el promedio de liga que normaliza a todos se calcula SOLO con los 18
    # equipos reales de Zona A, para no correr la base con un equipo de otra
    # categoría.
    zona_a = zona_a_team_ids(season)
    base_zona_a = resumen[resumen["team_id"].isin(zona_a)]
    avg_goals = base_zona_a["blend_gf"].mean()
    if not avg_goals or avg_goals <= 0:
        raise RuntimeError("Promedio de goles de la zona salió 0 — revisar team_summary_table().")

    resumen["attack"]  = resumen["blend_gf"] / avg_goals
    resumen["defense"] = resumen["blend_gc"] / avg_goals

    out = resumen.set_index("team_id")[
        ["equipo", "pj", "gf_pp", "gc_pp", "xgf_pp", "xgc_pp", "attack", "defense"]
    ].rename(columns={"equipo": "team_name"})
    out.attrs["avg_goals"] = float(avg_goals)
    out.attrs["home_advantage"] = _fit_home_advantage(season)
    return out


def fit_dc_strengths(season=None, xi=None, w_xg=None, matches=None, verbose=False):
    """Ataque (α) y defensa (β) por equipo con el modelo Dixon-Coles, ajustado
    por máxima verosimilitud sobre TODOS los partidos jugados del torneo (las
    dos zonas, 36 equipos).

    Diferencias con `fit_team_strengths()` (el modelo viejo):
      - los parámetros se estiman juntos, así que cada partido se corrige por
        la calidad del rival: golear al último no vale lo mismo que golear al
        puntero;
      - la localía (γ) y la escala de goles salen del mismo ajuste, en vez de
        ser un cociente aparte aplicado de un solo lado;
      - ρ captura la dependencia entre los goles del local y del visitante en
        los resultados bajos, que es lo que el Poisson independiente no puede
        representar;
      - los rivales interzonales de Zona B tienen rating propio en vez de
        entrar como equipo promedio.

    Devuelve el DataFrame de los equipos de Zona A (índice team_id, columnas
    team_name/pj/attack/defense) con el ajuste completo en
    `.attrs["dc_fit"]` — ahí están γ, ρ, `level` y los 36 equipos."""
    season = season or config.CURRENT_SEASON
    matches = DC.build_match_table(season) if matches is None else matches
    fit = DC.fit(matches, xi=xi, w_xg=w_xg, verbose=verbose)

    names = {}
    for _, r in matches.iterrows():
        names[int(r["home_team_id"])] = r["home_team"]
        names[int(r["away_team_id"])] = r["away_team"]
    pj = {}
    for col in ("home_team_id", "away_team_id"):
        for t, c in matches[col].value_counts().items():
            pj[int(t)] = pj.get(int(t), 0) + int(c)

    zona_a = zona_a_team_ids(season)
    st = load_standings(season)
    st_names = dict(zip(st["team_id"].astype(int), st["team_name"])) if st is not None else {}

    rows = []
    for t in fit["teams"]:
        if zona_a and t not in zona_a:
            continue
        rows.append({"team_id": t,
                     "team_name": st_names.get(t, names.get(t, t)),
                     "pj": pj.get(t, 0),
                     "attack": fit["alpha"][t],
                     "defense": fit["beta"][t]})
    out = pd.DataFrame(rows).set_index("team_id")
    out.attrs["dc_fit"] = fit
    out.attrs["avg_goals"] = fit["level"]
    out.attrs["home_advantage"] = fit["gamma"]
    return out


def _fit_home_advantage(season):
    """Factor multiplicativo de localía: goles promedio del local / goles
    promedio del visitante, sobre los partidos de Zona A ya jugados. Con
    ~22-23 fechas de muestra se usa un factor GLOBAL (no por equipo)."""
    from src.scraping.fixture_scraper import load_fixture
    fx = load_fixture(season)
    if fx is None or fx.empty:
        return 1.15  # fallback razonable (~15% de ventaja, valor típico de fútbol)
    zona_a = zona_a_team_ids(season)
    jugados = fx[
        (fx["status_type"] == "finished")
        & (fx["home_team_id"].isin(zona_a) | fx["away_team_id"].isin(zona_a))
    ]
    if jugados.empty:
        return 1.15
    avg_home = jugados["home_score"].mean()
    avg_away = jugados["away_score"].mean()
    if not avg_away or avg_away <= 0:
        return 1.15
    return float(avg_home / avg_away)


# ─────────────────────────── simulación ──────────────────────────────────────
def _lambda_for_match(home_id, away_id, strengths, home_advantage, avg_goals, default_rating):
    """(λ_local, λ_visitante) para un partido. Si algún equipo no está en
    `strengths` (rival interzonal de Zona B, sin datos en Fase 1), se usa
    `default_rating` (1.0 = promedio de liga) — queda aproximado y hay que
    etiquetarlo en el informe."""
    a_home = strengths["attack"].get(home_id, default_rating)
    d_home = strengths["defense"].get(home_id, default_rating)
    a_away = strengths["attack"].get(away_id, default_rating)
    d_away = strengths["defense"].get(away_id, default_rating)
    lam_home = a_home * d_away * avg_goals * home_advantage
    lam_away = a_away * d_home * avg_goals
    return max(lam_home, 0.05), max(lam_away, 0.05)


def simulate_season(season=None, n_sims=20000, w_xg=None, seed=None,
                    model="dc", xi=None, half_life=None):
    """
    Simula el resto de la Zona A `n_sims` veces (vectorizado con NumPy) desde
    la tabla actual (`standings.csv`) + el fixture restante
    (`remaining_fixture_zona_a`). Devuelve un dict con:
      - 'final_points'/'final_gd'/'final_gf': arrays (n_sims, n_teams)
      - 'position': array (n_sims, n_teams) con la posición final (1=mejor)
      - 'team_ids': lista de team_id en el mismo orden que las columnas
      - 'team_names': dict team_id -> nombre
      - 'strengths': el DataFrame de fit_team_strengths (para auditar el ajuste)
      - 'n_remaining': partidos restantes simulados

    `model`:
      - `"dc"` (default): Dixon-Coles ajustado por máxima verosimilitud sobre
        los partidos del torneo completo (`src/analysis/dixon_coles.py`), con
        corrección τ para los resultados bajos, localía y escala de goles
        estimadas dentro del mismo ajuste, y ratings ESTÁTICOS (se ajustan una
        vez y no se actualizan dentro de la simulación). Los resultados se
        muestrean de la conjunta, no de dos Poisson independientes.
      - `"legacy"`: el modelo anterior (promedios de goles y xG normalizados
        contra el promedio de la liga, Poisson independiente). Se mantiene
        para poder comparar; ver `half_life` y `w_xg`.

    `xi` / `w_xg` (solo en `"dc"`): decaimiento temporal por día y peso del xG
    en el rating. Los defaults salen del backtesting (`config.DC_XI`,
    `config.DC_W_XG`, ver `src/analysis/backtest.py`).
    `half_life` (solo en `"legacy"`): vida media en partidos del promedio
    ponderado por recencia.
    """
    season = season or config.CURRENT_SEASON
    rng = np.random.default_rng(seed)

    standings = load_standings(season)
    if standings is None or standings.empty:
        raise RuntimeError(f"No hay standings.csv para la temporada {season}.")

    if model == "dc":
        strengths = fit_dc_strengths(season, xi=xi, w_xg=w_xg)
        dc_fit = strengths.attrs["dc_fit"]
    elif model == "legacy":
        strengths = fit_team_strengths(season, w_xg=0.5 if w_xg is None else w_xg,
                                       half_life=half_life)
        avg_goals = strengths.attrs["avg_goals"]
        home_advantage = strengths.attrs["home_advantage"]
        dc_fit = None
    else:
        raise ValueError(f"model='{model}' desconocido (usar 'dc' o 'legacy').")

    team_ids = standings["team_id"].astype(int).tolist()
    n_teams = len(team_ids)
    idx_of = {tid: i for i, tid in enumerate(team_ids)}
    team_names = dict(zip(standings["team_id"].astype(int), standings["team_name"]))

    remaining = remaining_fixture_zona_a(season)
    if remaining is None:
        remaining = pd.DataFrame(columns=["home_team_id", "away_team_id"])
    # Un partido interzonal puede tener un equipo que no está en `team_ids`
    # (rival de Zona B) — no se le arma tabla propia, solo se usa para el
    # resultado del equipo de Zona A involucrado.
    matches = remaining[["home_team_id", "away_team_id"]].dropna().astype(int).values.tolist()
    n_matches = len(matches)

    lam_home = np.empty(n_matches)
    lam_away = np.empty(n_matches)
    for i, (h, a) in enumerate(matches):
        if dc_fit is not None:
            lam_home[i], lam_away[i] = DC.match_lambdas(dc_fit, h, a)
        else:
            lam_home[i], lam_away[i] = _lambda_for_match(
                h, a, strengths, home_advantage, avg_goals, default_rating=1.0)

    if not n_matches:
        home_goals = np.zeros((n_sims, 0), dtype=int)
        away_goals = np.zeros((n_sims, 0), dtype=int)
    elif dc_fit is not None:
        # Muestreo de la conjunta de Dixon-Coles: mantiene la corrección τ
        # (más 0-0 y 1-1 de los que da el Poisson independiente) dentro de la
        # simulación, no solo en el ajuste.
        home_goals, away_goals = DC.sample_scores(
            lam_home, lam_away, dc_fit["rho"], n_sims, rng)
    else:
        home_goals = rng.poisson(lam_home, size=(n_sims, n_matches))
        away_goals = rng.poisson(lam_away, size=(n_sims, n_matches))

    home_pts = np.where(home_goals > away_goals, 3, np.where(home_goals == away_goals, 1, 0))
    away_pts = np.where(away_goals > home_goals, 3, np.where(away_goals == home_goals, 1, 0))

    pts_delta = np.zeros((n_sims, n_teams))
    gf_delta  = np.zeros((n_sims, n_teams))
    gc_delta  = np.zeros((n_sims, n_teams))

    for i, (h, a) in enumerate(matches):
        if h in idx_of:
            j = idx_of[h]
            pts_delta[:, j] += home_pts[:, i]
            gf_delta[:, j]  += home_goals[:, i]
            gc_delta[:, j]  += away_goals[:, i]
        if a in idx_of:
            j = idx_of[a]
            pts_delta[:, j] += away_pts[:, i]
            gf_delta[:, j]  += away_goals[:, i]
            gc_delta[:, j]  += home_goals[:, i]

    base_pts = standings.set_index("team_id").loc[team_ids, "points"].to_numpy(dtype=float)
    base_gf  = standings.set_index("team_id").loc[team_ids, "goals_for"].to_numpy(dtype=float)
    base_gc  = standings.set_index("team_id").loc[team_ids, "goals_against"].to_numpy(dtype=float)

    final_points = base_pts[None, :] + pts_delta
    final_gf     = base_gf[None, :]  + gf_delta
    final_gc     = base_gc[None, :]  + gc_delta
    final_gd     = final_gf - final_gc

    # Desempate confirmado (tabla_historica_grupo_a.py): pts -> dif. gol -> gf.
    # Se codifica como un único score ordenable (evita un lexsort por fila).
    score = final_points * 1_000_000 + final_gd * 1_000 + final_gf
    order = np.argsort(-score, axis=1)          # equipo más fuerte primero
    position = np.empty_like(order)
    rows = np.arange(n_sims)[:, None]
    position[rows, order] = np.arange(1, n_teams + 1)[None, :]

    return {
        "final_points": final_points, "final_gd": final_gd, "final_gf": final_gf,
        "position": position, "team_ids": team_ids, "team_names": team_names,
        "strengths": strengths, "n_remaining": n_matches, "n_sims": n_sims,
        "model": model, "half_life": half_life,
        "xi": (dc_fit["xi"] if dc_fit else None),
        "w_xg": (dc_fit["w_xg"] if dc_fit else w_xg),
        "rho": (dc_fit["rho"] if dc_fit else None),
        "gamma": (dc_fit["gamma"] if dc_fit else None),
        "level": (dc_fit["level"] if dc_fit else None),
    }


# ─────────────────────────── agregación ──────────────────────────────────────
def position_probabilities(sims):
    """DataFrame equipo x posición con la probabilidad (0-1) de cada casillero."""
    n_sims, n_teams = sims["position"].shape
    rows = []
    for j, tid in enumerate(sims["team_ids"]):
        counts = np.bincount(sims["position"][:, j], minlength=n_teams + 1)[1:]
        rows.append({"team_id": tid, "team_name": sims["team_names"][tid],
                      **{f"pos_{p}": counts[p - 1] / n_sims for p in range(1, n_teams + 1)}})
    return pd.DataFrame(rows)


def promotion_relegation_probabilities(sims):
    """Probabilidad de descenso / Reducido-por-posición / mitad de tabla, por
    equipo. OJO: 'reducido' acá es SOLO por posición de zona (2°-8°); falta
    sumar la chance de colarse como perdedor de la final Zona A-Zona B, que
    no se puede calcular sin datos de Zona B (Fase 2)."""
    pos = sims["position"]
    n_sims = sims["n_sims"]
    rows = []
    for j, tid in enumerate(sims["team_ids"]):
        p = pos[:, j]
        rows.append({
            "team_id": tid,
            "team_name": sims["team_names"][tid],
            "prob_puntero_zona_a": float((p == 1).mean()),
            "prob_reducido_por_posicion": float(((p >= REDUCIDO_DESDE) & (p <= REDUCIDO_HASTA)).mean()),
            # postemporada = entrar entre los REDUCIDO_HASTA primeros, sea como
            # puntero (final por el ascenso directo) o vía Reducido
            "prob_playoff": float((p <= REDUCIDO_HASTA).mean()),
            "prob_descenso": float((p >= DESCENSO_DESDE).mean()),
            "posicion_media": float(p.mean()),
            "posicion_mediana": float(np.median(p)),
        })
    return pd.DataFrame(rows).sort_values("posicion_media").reset_index(drop=True)


# ─────────────────────────── cotas matemáticas ────────────────────────────
def points_bounds(season=None, n_descienden=2, n_playoff=REDUCIDO_HASTA,
                  empate_puede_superar=True):
    """Cotas matemáticas de descenso Y de clasificación a la postemporada,
    INDEPENDIENTES de la simulación: piso (si un equipo no suma un punto más)
    y techo (si gana TODOS sus partidos restantes de Zona A). No usa Poisson
    ni fuerza de equipos — solo cuenta partidos que quedan, así que es una
    garantía dura, no una probabilidad.

    Devuelve dos veredictos por equipo:

    `estado_descenso`
      - 'Matemáticamente salvado': ni en el peor caso propio y el mejor de
        todos los demás alcanzan (n_teams - n_descienden) rivales por encima.
      - 'Matemáticamente descendido': ya hay (n_teams - n_descienden) rivales
        con el piso por encima de su techo, así que no puede escapar de los
        últimos `n_descienden` puestos.
      - 'Con chance de descenso' en el resto de los casos.

    `estado_playoff` (postemporada = los `n_playoff` primeros de la zona: el
    1° va a la final por el ascenso directo y del 2° al `n_playoff` al
    Reducido)
      - 'Clasificado': como mucho `n_playoff - 1` rivales pueden terminar por
        encima, así que el puesto de postemporada ya no se le escapa.
      - 'Eliminado del playoff': ya hay `n_playoff` rivales cuyo piso supera
        su techo.
      - 'En pelea' en el resto de los casos.

    `empate_puede_superar` decide cómo se trata el empate en puntos. Con
    True (default) un rival que puede IGUALAR el piso cuenta como que puede
    superarlo, porque el desempate es por diferencia de gol y podría caer
    para cualquier lado; es el criterio conservador y el único que permite
    afirmar 'clasificado' o 'salvado' sin letra chica. Con False se exige
    superarlo estrictamente en puntos.

    OJO: esto es DISTINTO de que la simulación le dé ~0% o ~100%. El 0% de la
    simulación es una certeza ESTADÍSTICA (el escenario es tan improbable que
    en decenas de miles de simulaciones no aparece). Esta función da una
    certeza MATEMÁTICA (el escenario es literalmente imposible dado el
    reglamento), y se vuelve relevante recién sobre el final del campeonato,
    cuando quedan pocos puntos en juego."""
    season = season or config.CURRENT_SEASON
    st = load_standings(season)
    rem = remaining_fixture_zona_a(season)

    cnt = {}
    if rem is not None and not rem.empty:
        for _, r in rem.iterrows():
            for side in ("home_team_id", "away_team_id"):
                tid = r[side]
                if pd.notna(tid):
                    tid = int(tid)
                    cnt[tid] = cnt.get(tid, 0) + 1

    d = st.copy()
    d["restantes"] = d["team_id"].map(cnt).fillna(0).astype(int)
    d["piso"] = d["points"]
    d["techo"] = d["points"] + d["restantes"] * 3

    n = len(d)
    pueden_col, garantizados_col = [], []
    desc_col, play_col = [], []
    for _, row in d.iterrows():
        otros = d["team_id"] != row["team_id"]
        # rivales que TODAVÍA pueden terminar por encima
        pueden = int((((d["techo"] >= row["piso"]) if empate_puede_superar
                       else (d["techo"] > row["piso"])) & otros).sum())
        # rivales que YA están por encima pase lo que pase
        garantizados = int(((d["piso"] > row["techo"]) & otros).sum())
        pueden_col.append(pueden)
        garantizados_col.append(garantizados)

        if garantizados >= n - n_descienden:
            desc_col.append("Matemáticamente descendido")
        elif pueden <= n - n_descienden - 1:
            desc_col.append("Matemáticamente salvado")
        else:
            desc_col.append("Con chance de descenso")

        if pueden <= n_playoff - 1:
            play_col.append("Clasificado")
        elif garantizados >= n_playoff:
            play_col.append("Eliminado del playoff")
        else:
            play_col.append("En pelea")

    d["rivales_que_podrian_superarlo"] = pueden_col
    d["rivales_garantizados_arriba"] = garantizados_col
    d["estado_descenso"] = desc_col
    d["estado_playoff"] = play_col
    # alias retrocompatible: el nombre viejo de la columna de descenso
    d["estado_matematico"] = desc_col
    return d[["position", "team_id", "team_name", "points", "matches_played", "restantes",
              "piso", "techo", "rivales_que_podrian_superarlo",
              "rivales_garantizados_arriba", "estado_playoff", "estado_descenso",
              "estado_matematico"]]


# ─────────────────────── cuándo se define cada situación ──────────────────
def _remaining_by_round(season):
    """[(ronda, [(home_id, away_id), ...])] de lo que falta, solo Zona A."""
    st = load_standings(season)
    ids = set(int(t) for t in st["team_id"])
    rem = remaining_fixture_zona_a(season)
    if rem is None or rem.empty:
        return []
    rem = rem.copy()
    rem["round"] = rem["round"].astype(int)
    out = []
    for r in sorted(rem["round"].unique()):
        ms = [(int(x.home_team_id), int(x.away_team_id))
              for _, x in rem[rem["round"] == r].iterrows()
              if int(x.home_team_id) in ids and int(x.away_team_id) in ids]
        if ms:
            out.append((r, ms))
    return out


def earliest_decision_round(season=None, team_id=None, n_descienden=2,
                            n_playoff=REDUCIDO_HASTA, kind="descenso",
                            iters=20000, seed=7):
    """Fecha MÁS TEMPRANA en la que un equipo podría quedar matemáticamente
    descendido (`kind='descenso'`) o clasificado a la postemporada
    (`kind='playoff'`), construyendo el escenario más rápido posible.

    No es un pronóstico: es el peor (o mejor) caso admisible por el
    calendario. Para el descenso, el equipo pierde todos sus partidos y el
    resto reparte puntos de la forma que más rápido lo condena; para el
    playoff, gana todos y sus perseguidores pierden lo que pueden perder.

    Devuelve un dict con la ronda encontrada, el techo/piso del equipo en esa
    ronda y cuántos rivales quedan de un lado y del otro. `ronda=None`
    significa que ni en el escenario más rápido llega a definirse.

    OJO: la búsqueda es heurística con reintentos aleatorios. Si dice que en
    una ronda NO se puede, es que no encontró el escenario, no una prueba
    formal de imposibilidad; el resultado positivo, en cambio, sí es
    constructivo (existe el escenario que lo produce)."""
    season = season or config.CURRENT_SEASON
    st = load_standings(season).set_index("team_id")
    pts = {int(k): int(v) for k, v in st["points"].items()}
    ids = list(pts)
    n = len(ids)
    if team_id is None:
        raise ValueError("Hace falta team_id.")
    team_id = int(team_id)

    por_ronda = _remaining_by_round(season)
    rest = {t: 0 for t in ids}
    for _, ms in por_ronda:
        for h, a in ms:
            rest[h] += 1
            rest[a] += 1

    rng = np.random.default_rng(seed)
    # cuántos rivales tienen que quedar por encima (descenso) o cuántos
    # pueden quedar por encima (playoff)
    objetivo = (n - n_descienden) if kind == "descenso" else None

    for k in range(1, len(por_ronda) + 1):
        rr = por_ronda[:k]
        propios = sum(1 for _, ms in rr for h, a in ms if team_id in (h, a))
        if kind == "descenso":
            T = pts[team_id] + 3 * (rest[team_id] - propios)   # su techo
        else:
            T = pts[team_id] + 3 * propios                     # su piso si gana todo

        for intento in range(max(1, iters // 200)):
            P = dict(pts)
            if kind == "descenso":
                need = {t: max(0, T + 1 - pts[t]) for t in ids if t != team_id}
                # alcanza con `objetivo` rivales arriba: se descartan los más caros
                drop = set(sorted(need, key=lambda t: -need[t])[:n - 1 - objetivo])
            else:
                drop = set()
            for _, ms in rr:
                for h, a in ms:
                    if team_id in (h, a):
                        otro = a if h == team_id else h
                        if kind == "descenso":
                            if otro not in drop:
                                P[otro] += 3
                        else:
                            P[team_id] += 3
                        continue
                    if kind == "descenso":
                        dh = T + 1 - P[h] if h not in drop else -99
                        da = T + 1 - P[a] if a not in drop else -99
                        if dh <= 0 and da <= 0:
                            P[h] += 1
                            P[a] += 1
                        elif dh > da or (dh == da and rng.random() < .5):
                            P[h] += 3
                        else:
                            P[a] += 3
                    else:
                        # playoff: los rivales suman lo MENOS posible, pero
                        # cada partido reparte al menos 2 puntos (empate)
                        P[h] += 1
                        P[a] += 1

            if kind == "descenso":
                arriba = sum(1 for t in ids if t != team_id and t not in drop and P[t] > T)
                if arriba >= objetivo:
                    return {"ronda": rr[-1][0], "k_rondas": k, "partidos_propios": propios,
                            "techo": T, "rivales_arriba": arriba, "necesarios": objetivo,
                            "kind": kind}
            else:
                # queda clasificado si como mucho n_playoff-1 rivales pueden igualarlo
                techos = {t: P[t] + 3 * (rest[t] - sum(1 for _, ms in rr for h, a in ms if t in (h, a)))
                          for t in ids if t != team_id}
                pueden = sum(1 for t, v in techos.items() if v >= T)
                if pueden <= n_playoff - 1:
                    return {"ronda": rr[-1][0], "k_rondas": k, "partidos_propios": propios,
                            "piso": T, "rivales_que_pueden_superarlo": pueden,
                            "kind": kind}
    return {"ronda": None, "kind": kind}


def decision_round_distribution(season=None, team_id=None, n_sims=20000,
                                n_descienden=2, seed=None, sims=None):
    """Distribución simulada de la fecha en la que la situación de descenso de
    un equipo queda matemáticamente resuelta (para bien o para mal).

    A diferencia de `earliest_decision_round`, que da el caso extremo, esto
    juega el torneo `n_sims` veces con el mismo modelo de la proyección y
    anota en qué fecha se cierra el tema en cada una.

    Devuelve un dict con las probabilidades de cada desenlace y un Series con
    la distribución de la fecha de confirmación del descenso."""
    season = season or config.CURRENT_SEASON
    team_id = int(team_id)
    st = load_standings(season)
    ids = [int(t) for t in st["team_id"]]
    idx = {t: i for i, t in enumerate(ids)}
    n = len(ids)
    j = idx[team_id]

    por_ronda = _remaining_by_round(season)
    rest = {t: 0 for t in ids}
    for _, ms in por_ronda:
        for h, a in ms:
            rest[h] += 1
            rest[a] += 1

    strengths = fit_dc_strengths(season)
    fit = strengths.attrs["dc_fit"]
    rng = np.random.default_rng(seed)

    plano = [(r, h, a) for r, ms in por_ronda for h, a in ms]
    lam = np.array([DC.match_lambdas(fit, h, a)[0] for _, h, a in plano])
    mu = np.array([DC.match_lambdas(fit, h, a)[1] for _, h, a in plano])
    hg, ag = DC.sample_scores(lam, mu, fit["rho"], n_sims, rng)
    hp = np.where(hg > ag, 3, np.where(hg == ag, 1, 0))
    ap = np.where(ag > hg, 3, np.where(ag == hg, 1, 0))

    P = np.tile(np.array([st.set_index("team_id").loc[t, "points"] for t in ids], float), (n_sims, 1))
    Rm = np.tile(np.array([rest[t] for t in ids], float), (n_sims, 1))
    ronda = np.full(n_sims, -1)
    tipo = np.zeros(n_sims, dtype=int)      # 1 = descendido, 2 = salvado

    for r, _ in por_ronda:
        for i, (rr, h, a) in enumerate(plano):
            if rr != r:
                continue
            P[:, idx[h]] += hp[:, i]; Rm[:, idx[h]] -= 1
            P[:, idx[a]] += ap[:, i]; Rm[:, idx[a]] -= 1
        techo = P + 3 * Rm
        arriba = (P > techo[:, [j]]).sum(axis=1)      # rivales con piso > su techo
        abajo = (techo < P[:, [j]]).sum(axis=1)       # rivales con techo < su piso
        libre = ronda < 0
        desc = libre & (arriba >= n - n_descienden)
        salv = libre & (abajo >= n_descienden)
        ronda[desc] = r; tipo[desc] = 1
        ronda[salv] = r; tipo[salv] = 2

    d = pd.Series(ronda[tipo == 1])
    return {
        "prob_descendido": float((tipo == 1).mean()),
        "prob_salvado": float((tipo == 2).mean()),
        "prob_sin_definir": float((tipo == 0).mean()),
        "fecha_mediana": (int(d.median()) if len(d) else None),
        "distribucion_descenso": (d.value_counts(normalize=True).sort_index() if len(d)
                                  else pd.Series(dtype=float)),
    }
