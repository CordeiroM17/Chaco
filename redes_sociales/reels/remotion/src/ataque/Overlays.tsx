import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {EASE_OUT, center, clamp, rise, smooth} from '../fx';
import {BEFORE, Launch, RAIN1, RAIN2, STATS, currentMatch} from './schedule';
import {MATCHES} from './shots';
import {C, DISPLAY, HANDLE, MONO, NUM, T} from './tema';

const fmtDate = (d: string) => `${d.slice(8, 10)}/${d.slice(5, 7)}`;
const coma = (v: number, dec = 2) => v.toFixed(dec).replace('.', ',');
const big = (size: number, color: string = C.ink): React.CSSProperties => ({fontFamily: DISPLAY, fontSize: size, lineHeight: 1.05, color});
const num = (size: number, color: string = C.ink): React.CSSProperties => ({fontFamily: NUM, fontSize: size, lineHeight: 1, color});
const txt = (size: number, color: string = C.ink, peso = 700): React.CSSProperties => ({
  fontFamily: MONO,
  fontWeight: peso,
  fontSize: size,
  color,
});

// Gancho: después del gol de afuera
export const HookText: React.FC = () => {
  const frame = useCurrentFrame();
  const [a, b] = T.hookText;
  if (frame < a || frame > b) return null;
  const l1 = smooth(frame, a, b - 8, b);
  const l2 = smooth(frame, a + 8, b - 8, b);
  const l3 = smooth(frame, a + 26, b - 8, b);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(14,14,14,0.88) 0%, rgba(14,14,14,0) 38%)', opacity: l1}} />
      <div style={{...center, top: 190, ...rise(l1)}}>
        <div style={big(104)}>PATEAMOS</div>
      </div>
      <div style={{...center, top: 300, ...rise(l2)}}>
        <div style={big(150, C.gold)}>{STATS.shots} VECES</div>
      </div>
      <div style={{...center, top: 490, ...rise(l3, 16)}}>
        <div style={{...txt(30), letterSpacing: 8}}>ACÁ ESTÁN TODAS ↓</div>
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
  const lastGoal = launches.filter((l) => l.shot.kind === 'g' && l.t0 + l.dur <= frame).pop();
  const bump = lastGoal ? interpolate(frame - (lastGoal.t0 + lastGoal.dur), [0, 8], [1.25, 1], clamp) : 1;
  return (
    <div style={{...center, top: 150, opacity}}>
      <div style={{display: 'flex', justifyContent: 'center', gap: 90}}>
        <div>
          <div style={num(150)}>{shots}</div>
          <div style={{...txt(22, C.gray), letterSpacing: 6, marginTop: 8}}>REMATES</div>
        </div>
        <div style={{transform: `scale(${bump})`}}>
          <div style={num(150, C.gold)}>{goals}</div>
          <div style={{...txt(22, C.gold), letterSpacing: 6, marginTop: 8}}>GOLES</div>
        </div>
      </div>
      {cur ? (
        <div style={{marginTop: 22, display: 'inline-block', border: `2px solid rgba(245,245,245,0.25)`, padding: '6px 18px', ...txt(22)}}>
          {fmtDate(cur.shot.date)} · vs {cur.shot.rival}
        </div>
      ) : null}
    </div>
  );
};

export const Rain1Hud: React.FC = () => {
  const frame = useCurrentFrame();
  const o = smooth(frame, T.rain1[0] - 4, T.reveal[0] - 6, T.reveal[0] + 4);
  if (o <= 0) return null;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(14,14,14,0.82) 0%, rgba(14,14,14,0) 30%)', opacity: o}} />
      <Counters launches={RAIN1} frame={frame} opacity={o} />
    </AbsoluteFill>
  );
};

