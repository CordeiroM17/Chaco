import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {SoccerBall} from './Ball';
import {EASE_OUT, clamp, smooth} from './fx';
import {C, DISPLAY, HANDLE, MONO} from './theme';

const BALL_R = 70;
const REST = {x: 540, y: 610};

// Cierre (frames locales, 0 = inicio del cierre). Mismo lenguaje que el del reel de Ferro:
// wipe con rayas, entra la pelota, la frase y la marca.
type Props = {linea1?: string; linea2?: string; resaltado?: string};

export const Cierre: React.FC<Props> = ({linea1 = 'DE ÚLTIMO', linea2 = 'A SALVADO.', resaltado = C.ink}) => {
  const frame = useCurrentFrame();

  const wipe = interpolate(frame, [0, 16], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});

  const roll = interpolate(frame, [8, 40], [0, 1], {...clamp, easing: Easing.bezier(0.15, 0.85, 0.3, 1)});
  const bx = 1250 + (REST.x - 1250) * roll;
  const hop = Math.abs(Math.sin(interpolate(frame, [8, 40], [0, Math.PI * 2], clamp))) * interpolate(frame, [8, 40], [90, 0], clamp);
  const by = REST.y - hop;
  const rot = ((bx - REST.x) / BALL_R) * (180 / Math.PI);

  const kicker = smooth(frame, 22, 999, 1000);
  const l1 = smooth(frame, 34, 999, 1000, 16);
  const l2 = interpolate(frame, [42, 58], [0, 1], {...clamp, easing: EASE_OUT});
  const tail = smooth(frame, 62, 999, 1000);

  return (
    <AbsoluteFill style={{clipPath: `polygon(0 0, ${wipe * 230}% 0, ${wipe * 230 - 130}% 100%, 0 100%)`}}>
      <AbsoluteFill style={{backgroundColor: C.bg}} />
      <AbsoluteFill
        style={{
          backgroundImage: `repeating-linear-gradient(115deg, rgba(245,245,245,0.06) 0px, rgba(245,245,245,0.06) 70px, transparent 70px, transparent 140px)`,
          backgroundPosition: `${frame * 1.5}px 0`,
        }}
      />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, rgba(245,245,245,0.08), rgba(0,0,0,0) 55%)'}} />

      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        <ellipse cx={bx} cy={REST.y + BALL_R * 0.95} rx={BALL_R * (0.9 - hop / 400)} ry={BALL_R * 0.16} fill="#000" opacity={0.7} />
        <g transform={`translate(${bx} ${by})`}>
          <SoccerBall r={BALL_R} rot={rot} id="cierre-ball" />
        </g>
      </svg>

      <div style={{position: 'absolute', top: 760, left: 0, right: 0, textAlign: 'center'}}>
        <div style={{opacity: kicker, transform: `translateY(${(1 - kicker) * 20}px)`, fontFamily: MONO, fontWeight: 700, fontSize: 34, letterSpacing: 6, color: C.gray}}>
          TEMPORADA <span style={{color: C.ink}}>2026</span>
        </div>
        <div style={{height: 2, background: 'rgba(245,245,245,0.2)', margin: '36px 140px', transform: `scaleX(${kicker})`}} />
        <div style={{opacity: l1, transform: `translateY(${(1 - l1) * 40}px)`, fontFamily: DISPLAY, fontSize: 124, lineHeight: 1.05, color: C.ink}}>
          {linea1}
        </div>
        <div style={{position: 'relative', display: 'inline-block', marginTop: 10, padding: '8px 30px 0'}}>
          <div style={{position: 'absolute', inset: 0, background: resaltado, transform: `scaleX(${l2})`, transformOrigin: 'left'}} />
          <span style={{position: 'relative', fontFamily: DISPLAY, fontSize: 124, lineHeight: 1.05, color: C.bg, opacity: l2 > 0.4 ? 1 : 0}}>
            {linea2}
          </span>
        </div>
        <div style={{opacity: tail, marginTop: 56, fontFamily: MONO, fontWeight: 700, fontSize: 38, letterSpacing: 16, color: C.gold}}>
          VAMOS CHACO
        </div>
        <div style={{opacity: tail, marginTop: 120, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16}}>
          <div style={{display: 'flex', width: 46, height: 30}}>
            {[0, 1, 2, 3, 4].map((i) => (
              <div key={i} style={{flex: 1, background: i % 2 === 0 ? '#FFFFFF' : C.bg}} />
            ))}
          </div>
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
