"""
backtest.py
============
Validación fuera de muestra del modelo de la tabla. Corta el campeonato en
una fecha (por defecto la 18), ajusta el modelo **solo con lo jugado hasta
ahí** y mide qué tan bien predice todo lo que vino después.

Dos usos:

1. `evaluate()` / `tune()`: elegir los hiperparámetros (ξ del decaimiento
   temporal, w_xg del peso del xG) con un criterio objetivo en vez de a ojo.
   El criterio es el del propio Dixon-Coles (ec. 4.7 del paper): la
   log-verosimilitud predictiva del resultado 1X2 de cada partido no visto.
   Se agrega RPS, que es el estándar en la literatura de pronóstico de
   fútbol y castiga equivocarse "lejos" (dar favorito al que pierde) más que
   equivocarse "cerca" (dar favorito al que empata).
2. `projection_backtest()`: la prueba de punta a punta. Simula desde el corte
   con los ratings congelados y compara los puntos que cada equipo sacó de
   verdad contra la distribución simulada. Si el modelo está bien calibrado,
   los puntos reales tienen que caer repartidos por toda la distribución, no
   siempre en las colas.
3. `walk_forward()` / `outcome_bias()`: "¿a cuántos le viene acertando?".
   Reajusta antes de cada fecha y predice solo esa fecha, que es como se usa
   en la realidad, y después revisa si sobra o falta alguna salida.

Uso:
    from src.analysis import backtest as BT
    BT.evaluate(cutoff_round=18)                  # una corrida
    BT.tune()                                     # grilla de ξ y w_xg
    BT.projection_backtest(cutoff_round=18)       # calibración de la proyección
    por_ronda, P, tot = BT.walk_forward()         # acierto real, fecha por fecha
    BT.outcome_bias(P)                            # ¿sobran empates? ¿faltan locales?
"""
import math
import numpy as np
import pandas as pd

import config
from src.analysis import dixon_coles as DC

CUTOFF_DEFAULT = 18
XI_GRID   = [0.0, 0.0015, 0.003, 0.005, 0.008, 0.012, 0.020]
W_XG_GRID = [0.0, 0.15, 0.30, 0.45, 0.60, 0.80, 1.00]
CUTOFFS_DEFAULT = (14, 16, 18, 20, 22)


# ─────────────────────────── partición ───────────────────────────────────────
def cutoff_date(matches, cutoff_round):
    """Fecha de calendario que corresponde a "cortar en la fecha N".

    Se usa la MEDIANA de las fechas de esa ronda, no el máximo. En este
    torneo la ronda 4 se jugó entera en junio (postergada), así que el máximo
    de las rondas 1-14 cae DESPUÉS de la ronda 18: cortar por el máximo hacía
    que entrenar "hasta la fecha 14" y "hasta la fecha 18" dieran exactamente
    el mismo conjunto. La mediana es robusta a esos reprogramados sueltos."""
    d = matches.loc[matches["round"] == cutoff_round, "date"]
    if d.empty:
        raise RuntimeError(f"La fecha {cutoff_round} no tiene partidos jugados.")
    return d.median()


def split(matches, cutoff_round=CUTOFF_DEFAULT, horizon_days=None):
    """(entrenamiento, prueba, fecha_de_corte) partiendo por FECHA de
    calendario, no por número de ronda.

    Todo lo jugado hasta la fecha de corte entrena; todo lo posterior se
    predice, incluidos los partidos de rondas viejas que se jugaron
    reprogramados después del corte (que es exactamente lo correcto: a la
    fecha del corte todavía no se habían jugado).

    `horizon_days` recorta la ventana de prueba a los primeros N días
    posteriores al corte, para medir aparte el pronóstico de corto plazo."""
    hasta = cutoff_date(matches, cutoff_round)
    train = matches[matches["date"] <= hasta].copy()
    test  = matches[matches["date"] >  hasta].copy()
    if horizon_days is not None:
        test = test[test["date"] <= hasta + pd.Timedelta(days=horizon_days)]
    return train, test, hasta


# ─────────────────────────── métricas ────────────────────────────────────────
def _outcome(row):
    if row["home_goals"] > row["away_goals"]:
        return 0
    return 1 if row["home_goals"] == row["away_goals"] else 2


