# Texto de publicación — Cravero, versión estilo diario (cierre Fecha 28)

Mismo contenido que `placas/cravero_fecha_28_riesgo/` pero en la estética de
recorte de diario. Elegir una de las dos para publicar (no las dos).

## Caption

🖤🤍 DE LA ZONA ROJA AL RESPIRO

Daniel Cravero se crió en For Ever, salió campeón del Nacional B con la camiseta en 1988/89 y fue el DT que en 2021 devolvió al club a la Primera Nacional después de 23 años. Este año volvió: se operó del corazón, esperó el alta y agarró al equipo último en el Grupo A.

Diez fechas después el Negro es otro.

20 puntos de 30: seis triunfos, dos empates, dos derrotas. Recibe 0,50 gol por partido —eran 1,33 antes de que llegara— y lleva seis vallas invictas en diez fechas. Está 11°, cuatro puntos arriba de San Telmo, el primero abajo de la línea. Si el torneo se contara solo desde que asumió, sería puntero de la zona.

El once que más repite (posición promedio real, con el dorsal de cada uno): Caprio; Ojeda, Garay, Valdez, Luque; L. Fernández, Nievas, Carrizo, Gaggi; Romero y Pacheco. En el arco, Caprio le ganó el puesto a Canuto.

Lo que dice la simulación (Monte Carlo, 100.000 temporadas, modelo Dixon-Coles sobre la Zona A):

- Descenso: 1,8% — cuando Cravero asumió rondaba el 30%.
- Permanencia: 98,2%.
- Entrar al Reducido (terminar 2° a 8°): 10% — a mediados de agosto era del 1%.

Lo trajeron para no descender. Hoy la simulación lo pone a pelear por otra cosa.

#chacoforever #elnegro #primeranacional #yoconfío #ascenso

---

## Notas de armado

- 15 placas, carpeta `placas/cravero_fecha_28/`. Estética `estilo_diario.py`
  (papel + serif + filetes). Es la versión "diario" de
  `carrusel_cravero_riesgo.py` + una sección de trayectoria adelante (placas
  02-04: tabla "Toda una vida de Negro", "23" años afuera, "7 horas" de cirugía)
  que la de riesgo no tiene.
- Resaltado inline en varias placas: `frase` = negrita + rojo, `frase` =
  negrita. Lo parsea `estilo_diario.parrafo`.
- `scripts/carrusel_cravero.py`. Antes de correrlo:
  1. `python scripts/graficos_cravero_marca.py` — genera la cancha en tema papel
     (`assets/cravero_once_papel.png`).
  2. `PYTHONUTF8=1 python -c "from src.analysis import liga; liga.generate_projection_graphics('2026', n_sims=100000, seed=42)"`
     — regenera los 3 gráficos del modelo (placas 10-12).
- Placa 04: cancha con el 11 más usado por Cravero (posición promedio real +
  dorsal). Placas 10-12: los 3 gráficos del modelo a pantalla casi entera, sin
  cabezal (`D.grafico_full`), con un filete fino alrededor (aire de foto de
  diario).
- Funciones nuevas en `estilo_diario.py`: `columna` (metodología), `grafico`,
  `grafico_full`, `_recortar_blanco`.
- Sin menciones de amarillas / riesgo de suspensión (convención de la cuenta).
- La versión anterior de este carrusel (trayectoria: ídolo, 23 años, 7 horas de
  cirugía, vuelta de Romero) quedó reemplazada. Si se quiere recuperar, está en
  el historial de git de `scripts/carrusel_cravero.py`.
