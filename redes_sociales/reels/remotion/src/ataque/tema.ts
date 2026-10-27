export {DISPLAY, HANDLE, MONO, NUM} from '../theme';

export const DURATION = 1110; // 37 s

// Negro y blanco de Chaco For Ever + dorado solo para los goles
export const C = {
  bg: '#0E0E0E',
  pitchA: '#121212',
  pitchB: '#161616',
  ink: '#F5F5F5',
  gray: '#969696',
  gold: '#E8B23A',
};

// Línea de tiempo (frames a 30 fps)
export const T = {
  hookLaunch: 6, // el gol de afuera a Madryn, vista del arquero
  hookDur: 30,
  hookText: [40, 106] as const,
  rain1: [112, 472] as const, // los 314 remates, cada vez más rápido
  reveal: [500, 690] as const, // afuera vs adentro (dos tiempos)
  revealSplit: 596, // de "afuera" a "adentro"
  turn: [688, 740] as const, // "DESDE AGOSTO..."
  chart: [736, 838] as const, // goles a favor partido a partido
  rain2: [842, 942] as const, // los remates desde agosto
  ratio: [950, 1010] as const, // 1 de cada 6 vs 1 de cada 86
  outro: 1006,
};
