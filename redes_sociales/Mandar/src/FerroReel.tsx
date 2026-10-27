import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Flash, FilmLayer} from './components/fx';
import {Intro} from './components/Intro';
import {Outro} from './components/Outro';
import {Brand, Cards, Circuit, Stat, Titles} from './components/Overlays';
import {World} from './components/World';
import {C, DURATION, T} from './theme';

// 1080x1920 · 30 fps · 30 s
// 0.0 s  presentación: la pelota entra y forma FERR(O). "Si nos gana, sale campeón"
// 4.0 s  zoom out desde la pelota: aparece la cancha y el 11 de Ferro
// 8.0 s  la pelota recorre el circuito Hoyos → González → Parisi (zoom in a cada uno, zoom out en cada pase)
// 20.7 s el remate se congela: "hay que cortarlo"
// 23.3 s dato: 66% de sus goles en el 2° tiempo
// 25.6 s cierre: "QUE FESTEJEN OTRO DÍA."
// Cierre: la música y la imagen se apagan juntas
const FADE_AUDIO = 75; // 2,5 s
const FADE_VIDEO = 30; // 1 s

const FundidoFinal: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [DURATION - FADE_VIDEO, DURATION - 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return o > 0 ? <AbsoluteFill style={{backgroundColor: '#000', opacity: o}} /> : null;
};

export const FerroReel: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: C.bg}}>
      <World />
      <Titles />
      <Cards />
      <Circuit />
      <Stat />
      <Brand />
      <Sequence from={0} durationInFrames={T.introEnd} layout="none">
        <Intro />
      </Sequence>
      <Sequence from={T.outro} durationInFrames={DURATION - T.outro} layout="none">
        <Outro />
      </Sequence>
      <Flash at={T.circuit[0]} len={7} max={0.45} />
      <FilmLayer />
      <FundidoFinal />
      <Audio
        src={staticFile('musica.mp3')}
        volume={(f) =>
          interpolate(f, [0, 8, DURATION - FADE_AUDIO, DURATION - 1], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
        }
      />
    </AbsoluteFill>
  );
};
