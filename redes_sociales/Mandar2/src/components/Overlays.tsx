import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {AFTER, BEFORE, Launch, RAIN1, RAIN2, STATS, currentMatch} from '../schedule';
import {MATCHES} from '../shots';
import {C, DISPLAY, MONO, T} from '../theme';
import {EASE_OUT, center, clamp, rise, smooth} from './fx';

const fmtDate = (d: string) => `${d.slice(8, 10)}/${d.slice(5, 7)}`;
const big = (size: number, color: string = C.ink): React.CSSProperties => ({fontFamily: DISPLAY, fontSize: size, lineHeight: 1.05, color});
const mono = (size: number, color: string = C.ink, bold = true): React.CSSProperties => ({
  fontFamily: MONO,
  fontWeight: bold ? 700 : 400,
  fontSize: size,
  color,
});

// Gancho: después del gol de tiro libre
export const HookText: React.FC = () => {
  const frame = useCurrentFrame();
  const [a, b] = T.hookText;
  if (frame < a || frame > b) return null;
  const l1 = smooth(frame, a, b - 8, b);
  const l2 = smooth(frame, a + 8, b - 8, b);
  const l3 = smooth(frame, a + 26, b - 8, b);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(5,5,5,0.85) 0%, rgba(5,5,5,0) 38%)', opacity: l1}} />
      <div style={{...center, top: 200, ...rise(l1)}}>
        <div style={big(120)}>NOS PATEARON</div>
      </div>
      <div style={{...center, top: 330, ...rise(l2)}}>
        <div style={big(160, C.gold)}>{STATS.shots} VECES</div>
      </div>
      <div style={{...center, top: 520, ...rise(l3, 16)}}>
        <div style={{...mono(32), letterSpacing: 8}}>ACÁ ESTÁN TODAS ↓</div>
      </div>
    </AbsoluteFill>
  );
};

const Counters: React.FC<{launches: Launch[]; frame: number; opacity: number}> = ({launches, frame, opacity}) => {
  let shots = 0;
  let goals = 0;
  for (const l of launches) {
    if (l.t0 <= frame) shots++;
    if (l.shot.kind === 'g' && l.t0 + l.dur <= frame) goals++;
  }
  const cur = currentMatch(launches, frame);
  // "golpe" en el contador de goles cada vez que entra uno
  const lastGoal = launches.filter((l) => l.shot.kind === 'g' && l.t0 + l.dur <= frame).pop();
  const bump = lastGoal ? interpolate(frame - (lastGoal.t0 + lastGoal.dur), [0, 8], [1.25, 1], clamp) : 1;
  return (
    <div style={{...center, top: 150, opacity}}>
      <div style={{display: 'flex', justifyContent: 'center', gap: 90}}>
        <div>
          <div style={big(150)}>{shots}</div>
          <div style={{...mono(24, C.gray), letterSpacing: 6}}>REMATES</div>
        </div>
        <div style={{transform: `scale(${bump})`}}>
          <div style={big(150, C.gold)}>{goals}</div>
          <div style={{...mono(24, C.gold), letterSpacing: 6}}>GOLES</div>
        </div>
      </div>
      {cur ? (
        <div style={{marginTop: 22, display: 'inline-block', border: `2px solid rgba(245,245,240,0.25)`, padding: '6px 18px', ...mono(24)}}>
          {fmtDate(cur.shot.date)} · vs {cur.shot.rival}
        </div>
      ) : null}
    </div>
  );
};

// HUD de la primera lluvia
export const Rain1Hud: React.FC = () => {
  const frame = useCurrentFrame();
  const o = smooth(frame, T.rain1[0] - 4, T.reveal[0] - 6, T.reveal[0] + 4);
  if (o <= 0) return null;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(5,5,5,0.8) 0%, rgba(5,5,5,0) 30%)', opacity: o}} />
      <Counters launches={RAIN1} frame={frame} opacity={o} />
    </AbsoluteFill>
  );
};

