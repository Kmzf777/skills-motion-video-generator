import {describe, expect, it} from 'vitest';
import {cameraCena, cameraEm, deriva, desfoqueDoPlano, transformarPlano, tremor, velocidade} from '../src/colagem/camera';
import {blocoNoInstante, blocosA, Roteiro, type Palavra} from '../src/colagem/legenda';
import {carimbo, esmagar, posterizar} from '../src/colagem/movimento-colagem';

describe('câmera', () => {
  const chaves = [
    {q: 0, x: 0, y: 0, zoom: 1, rot: 0},
    {q: 30, x: 100, y: -50, zoom: 1.2, rot: 2},
  ];
  it('interpola entre chaves e segura nas pontas', () => {
    expect(cameraEm(-5, chaves).x).toBe(0);
    expect(cameraEm(30, chaves).zoom).toBeCloseTo(1.2);
    expect(cameraEm(99, chaves).x).toBe(100);
    const meio = cameraEm(15, chaves);
    expect(meio.x).toBeGreaterThan(0);
    expect(meio.x).toBeLessThan(100);
  });

  it('plano de profundidade 0 não anda; plano 2 anda o dobro', () => {
    const cam = {x: 40, y: 10, zoom: 1.1, rot: 0};
    expect(transformarPlano(cam, 0).escala).toBeCloseTo(1);
    expect(transformarPlano(cam, 0).transform).toContain('translate(0.00px, 0.00px)');
    expect(transformarPlano(cam, 2).transform).toContain('translate(-80.00px, -20.00px)');
    expect(transformarPlano(cam, 2).escala).toBeCloseTo(1.2);
  });

  it('primeiro plano desfoca, plano da cena fica nítido', () => {
    expect(desfoqueDoPlano(1)).toBe(0);
    expect(desfoqueDoPlano(2.5)).toBeGreaterThanOrEqual(10);
  });

  it('a deriva nunca deixa a câmera parada', () => {
    for (let q = 1; q < 600; q++) {
      expect(velocidade(deriva(q - 1, 'c'), deriva(q, 'c'))).toBeGreaterThan(0);
    }
  });

  it('a câmera de cena também nunca para, mesmo depois da última chave', () => {
    for (let q = 41; q < 200; q++) {
      expect(velocidade(cameraCena(q - 1, chaves, 'c1'), cameraCena(q, chaves, 'c1'))).toBeGreaterThan(0);
    }
  });

  it('tremor só existe na janela do impacto', () => {
    expect(tremor(9, 10).x).toBe(0);
    expect(Math.abs(tremor(10, 10).x) + Math.abs(tremor(10, 10).y)).toBeGreaterThan(0);
    expect(tremor(13, 10).x).toBe(0);
  });
});

describe('movimento de colagem', () => {
  it('posteriza em passos de 3 quadros', () => {
    expect(posterizar(10, 3)).toBe(9);
    expect(posterizar(11, 3)).toBe(9);
    expect(posterizar(12, 3)).toBe(12);
  });
  it('carimbo ultrapassa no máximo 12% e assenta em 1', () => {
    expect(carimbo(9, 10).visivel).toBe(false);
    expect(carimbo(10, 10).escala).toBeLessThanOrEqual(1.12);
    expect(carimbo(14, 10).escala).toBe(1);
  });
  it('squash chega largo e achatado e assenta', () => {
    const e = esmagar(20, 20);
    expect(e.sx).toBeGreaterThan(1);
    expect(e.sy).toBeLessThan(1);
    expect(esmagar(24, 20).sx).toBeCloseTo(1);
  });
});

const P = (txt: string, t0 = 0, passo = 0.3): Palavra[] =>
  txt.split(' ').map((w, i) => ({i, texto: w, inicio: t0 + i * passo, fim: t0 + i * passo + passo * 0.85}));

describe('legenda A/B', () => {
  it('nenhuma palavra vai para A e B ao mesmo tempo', () => {
    const ps = P('Respira! Não precisa jogar nada fora. Mas até o fim desse vídeo você vai saber se o seu é bom.');
    const r = new Roteiro(ps);
    r.b('Respira!');
    r.b('se o seu é bom.');
    const a = blocosA(ps, r.emB, r.mudas);
    const emA = new Set(a.flatMap((b) => b.palavras));
    for (const i of r.emB) expect(emA.has(i)).toBe(false);
  });

  it('pílula tem no máximo 4 palavras/16 caracteres e quebra na pontuação', () => {
    const ps = P('Não precisa mudar de hábito. Mas até o fim');
    const a = blocosA(ps, new Set());
    for (const b of a) { expect(b.palavras.length).toBeLessThanOrEqual(4); expect(b.texto.length).toBeLessThanOrEqual(16); }
    expect(a.some((b) => b.texto.endsWith('HÁBITO.'))).toBe(true);
  });

  it('a pílula some no instante em que um B entra', () => {
    const ps = P('E tá tudo dentro do prazo.');
    const r = new Roteiro(ps);
    const prazo = r.b('dentro do prazo.');
    const a = blocosA(ps, r.emB, r.mudas);
    expect(blocoNoInstante(a, prazo.inicio + 0.01)).toBeNull();
  });

  it('procura em ordem: a segunda ocorrência exige cursor adiante', () => {
    const ps = P('simples não é simples');
    const r = new Roteiro(ps);
    expect(r.b('simples').de).toBe(0);
    expect(r.b('simples').de).toBe(3);
    expect(() => r.b('simples')).toThrow();
  });

  it('não fecha bloco em palavra fraca quando dá para evitar', () => {
    const ps = P('Por isso a gente só vende o que a gente mesmo');
    const a = blocosA(ps, new Set());
    const fracas = ['A', 'O', 'QUE', 'DE', 'PRA'];
    for (const b of a.slice(0, -1)) expect(fracas).not.toContain(b.texto.split(' ').pop());
  });

  it('mudo não aparece em lugar nenhum', () => {
    const ps = P('A primeira é no papel.');
    const r = new Roteiro(ps);
    r.mudo('A primeira é no');
    r.b('papel.');
    expect(blocosA(ps, r.emB, r.mudas)).toHaveLength(0);
  });

  it('em() acha a palavra do meio do trecho (sem acento nem pontuação) e lança se não achar', () => {
    const ps = P('Agora vem a régua. Cinco réguas do mesmo lote.');
    const r = new Roteiro(ps);
    const f = r.t('Agora vem a régua.');
    expect(r.em(f, 'regua')).toBeCloseTo(ps[3].inicio);
    const g = r.t('Cinco réguas do mesmo lote.');
    expect(r.em(g, 'lote')).toBeCloseTo(ps[8].inicio);
    expect(() => r.em(g, 'régua')).toThrow();
    expect(() => r.em(f, 'régua', 2)).toThrow();
  });

  it('depois() é o início da palavra seguinte, ou o fim + 0,4 s na última', () => {
    const ps = P('Salva esse vídeo.');
    const r = new Roteiro(ps);
    const a = r.t('Salva');
    expect(r.depois(a)).toBeCloseTo(ps[1].inicio);
    const b = r.t('esse vídeo.');
    expect(r.depois(b)).toBeCloseTo(ps[2].fim + 0.4);
  });

  it('trecho vazio é erro, não faixa fantasma', () => {
    const r = new Roteiro(P('qualquer coisa'));
    expect(() => r.t('   ')).toThrow();
  });
});
