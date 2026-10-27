import {continueRender, delayRender, staticFile} from 'remotion';

// Tipografías de la marca (las mismas de las placas: nucleo/marca.py)
//   DISPLAY = Segoe UI Black (títulos) · MONO = Segoe UI (etiquetas, 400/600/700) · NUM = Bahnschrift (números)
const CARAS: [string, string, string][] = [
  ['CFE Black', 'seguibl.ttf', '400'],
  ['CFE Texto', 'segoeui.ttf', '400'],
  ['CFE Texto', 'seguisb.ttf', '600'],
  ['CFE Texto', 'segoeuib.ttf', '700'],
  ['CFE Num', 'bahnschrift.ttf', '400'],
];
if (typeof document !== 'undefined') {
  const h = delayRender('fuentes de la marca');
  Promise.all(
    CARAS.map(([familia, archivo, peso]) =>
      new FontFace(familia, `url(${staticFile(`fuentes/${archivo}`)})`, {weight: peso}).load().then((f) => {
        (document.fonts as unknown as {add: (x: FontFace) => void}).add(f);
      })
    )
  )
    .then(() => continueRender(h))
    .catch((e) => {
      console.error(e);
      continueRender(h);
    });
}

export const DISPLAY = 'CFE Black';
export const MONO = 'CFE Texto';
export const NUM = 'CFE Num';

export const HANDLE = '@chacoforever.stats';

export const W = 1080;
export const H = 1920;
export const FPS = 30;
export const DURATION = 1060; // 35,3 s (incluye el cierre)

// Estándar de la cuenta: negro y blanco Chaco For Ever + un solo acento dorado (#E8B23A)
export const C = {
  bg: '#0E0E0E',
  pitchA: '#121212',
  pitchB: '#161616',
  ink: '#F5F5F5',
  gray: '#969696',
  line: 'rgba(245,245,245,0.17)',
  shirt: '#1C1C1C',
  gold: '#E8B23A',
};

