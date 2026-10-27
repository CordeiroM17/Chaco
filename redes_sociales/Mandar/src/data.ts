// Datos tomados de ferro_carril_oeste_a/ (scouting_puestos.csv, informe pre partido, red de asistencias).
// Para cambiar el once, los textos o los números, editar SOLO este archivo.

export const PITCH = {x: 150, y: 300, w: 780, h: 1205};

export type Player = {
  id: string;
  name: string; // como aparece en la cancha
  nx: number; // 0 = izquierda, 1 = derecha
  ny: number; // 0 = arco que ataca Ferro, 1 = su arco
  threat?: boolean;
};

// 4-1-4-1 (su dibujo desde julio). Once del último partido, con Dening de 9 (alterna con Reniero).
export const XI: Player[] = [
  {id: 'monetti', name: 'MONETTI', nx: 0.5, ny: 0.93},
  {id: 'osuna', name: 'OSUNA', nx: 0.14, ny: 0.75},
  {id: 'canto', name: 'CANTO', nx: 0.38, ny: 0.8},
  {id: 'tevez', name: 'TÉVEZ', nx: 0.62, ny: 0.8},
  {id: 'kihm', name: 'KIHM', nx: 0.86, ny: 0.75},
  {id: 'obradovich', name: 'OBRADOVICH', nx: 0.5, ny: 0.64},
  {id: 'parisi', name: 'PARISI', nx: 0.17, ny: 0.36, threat: true},
  {id: 'hoyos', name: 'HOYOS', nx: 0.38, ny: 0.5, threat: true},
  {id: 'kabalin', name: 'KABALIN', nx: 0.62, ny: 0.5},
  {id: 'gonzalez', name: 'GONZÁLEZ', nx: 0.84, ny: 0.4, threat: true},
  {id: 'dening', name: 'DENING', nx: 0.5, ny: 0.2},
];

export const byId = (id: string) => {
  const p = XI.find((x) => x.id === id);
  if (!p) throw new Error(`Jugador desconocido: ${id}`);
  return p;
};

export const toPx = (p: Player) => ({x: PITCH.x + p.nx * PITCH.w, y: PITCH.y + p.ny * PITCH.h});

// Dónde queda la pelota cuando la tiene un jugador
export const feet = (id: string) => {
  const p = toPx(byId(id));
  return {x: p.x + 26, y: p.y + 36};
};

export type Card = {
  id: string;
  chip: string;
  name: string;
  value: number;
  countFrom: number;
  prefix?: string;
  suffix?: string;
  label: string;
  sub: string;
};

// El circuito, en orden: la pelota pasa por los tres
export const CARDS: Card[] = [
  {
    id: 'hoyos',
    chip: '01 · EL CEREBRO',
    name: 'HOYOS',
    value: 3,
    countFrom: 111,
    suffix: '°',
    label: 'DE 111 VOLANTES DEL TORNEO',
    sub: 'el mejor puntuado de Ferro',
  },
  {
    id: 'gonzalez',
    chip: '02 · EL QUE LA PONE',
    name: 'GONZÁLEZ',
    value: 7,
    countFrom: 0,
    label: 'ASISTENCIAS',
    sub: 'nadie asiste más en Ferro',
  },
  {
    id: 'parisi',
    chip: '03 · EL QUE LA METE',
    name: 'PARISI',
    value: 9,
    countFrom: 0,
    label: 'GOLES',
    sub: 'goleador del equipo',
  },
];
