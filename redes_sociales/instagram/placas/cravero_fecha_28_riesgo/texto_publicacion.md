# Texto de publicación — Cravero, versión estilo_riesgo (cierre Fecha 28)

## Caption

🖤🤍 DE LA ZONA ROJA AL RESPIRO

Daniel Cravero, el técnico del último ascenso, volvió operado del corazón y agarró a For Ever último en el Grupo A. Diez fechas después el Negro es otro.

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

- 12 placas, carpeta `placas/cravero_fecha_28_riesgo/`. Estética `estilo_riesgo.py`
  (fondo blanco, cinta de peligro, rojo) — la misma que la placa de "peligro de
  descenso" (`carrusel_curiosidad_montecarlo.py`).
- Placas 10-12 = los 3 gráficos del modelo completo (probabilidad por posición,
  distribución de puntos, proyección por zona) a pantalla casi entera, SIN el
  cabezal "CHACO FOR EVER / ESTADÍSTICAS" (función `R.grafico_full`). Se
  regeneran con `liga.generate_projection_graphics('2026', n_sims=100000,
  seed=42)` → `outputs/.../liga/proyeccion/`. Correr eso ANTES del carrusel para
  que los números del gráfico coincidan con los de las placas 6-8.
- Es la versión alternativa de `carrusel_cravero.py` (estilo diario). Mismo
  contenido base + el gráfico de cancha + las tres probabilidades.
- Gráfico de cancha: `scripts/graficos_cravero_marca.py` → `assets/cravero_once.png`.
  Correrlo ANTES del carrusel. Posiciones = promedio ponderado de
  `average_positions_clean.csv` de los 10 partidos de Cravero (afinadas a un
  4-4-2 legible); dorsal = el más usado por cada uno (`xi_pos.py`). El arco se
  muestra con Caprio (Canuto arrancó de titular y Caprio le ganó el puesto en
  la fecha 24).
- Probabilidades: `src/analysis/simulation.py` (Dixon-Coles, 100.000 sims),
  corrido el 2026-09-08 tras la fecha 28. Descenso 1,83% → 1,8%; Reducido por
  posición 10,06% → 10%; permanencia = complemento (98,2%). Posición media 11,8.
- Alcance del modelo: solo Zona A; "Reducido" = terminar 2°-8° por posición, no
  simula el cuadro del Reducido ni el ascenso directo (Fase 2 pendiente).
- Sin menciones de amarillas / riesgo de suspensión (convención de la cuenta).
