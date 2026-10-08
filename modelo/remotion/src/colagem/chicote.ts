// O CHICOTE (whip pan) entre cenas e entre fases de uma cena, em funções puras.
//
// Toda troca de enquadramento tem chicote ou cobertura de papel: corte seco de câmera
// é salto. O chicote é a imagem que SAI e a que ENTRA andando COLADAS, uma tela
// inteira em 12 quadros, sob borrão direcional (ver `Palco` em palco.tsx). Cada lado
// fica congelado no seu último/primeiro quadro durante a janela -- sob 60 px de borrão
// ninguém vê 5 quadros parados.
//
// Medido na peça de origem (07/10/2026): quando a cena que sai andava sozinha 520 px,
// o fundo da raiz aparecia numa faixa preta de até meia tela, nas 10 trocas. O defeito
// só aparece DENTRO da janela: a conferência precisa de still no meio do chicote.
//
// A renderização (as duas cenas lado a lado) fica no `Peca.tsx` de cada peça; aqui
// só o tempo, para poder ser testado.

export type Eixo = 'x' | 'y';
export type Chicote = {q: number; eixo: Eixo; dir: 1 | -1};
export type ChicoteNoQuadro = Chicote & {u: number; k: number};

/** Quadros antes e depois da troca que a janela do chicote ocupa (12 no total). */
export const JANELA_ANTES = 6;
export const JANELA_DEPOIS = 5;

/**
 * O chicote ativo no quadro q, ou null. `u` vai de 0 a 1 devagar-rápido-devagar (a
 * velocidade máxima cai na troca) e `k` é o borrão, máximo na troca.
 */
export function chicoteEm(q: number, chicotes: Chicote[]): ChicoteNoQuadro | null {
  for (const c of chicotes) {
    const d = q - c.q;
    if (d >= -JANELA_ANTES && d <= JANELA_DEPOIS) {
      const u = 0.5 - 0.5 * Math.cos((Math.PI * (d + JANELA_ANTES)) / (JANELA_ANTES + JANELA_DEPOIS));
      return {...c, u, k: Math.max(0, 1 - Math.abs(d + 0.5) / 6.5)};
    }
  }
  return null;
}

/** Índice da cena que vale no quadro q, dados os quadros de início de cada cena. */
export function cenaEm(q: number, limites: number[]): number {
  let i = 0;
  while (i + 1 < limites.length && q >= limites[i + 1]) i++;
  return i;
}

/**
 * Confere uma lista de chicotes contra a duração da peça: em ordem, dentro da peça e
 * sem janelas sobrepostas (duas trocas a menos de 12 quadros uma da outra fariam
 * `chicoteEm` ignorar a segunda). Devolve a lista de problemas; vazia = ok.
 */
export function problemasDosChicotes(chicotes: Chicote[], duracao: number): string[] {
  const erros: string[] = [];
  chicotes.forEach((c, i) => {
    if (!Number.isInteger(c.q)) erros.push(`chicote ${i}: quadro ${c.q} não é inteiro`);
    if (c.q - JANELA_ANTES < 0 || c.q + JANELA_DEPOIS >= duracao) {
      erros.push(`chicote ${i} (q=${c.q}): a janela sai da peça (0..${duracao - 1})`);
    }
    const ant = chicotes[i - 1];
    if (ant && c.q - ant.q <= JANELA_ANTES + JANELA_DEPOIS) {
      erros.push(`chicotes ${i - 1} e ${i} (q=${ant.q} e ${c.q}): janelas sobrepostas ou fora de ordem`);
    }
  });
  return erros;
}
