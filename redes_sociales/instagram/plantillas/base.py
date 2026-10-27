# -*- coding: utf-8 -*-
"""
Base común de las plantillas de Instagram.

Acá vive lo que comparten pre_partido / post_partido / historias / editable:
  - las rutas del proyecto y el sys.path hacia nucleo/ (estilos asentados)
  - el mecanismo de PLACAS POR PREFIJO, que es lo que hace ajustables a las plantillas
  - el guardado de la serie + la hoja de contactos (_preview.png)

PLACAS POR PREFIJO
------------------
Una plantilla tiene un ORDEN: la lista de placas, en el orden en que salen.
Cada entrada es  "tipo:prefijo"  (o un nombre especial de la plantilla). El prefijo
dice de qué claves de DATOS lee la placa. Ejemplo:

    ORDEN = ["portada", "dato:d1", "ficha:rival", "dato:d2"]

    "dato:d1"  lee  d1_num, d1_lab, d1_ctx  (y d1_kicker, opcional)

Para AGREGAR una placa: escribís sus claves en DATOS y la sumás al ORDEN.
Para QUITARLA: la sacás del ORDEN. Para MOVERLA: cambiás su lugar. Sin tocar código.
Si a una placa le faltan datos se saltea y avisa cuál clave falta.

Tipos genéricos (los que sirven para cualquier plantilla):

  dato:p          p_num  p_lab  p_ctx  [p_kicker]
  dato_vs:p       p_hero p_hero_sub p_col_izq p_col_der  [p_kicker p_franja]
  ficha:p         p_titulo p_sub p_stats  [p_destacar]
  ranking:p       p_titulo p_filas  [p_sub p_destacar p_piso p_unidad]
  grafico:p       p_ruta  [p_titulo p_sub]         (png del pipeline con la marca)
  resultado:p     p_local p_gl p_visitante p_gv  [p_torneo p_detalle]
  jugadores:p     p_titulo p_jugadores  [p_sub p_kicker]
  cita:p          p_frase  [p_autor]

TEXTOS CON VARIABLES
--------------------
Cualquier texto de DATOS puede llevar {fecha}, {rival}, {rival_corto} o
{apellido_figura}: se reemplazan solos. Así un título como "Ahora,\\n{rival_corto}"
no hay que reescribirlo cada semana.
"""
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]        # .../redes_sociales/instagram
PROYECTO = RAIZ.parents[1]                         # raíz del proyecto
NUCLEO = RAIZ / "nucleo"
for _p in (str(NUCLEO), str(PROYECTO)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import marca as M          # noqa: E402  (después de armar el sys.path)
import placas as P         # noqa: E402
import temas               # noqa: E402

ASSETS = RAIZ / "assets"
ESCUDOS = ASSETS / "escudos"
PLACAS = RAIZ / "placas"                           # donde salen las series
CUENTA = "@chacoforever.stats"
COMPETENCIA = "Primera Nacional 2026"


# --------------------------------------------------------------------------
# UTILES
# --------------------------------------------------------------------------
def ruta(p):
    """str(p) si el archivo existe; None si no (escudos y gráficos son opcionales)."""
    return str(p) if p and Path(p).exists() else None


def slug(s):
    """'Defensores de Belgrano' -> 'defensores_de_belgrano' (sin tildes)."""
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower())
                if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def apellido(nombre):
    return nombre.split()[-1] if nombre else ""


_VAR = re.compile(r"\{(\w+)\}")


def formatear(x, variables):
    """Reemplaza {variable} en todos los textos de x (str, list, tuple, dict).
    Solo toca las variables conocidas: cualquier otra llave queda como está."""
    if isinstance(x, str):
        return _VAR.sub(lambda m: str(variables.get(m.group(1), m.group(0))), x)
    if isinstance(x, list):
        return [formatear(i, variables) for i in x]
    if isinstance(x, tuple):
        return tuple(formatear(i, variables) for i in x)
    if isinstance(x, dict):
        return {k: formatear(v, variables) for k, v in x.items()}
    return x


class Falta(Exception):
    """A una placa le falta una clave de DATOS."""


