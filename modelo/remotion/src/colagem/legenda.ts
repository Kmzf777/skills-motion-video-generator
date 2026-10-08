// LEGENDA EM DOIS SISTEMAS, como nas referências de motion de colagem (medido em
// 07/10/2026).
//
//   A — pílula: 1 a 4 palavras, corte seco na palavra, some sozinha. É o conectivo.
//   B — colagem: a palavra-conceito vira objeto da cena (Dymo, serifa, marcador,
//       recorte) e FICA na cena enquanto ela existir.
//
// Regra que as referências seguem e este arquivo garante: UMA palavra falada vai para
// A ou para B, nunca para os dois. E A não pode estar na tela quando um B entra: a
// pílula some no quadro em que a colagem bate.
//
// O tempo de cada palavra vem de `motion/pecas/<NN-tema>/palavras.json`, produzido por
// `motion/ferramentas/alinhar_forcado.py` (fusão whisper + alinhamento forçado), e o
// TEXTO vem do roteiro -- o whisper quebra acento.

export type Palavra = {i: number; texto: string; inicio: number; fim: number};
export type Faixa = {de: number; ate: number; inicio: number; fim: number; texto: string};
export type BlocoA = {texto: string; inicio: number; fim: number; palavras: number[]};

/** Chave de comparação: sem acento, minúscula, só letras e dígitos. */
export const norm = (s: string) =>
  s.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');

/**
 * Cursor sobre a narração. Os trechos são procurados EM ORDEM a partir do cursor,
 * porque palavra repete: declarar fora de ordem acha a ocorrência errada, então
 * `b()`, `mudo()` e `t()` lançam se não acharem adiante.
 */
export class Roteiro {
  private cursor = 0;
  readonly emB = new Set<number>();
  readonly mudas = new Set<number>();
  constructor(readonly palavras: Palavra[]) {}

  private achar(trecho: string): Faixa {
    const alvo = trecho.split(/\s+/).map(norm).filter(Boolean);
    if (alvo.length === 0) throw new Error(`Roteiro: trecho vazio ("${trecho}")`);
    for (let i = this.cursor; i <= this.palavras.length - alvo.length; i++) {
      if (alvo.every((w, k) => norm(this.palavras[i + k].texto) === w)) {
        const de = i;
        const ate = i + alvo.length - 1;
        this.cursor = ate + 1;
        return {de, ate, inicio: this.palavras[de].inicio, fim: this.palavras[ate].fim,
                texto: this.palavras.slice(de, ate + 1).map((p) => p.texto).join(' ')};
      }
    }
    throw new Error(`Roteiro: "${trecho}" não encontrado a partir da palavra ${this.cursor}`);
  }

  /** Trecho que vira COLAGEM (B). Sai da pílula. */
  b(trecho: string): Faixa {
    const f = this.achar(trecho);
    for (let i = f.de; i <= f.ate; i++) this.emB.add(i);
    return f;
  }

  /** Trecho que a colagem já disse por outro nome: não vai nem para A nem para B. */
  mudo(trecho: string): Faixa {
    const f = this.achar(trecho);
    for (let i = f.de; i <= f.ate; i++) this.mudas.add(i);
    return f;
  }

  /** Só a marcação de tempo (para gesto/som), sem mudar o destino da palavra. */
  t(trecho: string): Faixa {
    return this.achar(trecho);
  }

  /**
   * Início (s) da `n`-ésima `palavra` dentro de uma faixa — para gesto, câmera ou som
   * que bate numa palavra do MEIO de um trecho. Nenhum tempo das cenas é escrito à mão:
   * realinhar a narração move inícios de frase em até 0,7 s, e cada segundo digitado
   * ficaria para trás. Lança se não achar.
   */
  em(f: Faixa, palavra: string, n = 1): number {
    let k = 0;
    for (let i = f.de; i <= f.ate; i++) {
      if (norm(this.palavras[i].texto) === norm(palavra) && ++k === n) return this.palavras[i].inicio;
    }
    throw new Error(`em(): "${palavra}" (${n}ª) não está em "${f.texto}"`);
  }

  /** Início da palavra seguinte à faixa: até onde a fala do trecho ocupa o tempo. */
  depois(f: Faixa): number {
    return this.palavras[f.ate + 1]?.inicio ?? f.fim + 0.4;
  }
}

const PONTUACAO_FINAL = /[.,!?:;…]$/;

/** Palavras que não podem fechar um bloco: a leitura fica pendurada ("POR ISSO A"). */
const FRACAS = new Set(['a', 'o', 'as', 'os', 'um', 'uma', 'de', 'do', 'da', 'dos', 'das', 'no', 'na', 'nos', 'nas',
  'em', 'e', 'que', 'pra', 'para', 'por', 'com', 'se', 'ate', 'ao', 'aos', 'pelo', 'pela', 'num', 'numa',
  // determinante e possessivo também penduram a leitura: "FIM DESSE / VÍDEO"
  'desse', 'dessa', 'deste', 'desta', 'esse', 'essa', 'este', 'esta', 'seu', 'sua', 'seus', 'suas', 'nosso', 'nossa',
  'meu', 'minha', 'todo', 'toda', 'cada', 'mais', 'muito']);

/**
 * Parte uma sequência de palavras em blocos de no máximo `maxChars` caracteres e
 * `maxPalavras` palavras, de tamanhos parecidos, evitando bloco que termina em palavra
 * fraca. Programação dinâmica: a sequência tem no máximo uma dúzia de palavras.
 */
