import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {BALL_R, PASSES, ballAt, camAt, camBlur, camTransform} from '../camera';
import {CARDS, PITCH, XI, toPx} from '../data';
import {C, MONO, T} from '../theme';
import {SoccerBall} from './Ball';
import {clamp} from './fx';

const X0 = PITCH.x;
const Y0 = PITCH.y;
const X1 = PITCH.x + PITCH.w;
const Y1 = PITCH.y + PITCH.h;
const MX = PITCH.x + PITCH.w / 2;
const MY = PITCH.y + PITCH.h / 2;

// Medidas reglamentarias escaladas a 780 px = 68 m
const BOX_HW = 231;
const BOX_D = 189;
const GA_HW = 105;
const GA_D = 63;
const CIRCLE = 105;
const SPOT = 126;
const ARC_DX = 84;

const PITCH_PATHS = [
  `M${X0} ${Y0} H${X1} V${Y1} H${X0} Z`,
  `M${X0} ${MY} H${X1}`,
  `M${MX - CIRCLE} ${MY} a${CIRCLE} ${CIRCLE} 0 1 0 ${CIRCLE * 2} 0 a${CIRCLE} ${CIRCLE} 0 1 0 ${-CIRCLE * 2} 0`,
  `M${MX - BOX_HW} ${Y0} V${Y0 + BOX_D} H${MX + BOX_HW} V${Y0}`,
  `M${MX - GA_HW} ${Y0} V${Y0 + GA_D} H${MX + GA_HW} V${Y0}`,
  `M${MX - ARC_DX} ${Y0 + BOX_D} A${CIRCLE} ${CIRCLE} 0 0 0 ${MX + ARC_DX} ${Y0 + BOX_D}`,
  `M${MX - BOX_HW} ${Y1} V${Y1 - BOX_D} H${MX + BOX_HW} V${Y1}`,
  `M${MX - GA_HW} ${Y1} V${Y1 - GA_D} H${MX + GA_HW} V${Y1}`,
  `M${MX - ARC_DX} ${Y1 - BOX_D} A${CIRCLE} ${CIRCLE} 0 0 1 ${MX + ARC_DX} ${Y1 - BOX_D}`,
];

// Camiseta vista de frente, centrada en (0,0)
const SHIRT =
  'M-13 -24 L-27 -18 L-36 -4 L-26 3 L-21 -3 L-21 24 Q0 28 21 24 L21 -3 L26 3 L36 -4 L27 -18 L13 -24 Q0 -13 -13 -24 Z';

// Orden de aparición: de atrás para adelante
const DROP_ORDER = ['monetti', 'canto', 'tevez', 'osuna', 'kihm', 'obradovich', 'kabalin', 'hoyos', 'gonzalez', 'parisi', 'dening'];

const cardStart = (id: string) => {
  const i = CARDS.findIndex((c) => c.id === id);
  return i < 0 ? Infinity : T.cards[i].from - 4;
};

const Goal: React.FC<{y: number; dir: 1 | -1}> = ({y, dir}) => {
  const depth = 22 * dir;
  return (
    <g stroke={C.ink} fill="none">
      <path d={`M${MX - 36} ${y} V${y - depth} H${MX + 36} V${y}`} strokeOpacity={0.6} strokeWidth={3} />
      {Array.from({length: 9}).map((_, i) => (
        <line key={i} x1={MX - 36 + i * 9} x2={MX - 36 + i * 9} y1={y} y2={y - depth} strokeOpacity={0.18} strokeWidth={1} />
      ))}
      {[0.33, 0.66].map((k) => (
        <line key={k} x1={MX - 36} x2={MX + 36} y1={y - depth * k} y2={y - depth * k} strokeOpacity={0.18} strokeWidth={1} />
      ))}
    </g>
  );
};

