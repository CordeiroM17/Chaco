"""Análisis a nivel liga/grupo (Grupo A 2026) reutilizando la maquinaria de
temporada. Dos usos:

1. Generar el informe estándar de CUALQUIER equipo del grupo (mismo set de
   gráficos que el de Chaco), para vender el servicio a los clubes.
2. Estadísticas globales del grupo: mejor 11 por fecha con suplentes, rankings
   ofensivo/defensivo por equipo, tendencias de origen de los remates, etc.

Todo se apoya en que las funciones de `src/analysis/season.py` trabajan por
`(match_keys, base_dir)` y resuelven "el equipo analizado" con el sufijo _h/_a
del match_key. Así, apuntando el base_dir a la carpeta de cada rival, sale el
mismo análisis sin nada hardcodeado de Chaco.
"""
import os
import math
import pandas as pd
import numpy as np

import config
from src.analysis import season as S
from src.analysis import pre_match as PM
from src.analysis.season import is_home_match

# CSVs mínimos para que un partido sea usable en el análisis de temporada.
CORE_CSVS = ("shotmap_clean.csv", "lineups_clean.csv",
             "incidents_clean.csv", "statistics_clean.csv")


# ─────────────────────────── contexto por equipo ────────────────────────────
def _match_has_core(match_dir):
    return all(os.path.exists(os.path.join(match_dir, c)) for c in CORE_CSVS)


def team_name(slug, season="2026"):
    return config.group_a_teams(season).get(slug, {}).get(
        "name", config.RIVALS.get(slug, {}).get("name", slug.replace("_", " ").title()))


def team_context(slug, season="2026"):
    """Devuelve (base_dir, match_keys_con_datos, nombre) del equipo.
    Chaco usa su propia carpeta de temporada; los rivales, rivals/{slug}/."""
    if slug in ("chaco_for_ever", "chaco-for-ever", "chaco"):
        base_dir = config.season_data_dir(season)
        all_mks = list(S.load_matches(season))
    else:
        base_dir = config.rival_data_dir(slug, season)
        all_mks = PM.rival_match_keys(slug, season) if os.path.isdir(base_dir) else []
    mks = [mk for mk in all_mks if _match_has_core(os.path.join(base_dir, mk))]
    return base_dir, mks, team_name(slug, season)


