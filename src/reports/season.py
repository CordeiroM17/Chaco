"""
season.py (reports)
====================
Informes narrativos de temporada y de partido individual.

El modelo de lenguaje se elige en config.REPORT_PROVIDER:
  - "nvidia"    -> build.nvidia.com (NIM), GRATIS, endpoint compatible con OpenAI.
  - "anthropic" -> API de Claude (paga).
"""

import os
import json
import pandas as pd

import config


def _missing_key_error():
    if config.REPORT_PROVIDER == "anthropic":
        return EnvironmentError(
            "Falta ANTHROPIC_API_KEY.\n"
            "Ejemplo: import os; os.environ['ANTHROPIC_API_KEY'] = 'tu-key'")
    return EnvironmentError(
        "Falta NVIDIA_API_KEY (gratis en build.nvidia.com).\n"
        "Ejemplo: import os; os.environ['NVIDIA_API_KEY'] = 'nvapi-...'")


def _call_nvidia(api_key, system_prompt, user_prompt, max_tokens):
    """NVIDIA NIM — endpoint compatible con OpenAI (chat/completions)."""
    import requests
    url = f"{config.NVIDIA_BASE_URL}/chat/completions"
    payload = {
        "model": config.NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.6,
        "top_p": 0.95,
        "stream": False,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    resp = requests.post(url, headers=headers, json=payload, timeout=180)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_anthropic(api_key, system_prompt, user_prompt, max_tokens):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def _call_llm(system_prompt, user_prompt, max_tokens=1500):
    """Llama al proveedor configurado (config.REPORT_PROVIDER)."""
    api_key = config.report_api_key()
    if not api_key:
        raise _missing_key_error()
    if config.REPORT_PROVIDER == "anthropic":
        return _call_anthropic(api_key, system_prompt, user_prompt, max_tokens)
    return _call_nvidia(api_key, system_prompt, user_prompt, max_tokens)


# Alias retrocompatible (pre_match.py / post_match.py importan este nombre)
_call_claude = _call_llm


def _save_report(content, folder, filename):
    path = os.path.join(folder, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ─── Informe de partido ───────────────────────────────────────────────────────

def match_report(match_summary: dict, player_stats_df: pd.DataFrame = None,
                 season=None) -> str:
    rival      = match_summary.get("opponent", "Rival")
    fecha      = match_summary.get("date", "")
    local      = match_summary.get("venue", "Local")
    gf         = match_summary.get("chaco_goals", "?")
    ga         = match_summary.get("rival_goals", "?")
    resultado  = match_summary.get("result", "?")
    xg_chaco   = match_summary.get("chaco_xg", "N/D")
    xg_rival   = match_summary.get("rival_xg", "N/D")
    shots_chaco = match_summary.get("chaco_total_shots", "N/D")
    shots_rival  = match_summary.get("rival_total_shots", "N/D")

    stats_texto = ""
    skip = {"match_key","date","opponent","venue","chaco_goals","rival_goals","result",
            "chaco_xg","rival_xg","chaco_total_shots","rival_total_shots","points","points_cumsum"}
    for key, val in match_summary.items():
        if key not in skip and val is not None:
            stats_texto += f"- {key.replace('_', ' ').title()}: {val}\n"

    player_texto = ""
    if player_stats_df is not None and not player_stats_df.empty:
        player_texto = "\nJugadores destacados:\n"
        r_col = "rating" if "rating" in player_stats_df.columns else None
        top = player_stats_df.sort_values(r_col, ascending=False).head(5) if r_col else player_stats_df.head(5)
        for _, p in top.iterrows():
            player_texto += (
                f"- {p.get('player_name', p.get('player','?'))}: "
                f"rating {p.get('rating','N/D')}, "
                f"{p.get('minutes_played', p.get('minutes','?'))} min\n"
            )

    system_prompt = (
        "Sos un analista deportivo de fútbol argentino, especializado en la Primera Nacional. "
        "Escribís informes técnicos y narrativos sobre partidos del equipo Chaco For Ever. "
        "Tu tono es profesional pero apasionado. Usás datos concretos. Escribís en español rioplatense."
    )

    user_prompt = f"""Generá un informe del siguiente partido de Chaco For Ever:

Fecha: {fecha}  |  Rival: {rival}  |  Condición: {local}
Resultado: Chaco For Ever {gf} - {ga} {rival}  ({resultado})
xG Chaco / Rival: {xg_chaco} / {xg_rival}
Tiros Chaco / Rival: {shots_chaco} / {shots_rival}
{stats_texto}
{player_texto}

El informe debe incluir:
1. Título con el marcador
2. Contexto del partido (2-3 oraciones)
3. Análisis táctico (posesión, presión, transiciones)
4. Momentos clave
5. Análisis de xG: ¿fue justo el resultado?
6. Conclusión con rating del partido (1-10)

Extensión: 400-500 palabras. Formato Markdown."""

    report = _call_claude(system_prompt, user_prompt, max_tokens=800)
    match_key = match_summary.get("match_key", "partido")
    out_dir = config.match_outputs_dir(match_key)
    path = _save_report(report, out_dir, "informe_post.md")
    print(f"[OK] Informe guardado: {path}")
    return report


# ─── Informe de jugador en partido ───────────────────────────────────────────

def player_match_report(player_stats_df: pd.DataFrame, match_summary: dict,
                         player_name: str) -> str:
    name_col = "player_name" if "player_name" in player_stats_df.columns else "player"
    row = player_stats_df[player_stats_df[name_col] == player_name]
    if row.empty:
        return f"No se encontraron datos para {player_name}."
    row = row.iloc[0]

    system_prompt = (
        "Sos un analista de scouting de fútbol argentino. "
        "Generás fichas de análisis de jugador concisas y técnicas. "
        "Escribís en español rioplatense, tono profesional."
    )

    user_prompt = f"""Analizá la actuación de este jugador de Chaco For Ever:

Jugador: {player_name}
Partido: vs {match_summary.get('opponent')} ({match_summary.get('date')})
Posición: {row.get('position','N/D')}  |  Minutos: {row.get('minutes_played', row.get('minutes','N/D'))}
Titular: {'Sí' if row.get('is_starter') else 'No'}  |  Rating: {row.get('rating','N/D')}
Goles: {row.get('goals_shotmap', row.get('goals',0))}  |  Asistencias: {row.get('assists',0)}
Tiros: {row.get('total_shots', row.get('shots',0))}  |  xG: {row.get('xg', row.get('xg_shotmap',0))}
Amarillas: {row.get('yellow_cards',0)}  |  Rojas: {row.get('red_cards',0)}

Generá una ficha con:
1. Resumen en 2-3 líneas
2. Puntos fuertes del partido
3. Áreas a mejorar
4. Nota final (1-10)

Extensión: 150-200 palabras. Formato Markdown."""

    report = _call_claude(system_prompt, user_prompt, max_tokens=400)
    match_key = match_summary.get("match_key", "partido")
    safe_name = player_name.replace(" ", "_").replace(".", "")
    out_dir = os.path.join(config.match_outputs_dir(match_key), "jugadores")
    path = _save_report(report, out_dir, f"{safe_name}.md")
    print(f"[OK] Ficha guardada: {path}")
    return report


# ─── Informe de temporada ─────────────────────────────────────────────────────

def season_report(season_stats: dict, season_df: pd.DataFrame,
                  player_season_df: pd.DataFrame, season=None) -> str:
    top_scorers  = player_season_df.nlargest(3, "goles")[["player","goles"]].to_dict("records")
    most_used    = player_season_df.nlargest(5, "minutos")[["player","minutos"]].to_dict("records")
    mejores = season_df.nlargest(3, "chaco_xg")[["date","opponent","result","chaco_goals","rival_goals"]] \
        if "chaco_xg" in season_df.columns else season_df.head(3)
    peores  = season_df.nsmallest(3, "chaco_xg")[["date","opponent","result","chaco_goals","rival_goals"]] \
        if "chaco_xg" in season_df.columns else season_df.tail(3)

    system_prompt = (
        "Sos un cronista deportivo especializado en el fútbol del interior argentino. "
        "Escribís informes de temporada con narrativa emocionante y análisis certero. "
        "Conocés la historia de Chaco For Ever y la Primera Nacional. "
        "Tu prosa es clara, periodística, en español rioplatense."
    )

    user_prompt = f"""Escribí el informe de temporada de Chaco For Ever en la Primera Nacional.

TABLA GENERAL:
- Partidos: {season_stats.get('partidos')}
- Victorias / Empates / Derrotas: {season_stats.get('victorias')} / {season_stats.get('empates')} / {season_stats.get('derrotas')}
- Puntos: {season_stats.get('puntos')}
- Goles a favor / en contra: {season_stats.get('goles_favor')} / {season_stats.get('goles_contra')}
- xG total a favor / en contra: {season_stats.get('xg_favor')} / {season_stats.get('xg_contra')}
- Rendimiento local: {season_stats.get('rendimiento_local')}
- Rendimiento visitante: {season_stats.get('rendimiento_visitante')}

GOLEADORES:
{json.dumps(top_scorers, ensure_ascii=False, indent=2)}

MÁS UTILIZADOS:
{json.dumps(most_used, ensure_ascii=False, indent=2)}

MEJORES ACTUACIONES (mayor xG):
{mejores.to_string(index=False)}

PEORES ACTUACIONES (menor xG):
{peores.to_string(index=False)}

El informe debe incluir:
1. Título y subtítulo
2. Introducción: contexto y expectativas
3. Campaña: primera vs segunda rueda
4. Análisis táctico: patrones y problemas estructurales
5. Héroes de la temporada
6. Partidos bisagra
7. Conclusión: qué necesita el club

Extensión: 700-900 palabras. Formato Markdown con encabezados."""

    report = _call_claude(system_prompt, user_prompt, max_tokens=1500)
    s = season or config.CURRENT_SEASON
    out_dir = config.season_reports_dir(s)
    path = _save_report(report, out_dir, "informe_temporada.md")
    print(f"[OK] Informe de temporada guardado: {path}")
    return report


# ─── Informe de jugador por temporada ────────────────────────────────────────

def player_season_report(player_name: str, player_season_df: pd.DataFrame,
                          all_match_stats: pd.DataFrame = None, season=None) -> str:
    row = player_season_df[player_season_df["player"] == player_name]
    if row.empty:
        return f"No hay datos de temporada para {player_name}."
    row = row.iloc[0]

    evolucion = ""
    if all_match_stats is not None:
        pm = all_match_stats[all_match_stats["player"] == player_name]
        if not pm.empty and "rating" in pm.columns:
            ratings = pm.dropna(subset=["rating"])["rating"].round(1).tolist()
            evolucion = f"Evolución de rating: {ratings}"

    system_prompt = (
        "Sos un analista de scouting para un club de fútbol argentino. "
        "Generás informes de fin de temporada por jugador, combinando datos y observaciones tácticas. "
        "Escribís en español rioplatense, tono profesional."
    )

    user_prompt = f"""Generá el informe de temporada de este jugador de Chaco For Ever:

Jugador: {player_name}
Partidos: {row.get('partidos')}  |  Titularidades: {row.get('titularidades')}  |  Minutos: {row.get('minutos')}
Rating promedio: {row.get('rating_promedio')}
Goles: {row.get('goles')}  |  Asistencias: {row.get('asistencias')}
Tiros: {row.get('tiros_totales')}  |  Al arco: {row.get('tiros_al_arco')}  |  xG: {row.get('xg_total')}
Amarillas / Rojas: {row.get('amarillas')} / {row.get('rojas')}
{evolucion}

El informe debe incluir:
1. Perfil general en la temporada
2. Fortalezas demostradas
3. Áreas de mejora
4. Conclusión: ¿renovar? ¿titular indiscutible? ¿potencial de venta?
5. Nota de temporada (1-10)

Extensión: 200-300 palabras. Formato Markdown."""

    report = _call_claude(system_prompt, user_prompt, max_tokens=600)
    safe_name = player_name.replace(" ", "_").replace(".", "")
    s = season or config.CURRENT_SEASON
    out_dir = os.path.join(config.season_reports_dir(s), "jugadores")
    path = _save_report(report, out_dir, f"{safe_name}.md")
    print(f"[OK] Informe de jugador guardado: {path}")
    return report