// Dónde entraron
export const Reveal: React.FC = () => {
  const frame = useCurrentFrame();
  const [a, b] = T.reveal;
  if (frame < a || frame > b) return null;
  const l1 = smooth(frame, a + 4, 566, 574);
  const l2 = smooth(frame, 578, b - 8, b);
  const note = smooth(frame, a + 10, b - 8, b);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(5,5,5,0.85) 0%, rgba(5,5,5,0) 30%)'}} />
      <div style={{...center, top: 170, ...rise(l1)}}>
        <div style={big(150, C.gold)}>
          {STATS.inBox} DE {STATS.goals}
        </div>
        <div style={{...mono(34), marginTop: 6}}>goles, desde adentro del área</div>
      </div>
      <div style={{...center, top: 170, ...rise(l2)}}>
        <div style={big(150, C.ink)}>{STATS.headers} DE CABEZA</div>
        <div style={{...mono(34, C.gold), marginTop: 6}}>el juego aéreo nos costó</div>
      </div>
      <div style={{...center, top: 1580, opacity: note * 0.8}}>
        <div style={mono(20, C.gray, false)}>
          {STATS.goals} de los {STATS.totalGA} goles recibidos tienen el remate registrado
        </div>
      </div>
    </AbsoluteFill>
  );
};

// El giro de la historia
export const Turn: React.FC = () => {
  const frame = useCurrentFrame();
  const [a, b] = T.turn;
  if (frame < a || frame > T.chart[1]) return null;
  const dim = interpolate(frame, [a, a + 12], [0, 0.92], {...clamp, easing: EASE_OUT});
  const t = smooth(frame, a + 6, b - 4, b + 4);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{backgroundColor: C.bg, opacity: Math.min(dim, interpolate(frame, [T.chart[1] - 12, T.chart[1]], [0.92, 0], clamp))}} />
      <div style={{...center, top: 800, ...rise(t)}}>
        <div style={big(150)}>PERO</div>
        <div style={big(150, C.gold)}>DESDE AGOSTO...</div>
      </div>
    </AbsoluteFill>
  );
};

// Goles en contra partido a partido: antes y después del 2 de agosto
export const Chart: React.FC = () => {
  const frame = useCurrentFrame();
  const [a, b] = T.chart;
  if (frame < a || frame > b) return null;
  const all = smooth(frame, a + 4, b - 10, b);
  const n = MATCHES.length;
  const left = 90;
  const width = 900;
  const gap = 6;
  const bw = (width - gap * (n - 1)) / n;
  const base = 1040;
  const unit = 95;
  const split = BEFORE.length;
  const numA = smooth(frame, a + 40, b - 10, b);
  const numB = smooth(frame, a + 54, b - 10, b);
  const vA = (STATS.beforeGA / STATS.beforeGames).toFixed(2);
  const vB = interpolate(frame, [a + 54, a + 76], [STATS.beforeGA / STATS.beforeGames, STATS.afterGA / STATS.afterGames], {
    ...clamp,
    easing: Easing.out(Easing.cubic),
  }).toFixed(2);
  return (
    <AbsoluteFill style={{opacity: all}}>
      <div style={{...center, top: 560}}>
        <div style={{...mono(26, C.gray), letterSpacing: 6}}>GOLES EN CONTRA, PARTIDO A PARTIDO</div>
      </div>
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        {MATCHES.map((m, i) => {
          const g = interpolate(frame, [a + 6 + i * 1.6, a + 18 + i * 1.6], [0, 1], {...clamp, easing: EASE_OUT});
          const x = left + i * (bw + gap);
          const h = m[2] * unit * g;
          const late = i >= split;
          return (
            <g key={m[0]}>
              {m[2] > 0 ? (
                <rect x={x} y={base - h} width={bw} height={h} fill={late ? C.gold : C.ink} opacity={late ? 1 : 0.85} />
              ) : (
                <circle cx={x + bw / 2} cy={base - 14} r={9 * g} fill="none" stroke={late ? C.gold : C.gray} strokeWidth={3} />
              )}
            </g>
          );
        })}
        <line x1={left - 10} x2={left + width + 10} y1={base} y2={base} stroke={C.ink} strokeOpacity={0.4} strokeWidth={2} />
        {(() => {
          const x = left + split * (bw + gap) - gap / 2;
          const p = interpolate(frame, [a + 30, a + 44], [0, 1], {...clamp, easing: EASE_OUT});
          return (
            <g opacity={p}>
              <line x1={x} x2={x} y1={base + 30} y2={base - 330 * p} stroke={C.gold} strokeWidth={3} strokeDasharray="10 8" />
              <text x={x} y={base - 345} fill={C.gold} fontFamily={MONO} fontWeight={700} fontSize={24} textAnchor="middle">
                2/8
              </text>
            </g>
          );
        })()}
        <text x={left} y={base + 50} fill={C.gray} fontFamily={MONO} fontSize={20}>
          ○ = valla invicta
        </text>
      </svg>
      <div style={{position: 'absolute', top: 1150, left: 90, right: 90, display: 'flex', justifyContent: 'space-between'}}>
        <div style={{textAlign: 'left', ...rise(numA, 20)}}>
          <div style={{...mono(24, C.gray), letterSpacing: 4}}>ANTES</div>
          <div style={big(180)}>{vA}</div>
          <div style={mono(22, C.gray, false)}>goles por partido</div>
        </div>
        <div style={{textAlign: 'right', ...rise(numB, 20)}}>
          <div style={{...mono(24, C.gold), letterSpacing: 4}}>DESDE AGOSTO</div>
          <div style={big(180, C.gold)}>{vB}</div>
          <div style={mono(22, C.gray, false)}>goles por partido</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Segunda lluvia: nos siguen pateando, pero no entra
export const Rain2Hud: React.FC = () => {
  const frame = useCurrentFrame();
  const [a] = T.rain2;
  const o = smooth(frame, a - 4, T.clean[0] - 6, T.clean[0] + 2);
  if (o <= 0) return null;
  const l1 = smooth(frame, a + 2, 846, 854);
  const l2 = smooth(frame, 856, T.clean[0] - 6, T.clean[0] + 2);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(5,5,5,0.85) 0%, rgba(5,5,5,0) 34%)', opacity: o}} />
      <div style={{...center, top: 170, ...rise(l1)}}>
        <div style={big(120)}>NOS SIGUEN PATEANDO</div>
        <div style={{...mono(30, C.gray), marginTop: 8}}>{Math.round(STATS.lateShots / (STATS.afterGames - 1))} remates por partido, igual que antes</div>
      </div>
      <div style={{...center, top: 170, ...rise(l2)}}>
        <div style={big(150, C.gold)}>PERO NO ENTRA.</div>
      </div>
      <div style={{position: 'absolute', top: 1540, left: 0, right: 0, opacity: o}}>
        <MiniCounter launches={RAIN2} frame={frame} />
      </div>
    </AbsoluteFill>
  );
};

