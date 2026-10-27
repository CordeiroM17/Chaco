# redes_sociales / instagram

Workspace **separado** para la cuenta de Instagram de estadísticas de Chaco For Ever.
Es para los fanáticos, no tiene que ver con los informes técnicos del pipeline. Acá se
diseña, se define el estándar de color y se generan las placas listas para publicar.

## Cómo se trabaja

Hay **cuatro tipos de publicación**. Cada una tiene una *plantilla* (la lógica, que no se
toca) y un archivo de *publicación* (los datos del día, que es lo único que editás).

| Tipo | Para qué | Plantilla |
|------|----------|-----------|
| `pre_partido` | Carrusel de previa (tema hueso) | `plantillas/pre_partido.py` |
| `post_partido` | Carrusel de análisis del partido (tema oscuro) | `plantillas/post_partido.py` |
| `historias` | Historias 9:16 del partido | `plantillas/historias.py` |
| `editable` | Libres, a mano, sobre un estilo asentado (Cravero, permanencia...) | `plantillas/editable.py` |

Todo se maneja con un solo comando (usar el python del `venv` del proyecto):

```bash
cd redes_sociales/instagram
python ig.py listar                          # qué publicaciones hay armadas
python ig.py nuevo pre_partido f34_rival     # crea publicaciones/pre_partido/f34_rival.py desde el modelo
python ig.py pre_partido f34_rival           # genera las placas en placas/previa_fecha_34_rival/
python ig.py post_partido f32_defensores
python ig.py historias f32_defensores
python ig.py editable cravero
python ig.py pre_partido f33_madryn --salida C:/tmp/prueba    # probar sin pisar placas/
```

### Ajustar una publicación día a día

Abrís el archivo en `publicaciones/<tipo>/` y tocás:

- **`DATOS`**: los números y textos. Los textos aceptan `{fecha}`, `{rival}`, `{rival_corto}`
  y `{apellido_figura}`, que se reemplazan solos.
- **`ORDEN`**: la lista de placas, en el orden en que salen. Para **sacar** una placa la
  borrás de la lista; para **moverla**, la cambiás de lugar; para **sumar** una, escribís
  sus claves en `DATOS` y la agregás. Cada entrada es `"tipo:prefijo"` y el prefijo dice de
  qué claves lee (`"dato:d2"` lee `d2_num`, `d2_lab`, `d2_ctx`, `d2_kicker`). Los tipos y
  sus claves están en el docstring de `plantillas/base.py`.
- Si a una placa le falta una clave, se saltea y avisa cuál falta.

En `editable` no hay ORDEN: la publicación define `construir(E)` y arma sus placas a mano
con el estilo elegido (`ESTILO = "diario" | "fiesta" | "riesgo" | "marca"`). Ver
`plantillas/modelos/editable.py`.

## Qué hay

```
instagram/
├── ig.py                    # lanzador único (ver arriba)
├── plantillas/              # la lógica de cada tipo: no se toca día a día
│   ├── base.py              #   placas por prefijo, variables, guardado + hoja de contactos
│   ├── pre_partido.py  post_partido.py  historias.py  editable.py
│   └── modelos/             #   punto de partida que copia `ig.py nuevo`
├── publicaciones/           # LO QUE EDITÁS: una por post
│   ├── pre_partido/  post_partido/  historias/  editables/
├── nucleo/                  # estilos y primitivas asentadas
│   ├── marca.py             #   identidad: colores, fuentes, primitivas
│   ├── placas.py            #   las placas del estándar negro + dorado
│   ├── temas.py             #   paletas alternativas (oscuro, hueso, blanco, dorada)
│   ├── estilo_diario.py  estilo_fiesta.py  estilo_riesgo.py
│   └── graficos_*.py  tabla_historica_grupo_a.py     # gráficos de cancha y tablas
├── herramientas/            # utilidades sueltas (bajar_escudos.py)
├── marca/estandar_visual.md # el estándar: paleta, tipografía, composición, tono
├── assets/                  # escudos, fotos, gráficos de cancha
├── placas/                  # SALIDAS: una carpeta por serie generada
├── _archivo/                # scripts viejos de una sola vez (referencia, no se ejecutan)
└── plan_contenido.md        # pilares, cadencia y backlog de posts
```

## Estándar de color

Base blanco y negro (colores del club) + acento **dorado `#E8B23A`**. Detalle completo
en `marca/estandar_visual.md`. Todo está en `nucleo/marca.py`: para cambiar el acento se
toca un solo valor y todo se regenera coherente. La previa usa el tema `hueso` y el
post-partido el `oscuro` (`nucleo/temas.py`).

## Tipos de placa del estándar (`nucleo/placas.py`)

| Función | Para qué |
|---------|----------|
| `portada(titulo, subtitulo, etiqueta)` | Tapa de carrusel |
| `dato(numero, etiqueta, contexto)` | Un número grande que sorprende |
| `dato_vs(hero, sub, col_izq, col_der)` | Número héroe + dos columnas |
| `ficha(titulo, subtitulo, filas)` | Tabla corta de estadísticas |
| `ranking(titulo, filas)` | Top de goleadores / rating / minutos |
| `resultado(local, gl, visitante, gv)` | Marcador de partido |
| `cita(frase, autor)` | Frase / lectura táctica |
| `grafico_marca(ruta_png, titulo)` | Meter un gráfico del pipeline con la marca |

## Skills de marketing

En `.claude/skills/` quedaron instaladas 46 skills (`social`, `content-strategy`,
`copywriting`, `image`...). Se invocan con `/social`, etc., para pedir ideas, calendarios
o textos para los posts, sobre lo definido en `plan_contenido.md`.