# ─────────────────── generación del pack de gráficos por equipo ──────────────
def generate_team_graphics(slug, season="2026", plots_dir=None, verbose=True):
    """Replica el set estándar de gráficos de temporada para `slug`, guardándolos
    en `plots_dir`. Devuelve un dict con las tablas y métricas clave + la lista
    de archivos generados (cada gráfico va envuelto en try/except: si falta un
    dato, se saltea sin romper el resto)."""
    import matplotlib
    matplotlib.use("Agg")
    from src.visualization.season import (
        plot_season_points, plot_xg_season, plot_top_players, plot_shotmap_4grid,
        save_fig, plot_shared_minutes_network, plot_recent_form,
        plot_home_away_panel, plot_discipline, plot_load_calendar,
        plot_assists_network, plot_threat_by_situation, plot_xg_by_score_state,
        plot_final_third_touches, plot_markov_transitions, plot_eigen_centrality,
        plot_shot_entropy, plot_defensive_hazard,
    )

    base_dir, mks, name = team_context(slug, season)
    if plots_dir is None:
        plots_dir = os.path.join(config.team_report_dir(slug, season), "graficos")
    os.makedirs(plots_dir, exist_ok=True)
    made = []

    def _p(fname):
        return os.path.join(plots_dir, fname)

    def _try(label, fn):
        try:
            fn()
            if verbose:
                print(f"  ✔ {label}")
        except Exception as e:
            if verbose:
                print(f"  ✖ {label}: {type(e).__name__}: {e}")

    if not mks:
        raise RuntimeError(f"Sin partidos con datos para '{slug}' en {base_dir}")

    # Tablas base
    season_df = S.build_season_table(mks, base_dir)
    stats = S.season_stats(season_df)
    player_df = S.season_player_stats(mks, base_dir)

    # 1) puntos acumulados
    def _f():
        save_fig(plot_season_points(season_df, team_label=name), _p("puntos_acumulados.png")); made.append("puntos_acumulados.png")
    _try("puntos_acumulados", _f)

    # 2) xG temporada
    def _f():
        fig = plot_xg_season(season_df, team_label=name)
        if fig: save_fig(fig, _p("xg_temporada.png")); made.append("xg_temporada.png")
    _try("xg_temporada", _f)

    # 3) top minutos
    def _f():
        if not player_df.empty:
            save_fig(plot_top_players(player_df, metric="minutos", top_n=15), _p("top_minutos.png")); made.append("top_minutos.png")
    _try("top_minutos", _f)

    # 4) top rating (min 600')
    def _f():
        rdf = player_df[player_df["minutos"] >= 600].dropna(subset=["rating_promedio"])
        if not rdf.empty:
            xmin = max(4.0, float(rdf["rating_promedio"].min()) - 0.3)
            save_fig(plot_top_players(rdf, metric="rating_promedio", top_n=15, xmin=xmin), _p("top_rating.png")); made.append("top_rating.png")
    _try("top_rating", _f)

    # 5) shotmap propio
    def _f():
        shots = []
        for mk in mks:
            sp = os.path.join(base_dir, mk, "shotmap_clean.csv")
            if os.path.exists(sp):
                d = pd.read_csv(sp); shots.append(d[d["isHome"] == is_home_match(mk)])
        if shots:
            df = pd.concat(shots, ignore_index=True)
            fig = plot_shotmap_4grid(df, team_label=name, title=f"Distribución de Tiros — {name} {season}")
            save_fig(fig, _p("shotmap_temporada.png")); made.append("shotmap_temporada.png")
    _try("shotmap_temporada", _f)

    # 6) red de minutos compartidos (+ 12) núcleo táctico eigen)
    nodes = edges = None
    def _f():
        nonlocal nodes, edges
        nodes, edges = S.shared_minutes_network(mks, base_dir, min_minutes=270)
        if not nodes.empty:
            plot_shared_minutes_network(nodes, edges, season=season, min_edge_minutes=180, top_edges=22, title=f"Red de Minutos Compartidos – {name}", save_path=_p("red_minutos_compartidos.png")); made.append("red_minutos_compartidos.png")
    _try("red_minutos_compartidos", _f)

    # 7) tiros concedidos
    def _f():
        conc = []
        for mk in mks:
            sp = os.path.join(base_dir, mk, "shotmap_clean.csv")
            if os.path.exists(sp):
                d = pd.read_csv(sp); conc.append(d[d["isHome"] != is_home_match(mk)])
        if conc:
            df = pd.concat(conc, ignore_index=True)
            plot_shotmap_4grid(df, team_label="Tiros Concedidos", title=f"Tiros Concedidos — {name} {season}", save_path=_p("tiros_concedidos_temporada.png")); made.append("tiros_concedidos_temporada.png")
    _try("tiros_concedidos_temporada", _f)

    # 8) forma reciente
    def _f():
        plot_recent_form(season_df, window=5, season=season, title=f"Forma Reciente – {name}", save_path=_p("forma_reciente.png")); made.append("forma_reciente.png")
    _try("forma_reciente", _f)

    # 9) local vs visitante
    def _f():
        plot_home_away_panel(season_df, season=season, title=f"Local vs Visitante – {name}", save_path=_p("local_vs_visitante.png")); made.append("local_vs_visitante.png")
    _try("local_vs_visitante", _f)

    # 10) disciplina
    def _f():
        plot_discipline(player_df, season=season, suspension_at=5, title=f"Disciplina Acumulada – {name}", save_path=_p("disciplina.png")); made.append("disciplina.png")
    _try("disciplina", _f)

    # 11) calendario de carga
    def _f():
        mat, meta = S.load_calendar(mks, base_dir, top_n=16)
        plot_load_calendar(mat, meta, season=season, title=f"Calendario de Carga – {name}", save_path=_p("calendario_carga.png")); made.append("calendario_carga.png")
    _try("calendario_carga", _f)

    # 12) red de asistencias
    def _f():
        an, ae = S.assists_network(mks, base_dir)
        if not an.empty:
            plot_assists_network(an, ae, season=season, title=f"Red de Asistencias – {name}", save_path=_p("red_asistencias.png")); made.append("red_asistencias.png")
    _try("red_asistencias", _f)

    # 13) amenaza por tipo de jugada
    def _f():
        th = S.threat_by_situation(mks, base_dir)
        if not th.empty:
            plot_threat_by_situation(th, season=season, title=f"Amenaza por Tipo de Jugada – {name}", save_path=_p("amenaza_por_jugada.png")); made.append("amenaza_por_jugada.png")
    _try("amenaza_por_jugada", _f)

    # 14) xG por estado del marcador
    def _f():
        x = S.xg_by_score_state(mks, base_dir)
        if not x.empty:
            plot_xg_by_score_state(x, season=season, title=f"xG según Estado del Marcador – {name}", save_path=_p("xg_por_estado_marcador.png")); made.append("xg_por_estado_marcador.png")
    _try("xg_por_estado_marcador", _f)

    # 15) toques en último tercio
    def _f():
        ft = S.final_third_touches(mks, base_dir, top_n=14)
        if not ft.empty:
            plot_final_third_touches(ft, season=season, title=f"Participación en Último Tercio – {name}", save_path=_p("toques_ultimo_tercio.png")); made.append("toques_ultimo_tercio.png")
    _try("toques_ultimo_tercio", _f)

    # 16) markov del marcador
    def _f():
        mm, mt = S.markov_game_state(mks, base_dir)
        plot_markov_transitions(mm, mt, season=season, title=f"Cadena de Markov del Marcador – {name}", save_path=_p("markov_marcador.png")); made.append("markov_marcador.png")
    _try("markov_marcador", _f)

    # 17) núcleo táctico (eigen)
    def _f():
        if nodes is not None and not nodes.empty:
            en = S.eigenvector_centrality_network(nodes, edges, min_minutes=270)
            plot_eigen_centrality(en, season=season, title=f"Núcleo Táctico del Plantel – {name}", save_path=_p("nucleo_tactico.png")); made.append("nucleo_tactico.png")
    _try("nucleo_tactico", _f)

    # 18) entropía de tiros
    entropy = {}
    def _f():
        nonlocal entropy
        entropy = S.shot_entropy(mks, base_dir)
        if entropy.get("n_shots"):
            plot_shot_entropy(entropy, season=season, team_label=name, save_path=_p("entropia_tiros.png")); made.append("entropia_tiros.png")
    _try("entropia_tiros", _f)

    # 19) riesgo defensivo (Cox) — opcional
    def _f():
        surv = S.build_defensive_survival_dataset(mks, base_dir)
        if surv["event"].sum() >= 2 and surv["defensive_fatigue"].std() > 0:
            cph = S.fit_defensive_hazard_model(surv)
            plot_defensive_hazard(cph, season=season, title=f"Riesgo de Colapso Defensivo – {name}", save_path=_p("riesgo_defensivo_cox.png")); made.append("riesgo_defensivo_cox.png")
    _try("riesgo_defensivo_cox", _f)

    return {
        "slug": slug, "name": name, "season": season, "base_dir": base_dir,
        "n_matches": len(mks), "match_keys": mks, "plots_dir": plots_dir,
        "season_df": season_df, "stats": stats, "player_df": player_df,
        "entropy": entropy, "graphics": made,
    }


