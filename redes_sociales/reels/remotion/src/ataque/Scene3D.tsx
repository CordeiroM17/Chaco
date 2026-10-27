import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Camera, V3, arc, makeCamera, polygon, polyline, project, segment} from './engine3d';
import {rigAt} from './rig';
import {HOOK, Launch, RAIN1, RAIN2, ballPos, inBox} from './schedule';
import {C, T} from './tema';
import {SoccerBall} from '../Ball';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const HALF = 52.5;
const PW = 34;
const POST = 3.66;
const BAR = 2.44;
const NET_D = 1.8;
const NET_TOP = 2.0;

const PITCH_LINES: V3[][] = [
  [[-PW, 0, 0], [PW, 0, 0]],
  [[-PW, 0, 0], [-PW, HALF, 0]],
  [[PW, 0, 0], [PW, HALF, 0]],
  [[-PW, HALF, 0], [PW, HALF, 0]],
  [[-20.16, 0, 0], [-20.16, 16.5, 0], [20.16, 16.5, 0], [20.16, 0, 0]],
  [[-9.16, 0, 0], [-9.16, 5.5, 0], [9.16, 5.5, 0], [9.16, 0, 0]],
  arc(0, 11, 9.15, 0.645, 2.497, 16),
  arc(0, HALF, 9.15, Math.PI, Math.PI * 2, 24),
];

const BOX: V3[] = [[-20.16, 0, 0], [-20.16, 16.5, 0], [20.16, 16.5, 0], [20.16, 0, 0]];

type Hit = {x: number; z: number; age: number};

const ease = (p: number) => 1 - Math.pow(1 - p, 1.25);

// Estado de un remate en el frame actual
const stateOf = (l: Launch, frame: number) => {
  const age = frame - l.t0;
  if (age < 0) return null;
  const p = age / l.dur;
  const post = Math.max(0, age - l.dur);
  const u = p <= 1 ? ease(p) : 1 + Math.min(post / 12, 1) * 0.35;
  return {age, p, post, u};
};

const Net: React.FC<{cam: Camera; hits: Hit[]; glow: number}> = ({cam, hits, glow}) => {
  const ripple = (x: number, z: number) =>
    hits.reduce((acc, h) => {
      const amp = 0.9 * Math.cos(h.age * 0.55) * Math.exp(-h.age / 9);
      return acc - amp * Math.exp(-((x - h.x) ** 2 + (z - h.z) ** 2) / 0.9);
    }, 0);
  const back = (x: number, z: number): V3 => [x, -NET_D + ripple(x, z), z];
  const xs = Array.from({length: 13}, (_, i) => -POST + (i * 2 * POST) / 12);
  const zs = [0.4, 0.8, 1.2, 1.6, NET_TOP];
  let d = '';
  for (const x of xs) {
    d += polyline(cam, Array.from({length: 7}, (_, k) => back(x, (k * NET_TOP) / 6)));
    d += segment(cam, [x, 0, BAR], back(x, NET_TOP)) ?? '';
  }
  for (const z of zs) d += polyline(cam, xs.map((x) => back(x, z)));
  for (const sx of [-POST, POST]) {
    for (const z of [0, 0.6, 1.2, 1.8, BAR]) d += segment(cam, [sx, 0, z], [sx, -NET_D, (z * NET_TOP) / BAR]) ?? '';
    d += segment(cam, [sx, -NET_D, 0], [sx, -NET_D, NET_TOP]) ?? '';
  }
  const frame = polyline(cam, [[-POST, 0, 0], [-POST, 0, BAR], [POST, 0, BAR], [POST, 0, 0]]);
  const near = project(cam, [0, 0, BAR]);
  const w = near ? Math.min(14, Math.max(2.5, 0.12 * near.s)) : 3;
  return (
    <g fill="none">
      <path d={d} stroke={C.ink} strokeOpacity={0.22} strokeWidth={1.2} />
      {glow > 0 ? <path d={frame} stroke={C.gold} strokeWidth={w * 2.6} strokeOpacity={glow * 0.5} filter="url(#glow)" /> : null}
      <path d={frame} stroke={C.ink} strokeWidth={w} strokeLinecap="round" />
    </g>
  );
};