def score_predictions(pred):
    """pred: DataFrame con columnas pH, pD, pA y el resultado real.
    Devuelve log-loss, S (la de la ec. 4.7), RPS, Brier y acierto del favorito.

    `rps` está NORMALIZADO: se divide por (r-1) = 2, que es la definición
    estándar (Epstein 1969; Constantinou & Fenton 2012). Así el número es
    comparable contra los benchmarks publicados — las casas de apuestas en
    ligas top rinden ~0.19-0.21 — y cae siempre en [0, 1].

    OJO si comparás contra corridas viejas: hasta 2026-09-02 esta función
    devolvía la suma SIN dividir por 2, o sea el doble. Los rankings y las
    comparaciones entre modelos no cambian (es un factor constante), pero los
    valores absolutos de cualquier tabla anterior a esa fecha están al doble.
    Queda `rps_sin_normalizar` para poder reproducirlos."""
    p = pred[["pH", "pD", "pA"]].to_numpy()
    p = np.clip(p, 1e-12, 1.0)
    o = pred["outcome"].to_numpy()
    n = len(pred)
    if n == 0:
        return {}
    p_true = p[np.arange(n), o]

    # RPS sobre el orden natural local / empate / visitante
    cum_p = np.cumsum(p, axis=1)[:, :2]
    obs = np.zeros_like(p)
    obs[np.arange(n), o] = 1.0
    cum_o = np.cumsum(obs, axis=1)[:, :2]
    rps_bruto = np.mean(np.sum((cum_p - cum_o) ** 2, axis=1))
    rps = rps_bruto / (p.shape[1] - 1)          # /(r-1) = /2

    brier = np.mean(np.sum((p - obs) ** 2, axis=1))
    return {
        "n": int(n),
        "logloss": float(-np.mean(np.log(p_true))),
        "S": float(np.sum(np.log(p_true))),
        "rps": float(rps),
        "rps_sin_normalizar": float(rps_bruto),
        "brier": float(brier),
        "acierto": float(np.mean(np.argmax(p, axis=1) == o)),
        "goles_pred": float(pred["lam"].mean() + pred["mu"].mean()),
        "goles_real": float((pred["home_goals"] + pred["away_goals"]).mean()),
        "empates_pred": float(pred["pD"].mean()),
        "empates_real": float((pred["outcome"] == 1).mean()),
    }


