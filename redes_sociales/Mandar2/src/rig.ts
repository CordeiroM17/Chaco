import {Easing} from 'remotion';
import {Rig} from './engine3d';

type Key = Rig & {fr: number};

// Vista del arquero (detrás del arco) → órbita → vista aérea → vuelta al arquero
const KEEPER = {tx: 0, ty: 16, tz: 1, dist: 24, az: 0, el: 8, f: 950};
const AERIAL = {tx: 0, ty: 17, tz: 0, dist: 58, az: 0, el: 66, f: 950};

const KEYS: Key[] = [
  {fr: 0, ...KEEPER, dist: 26},
  {fr: 34, ...KEEPER, dist: 21.5, el: 8.5}, // empuje al momento del gol
  {fr: 104, ...KEEPER, dist: 23, el: 9},
  {fr: 290, tx: 0, ty: 16, tz: 0.5, dist: 33, az: 30, el: 15, f: 950},
  {fr: 480, ...AERIAL, az: -6, el: 56, dist: 56},
  {fr: 520, ...AERIAL},
  {fr: 642, ...AERIAL, ty: 14, dist: 48, el: 72},
  {fr: 700, ...AERIAL, ty: 14, dist: 48, el: 72},
  {fr: 790, ...KEEPER, az: -14, el: 9},
  {fr: 900, ...KEEPER, az: 10, el: 11, dist: 22},
  {fr: 1080, ...KEEPER, az: 16, el: 13, dist: 20},
];

const ease = Easing.bezier(0.65, 0, 0.35, 1);
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const rigAt = (frame: number): Rig => {
  if (frame <= KEYS[0].fr) return KEYS[0];
  for (let i = 0; i < KEYS.length - 1; i++) {
    const a = KEYS[i];
    const b = KEYS[i + 1];
    if (frame <= b.fr) {
      const t = ease((frame - a.fr) / (b.fr - a.fr));
      return {
        tx: lerp(a.tx, b.tx, t),
        ty: lerp(a.ty, b.ty, t),
        tz: lerp(a.tz, b.tz, t),
        dist: Math.exp(lerp(Math.log(a.dist), Math.log(b.dist), t)),
        az: lerp(a.az, b.az, t),
        el: lerp(a.el, b.el, t),
        f: lerp(a.f, b.f, t),
      };
    }
  }
  return KEYS[KEYS.length - 1];
};
