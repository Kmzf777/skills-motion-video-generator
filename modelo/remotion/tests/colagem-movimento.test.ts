import {describe, expect, it} from 'vitest';
import {semente} from '../src/colagem/semente';
import {assentar, boil, carimbar} from '../src/colagem/movimento-colagem';

describe('semente', () => {
  it('é determinística por chave e fica em [0,1)', () => {
    const a = semente('xicara');
    const b = semente('xicara');
    const va = [a(), a(), a()];
    expect([b(), b(), b()]).toEqual(va);
    for (const v of va) {
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThan(1);
    }
  });

  it('chaves diferentes dão sequências diferentes', () => {
    expect(semente('xicara')()).not.toBe(semente('colher')());
  });
});

describe('assentar', () => {
  it('antes do início a peça não existe', () => {
    expect(assentar(9, 10, 'x').visivel).toBe(false);
  });

  it('entra grande e girada, e assenta em 6 quadros', () => {
    const ini = assentar(10, 10, 'x');
    expect(ini.visivel).toBe(true);
    expect(ini.escala).toBeCloseTo(1.04, 5);
    expect(Math.abs(ini.rot)).toBeGreaterThanOrEqual(2);
    expect(Math.abs(ini.rot)).toBeLessThanOrEqual(4);
    const fim = assentar(16, 10, 'x');
    expect(fim.escala).toBeCloseTo(1, 5);
    expect(Math.abs(fim.rot)).toBeLessThanOrEqual(0.6);
  });

  it('nunca afunda mais que 3% (sem elástico)', () => {
    for (let q = 10; q < 40; q++) {
      expect(assentar(q, 10, 'x').escala).toBeGreaterThanOrEqual(0.97);
    }
  });
});

describe('boil', () => {
  it('só muda a cada 3 quadros', () => {
    expect(boil(30, 'g')).toEqual(boil(31, 'g'));
    expect(boil(31, 'g')).toEqual(boil(32, 'g'));
  });

  it('variante em {0,1,2} e micro-rotação limitada', () => {
    for (let q = 0; q < 90; q++) {
      const b = boil(q, 'g');
      expect([0, 1, 2]).toContain(b.variante);
      expect(Math.abs(b.rot)).toBeLessThanOrEqual(0.6);
    }
  });

  it('varia ao longo do tempo', () => {
    const vs = new Set(Array.from({length: 30}, (_, i) => boil(i * 3, 'g').variante));
    expect(vs.size).toBeGreaterThan(1);
  });
});

describe('carimbar', () => {
  it('bate grande e assenta em 3 quadros', () => {
    expect(carimbar(20, 20).escala).toBeCloseTo(1.15, 5);
    expect(carimbar(23, 20).escala).toBeCloseTo(1, 5);
    expect(carimbar(19, 20).visivel).toBe(false);
  });
});
