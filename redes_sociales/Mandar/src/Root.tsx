import React from 'react';
import {Composition} from 'remotion';
import {FerroReel} from './FerroReel';
import {DURATION, FPS, H, W} from './theme';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="FerroReel"
      component={FerroReel}
      durationInFrames={DURATION}
      fps={FPS}
      width={W}
      height={H}
    />
  );
};
