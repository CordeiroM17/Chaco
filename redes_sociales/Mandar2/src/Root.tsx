import React from 'react';
import {Composition} from 'remotion';
import {DefensaReel} from './DefensaReel';
import {DURATION, FPS, H, W} from './theme';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="DefensaReel"
      component={DefensaReel}
      durationInFrames={DURATION}
      fps={FPS}
      width={W}
      height={H}
    />
  );
};