def _req(d, p, *claves):
    out = []
    for c in claves:
        k = f"{p}_{c}"
        if d.get(k) in (None, ""):
            raise Falta(k)
        out.append(d[k])
    return out if len(out) > 1 else out[0]


def _opc(d, p, c, defecto=None):
    v = d.get(f"{p}_{c}")
    return defecto if v in (None, "") else v


# --------------------------------------------------------------------------
# TIPOS GENERICOS DE PLACA   (cada uno: (prefijo, datos, contexto) -> imagen)
# --------------------------------------------------------------------------
def _dato(p, d, cx):
    num, lab, ctx = _req(d, p, "num", "lab", "ctx")
    return P.dato(num, lab, ctx, kicker=_opc(d, p, "kicker", "EL DATO"), nota=cx["nota"])


def _dato_vs(p, d, cx):
    hero, sub, izq, der = _req(d, p, "hero", "hero_sub", "col_izq", "col_der")
    return P.dato_vs(hero, sub, col_izq=izq, col_der=der,
                     kicker=_opc(d, p, "kicker"), franja=_opc(d, p, "franja"),
                     nota=cx["nota"])


def _ficha(p, d, cx):
    titulo, sub, stats = _req(d, p, "titulo", "sub", "stats")
    return P.ficha(titulo, sub, stats, nota=cx["nota"], destacar=_opc(d, p, "destacar"))


def _ranking(p, d, cx):
    titulo, filas = _req(d, p, "titulo", "filas")
    extra = {k: d[f"{p}_{k}"] for k in ("destacar", "piso") if f"{p}_{k}" in d}
    return P.ranking(titulo, filas, subtitulo=_opc(d, p, "sub", ""),
                     unidad=_opc(d, p, "unidad", ""), nota=cx["nota"], **extra)


def _grafico(p, d, cx):
    r = ruta(_req(d, p, "ruta"))
    if not r:
        raise Falta(f"{p}_ruta (no existe el archivo: {d.get(p + '_ruta')})")
    return P.grafico_marca(r, _opc(d, p, "titulo", ""), _opc(d, p, "sub"),
                           nota="Fuente: SofaScore")


def _resultado(p, d, cx):
    local, gl, visit, gv = _req(d, p, "local", "gl", "visitante", "gv")
    # Los escudos siguen a quién fue local ESA vez (no siempre es el Negro).
    negro_local = local == "Chaco For Ever"
    en, er = ruta(d.get("escudo_negro")), ruta(d.get("escudo_rival"))
    if not (en and er):            # o van los dos escudos o ninguno: con uno queda torcida
        en = er = None
    return P.resultado(local, gl, visit, gv,
                       torneo=_opc(d, p, "torneo", ""), detalle=_opc(d, p, "detalle", ""),
                       nota="SofaScore",
                       logo_local=en if negro_local else er,
                       logo_visitante=er if negro_local else en)


def _jugadores(p, d, cx):
    titulo, jugadores = _req(d, p, "titulo", "jugadores")
    return P.jugadores_clave(titulo, jugadores, subtitulo=_opc(d, p, "sub", ""),
                             nota=cx["nota"], kicker=_opc(d, p, "kicker", "ASI LLEGA EL RIVAL"))


def _cita(p, d, cx):
    return P.cita(_req(d, p, "frase"), autor=_opc(d, p, "autor", ""), nota=None)


TIPOS = {"dato": _dato, "dato_vs": _dato_vs, "ficha": _ficha, "ranking": _ranking,
         "grafico": _grafico, "resultado": _resultado, "jugadores": _jugadores,
         "cita": _cita}


