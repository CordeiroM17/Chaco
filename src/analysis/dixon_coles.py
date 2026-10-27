"""
dixon_coles.py
===============
Modelo Dixon-Coles (1997) ajustado por máxima verosimilitud sobre los
resultados reales del torneo, con dos agregados propios del repo:

1. **Decaimiento temporal** φ(t) = exp(-ξ·días), la pseudo-verosimilitud de
   la ecuación (4.5) del paper. ξ se elige por backtesting, no a ojo
   (`src/analysis/backtest.py`).
2. **xG como observación auxiliar**: cada partido aporta el término de goles
   reales con peso (1 - w_xg) y un término Poisson con el xG del partido con
   peso w_xg. Sirve para amortiguar la varianza de la definición. El
   backtesting pareado elige `w_xg = 0.8`, o sea que el xG manda en el
   rating; los goles reales siguen siendo la única fuente de ρ/τ, de la
   escala de goles (`level`) y de los partidos sin shotmap, donde el peso
   efectivo `w · (1 - w_xg · has_xg)` deja el término de goles intacto.

Paper: `docs/papers/Dixon_Coles_1997_Modelling_Association_Football_Scores.pdf`

Modelo (ec. 4.2 del paper), para un partido entre el local i y el visitante j:

    P(X=x, Y=y) = τ(x, y, λ, μ) · Poisson(x; λ) · Poisson(y; μ)
    λ = α_i · β_j · γ        (goles esperados del local)
    μ = α_j · β_i            (goles esperados del visitante)

    τ = 1 - λμρ   si x=0, y=0
        1 + λρ    si x=0, y=1
        1 + μρ    si x=1, y=0
        1 - ρ     si x=1, y=1
        1         en cualquier otro caso

α es el ataque (más es mejor), β la defensa (menos es mejor), γ la ventaja
de localía y ρ la corrección de dependencia para los resultados bajos, que
es lo que el Poisson independiente no puede reproducir (0-0, 1-0, 0-1, 1-1).
Restricción de identificabilidad: promedio de α = 1.

Los ratings son **estáticos**: se ajustan una vez con toda la historia
disponible hasta la fecha de corte y quedan fijos para todo lo que se
simula hacia adelante. El decaimiento temporal ya le da más peso a lo
reciente dentro del ajuste; no hay actualización dentro de la simulación.

Uso:
    from src.analysis import dixon_coles as DC
    matches = DC.build_match_table("2026")
    fit = DC.fit(matches)
    lam, mu = DC.match_lambdas(fit, home_id, away_id)
    pH, pD, pA = DC.outcome_probs(lam, mu, fit["rho"])
"""
import os
import glob

import numpy as np
import pandas as pd
from scipy.optimize import minimize

import config

# Defaults elegidos por backtesting (ver src/analysis/backtest.py y
# EXPLICACION_montecarlo.md). Viven en config.py para no dispersar constantes.
XI_DEFAULT    = getattr(config, "DC_XI", 0.0035)      # decaimiento por día
W_XG_DEFAULT  = getattr(config, "DC_W_XG", 0.30)      # peso del xG (goles = 0.70)
MAX_GOALS     = getattr(config, "DC_MAX_GOALS", 12)   # techo de la grilla de scores

_TAU_FLOOR = 1e-8          # τ no puede ser <= 0 (rompería el log)
_PIN = 1e-6                # penalización que fija la dirección plana α·c / β/c


# ─────────────────────────── datos ───────────────────────────────────────────
_MATCH_TABLE_CACHE = {}


def _xg_by_event(season):
    """{event_id: (xg_local, xg_visitante)} recorriendo todas las carpetas de
    partido del repo (Chaco + rivales). Cada carpeta trae `event_clean.csv`
    (de ahí sale el event_id, que es la clave común con el fixture) y
    `shotmap_clean.csv` (xG de cada remate, con `isHome` para saber de qué
    lado va). Un partido scrapeado por dos equipos distintos da el mismo
    valor, así que sobrescribir no molesta."""
    out = {}
    roots = [os.path.join(config.season_data_dir(season), "*"),
             os.path.join(config.rivals_dir(season), "*", "*")]
    for pattern in roots:
        for d in glob.glob(pattern):
            ev = os.path.join(d, "event_clean.csv")
            sm = os.path.join(d, "shotmap_clean.csv")
            if not (os.path.isfile(ev) and os.path.isfile(sm)):
                continue
            try:
                e = pd.read_csv(ev)
                s = pd.read_csv(sm)
            except Exception:
                continue
            if e.empty or "event_id" not in e.columns or "xg" not in s.columns:
                continue
            eid = int(e.iloc[0]["event_id"])
            home = s.loc[s["isHome"] == True, "xg"].sum()
            away = s.loc[s["isHome"] == False, "xg"].sum()
            out[eid] = (float(home), float(away))
    return out


