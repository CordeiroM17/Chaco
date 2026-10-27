import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {CARDS, Card} from '../data';
import {C, DISPLAY, HANDLE, MONO, NUM, T} from '../theme';
import {EASE_OUT, clamp, smooth} from './fx';

const rise = (p: number, d = 30): React.CSSProperties => ({opacity: p, transform: `translateY(${(1 - p) * d}px)`});

const center: React.CSSProperties = {position: 'absolute', left: 0, right: 0, textAlign: 'center'};

// "EL 11 DE FERRO" y después "3 JUGADORES. 1 CIRCUITO."
export const Titles: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < T.title[0] || frame > T.tagline[1]) return null;
  const a = smooth(frame, T.title[0], T.title[1] - 10, T.title[1]);
  const b = smooth(frame, T.tagline[0], T.tagline[1] - 10, T.tagline[1]);
  return (
    <AbsoluteFill>
      <div style={{...center, top: 150, ...rise(a)}}>
        <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 28, letterSpacing: 10, color: C.gold}}>SU DIBUJO · 4-1-4-1</div>
        <div style={{fontFamily: DISPLAY, fontSize: 120, lineHeight: 1.05, color: C.ink}}>EL 11 DE FERRO</div>
      </div>
      <div style={{...center, top: 150, ...rise(b)}}>
        <div style={{fontFamily: DISPLAY, fontSize: 110, lineHeight: 1.05, color: C.ink}}>3 JUGADORES.</div>
        <div style={{fontFamily: DISPLAY, fontSize: 110, lineHeight: 1.05, color: C.gold}}>1 CIRCUITO.</div>
      </div>
    </AbsoluteFill>
  );
};

// Ficha de cada jugador del circuito: centrada, un dato
const PlayerCard: React.FC<{card: Card; from: number; to: number}> = ({card, from, to}) => {
  const frame = useCurrentFrame();
  if (frame < from - 2 || frame > to) return null;
  const all = smooth(frame, from, to - 10, to);
  const chip = smooth(frame, from + 2, to - 10, to);
  const name = smooth(frame, from + 6, to - 10, to);
  const stat = smooth(frame, from + 12, to - 10, to);
  const sub = smooth(frame, from + 22, to - 10, to);
  const n = Math.round(
    interpolate(frame, [from + 12, from + 40], [card.countFrom, card.value], {...clamp, easing: Easing.out(Easing.cubic)})
  );
  const ring = interpolate(frame, [from, from + 20], [0, 1], {...clamp, easing: EASE_OUT});

  return (
    <AbsoluteFill>
      {/* Foco: todo oscuro menos el jugador */}
      <AbsoluteFill
        style={{
          opacity: all,
          background:
            'radial-gradient(circle at 540px 700px, rgba(6,6,6,0) 0px, rgba(6,6,6,0) 170px, rgba(6,6,6,0.82) 360px), linear-gradient(180deg, rgba(6,6,6,0) 45%, rgba(6,6,6,0.6) 60%)',
        }}
      />
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, opacity: all}}>
        <circle
          cx={540}
          cy={700}
          r={150 + (1 - ring) * 120}
          fill="none"
          stroke={C.gold}
          strokeWidth={3}
          strokeDasharray={`${ring * 942} 942`}
          transform="rotate(-90 540 700)"
        />
      </svg>

      <div style={{...center, top: 960}}>
        <div
          style={{
            display: 'inline-block',
            fontFamily: MONO,
            fontWeight: 700,
            fontSize: 28,
            letterSpacing: 6,
            color: C.bg,
            background: C.gold,
            padding: '8px 22px',
            ...rise(chip, 20),
          }}
        >
          {card.chip}
        </div>
      </div>
      <div style={{...center, top: 1020, ...rise(name, 40)}}>
        <div style={{fontFamily: DISPLAY, fontSize: card.name.length > 6 ? 150 : 170, lineHeight: 1.1, color: C.ink}}>{card.name}</div>
      </div>
      <div style={{...center, top: 1215, ...rise(stat, 40)}}>
        <div style={{fontFamily: NUM, fontSize: 230, lineHeight: 1, color: C.gold}}>
          {card.prefix ?? ''}
          {n}
          {card.suffix ?? ''}
        </div>
        <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 32, letterSpacing: 6, color: C.ink, marginTop: 10}}>{card.label}</div>
      </div>
      <div style={{...center, top: 1515, ...rise(sub, 16)}}>
        <div style={{fontFamily: MONO, fontSize: 28, color: C.gray}}>{card.sub}</div>
      </div>
    </AbsoluteFill>
  );
};

export const Cards: React.FC = () => (
  <>
    {CARDS.map((c, i) => (
      <PlayerCard key={c.id} card={c} from={T.cards[i].from} to={T.cards[i].to} />
    ))}
  </>
);

