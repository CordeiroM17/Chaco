import React from 'react';

const pentagon = (cx: number, cy: number, rad: number, a0: number) =>
  Array.from({length: 5})
    .map((_, k) => {
      const a = ((a0 + k * 72) * Math.PI) / 180;
      return `${cx + rad * Math.cos(a)},${cy + rad * Math.sin(a)}`;
    })
    .join(' ');

// Pelota clásica (pentágonos negros). Se dibuja centrada en (0,0). `id` tiene que ser único.
export const SoccerBall: React.FC<{r: number; rot: number; id: string}> = ({r, rot, id}) => {
  const outer = Array.from({length: 5}).map((_, k) => {
    const a = ((-90 + k * 72) * Math.PI) / 180;
    return {x: Math.cos(a) * r * 0.98, y: Math.sin(a) * r * 0.98, inner: {x: Math.cos(a) * r * 0.36, y: Math.sin(a) * r * 0.36}};
  });
  return (
    <g>
      <defs>
        <clipPath id={`${id}-clip`}>
          <circle r={r} />
        </clipPath>
        <radialGradient id={`${id}-shade`} cx="35%" cy="30%" r="80%">
          <stop offset="0" stopColor="#000" stopOpacity="0" />
          <stop offset="0.6" stopColor="#000" stopOpacity="0.08" />
          <stop offset="1" stopColor="#000" stopOpacity="0.55" />
        </radialGradient>
      </defs>
      <circle r={r} fill="#F7F7F2" />
      <g clipPath={`url(#${id}-clip)`} transform={`rotate(${rot})`}>
        {outer.map((o, k) => (
          <line key={`s${k}`} x1={o.inner.x} y1={o.inner.y} x2={o.x} y2={o.y} stroke="#2A2A2A" strokeWidth={r * 0.05} />
        ))}
        <polygon points={pentagon(0, 0, r * 0.38, -90)} fill="#111" />
        {outer.map((o, k) => (
          <polygon key={`p${k}`} points={pentagon(o.x, o.y, r * 0.36, 90 + k * 72)} fill="#111" />
        ))}
      </g>
      <circle r={r} fill={`url(#${id}-shade)`} />
      <circle r={r} fill="none" stroke="#000" strokeOpacity={0.6} strokeWidth={r * 0.04} />
    </g>
  );
};
