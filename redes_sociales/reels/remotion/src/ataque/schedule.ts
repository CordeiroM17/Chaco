import {V3} from './engine3d';
import {MATCHES, SHOTS} from './shots';
import {T} from './tema';

export type Shot = {
  date: string;
  rival: string;
  minute: number;
  kind: 'g' | 's' | 'b' | 'm' | 'p';
  head: boolean;
  xg: number;
  from: V3;
  to: V3;
  lift: number;
  late: boolean; // desde el 2 de agosto
};

export const ALL: Shot[] = SHOTS.map((r) => {
  const head = r[4] === 1;
  const from: V3 = [r[6], r[7], head ? 1.9 : 0.15];
  const to: V3 = [r[8], r[9], r[10]];
  const dist = Math.hypot(to[0] - from[0], to[1] - from[1]);
  return {
    date: r[0],
    rival: r[1],
    minute: r[2],
    kind: r[3] as Shot['kind'],
    head,
    xg: r[5],
    from,
    to,
    lift: head ? 0.4 : Math.min(2.6, Math.max(0.3, dist * 0.06)),
    late: r[11] === 1,
  };
});

export const GOALS = ALL.filter((s) => s.kind === 'g');
export const LATE = ALL.filter((s) => s.late);

export type Launch = {shot: Shot; t0: number; dur: number};

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// Crescendo: los primeros remates salen de a uno, los últimos casi todos juntos
const rain = (shots: Shot[], start: number, end: number, power: number, durA: number, durB: number): Launch[] =>
  shots.map((shot, i) => {
    const u = shots.length > 1 ? i / (shots.length - 1) : 0;
    return {shot, t0: start + (end - start) * Math.pow(u, power), dur: lerp(durA, durB, u)};
  });

export const RAIN1 = rain(ALL, T.rain1[0], T.rain1[1], 0.55, 28, 12);
export const RAIN2 = rain(LATE, T.rain2[0], T.rain2[1], 0.6, 22, 12);

export const inBox = (s: Shot) => s.from[1] <= 16.5 && Math.abs(s.from[0]) <= 20.16;

// Gancho: el gol de afuera a Madryn (uno de los 2 de afuera en todo el año)
const hookShot = GOALS.find((s) => s.rival === 'MADRYN' && !inBox(s)) ?? GOALS[0];
export const HOOK: Launch[] = [{shot: hookShot, t0: T.hookLaunch, dur: T.hookDur}];

// Posición de la pelota en el vuelo (u de 0 a 1) y después del impacto
export const ballPos = (s: Shot, u: number): V3 => {
  if (u <= 1) {
    const x = s.from[0] + (s.to[0] - s.from[0]) * u;
    const y = s.from[1] + (s.to[1] - s.from[1]) * u;
    const z = s.from[2] + (s.to[2] - s.from[2]) * u + 4 * s.lift * u * (1 - u);
    return [x, y, z];
  }
  // después del impacto: gol → se mete en la red; afuera → sigue de largo; atajada/bloqueo → rebota
  const k = Math.min(u - 1, 0.35);
  if (s.kind === 'g') return [s.to[0], s.to[1] - 4.5 * k, Math.max(0.1, s.to[2] - 3 * k)];
  if (s.kind === 'm' || s.kind === 'p') {
    const dx = s.to[0] - s.from[0];
    const dy = s.to[1] - s.from[1];
    return [s.to[0] + dx * k * 0.4, s.to[1] + dy * k * 0.4, s.to[2] + 2 * k];
  }
  const dx = s.from[0] - s.to[0];
  const dy = s.from[1] - s.to[1];
  const l = Math.hypot(dx, dy) || 1;
  return [s.to[0] + (dx / l) * 9 * k, s.to[1] + (dy / l) * 9 * k, Math.max(0.1, s.to[2] + 3 * k - 12 * k * k)];
};

// Fecha y rival del último remate lanzado
export const currentMatch = (launches: Launch[], frame: number) => {
  let last: Launch | null = null;
  for (const l of launches) if (l.t0 <= frame) last = l;
  return last;
};

const AUG = '2026-08-02';
export const BEFORE = MATCHES.filter((m) => m[0] < AUG);
export const AFTER = MATCHES.filter((m) => m[0] >= AUG);
const sum = (ms: typeof MATCHES) => ms.reduce((a, m) => a + m[2], 0);
const OUT = ALL.filter((s) => !inBox(s));
const IN = ALL.filter(inBox);
// partidos con remates registrados (5 no tienen shotmap)
const games = (ss: Shot[]) => new Set(ss.map((s) => s.date)).size;
export const STATS = {
  shots: ALL.length,
  goals: GOALS.length,
  totalGF: sum(MATCHES),
  out: OUT.length,
  outGoals: OUT.filter((s) => s.kind === 'g').length,
  in: IN.length,
  inGoals: IN.filter((s) => s.kind === 'g').length,
  beforeGames: BEFORE.length,
  beforeGF: sum(BEFORE),
  afterGames: AFTER.length,
  afterGF: sum(AFTER),
  beforeShotsPG: ALL.filter((s) => !s.late).length / games(ALL.filter((s) => !s.late)),
  lateShotsPG: LATE.length / games(LATE),
  lateShots: LATE.length,
  lateOut: LATE.filter((s) => !inBox(s)).length,
  lateGoals: LATE.filter((s) => s.kind === 'g').length,
};
