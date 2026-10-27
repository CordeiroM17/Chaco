import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {C, DISPLAY, HANDLE, MONO} from '../theme';
import {Rayas} from './Overlays';
import {SoccerBall} from './Ball';
import {EASE_OUT, clamp, smooth} from './fx';

const BALL_R = 70;
const REST = {x: 540, y: 610};

// Cierre (frames locales, 0 = T.outro): rayas Chaco, entra la pelota y la frase final
export const Outro: React.FC = () => {
  const frame = useCurrentFrame();

  const wipe = interpolate(frame, [0, 16], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});

  // La pelota entra rodando desde la derecha, pica y queda quieta arriba del texto
  const roll = interpolate(frame, [8, 40], [0, 1], {...clamp, easing: Easing.bezier(0.15, 0.85, 0.3, 1)});
  const bx = 1250 + (REST.x - 1250) * roll;
  const hop = Math.abs(Math.sin(interpolate(frame, [8, 40], [0, Math.PI * 2], clamp))) * interpolate(frame, [8, 40], [90, 0], clamp);
  const by = REST.y - hop;
  const rot = ((bx - REST.x) / BALL_R) * (180 / Math.PI);

  const vs = smooth(frame, 22, 999, 1000);
  const l1 = smooth(frame, 34, 999, 1000, 16);
  const l2 = interpolate(frame, [42, 58], [0, 1], {...clamp, easing: EASE_OUT});
  const tail = smooth(frame, 62, 999, 1000);

  return (
    <AbsoluteFill style={{clipPath: `polygon(0 0, ${wipe * 230}% 0, ${wipe * 230 - 130}% 100%, 0 100%)`}}>
      <AbsoluteFill style={{backgroundColor: C.bg}} />
      {/* Rayas blanco y negro, oscuras */}
      <AbsoluteFill
        style={{
          backgroundImage: `repeating-linear-gradient(115deg, rgba(245,245,240,0.06) 0px, rgba(245,245,240,0.06) 70px, transparent 70px, transparent 140px)`,
          backgroundPosition: `${frame * 1.5}px 0`,
        }}
      />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, rgba(245,245,240,0.08), rgba(0,0,0,0) 55%)'}} />

      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        <ellipse cx={bx} cy={REST.y + BALL_R * 0.95} rx={BALL_R * (0.9 - hop / 400)} ry={BALL_R * 0.16} fill="#000" opacity={0.7} />
        <g transform={`translate(${bx} ${by})`}>
          <SoccerBall r={BALL_R} rot={rot} id="outro-ball" />
        </g>
      </svg>

      <div style={{position: 'absolute', top: 760, left: 0, right: 0, textAlign: 'center'}}>
        <div style={{opacity: vs, transform: `translateY(${(1 - vs) * 20}px)`, fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 6, color: C.gray}}>
          FERRO <span style={{color: C.gold}}>vs</span> <span style={{color: C.ink}}>CHACO FOR EVER</span>
        </div>
        <div style={{height: 2, background: 'rgba(245,245,240,0.2)', margin: '36px 140px', transform: `scaleX(${vs})`}} />
        <div style={{opacity: l1, transform: `translateY(${(1 - l1) * 40}px)`, fontFamily: DISPLAY, fontSize: 112, lineHeight: 1.05, color: C.ink}}>
          QUE FESTEJEN
        </div>
        <div style={{position: 'relative', display: 'inline-block', marginTop: 10, padding: '8px 30px 0'}}>
          <div style={{position: 'absolute', inset: 0, background: C.ink, transform: `scaleX(${l2})`, transformOrigin: 'left'}} />
          <span style={{position: 'relative', fontFamily: DISPLAY, fontSize: 112, lineHeight: 1.05, color: C.bg, opacity: l2 > 0.4 ? 1 : 0}}>
            OTRO DÍA.
          </span>
        </div>
        <div style={{opacity: tail, marginTop: 56, fontFamily: MONO, fontWeight: 700, fontSize: 38, letterSpacing: 16, color: C.gold}}>
          VAMOS CHACO
        </div>
        <div style={{opacity: tail, marginTop: 120, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16}}>
          <Rayas />
          <div style={{textAlign: 'left'}}>
            <div style={{fontFamily: DISPLAY, fontSize: 26, letterSpacing: 2, color: C.ink, lineHeight: 1.05}}>CHACO FOR EVER</div>
            <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 15, letterSpacing: 6, color: C.gold}}>ESTADÍSTICAS</div>
          </div>
        </div>
        <div style={{opacity: tail, marginTop: 18, fontFamily: MONO, fontWeight: 600, fontSize: 30, color: C.ink}}>{HANDLE}</div>
      </div>
    </AbsoluteFill>
  );
};
