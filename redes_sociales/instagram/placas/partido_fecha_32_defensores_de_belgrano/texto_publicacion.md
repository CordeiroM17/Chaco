# Texto de publicación — Post-partido Fecha 32 vs Defensores de Belgrano (2-2)

## Caption

🖤🤍 EMPATAMOS 2-2 CON DEFENSORES

Brian Nievas hizo los dos goles del primer tiempo: de cabeza a los 5', con centro de Agustín Ojeda, y a los 45'+3 con un remate de derecha después de un pase entre líneas. El Negro se fue al descanso 2-0 arriba, con 1.26 de xG contra 0.63.

En el segundo tiempo el partido cambió. Defensores hizo dos cambios a los 60', Benítez descontó a los 63' y Aguirre empató a los 85'. Terminó con 1.80 de xG contra 1.60 nuestro, con 15 remates para cada lado.

¿Por qué empatamos? Hasta los 69' el partido estaba parejo: de los 60' a los 69' el xG fue 0.08 para el Negro y 0.09 para Defensores. Del 69' al final, Defensores sumó 0.86 de xG y nosotros 0.14. En todo el segundo tiempo no tuvimos ningún remate dentro del área (ellos, 5). El 2-1 salió de un remate de 0.05 de xG desde unos 22 metros y el 2-2, de una ocasión de 0.36. Caprio, además, atajó tres, dos de valor alto.

Nievas fue el mejor puntuado de la fecha en toda la Zona A (9.4), entró al Mejor 11 y llegó a 5 goles en el año.

El Negro sigue 10° con 37 puntos, a 6 de la zona de descenso, con el 0,17% de chances de bajar. Quedan cuatro fechas. Lo próximo: Deportivo Madryn, de visitante.

#chacoforever #elnegro #primeranacional #yoconfío #ascenso

---

## Historias (9:16)

Carpeta `placas/historias_fecha_32_defensores_de_belgrano/`:
`01_ratings`, `02_shotmap`, `03_stats`, `04_salvados` (Almirante Brown, Estudiantes de Buenos Aires y Ciudad de Bolívar, que se salvaron en esta fecha) y `05_combinacion_chaco` (cómo puede salvarse Chaco tras la fecha 34).

---

## Notas de armado

- 18 placas, carpeta `placas/partido_fecha_32_defensores_de_belgrano/`. Generadas con
  `scripts/carrusel_partido.py` (DATOS de la F32 cargado ahí) y los gráficos de
  `scripts/graficos_partido_marca.py` (FIGURA = "B. Nievas").
- Foto de la figura (placa 04): `assets/Nievas2.jpg`, la foto completa y sin recorte, sacada de la publicación
  abierta en `assets/Nievas2.html` (instagram.com/chinonievas/p/DcZisEIj0X_, 1ª de 2 imágenes; el .heic se convirtió
  a JPG). La 2ª imagen de esa publicación (blanco y negro) quedó como `assets/Nievas2_b.jpg`. Alternativas que
  quedan guardadas: `Brian_Nievas_recorte.jpg` (foto anterior) y `Brian_Nievas2_recorte(_amplio).jpg` (recortes de
  la gráfica "¡Goleador Chino!", que se descartaron).
- Esta fecha sí hubo un jugador de Chaco en el Mejor 11 (Nievas): placa 06 = ranking de ratings
  del Negro, placa 07 = su lugar en el Mejor 11 (`slot7_*`).
- Placas 10 a 13 = análisis de por qué empatamos: 10 xG por tramo (la fila del 69'–90' destacada), 11 "69'" (el
  minuto en que se inclinó el partido), 12 el segundo tiempo en números (0 remates en el área contra 5), 13 los dos
  goles del empate (0.05 y 0.36 de xG). Salen de `tramos_*`, `quiebre_*`, `st_*` y `goles_*` en DATOS; las placas
  `arco_*` y `patron_*` de otras fechas son opcionales y acá no se usan.
- Los números salen del shotmap: "dentro del área" = `coord_x <= 15`, el criterio que reproduce la estadística de SofaScore.
- Los mapas de calor no se leen como "se replegó": Defensores tuvo 51% de pelota. Los títulos son neutros.
- Sin placa de amarillas / riesgo de suspensión (convención de la cuenta).