const MiniCounter: React.FC<{launches: Launch[]; frame: number}> = ({launches, frame}) => {
  const shots = launches.filter((l) => l.t0 <= frame).length;
  const goals = launches.filter((l) => l.shot.kind === 'g' && l.t0 + l.dur <= frame).length;
  return (
    <div style={{display: 'flex', justifyContent: 'center', gap: 60, ...mono(30)}}>
      <span>
        {shots} <span style={{color: C.gray}}>REMATES</span>
      </span>
      <span style={{color: C.gold}}>
        {goals} <span>GOLES</span>
      </span>
    </div>
  );
};

// 6 vallas invictas
export const Clean: React.FC = () => {
  const frame = useCurrentFrame();
  const [a, b] = T.clean;
  if (frame < a || frame > b + 4) return null;
  const dim = interpolate(frame, [a, a + 10], [0, 0.85], {...clamp, easing: EASE_OUT});
  const n = smooth(frame, a + 4, b + 40, b + 41);
  const t = smooth(frame, a + 14, b + 40, b + 41);
  const count = Math.round(interpolate(frame, [a + 4, a + 26], [0, STATS.afterClean], {...clamp, easing: Easing.out(Easing.cubic)}));
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{backgroundColor: C.bg, opacity: dim}} />
      <div style={{...center, top: 560, opacity: n, transform: `scale(${0.85 + 0.15 * n})`}}>
        <div style={{...big(440, C.gold), lineHeight: 1}}>{count}</div>
      </div>
      <div style={{...center, top: 1030, ...rise(t)}}>
        <div style={big(130)}>VALLAS INVICTAS</div>
        <div style={{...mono(32, C.gray), marginTop: 10}}>
          en {AFTER.length} partidos desde agosto
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Marca fija arriba
export const Brand: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [T.rain1[0], T.rain1[0] + 14, T.outro, T.outro + 10], [0, 1, 1, 0], clamp);
  if (o <= 0) return null;
  return (
    <AbsoluteFill style={{opacity: o * 0.85}}>
      <div style={{position: 'absolute', top: 70, left: 60, display: 'flex', alignItems: 'center', gap: 14}}>
        <div
          style={{
            width: 30,
            height: 30,
            border: `2px solid ${C.ink}`,
            backgroundImage: `repeating-linear-gradient(90deg, ${C.ink} 0px, ${C.ink} 5px, ${C.bg} 5px, ${C.bg} 10px)`,
          }}
        />
        <span style={{...mono(20), letterSpacing: 4}}>CHACO FOR EVER</span>
      </div>
      <div style={{position: 'absolute', top: 75, right: 60, ...mono(20, C.gray, false), letterSpacing: 4}}>TEMPORADA 2026</div>
    </AbsoluteFill>
  );
};