# ─────────────────────────── estadísticas globales ──────────────────────────
def team_summary_table(season="2026"):
    """Una fila por equipo del grupo: PJ, V/E/D, pts, GF/GC, xG a favor/contra
    y promedios por partido. Base para rankings ofensivo y defensivo."""
    rows = []
    for slug in config.group_a_teams(season):
        base_dir, mks, name = team_context(slug, season)
        if not mks:
            continue
        sdf = S.build_season_table(mks, base_dir)
        st = S.season_stats(sdf)
        pj = st.get("partidos", len(sdf)) or len(sdf)
        rows.append({
            "slug": slug, "equipo": name, "pj": pj,
            "V": st.get("victorias"), "E": st.get("empates"), "D": st.get("derrotas"),
            "pts": st.get("puntos"),
            "gf": st.get("goles_favor"), "gc": st.get("goles_contra"),
            "xg_favor": st.get("xg_favor"), "xg_contra": st.get("xg_contra"),
            "gf_pp": round((st.get("goles_favor") or 0) / pj, 2) if pj else None,
            "gc_pp": round((st.get("goles_contra") or 0) / pj, 2) if pj else None,
            "xgf_pp": round((st.get("xg_favor") or 0) / pj, 2) if pj else None,
            "xgc_pp": round((st.get("xg_contra") or 0) / pj, 2) if pj else None,
        })
    df = pd.DataFrame(rows)
    return df.sort_values("pts", ascending=False).reset_index(drop=True) if not df.empty else df