// Afuera vs adentro
export const Reveal: React.FC = () => {
  const frame = useCurrentFrame();
  const [a, b] = T.reveal;
  const s = T.revealSplit;
  if (frame < a || frame > b) return null;
  const l1 = smooth(frame, a + 4, s - 8, s);
  const l1b = smooth(frame, a + 22, s - 8, s);
  const l2 = smooth(frame, s + 2, b - 8, b);
  const l2b = smooth(frame, s + 20, b - 8, b);
  const note = smooth(frame, a + 10, b - 8, b);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(14,14,14,0.88) 0%, rgba(14,14,14,0) 30%)'}} />
      <div style={{...center, top: 160}}>
        <div style={{...big(118), ...rise(l1)}}>{STATS.out} DE AFUERA</div>
        <div style={{...txt(40, C.ink, 600), marginTop: 14, ...rise(l1b, 16)}}>
          solo <span style={{color: C.gold, fontWeight: 700}}>{STATS.outGoals}</span> fueron gol
        </div>
      </div>
      <div style={{...center, top: 160}}>
        <div style={{...big(118), ...rise(l2)}}>{STATS.in} DE ADENTRO</div>
        <div style={{...txt(40, C.ink, 600), marginTop: 14, ...rise(l2b, 16)}}>
          <span style={{color: C.gold, fontWeight: 700}}>{STATS.inGoals}</span> fueron gol
        </div>
      </div>
      <div style={{...center, top: 1540, opacity: note * 0.8}}>
        <div style={txt(20, C.gray, 400)}>
          {STATS.goals} de los {STATS.totalGF} goles tienen el remate registrado (5 partidos sin datos)
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
        <div style={big(130)}>Y DESDE</div>
        <div style={big(130, C.gold)}>AGOSTO...</div>
      </div>
    </AbsoluteFill>
  );
};

// Goles a favor partido a partido: antes y después del 2 de agosto
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
  const pA = STATS.beforeGF / STATS.beforeGames;
  const pB = STATS.afterGF / STATS.afterGames;
  const vB = interpolate(frame, [a + 54, a + 76], [pA, pB], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{opacity: all}}>
      <div style={{...center, top: 560}}>
        <div style={{...txt(24, C.gray), letterSpacing: 6}}>GOLES A FAVOR, PARTIDO A PARTIDO</div>
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
                <circle cx={x + bw / 2} cy={base - 14} r={8 * g} fill="none" stroke={late ? C.gold : C.gray} strokeWidth={3} />
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
          ○ = no hicimos gol
        </text>
      </svg>
      <div style={{position: 'absolute', top: 1150, left: 90, right: 90, display: 'flex', justifyContent: 'space-between'}}>
        <div style={{textAlign: 'left', ...rise(numA, 20)}}>
          <div style={{...txt(22, C.gray), letterSpacing: 4}}>ANTES</div>
          <div style={num(170)}>{coma(pA)}</div>
          <div style={txt(22, C.gray, 400)}>goles por partido</div>
        </div>
        <div style={{textAlign: 'right', ...rise(numB, 20)}}>
          <div style={{...txt(22, C.gold), letterSpacing: 4}}>DESDE AGOSTO</div>
          <div style={num(170, C.gold)}>{coma(vB)}</div>
          <div style={txt(22, C.gray, 400)}>goles por partido</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Segunda lluvia: pateamos más... pero seguimos de afuera
export const Rain2Hud: React.FC = () => {
  const frame = useCurrentFrame();
  const [a] = T.rain2;
  const o = smooth(frame, a - 4, T.ratio[0] - 6, T.ratio[0] + 2);
  if (o <= 0) return null;
  const mid = Math.round((T.rain2[0] + T.rain2[1]) / 2);
  const l1 = smooth(frame, a + 2, mid - 8, mid);
  const l2 = smooth(frame, mid + 2, T.ratio[0] - 6, T.ratio[0] + 2);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(14,14,14,0.88) 0%, rgba(14,14,14,0) 34%)', opacity: o}} />
      <div style={{...center, top: 170, ...rise(l1)}}>
        <div style={big(112)}>PATEAMOS MÁS</div>
        <div style={{...txt(32, C.gray, 600), marginTop: 10}}>
          de {Math.round(STATS.beforeShotsPG)} a {Math.round(STATS.lateShotsPG)} remates por partido
        </div>
      </div>
      <div style={{...center, top: 170, ...rise(l2)}}>
        <div style={big(96)}>PERO SEGUIMOS</div>
        <div style={big(96, C.gold)}>DE AFUERA</div>
        <div style={{...txt(32, C.gray, 600), marginTop: 10}}>
          {STATS.lateOut} de {STATS.lateShots} remates
        </div>
      </div>
      <div style={{position: 'absolute', top: 1520, left: 0, right: 0, opacity: o}}>
        <MiniCounter launches={RAIN2} frame={frame} />
      </div>
    </AbsoluteFill>
  );
};

