import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Cierre} from '../Cierre';
import {Flash, FilmLayer, clamp} from '../fx';
import {Brand, Chart, HookText, Rain1Hud, Rain2Hud, Ratio, Reveal, Turn} from './Overlays';
import {Scene3D} from './Scene3D';
import {C, DURATION, T} from './tema';

// 1080x1920 · 30 fps · 37 s — "CÓMO PATEAMOS"
// 0 s    vista del arquero: el gol de afuera a Madryn. "PATEAMOS 314 VECES"
// 3.7 s  los 314 remates en orden, cada vez más rápido; la cámara orbita hasta la vista aérea
// 16.7 s 172 de afuera: solo 2 goles · 142 de adentro: 25 goles
// 23 s   "Y DESDE AGOSTO..." goles a favor partido a partido: 0,86 → 1,15
// 28 s   los remates desde agosto: pateamos más, pero seguimos de afuera
// 31.7 s adentro 1 de cada 6 es gol, afuera 1 de cada 86
// 33.5 s cierre: "EL GOL ESTÁ ADENTRO."
export const AtaqueReel: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor: C.bg}}>
      <Scene3D />
      <HookText />
      <Rain1Hud />
      <Reveal />
      <Turn />
      <Chart />
      <Rain2Hud />
      <Ratio />
      <Brand />
      <Sequence from={T.outro} durationInFrames={DURATION - T.outro} layout="none">
        <Cierre linea1="EL GOL ESTÁ" linea2="ADENTRO." resaltado={C.gold} />
      </Sequence>
      <Flash at={T.hookLaunch + T.hookDur} len={8} max={0.5} />
      <FilmLayer />
      <AbsoluteFill style={{backgroundColor: '#000', opacity: interpolate(f, [DURATION - 30, DURATION - 1], [0, 1], clamp)}} />
      <Audio
        src={staticFile('musica.mp3')}
        volume={(fr) => interpolate(fr, [0, 8, DURATION - 75, DURATION - 1], [0, 1, 1, 0], clamp)}
      />
    </AbsoluteFill>
  );
};
