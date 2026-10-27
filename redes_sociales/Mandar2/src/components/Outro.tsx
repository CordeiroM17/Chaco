import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {C, DISPLAY, MONO} from '../theme';
import {SoccerBall} from './Ball';
import {EASE_OUT, clamp, smooth} from './fx';

const BALL_R = 70;
const REST = {x: 540, y: 620};

// Cierre (frames locales, 0 = T.outro): "EL ARCO SE CERRÓ."
export const Outro: React.FC = () => {
  const frame = useCurrentFrame();

  const wipe = interpolate(frame, [0, 16], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const roll = interpolate(frame, [8, 40], [0, 1], {...clamp, easing: Easing.bezier(0.15, 0.85, 0.3, 1)});
  const bx = -170 + (REST.x + 170) * roll;
  const hop = Math.abs(Math.sin(interpolate(frame, [8, 40], [0, Math.PI * 2], clamp))) * interpolate(frame, [8, 40], [90, 0], clamp);
  const rot = ((bx - REST.x) / BALL_R) * (180 / Math.PI);

  const l1 = smooth(frame, 30, 999, 1000, 16);
  const l2 = interpolate(frame, [40, 56], [0, 1], {...clamp, easing: EASE_OUT});
  const sub = smooth(frame, 60, 999, 1000);
  const tail = smooth(frame, 72, 999, 1000);

  return (
    <AbsoluteFill style={{clipPath: `polygon(0 0, ${wipe * 230}% 0, ${wipe * 230 - 130}% 100%, 0 100%)`}}>
      <AbsoluteFill style={{backgroundColor: C.bg}} />
      <AbsoluteFill
        style={{
          backgroundImage: `repeating-linear-gradient(115deg, rgba(245,245,240,0.06) 0px, rgba(245,245,240,0.06) 70px, transparent 70px, transparent 140px)`,
          backgroundPosition: `${frame * 1.5}px 0`,
        }}
      />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, rgba(245,245,240,0.08), rgba(0,0,0,0) 55%)'}} />

      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        <ellipse cx={bx} cy={REST.y + BALL_R * 0.95} rx={BALL_R * (0.9 - hop / 400)} ry={BALL_R * 0.16} fill="#000" opacity={0.7} />
        <g transform={`translate(${bx} ${REST.y - hop})`}>
          <SoccerBall r={BALL_R} rot={rot} id="outro-ball" />
        </g>
      </svg>

      <div style={{position: 'absolute', top: 780, left: 0, right: 0, textAlign: 'center'}}>
        <div style={{opacity: l1, transform: `translateY(${(1 - l1) * 40}px)`, fontFamily: DISPLAY, fontSize: 170, lineHeight: 1.05, color: C.ink}}>
          EL ARCO
        </div>
        <div style={{position: 'relative', display: 'inline-block', marginTop: 10, padding: '8px 30px 0'}}>
          <div style={{position: 'absolute', inset: 0, background: C.gold, transform: `scaleX(${l2})`, transformOrigin: 'left'}} />
          <span style={{position: 'relative', fontFamily: DISPLAY, fontSize: 170, lineHeight: 1.05, color: C.bg, opacity: l2 > 0.4 ? 1 : 0}}>
            SE CERRÓ.
          </span>
        </div>
        <div style={{opacity: sub, marginTop: 44, fontFamily: MONO, fontWeight: 700, fontSize: 30, letterSpacing: 6, color: C.gray}}>
          CHACO FOR EVER · TEMPORADA 2026
        </div>
        <div style={{opacity: tail, marginTop: 30, fontFamily: MONO, fontWeight: 700, fontSize: 40, letterSpacing: 16, color: C.ink}}>
          VAMOS CHACO
        </div>
      </div>
    </AbsoluteFill>
  );
};