// fuera / dentro: 0..1, cuánto se resaltan los remates de afuera o de adentro del área
type LayerOpts = {opacity: number; fuera: number; dentro: number};

// Dibuja un grupo de remates: punto de origen, trayectoria, pelota e impacto
const Layer: React.FC<{cam: Camera; launches: Launch[]; frame: number; o: LayerOpts; idp: string}> = ({
  cam,
  launches,
  frame,
  o,
  idp,
}) => {
  if (o.opacity <= 0) return null;
  const dots: React.ReactNode[] = [];
  const trails: React.ReactNode[] = [];
  const balls: React.ReactNode[] = [];
  const rings: React.ReactNode[] = [];

  launches.forEach((l, i) => {
    const st = stateOf(l, frame);
    if (!st) return;
    const s = l.shot;
    const goal = s.kind === 'g';
    const dim = 1 - 0.88 * (inBox(s) ? o.fuera : o.dentro);

    // Punto de origen (tamaño = peligro, xG)
    const org = project(cam, [s.from[0], s.from[1], 0]);
    if (org) {
      const r = Math.min(26, Math.max(2.5, (0.3 + s.xg * 1.4) * org.s)) * Math.min(1, st.age / 6);
      dots.push(
        <g key={`d${i}`}>
          <circle cx={org.x} cy={org.y} r={r} fill={goal ? C.gold : C.ink} opacity={(goal ? 0.95 : 0.5) * dim} />
        </g>
      );
    }

    // Trayectoria
    const uEnd = Math.min(st.u, 1);
    const n = 14;
    const pts = Array.from({length: n + 1}, (_, k) => ballPos(s, (uEnd * k) / n));
    const fade = goal
      ? interpolate(st.post, [0, 30], [0.95, 0.55], clamp)
      : interpolate(st.post, [0, 24], [0.75, 0.07], clamp);
    trails.push(
      <path
        key={`t${i}`}
        d={polyline(cam, pts)}
        fill="none"
        stroke={goal ? C.gold : C.ink}
        strokeWidth={goal ? 3.5 : 1.6}
        strokeLinecap="round"
        opacity={fade * dim}
      />
    );

    // Pelota en vuelo
    if (st.post < 12) {
      const bp = project(cam, ballPos(s, st.u));
      if (bp) {
        const r = Math.max(6, 0.11 * bp.s * 1.6);
        const bo = interpolate(st.post, [4, 12], [1, 0], clamp);
        balls.push(
          <g key={`b${i}`} opacity={bo}>
            <circle cx={bp.x} cy={bp.y} r={r * 2.2} fill={goal ? C.gold : C.ink} opacity={0.18} />
            {r > 9 ? (
              <g transform={`translate(${bp.x} ${bp.y})`}>
                <SoccerBall r={r} rot={st.u * 900} id={`${idp}${i}`} />
              </g>
            ) : (
              <circle cx={bp.x} cy={bp.y} r={r} fill={C.ink} />
            )}
          </g>
        );
      }
    }

    // Impacto del gol
    if (goal && st.post > 0 && st.post < 20) {
      const ip = project(cam, s.to);
      if (ip) {
        rings.push(
          <circle
            key={`r${i}`}
            cx={ip.x}
            cy={ip.y}
            r={(0.3 + st.post * 0.12) * ip.s}
            fill="none"
            stroke={C.gold}
            strokeWidth={3}
            opacity={1 - st.post / 20}
          />
        );
      }
    }
  });

  return (
    <g opacity={o.opacity}>
      <g>{dots}</g>
      <g>{trails}</g>
      <g>{balls}</g>
      <g>{rings}</g>
    </g>
  );
};

