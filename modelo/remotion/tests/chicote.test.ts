import {describe, expect, it} from 'vitest';
import {cenaEm, chicoteEm, JANELA_ANTES, JANELA_DEPOIS, problemasDosChicotes, type Chicote} from '../src/colagem/chicote';

const CH: Chicote[] = [{q: 100, eixo: 'x', dir: -1}, {q: 200, eixo: 'y', dir: 1}];

describe('chicote', () => {
  it('a janela tem 12 quadros em volta da troca e fora dela não há chicote', () => {
    expect(chicoteEm(100 - JANELA_ANTES - 1, CH)).toBeNull();
    expect(chicoteEm(100 + JANELA_DEPOIS + 1, CH)).toBeNull();
    let n = 0;
    for (let q = 80; q < 120; q++) if (chicoteEm(q, CH)) n++;
    expect(n).toBe(JANELA_ANTES + JANELA_DEPOIS + 1);
  });

  it('u vai de 0 a 1 sem voltar e o borrão é máximo na troca', () => {
    let u = -1;
    for (let q = 100 - JANELA_ANTES; q <= 100 + JANELA_DEPOIS; q++) {
      const c = chicoteEm(q, CH)!;
      expect(c.u).toBeGreaterThanOrEqual(u);
      u = c.u;
    }
    expect(chicoteEm(100 - JANELA_ANTES, CH)!.u).toBeCloseTo(0);
    expect(chicoteEm(100 + JANELA_DEPOIS, CH)!.u).toBeCloseTo(1);
    const ks = Array.from({length: 12}, (_, k) => chicoteEm(100 - JANELA_ANTES + k, CH)!.k);
    expect(Math.max(...ks)).toBe(Math.max(chicoteEm(99, CH)!.k, chicoteEm(100, CH)!.k));
  });

  it('cenaEm escolhe a cena pelo quadro', () => {
    const lim = [0, 105, 268];
    expect(cenaEm(0, lim)).toBe(0);
    expect(cenaEm(104, lim)).toBe(0);
    expect(cenaEm(105, lim)).toBe(1);
    expect(cenaEm(400, lim)).toBe(2);
  });

  it('acusa janela fora da peça, fora de ordem e sobreposta', () => {
    expect(problemasDosChicotes(CH, 300)).toEqual([]);
    expect(problemasDosChicotes([{q: 3, eixo: 'x', dir: 1}], 300)).toHaveLength(1);
    expect(problemasDosChicotes([{q: 296, eixo: 'x', dir: 1}], 300)).toHaveLength(1);
    expect(problemasDosChicotes([{q: 100, eixo: 'x', dir: 1}, {q: 108, eixo: 'y', dir: 1}], 300)).toHaveLength(1);
    expect(problemasDosChicotes([{q: 200, eixo: 'x', dir: 1}, {q: 100, eixo: 'y', dir: 1}], 300)).toHaveLength(1);
  });
});