def build_match_table(season=None, refresh=False):
    """Tabla de partidos JUGADOS del torneo, a nivel partido, con goles y xG.

    Usa el fixture completo (las dos zonas, 36 equipos): el modelo se ajusta
    sobre el torneo entero aunque después solo se simule la Zona A. Así los
    rivales interzonales de Zona B tienen ataque y defensa propios en vez de
    entrar como "equipo promedio", y el ajuste tiene el doble de partidos
    para estimar la localía y ρ, que son parámetros comunes a todos.

    El xG solo existe para los partidos scrapeados (los de Zona A); en el
    resto queda NaN y esos partidos aportan únicamente el término de goles.

    Columnas: event_id, round, date, home_team_id, away_team_id, home_team,
    away_team, home_goals, away_goals, home_xg, away_xg.
    """
    season = season or config.CURRENT_SEASON
    key = str(season)
    if not refresh and key in _MATCH_TABLE_CACHE:
        return _MATCH_TABLE_CACHE[key].copy()

    from src.scraping.fixture_scraper import load_fixture
    fx = load_fixture(season)
    if fx is None or fx.empty:
        raise RuntimeError(f"No hay fixture.csv para la temporada {season}.")

    m = fx[(fx["status_type"] == "finished")
           & fx["home_score"].notna() & fx["away_score"].notna()].copy()
    m = m.drop_duplicates(subset="event_id")
    m["date"] = pd.to_datetime(m["start_time_utc"], errors="coerce", utc=True)
    m = m.dropna(subset=["date", "home_team_id", "away_team_id"])
    m = m.sort_values("date").reset_index(drop=True)

    xg = _xg_by_event(season)
    m["home_xg"] = m["event_id"].map(lambda e: xg.get(int(e), (np.nan, np.nan))[0])
    m["away_xg"] = m["event_id"].map(lambda e: xg.get(int(e), (np.nan, np.nan))[1])

    out = pd.DataFrame({
        "event_id":     m["event_id"].astype(int),
        "round":        m["round"],
        "date":         m["date"],
        "home_team_id": m["home_team_id"].astype(int),
        "away_team_id": m["away_team_id"].astype(int),
        "home_team":    m["home_team"],
        "away_team":    m["away_team"],
        "home_goals":   m["home_score"].astype(int),
        "away_goals":   m["away_score"].astype(int),
        "home_xg":      m["home_xg"],
        "away_xg":      m["away_xg"],
    })
    _MATCH_TABLE_CACHE[key] = out.copy()
    return out


# ─────────────────────────── τ de Dixon-Coles ────────────────────────────────
def tau(x, y, lam, mu, rho):
    """Corrección de dependencia para resultados bajos (ec. 4.2). Vectorizada:
    x, y, lam, mu son arrays del mismo largo."""
    x = np.asarray(x); y = np.asarray(y)
    t = np.ones(np.broadcast(x, y, lam, mu).shape, dtype=float)
    t = np.where((x == 0) & (y == 0), 1.0 - lam * mu * rho, t)
    t = np.where((x == 0) & (y == 1), 1.0 + lam * rho, t)
    t = np.where((x == 1) & (y == 0), 1.0 + mu * rho, t)
    t = np.where((x == 1) & (y == 1), 1.0 - rho, t)
    return t


