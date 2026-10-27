import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {C, DISPLAY, MONO} from '../theme';
import {SoccerBall} from './Ball';
import {clamp, smooth} from './fx';

const BALL_R = 82;
// La pelota hace de "O" en FERRO
const SLOT = {x: 760, y: 960};
const CENTER = {x: 540, y: 960};

// 0 – 4.3 s: presentación
export const Intro: React.FC = () => {
  const frame = useCurrentFrame();

  // 1) entra rodando y frena en el lugar de la "O"
  const roll = interpolate(frame, [0, 30], [0, 1], {...clamp, easing: Easing.bezier(0.15, 0.85, 0.3, 1)});
  const startX = -150;
  let bx = startX + (SLOT.x - startX) * roll;
  let by = SLOT.y;
  // rebotito al frenar
  by -= Math.max(0, Math.sin(interpolate(frame, [26, 40], [0, Math.PI], clamp))) * 26;
  // 2) al final viaja al centro y crece: la cámara "entra" en la pelota
  const toCenter = interpolate(frame, [100, 118], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  bx = bx + (CENTER.x - bx) * toCenter;
  by = by + (CENTER.y - by) * toCenter;
  const grow = interpolate(frame, [104, 118], [1, 4.15], {...clamp, easing: Easing.in(Easing.cubic)});
  // giro: termina en 0° (coincide con la pelota de la cancha)
  const rot = ((bx - CENTER.x) / BALL_R) * (180 / Math.PI);

  const presenta = smooth(frame, 6, 30, 38);
  const rival = smooth(frame, 34, 98, 104);
  const word = interpolate(frame, [36, 52], [0, 1], {...clamp, easing: Easing.bezier(0.22, 1, 0.36, 1)});
  const sub = smooth(frame, 54, 98, 104);
  const line = smooth(frame, 68, 98, 104);
  const hl = interpolate(frame, [76, 88], [0, 1], {...clamp, easing: Easing.bezier(0.22, 1, 0.36, 1)});
  const bgOut = interpolate(frame, [118, 130], [1, 0], clamp);

  return (
    <AbsoluteFill style={{opacity: bgOut}}>
      <AbsoluteFill style={{backgroundColor: C.bg}} />
      {/* Rayas Chaco, apenas visibles */}
      <AbsoluteFill
        style={{
          backgroundImage: `repeating-linear-gradient(115deg, rgba(245,245,240,0.035) 0px, rgba(245,245,240,0.035) 70px, transparent 70px, transparent 140px)`,
          backgroundPosition: `${frame * 1.5}px 0`,
        }}
      />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 50%, rgba(245,245,240,0.07), rgba(0,0,0,0) 55%)'}} />

      <div style={{position: 'absolute', top: 700, width: '100%', textAlign: 'center'}}>
        <div style={{...lineStyle(presenta), fontFamily: MONO, fontWeight: 700, fontSize: 32, letterSpacing: 12, color: C.ink}}>
          CHACO FOR EVER PRESENTA
        </div>
      </div>
      <div style={{position: 'absolute', top: 700, width: '100%', textAlign: 'center'}}>
        <div style={{...lineStyle(rival), fontFamily: MONO, fontWeight: 700, fontSize: 32, letterSpacing: 12, color: C.gold}}>
          PRÓXIMO RIVAL
        </div>
      </div>

      {/* FERR + pelota */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          width: SLOT.x - BALL_R - 14,
          top: SLOT.y - 125,
          textAlign: 'right',
          fontFamily: DISPLAY,
          fontSize: 250,
          lineHeight: 1,
          color: C.ink,
          clipPath: `inset(0 0 0 ${(1 - word) * 100}%)`,
          opacity: 1 - toCenter,
          transform: `translateX(${(1 - word) * 40}px)`,
        }}
      >
        FERR
      </div>

      <div style={{position: 'absolute', top: 1110, width: '100%', textAlign: 'center'}}>
        <div style={{...lineStyle(sub), fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 6, color: C.gray}}>
          EL PUNTERO · 1° · 65 PTS
        </div>
      </div>
      <div style={{position: 'absolute', top: 1200, width: '100%', textAlign: 'center', ...lineStyle(line)}}>
        <div style={{fontFamily: DISPLAY, fontSize: 92, lineHeight: 1.1, color: C.ink}}>SI NOS GANA,</div>
        <div style={{position: 'relative', display: 'inline-block', fontFamily: DISPLAY, fontSize: 92, lineHeight: 1.1, padding: '0 18px'}}>
          <div style={{position: 'absolute', inset: 0, background: C.gold, transform: `scaleX(${hl})`, transformOrigin: 'left'}} />
          <span style={{position: 'relative', color: hl > 0.5 ? C.bg : C.ink}}>SALE CAMPEÓN</span>
        </div>
      </div>

      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        <ellipse
          cx={bx + 8}
          cy={SLOT.y + BALL_R * 0.92}
          rx={BALL_R * 0.9}
          ry={BALL_R * 0.18}
          fill="#000"
          opacity={0.6 * (1 - toCenter)}
        />
        <g transform={`translate(${bx} ${by}) scale(${grow})`}>
          <SoccerBall r={BALL_R} rot={rot} id="intro-ball" />
        </g>
      </svg>
    </AbsoluteFill>
  );
};

const lineStyle = (p: number): React.CSSProperties => ({opacity: p, transform: `translateY(${(1 - p) * 24}px)`});
