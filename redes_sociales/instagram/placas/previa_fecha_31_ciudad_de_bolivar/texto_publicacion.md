# Texto de publicación — Previa Fecha 31 vs Ciudad de Bolívar (visitante)

## Caption

🖤🤍 AHORA, BOLÍVAR

El sábado 26/9 visitamos a Ciudad de Bolívar (16:00), 8° con 39 puntos: un equipo de mitad de tabla que empata muchísimo (12 de sus 30 partidos) y tuvo un solo entrenador en toda la temporada, Diego Funes.

El número que lo define: en xG concede 1.28 por partido pero solo recibe 0.90 goles reales —unos 11 de menos en 30 fechas—, sostenido por A. Rufinetti, su arquero. Misma historia que la semana pasada con Almirante Brown.

En el duelo de números nos favorece con claridad: +0.50 de xG combinado a nuestro favor, la brecha más amplia que tenemos contra un rival esta temporada. Pero ojo: el único antecedente que tenemos con ellos fue una derrota, 0-1 en nuestra cancha, y ahí también perdimos el duelo de xG (0.49 a 1.40) pese a dominar la posesión y los córners.

Nosotros llegamos de la mejor manera: 6 partidos seguidos sin recibir goles, la racha más larga del año, y 3 victorias y 2 empates en los últimos cinco.

#chacoforever #elnegro #primeranacional #yoconfío #ascenso

---

## Notas de armado

- 13 placas, carpeta `placas/previa_fecha_31_ciudad_de_bolivar/`. Generadas con
  `scripts/carrusel_previa_ciudad_de_bolivar.py` (nuevo, basado en
  `carrusel_previa_almirante_brown.py`). Tema "hueso".
- Datos sacados de `outputs/temporadas/2026/pre_partido/ciudad_de_bolivar_a/
  Informe_pre_partido_ciudad_de_bolivar.tex` (informe pre-partido armado en
  esta misma sesión).
- Escudo de Ciudad de Bolívar bajado con `scripts/bajar_escudos.py` ->
  `assets/escudos/ciudad_de_bolivar.png`.
- Ajuste de texto: las primeras placas generadas se probaron con párrafos
  más largos que los del molde de Almirante Brown y el texto se salía del
  marco (se metía en el pie de página). `placas.py` no recorta ni achica
  texto automáticamente en `dato()`/`dato_vs()` — hay que medirlo a mano
  contra el ancho real de fuente antes de darlo por bueno. Quedó verificado
  con las fuentes reales (helper descartable, ya borrado) antes de la
  versión final.
- Sin placas de amarillas ni de riesgo de suspensión (convención de la
  cuenta). El informe base sí trae la alerta de disciplina propia, pero
  pide confirmarla con el club antes de publicarla en cualquier lado.