def _dlog_tau(x, y, lam, mu, rho):
    """Derivadas de log τ respecto de log λ, log μ y ρ (para el gradiente
    analítico del optimizador)."""
    t = np.maximum(tau(x, y, lam, mu, rho), _TAU_FLOOR)
    z = np.zeros_like(t)

    d_lam = np.where((x == 0) & (y == 0), -lam * mu * rho / t,
             np.where((x == 0) & (y == 1),  lam * rho / t, z))
    d_mu  = np.where((x == 0) & (y == 0), -lam * mu * rho / t,
             np.where((x == 1) & (y == 0),  mu * rho / t, z))
    d_rho = np.where((x == 0) & (y == 0), -lam * mu / t,
             np.where((x == 0) & (y == 1),  lam / t,
              np.where((x == 1) & (y == 0), mu / t,
               np.where((x == 1) & (y == 1), -1.0 / t, z))))
    return d_lam, d_mu, d_rho


# ─────────────────────────── ajuste (MLE) ────────────────────────────────────
def _prepare(matches, xi, ref_date):
    """Índices de equipo, pesos temporales y arrays listos para el optimizador."""
    teams = sorted(set(matches["home_team_id"]) | set(matches["away_team_id"]))
    idx = {t: i for i, t in enumerate(teams)}
    hi = matches["home_team_id"].map(idx).to_numpy()
    ai = matches["away_team_id"].map(idx).to_numpy()
    x  = matches["home_goals"].to_numpy(dtype=float)
    y  = matches["away_goals"].to_numpy(dtype=float)

    ref = ref_date if ref_date is not None else matches["date"].max()
    ref = pd.Timestamp(ref)
    if ref.tzinfo is None:
        ref = ref.tz_localize("UTC")
    days = (ref - matches["date"]).dt.total_seconds().to_numpy() / 86400.0
    days = np.maximum(days, 0.0)
    w = np.exp(-xi * days)

    xgh = matches["home_xg"].to_numpy(dtype=float)
    xga = matches["away_xg"].to_numpy(dtype=float)
    has_xg = np.isfinite(xgh) & np.isfinite(xga)
    return teams, idx, hi, ai, x, y, w, xgh, xga, has_xg


def _objective(matches, xi, w_xg, ref_date):
    """Arma la función objetivo (negativo del log-likelihood ponderado) y su
    gradiente analítico. Separado de `fit()` para poder testear el gradiente
    contra diferencias finitas."""
    teams, idx, hi, ai, x, y, w, xgh, xga, has_xg = _prepare(matches, xi, ref_date)
    n = len(teams)
    wg = w * (1.0 - w_xg * has_xg)      # peso efectivo del término de goles
    wx = w * (w_xg * has_xg)            # peso efectivo del término de xG
    xgh = np.where(has_xg, xgh, 0.0)
    xga = np.where(has_xg, xga, 0.0)
    # τ (la dependencia entre los goles del local y del visitante) se estima
    # SIEMPRE con los goles reales y peso completo, aunque w_xg mande la mayor
    # parte del peso al xG: el xG no tiene resultado exacto del que sacar esa
    # dependencia. Sin esto, w_xg=1 dejaría a ρ sin datos y sin gradiente.

    def unpack(p):
        la = p[:n]; lb = p[n:2 * n]; lg = p[2 * n]; rho = p[2 * n + 1]
        log_lam = la[hi] + lb[ai] + lg
        log_mu  = la[ai] + lb[hi]
        return la, lb, lg, rho, np.exp(log_lam), np.exp(log_mu)

    def nll(p):
        la, lb, lg, rho, lam, mu = unpack(p)
        t = np.maximum(tau(x, y, lam, mu, rho), _TAU_FLOOR)
        ll_goals = x * np.log(lam) - lam + y * np.log(mu) - mu
        ll_xg    = xgh * np.log(lam) - lam + xga * np.log(mu) - mu
        total = (np.sum(w * np.log(t)) + np.sum(wg * ll_goals)
                 + np.sum(wx * ll_xg))
        return -total + _PIN * (la.mean() ** 2) * len(x)

    def grad(p):
        la, lb, lg, rho, lam, mu = unpack(p)
        dt_lam, dt_mu, dt_rho = _dlog_tau(x, y, lam, mu, rho)
        # d(ll)/d(log λ) y d(ll)/d(log μ), sumando goles y xG con sus pesos
        g_lam = w * dt_lam + wg * (x - lam) + wx * (xgh - lam)
        g_mu  = w * dt_mu  + wg * (y - mu)   + wx * (xga - mu)

        d_la = np.zeros(n); d_lb = np.zeros(n)
        np.add.at(d_la, hi, g_lam)      # log λ = la[local] + lb[visitante] + lg
        np.add.at(d_lb, ai, g_lam)
        np.add.at(d_la, ai, g_mu)       # log μ = la[visitante] + lb[local]
        np.add.at(d_lb, hi, g_mu)
        d_lg = g_lam.sum()
        d_rho = np.sum(w * dt_rho)

        out = -np.concatenate([d_la, d_lb, [d_lg], [d_rho]])
        out[:n] += 2 * _PIN * la.mean() * len(x) / n
        return out

    return nll, grad, unpack, teams, w


