# -*- coding: utf-8 -*-
"""
Puesto absoluto de jugadores para escribir placas e historias.

    venv/Scripts/python.exe redes_sociales/instagram/herramientas/ranking.py "Hoyos" [metrica] [equipo]

Sin metrica: puntaje compuesto del rol. Con metrica: p. ej. key_passes_p90, rating,
aerial_duels_won_p90, goals_p90, xa_p90, interceptions_padj, duelos_aereos_pct.
Sin argumentos de metrica lista el puesto en TODAS las metricas del rol del jugador.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.analysis import scouting as SC

pool = SC.pool_liga("2026", min_minutos=300, verbose=False)
pool = SC.suavizar_p90(pool)
pool = SC.scores_compuestos(pool)

nombre = sys.argv[1]
metrica = sys.argv[2] if len(sys.argv) > 2 else None
equipo = sys.argv[3] if len(sys.argv) > 3 else None
if metrica:
    print(SC.ranking_puesto(pool, nombre, metrica, equipo))
else:
    g = SC.ranking_puesto(pool, nombre, None, equipo)
    print("COMPUESTO:", g)
    if g:
        for m in SC.metricas_del_score(g["rol"]):
            try:
                r = SC.ranking_puesto(pool, nombre, m, equipo)
                print(f"  {m:28s} {r['texto'] if r else '-'}")
            except KeyError:
                pass
