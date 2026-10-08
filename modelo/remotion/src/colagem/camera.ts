// CÂMERA 2.5D da colagem: um caminho de câmera por cena e planos de profundidade.
//
// O que as referências de motion de colagem mostram, medido quadro a quadro em
// 07/10/2026: a câmera NUNCA para (a colagem do gancho sobe ~180 px entre 1,75 s e
// 2,0 s), e a profundidade vem de planos que andam em velocidades diferentes --
// papéis enormes e desfocados passando quase na lente, o mural no meio, o fundo devagar.
//
// Modelo: cada camada mora em coordenadas de QUADRO (1080x1920) com a câmera em
// repouso. A câmera tem deslocamento (x, y em px), zoom e rotação. Uma camada de
// profundidade p (0 = infinito, 1 = plano da cena, >1 = mais perto da lente) anda
// p vezes o deslocamento e amplia (zoom-1)*p. É o parallax de After Effects sem 3D.
//
// Tudo puro e de quadro: o mesmo quadro dá a mesma câmera (render determinístico).

import {semente} from './semente';

export type Cam = {x: number; y: number; zoom: number; rot: number};
export type Curva = 'suave' | 'rapida' | 'linear' | 'segura';
export type Chave = Cam & {q: number; curva?: Curva};

export const REPOUSO: Cam = {x: 0, y: 0, zoom: 1, rot: 0};
export const CENTRO = {x: 540, y: 960};

const suave = (t: number) => t * t * (3 - 2 * t);
const rapida = (t: number) => 1 - Math.pow(1 - t, 3);

function curvar(t: number, c: Curva = 'suave'): number {
  const u = Math.min(1, Math.max(0, t));
  if (c === 'linear') return u;
  if (c === 'rapida') return rapida(u);
  if (c === 'segura') return u < 1 ? 0 : 1;
  return suave(u);
}

/** Câmera no quadro q a partir de chaves ordenadas por q. A curva é a da chave de CHEGADA. */
export function cameraEm(q: number, chaves: Chave[]): Cam {
  if (chaves.length === 0) return REPOUSO;
  if (q <= chaves[0].q) return {...chaves[0]};
  for (let i = 1; i < chaves.length; i++) {
    const a = chaves[i - 1];
    const b = chaves[i];
    if (q <= b.q) {
      const t = curvar((q - a.q) / Math.max(1, b.q - a.q), b.curva);
      return {
        x: a.x + (b.x - a.x) * t,
        y: a.y + (b.y - a.y) * t,
        zoom: a.zoom + (b.zoom - a.zoom) * t,
        rot: a.rot + (b.rot - a.rot) * t,
      };
    }
  }
  return {...chaves[chaves.length - 1]};
}

/**
 * Deriva de mão: a câmera respira sempre, mesmo quando a cena "para".
 * Duas senoides por eixo com fase da semente — contínua, sem salto, determinística.
 */
export function deriva(q: number, chave: string, intensidade = 1): Cam {
  const s = semente(chave);
  const f = () => s() * Math.PI * 2;
  const [a, b, c, d, e] = [f(), f(), f(), f(), f()];
  const t = q / 30;
  return {
    x: intensidade * (5 * Math.sin(t * 0.9 + a) + 2.5 * Math.sin(t * 2.3 + b)),
    y: intensidade * (6 * Math.sin(t * 0.7 + c) + 2 * Math.sin(t * 1.9 + d)),
    zoom: intensidade * 0.004 * Math.sin(t * 0.5 + e),
    rot: intensidade * 0.35 * Math.sin(t * 0.6 + a + d),
  };
}

/** Tremor de impacto (carimbo): 3 quadros que decaem. Fora da janela é zero. */
export function tremor(q: number, inicio: number, amp = 14, quadros = 3): Cam {
  const k = q - inicio;
  if (k < 0 || k >= quadros) return {x: 0, y: 0, zoom: 0, rot: 0};
  const s = semente(`tremor#${inicio}#${k}`);
  const fade = 1 - k / quadros;
  return {
    x: (s() * 2 - 1) * amp * fade,
    y: (s() * 2 - 1) * amp * fade,
    zoom: 0.012 * fade,
    rot: (s() * 2 - 1) * 0.8 * fade,
  };
}

/**
 * Snap zoom em pulso: na palavra-colagem a câmera "fura" dz em 3 quadros e devolve
 * devagar (~10 quadros). Não acumula: dez pulsos seguidos não viram zoom de 50%.
 */
export function pulso(q: number, marcas: number[], dz = 0.05): Cam {
  let z = 0;
  for (const m of marcas) {
    const k = q - m;
    if (k < 0) continue;
    z = Math.max(z, k < 3 ? (dz * k) / 3 : dz * Math.exp(-(k - 3) / 10));
  }
  return {x: 0, y: 0, zoom: z, rot: 0};
}

/** Soma deslocamentos (zoom é somado como incremento sobre 1). */
export function somar(base: Cam, ...extras: Cam[]): Cam {
  return extras.reduce(
    (acc, e) => ({x: acc.x + e.x, y: acc.y + e.y, zoom: acc.zoom + e.zoom, rot: acc.rot + e.rot}),
    base,
  );
}

/**
 * A câmera de uma cena, como as cenas a montam: chaves + deriva (nunca parada) +
 * pulso nas palavras-colagem + tremor só nos impactos. Todos os quadros vêm do
 * roteiro (`fq(S1.x.inicio)`), nunca digitados.
 */
export function cameraCena(
  q: number, chaves: Chave[], chave: string, intensidade = 1, pulsos: number[] = [], tremores: number[] = [],
): Cam {
  return somar(cameraEm(q, chaves), deriva(q, chave, intensidade), pulso(q, pulsos), ...tremores.map((t) => tremor(q, t)));
}

/** Transformação CSS de uma camada de profundidade p, com origem no centro do quadro. */
export function transformarPlano(cam: Cam, p: number): {transform: string; escala: number} {
  const escala = Math.max(0.2, 1 + (cam.zoom - 1) * p);
  const tx = -cam.x * p;
  const ty = -cam.y * p;
  return {
    transform: `rotate(${cam.rot.toFixed(4)}deg) scale(${escala.toFixed(5)}) translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px)`,
    escala,
  };
}

/** Desfoque de profundidade: nítido até p=1,4; o primeiro plano (p≈2,5) borra ~12 px. */
export function desfoqueDoPlano(p: number): number {
  return p <= 1.4 ? 0 : Math.round((p - 1.4) * 11);
}

/** Velocidade da câmera entre q-1 e q, em px de tela: a câmera nunca para se > 0. */
export function velocidade(cam0: Cam, cam1: Cam): number {
  return Math.hypot(cam1.x - cam0.x, cam1.y - cam0.y) + Math.abs(cam1.zoom - cam0.zoom) * 1000 +
    Math.abs(cam1.rot - cam0.rot) * 20;
}
