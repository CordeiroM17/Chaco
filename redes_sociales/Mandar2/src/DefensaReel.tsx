import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {Flash, FilmLayer} from './components/fx';
import {Outro} from './components/Outro';
import {Brand, Chart, Clean, HookText, Rain1Hud, Rain2Hud, Reveal, Turn} from './components/Overlays';
import {Scene3D} from './components/Scene3D';
import {C, DURATION, T} from './theme';

// 1080x1920 · 30 fps · 36 s
// 0 s    vista del arquero: un tiro libre al ángulo. "NOS PATEARON 279 VECES"
// 3.7 s  los 279 remates en orden, cada vez más rápido; la cámara orbita hasta la vista aérea
// 16.7 s dónde entraron: 20 de 26 desde el área, 6 de cabeza
// 21.3 s "PERO DESDE AGOSTO..." goles en contra partido a partido: 1.24 → 0.38
// 26.5 s los 70 remates desde agosto: nos siguen pateando, pero no entra
// 30.1 s 6 vallas invictas → "EL ARCO SE CERRÓ."
export const DefensaReel: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: C.bg}}>
      <Scene3D />
      <HookText />
      <Rain1Hud />
      <Reveal />
      <Turn />
      <Chart />
      <Rain2Hud />
      <Clean />
      <Brand />
      <Sequence from={T.outro} durationInFrames={DURATION - T.outro} layout="none">
        <Outro />
      </Sequence>
      <Flash at={T.hookLaunch + T.hookDur} len={8} max={0.5} />
      <FilmLayer />
    </AbsoluteFill>
  );
};