def fit(matches, xi=None, w_xg=None, ref_date=None, rho0=-0.05,
        fix_rho=None, calibrate_level=True, verbose=False):
    """Ajusta α, β (por equipo), γ (localía) y ρ por máxima verosimilitud
    ponderada en el tiempo.

    `matches`: salida de `build_match_table()`, ya filtrada a la ventana de
    entrenamiento que corresponda (en un backtest, solo lo jugado antes del
    corte).
    `xi`: decaimiento por día. 0 = todos los partidos pesan igual.
    `w_xg`: peso del término de xG (0 = solo goles observados).
    `ref_date`: fecha respecto de la cual se mide la antigüedad; por defecto,
    el último partido de `matches`.

    Devuelve un dict con alpha/beta (dict team_id -> valor), gamma, rho, la
    lista de equipos, el log-likelihood y los hiperparámetros usados.
    """
    xi = XI_DEFAULT if xi is None else xi
    w_xg = W_XG_DEFAULT if w_xg is None else w_xg
    if matches is None or matches.empty:
        raise RuntimeError("No hay partidos para ajustar el modelo.")

    nll, grad, unpack, teams, w = _objective(matches, xi, w_xg, ref_date)
    n = len(teams)
    r0 = rho0 if fix_rho is None else fix_rho
    p0 = np.concatenate([np.zeros(n), np.zeros(n), [np.log(1.25)], [r0]])
    # fix_rho=0 apaga la corrección de Dixon-Coles y deja el Poisson
    # independiente de Maher, para poder medir cuánto aporta τ.
    rho_bounds = (-0.85, 0.85) if fix_rho is None else (fix_rho, fix_rho)
    bounds = ([(-2.0, 2.0)] * n + [(-2.0, 2.0)] * n
              + [(-1.0, 1.5)] + [rho_bounds])
    res = minimize(nll, p0, jac=grad, method="L-BFGS-B", bounds=bounds,
                   options={"maxiter": 2000, "ftol": 1e-11, "gtol": 1e-8})

    la, lb, lg, rho, _, _ = unpack(res.x)
    alpha = np.exp(la); beta = np.exp(lb); gamma = float(np.exp(lg))
    # Restricción del paper: promedio de α = 1. λ = α_i·β_j·γ no cambia si se
    # escala α por 1/c y β por c, así que se normaliza después de optimizar.
    c = alpha.mean()
    alpha = alpha / c
    beta = beta * c

    # Escala de goles: el xG de SofaScore promedia por encima de los goles
    # reales de esta liga, así que si w_xg > 0 el ajuste queda apuntando a un
    # nivel de goles más alto del que se convierte de verdad. `level` corrige
    # eso con un solo número: es el estimador de máxima verosimilitud del
    # factor común que iguala los goles esperados a los goles OBSERVADOS
    # (ponderados en el tiempo igual que el resto). Queda "la forma del rating
    # la pone el xG, el nivel lo ponen los goles que entraron".
    level = 1.0
    if calibrate_level:
        la2 = np.log(alpha); lb2 = np.log(beta)
        _, idx, hi, ai, x, y, w, _, _, _ = _prepare(matches, xi, ref_date)
        lam = np.exp(la2[hi] + lb2[ai] + np.log(gamma))
        mu  = np.exp(la2[ai] + lb2[hi])
        denom = float(np.sum(w * (lam + mu)))
        if denom > 0:
            level = float(np.sum(w * (x + y)) / denom)

    if verbose:
        print(f"DC fit: {len(matches)} partidos, {n} equipos, xi={xi}, w_xg={w_xg} | "
              f"gamma={gamma:.3f} rho={rho:+.3f} level={level:.3f} | ok={res.success}")

    return {
        "alpha": dict(zip(teams, alpha)),
        "beta":  dict(zip(teams, beta)),
        "gamma": gamma,
        "level": level,
        "rho":   float(rho),
        "teams": teams,
        "xi": xi, "w_xg": w_xg,
        "n_matches": int(len(matches)),
        "ref_date": (ref_date if ref_date is not None else matches["date"].max()),
        "loglik": float(-res.fun),
        "success": bool(res.success),
        # Tamaño de muestra efectivo (Kish) con los pesos temporales: cuántos
        # partidos "de peso completo" equivalen a la ventana ponderada.
        "n_eff": float(w.sum() ** 2 / np.sum(w ** 2)),
    }


