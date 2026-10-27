import React from 'react';
import {Composition} from 'remotion';
import {AtaqueReel} from './ataque/AtaqueReel';
import {DURATION as DUR_ATAQUE} from './ataque/tema';
import {TablaReel} from './TablaReel';
import {DURATION, FPS, H, W} from './theme';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="TablaReel" component={TablaReel} durationInFrames={DURATION} fps={FPS} width={W} height={H} />
    <Composition id="AtaqueReel" component={AtaqueReel} durationInFrames={DUR_ATAQUE} fps={FPS} width={W} height={H} />
  </>
);
