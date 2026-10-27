# -*- coding: utf-8 -*-
"""Serie fecha por fecha de Chaco 2026: rival, resultado, puntos acumulados, posicion y DT."""
import sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[0] / "instagram" / "nucleo"))
import tabla_historica_grupo_a as T   # chdir al proyecto al importar
import pandas as pd


def serie():
    ev = T.cargar_partidos()
    ch = ev[(ev.home_team_id == T.CHACO) | (ev.away_team_id == T.CHACO)].copy()
    ch = ch.sort_values("start_time_utc")
    filas, pts = [], 0
    for _, r in ch.iterrows():
        local = r.home_team_id == T.CHACO
        gf, gc = (r.home_score, r.away_score) if local else (r.away_score, r.home_score)
        rival = r.away_team if local else r.home_team
        p = 3 if gf > gc else 1 if gf == gc else 0
        pts += p
        t = T.tabla_hasta(ev, r.date)
        pos = int(t.query("team_id == @T.CHACO").iloc[0].pos)
        filas.append(dict(n=len(filas) + 1, ronda=r["round"], fecha=r.date, rival=rival, local=local,
                          gf=int(gf), gc=int(gc), p=p, pts=pts, pos=pos))
    return pd.DataFrame(filas)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(serie().to_string(index=False))
