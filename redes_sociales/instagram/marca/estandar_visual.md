# Estándar visual — @chacoforever.stats

La cuenta es de fanáticos, no un informe técnico. La regla es simple: que cualquier
placa se reconozca como nuestra a un metro de distancia, sin leer el texto. Eso lo
logra el estándar de color y la tipografía, no un logo.

## Colores

La base son los colores del club: **blanco y negro** (el blanco del algodón, el negro
del carbón). Encima va un **acento dorado** para que en el feed no se vea plano y para
resaltar el dato que importa.

| Uso | Nombre | HEX | RGB |
|-----|--------|-----|-----|
| Fondo principal | Negro | `#0E0E0E` | 14, 14, 14 |
| Tarjetas / bloques | Carbón | `#1C1C1C` | 28, 28, 28 |
| Texto principal | Tinta (blanco roto) | `#F5F5F5` | 245, 245, 245 |
| Rayas del club | Blanco puro | `#FFFFFF` | 255, 255, 255 |
| **Acento** | **Dorado** | **`#E8B23A`** | 232, 178, 58 |
| Acento apagado | Dorado oscuro | `#B78A28` | 183, 138, 40 |
| Texto secundario | Gris | `#969696` | 150, 150, 150 |
| Separadores | Gris oscuro | `#464646` | 70, 70, 70 |

**Regla del dorado:** una sola cosa dorada por placa. El número clave, o el título, o la
barra del líder. Si todo es dorado, nada resalta.

## Tipografía

Todo sale de fuentes ya instaladas en Windows, así que no hay que instalar nada.

- **Números gigantes:** Bahnschrift (condensada, deportiva) → `bahnschrift.ttf`
- **Títulos y nombres fuertes:** Segoe UI Black → `seguibl.ttf`
- **Subtítulos:** Segoe UI Bold → `segoeuib.ttf`
- **Etiquetas / versales:** Segoe UI Semibold → `seguisb.ttf`
- **Cuerpo:** Segoe UI → `segoeui.ttf`

Los kickers y etiquetas van en MAYÚSCULA con espaciado entre letras (tracking). Los
títulos, en mayúscula pesada. El cuerpo, normal.

## Composición

- Lienzo **1080 × 1080** (feed cuadrado). Márgenes de seguridad de 84 px.
- **Cabecera** fija arriba a la izquierda: rayas + "CHACO FOR EVER / ESTADÍSTICAS".
- **Pie** fijo abajo: línea dorada + `@handle` a la izquierda, fuente del dato a la derecha.
- Las **rayas blanco/negro** son el sello del club: van como marca de agua chica en la
  cabecera y, en portadas, como franjas laterales.
- Aire. Un dato por placa. Si hace falta contar más, es un carrusel, no una placa cargada.

## Tono

Hincha, no académico. Se puede opinar y picantear, pero el número manda y siempre se
cita la fuente (SofaScore). Nada de promesas ni "call to action" de venta: es por diversión.

## Cómo se aplica

Todo esto está codificado en `nucleo/marca.py`. Nadie elige colores a mano: se llaman
las constantes (`DORADO`, `NEGRO`, `TINTA`...) y las funciones de placa. Si algún día se
cambia el acento, se toca un solo valor en `marca.py` y todas las placas se regeneran
coherentes.