export const World: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (frame < T.worldIn) return null;

  const cam = camAt(frame);
  const blur = camBlur(frame);
  // Nombres en la cancha: solo cuando la cámara está lejos
  const labels = interpolate(cam.s, [1.25, 1.8], [1, 0], clamp);
  // Durante la historia, los que no son del circuito quedan en segundo plano
  const story = interpolate(frame, [T.storyStart, T.storyStart + 20], [0, 1], clamp);
  const circuit = interpolate(frame, [T.circuit[0], T.circuit[0] + 20], [0, 1], clamp);

  const ball = ballAt(frame);
  const prev = [1, 2, 3].map((d) => ballAt(frame - d));
  const ballSpeed = Math.hypot(ball.x - prev[0].x, ball.y - prev[0].y);

  return (
    <AbsoluteFill
      style={{
        transformOrigin: '0 0',
        transform: camTransform(cam),
        filter: blur > 0.4 ? `blur(${blur.toFixed(2)}px)` : undefined,
      }}
    >
      <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{overflow: 'visible'}}>
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">
            <circle cx="14" cy="14" r="1.3" fill={C.ink} fillOpacity="0.07" />
          </pattern>
        </defs>

        <rect x={-1500} y={-1500} width={4080} height={4920} fill="url(#dots)" />

        {/* Césped oscuro a franjas */}
        {Array.from({length: 12}).map((_, i) => (
          <rect
            key={i}
            x={X0}
            y={Y0 + (i * PITCH.h) / 12}
            width={PITCH.w}
            height={PITCH.h / 12 + 0.5}
            fill={i % 2 === 0 ? C.pitchA : C.pitchB}
          />
        ))}

        <g fill="none" stroke={C.ink} strokeOpacity={0.3} strokeWidth={2.5}>
          {PITCH_PATHS.map((d, i) => (
            <path key={i} d={d} />
          ))}
        </g>
        {[Y0 + SPOT, MY, Y1 - SPOT].map((y) => (
          <circle key={y} cx={MX} cy={y} r={4} fill={C.ink} opacity={0.4} />
        ))}
        <Goal y={Y0} dir={1} />
        <Goal y={Y1} dir={-1} />

        {/* El circuito: la pelota deja una estela dorada */}
        {PASSES.map((p, i) => {
          if (frame < p.start) return null;
          const b = frame >= p.end ? p.to : ballAt(frame);
          const pulse = circuit > 0 ? 0.75 + 0.25 * Math.sin((frame - T.circuit[0]) / 5 + i) : 1;
          return (
            <g key={i} opacity={pulse}>
              <line
                x1={p.from.x}
                y1={p.from.y}
                x2={b.x}
                y2={b.y}
                stroke={C.gold}
                strokeWidth={4 + circuit * 2}
                strokeLinecap="round"
                strokeDasharray="2 12"
                filter="url(#glow)"
              />
            </g>
          );
        })}

        {/* Jugadores */}
        {XI.map((pl) => {
          const {x, y} = toPx(pl);
          const t0 = T.playersIn + DROP_ORDER.indexOf(pl.id) * 4;
          if (frame < t0) return null;
          const pop = spring({frame: frame - t0, fps, config: {damping: 16, stiffness: 150}});
          const lit = pl.threat === true && frame >= cardStart(pl.id);
          const litP = lit ? spring({frame: frame - cardStart(pl.id), fps, config: {damping: 200}}) : 0;
          const op = pl.threat ? 1 : 1 - story * 0.55;
          const color = lit ? C.gold : C.ink;
          return (
            <g key={pl.id} opacity={op}>
              <ellipse cx={x} cy={y + 30} rx={30 * pop} ry={7 * pop} fill="#000" opacity={0.7} />
              {lit ? (
                <circle
                  cx={x}
                  cy={y}
                  r={46 + ((frame - cardStart(pl.id)) % 40) * 1.2}
                  fill="none"
                  stroke={C.gold}
                  strokeWidth={2}
                  opacity={(1 - ((frame - cardStart(pl.id)) % 40) / 40) * 0.8}
                />
              ) : null}
              <g transform={`translate(${x} ${y - (1 - pop) * 40}) scale(${pop})`}>
                <path d={SHIRT} fill={lit ? C.gold : C.shirt} stroke={color} strokeWidth={2.5} strokeOpacity={lit ? 1 : 0.75} />
                <path d="M-13 -24 Q0 -13 13 -24" fill="none" stroke={lit ? C.bg : C.ink} strokeOpacity={0.6} strokeWidth={2} />
                <circle r={46} fill="none" stroke={C.gold} strokeWidth={3} opacity={litP} filter="url(#glow)" />
              </g>
              <text
                x={x}
                y={y + 56}
                fill={color}
                fontFamily={MONO}
                fontWeight={700}
                fontSize={19}
                letterSpacing={2}
                textAnchor="middle"
                opacity={labels * Math.min(1, pop * 1.5)}
              >
                {pl.name}
              </text>
            </g>
          );
        })}

        {/* Pelota: sombra, estela y altura en los pases aéreos */}
        <ellipse
          cx={ball.x + ball.h * 18}
          cy={ball.y + BALL_R * 0.8 + ball.h * 8}
          rx={BALL_R * (1 - ball.h * 0.25)}
          ry={BALL_R * 0.35}
          fill="#000"
          opacity={0.75 - ball.h * 0.35}
        />
        {ballSpeed > 2
          ? prev.map((p, i) => (
              <circle key={i} cx={p.x} cy={p.y - p.h * 70} r={BALL_R * (1 + p.h * 0.7)} fill={C.ink} opacity={0.18 - i * 0.05} />
            ))
          : null}
        <g transform={`translate(${ball.x} ${ball.y - ball.h * 70}) scale(${1 + ball.h * 0.7})`}>
          <SoccerBall r={BALL_R} rot={ball.rot} id="world-ball" />
        </g>
      </svg>
    </AbsoluteFill>
  );
};
