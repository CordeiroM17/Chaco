"""
post_match.py (reports)
========================
Informe narrativo post-partido con análisis profundo usando Claude.
Más detallado que el informe básico de season.py: incluye timeline, xG,
análisis de cambios y jugadores clave.
"""

import os
import pandas as pd

import config
from src.reports.season import _call_claude, _save_report


def post_match_report(match_key, match_data, xg_data=None, sub_impact=None,
                      player_perf=None, season=None) -> str:
    """
    Informe post-partido completo.

    Parámetros
    ----------
    match_key : str
    match_data : dict  — resultado de post_match.load_match_data()
    xg_data   : dict  — resultado de post_match.xg_analysis()
    sub_impact : DataFrame — resultado de post_match.substitution_impact()
    player_perf : DataFrame — resultado de post_match.player_performance_table()
    season : str
    """
    df_event = match_data.get("event")
    if df_event is not None and not df_event.empty:
        ev = df_event.iloc[0]
        rival     = ev.get("away_team") if ev.get("chaco_home") else ev.get("home_team")
        fecha     = str(ev.get("start_time_utc", ""))[:10]
        condicion = "Local" if ev.get("chaco_home") else "Visitante"
        chaco_g   = ev.get("chaco_goals", "?")
        rival_g   = ev.get("rival_goals", "?")
        referee   = ev.get("referee", "N/D")
        venue     = ev.get("venue", "N/D")
    else:
        from src.analysis.season import get_opponent, get_match_date, is_home_match
        rival     = get_opponent(match_key)
        fecha     = get_match_date(match_key)
        condicion = "Local" if is_home_match(match_key) else "Visitante"
        chaco_g = rival_g = "?"
        referee = venue = "N/D"

    # xG
    xg_texto = ""
    if xg_data:
        xg_texto = (
            f"\nxG Chaco: {xg_data.get('chaco_xg')} vs "
            f"Rival: {xg_data.get('rival_xg')}\n"
            f"Veredicto xG: {xg_data.get('verdict')}"
        )

    # Impacto de cambios
    subs_texto = ""
    if sub_impact is not None and not sub_impact.empty:
        subs_texto = "\nFases por cambios (xG por período):\n"
        for _, r in sub_impact.iterrows():
            subs_texto += (
                f"  {r.get('phase')}: {r.get('shots')} tiros, "
                f"xG={r.get('xg'):.3f}"
            )
            if r.get("player_in") and r.get("player_in") != "—":
                subs_texto += f" | Cambio: +{r.get('player_in')} -{r.get('player_out')}"
            subs_texto += "\n"

    # Top jugadores
    players_texto = ""
    if player_perf is not None and not player_perf.empty:
        players_texto = "\nMejores jugadores:\n"
        top = player_perf.head(5)
        for _, p in top.iterrows():
            players_texto += (
                f"  - {p.get('player_name','?')}: "
                f"rating {p.get('rating','N/D')}, "
                f"{p.get('minutes_played','?')} min, "
                f"xG {p.get('xg_shotmap', p.get('xg', 0)):.2f}\n"
            )

    system_prompt = (
        "Sos un analista deportivo de Chaco For Ever especializado en la Primera Nacional argentina. "
        "Escribís crónicas de partido profundas y técnicas, con datos precisos y narrativa emocionante. "
        "Español rioplatense. Tono profesional-apasionado."
    )

    user_prompt = f"""Escribí el informe post-partido completo de Chaco For Ever.

DATOS DEL PARTIDO:
Fecha: {fecha}
Rival: {rival}
Condición: {condicion}
Resultado: Chaco For Ever {chaco_g} - {rival_g} {rival}
Estadio: {venue}  |  Árbitro: {referee}
{xg_texto}
{subs_texto}
{players_texto}

El informe debe incluir:
1. **Título** con el marcador
2. **Contexto** del partido (posición en tabla, importancia)
3. **Análisis táctico** detallado (primeros 45' vs. segundo tiempo)
4. **Momentos determinantes** (goles, tarjetas, cambios decisivos)
5. **Análisis de xG**: ¿el resultado fue justo?
6. **Impacto de los cambios**: ¿mejoraron el rendimiento?
7. **Figura del partido** (de Chaco)
8. **Conclusión** con nota del partido (1-10) y proyección al próximo

Extensión: 500-650 palabras. Formato Markdown con encabezados."""

    report = _call_claude(system_prompt, user_prompt, max_tokens=1000)

    out_dir = config.match_outputs_dir(match_key)
    path = _save_report(report, out_dir, "informe_post.md")
    print(f"[OK] Informe post-partido guardado: {path}")
    return report