def strengths_table(fit_res, team_names=None):
    """α y β por equipo en un DataFrame ordenable, para auditar el ajuste."""
    rows = []
    for t in fit_res["teams"]:
        rows.append({"team_id": t,
                     "team_name": (team_names or {}).get(t, t),
                     "ataque": fit_res["alpha"][t],
                     "defensa": fit_res["beta"][t]})
    df = pd.DataFrame(rows).sort_values("ataque", ascending=False)
    return df.reset_index(drop=True)


# ─────────────────────────── predicción ──────────────────────────────────────
def match_lambdas(fit_res, home_id, away_id, default=1.0):
    """(λ_local, λ_visitante). Un equipo sin parámetros (no jugó nada en la
    ventana de ajuste) entra como promedio de la liga."""
    a_h = fit_res["alpha"].get(home_id, default)
    b_h = fit_res["beta"].get(home_id, default)
    a_a = fit_res["alpha"].get(away_id, default)
    b_a = fit_res["beta"].get(away_id, default)
    lv = fit_res.get("level", 1.0)
    lam = a_h * b_a * fit_res["gamma"] * lv
    mu  = a_a * b_h * lv
    return max(float(lam), 0.02), max(float(mu), 0.02)


def score_matrix(lam, mu, rho, max_goals=MAX_GOALS):
    """Matriz (max_goals+1)² con la probabilidad de cada resultado exacto,
    ya con la corrección τ y renormalizada."""
    from scipy.stats import poisson
    ph = poisson.pmf(np.arange(max_goals + 1), lam)
    pa = poisson.pmf(np.arange(max_goals + 1), mu)
    m = np.outer(ph, pa)
    m[0, 0] *= 1.0 - lam * mu * rho
    m[0, 1] *= 1.0 + lam * rho
    m[1, 0] *= 1.0 + mu * rho
    m[1, 1] *= 1.0 - rho
    m = np.maximum(m, 0.0)
    return m / m.sum()


def outcome_probs(lam, mu, rho, max_goals=MAX_GOALS):
    """(prob. gana local, empate, gana visitante)."""
    m = score_matrix(lam, mu, rho, max_goals)
    home = np.tril(m, -1).sum()      # filas > columnas
    draw = np.trace(m)
    away = np.triu(m, 1).sum()
    return float(home), float(draw), float(away)


def sample_scores(lam, mu, rho, n_sims, rng, max_goals=MAX_GOALS):
    """Muestrea resultados de la distribución conjunta de Dixon-Coles.

    Devuelve dos arrays (n_sims, n_partidos) con los goles del local y del
    visitante. Se arma la grilla de resultados exactos de cada partido una
    sola vez y se muestrea por inversión de la acumulada, así que el costo es
    una búsqueda binaria por simulación y por partido. Muestrear de la
    conjunta (y no dos Poisson por separado) es lo que mantiene la
    corrección τ dentro de la simulación."""
    lam = np.asarray(lam, dtype=float); mu = np.asarray(mu, dtype=float)
    n = len(lam)
    K = max_goals + 1
    hg = np.empty((n_sims, n), dtype=np.int16)
    ag = np.empty((n_sims, n), dtype=np.int16)
    for i in range(n):
        flat = score_matrix(lam[i], mu[i], rho, max_goals).ravel()
        cum = np.cumsum(flat)
        cum[-1] = 1.0
        k = np.searchsorted(cum, rng.random(n_sims))
        hg[:, i] = k // K
        ag[:, i] = k % K
    return hg, ag
