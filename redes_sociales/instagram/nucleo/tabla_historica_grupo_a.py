# -*- coding: utf-8 -*-
"""
Reconstruye la tabla del Grupo A DÍA POR DÍA y saca la posición de Chaco después
de cada jornada propia. Es la verificación detrás del carrusel
`carrusel_sale_del_descenso.py`: sirve para responder "¿desde cuándo está en zona
de descenso?" sin tener que guardar una foto de la tabla cada fecha.

    python scripts/tabla_historica_grupo_a.py

Cómo funciona: junta los `event_clean.csv` de TODAS las carpetas de rivals (cada
rival del Grupo A tiene todos sus partidos de la temporada) más los partidos
propios de Chaco, y los deduplica por `event_id`, así que un mismo partido
cargado desde los dos lados cuenta una sola vez. Después arma la tabla acumulada
hasta cada fecha de calendario.

Notas:
  - Los partidos interzonales (ej. Chaco vs Gimnasia de Jujuy, que es del Grupo B)
    SÍ suman para la tabla del grupo. Por eso no se filtran.
  - Descienden el 17 y el 18 de cada grupo (`promotion="Relegation"` en el
    standings de SofaScore).
  - Control: la tabla reconstruida al cierre de la fecha 23 coincide con la
    oficial en la posición de Chaco (16°). San Miguel queda 1 punto abajo de la
    oficial, probablemente por un partido no scrapeado; no afecta a Chaco.
"""
import io
import os
import sys
import glob
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROYECTO = Path(__file__).resolve().parents[3]
os.chdir(PROYECTO)
sys.path.insert(0, str(PROYECTO))

import pandas as pd
import config

SEASON = "2026"
CHACO = 252726
PUESTOS_DESCENSO = 17          # descienden del 17 para abajo

# ids del Grupo A según el standings de SofaScore
GRUPO_A = {
    36841: "Ferro", 93109: "Deportivo Moron", 3207: "Colon", 43740: "Almirante Brown",
    6074: "Godoy Cruz", 340432: "Ciudad de Bolivar", 112497: "Los Andes",
    222120: "Deportivo Madryn", 93107: "Estudiantes (BA)", 264945: "San Miguel",
    273657: "Racing de Cordoba", 52215: "Defensores de Belgrano", 255425: "Mitre",
    213361: "San Telmo", 36834: "All Boys", 252726: "Chaco For Ever",
    255426: "Central Norte", 112491: "Acassuso",
}


def cargar_partidos():
    """Todos los partidos terminados, deduplicados por event_id."""
    paths = glob.glob(os.path.join(config.rivals_dir(SEASON), "*", "*", "event_clean.csv"))
    paths += glob.glob(os.path.join(config.season_data_dir(SEASON), "*", "event_clean.csv"))
    frames = []
    for p in paths:
        try:
            frames.append(pd.read_csv(p))
        except Exception:
            pass
    ev = pd.concat(frames, ignore_index=True).drop_duplicates(subset="event_id")
    ev = ev[ev.status == "Ended"].copy()
    ev["date"] = pd.to_datetime(ev.start_time_utc).dt.tz_convert(None).dt.date
    return ev[ev.home_team_id.isin(GRUPO_A) | ev.away_team_id.isin(GRUPO_A)]


def tabla_hasta(ev, fecha):
    """Tabla del Grupo A con todo lo jugado hasta `fecha` inclusive."""
    d = ev[ev.date <= fecha]
    st = {t: dict(pj=0, pts=0, gf=0, gc=0) for t in GRUPO_A}
    for _, r in d.iterrows():
        for tid, gf, gc in ((r.home_team_id, r.home_score, r.away_score),
                            (r.away_team_id, r.away_score, r.home_score)):
            if tid not in st:
                continue
            s = st[tid]
            s["pj"] += 1
            s["gf"] += gf
            s["gc"] += gc
            s["pts"] += 3 if gf > gc else (1 if gf == gc else 0)
    df = pd.DataFrame([{"team_id": k, "equipo": GRUPO_A[k], **v} for k, v in st.items()])
    df["dg"] = df.gf - df.gc
    df = df.sort_values(["pts", "dg", "gf"], ascending=False).reset_index(drop=True)
    df["pos"] = df.index + 1
    return df


def main():
    ev = cargar_partidos()
    print("partidos únicos del Grupo A:", len(ev))

    fechas = sorted(ev[(ev.home_team_id == CHACO) | (ev.away_team_id == CHACO)].date.unique())
    print("\n=== POSICIÓN DE CHACO DESPUÉS DE CADA JORNADA PROPIA ===")
    print(f"{'fecha':12s} {'pos':>4s} {'pj':>3s} {'pts':>4s} {'dg':>4s}   zona")
    hist = []
    for f in fechas:
        row = tabla_hasta(ev, f).query("team_id == @CHACO").iloc[0]
        zona = "DESCENSO" if row.pos >= PUESTOS_DESCENSO else "salvado"
        hist.append((f, int(row.pos), zona))
        print(f"{str(f):12s} {int(row.pos):4d} {int(row.pj):3d} {int(row.pts):4d} "
              f"{int(row.dg):4d}   {zona}")

    # racha más larga en zona de descenso
    mejor = actual = 0
    ini = fin = ini_act = None
    for f, _, zona in hist:
        if zona == "DESCENSO":
            actual += 1
            ini_act = ini_act or f
            if actual > mejor:
                mejor, ini, fin = actual, ini_act, f
        else:
            actual, ini_act = 0, None
    print(f"\nracha más larga en zona de descenso: {mejor} jornadas ({ini} -> {fin})")

    # OJO: dos números distintos, no confundirlos. El del carrusel es el primero.
    en_racha = [h for h in hist if ini <= h[0] <= fin and h[1] == 18]
    print(f"  de esas, en el último puesto: {len(en_racha)}")
    print(f"jornadas en el último puesto en toda la temporada: "
          f"{len([h for h in hist if h[1] == 18])}")

    print("\n=== TABLA FINAL RECONSTRUIDA ===")
    print(tabla_hasta(ev, fechas[-1])[["pos", "equipo", "pj", "pts", "dg"]].to_string(index=False))


if __name__ == "__main__":
    main()
