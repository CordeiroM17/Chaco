import {Easing} from 'remotion';
import {byId, feet, toPx} from './data';

type Ez = 'io' | 'in' | 'out' | 'lin' | 'zoom';

const EASE: Record<Ez, (t: number) => number> = {
  io: Easing.bezier(0.65, 0, 0.35, 1),
  // in + out encadenados dan velocidad continua en el punto medio (zoom out → zoom in sin frenar)
  in: (t) => t * t,
  out: (t) => 1 - (1 - t) * (1 - t),
  lin: (t) => t,
  zoom: Easing.bezier(0.7, 0, 0.2, 1),
};

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

const segment = <K extends {f: number; e?: Ez}>(keys: K[], frame: number) => {
  if (frame <= keys[0].f) return {a: keys[0], b: keys[0], t: 0, raw: 0};
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i];
    const b = keys[i + 1];
    if (frame <= b.f) {
      const raw = (frame - a.f) / (b.f - a.f);
      return {a, b, t: EASE[b.e ?? 'io'](raw), raw};
    }
  }
  const last = keys[keys.length - 1];
  return {a: last, b: last, t: 0, raw: 0};
};

// ---------- Cámara ----------
// (cx, cy) = punto de la cancha que se lleva a la posición de pantalla (ax, ay)
export type Cam = {cx: number; cy: number; s: number; ax: number; ay: number; rot: number};
type CamKey = Cam & {f: number; e?: Ez};

const OV = {cx: 540, cy: 902, ax: 540, ay: 985};
const on = (id: string) => {
  const p = toPx(byId(id));
  return {cx: p.x + 10, cy: p.y + 14, ax: 540, ay: 700};
};
const mid = (a: string, b: string) => {
  const pa = on(a);
  const pb = on(b);
  return {cx: (pa.cx + pb.cx) / 2, cy: (pa.cy + pb.cy) / 2, ax: 540, ay: 760};
};

const CAM: CamKey[] = [
  {f: 116, cx: 540, cy: 902, ax: 540, ay: 960, s: 31, rot: 0},
  {f: 128, cx: 540, cy: 902, ax: 540, ay: 960, s: 30, rot: 0, e: 'lin'},
  {f: 194, ...OV, s: 1, rot: 0, e: 'zoom'}, // gran zoom out desde la pelota
  {f: 242, ...OV, s: 1.04, rot: 0, e: 'lin'},
  {f: 274, ...on('hoyos'), s: 2.6, rot: -3, e: 'io'}, // zoom in
  {f: 356, ...on('hoyos'), s: 2.8, rot: -1, e: 'lin'},
  {f: 376, ...mid('hoyos', 'gonzalez'), s: 1.45, rot: 0, e: 'in'}, // zoom out siguiendo el pase
  {f: 396, ...on('gonzalez'), s: 2.6, rot: 3, e: 'out'}, // zoom in
  {f: 476, ...on('gonzalez'), s: 2.8, rot: 1, e: 'lin'},
  {f: 496, ...mid('gonzalez', 'parisi'), s: 1.45, rot: 0, e: 'in'},
  {f: 516, ...on('parisi'), s: 2.6, rot: -3, e: 'out'},
  {f: 600, ...on('parisi'), s: 2.8, rot: -1, e: 'lin'},
  {f: 626, cx: 500, cy: 420, ax: 540, ay: 820, s: 2.1, rot: 0, e: 'io'}, // sigue el remate
  {f: 640, cx: 500, cy: 420, ax: 540, ay: 820, s: 2.15, rot: 0, e: 'lin'},
  {f: 690, ...OV, ay: 1000, s: 0.92, rot: 0, e: 'io'}, // zoom out al circuito completo
  {f: 900, ...OV, ay: 1000, s: 0.8, rot: 0, e: 'lin'},
];

export const camAt = (frame: number): Cam => {
  const {a, b, t} = segment(CAM, frame);
  return {
    cx: lerp(a.cx, b.cx, t),
    cy: lerp(a.cy, b.cy, t),
    // zoom en escala logarítmica: se siente parejo de punta a punta
    s: Math.exp(lerp(Math.log(a.s), Math.log(b.s), t)),
    ax: lerp(a.ax, b.ax, t),
    ay: lerp(a.ay, b.ay, t),
    rot: lerp(a.rot, b.rot, t),
  };
};

export const camTransform = (c: Cam) =>
  `translate(${c.ax}px, ${c.ay}px) rotate(${c.rot}deg) scale(${c.s}) translate(${-c.cx}px, ${-c.cy}px)`;

// Desenfoque leve según velocidad de cámara
export const camBlur = (frame: number) => {
  const a = camAt(frame - 1);
  const b = camAt(frame);
  const speed = Math.hypot((b.cx - a.cx) * b.s, (b.cy - a.cy) * b.s) + Math.abs(Math.log(b.s / a.s)) * 400;
  return Math.min(speed * 0.04, 6);
};

// ---------- Pelota ----------
type BallKey = {f: number; x: number; y: number; air?: number; e?: Ez};

const fh = feet('hoyos');
const fg = feet('gonzalez');
const fp = feet('parisi');
export const BALL_R = 11;
export const SHOT_END = {x: 548, y: 322};

const BALL: BallKey[] = [
  {f: 0, x: 540, y: 902},
  {f: 240, x: 540, y: 902, e: 'lin'},
  {f: 274, ...fh, e: 'out'}, // conducción hasta Hoyos
  {f: 356, ...fh, e: 'lin'},
  {f: 396, ...fg, air: 1, e: 'io'}, // cambio de frente a González
  {f: 476, ...fg, e: 'lin'},
  {f: 516, ...fp, air: 0.8, e: 'io'}, // centro a Parisi
  {f: 600, ...fp, e: 'lin'},
  {f: 620, ...SHOT_END, e: 'in'}, // remate... y se congela
  {f: 900, ...SHOT_END, e: 'lin'},
];

export const ballAt = (frame: number) => {
  const {a, b, t, raw} = segment(BALL, frame);
  const x = lerp(a.x, b.x, t);
  const y = lerp(a.y, b.y, t);
  const h = (b.air ?? 0) * Math.sin(Math.PI * raw);
  // gira según lo que recorrió (0° en el círculo central, igual que la pelota de la presentación)
  const rot = (((x - 540) + (y - 902)) / BALL_R) * (180 / Math.PI);
  return {x, y, h, rot};
};

// Tramos del circuito que la pelota va dibujando
export const PASSES = [
  {from: fh, to: fg, start: 356, end: 396},
  {from: fg, to: fp, start: 476, end: 516},
  {from: fp, to: SHOT_END, start: 600, end: 620},
];
