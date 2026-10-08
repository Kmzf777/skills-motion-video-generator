// Peça modelo — o roteiro falado, palavra a palavra, com o DESTINO de cada trecho.
//
//   r.b(...)    → vira colagem (sistema B) e sai da pílula
//   r.mudo(...) → a colagem já diz isso por outro nome; não aparece em lugar nenhum
//   r.t(...)    → só marca tempo (gesto, câmera, som); a palavra continua na pílula
//
// O que não é declarado vai para a pílula (sistema A). Os trechos são procurados EM
// ORDEM -- palavra repete --, então esta lista segue a narração.
//
// PEÇA NOVA: copie a pasta `_modelo` para `src/pecas/<NN-tema>/` e troque `00-exemplo`
// pelo `<NN-tema>` no import abaixo. Os tempos vêm de
// `motion/pecas/<NN-tema>/palavras.json` (motion/ferramentas/alinhar_forcado.py).
// O exemplo tem tempos FABRICADOS (não há narração gravada): servem para o motor
// compilar e desenhar, não como medida.

import palavrasJson from '../../../../pecas/00-exemplo/palavras.json';
import {blocosA, Roteiro, type Faixa, type Palavra} from '../../colagem/legenda';

export const PALAVRAS = palavrasJson as Palavra[];
const r = new Roteiro(PALAVRAS);

/**
 * Início (s) da `n`-ésima `palavra` dentro de uma faixa — para gesto, câmera ou som que
 * bate numa palavra do MEIO de um trecho. Lança se não achar. Nenhum tempo das cenas é
 * escrito à mão: realinhar a narração move palavras, e o segundo digitado fica para trás.
 */
export const em = (f: Faixa, palavra: string, n = 1): number => r.em(f, palavra, n);

/** Início da palavra seguinte à faixa: até onde a fala do trecho ocupa o tempo. */
export const depois = (f: Faixa): number => r.depois(f);

// ---------------------------------------------------------------- 1 gancho
export const S1 = {
  tres: r.b('Três segundos.'),
  tempo: r.t('É o tempo que você tem'),
  prender: r.b('pra prender alguém.'),
};
// ---------------------------------------------------------------- 2 conteúdo
export const S2 = {
  palavra: r.t('Palavra forte'),
  vira: r.b('vira colagem,'),
  escrita: r.b('escrita na hora'),
  dita: r.b('em que é dita.'),
  resto: r.t('O resto passa aqui embaixo.'),
};
// ---------------------------------------------------------------- 3 fecho
export const S3 = {
  noFim: r.t('No fim,'),
  marca: r.mudo('a sua marca.'),
  salva: r.b('Salva esse vídeo.'),
};

export const EM_B = r.emB;
export const MUDAS = r.mudas;
export const BLOCOS_A = blocosA(PALAVRAS, EM_B, MUDAS);

/** Início de cada cena (s): a fala que abre a cena. */
export const CENA_INICIO = [0, S2.palavra.inicio, S3.noFim.inicio];

/**
 * Fim da peça (s): a última palavra + 0,5 s para o fecho respirar, arredondado para cima
 * ao décimo. Derivado, não digitado -- e é a mesma conta do `DUR` de sons.py (contrato C4),
 * então trilha e vídeo têm a mesma duração.
 */
export const FIM = Math.ceil((PALAVRAS[PALAVRAS.length - 1].fim + 0.5) * 10) / 10;

/**
 * Trocas DENTRO de uma cena (s). A cena muda de fase e a raiz dá o chicote no mesmo
 * instante, então as duas leem daqui: dois números digitados em dois arquivos se
 * separam no primeiro realinhamento.
 */
export const TROCA = {
  /** "…é dita." → "O resto passa aqui embaixo.": a câmera desce para a pílula */
  resto: S2.resto.inicio - 0.1,
};
