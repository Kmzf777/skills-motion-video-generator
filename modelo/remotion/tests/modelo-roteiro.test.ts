// Portão de A/B e de tempo da peça modelo.
//
// PEÇA NOVA: copie este arquivo para `tests/<NN-tema>-roteiro.test.ts`, troque `_modelo`
// por `<NN-tema>` no import e atualize o FIM esperado (penúltimo teste).

import {describe, expect, it} from 'vitest';
import {BLOCOS_A, CENA_INICIO, EM_B, FIM, MUDAS, PALAVRAS, TROCA} from '../src/pecas/_modelo/roteiro';

describe('peça modelo — roteiro e legendas', () => {
  it('nenhuma palavra em A e B ao mesmo tempo', () => {
    const emA = new Set(BLOCOS_A.flatMap((b) => b.palavras));
    for (const i of EM_B) expect(emA.has(i)).toBe(false);
    for (const i of MUDAS) expect(emA.has(i)).toBe(false);
  });

  it('toda palavra falada aparece em A, em B, ou foi silenciada de propósito', () => {
    const emA = new Set(BLOCOS_A.flatMap((b) => b.palavras));
    const soltas = PALAVRAS.filter((p) => !emA.has(p.i) && !EM_B.has(p.i) && !MUDAS.has(p.i));
    expect(soltas.map((p) => p.texto)).toEqual([]);
  });

  it('os índices do palavras.json batem com a posição (i = 0, 1, 2, ...)', () => {
    PALAVRAS.forEach((p, k) => expect(p.i).toBe(k));
  });

  it('pílula: até 4 palavras e 16 caracteres, ao menos 0,2 s, sem se sobrepor', () => {
    for (let k = 0; k < BLOCOS_A.length; k++) {
      const b = BLOCOS_A[k];
      expect(b.palavras.length).toBeGreaterThanOrEqual(1);
      expect(b.palavras.length, b.texto).toBeLessThanOrEqual(4);
      expect(b.texto.length, b.texto).toBeLessThanOrEqual(16);
      // 0,2 s = 6 quadros: menos que isso pisca e não se lê
      expect(b.fim - b.inicio, b.texto).toBeGreaterThanOrEqual(0.2);
      if (k > 0) expect(b.inicio).toBeGreaterThanOrEqual(BLOCOS_A[k - 1].fim - 1e-9);
    }
  });

  it('as cenas começam em ordem, dentro da narração, e as trocas internas caem dentro da peça', () => {
    expect(CENA_INICIO[0]).toBe(0);
    for (let k = 1; k < CENA_INICIO.length; k++) expect(CENA_INICIO[k]).toBeGreaterThan(CENA_INICIO[k - 1]);
    expect(CENA_INICIO[CENA_INICIO.length - 1]).toBeLessThan(FIM);
    for (const [nome, s] of Object.entries(TROCA)) {
      expect(s, `TROCA.${nome}`).toBeGreaterThan(0);
      expect(s, `TROCA.${nome}`).toBeLessThan(FIM);
    }
  });

  it('FIM é DERIVADO: última palavra + 0,5 s, arredondado para cima ao décimo', () => {
    const ultima = PALAVRAS[PALAVRAS.length - 1].fim;
    expect(FIM).toBeGreaterThanOrEqual(ultima + 0.5);
    expect(FIM).toBeLessThan(ultima + 0.6 + 1e-9);
    expect(Math.round(FIM * 10)).toBeCloseTo(FIM * 10, 9);
    // O valor esperado desta peça. Peça nova: troque pelo dela (a peça de origem
    // conferiu assim que o FIM derivado reproduzia a duração entregue).
    expect(FIM).toBe(11.9);
  });

  it('imprime a pílula para revisão', () => {
    console.log(BLOCOS_A.map((b) => `${b.inicio.toFixed(2)}-${b.fim.toFixed(2)} ${b.texto}`).join('\n'));
  });
});