const hitsOf = (launches: Launch[], frame: number, opacity: number): Hit[] => {
  if (opacity <= 0) return [];
  const hits: Hit[] = [];
  for (const l of launches) {
    if (l.shot.kind !== 'g') continue;
    const age = frame - l.t0 - l.dur;
    if (age >= 0 && age < 40) hits.push({x: l.shot.to[0], z: l.shot.to[2], age});
  }
  return hits;
};

export const Scene3D: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = makeCamera(rigAt(frame));

  const hookO = interpolate(frame, [T.rain1[0] - 8, T.rain1[0]], [1, 0], clamp);
  const r1O = Math.min(
    interpolate(frame, [T.rain1[0] - 8, T.rain1[0]], [0, 1], clamp),
    interpolate(frame, [T.turn[0] + 10, T.turn[1]], [1, 0], clamp)
  );
  const r2O = interpolate(frame, [T.rain2[0] - 10, T.rain2[0]], [0, 1], clamp);
  // afuera primero, adentro después
  const fuera = Math.min(
    interpolate(frame, [T.reveal[0], T.reveal[0] + 16], [0, 1], clamp),
    interpolate(frame, [T.revealSplit - 6, T.revealSplit + 8], [1, 0], clamp)
  );
  const dentro = Math.min(
    interpolate(frame, [T.revealSplit - 6, T.revealSplit + 8], [0, 1], clamp),
    interpolate(frame, [T.reveal[1] - 12, T.reveal[1]], [1, 0], clamp)
  );
  const area = dentro;

  const hits = [...hitsOf(HOOK, frame, hookO), ...hitsOf(RAIN1, frame, r1O), ...hitsOf(RAIN2, frame, r2O)];
  const glow = hits.reduce((a, h) => Math.max(a, Math.exp(-h.age / 8)), 0);

  const stripes = Array.from({length: 10}, (_, i) => {
    const y0 = (i * HALF) / 10;
    const y1 = ((i + 1) * HALF) / 10;
    return polygon(cam, [[-PW, y0, 0], [PW, y0, 0], [PW, y1, 0], [-PW, y1, 0]]);
  });
  const box = polygon(cam, BOX);

  return (
    <AbsoluteFill>
      <svg width={1080} height={1920}>
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <radialGradient id="sky" cx="50%" cy="35%" r="70%">
            <stop offset="0" stopColor="#1A1A1A" />
            <stop offset="1" stopColor={C.bg} />
          </radialGradient>
        </defs>
        <rect width={1080} height={1920} fill="url(#sky)" />
        {stripes.map((p, i) => (p ? <polygon key={i} points={p} fill={i % 2 === 0 ? C.pitchA : C.pitchB} /> : null))}
        {area > 0 && box ? <polygon points={box} fill={C.gold} opacity={area * (0.12 + 0.06 * Math.sin(frame / 4))} /> : null}
        <path d={PITCH_LINES.map((l) => polyline(cam, l)).join('')} fill="none" stroke={C.ink} strokeOpacity={0.3} strokeWidth={2} />
        {area > 0 ? <path d={polyline(cam, BOX)} fill="none" stroke={C.gold} strokeWidth={4} opacity={area} /> : null}
        {(() => {
          const spot = project(cam, [0, 11, 0]);
          return spot ? <circle cx={spot.x} cy={spot.y} r={Math.max(2, 0.2 * spot.s)} fill={C.ink} opacity={0.4} /> : null;
        })()}

        <Layer cam={cam} launches={HOOK} frame={frame} o={{opacity: hookO, fuera: 0, dentro: 0}} idp="h" />
        <Layer cam={cam} launches={RAIN1} frame={frame} o={{opacity: r1O, fuera, dentro}} idp="a" />
        <Layer cam={cam} launches={RAIN2} frame={frame} o={{opacity: r2O, fuera: 0, dentro: 0}} idp="b" />

        <Net cam={cam} hits={hits} glow={glow} />
      </svg>
    </AbsoluteFill>
  );
};
