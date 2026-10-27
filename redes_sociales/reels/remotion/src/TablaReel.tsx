import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import datos from '../public/tabla.json';
import {EASE_OUT, FilmLayer, clamp, smooth} from './fx';
import {Cierre} from './Cierre';
import {C, DISPLAY, DURATION, HANDLE, MONO, NUM} from './theme';

// "DE ÚLTIMO A 10°": la tabla del Grupo A partido a partido. 18 equipos, uno solo importa.
// Datos: ../exportar_tabla.py -> public/tabla.json (validado contra la tabla oficial).

type Equipo = {id: number; nombre: string; escudo: string; pos: number[]; pts: number[]};
const EQ = datos.equipos as Equipo[];
const CHACO = EQ.find((e) => e.id === datos.chaco)!;
const N = CHACO.pos.length; // 34

// ---------------------------------------------------------------- guion (frames a 30 fps)
const P1 = [75, 345] as const; // partidos 1 -> 18
const REC = [345, 435] as const; // receso: se frena todo
const P2 = [435, 735] as const; // partidos 18 -> 34
const FIN = 735;
const CIERRE = 930; // cierre con rayas, pelota y marca (como el de Ferro)

// avance con aceleración y frenado suaves (velocidad trapezoidal)
const avance = (f: number, [a, b]: readonly [number, number], g0: number, g1: number, k = 0.14) => {
  const p = Math.min(Math.max((f - a) / (b - a), 0), 1);
  const v = 1 / (1 - k);
  const s = p < k ? (v * p * p) / (2 * k) : p < 1 - k ? v * (k / 2 + p - k) : 1 - (v * (1 - p) ** 2) / (2 * k);
  return g0 + (g1 - g0) * s;
};
const gDe = (f: number) => (f < P1[0] ? 1 : f < P1[1] ? avance(f, P1, 1, 18) : f < P2[0] ? 18 : avance(f, P2, 18, N));

// ---------------------------------------------------------------- geometría
const X0 = 200;
const X1 = 770;
const Y0 = 556;
const RH = 56;
const X = (g: number) => X0 + ((g - 1) / (N - 1)) * (X1 - X0);
const Y = (pos: number) => Y0 + (pos - 1) * RH;
const ss = (t: number) => t * t * (3 - 2 * t);

const posEn = (e: Equipo, g: number) => {
  const i = Math.min(Math.floor(g), N - 1);
  const t = Math.min(g - i, 1);
  return e.pos[i - 1] + (e.pos[Math.min(i, N - 1)] - e.pos[i - 1]) * ss(t);
};

const trazo = (e: Equipo, gA: number, gB: number) => {
  const pts: string[] = [];
  for (let g = gA; g <= gB + 1e-6; g += 0.1) pts.push(`${X(g).toFixed(1)},${Y(posEn(e, g)).toFixed(1)}`);
  pts.push(`${X(gB).toFixed(1)},${Y(posEn(e, gB)).toFixed(1)}`);
  return 'M' + pts.join(' L');
};

const centro: React.CSSProperties = {position: 'absolute', left: 60, right: 60, textAlign: 'center'};
const sube = (p: number, d = 30): React.CSSProperties => ({opacity: p, transform: `translateY(${(1 - p) * d}px)`});

// ---------------------------------------------------------------- textos (uno por capítulo)
const Titulo: React.FC<{de: number; a: number; grande: React.ReactNode; bajada: React.ReactNode; size?: number}> = ({
  de,
  a,
  grande,
  bajada,
  size = 104,
}) => {
  const f = useCurrentFrame();
  if (f < de - 1 || f > a + 1) return null;
  const t = de === 0 ? 1 : smooth(f, de, a - 12, a, 16);
  const b = de === 0 ? 1 : smooth(f, de + 8, a - 12, a, 16);
  return (
    <div style={{...centro, top: 150}}>
      <div style={{...sube(t, 40), fontFamily: DISPLAY, fontSize: size, lineHeight: 1.02, color: C.ink}}>{grande}</div>
      <div style={{...sube(b, 20), fontFamily: MONO, fontWeight: 600, fontSize: 36, color: C.gray, marginTop: 18}}>{bajada}</div>
    </div>
  );
};

const Marca: React.FC = () => (
  <>
    <div style={{position: 'absolute', top: 64, left: 60, display: 'flex', alignItems: 'center', gap: 16}}>
      <div style={{display: 'flex', width: 46, height: 30}}>
        {[0, 1, 2, 3, 4].map((i) => (
          <div key={i} style={{flex: 1, background: i % 2 === 0 ? '#FFFFFF' : C.bg}} />
        ))}
      </div>
      <div>
        <div style={{fontFamily: DISPLAY, fontSize: 24, letterSpacing: 2, color: C.ink, lineHeight: 1.05}}>CHACO FOR EVER</div>
        <div style={{fontFamily: MONO, fontWeight: 600, fontSize: 14, letterSpacing: 6, color: C.gold}}>ESTADÍSTICAS</div>
      </div>
    </div>
    <div style={{position: 'absolute', top: 74, right: 60, fontFamily: MONO, fontWeight: 700, fontSize: 18, letterSpacing: 4, color: C.gray}}>
      PRIMERA NACIONAL 2026
    </div>
    <div style={{position: 'absolute', top: 1596, left: 60, display: 'flex', alignItems: 'center', gap: 14}}>
      <div style={{width: 40, height: 4, background: C.gold}} />
      <span style={{fontFamily: MONO, fontWeight: 600, fontSize: 22, color: C.ink, letterSpacing: 1}}>{HANDLE}</span>
    </div>
  </>
);

