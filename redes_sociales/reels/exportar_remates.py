# -*- coding: utf-8 -*-
"""
Remates de Chaco For Ever 2026 (a favor) para el reel 3D de ataque.

    venv/Scripts/python.exe redes_sociales/reels/exportar_remates.py [--resumen]

Lee data/temporadas/2026/partidos/*/raw/shotmap.json (SofaScore) y escribe
remotion/src/ataque/shots.ts con el mismo formato que el reel de defensa (Mandar2):
  [fecha, rival, minuto, resultado g|s|b|m|p, cabeza, xG, origenX, origenY, finX, finY, finZ, desdeAgosto]
Metros: x lateral (0 = centro del arco), y distancia a la línea de gol, z altura.
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PROY = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import datos_temporada        # noqa: E402  (serie oficial de partidos)

PART = PROY / "data" / "temporadas" / "2026" / "partidos"
AGOSTO = "2026-08-02"
TIPO = {"goal": "g", "save": "s", "block": "b", "miss": "m", "post": "p"}
CORTO = {
    "Club Ferro Carril Oeste": "FERRO", "Club Atletico Colón": "COLÓN", "Gimnasia Y Esgrima De Jujuy": "GIMNASIA (J)",
    "Gimnasia Jujuy": "GIMNASIA (J)", "Estudiantes de Buenos Aires": "ESTUDIANTES (BA)", "CA Mitre": "MITRE",
    "Central Norte de Salta": "CENTRAL NORTE", "Deportivo Morón": "MORÓN", "Deportivo Madryn": "MADRYN",
    "Defensores de Belgrano": "DEFENSORES", "Ciudad de Bolivar": "CIUDAD DE BOLÍVAR", "Almirante Brown": "ALTE. BROWN",
    "Racing de Córdoba": "RACING (C)",
}


def metros(sh):
    pc, gm = sh["playerCoordinates"], sh.get("goalMouthCoordinates") or {}
    ox, oy = round((pc["y"] - 50) * 0.68, 2), round(pc["x"] * 1.05, 2)
    t = TIPO[sh["shotType"]]
    if t == "b":                                   # bloqueado: queda cerca de donde salió
        b = sh.get("blockCoordinates") or pc
        return ox, oy, round((b["y"] - 50) * 0.68, 2), round(b["x"] * 1.05, 2), 0.7
    fx = round((gm.get("y", 50) - 50) * 0.7625, 2)
    fz = round(gm.get("z", 10) * 0.0678, 2)
    fy = 0.4 if t == "s" else 0.0                  # atajada: el arquero la para sobre la línea
    return ox, oy, fx, fy, fz


def main():
    S = datos_temporada.serie()
    filas, partidos, sin_shotmap = [], [], []
    for r in S.itertuples():
        fecha = str(r.fecha)
        carpeta = next((p for p in PART.iterdir() if p.name.startswith(fecha[:10])), None)
        rival = CORTO.get(r.rival, r.rival.upper())
        partidos.append([fecha, rival, int(r.gf)])
        f = carpeta / "raw" / "shotmap.json" if carpeta else None
        if not f or not f.exists():
            sin_shotmap.append(f"{fecha} {rival} ({r.gf}-{r.gc})")
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        shots = d["shotmap"] if isinstance(d, dict) else d
        if not shots:
            sin_shotmap.append(f"{fecha} {rival} ({r.gf}-{r.gc})")
            continue
        for sh in sorted(shots, key=lambda s: s.get("timeSeconds", s["time"] * 60)):
            if sh["isHome"] != bool(r.local) or sh.get("goalType") == "own":
                continue
            ox, oy, fx, fy, fz = metros(sh)
            filas.append([fecha, rival, int(sh["time"]), TIPO[sh["shotType"]], int(sh.get("bodyPart") == "head"),
                          round(sh.get("xg", 0.0), 3), ox, oy, fx, fy, fz, int(fecha >= AGOSTO),
                          sh.get("situation", "")])
    return filas, partidos, sin_shotmap


def resumen(filas, partidos, sin):
    import statistics as st
    print("sin shotmap:", sin)
    def bloque(nombre, F, P):
        g = [f for f in F if f[3] == "g"]
        caja = lambda f: f[7] <= 16.5 and abs(f[6]) <= 20.16           # noqa: E731
        fuera = [f for f in F if not caja(f)]
        dentro = [f for f in F if caja(f)]
        arco = [f for f in F if f[3] in "gs"]
        print(f"\n== {nombre}: {len(P)} partidos, goles reales {sum(p[2] for p in P)}")
        print(f"remates {len(F)} ({len(F)/len(P):.1f}/pj)  goles con remate {len(g)}  xG {sum(f[5] for f in F):.1f}")
        print(f"al arco {len(arco)} ({len(arco)/len(F):.0%})  bloqueados {sum(f[3]=='b' for f in F)}  palos {sum(f[3]=='p' for f in F)}")
        print(f"desde afuera {len(fuera)} ({len(fuera)/len(F):.0%}) -> goles {sum(f[3]=='g' for f in fuera)}  xG {sum(f[5] for f in fuera):.2f}")
        print(f"desde adentro {len(dentro)} -> goles {sum(f[3]=='g' for f in dentro)}  xG {sum(f[5] for f in dentro):.2f}")
        print(f"cabeza {sum(f[4] for f in F)} -> goles {sum(f[4] and f[3]=='g' for f in F)}")
        print("goles por situación:", {s: sum(1 for f in g if f[12] == s) for s in set(f[12] for f in g)})
        print(f"distancia media {st.mean(f[7] for f in F):.1f} m")
    bloque("TODO", filas, partidos)
    bloque("ANTES 2/8", [f for f in filas if not f[11]], [p for p in partidos if p[0] < AGOSTO])
    bloque("DESDE 2/8", [f for f in filas if f[11]], [p for p in partidos if p[0] >= AGOSTO])


def escribir(filas, partidos):
    out = AQUI / "remotion" / "src" / "ataque" / "shots.ts"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = [f[:12] for f in filas]
    out.write_text(
        "// Generado por redes_sociales/reels/exportar_remates.py desde data/temporadas/2026/partidos/*/raw/shotmap.json\n"
        "// Remates de Chaco For Ever (a favor). Metros: x lateral (0 = centro del arco), y distancia a la línea, z altura.\n"
        "// [fecha, rival, minuto, resultado g|s|b|m|p, cabeza, xG, origenX, origenY, finX, finY, finZ, desdeAgosto]\n"
        "export type ShotRow = [string, string, number, string, number, number, number, number, number, number, number, number];\n"
        f"export const SHOTS: ShotRow[] = {json.dumps(rows, ensure_ascii=False)};\n\n"
        "// [fecha, rival, goles a favor] (todos los partidos, tengan o no shotmap)\n"
        f"export const MATCHES: [string, string, number][] = {json.dumps(partidos, ensure_ascii=False)};\n",
        encoding="utf-8")
    print("ok ->", out)


if __name__ == "__main__":
    F, P, sin = main()
    if "--resumen" in sys.argv:
        resumen(F, P, sin)
    else:
        escribir(F, P)
