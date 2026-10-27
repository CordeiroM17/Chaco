import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {C} from './theme';

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const EASE_OUT = Easing.bezier(0.22, 1, 0.36, 1);

// Entra en `start` (14 frames, suave) y sale entre `outStart` y `outEnd`
export const smooth = (frame: number, start: number, outStart: number, outEnd: number, inLen = 14) => {
  const i = interpolate(frame, [start, start + inLen], [0, 1], {...clamp, easing: EASE_OUT});
  const o = interpolate(frame, [outStart, outEnd], [1, 0], {...clamp, easing: Easing.in(Easing.cubic)});
  return Math.min(i, o);
};

// Grano de película suave + viñeta
export const FilmLayer: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <AbsoluteFill
        style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 50%, rgba(0,0,0,0.7) 100%)'}}
      />
      <AbsoluteFill style={{opacity: 0.08, mixBlendMode: 'screen'}}>
        <svg width="100%" height="100%">
          <filter id="grain">
            <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={frame % 24} stitchTiles="stitch" />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width="100%" height="100%" filter="url(#grain)" />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Destello blanco puntual
export const Flash: React.FC<{at: number; len?: number; max?: number}> = ({at, len = 8, max = 0.9}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [at - 2, at, at + len], [0, max, 0], clamp);
  if (o <= 0) return null;
  return <AbsoluteFill style={{backgroundColor: C.ink, opacity: o, pointerEvents: 'none'}} />;
};

export const rise = (p: number, d = 30): React.CSSProperties => ({opacity: p, transform: `translateY(${(1 - p) * d}px)`});

export const center: React.CSSProperties = {position: 'absolute', left: 0, right: 0, textAlign: 'center'};