// ---------------------------------------------------------------- composición
export const TablaReel: React.FC = () => {
  const f = useCurrentFrame();
  const g = gDe(f);
  const fase2 = g > 18 + 1e-3;
  const yCh = Y(posEn(CHACO, g));
  const xCh = X(g);
  const posActual = Math.round(posEn(CHACO, g));

  // cámara: se acerca a Chaco en el receso y vuelve
  // foco del receso: se oscurece todo menos Chaco
  const foco = interpolate(f, [REC[0], REC[0] + 24, REC[1] - 6, REC[1] + 20], [0, 1, 1, 0], {...clamp, easing: Easing.inOut(Easing.cubic)});

  // la zona de descenso se apaga cuando Chaco sale para siempre (partido 25)
  const banda = interpolate(g, [24.5, 25.5], [1, 0.35], clamp);
  const recesoA = interpolate(f, [REC[0], REC[0] + 18], [0, 1], {...clamp, easing: EASE_OUT});
  const fin = interpolate(f, [FIN + 20, FIN + 50], [0, 1], {...clamp, easing: EASE_OUT});
  const fila10 = interpolate(f, [FIN + 30, FIN + 60], [0, 1], {...clamp, easing: EASE_OUT});
  const superados = Math.max(0, 18 - posActual);

  // ondas sobre el escudo de Chaco en los momentos clave
  const ondas = [REC[0], FIN + 25]
    .map((t0) => (f - t0) / 40)
    .filter((q) => q > 0 && q < 1);

  return (
    <AbsoluteFill style={{backgroundColor: C.bg}}>
      <AbsoluteFill>
        <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
          <defs>
            <filter id="brillo" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="b" />
              <feMerge>
                <feMergeNode in="b" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* filas */}
          {Array.from({length: 18}).map((_, i) => (
            <g key={i}>
              <line x1={X0 - 30} x2={X1 + 30} y1={Y(i + 1)} y2={Y(i + 1)} stroke="rgba(245,245,245,0.05)" strokeWidth={1} />
              <text
                x={150}
                y={Y(i + 1) + 7}
                textAnchor="end"
                fontFamily={MONO}
                fontWeight={600}
                fontSize={19}
                fill={i + 1 === 10 && fin > 0 ? C.gold : C.gray}
                opacity={i + 1 === 10 && fin > 0 ? 1 : 0.6}
              >
                {i + 1}°
              </text>
            </g>
          ))}

          {/* zona de descenso */}
          <g opacity={banda}>
            <rect x={X0 - 30} y={Y(16.5)} width={X1 - X0 + 60} height={RH * 2} fill="rgba(245,245,245,0.045)" />
            <line x1={X0 - 30} x2={X1 + 30} y1={Y(16.5)} y2={Y(16.5)} stroke={C.gray} strokeWidth={2} strokeDasharray="10 10" />
            <text x={X0 - 30} y={Y(16.5) - 12} fontFamily={MONO} fontWeight={700} fontSize={18} letterSpacing={5} fill={C.gray}>
              ZONA DE DESCENSO
            </text>
          </g>

          {/* fila del 10° al final */}
          <rect
            x={X0 - 30}
            y={Y(10) - RH / 2}
            width={(X1 - X0 + 60) * fila10}
            height={RH}
            fill={C.gold}
            opacity={0.14}
          />

          {/* receso */}
          <g opacity={recesoA}>
            <line x1={X(18.5)} x2={X(18.5)} y1={Y(1) - 34} y2={Y(18) + 26} stroke={C.gray} strokeWidth={2} strokeDasharray="4 10" />
            <text x={X(18.5)} y={Y(1) - 46} textAnchor="middle" fontFamily={MONO} fontWeight={700} fontSize={18} letterSpacing={5} fill={C.gray}>
              RECESO
            </text>
          </g>

          {/* eje de partidos */}
          <text x={X0} y={Y(18) + 64} fontFamily={MONO} fontWeight={600} fontSize={18} letterSpacing={3} fill={C.gray} opacity={0.7}>
            PARTIDO 1
          </text>
          <text x={X1} y={Y(18) + 64} textAnchor="end" fontFamily={MONO} fontWeight={600} fontSize={18} letterSpacing={3} fill={C.gray} opacity={0.7}>
            34
          </text>

          {/* los otros 17 */}
          {EQ.filter((e) => e.id !== CHACO.id).map((e) => (
            <path key={e.id} d={trazo(e, 1, g)} fill="none" stroke="rgba(245,245,245,0.07)" strokeWidth={2} strokeLinejoin="round" />
          ))}

          {/* Chaco: blanco hasta el receso, dorado después */}
          <path
            d={trazo(CHACO, 1, Math.min(g, 18))}
            fill="none"
            stroke={C.ink}
            strokeWidth={9}
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity={fase2 ? 0.75 : 1}
          />
          {fase2 ? (
            <path
              d={trazo(CHACO, 18, g)}
              fill="none"
              stroke={C.gold}
              strokeWidth={10}
              strokeLinecap="round"
              strokeLinejoin="round"
              filter="url(#brillo)"
            />
          ) : null}

          {ondas.map((q, i) => (
            <circle key={i} cx={xCh} cy={yCh} r={40 + 110 * EASE_OUT(q)} fill="none" stroke={fase2 || f > FIN ? C.gold : C.ink} strokeWidth={3} opacity={1 - q} />
          ))}
        </svg>

        {/* escudos en la punta de cada línea: los que quedan abajo de Chaco se apagan */}
        {EQ.filter((e) => e.id !== CHACO.id).map((e) => {
          const y = Y(posEn(e, g));
          const op = interpolate(y - yCh, [-30, 30], [0.85, 0.22], clamp);
          return (
            <Img
              key={e.id}
              src={staticFile(e.escudo)}
              style={{position: 'absolute', left: X(g) - 19, top: y - 19, width: 38, height: 38, objectFit: 'contain', opacity: op}}
            />
          );
        })}

        {/* Chaco */}
        <div
          style={{
            position: 'absolute',
            left: xCh - 34,
            top: yCh - 34,
            width: 68,
            height: 68,
            borderRadius: 34,
            background: '#F4F4F4',
            boxShadow: `0 0 0 ${fase2 ? 4 : 0}px ${C.gold}, 0 6px 24px rgba(0,0,0,0.6)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Img src={staticFile(CHACO.escudo)} style={{width: 50, height: 50, objectFit: 'contain'}} />
        </div>
        <div
          style={{
            position: 'absolute',
            left: xCh + 48,
            top: yCh - 34,
            fontFamily: NUM,
            fontSize: 58,
            lineHeight: '68px',
            color: f > FIN ? C.gold : C.ink,
          }}
        >
          {posActual}°
        </div>
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          opacity: foco * 0.85,
          background: `radial-gradient(circle at ${xCh}px ${yCh}px, rgba(14,14,14,0) 70px, rgba(14,14,14,0.92) 260px)`,
        }}
      />

      {/* capítulos */}
      <Titulo de={0} a={REC[0]} grande="ESTUVO ÚLTIMO" bajada={<>14 partidos seguidos. ¿Cómo terminó?</>} />
      <Titulo de={REC[0]} a={P2[0] + 6} grande="EL RECESO" bajada="12 puntos en 18 partidos" />
      <Titulo
        de={P2[0] + 6}
        a={FIN}
        grande="DESPUÉS DEL RECESO"
        size={92}
        bajada={superados > 0 ? `Pasó a ${superados} equipo${superados > 1 ? 's' : ''}` : 'Vuelve a sumar'}
      />
      <div style={{...centro, top: 150}}>
        <div style={{...sube(fin, 40), fontFamily: DISPLAY, fontSize: 104, lineHeight: 1.02, color: C.ink}}>
          DE ÚLTIMO A <span style={{color: C.gold}}>10°</span>
        </div>
        <div style={{...sube(interpolate(f, [FIN + 34, FIN + 60], [0, 1], {...clamp, easing: EASE_OUT}), 20), fontFamily: MONO, fontWeight: 600, fontSize: 36, color: C.gray, marginTop: 18}}>
          Pasó a 8 equipos · 40 puntos · salvado
        </div>
      </div>
      <div
        style={{
          ...centro,
          top: 400,
          ...sube(interpolate(f, [FIN + 80, FIN + 105], [0, 1], {...clamp, easing: EASE_OUT}), 16),
          fontFamily: MONO,
          fontWeight: 700,
          fontSize: 30,
          color: C.ink,
        }}
      >
        ¿En qué partido sentiste que se salvaba?
      </div>

      <Marca />
      <Sequence from={CIERRE} durationInFrames={DURATION - CIERRE} layout="none">
        <Cierre />
      </Sequence>
      <FilmLayer />
      <AbsoluteFill style={{backgroundColor: '#000', opacity: interpolate(f, [DURATION - 30, DURATION - 1], [0, 1], clamp)}} />
      <Audio
        src={staticFile('musica.mp3')}
        volume={(fr) => interpolate(fr, [0, 8, DURATION - 75, DURATION - 1], [0, 1, 1, 0], clamp)}
      />
    </AbsoluteFill>
  );
};
