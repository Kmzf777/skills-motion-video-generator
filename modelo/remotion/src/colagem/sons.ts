// Os EFEITOS sonoros da colagem: os nomes e as regras de tempo, em módulo puro.
//
// Os arquivos são gerados por `python motion/ferramentas/sons.py motion/pecas/<NN-tema>`
// em `public/sfx/<nome>.wav` (síntese com semente fixa: rodar duas vezes dá os mesmos
// bytes), junto com `trilha.wav` em seções que começam em frases da narração
// (`sons.json`). Se o gerador mudar a lista, mude `Efeito` aqui: um nome sem arquivo só
// aparece no meio do render, como 404, e mata a rodada.
//
// Regra das referências: UM som por entrada de colagem -- pop no texto e na letra
// recortada, fita no recorte, rabisco no traço (marcador, seta, elipse), carimbo +
// digitação no Dymo, thump no impacto com tremor, whoosh no objeto que cruza, rasgo na
// cobertura de papel, chicote na troca.

export type Efeito =
  | 'pop' | 'fita' | 'rabisco' | 'carimbo' | 'digitacao' | 'thump' | 'whoosh' | 'rasgo' | 'chicote'
  | 'brilho' | 'tick' | 'tink' | 'slide' | 'ding' | 'vento' | 'batimento' | 'drone'
  | 'nota1' | 'nota2' | 'nota3' | 'nota4' | 'golinho' | 'graos';

/** [efeito, segundo em que toca, volume 0..1]. O segundo é sempre DERIVADO do roteiro. */
export type Ef = [Efeito, number, number?];

/**
 * Quanto tempo (s) a JANELA de cada efeito fica montada -- teto de desempenho, não tempo
 * de evento: o arquivo acaba sozinho dentro dela. O drone dura a tensão inteira (sons.py
 * deriva: 1ª seção + 0,6 s) e o vento é longo, então os dois ficam abertos até o fim da
 * peça; nenhuma duração deles é digitada aqui. Os curtos cabem em 3 s (o mais longo, o
 * ding, tem 1,8 s). Efeito novo e longo no gerador: acrescente aqui com `Infinity`.
 */
export const DURACAO_EFEITO: Partial<Record<Efeito, number>> = {drone: Infinity, vento: Infinity};
export const DURACAO_PADRAO_EFEITO = 3;

/**
 * O chicote soa 0,16 s ANTES da troca: a janela do borrão começa 6 quadros antes dela
 * (ver chicote.ts), e o som tem que crescer junto com o borrão.
 */
export const somDeChicote = (troca: number, vol = 0.7): Ef => ['chicote', troca - 0.16, vol];

/**
 * Um pop por letra de um `Recortadas` que entra a cada `intervalo` quadros a partir de
 * `inicio` (s). Espaço não soa.
 */
export const somDeLetras = (texto: string, inicio: number, intervalo = 2, vol = 0.45, fps = 30): Ef[] =>
  [...texto].flatMap((ch, i): Ef[] => (ch === ' ' ? [] : [['pop', inicio + (i * intervalo) / fps, vol]]));

/** Cobertura de papel: o rasgo soa ~0,2 s antes da troca, enquanto a folha sobe. */
export const somDeCobertura = (troca: number, vol = 0.7): Ef => ['rasgo', troca - 0.21, vol];