const MiniCounter: React.FC<{launches: Launch[]; frame: number}> = ({launches, frame}) => {
  const shots = launches.filter((l) => l.t0 <= frame).length;
  const goals = launches.filter((l) => l.shot.kind === 'g' && l.t0 + l.dur <= frame).length;
  return (
    <div style={{display: 'flex', justifyContent: 'center', gap: 60, ...txt(30)}}>
      <span>
        {shots} <span style={{color: C.gray}}>REMATES</span>
      </span>
      <span style={{color: C.gold}}>{goals} GOLES</span>
    </div>
  );
};

// El dato que lo resume: adentro 1 de cada 6, afuera 1 de cada 86
export const Ratio: React.FC = () => {
  const frame = useCurrentFrame();
  const [a, b] = T.ratio;
  if (frame < a || frame > b + 4) return null;
  const dim = interpolate(frame, [a, a + 10], [0, 0.9], {...clamp, easing: EASE_OUT});
  const r1 = smooth(frame, a + 4, b + 40, b + 41);
  const r2 = smooth(frame, a + 18, b + 40, b + 41);
  const fila = (lab: string, n: number, color: string, p: number) => (
    <div style={{...rise(p, 30), marginBottom: 70}}>
      <div style={{...txt(30, C.gray), letterSpacing: 10}}>{lab}</div>
      <div style={{display: 'flex', justifyContent: 'center', alignItems: 'baseline', gap: 26, marginTop: 6}}>
        <span style={big(76, color)}>1 DE CADA</span>
        <span style={num(230, color)}>{n}</span>
      </div>
      <div style={{...txt(28, C.gray, 400)}}>remates es gol</div>
    </div>
  );
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{backgroundColor: C.bg, opacity: dim}} />
      <div style={{...center, top: 560}}>
        {fila('DESDE ADENTRO', Math.round(STATS.in / STATS.inGoals), C.gold, r1)}
        {fila('DESDE AFUERA', Math.round(STATS.out / STATS.outGoals), C.ink, r2)}
      </div>
    </AbsoluteFill>
  );
};

// Marca fija (la de las placas)
export const Brand: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [T.rain1[0], T.rain1[0] + 14, T.outro, T.outro + 10], [0, 1, 1, 0], clamp);
  if (o <= 0) return null;
  return (
    <AbsoluteFill style={{opacity: o}}>
      <div style={{position: 'absolute', top: 64, left: 60, display: 'flex', alignItems: 'center', gap: 16}}>
        <div style={{display: 'flex', width: 46, height: 30}}>
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={i} style={{flex: 1, background: i % 2 === 0 ? '#FFFFFF' : C.bg}} />
          ))}
        </div>
        <div>
          <div style={{fontFamily: DISPLAY, fontSize: 24, letterSpacing: 2, color: C.ink, lineHeight: 1.05}}>CHACO FOR EVER</div>
          <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 14, letterSpacing: 6, color: C.gold}}>ESTADÍSTICAS</div>
        </div>
      </div>
      <div style={{position: 'absolute', top: 74, right: 60, ...txt(18, C.gray), letterSpacing: 4}}>TEMPORADA 2026</div>
      <div style={{position: 'absolute', top: 1596, left: 60, display: 'flex', alignItems: 'center', gap: 14}}>
        <div style={{width: 40, height: 4, background: C.gold}} />
        <span style={{...txt(22, C.ink, 600), letterSpacing: 1}}>{HANDLE}</span>
      </div>
    </AbsoluteFill>
  );
};
