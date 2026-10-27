// Motor 3D mínimo: proyección en perspectiva a SVG. Sin WebGL, rinde rápido en cualquier PC.
// Mundo en metros: x lateral (0 = centro del arco), y hacia la cancha (0 = línea de gol), z altura.

export type V3 = [number, number, number];
export type Rig = {tx: number; ty: number; tz: number; dist: number; az: number; el: number; f: number};

export const SCREEN = {cx: 540, cy: 900};
const NEAR = 0.4;

const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a: V3): V3 => {
  const l = Math.hypot(a[0], a[1], a[2]) || 1;
  return [a[0] / l, a[1] / l, a[2] / l];
};

export type Camera = {pos: V3; right: V3; up: V3; fwd: V3; f: number};

// az = 0: cámara detrás del arco mirando hacia la cancha. el = elevación en grados.
export const makeCamera = (r: Rig): Camera => {
  const az = (r.az * Math.PI) / 180;
  const el = (r.el * Math.PI) / 180;
  const target: V3 = [r.tx, r.ty, r.tz];
  const pos: V3 = [
    r.tx + r.dist * Math.sin(az) * Math.cos(el),
    r.ty - r.dist * Math.cos(az) * Math.cos(el),
    r.tz + r.dist * Math.sin(el),
  ];
  const fwd = norm(sub(target, pos));
  const right = norm(cross(fwd, [0, 0, 1]));
  const up = cross(right, fwd);
  return {pos, right, up, fwd, f: r.f};
};

const toCam = (c: Camera, p: V3): V3 => {
  const d = sub(p, c.pos);
  return [dot(d, c.right), dot(d, c.up), dot(d, c.fwd)];
};

const projCam = (c: Camera, q: V3) => ({x: SCREEN.cx + (c.f * q[0]) / q[2], y: SCREEN.cy - (c.f * q[1]) / q[2], s: c.f / q[2]});

// Proyecta un punto; null si queda detrás de la cámara. `s` = píxeles por metro a esa distancia.
export const project = (c: Camera, p: V3) => {
  const q = toCam(c, p);
  if (q[2] < NEAR) return null;
  return projCam(c, q);
};

// Segmento con recorte contra el plano cercano
export const segment = (c: Camera, a: V3, b: V3): string | null => {
  let qa = toCam(c, a);
  let qb = toCam(c, b);
  if (qa[2] < NEAR && qb[2] < NEAR) return null;
  if (qa[2] < NEAR || qb[2] < NEAR) {
    const t = (NEAR - qa[2]) / (qb[2] - qa[2]);
    const cut: V3 = [qa[0] + (qb[0] - qa[0]) * t, qa[1] + (qb[1] - qa[1]) * t, NEAR];
    if (qa[2] < NEAR) qa = cut;
    else qb = cut;
  }
  const pa = projCam(c, qa);
  const pb = projCam(c, qb);
  return `M${pa.x.toFixed(1)} ${pa.y.toFixed(1)}L${pb.x.toFixed(1)} ${pb.y.toFixed(1)}`;
};

// Polilínea abierta (puntos 3D)
export const polyline = (c: Camera, pts: V3[]): string => {
  let d = '';
  for (let i = 0; i < pts.length - 1; i++) {
    const s = segment(c, pts[i], pts[i + 1]);
    if (s) d += s;
  }
  return d;
};

// Polígono relleno en el piso (sin recorte: usar solo con todos los puntos delante de la cámara)
export const polygon = (c: Camera, pts: V3[]): string | null => {
  const out: string[] = [];
  for (const p of pts) {
    const q = project(c, p);
    if (!q) return null;
    out.push(`${q.x.toFixed(1)},${q.y.toFixed(1)}`);
  }
  return out.join(' ');
};

export const arc = (cx: number, cy: number, r: number, a0: number, a1: number, n = 24): V3[] =>
  Array.from({length: n + 1}, (_, i) => {
    const a = a0 + ((a1 - a0) * i) / n;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a), 0] as V3;
  });
