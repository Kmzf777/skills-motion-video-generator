// Limites da pílula (blocosA) numa frase longa: 4 palavras, 16 caracteres, nada de
// bloco-relâmpago (< 0,3 s na tela) e nada de bloco que atravessa respiro.
//
// `particao` roda blocosA com os padrões do motor, ou com uma opção trocada: é o que prova,
// por mutação, que cada teste pega o limite que diz pegar. Mutação no código-fonte
// (maxPalavras: 5, maxChars: 24, minimo: 0.05 em legenda.ts) derruba o bloco de cima.

import {describe, expect, it} from 'vitest';
import {blocosA, type Palavra} from '../src/colagem/legenda';
import {AREA_SEGURA, ALTURA_PILULA, yDaPilula} from '../src/colagem/area-segura';

const PADRAO = {maxChars: 16, maxPalavras: 4, pausa: 0.3, minimo: 0.3, cauda: 0.22};

/** Palavras com tempos dados: [texto, inicio, fim]. */
const P = (ps: Array<[string, number, number]>): Palavra[] => ps.map(([texto, inicio, fim], i) => ({i, texto, inicio, fim}));
/** Frase corrida: cada palavra dura `passo` e começa logo após a anterior. */
const corrida = (txt: string, passo = 0.25, t0 = 0) =>
  P(txt.split(' ').map((w, k): [string, number, number] => [w, t0 + k * passo, t0 + k * passo + passo * 0.9]));

/** Sem troca, usa os PADRÕES do motor (é neles que a mutação do código-fonte bate). */
const particao = (ps: Palavra[], troca: Partial<typeof PADRAO> = {}) =>
  Object.keys(troca).length ? blocosA(ps, new Set(), new Set(), {...PADRAO, ...troca}) : blocosA(ps, new Set(), new Set());

const FRASE = 'cada palavra importante vira colagem e o resto passa aqui embaixo devagar sem pressa nenhuma';

const maxPalavras = (ps: Palavra[], o = {}) => Math.max(...particao(ps, o).map((b) => b.palavras.length));
const maxChars = (ps: Palavra[], o = {}) => Math.max(...particao(ps, o).map((b) => b.texto.length));

/**
 * Palavra-relâmpago: "mas" dura 0,08 s e a seguinte entra 0,02 s depois. Não cabe com
 * "extraordinário" (18 caracteres) e só junta com "Sabe" atravessando um respiro de
 * 0,29 s; sem a trava do mínimo, o mais barato seria deixá-la sozinha, 0,1 s na tela.
 */
const RELAMPAGO = P([['Sabe', 0, 0.3], ['mas', 0.59, 0.67], ['extraordinário', 0.69, 1.2], ['agora', 1.22, 1.5]]);
/** Cinco palavras curtas (14 caracteres): só o limite de 4 palavras impede um bloco único. */
const CURTAS = corrida('eu vi tu ri já');
/** Respiro de 0,25 s DENTRO do segmento (abaixo da pausa de quebra de 0,3 s). */
const RESPIRO = P([['Até', 0, 0.2], ['um', 0.22, 0.35], ['pouco', 0.37, 0.6], ['compra', 0.62, 0.9],
  ['pode', 1.15, 1.3], ['ser', 1.32, 1.45], ['bom', 1.47, 1.7]]);

const menorDuracao = (ps: Palavra[], o = {}) => Math.min(...particao(ps, o).map((b) => b.fim - b.inicio));
/** Algum bloco tem dentro dele o vão de mais de 0,2 s entre "compra" e "pode"? */
const atravessaRespiro = (ps: Palavra[], o = {}) => particao(ps, o).some((b) => b.palavras.includes(3) && b.palavras.includes(4));

describe('blocosA: limites na frase longa', () => {
  it('nunca passa de 4 palavras', () => {
    expect(maxPalavras(corrida(FRASE))).toBeLessThanOrEqual(4);
    expect(maxPalavras(CURTAS)).toBeLessThanOrEqual(4);
  });
  it('nunca passa de 16 caracteres', () => expect(maxChars(corrida(FRASE))).toBeLessThanOrEqual(16));
  it('nenhum bloco-relâmpago: todo bloco fica ao menos 0,3 s', () => expect(menorDuracao(RELAMPAGO)).toBeGreaterThanOrEqual(0.3 - 1e-9));
  it('nenhum bloco atravessa o respiro', () => expect(atravessaRespiro(RESPIRO)).toBe(false));
  it('a frase inteira é coberta, em ordem e sem repetir palavra', () => {
    const ps = corrida(FRASE);
    expect(particao(ps).flatMap((b) => b.palavras)).toEqual(ps.map((p) => p.i));
  });
});

describe('blocosA: mutação -- afrouxar cada limite tem que quebrar o teste dele', () => {
  it('maxPalavras: 5 deixa passar bloco de 5 palavras', () => expect(maxPalavras(CURTAS, {maxPalavras: 5})).toBeGreaterThan(4));
  it('maxChars: 24 deixa passar bloco de mais de 16 caracteres', () => expect(maxChars(corrida(FRASE), {maxChars: 24})).toBeGreaterThan(16));
  it('minimo: 0.05 deixa passar bloco-relâmpago', () => expect(menorDuracao(RELAMPAGO, {minimo: 0.05})).toBeLessThan(0.3));
});

describe('área segura', () => {
  it('os números do contrato', () => {
    expect(AREA_SEGURA.organico).toEqual({x0: 140, x1: 940, y0: 96, y1: 1613});
    expect(AREA_SEGURA.anuncio).toEqual({x0: 65, x1: 1015, y0: 269, y1: 1248});
  });
  it('orgânico (padrão): pílula em 1500, inteira dentro da área', () => {
    expect(yDaPilula()).toBe(1500);
    expect(yDaPilula('organico') + ALTURA_PILULA / 2).toBeLessThanOrEqual(AREA_SEGURA.organico.y1);
  });
  it('anúncio: a pílula de 76 px fica inteira acima de y 1248 (centro <= 1210), mesmo pedindo 1500', () => {
    expect(ALTURA_PILULA).toBe(76);
    for (const y of [undefined, 1500, 1900]) {
      const c = yDaPilula('anuncio', y);
      expect(c).toBeLessThanOrEqual(1210);
      expect(c + ALTURA_PILULA / 2).toBeLessThanOrEqual(1248);
      expect(c - ALTURA_PILULA / 2).toBeGreaterThanOrEqual(269);
    }
  });
});