# ─────────────────────────── modelos a comparar ──────────────────────────────
def predict_dc(train, test, xi=None, w_xg=None, fix_rho=None, ref_date=None):
    """Ajusta Dixon-Coles con `train` y predice cada partido de `test`."""
    f = DC.fit(train, xi=xi, w_xg=w_xg, fix_rho=fix_rho,
               ref_date=ref_date if ref_date is not None else train["date"].max())
    rows = []
    for _, r in test.iterrows():
        lam, mu = DC.match_lambdas(f, int(r["home_team_id"]), int(r["away_team_id"]))
        pH, pD, pA = DC.outcome_probs(lam, mu, f["rho"])
        rows.append({"pH": pH, "pD": pD, "pA": pA, "lam": lam, "mu": mu})
    out = pd.concat([test.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    out["outcome"] = out.apply(_outcome, axis=1)
    return out, f


def _legacy_strengths(train, half_life=6, w_xg=0.5):
    """Réplica exacta del modelo viejo (`simulation.fit_team_strengths`) sobre
    la misma tabla de partidos: promedios por partido con decaimiento
    exponencial medido EN PARTIDOS, mezcla 50/50 con xG, normalización contra
    el promedio de la liga y localía global de un solo lado. Está acá para
    poder compararlo contra Dixon-Coles con el mismo corte y la misma métrica."""
    teams = sorted(set(train["home_team_id"]) | set(train["away_team_id"]))
    rows = []
    for t in teams:
        mine = train[(train["home_team_id"] == t) | (train["away_team_id"] == t)]
        mine = mine.sort_values("date")
        if mine.empty:
            continue
        is_home = (mine["home_team_id"] == t).to_numpy()
        gf = np.where(is_home, mine["home_goals"], mine["away_goals"]).astype(float)
        gc = np.where(is_home, mine["away_goals"], mine["home_goals"]).astype(float)
        xf = np.where(is_home, mine["home_xg"], mine["away_xg"]).astype(float)
        xc = np.where(is_home, mine["away_xg"], mine["home_xg"]).astype(float)
        n = len(mine)
        w = 0.5 ** (((n - 1) - np.arange(n)) / half_life)

        def wavg(v):
            m = np.isfinite(v)
            return float((v[m] * w[m]).sum() / w[m].sum()) if m.any() else np.nan

        gf_pp, gc_pp = wavg(gf), wavg(gc)
        xf_pp, xc_pp = wavg(xf), wavg(xc)
        if not np.isfinite(xf_pp):
            xf_pp = gf_pp
        if not np.isfinite(xc_pp):
            xc_pp = gc_pp
        rows.append({"team_id": t,
                     "blend_gf": w_xg * xf_pp + (1 - w_xg) * gf_pp,
                     "blend_gc": w_xg * xc_pp + (1 - w_xg) * gc_pp})
    d = pd.DataFrame(rows).set_index("team_id")
    avg = d["blend_gf"].mean()
    d["attack"] = d["blend_gf"] / avg
    d["defense"] = d["blend_gc"] / avg
    ha = train["home_goals"].mean() / max(train["away_goals"].mean(), 1e-9)
    return d, float(avg), float(ha)


def predict_legacy(train, test, half_life=6, w_xg=0.5, max_goals=DC.MAX_GOALS):
    """Modelo viejo: Poisson independiente, sin τ, con la localía de un solo
    lado y la escala inflada por el xG."""
    from scipy.stats import poisson
    d, avg, ha = _legacy_strengths(train, half_life=half_life, w_xg=w_xg)
    rows = []
    for _, r in test.iterrows():
        h, a = int(r["home_team_id"]), int(r["away_team_id"])
        ah = d["attack"].get(h, 1.0); dh = d["defense"].get(h, 1.0)
        aa = d["attack"].get(a, 1.0); da = d["defense"].get(a, 1.0)
        lam = max(ah * da * avg * ha, 0.05)
        mu  = max(aa * dh * avg, 0.05)
        ph = poisson.pmf(np.arange(max_goals + 1), lam)
        pa = poisson.pmf(np.arange(max_goals + 1), mu)
        m = np.outer(ph, pa); m /= m.sum()
        rows.append({"pH": np.tril(m, -1).sum(), "pD": np.trace(m),
                     "pA": np.triu(m, 1).sum(), "lam": lam, "mu": mu})
    out = pd.concat([test.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    out["outcome"] = out.apply(_outcome, axis=1)
    return out


# ─────────────────────────── evaluación ──────────────────────────────────────
def evaluate(season=None, cutoff_round=CUTOFF_DEFAULT, xi=None, w_xg=None,
             fix_rho=None, matches=None, verbose=True):
    """Corta en `cutoff_round`, ajusta con lo anterior y mide la predicción de
    TODO lo jugado después. Compara Dixon-Coles contra el modelo viejo."""
    matches = DC.build_match_table(season) if matches is None else matches
    train, test, hasta = split(matches, cutoff_round)
    if test.empty:
        raise RuntimeError(f"No hay partidos después de la fecha {cutoff_round}.")

    pred_dc, f = predict_dc(train, test, xi=xi, w_xg=w_xg, fix_rho=fix_rho)
    pred_lg = predict_legacy(train, test)
    m_dc = score_predictions(pred_dc)
    m_lg = score_predictions(pred_lg)

    if verbose:
        print(f"Corte: fecha {cutoff_round} ({hasta:%Y-%m-%d}) | "
              f"entrena con {len(train)} partidos, predice {len(test)}")
        print(f"  Dixon-Coles (xi={f['xi']}, w_xg={f['w_xg']}, rho={f['rho']:+.3f}, "
              f"gamma={f['gamma']:.3f})")
        print(f"    logloss {m_dc['logloss']:.4f} | RPS {m_dc['rps']:.4f} | "
              f"acierto {m_dc['acierto']*100:.1f}% | "
              f"goles {m_dc['goles_pred']:.2f} vs {m_dc['goles_real']:.2f} reales | "
              f"empates {m_dc['empates_pred']*100:.1f}% vs {m_dc['empates_real']*100:.1f}%")
        print(f"  Modelo viejo (half_life=6 partidos, w_xg=0.5, Poisson independiente)")
        print(f"    logloss {m_lg['logloss']:.4f} | RPS {m_lg['rps']:.4f} | "
              f"acierto {m_lg['acierto']*100:.1f}% | "
              f"goles {m_lg['goles_pred']:.2f} vs {m_lg['goles_real']:.2f} reales | "
              f"empates {m_lg['empates_pred']*100:.1f}% vs {m_lg['empates_real']*100:.1f}%")
    return {"dc": m_dc, "legacy": m_lg, "fit": f,
            "pred_dc": pred_dc, "pred_legacy": pred_lg,
            "train": train, "test": test, "cutoff_date": hasta}


def tune(season=None, cutoffs=CUTOFFS_DEFAULT, xi_grid=None, w_xg_grid=None,
         horizon_days=None, matches=None, verbose=True):
    """Grilla de (ξ, w_xg) evaluada con origen móvil: se repite el corte en
    varias fechas y se promedian las métricas, para no elegir parámetros que
    andan bien en un solo corte por casualidad.

    Devuelve un DataFrame ordenado por log-loss (menor es mejor)."""
    matches = DC.build_match_table(season) if matches is None else matches
    xi_grid = XI_GRID if xi_grid is None else xi_grid
    w_xg_grid = W_XG_GRID if w_xg_grid is None else w_xg_grid

    splits = []
    for c in cutoffs:
        tr, te, _ = split(matches, c, horizon_days)
        if not te.empty:
            splits.append((c, tr, te))

    rows = []
    for xi in xi_grid:
        for wx in w_xg_grid:
            acc = []
            for c, tr, te in splits:
                pred, _ = predict_dc(tr, te, xi=xi, w_xg=wx)
                m = score_predictions(pred)
                m["cutoff"] = c
                acc.append(m)
            a = pd.DataFrame(acc)
            rows.append({
                "xi": xi, "w_xg": wx,
                "half_life_dias": (np.log(2) / xi) if xi > 0 else np.inf,
                "logloss": a["logloss"].mean(),
                "rps": a["rps"].mean(),
                "brier": a["brier"].mean(),
                "acierto": a["acierto"].mean(),
                "S": a["S"].sum(),
                "n": int(a["n"].sum()),
            })
            if verbose:
                r = rows[-1]
                print(f"  xi={xi:<7} w_xg={wx:<5} -> logloss {r['logloss']:.4f} "
                      f"RPS {r['rps']:.4f} acierto {r['acierto']*100:.1f}%")
    out = pd.DataFrame(rows).sort_values("logloss").reset_index(drop=True)
    return out


def ablation(season=None, cutoffs=CUTOFFS_DEFAULT, xi=None, w_xg=None, matches=None):
    """Cuánto aporta cada pieza: la corrección τ de Dixon-Coles, el
    decaimiento temporal y el xG. Todo con los mismos cortes y la misma
    métrica que `tune()`."""
    matches = DC.build_match_table(season) if matches is None else matches
    xi = DC.XI_DEFAULT if xi is None else xi
    w_xg = DC.W_XG_DEFAULT if w_xg is None else w_xg
    variantes = {
        "DC completo":            dict(xi=xi,  w_xg=w_xg, fix_rho=None),
        "sin tau (Poisson indep)": dict(xi=xi,  w_xg=w_xg, fix_rho=0.0),
        "sin decaimiento (xi=0)": dict(xi=0.0, w_xg=w_xg, fix_rho=None),
        "sin xG (w_xg=0)":        dict(xi=xi,  w_xg=0.0,  fix_rho=None),
        "solo xG (w_xg=1)":       dict(xi=xi,  w_xg=1.0,  fix_rho=None),
    }
    rows = []
    for nombre, kw in variantes.items():
        acc = []
        for c in cutoffs:
            tr, te, _ = split(matches, c)
            if te.empty:
                continue
            pred, _ = predict_dc(tr, te, **kw)
            acc.append(score_predictions(pred))
        a = pd.DataFrame(acc)
        rows.append({"variante": nombre, "logloss": a["logloss"].mean(),
                     "rps": a["rps"].mean(), "acierto": a["acierto"].mean()})
    # el modelo viejo, con la misma vara
    acc = []
    for c in cutoffs:
        tr, te, _ = split(matches, c)
        if not te.empty:
            acc.append(score_predictions(predict_legacy(tr, te)))
    a = pd.DataFrame(acc)
    rows.append({"variante": "modelo viejo", "logloss": a["logloss"].mean(),
                 "rps": a["rps"].mean(), "acierto": a["acierto"].mean()})
    return pd.DataFrame(rows).sort_values("logloss").reset_index(drop=True)


def calibration(pred, bins=None):
    """Tabla de calibración: de los partidos donde el modelo dio entre 40% y
    50% de victoria local, ¿en qué proporción ganó el local? Junta las tres
    salidas en la misma grilla de probabilidad."""
    bins = bins if bins is not None else [0, .1, .2, .3, .4, .5, .6, .7, 1.0]
    p = pred[["pH", "pD", "pA"]].to_numpy().ravel()
    o = pred["outcome"].to_numpy()
    hit = np.zeros((len(pred), 3)); hit[np.arange(len(pred)), o] = 1
    hit = hit.ravel()
    idx = np.digitize(p, bins) - 1
    rows = []
    for b in range(len(bins) - 1):
        m = idx == b
        if m.sum() == 0:
            continue
        rows.append({"rango": f"{bins[b]:.0%}-{bins[b+1]:.0%}",
                     "casos": int(m.sum()),
                     "prob_media": float(p[m].mean()),
                     "frecuencia_real": float(hit[m].mean())})
    return pd.DataFrame(rows)


# ─────────────────────────── proyección desde el corte ───────────────────────
def projection_backtest(season=None, cutoff_round=CUTOFF_DEFAULT, n_sims=5000,
                        seed=42, xi=None, w_xg=None, matches=None, verbose=True):
    """Prueba de punta a punta de la proyección, no de los partidos sueltos.

    Ajusta con lo jugado hasta el corte, congela los ratings y simula
    `n_sims` veces los partidos que se jugaron entre el corte y hoy. Después
    compara los puntos que cada equipo sacó de verdad en esa ventana contra
    su distribución simulada.

    Lo que interesa es el percentil (PIT): si el modelo está bien calibrado,
    los percentiles de los 36 equipos tienen que quedar repartidos entre 0 y
    1. Si se amontonan en los extremos, la simulación es demasiado confiada;
    si se amontonan en el medio, es demasiado ancha. Un 80% de cobertura
    quiere decir que el intervalo 10%-90% de la simulación contuvo los
    puntos reales en 8 de cada 10 equipos."""
    matches = DC.build_match_table(season) if matches is None else matches
    train, test, hasta = split(matches, cutoff_round)
    if test.empty:
        raise RuntimeError(f"No hay partidos después de la fecha {cutoff_round}.")

    f = DC.fit(train, xi=xi, w_xg=w_xg, ref_date=hasta)
    rng = np.random.default_rng(seed)

    teams = sorted(set(matches["home_team_id"]) | set(matches["away_team_id"]))
    pos = {t: i for i, t in enumerate(teams)}
    hi = test["home_team_id"].map(pos).to_numpy()
    ai = test["away_team_id"].map(pos).to_numpy()

    lam = np.empty(len(test)); mu = np.empty(len(test))
    for i, (_, r) in enumerate(test.iterrows()):
        lam[i], mu[i] = DC.match_lambdas(f, int(r["home_team_id"]), int(r["away_team_id"]))
    hg, ag = DC.sample_scores(lam, mu, f["rho"], n_sims, rng)

    hp = np.where(hg > ag, 3, np.where(hg == ag, 1, 0))
    ap = np.where(ag > hg, 3, np.where(hg == ag, 1, 0))
    pts = np.zeros((n_sims, len(teams)))
    for i in range(len(test)):
        pts[:, hi[i]] += hp[:, i]
        pts[:, ai[i]] += ap[:, i]

    real_h = np.where(test["home_goals"] > test["away_goals"], 3,
                      np.where(test["home_goals"] == test["away_goals"], 1, 0))
    real_a = np.where(test["away_goals"] > test["home_goals"], 3,
                      np.where(test["home_goals"] == test["away_goals"], 1, 0))
    real = np.zeros(len(teams))
    for i in range(len(test)):
        real[hi[i]] += real_h[i]
        real[ai[i]] += real_a[i]

    names = {}
    for _, r in matches.iterrows():
        names[int(r["home_team_id"])] = r["home_team"]
        names[int(r["away_team_id"])] = r["away_team"]

    rows = []
    for j, t in enumerate(teams):
        col = pts[:, j]
        jugados = int(((test["home_team_id"] == t) | (test["away_team_id"] == t)).sum())
        if jugados == 0:
            continue
        rows.append({
            "team_id": t, "team_name": names.get(t, t), "pj_ventana": jugados,
            "pts_reales": float(real[j]),
            "pts_simulados": float(col.mean()),
            "p10": float(np.percentile(col, 10)),
            "p90": float(np.percentile(col, 90)),
            "percentil": float((col < real[j]).mean() + 0.5 * (col == real[j]).mean()),
        })
    d = pd.DataFrame(rows)
    d["error"] = d["pts_reales"] - d["pts_simulados"]
    d["dentro_80"] = (d["pts_reales"] >= d["p10"]) & (d["pts_reales"] <= d["p90"])

    resumen = {
        "cutoff_round": cutoff_round, "cutoff_date": hasta,
        "n_partidos_ventana": int(len(test)),
        "mae_puntos": float(d["error"].abs().mean()),
        "sesgo_puntos": float(d["error"].mean()),
        "cobertura_80": float(d["dentro_80"].mean()),
        "percentil_medio": float(d["percentil"].mean()),
    }
    if verbose:
        print(f"Proyección desde la fecha {cutoff_round} ({hasta:%Y-%m-%d}), "
              f"{len(test)} partidos simulados {n_sims} veces")
        print(f"  MAE {resumen['mae_puntos']:.2f} pts | sesgo {resumen['sesgo_puntos']:+.2f} | "
              f"cobertura del 80%: {resumen['cobertura_80']*100:.0f}% "
              f"({int(d['dentro_80'].sum())} de {len(d)} equipos)")
    return {"tabla": d.sort_values("error").reset_index(drop=True),
            "resumen": resumen, "fit": f}


# ─────────────────── backtest de POSICIONES de la tabla ──────────────────────
def _zone_table(matches, zona):
    """Tabla de posiciones de la zona acumulando los partidos de `matches`.

    Cuenta los partidos INTRAZONA y los INTERZONALES (verificado contra
    `standings.csv`: sumando los dos, la reconstrucción da exactamente los
    mismos pj/pts/gf/gc que publica SofaScore; solo con los intrazona quedan
    2 partidos y hasta 6 puntos de menos por equipo)."""
    acc = {t: dict(pj=0, pts=0, gf=0, gc=0) for t in zona}
    for _, r in matches.iterrows():
        for tid, gf, gc in ((int(r["home_team_id"]), r["home_goals"], r["away_goals"]),
                            (int(r["away_team_id"]), r["away_goals"], r["home_goals"])):
            if tid not in acc:
                continue
            d = acc[tid]
            d["pj"] += 1
            d["gf"] += int(gf)
            d["gc"] += int(gc)
            d["pts"] += 3 if gf > gc else (1 if gf == gc else 0)
    return pd.DataFrame([{"team_id": k, **v} for k, v in acc.items()]).set_index("team_id")


def _rank(points, gd, gf):
    """Posiciones (1 = mejor) por el desempate del torneo: pts, dif. gol, gf.
    Acepta arrays (n_sims, n_teams) o vectores de un solo escenario."""
    points = np.atleast_2d(points)
    gd = np.atleast_2d(gd)
    gf = np.atleast_2d(gf)
    score = points * 1_000_000 + gd * 1_000 + gf
    order = np.argsort(-score, axis=1)
    pos = np.empty_like(order)
    rows = np.arange(score.shape[0])[:, None]
    pos[rows, order] = np.arange(1, score.shape[1] + 1)[None, :]
    return pos


def position_backtest(season=None, cutoff_round=CUTOFF_DEFAULT, n_sims=20000,
                      seed=42, xi=None, w_xg=None, matches=None, verbose=True):
    """¿Con qué precisión ubica el modelo a los equipos en la tabla?

    Corta en `cutoff_round`, ajusta SOLO con lo jugado hasta ahí, congela los
    ratings y simula los partidos que se jugaron entre el corte y hoy.
    Después compara la posición proyectada de cada equipo contra la que
    realmente ocupa hoy.

    A diferencia de `projection_backtest()`, que mide puntos, acá se mide lo
    que se termina publicando: el orden. Dos modelos pueden errar los mismos
    puntos y ordenar la tabla muy distinto.

    Se incluye una línea de base ingenua (congelar la tabla del corte, es
    decir suponer que nadie se mueve). Si el modelo no le gana a eso, no está
    aportando nada por encima de lo que ya decía la tabla."""
    from src.scraping.fixture_scraper import zona_a_team_ids
    from scipy.stats import spearmanr

    season = season or config.CURRENT_SEASON
    matches = DC.build_match_table(season) if matches is None else matches
    zona = set(zona_a_team_ids(season))
    if not zona:
        raise RuntimeError("zona_a_team_ids() vino vacío.")

    train, test, hasta = split(matches, cutoff_round)
    if test.empty:
        raise RuntimeError(f"No hay partidos después de la fecha {cutoff_round}.")

    # Solo los partidos de la ventana que tocan a un equipo de Zona A.
    test_z = test[test["home_team_id"].isin(zona) | test["away_team_id"].isin(zona)]

    base = _zone_table(train, zona)
    real = _zone_table(matches, zona)
    teams = list(base.index)
    ti = {t: i for i, t in enumerate(teams)}

    f = DC.fit(train, xi=xi, w_xg=w_xg, ref_date=hasta)
    rng = np.random.default_rng(seed)

    lam = np.empty(len(test_z))
    mu = np.empty(len(test_z))
    for i, (_, r) in enumerate(test_z.iterrows()):
        lam[i], mu[i] = DC.match_lambdas(f, int(r["home_team_id"]), int(r["away_team_id"]))
    hg, ag = DC.sample_scores(lam, mu, f["rho"], n_sims, rng)
    hp = np.where(hg > ag, 3, np.where(hg == ag, 1, 0))
    ap = np.where(ag > hg, 3, np.where(hg == ag, 1, 0))

    n_t = len(teams)
    d_pts = np.zeros((n_sims, n_t))
    d_gf = np.zeros((n_sims, n_t))
    d_gc = np.zeros((n_sims, n_t))
    for i, (_, r) in enumerate(test_z.iterrows()):
        h, a = int(r["home_team_id"]), int(r["away_team_id"])
        if h in ti:
            j = ti[h]
            d_pts[:, j] += hp[:, i]; d_gf[:, j] += hg[:, i]; d_gc[:, j] += ag[:, i]
        if a in ti:
            j = ti[a]
            d_pts[:, j] += ap[:, i]; d_gf[:, j] += ag[:, i]; d_gc[:, j] += hg[:, i]

    b_pts = base.loc[teams, "pts"].to_numpy(float)
    b_gf = base.loc[teams, "gf"].to_numpy(float)
    b_gc = base.loc[teams, "gc"].to_numpy(float)
    sim_pts = b_pts[None, :] + d_pts
    sim_gf = b_gf[None, :] + d_gf
    sim_gc = b_gc[None, :] + d_gc
    sim_pos = _rank(sim_pts, sim_gf - sim_gc, sim_gf)

    r_pts = real.loc[teams, "pts"].to_numpy(float)
    r_gf = real.loc[teams, "gf"].to_numpy(float)
    r_gc = real.loc[teams, "gc"].to_numpy(float)
    real_pos = _rank(r_pts, r_gf - r_gc, r_gf)[0]
    base_pos = _rank(b_pts, b_gf - b_gc, b_gf)[0]

    names = {}
    for _, r in matches.iterrows():
        names[int(r["home_team_id"])] = r["home_team"]
        names[int(r["away_team_id"])] = r["away_team"]

    rows = []
    for j, t in enumerate(teams):
        p = sim_pos[:, j]
        rows.append({
            "team_id": t, "team_name": names.get(t, t),
            "pos_corte": int(base_pos[j]),
            "pos_proyectada": float(p.mean()),
            "pos_mediana": float(np.median(p)),
            "p10": float(np.percentile(p, 10)),
            "p90": float(np.percentile(p, 90)),
            "pos_real": int(real_pos[j]),
            "pts_proy": float(sim_pts[:, j].mean()),
            "pts_reales": float(r_pts[j]),
            "prob_descenso_proy": float((p >= 17).mean()),
            "prob_top8_proy": float((p <= 8).mean()),
        })
    d = pd.DataFrame(rows)
    d["error_pos"] = d["pos_mediana"] - d["pos_real"]
    d["error_base"] = d["pos_corte"] - d["pos_real"]
    d["error_pts"] = d["pts_proy"] - d["pts_reales"]
    d["dentro_80"] = (d["pos_real"] >= d["p10"]) & (d["pos_real"] <= d["p90"])
    d = d.sort_values("pos_real").reset_index(drop=True)

    rho_s = float(spearmanr(d["pos_proyectada"], d["pos_real"]).statistic)
    rho_b = float(spearmanr(d["pos_corte"], d["pos_real"]).statistic)

    desc_real = set(d.loc[d["pos_real"] >= 17, "team_id"])
    desc_proy = set(d.nlargest(2, "pos_proyectada")["team_id"])
    top8_real = set(d.loc[d["pos_real"] <= 8, "team_id"])
    top8_proy = set(d.nsmallest(8, "pos_proyectada")["team_id"])

    pj_win = float((real.loc[teams, "pj"] - base.loc[teams, "pj"]).mean())
    resumen = {
        "cutoff_round": cutoff_round, "cutoff_date": hasta,
        "n_partidos_ventana": int(len(test_z)),
        "pj_ventana_medio": pj_win,
        "mae_pos": float(d["error_pos"].abs().mean()),
        "mae_pos_base": float(d["error_base"].abs().mean()),
        "mae_pts": float(d["error_pts"].abs().mean()),
        "sesgo_pts": float(d["error_pts"].mean()),
        "spearman": rho_s, "spearman_base": rho_b,
        "cobertura_80": float(d["dentro_80"].mean()),
        "pct_dentro_1": float((d["error_pos"].abs() <= 1).mean()),
        "pct_dentro_2": float((d["error_pos"].abs() <= 2).mean()),
        "pct_dentro_3": float((d["error_pos"].abs() <= 3).mean()),
        "descenso_acertados": len(desc_real & desc_proy),
        "top8_acertados": len(top8_real & top8_proy),
    }

    if verbose:
        s = resumen
        print(f"Corte fecha {cutoff_round} ({hasta:%Y-%m-%d}) -> hoy: "
              f"{s['n_partidos_ventana']} partidos de Zona A, {n_sims} simulaciones")
        print(f"  MAE posicion   {s['mae_pos']:.2f}  (tabla congelada: {s['mae_pos_base']:.2f})")
        print(f"  Spearman       {s['spearman']:.3f}  (tabla congelada: {s['spearman_base']:.3f})")
        print(f"  MAE puntos     {s['mae_pts']:.2f}   sesgo {s['sesgo_pts']:+.2f}")
        print(f"  +/-1 puesto {s['pct_dentro_1']*100:.0f}%  +/-2 {s['pct_dentro_2']*100:.0f}%  "
              f"+/-3 {s['pct_dentro_3']*100:.0f}%   cobertura 80%: {s['cobertura_80']*100:.0f}%")
        print(f"  Descenso: {s['descenso_acertados']}/2 acertados   "
              f"Top-8: {s['top8_acertados']}/8")
    return {"tabla": d, "resumen": resumen, "fit": f}


# ─────────────────────── evaluación con origen móvil ─────────────────────────
def walk_forward(season=None, desde=12, hasta=None, xi=None, w_xg=None,
                 matches=None, verbose=True):
    """La medición más honesta de "a cuántos le acertó": para cada fecha se
    reajusta el modelo con TODO lo jugado antes y se predice solo esa fecha.

    A diferencia de `evaluate()`, que corta una vez y predice el resto (donde
    los últimos partidos se predicen con un modelo muy desactualizado), acá
    cada partido se predice con la mejor información disponible hasta el día
    anterior. Es lo que replica el uso real.

    Devuelve (resumen_por_ronda, predicciones, metricas_acumuladas).

    Leer el resultado con cuidado: el ACIERTO del favorito es mala vara en un
    problema de tres salidas con ~28% de empates. Un modelo que diga siempre
    "gana el local" acierta parecido y no sirve para nada, porque la
    proyección usa la distribución completa, no el pick. Mirar log-loss y RPS,
    que son los que ordenan bien."""
    matches = DC.build_match_table(season) if matches is None else matches
    matches = matches.sort_values("date").reset_index(drop=True)
    hasta = int(matches["round"].max()) if hasta is None else hasta

    filas, preds = [], []
    for r in range(desde, hasta + 1):
        try:
            corte = cutoff_date(matches, r)
        except RuntimeError:
            continue
        train = matches[matches["date"] < corte]
        test = matches[(matches["round"] == r) & (matches["date"] >= corte)]
        if len(train) < 60 or test.empty:
            continue
        pred, _ = predict_dc(train, test, xi=xi, w_xg=w_xg,
                             ref_date=train["date"].max())
        m = score_predictions(pred)
        m["ronda"] = r
        m["n_train"] = len(train)
        filas.append(m)
        pred = pred.copy()
        pred["ronda"] = r
        preds.append(pred)

    if not filas:
        raise RuntimeError("No hubo ninguna ronda con datos suficientes.")

    por_ronda = pd.DataFrame(filas)[
        ["ronda", "n", "n_train", "acierto", "logloss", "rps"]]
    P = pd.concat(preds, ignore_index=True)
    tot = score_predictions(P)

    if verbose:
        o = P["outcome"].to_numpy()
        base = max((o == 0).mean(), (o == 1).mean(), (o == 2).mean())
        print(f"Origen móvil: fechas {desde}-{hasta} | {len(P)} partidos, "
              f"ninguno visto al ajustar")
        print(f"  Acierto del favorito : {int(tot['acierto']*len(P))}/{len(P)} "
              f"= {tot['acierto']*100:.1f}%   (clase mayoritaria: {base*100:.1f}%)")
        print(f"  Log-loss             : {tot['logloss']:.4f}   "
              f"(azar = {np.log(3):.4f})")
        print(f"  RPS normalizado      : {tot['rps']:.4f}   "
              f"(casas de apuestas ~0.19-0.21)")
        print("  Recordá: el acierto top-1 no es la vara; mirá log-loss y RPS.")
    return por_ronda, P, tot


def outcome_bias(pred, verbose=True):
    """¿El modelo predice de más o de menos cada salida? Compara los locales /
    empates / visitantes ESPERADOS (suma de probabilidades) contra los que
    ocurrieron, y le pone un z y un p usando la desviación de la
    Poisson-binomial, que es la correcta cuando cada partido tiene su propia
    probabilidad.

    Sirve para decidir si un desajuste amerita tocar el modelo o es ruido. Con
    ~150 partidos hace falta un desvío grande para cruzar p<0.05; si algo
    aparece significativo y sostenido, lo que hay que revisar es `gamma` (la
    localía) y `rho` (la corrección τ, que es la que fabrica empates), NO
    `w_xg`."""
    p = pred[["pH", "pD", "pA"]].to_numpy()
    o = pred["outcome"].to_numpy()
    rows = []
    for i, lab in enumerate(["local", "empate", "visitante"]):
        esp = float(p[:, i].sum())
        obs = int((o == i).sum())
        sd = float(np.sqrt((p[:, i] * (1 - p[:, i])).sum()))
        z = (obs - esp) / sd if sd > 0 else 0.0
        pv = math.erfc(abs(z) / np.sqrt(2))
        rows.append({"salida": lab, "esperados": round(esp, 1), "observados": obs,
                     "z": round(z, 2), "p_valor": round(pv, 3),
                     "veredicto": "significativo" if pv < 0.05 else "dentro del ruido"})
    out = pd.DataFrame(rows)
    if verbose:
        print(out.to_string(index=False))
    return out
