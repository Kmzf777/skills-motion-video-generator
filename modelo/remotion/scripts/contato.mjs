// Folha de contato de qualquer composição: um bundle, N stills, um mosaico.
//
//   node scripts/contato.mjs <Comp> <NN-tema> [s1,s2,...] [--escala=0.25] [--cols=8] [--saida=nome.png]
//
// Roda de `motion/remotion`. A peça é `motion/pecas/<NN-tema>/`: o public dir é o
// `public/` dela, os stills vão para `saida/stills/` e a folha para `saida/<nome>`.
// `--saida` com barra é caminho (relativo a onde você rodou); sem barra, é nome dentro
// de `saida/`. Os instantes são em SEGUNDOS; sem lista (ou com "-"), um quadro a cada
// 2,5 s da peça inteira.
//
// Cada célula leva o instante (segundos e quadro) desenhado no canto, em pixel, para a
// conferência citar o tempo. Still não toca áudio: a folha sai mesmo sem narração e sem
// sfx; imagem que falta (recorte, logo), não -- o render do still cancela.

import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {PNG} from 'pngjs';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const USO = 'uso: node scripts/contato.mjs <Comp> <NN-tema> [s1,s2,...] [--escala=0.25] [--cols=8] [--saida=nome.png]';

/** Erro de uso: mensagem curta, sem pilha. */
function falhar(msg) {
  console.error(`FALHA  ${msg}`);
  process.exit(1);
}

const posicionais = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const opc = Object.fromEntries(process.argv.slice(2).filter((a) => a.startsWith('--')).map((a) => {
  const [k, ...v] = a.slice(2).split('=');
  return [k, v.join('=')];
}));
for (const k of Object.keys(opc)) {
  if (!['escala', 'cols', 'saida'].includes(k)) falhar(`--${k} não existe. ${USO}`);
}
const [comp, peca, lista] = posicionais;
if (!comp || !peca) falhar(USO);
const escala = Number(opc.escala ?? 0.25);
const cols = Number(opc.cols ?? 8);
if (!(escala > 0 && escala <= 1)) falhar(`--escala tem que estar em (0, 1], veio ${opc.escala}`);
if (!(Number.isInteger(cols) && cols >= 1)) falhar(`--cols tem que ser inteiro >= 1, veio ${opc.cols}`);

const PECA = path.resolve(RAIZ, '..', 'pecas', peca);
if (!fs.existsSync(PECA)) falhar(`não existe a peça ${PECA} (o <NN-tema> é a pasta em motion/pecas/)`);
const saida = opc.saida ?? 'contato.png';
const destino = /[\\/]/.test(saida) ? path.resolve(process.cwd(), saida) : path.join(PECA, 'saida', saida);

const servir = await bundle({entryPoint: path.join(RAIZ, 'src', 'index.ts'), publicDir: path.join(PECA, 'public')});
const c = await selectComposition({serveUrl: servir, id: comp});
const segs = lista && lista !== '-'
  ? lista.split(',').map((v) => {
    const n = Number(v);
    if (!Number.isFinite(n) || n < 0) falhar(`instante inválido: "${v}" (segundos, separados por vírgula)`);
    return n;
  })
  : Array.from({length: Math.floor(c.durationInFrames / c.fps / 2.5) + 1}, (_, k) => k * 2.5);

const dir = path.join(PECA, 'saida', 'stills');
fs.mkdirSync(dir, {recursive: true});
fs.mkdirSync(path.dirname(destino), {recursive: true});
const cw = Math.round(c.width * escala);
const ch = Math.round(c.height * escala);
const celulas = [];
for (const s of segs) {
  const q = Math.min(c.durationInFrames - 1, Math.round(s * c.fps));
  const out = path.join(dir, `${comp}-q${String(q).padStart(4, '0')}.png`);
  await renderStill({composition: c, serveUrl: servir, frame: q, output: out, scale: escala, imageFormat: 'png'});
  celulas.push({s, q, arquivo: out});
  process.stdout.write(`${s.toFixed(2)}s `);
}

// --- mosaico, com o instante escrito em cada célula (fonte de pixel 5x7, só o necessário)
const GLIFOS = {
  0: ['.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'],
  1: ['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'],
  2: ['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'],
  3: ['####.', '....#', '....#', '.###.', '....#', '....#', '####.'],
  4: ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'],
  5: ['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'],
  6: ['..##.', '.#...', '#....', '####.', '#...#', '#...#', '.###.'],
  7: ['#####', '....#', '...#.', '..#..', '.#...', '.#...', '.#...'],
  8: ['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'],
  9: ['.###.', '#...#', '#...#', '.####', '....#', '...#.', '.##..'],
  '.': ['.....', '.....', '.....', '.....', '.....', '.##..', '.##..'],
  s: ['.....', '.....', '.####', '#....', '.###.', '....#', '####.'],
  q: ['.....', '.....', '.####', '#...#', '.####', '....#', '....#'],
  ' ': ['.....', '.....', '.....', '.....', '.....', '.....', '.....'],
};

function pintar(png, x, y, w, h, [r, g, b]) {
  for (let yy = Math.max(0, y); yy < Math.min(png.height, y + h); yy++) {
    for (let xx = Math.max(0, x); xx < Math.min(png.width, x + w); xx++) {
      const i = (yy * png.width + xx) * 4;
      png.data[i] = r; png.data[i + 1] = g; png.data[i + 2] = b; png.data[i + 3] = 255;
    }
  }
}

function escrever(png, texto, x, y, k) {
  const largura = texto.length * 6 * k + k;
  pintar(png, x, y, largura + 2 * k, 9 * k, [0, 0, 0]);
  [...texto].forEach((caractere, n) => {
    const g = GLIFOS[caractere];
    if (!g) return;
    g.forEach((linha, gy) => [...linha].forEach((p, gx) => {
      if (p === '#') pintar(png, x + 2 * k + (n * 6 + gx) * k, y + k + gy * k, k, k, [255, 255, 255]);
    }));
  });
}

const linhas = Math.ceil(celulas.length / cols);
const folha = new PNG({width: cols * (cw + 6), height: linhas * (ch + 6)});
folha.data.fill(30);
const k = Math.max(2, Math.round(cw / 120));
celulas.forEach(({s, q, arquivo}, i) => {
  const img = PNG.sync.read(fs.readFileSync(arquivo));
  const x = (i % cols) * (cw + 6) + 3;
  const y = Math.floor(i / cols) * (ch + 6) + 3;
  PNG.bitblt(img, folha, 0, 0, img.width, img.height, x, y);
  escrever(folha, `${s.toFixed(2)}s q${q}`, x + 4, y + 4, k);
});
fs.writeFileSync(destino, PNG.sync.write(folha));
console.log('\nfolha:', destino);
