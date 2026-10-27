import {loadFont as loadAnton} from '@remotion/google-fonts/Anton';
import {loadFont as loadMono} from '@remotion/google-fonts/JetBrainsMono';

export const DISPLAY = loadAnton('normal', {weights: ['400'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const MONO = loadMono('normal', {weights: ['400', '700'], subsets: ['latin', 'latin-ext']}).fontFamily;

export const W = 1080;
export const H = 1920;
export const FPS = 30;
export const DURATION = 1080; // 36 s

// Negro y blanco de Chaco For Ever + dorado solo para los goles
export const C = {
  bg: '#050505',
  pitchA: '#0B0B0B',
  pitchB: '#0F0F0F',
  ink: '#F5F5F0',
  gray: '#8C8C88',
  gold: '#F2C14E',
};

// Línea de tiempo (frames a 30 fps)
export const T = {
  hookLaunch: 6, // un gol de tiro libre, vista del arquero
  hookDur: 28,
  hookText: [38, 104] as const,
  rain1: [110, 470] as const, // los 279 remates, cada vez más rápido
  reveal: [500, 642] as const, // dónde entraron
  turn: [640, 694] as const, // "PERO DESDE AGOSTO..."
  chart: [690, 792] as const, // goles en contra partido a partido
  rain2: [796, 896] as const, // los 70 remates desde agosto
  clean: [904, 972] as const, // 6 vallas invictas
  outro: 966,
};
