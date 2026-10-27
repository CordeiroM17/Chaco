# -*- coding: utf-8 -*-
"""
Lanzador único de las publicaciones de Instagram.

    python ig.py listar                           # qué hay armado
    python ig.py nuevo pre_partido f34_rival      # crea publicaciones/pre_partido/f34_rival.py desde el modelo
    python ig.py pre_partido f33_madryn           # genera la serie en placas/
    python ig.py post_partido f32_defensores
    python ig.py historias f32_defensores
    python ig.py editable cravero_fecha_28
    python ig.py pre_partido f33_madryn --salida C:/algun/lado    # probar sin pisar placas/

Tipos: pre_partido · post_partido · historias · editable
Cada tipo tiene su plantilla en plantillas/ y su modelo en plantillas/modelos/.
La parte que cambia cada día es el archivo de publicaciones/<tipo>/<nombre>.py.

Usar el python del venv del proyecto (tiene pandas, mplsoccer, etc.).
"""
import argparse
import importlib
import importlib.util
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

# tipo -> carpeta dentro de publicaciones/
CARPETAS = {"pre_partido": "pre_partido", "post_partido": "post_partido",
            "historias": "historias", "editable": "editables"}


def _archivo(tipo, nombre):
    return RAIZ / "publicaciones" / CARPETAS[tipo] / f"{nombre}.py"


def _cargar(tipo, nombre):
    """Importa publicaciones/<tipo>/<nombre>.py como módulo."""
    arch = _archivo(tipo, nombre)
    if not arch.exists():
        disponibles = sorted(p.stem for p in arch.parent.glob("*.py") if not p.stem.startswith("_"))
        sys.exit(f"No existe {arch.relative_to(RAIZ)}.\nDisponibles en {tipo}: "
                 f"{', '.join(disponibles) or '(ninguna)'}\n"
                 f"Para crearla:  python ig.py nuevo {tipo} {nombre}")
    spec = importlib.util.spec_from_file_location(f"pub_{tipo}_{nombre}", arch)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_listar():
    for tipo, carpeta in CARPETAS.items():
        archivos = sorted(p.stem for p in (RAIZ / "publicaciones" / carpeta).glob("*.py")
                          if not p.stem.startswith("_"))
        print(f"{tipo:13s} {', '.join(archivos) if archivos else '(vacío)'}")


def cmd_nuevo(tipo, nombre):
    destino = _archivo(tipo, nombre)
    if destino.exists():
        sys.exit(f"Ya existe {destino.relative_to(RAIZ)}; no la piso.")
    modelo = RAIZ / "plantillas" / "modelos" / f"{tipo}.py"
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(modelo, destino)
    print(f"Creada {destino.relative_to(RAIZ)}\n"
          f"Completá los datos y generá con:  python ig.py {tipo} {nombre}")


def cmd_generar(tipo, nombre, salida):
    mod = _cargar(tipo, nombre)
    plantilla = importlib.import_module(f"plantillas.{tipo}")
    salida = Path(salida) if salida else None
    if tipo == "editable":
        carpeta = plantilla.generar(mod, salida=salida)
    else:
        carpeta = plantilla.generar(mod.DATOS, orden=getattr(mod, "ORDEN", None), salida=salida)
    # Caption: TEXTO (string) o texto() (función) en la publicación -> texto_publicacion.md
    texto = mod.texto() if callable(getattr(mod, "texto", None)) else getattr(mod, "TEXTO", None)
    if texto and carpeta:
        from plantillas import base as B
        B.escribir_texto(carpeta, getattr(mod, "TITULO", nombre), texto,
                         aviso=getattr(mod, "AVISO", None), notas=getattr(mod, "NOTAS", None))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", help="listar | nuevo | pre_partido | post_partido | historias | editable")
    ap.add_argument("tipo_o_nombre", nargs="?")
    ap.add_argument("nombre", nargs="?")
    ap.add_argument("--salida", help="carpeta de salida alternativa (default: placas/<serie>)")
    a = ap.parse_args()

    if a.accion == "listar":
        return cmd_listar()
    if a.accion == "nuevo":
        if a.tipo_o_nombre not in CARPETAS or not a.nombre:
            sys.exit(f"Uso: python ig.py nuevo <{'|'.join(CARPETAS)}> <nombre>")
        return cmd_nuevo(a.tipo_o_nombre, a.nombre)
    if a.accion in CARPETAS:
        if not a.tipo_o_nombre:
            sys.exit(f"Uso: python ig.py {a.accion} <nombre>   (python ig.py listar para ver las que hay)")
        return cmd_generar(a.accion, a.tipo_o_nombre, a.salida)
    sys.exit(f"Acción desconocida '{a.accion}'. Tipos: {', '.join(CARPETAS)}")


if __name__ == "__main__":
    main()