def round_matches(round_num, season="2026"):
    """Partidos ÚNICOS de una fecha/ronda en todo el grupo (deduplicados por
    event_id, ya que cada partido aparece en la carpeta de los dos equipos).
    Devuelve DataFrame con datos del partido + la ruta a una carpeta con datos."""
    seen = {}
    for slug in config.group_a_teams(season):
        base_dir = (config.season_data_dir(season)
                    if slug.startswith("chaco") else config.rival_data_dir(slug, season))
        if not os.path.isdir(base_dir):
            continue
        for mk in os.listdir(base_dir):
            ev = os.path.join(base_dir, mk, "event_clean.csv")
            if not os.path.exists(ev):
                continue
            try:
                e = pd.read_csv(ev).iloc[0]
            except Exception:
                continue
            if pd.isna(e.get("round")) or int(float(e["round"])) != int(round_num):
                continue
            eid = e.get("event_id")
            if eid in seen:
                continue
            seen[eid] = {
                "event_id": eid, "match_dir": os.path.join(base_dir, mk),
                "home_team": e.get("home_team"), "away_team": e.get("away_team"),
                "home_score": e.get("home_score"), "away_score": e.get("away_score"),
                "date": e.get("start_time_utc"),
            }
    return pd.DataFrame(seen.values())


_POS_BUCKET = {"G": "G", "D": "D", "M": "M", "F": "F"}


def round_player_ratings(round_num, season="2026"):
    """Todos los jugadores (ambos equipos) de la fecha con su rating, posición,
    equipo y si fue titular o suplente."""
    rm = round_matches(round_num, season)
    rows = []
    for _, m in rm.iterrows():
        lp = os.path.join(m["match_dir"], "lineups_clean.csv")
        if not os.path.exists(lp):
            continue
        lin = pd.read_csv(lp)
        for _, p in lin.iterrows():
            team = m["home_team"] if p.get("team_side") == "home" else m["away_team"]
            is_sub = not bool(p.get("is_starter"))
            rows.append({
                "player": p.get("player_name"), "team": team,
                "position": _POS_BUCKET.get(str(p.get("position")), None),
                "rating": p.get("rating"), "is_sub": is_sub,
                "minutes": p.get("minutes_played"),
                "event_id": m["event_id"],
            })
    df = pd.DataFrame(rows)
    return df.dropna(subset=["rating", "position"]) if not df.empty else df


def best_xi_round(round_num, season="2026", formation=(4, 3, 3), n_bench=10):
    """Mejor 11 de la fecha por rating SofaScore, respetando una formación
    (def, med, del) + 1 arquero, usando TITULARES. Además un banco ideal con los
    mejores SUPLENTES que ingresaron. Devuelve dict con DataFrames."""
    df = round_player_ratings(round_num, season)
    if df.empty:
        return {"xi": df, "bench": df, "formation": formation}
    starters = df[~df["is_sub"]].sort_values("rating", ascending=False)
    need = {"G": 1, "D": formation[0], "M": formation[1], "F": formation[2]}
    xi = []
    for pos, k in need.items():
        xi.append(starters[starters["position"] == pos].head(k))
    xi = pd.concat(xi, ignore_index=True) if xi else df.head(0)
    bench = (df[df["is_sub"]].sort_values("rating", ascending=False)
             .head(n_bench).reset_index(drop=True))
    return {"xi": xi.reset_index(drop=True), "bench": bench, "formation": formation}


