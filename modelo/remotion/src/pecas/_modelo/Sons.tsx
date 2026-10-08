// Som da peça: narração, trilha em seções e UM efeito para cada entrada de colagem
// (pop no texto e na letra recortada, rabisco no traço, carimbo + digitação no Dymo,
// thump no impacto, rasgo na cobertura, chicote na troca).
//
// Nenhum tempo aqui é digitado: cada efeito lê a palavra (`em`, `S1.x.inicio`) ou a troca
// (`TROCA`, `CENA_INICIO`) que ele acompanha.
//
// Os arquivos vêm de `public/` da peça:
//   fonte/narracao.mp3  -- a narração final (fase 04)
//   sfx/trilha.wav      -- `python motion/ferramentas/sons.py motion/pecas/<NN-tema>`
//   sfx/<efeito>.wav    -- idem (nomes em src/colagem/sons.ts)
// TUDO é exigido: arquivo que falta derruba o render do vídeo com 404 -- é a trava que
// impede uma peça de sair muda (still e contato só registram o 404 no log). A única
// exceção é a composição de exemplo, que o `Raiz.tsx` envolve em `<SomTolerante>`
// (ver colagem/som-tolerante.tsx): sem narração gravada, ela toca só o que existe.

import {Audio} from '@remotion/media';
import React from 'react';
import {getStaticFiles, interpolate, Sequence, staticFile} from 'remotion';
import {useSomTolerante} from '../../colagem/som-tolerante';
import {DURACAO_EFEITO, DURACAO_PADRAO_EFEITO, somDeChicote, somDeCobertura, somDeLetras, type Ef} from '../../colagem/sons';
import {fq} from './apoio';
import {CENA_INICIO, em, FIM, PALAVRAS, S1, S2, S3, TROCA} from './roteiro';

const DUR_Q = fq(FIM);
const ini = (f: {inicio: number}) => f.inicio;

// tempos que mais de um efeito usa
const segundos = em(S1.tres, 'segundos');
const colagem = em(S2.vira, 'colagem');
const aqui = em(S2.resto, 'aqui');
const esse = em(S3.salva, 'esse');

export const EFEITOS: Ef[] = [
  // 1 · gancho
  ['drone', 0, 0.7], ['batimento', 0.05, 0.8],
  ...somDeLetras('3', ini(S1.tres)), ['thump', ini(S1.tres), 0.7],
  ...somDeLetras('SEGUNDOS', segundos, 2, 0.4),
  ['rabisco', em(S1.tempo, 'tempo'), 0.45], ['rabisco', segundos + 0.33, 0.35],
  ['pop', ini(S1.prender), 0.55], ['brilho', ini(S1.prender) + 0.1, 0.5],
  somDeCobertura(CENA_INICIO[1]),
  // 2 · conteúdo
  ['carimbo', ini(S2.vira), 0.7], ['digitacao', ini(S2.vira) + 0.05, 0.45],
  ['carimbo', colagem, 0.8], ['digitacao', colagem + 0.05, 0.45], ['rabisco', colagem + 0.27, 0.35],
  ['rabisco', ini(S2.escrita), 0.45], ['rabisco', ini(S2.escrita) + 0.27, 0.35], ['rabisco', ini(S2.dita), 0.45],
  somDeChicote(TROCA.resto, 0.6), ['whoosh', TROCA.resto + 0.1, 0.4], ['rabisco', aqui, 0.45],
  somDeChicote(CENA_INICIO[2]),
  // 3 · fecho
  ['pop', ini(S3.marca), 0.55], ['brilho', ini(S3.marca) + 0.27, 0.55],
  ['carimbo', ini(S3.salva), 0.8], ['thump', ini(S3.salva), 0.6], ['digitacao', ini(S3.salva) + 0.05, 0.45],
  ['carimbo', esse, 0.75], ['digitacao', esse + 0.05, 0.45], ['rabisco', em(S3.salva, 'vídeo') + 0.13, 0.4],
];

export const Sons: React.FC = () => {
  // Só dentro de <SomTolerante> (o exemplo) arquivo ausente é pulado; getStaticFiles lista
  // o public/ da peça. Fora dele, todo <Audio> é montado e o que faltar derruba o render.
  const tolerante = useSomTolerante();
  const toca = (arquivo: string) => !tolerante || getStaticFiles().some((f) => f.name === arquivo);
  const fimFala = fq(PALAVRAS[PALAVRAS.length - 1].fim + 0.22);
  // a trilha fica baixa sob a voz, sobe quando a fala acaba e some nos últimos 10 quadros
  const trilha = (q: number) => {
    const base = 0.2;
    const fim = interpolate(q, [fimFala, fimFala + 6], [base, 0.34], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    const sai = interpolate(q, [DUR_Q - 10, DUR_Q], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    return Math.max(base, fim) * sai;
  };
  return (
    <>
      {toca('fonte/narracao.mp3') && <Audio src={staticFile('fonte/narracao.mp3')} volume={1} />}
      {toca('sfx/trilha.wav') && <Audio src={staticFile('sfx/trilha.wav')} volume={trilha} />}
      {EFEITOS.map(([arq, s, vol = 0.5], i) => {
        const de = Math.max(0, fq(s));
        const dura = Math.min(DUR_Q - de, fq(DURACAO_EFEITO[arq] ?? DURACAO_PADRAO_EFEITO));
        return dura > 0 && toca(`sfx/${arq}.wav`) && (
          <Sequence key={i} from={de} durationInFrames={dura}>
            <Audio src={staticFile(`sfx/${arq}.wav`)} volume={vol * 0.8} />
          </Sequence>
        );
      })}
    </>
  );
};