# --------------------------------------------------------------------------
# CONSTRUCCION DE UNA SERIE
# --------------------------------------------------------------------------
def construir(orden, datos, contexto, especiales=None, tipos=None):
    """Recorre el ORDEN y devuelve [(id, imagen), ...]. `especiales` son las placas
    propias de la plantilla (nombre -> funcion(datos, contexto)); `tipos` suma o pisa
    tipos "tipo:prefijo" (las historias pisan "grafico" con su versión 9:16)."""
    especiales = especiales or {}
    tipos = {**TIPOS, **(tipos or {})}
    out = []
    for item in orden:
        try:
            if ":" in item:
                tipo, p = item.split(":", 1)
                if tipo not in tipos:
                    raise ValueError(f"tipo de placa desconocido '{tipo}' en '{item}'. "
                                     f"Opciones: {sorted(tipos)}")
                img = tipos[tipo](p, datos, contexto)
            elif item in especiales:
                img = especiales[item](datos, contexto)
            else:
                raise ValueError(f"placa desconocida '{item}'. Especiales de esta plantilla: "
                                 f"{sorted(especiales)}; o usá 'tipo:prefijo' con tipo en {sorted(tipos)}")
        except Falta as e:
            print(f"   (saltada) {item}: falta {e}")
            continue
        if img is not None:
            out.append((item, img))
    return out


# --------------------------------------------------------------------------
# TEXTO DE LA PUBLICACIÓN (caption)
# --------------------------------------------------------------------------
HASHTAGS = "#chacoforever #elnegro #primeranacional #yoconfío #ascenso"


def limpiar_texto(texto):
    """Deja el caption listo para Instagram: sin asteriscos (Instagram no los interpreta,
    el énfasis va en MAYÚSCULAS o con emojis), con los hashtags fijos al final. Avisa
    (no frena) si encuentra algo que la cuenta no publica."""
    t = texto.strip()
    if "*" in t:
        print("!! El texto tenía asteriscos: Instagram no los detecta. Se sacaron; para "
              "resaltar usá MAYÚSCULAS.")
        t = re.sub(r"\*+", "", t)
    if re.search(r"datos:\s*sofascore|no oficial", t, re.I):
        print("!! El texto lleva firma de fuente/disclaimer: la cuenta no la usa.")
    if re.search(r"amarilla", t, re.I):
        print("!! El texto habla de amarillas: la cuenta no las publica (sí una expulsión concreta).")
    if "#chacoforever" not in t:
        t += "\n\n" + HASHTAGS
    return t


def escribir_texto(salida, titulo, texto, aviso=None, notas=None):
    """Escribe <salida>/texto_publicacion.md (caption + notas) junto a las placas."""
    partes = [f"# Texto de publicación — {titulo}", ""]
    if aviso:
        partes += [f"> {aviso}", ""]
    partes += ["## Caption", "", limpiar_texto(texto), ""]
    if notas:
        partes += ["---", "", "## Notas de armado", "", notas.strip(), ""]
    destino = Path(salida) / "texto_publicacion.md"
    destino.write_text("\n".join(partes), encoding="utf-8")
    print("OK", destino)
    return destino


def guardar_serie(placas, salida, con_nombre=False):
    """Guarda la serie como 01.png, 02.png... (o 01_nombre.png) y arma _preview.png."""
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    previas = {f.name for f in salida.glob("[0-9]*.png")}
    nuevas = set()
    for i, (nombre, img) in enumerate(placas, 1):
        archivo = f"{i:02d}_{slug(nombre)}.png" if con_nombre else f"{i:02d}.png"
        M.guardar(img, salida / archivo)
        nuevas.add(archivo)
        print("OK", archivo)
    sobran = sorted(previas - nuevas)
    if sobran:                                   # no se borra nada: se avisa
        print(f"!! En la carpeta quedan placas de una corrida anterior que ya no son parte "
              f"de esta serie: {', '.join(sobran)}")
    print("OK", hoja_de_contactos(salida))
    return salida


def hoja_de_contactos(carpeta, cols=3, lado=300):
    from PIL import Image
    carpeta = Path(carpeta)
    files = sorted(carpeta.glob("[0-9]*.png"))
    if not files:
        return carpeta
    th = [Image.open(f).convert("RGB").resize((lado, lado)) for f in files]
    rows = (len(th) + cols - 1) // cols
    s = Image.new("RGB", (cols * lado + (cols + 1) * 10, rows * lado + (rows + 1) * 10), (45, 45, 45))
    for i, t in enumerate(th):
        r, c = divmod(i, cols)
        s.paste(t, (10 + c * (lado + 10), 10 + r * (lado + 10)))
    destino = carpeta / "_preview.png"
    s.save(destino)
    return destino