def generate_round_best_xi(round_num, season="2026", formation=(4, 3, 3),
                           out_dir=None, verbose=False):
    """Genera el gráfico del mejor 11 (+ banco de 10) de una fecha en su carpeta
    `.../liga/fechas/fecha_NN/`. Devuelve la ruta del png o None si la fecha no
    tiene datos todavía."""
    from src.visualization.liga import plot_best_xi_pitch
    out_dir = out_dir or config.group_round_dir(round_num, season)
    os.makedirs(out_dir, exist_ok=True)
    bx = best_xi_round(round_num, season, formation=formation)
    if bx["xi"].empty:
        if verbose:
            print(f"  fecha {round_num:>2}: sin datos aún")
        return None
    # guardar también las tablas de esa fecha
    bx["xi"].to_csv(os.path.join(out_dir, "mejor_11.csv"), index=False)
    bx["bench"].to_csv(os.path.join(out_dir, "banco.csv"), index=False)
    p = os.path.join(out_dir, "mejor_11.png")
    plot_best_xi_pitch(bx["xi"], bx["bench"], formation=formation,
                       round_num=round_num, season=season, save_path=p)
    if verbose:
        print(f"  fecha {round_num:>2}: ✔ ({len(bx['xi'])} titulares, {len(bx['bench'])} suplentes)")
    return p


def generate_all_rounds(season="2026", rounds=range(1, 37), verbose=True):
    """Crea las carpetas de las fechas 1..36 y genera el mejor 11 en cada una que
    tenga datos. Las fechas aún no jugadas quedan con la carpeta creada, vacías."""
    done = []
    for r in rounds:
        os.makedirs(config.group_round_dir(r, season), exist_ok=True)  # crea fecha_NN aunque no haya datos
        p = generate_round_best_xi(r, season, verbose=verbose)
        if p:
            done.append(r)
    if verbose:
        print(f"\nFechas con mejor 11 generado: {done}")
    return done


def _shot_zone(x, y):
    """Clasifica un remate por origen usando coords Opta del shotmap (x = distancia
    al arco: 0=línea de gol; y = eje lateral 0..100, 50=centro). Zonas: 'area_centro',
    'area_lateral', 'fuera_centro', 'fuera_lateral'."""
    try:
        x = float(x); y = float(y)
    except Exception:
        return None
    in_box = x <= 17  # ~16.5m: dentro del área (x es distancia al arco)
    central = 35 <= y <= 65  # corredor central (~30% del ancho)
    zona = "area" if in_box else "fuera"
    lado = "centro" if central else "lateral"
    return f"{zona}_{lado}"


def shot_origin_distribution(season="2026", by_team=False, round_num=None):
    """Distribución de remates por zona de origen (para ver cuánto se ataca por
    el centro). Si round_num, solo esa fecha; si by_team, desglosa por equipo."""
    rows = []
    if round_num is not None:
        rm = round_matches(round_num, season)
        dirs = [(r["match_dir"], None) for _, r in rm.iterrows()]
        # en modo fecha tomamos TODOS los remates del partido (los dos equipos)
        for d, _ in dirs:
            sp = os.path.join(d, "shotmap_clean.csv")
            if os.path.exists(sp):
                for _, s in pd.read_csv(sp).iterrows():
                    z = _shot_zone(s.get("coord_x"), s.get("coord_y"))
                    if z:
                        rows.append({"equipo": "LIGA", "zona": z})
    else:
        for slug in config.group_a_teams(season):
            base_dir, mks, name = team_context(slug, season)
            for mk in mks:
                sp = os.path.join(base_dir, mk, "shotmap_clean.csv")
                if not os.path.exists(sp):
                    continue
                d = pd.read_csv(sp)
                own = d[d["isHome"] == is_home_match(mk)]
                for _, s in own.iterrows():
                    z = _shot_zone(s.get("coord_x"), s.get("coord_y"))
                    if z:
                        rows.append({"equipo": name if by_team else "LIGA", "zona": z})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    grp = df.groupby(["equipo", "zona"]).size().reset_index(name="n")
    tot = grp.groupby("equipo")["n"].transform("sum")
    grp["pct"] = (grp["n"] / tot * 100).round(1)
    return grp
