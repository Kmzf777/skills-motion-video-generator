// Portão "nenhum segundo digitado" da peça modelo: as duas varreduras da fase 07
// (07-montagem.md, passo 3) rodando como teste, mais a prova de que o FIM vem de PALAVRAS.
//
// PEÇA NOVA: copie para `tests/<NN-tema>-tempos.test.ts` e troque `_modelo` em PASTA.

import fs from 'node:fs';
import path from 'node:path';
import {describe, expect, it} from 'vitest';

const PASTA = path.join(__dirname, '..', 'src', 'pecas', '_modelo'); // <- peça

/** roteiro.ts: número solto em CENA_INICIO, TROCA ou constante. */
const RE_ROTEIRO = /([[,:=]) *([0-9]*\.[0-9]+|[1-9][0-9]*) *[\],};]/;
/** .tsx: fq(n) fora de soma, q:, ini=, fora=, tempo de efeito e constante decimal. */
const RE_TSX =
  /(^|[^-+ ]) *fq\( *[0-9]|(^|[^A-Za-z0-9_])q: *[1-9]|(ini|fora)=\{ *[1-9]|\['[a-z0-9-]+', *([0-9]*\.[0-9]*[1-9]|[1-9])|(const|let) +[A-Za-z_][A-Za-z0-9_]* *= *[0-9]*\.[0-9]+ *;/;

/**
 * As únicas linhas legítimas (07-montagem.md):
 *   ['batimento', 0.05, …] -- contado do zero da peça, ANTES da primeira palavra: não anda
 *                             quando a narração é realinhada;
 *   const base = 0.2       -- volume da trilha, não tempo.
 */
const EXCECOES = [/\['batimento', *0\.05,/, /const base = 0\.2;/];

/** Linhas que casam a regex e não são exceção, como "arquivo:linha: texto". */
export function tempoDigitado(arquivo: string, texto: string, re: RegExp): string[] {
  return texto.split('\n').flatMap((linha, i) =>
    re.test(linha) && !EXCECOES.some((e) => e.test(linha)) ? [`${arquivo}:${i + 1}: ${linha.trim()}`] : []);
}

const ler = (f: string) => fs.readFileSync(path.join(PASTA, f), 'utf8');

describe('nenhum segundo digitado', () => {
  it('roteiro.ts não tem número absoluto', () => {
    expect(tempoDigitado('roteiro.ts', ler('roteiro.ts'), RE_ROTEIRO)).toEqual([]);
  });

  it('as .tsx da peça não têm tempo absoluto (fora as duas exceções)', () => {
    const tsx = fs.readdirSync(PASTA).filter((f) => f.endsWith('.tsx'));
    expect(tsx.length).toBeGreaterThanOrEqual(4);
    expect(tsx.flatMap((f) => tempoDigitado(f, ler(f), RE_TSX))).toEqual([]);
  });

  it('as duas exceções existem e são as únicas linhas que a varredura acha', () => {
    const achadas = fs.readdirSync(PASTA).filter((f) => f.endsWith('.tsx'))
      .flatMap((f) => ler(f).split('\n').filter((l) => RE_TSX.test(l)));
    expect(achadas.every((l) => EXCECOES.some((e) => e.test(l)))).toBe(true);
  });

  it('FIM sai da última palavra de PALAVRAS, não de um literal', () => {
    const linha = ler('roteiro.ts').split('\n').find((l) => /export const FIM\b/.test(l)) ?? '';
    expect(linha).toMatch(/PALAVRAS\[PALAVRAS\.length - 1\]\.fim/);
    expect(linha).not.toMatch(/FIM *= *[0-9]/);
  });

  it('mutação: fq(4.2) numa cena e FIM = 11.9 digitado reprovam', () => {
    expect(tempoDigitado('cenas.tsx', "  const tres = fq(4.2);", RE_TSX)).toHaveLength(1);
    expect(tempoDigitado('cenas.tsx', "  <Dymo q={q} ini={fq(4.2)} texto=\"X\" />", RE_TSX)).toHaveLength(1);
    expect(tempoDigitado('cenas.tsx', "  {q: 126, x: 0, y: 0, zoom: 1, rot: 0},", RE_TSX)).toHaveLength(1);
    expect(tempoDigitado('Sons.tsx', "  ['pop', 3.5, 0.5],", RE_TSX)).toHaveLength(1);
    expect(tempoDigitado('roteiro.ts', 'export const FIM = 11.9;', RE_ROTEIRO)).toHaveLength(1);
    expect(tempoDigitado('roteiro.ts', 'export const CENA_INICIO = [0, 3.5, 8.9];', RE_ROTEIRO)).toHaveLength(1);
    // e o derivado passa
    expect(tempoDigitado('cenas.tsx', '  const tres = fq(S1.tres.inicio) + 6;', RE_TSX)).toEqual([]);
  });
});
