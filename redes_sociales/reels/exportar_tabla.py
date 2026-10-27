# -*- coding: utf-8 -*-
"""
Exporta la tabla del Grupo A después de cada partido de Chaco para el reel de
Remotion (remotion/public/tabla.json) y copia los escudos a remotion/public/escudos/.

    venv/Scripts/python.exe redes_sociales/reels/exportar_tabla.py

Partidos = event_clean.csv de todos los equipos (tabla_historica_grupo_a) + los
del fixture.csv que falten (p. ej. San Telmo 0-0 Defensores del 19/10, jugado
después del último partido de Chaco). La foto n es la tabla al día del partido n
de Chaco; la 34 es la tabla final. Se valida contra standings.csv.
"""
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "instagram" / "nucleo"))
import tabla_historica_grupo_a as T     # noqa: E402  (chdir al proyecto)
import datos_temporada                  # noqa: E402
import pandas as pd                     # noqa: E402

PUB = AQUI / "remotion" / "public"
ESCUDOS = AQUI.parent / "instagram" / "assets" / "escudos"

ARCHIVO = {
    36841: "ferro_carril_oeste", 93109: "deportivo_moron", 3207: "colon", 43740: "almirante_brown",
    6074: "godoy_cruz", 340432: "ciudad_de_bolivar", 112497: "los_andes", 222120: "deportivo_madryn",
    93107: "estudiantes_caseros", 264945: "san_miguel", 273657: "racing_de_c_rdoba",
    52215: "defensores_de_belgrano", 255425: "ca_mitre", 213361: "san_telmo", 36834: "all_boys",
    252726: "chaco_for_ever", 255426: "central_norte_de_salta", 112491: "acassuso",
}
CORTO = {
    36841: "Ferro", 93109: "Morón", 3207: "Colón", 43740: "Almirante Brown", 6074: "Godoy Cruz",
    340432: "Ciudad de Bolívar", 112497: "Los Andes", 222120: "Madryn", 93107: "Estudiantes",
    264945: "San Miguel", 273657: "Racing (C)", 52215: "Defensores", 255425: "Mitre",
    213361: "San Telmo", 36834: "All Boys", 252726: "Chaco For Ever", 255426: "Central Norte",
    112491: "Acassuso",
}


def partidos():
    ev = T.cargar_partidos()
    fx = pd.read_csv(Path(T.PROYECTO) / "data" / "temporadas" / "2026" / "fixture.csv")
    fx = fx[(fx.status_type == "finished") & ~fx.event_id.isin(ev.event_id)]
    fx = fx[fx.home_team_id.isin(T.GRUPO_A) | fx.away_team_id.isin(T.GRUPO_A)].copy()
    fx["status"] = "Ended"
    fx["date"] = pd.to_datetime(fx.start_time_utc, utc=True).dt.tz_convert(None).dt.date
    cols = ["event_id", "home_team_id", "away_team_id", "home_score", "away_score", "status", "date"]
    print(f"partidos agregados desde el fixture: {len(fx)}")
    return pd.concat([ev[cols], fx[cols]], ignore_index=True)


def main():
    ev = partidos()
    S = datos_temporada.serie()
    fechas = list(S.fecha)
    fechas[-1] = max(ev.date)                      # la última foto = tabla final
    fotos = [T.tabla_hasta(ev, f).set_index("team_id") for f in fechas]

    final = fotos[-1]
    of = pd.read_csv(Path(T.PROYECTO) / "data" / "temporadas" / "2026" / "standings.csv").set_index("team_id")
    assert (final.loc[of.index, "pos"] == of.position).all(), "la tabla final no coincide con la oficial"
    assert (final.loc[of.index, "pts"] == of.points).all()
    chaco_pos = [int(f.loc[T.CHACO, "pos"]) for f in fotos]
    assert chaco_pos[-1] == 10 and chaco_pos[0] == 18

    equipos = []
    for tid in T.GRUPO_A:
        equipos.append(dict(id=int(tid), nombre=CORTO[tid], escudo=f"escudos/{tid}.png",
                            pos=[int(f.loc[tid, "pos"]) for f in fotos],
                            pts=[int(f.loc[tid, "pts"]) for f in fotos]))
        shutil.copy(ESCUDOS / f"{ARCHIVO[tid]}.png", PUB / "escudos" / f"{tid}.png")

    juegos = [dict(n=int(r.n), rival=r.rival, local=bool(r.local), gf=int(r.gf), gc=int(r.gc),
                   res=int(r.p), pts=int(r.pts), pos=chaco_pos[i]) for i, r in enumerate(S.itertuples())]
    out = dict(chaco=T.CHACO, equipos=equipos, juegos=juegos)
    (PUB / "tabla.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print("posición de Chaco por partido:", chaco_pos)
    print("ok ->", PUB / "tabla.json")


if __name__ == "__main__":
    main()
