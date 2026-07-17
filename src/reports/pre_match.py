"""
pre_match.py (reports)
=======================
Informe narrativo pre-partido con scouting del rival usando Claude.
"""

import os
import pandas as pd

import config
from src.reports.season import _call_claude, _save_report


def pre_match_report(next_match_key, rival_slug,
                     chaco_form_summary: dict,
                     rival_form_summary: dict,
                     rival_profile: dict,
                     rival_players_df: pd.DataFrame = None,
                     h2h_df: pd.DataFrame = None,
                     standings_df: pd.DataFrame = None,
                     chaco_scorers_df: pd.DataFrame = None,
                     rival_scorers_df: pd.DataFrame = None,
                     discipline_alert_df: pd.DataFrame = None) -> str:
    """
    Informe de scouting pre-partido.

    Parámetros
    ----------
    next_match_key   : str  — ej. '2026-03-08_vs_temperley_h'
    rival_slug       : str  — ej. 'temperley'
    chaco_form_summary : dict — de pre_match.chaco_form_summary()
    rival_form_summary : dict — de pre_match.rival_form_summary()
    rival_profile    : dict — de pre_match.rival_tactical_profile()
    rival_players_df : DataFrame — de pre_match.rival_key_players()
    h2h_df           : DataFrame — de pre_match.head_to_head() (todas las temporadas)
    standings_df     : DataFrame — de standings_scraper.load_standings()
    chaco_scorers_df, rival_scorers_df : DataFrame — de pre_match.head_to_head_goalscorers()
    discipline_alert_df : DataFrame — de pre_match.discipline_alert()
    """
    rival_info = config.RIVALS.get(rival_slug, {})
    rival_name = rival_info.get("name", rival_slug.replace("_", " ").title())

    from src.analysis.season import is_home_match
    condicion = "Local" if is_home_match(next_match_key) else "Visitante"
    from src.analysis.season import get_match_date
    fecha = get_match_date(next_match_key)

    # Posiciones en tabla
    tabla_texto = ""
    if standings_df is not None and not standings_df.empty:
        chaco_row = standings_df[standings_df["team_id"] == config.CHACO_TEAM_ID]
        rival_row = standings_df[standings_df["team_name"].str.lower() == rival_name.lower()]
        if not chaco_row.empty:
            r = chaco_row.iloc[0]
            tabla_texto += f"\nChaco: {int(r['position'])}° | {int(r['points'])} pts | GD {int(r['goal_diff'])}"
        if not rival_row.empty:
            r = rival_row.iloc[0]
            tabla_texto += f"\n{rival_name}: {int(r['position'])}° | {int(r['points'])} pts | GD {int(r['goal_diff'])}"

    # Forma Chaco
    chaco_str = (
        f"Forma Chaco ({chaco_form_summary.get('partidos','?')} partidos): "
        f"{chaco_form_summary.get('forma_str','')} | "
        f"GF {chaco_form_summary.get('goles_favor',0)} "
        f"GC {chaco_form_summary.get('goles_contra',0)} | "
        f"xG prom {chaco_form_summary.get('xg_favor','N/D')} "
        f"xGA prom {chaco_form_summary.get('xg_contra','N/D')}"
    )

    # Forma rival
    rival_str = (
        f"Forma {rival_name} ({rival_form_summary.get('partidos','?')} partidos): "
        f"{rival_form_summary.get('forma_str','')} | "
        f"GF {rival_form_summary.get('goles_favor',0)} "
        f"GC {rival_form_summary.get('goles_contra',0)} | "
        f"xG prom {rival_form_summary.get('xg_favor','N/D')} "
        f"xGA prom {rival_form_summary.get('xg_contra','N/D')}"
    )

    # Perfil táctico rival
    profile_texto = ""
    PROFILE_METRICS = ["Ball possession", "Total shots", "Accurate passes",
                       "Fouls", "Corner kicks", "Tackles"]
    for m in PROFILE_METRICS:
        val = rival_profile.get(m)
        if val is not None:
            profile_texto += f"  {m}: {val}\n"

    # Jugadores clave rival
    players_texto = ""
    if rival_players_df is not None and not rival_players_df.empty:
        players_texto = f"\nJugadores peligrosos de {rival_name}:\n"
        for _, p in rival_players_df.head(5).iterrows():
            players_texto += (
                f"  - {p.get('player_name','?')}: "
                f"rating prom {p.get('avg_rating','?')}, "
                f"{int(p.get('goals',0))} goles, "
                f"{int(p.get('assists',0))} asistencias\n"
            )

    # H2H (todas las temporadas con datos)
    h2h_texto = ""
    if h2h_df is not None and not h2h_df.empty:
        h2h_texto = f"\nHistorial completo vs {rival_name} ({len(h2h_df)} partidos):\n"
        for _, r in h2h_df.iterrows():
            h2h_texto += (
                f"  {r.get('date')} {r.get('season','')} ({r.get('venue')}): "
                f"Chaco {r.get('chaco_goals')} - {r.get('rival_goals')} {rival_name} "
                f"[{r.get('result')}]\n"
            )
        if chaco_scorers_df is not None and not chaco_scorers_df.empty:
            h2h_texto += "  Goleadores de Chaco en este historial: " + ", ".join(
                f"{r['player']} ({int(r['goals'])})" for _, r in chaco_scorers_df.head(5).iterrows()
            ) + "\n"
        if rival_scorers_df is not None and not rival_scorers_df.empty:
            h2h_texto += f"  Goleadores de {rival_name} en este historial: " + ", ".join(
                f"{r['player']} ({int(r['goals'])})" for _, r in rival_scorers_df.head(5).iterrows()
            ) + "\n"

    # Alerta de amonestados
    discipline_texto = ""
    if discipline_alert_df is not None and not discipline_alert_df.empty:
        discipline_texto = "\nRIESGO DE SUSPENSIÓN (a 1 amarilla del corte): " + ", ".join(
            f"{r['player']} ({int(r['amarillas'])}A)" for _, r in discipline_alert_df.iterrows()
        ) + "\n"

    system_prompt = (
        "Sos el analista táctico de Chaco For Ever en la Primera Nacional argentina. "
        "Preparás el scouting de los rivales antes de cada partido. "
        "Tu informe ayuda al cuerpo técnico a entender cómo juega el rival y cómo neutralizarlo. "
        "Basás tu análisis en datos estadísticos reales. "
        "Español rioplatense, tono técnico y directo."
    )

    user_prompt = f"""Escribí el informe de scouting pre-partido de Chaco For Ever vs {rival_name}.

PARTIDO:
Fecha: {fecha}  |  Condición: {condicion}
{tabla_texto}

FORMA RECIENTE:
{chaco_str}
{rival_str}

PERFIL TÁCTICO DE {rival_name.upper()} (promedios últimos partidos):
{profile_texto}

{players_texto}
{h2h_texto}
{discipline_texto}

El informe debe incluir:
1. **Contexto del partido** (importancia para ambos equipos)
2. **Cómo juega {rival_name}**: sistema, estilo, tendencias estadísticas
3. **Amenazas del rival**: jugadores a vigilar y situaciones de peligro
4. **Puntos débiles del rival**: dónde atacar
5. **Historial reciente entre los dos equipos** (si hay datos): qué patrón se repite
6. **Plan de juego recomendado para Chaco**: presión, transiciones, set pieces
7. **Alertas propias**: si hay jugadores a 1 amarilla de la suspensión, mencionarlo
8. **Predicción y claves del partido**

Extensión: 450-650 palabras. Formato Markdown con encabezados."""

    report = _call_claude(system_prompt, user_prompt, max_tokens=900)

    rival_clean = next_match_key.split("_vs_", 1)[-1] if "_vs_" in next_match_key else rival_slug
    out_dir = config.pre_outputs_dir(rival_clean, season=config.season_from_match_key(next_match_key))
    path = _save_report(report, out_dir, "informe_pre.md")
    print(f"[OK] Informe pre-partido guardado: {path}")
    return report