function particionar(
  textos: string[], maxChars: number, maxPalavras: number,
  inicios: number[] = [], minimo = 0.3, fins: number[] = [],
): number[][] {
  const n = textos.length;
  const chars = (a: number, b: number) => textos.slice(a, b).join(' ').length;
  // respiro DENTRO do bloco: a voz fecha a ideia e o texto não ("COMPRA PODE SER")
  const respiro = (a: number, b: number) => {
    let k = 0;
    for (let j = a; j < b - 1 && fins.length; j++) k += Math.max(0, inicios[j + 1] - fins[j] - 0.12);
    return k;
  };
  // quanto tempo o bloco [a,b) fica na tela: do início dele ao início do seguinte
  const dura = (a: number, b: number) =>
    inicios.length ? (b < n ? inicios[b] : inicios[n - 1] + 0.4) - inicios[a] : Infinity;
  const custo = (a: number, b: number, ultimo: boolean) => {
    const c = chars(a, b);
    let k = 0;
    if (b - a > maxPalavras) k += 1e6;
    if (c > maxChars) k += 1e4 * (c - maxChars);
    if (!ultimo && FRACAS.has(norm(textos[b - 1]))) k += 400;
    if (b - a === 1 && FRACAS.has(norm(textos[a]))) k += 600;
    // bloco que pisca (menos de `minimo` na tela) não dá para ler: "MAS" por 0,11 s
    if (dura(a, b) < minimo) k += 3000 * (minimo - dura(a, b));
    k += 800 * respiro(a, b);
    return k + (maxChars - c) ** 2 * 0.3;
  };
  const melhor: number[] = Array(n + 1).fill(Infinity);
  const corte: number[] = Array(n + 1).fill(0);
  melhor[0] = 0;
  for (let b = 1; b <= n; b++) {
    for (let a = Math.max(0, b - maxPalavras); a < b; a++) {
      const v = melhor[a] + custo(a, b, b === n);
      if (v < melhor[b]) {
        melhor[b] = v;
        corte[b] = a;
      }
    }
  }
  const blocos: number[][] = [];
  for (let b = n; b > 0; b = corte[b]) blocos.unshift(Array.from({length: b - corte[b]}, (_, k) => corte[b] + k));
  return blocos;
}

/** Blocos da pílula A: o que não é B nem mudo, partido em leitura natural. */
export function blocosA(
  palavras: Palavra[],
  emB: Set<number>,
  mudas: Set<number> = new Set(),
  opc = {maxChars: 16, maxPalavras: 4, pausa: 0.3, minimo: 0.3, cauda: 0.22},
): BlocoA[] {
  const fora = (i: number) => emB.has(i) || mudas.has(i);
  // 1) segmentos: corridas de palavras A, quebradas em pontuação, pausa ou colagem
  const segmentos: number[][] = [];
  let atual: number[] = [];
  for (let i = 0; i < palavras.length; i++) {
    if (fora(i)) {
      if (atual.length) segmentos.push(atual);
      atual = [];
      continue;
    }
    const ant = atual[atual.length - 1];
    const quebra =
      (ant !== undefined && PONTUACAO_FINAL.test(palavras[ant].texto)) ||
      (ant !== undefined && palavras[i].inicio - palavras[ant].fim > opc.pausa);
    if (quebra && atual.length) {
      segmentos.push(atual);
      atual = [];
    }
    atual.push(i);
  }
  if (atual.length) segmentos.push(atual);
  // 2) cada segmento vira blocos equilibrados
  const grupos: number[][] = segmentos.flatMap((seg) =>
    particionar(seg.map((i) => palavras[i].texto), opc.maxChars, opc.maxPalavras,
      seg.map((i) => palavras[i].inicio), opc.minimo, seg.map((i) => palavras[i].fim))
      .map((g) => g.map((k) => seg[k])),
  );

  const blocos: BlocoA[] = grupos.map((g) => ({
    texto: g.map((i) => palavras[i].texto).join(' ').toUpperCase(),
    inicio: palavras[g[0]].inicio,
    fim: palavras[g[g.length - 1]].fim + opc.cauda,
    palavras: g,
  }));
  for (let k = 0; k < blocos.length; k++) {
    const ultimo = blocos[k].palavras[blocos[k].palavras.length - 1];
    // a pílula nunca invade o próximo bloco nem a entrada de um B
    const proxB = palavras.findIndex((p, i) => i > ultimo && emB.has(i));
    const limites = [blocos[k + 1]?.inicio, proxB >= 0 ? palavras[proxB].inicio : undefined]
      .filter((v): v is number => v !== undefined);
    if (limites.length) blocos[k].fim = Math.min(blocos[k].fim, ...limites);
    if (blocos[k].fim - blocos[k].inicio < opc.minimo) {
      const teto = limites.length ? Math.min(...limites) : blocos[k].inicio + opc.minimo;
      blocos[k].fim = Math.min(teto, blocos[k].inicio + opc.minimo);
    }
  }
  return blocos;
}

/** O bloco A visível no instante s (segundos), ou null. */
export function blocoNoInstante(blocos: BlocoA[], s: number): BlocoA | null {
  for (const b of blocos) if (s >= b.inicio && s < b.fim) return b;
  return null;
}
