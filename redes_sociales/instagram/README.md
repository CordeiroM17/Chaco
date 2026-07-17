# redes_sociales / instagram

Workspace **separado** para la cuenta de Instagram de estadísticas de Chaco For Ever.
Es para los fanáticos, no tiene que ver con los informes técnicos del pipeline. Acá se
diseña, se define el estándar de color y se generan las placas listas para publicar.

## Qué hay

```
instagram/
├── marca/
│   └── estandar_visual.md      # el estándar: paleta, tipografía, composición, tono
├── scripts/
│   ├── marca.py                # identidad codificada: colores, fuentes, primitivas
│   └── placas.py               # generadores de placa (portada, dato, ranking, etc.)
├── placas/
│   └── ejemplos/               # placas de muestra ya generadas
├── assets/                     # logos/escudos si se suman más adelante
├── plan_contenido.md           # pilares, cadencia y backlog de posts
└── README.md
```

## Estándar de color

Base blanco y negro (colores del club) + acento **dorado `#E8B23A`**. Detalle completo
en `marca/estandar_visual.md`. Todo está en `scripts/marca.py`: para cambiar el acento se
toca un solo valor y todo se regenera coherente.

## Generar placas

```bash
cd redes_sociales/instagram/scripts
python placas.py           # regenera los ejemplos en placas/ejemplos/
```

Para una placa nueva, desde Python:

```python
import placas as P, marca as M
img = P.dato("6.4", "goles concedidos por encima del xG",
             "El foco está atrás.", nota="Temporada 2026")
M.guardar(img, "../placas/mi_placa.png")
```

## Tipos de placa disponibles

| Función | Para qué |
|---------|----------|
| `portada(titulo, subtitulo, etiqueta)` | Tapa de carrusel |
| `dato(numero, etiqueta, contexto)` | Un número grande que sorprende |
| `ranking(titulo, filas, unidad)` | Top de goleadores / rating / minutos |
| `resultado(local, gl, visitante, gv)` | Marcador de partido |
| `cita(frase, autor)` | Frase / lectura táctica |
| `enmarcar(ruta_png, titulo)` | Meter un gráfico del pipeline con la marca |

## Skills de marketing

En `.claude/skills/` quedaron instaladas 46 skills (`social`, `content-strategy`,
`copywriting`, `image`...). Tras reiniciar Claude Code, se invocan con `/social`, etc.,
para pedir ideas, calendarios o textos para los posts, sobre lo definido en
`plan_contenido.md`.