// El remate se congela: "ESTE ES EL CIRCUITO. HAY QUE CORTARLO."
export const Circuit: React.FC = () => {
  const frame = useCurrentFrame();
  const [from, to] = T.circuit;
  if (frame < from || frame > to) return null;
  const a = smooth(frame, from + 4, to - 10, to);
  const names = smooth(frame, from + 14, to - 10, to);
  const cut = smooth(frame, from + 42, to - 10, to);
  const bar = interpolate(frame, [from + 42, from + 54], [0, 1], {...clamp, easing: EASE_OUT});
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(6,6,6,0.85) 0%, rgba(6,6,6,0) 30%)', opacity: a}} />
      <div style={{...center, top: 130, ...rise(a)}}>
        <div style={{fontFamily: DISPLAY, fontSize: 80, lineHeight: 1.05, color: C.ink}}>ESTE ES EL CIRCUITO</div>
      </div>
      <div style={{...center, top: 260, ...rise(names, 16)}}>
        <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 30, letterSpacing: 3, color: C.gold}}>
          HOYOS → GONZÁLEZ → PARISI
        </div>
      </div>
      <div style={{...center, top: 330, ...rise(cut, 20)}}>
        <div style={{position: 'relative', display: 'inline-block', padding: '6px 26px 0'}}>
          <div style={{position: 'absolute', inset: 0, background: C.ink, transform: `scaleX(${bar})`, transformOrigin: 'left'}} />
          <span style={{position: 'relative', fontFamily: DISPLAY, fontSize: 80, lineHeight: 1.1, color: C.bg}}>HAY QUE CORTARLO.</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Dato final: 66% de sus goles en el segundo tiempo
export const Stat: React.FC = () => {
  const frame = useCurrentFrame();
  const [from, to] = T.stat;
  if (frame < from || frame > to + 4) return null;
  const dim = interpolate(frame, [from, from + 12], [0, 1], {...clamp, easing: EASE_OUT});
  const chip = smooth(frame, from + 4, to + 100, to + 101);
  const big = smooth(frame, from + 8, to + 100, to + 101);
  const txt = smooth(frame, from + 18, to + 100, to + 101);
  const pct = Math.round(interpolate(frame, [from + 8, from + 34], [0, 66], {...clamp, easing: Easing.out(Easing.cubic)}));
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{backgroundColor: 'rgba(6,6,6,0.8)', opacity: dim}} />
      <div style={{...center, top: 640, ...rise(chip, 16)}}>
        <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 32, letterSpacing: 12, color: C.gold}}>Y OJO AL FINAL</div>
      </div>
      <div style={{...center, top: 690, opacity: big, transform: `scale(${0.85 + big * 0.15})`}}>
        <div style={{fontFamily: NUM, fontSize: 400, lineHeight: 1, color: C.ink}}>{pct}%</div>
      </div>
      <div style={{...center, top: 1090, ...rise(txt, 20)}}>
        <div style={{fontFamily: MONO, fontSize: 36, color: C.ink}}>de sus goles llegan</div>
        <div style={{fontFamily: DISPLAY, fontSize: 110, lineHeight: 1.15, color: C.gold}}>EN EL 2° TIEMPO</div>
      </div>
    </AbsoluteFill>
  );
};

// Marca fija (la de las placas): rayas + CHACO FOR EVER / ESTADÍSTICAS arriba, @ abajo
export const Rayas: React.FC<{w?: number; h?: number; n?: number}> = ({w = 46, h = 30, n = 5}) => (
  <div style={{display: 'flex', width: w, height: h}}>
    {Array.from({length: n}).map((_, i) => (
      <div key={i} style={{flex: 1, background: i % 2 === 0 ? '#FFFFFF' : C.bg}} />
    ))}
  </div>
);

export const Brand: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [T.introEnd, T.introEnd + 14, T.outro, T.outro + 10], [0, 1, 1, 0], clamp);
  if (o <= 0) return null;
  return (
    <AbsoluteFill style={{opacity: o}}>
      <div style={{position: 'absolute', top: 64, left: 60, display: 'flex', alignItems: 'center', gap: 16}}>
        <Rayas />
        <div>
          <div style={{fontFamily: DISPLAY, fontSize: 24, letterSpacing: 2, color: C.ink, lineHeight: 1.05}}>CHACO FOR EVER</div>
          <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 14, letterSpacing: 6, color: C.gold}}>ESTADÍSTICAS</div>
        </div>
      </div>
      <div style={{position: 'absolute', top: 74, right: 60, fontFamily: MONO, fontWeight: 700, fontSize: 18, letterSpacing: 4, color: C.gray}}>
        PREVIA · FECHA 35
      </div>
      <div style={{position: 'absolute', bottom: 300, left: 60, display: 'flex', alignItems: 'center', gap: 14}}>
        <div style={{width: 40, height: 4, background: C.gold}} />
        <span style={{fontFamily: MONO, fontWeight: 600, fontSize: 22, color: C.ink, letterSpacing: 1}}>{HANDLE}</span>
      </div>
    </AbsoluteFill>
  );
};
