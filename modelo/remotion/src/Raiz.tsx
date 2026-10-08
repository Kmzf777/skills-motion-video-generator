// Registro das composições.
//
// Cada peça de colagem é uma composição própria, 1080x1920 a 30 fps, com a duração
// DERIVADA do roteiro dela (`DURACAO = fq(FIM)`, FIM = última palavra + 0,5 s). Nada de
// duração digitada aqui.
//
// PEÇA NOVA (fase 07): copie `src/pecas/_modelo/` para `src/pecas/<NN-tema>/` (e os testes
// `modelo-roteiro` e `modelo-tempos` para `<NN-tema>-*`), troque o import do palavras.json
// no roteiro.ts e acrescente, imitando o Exemplo:
//
//   import * as P01 from './pecas/01-tema/Peca';
//   <Composition id="P01-tema" component={P01.Peca} durationInFrames={P01.DURACAO}
//     fps={P01.FPS} width={1080} height={1920} />
//
// O id aceita letras, números e hífen. Render, still e contato recebem o public/ da peça:
//   npx remotion still src/index.ts Exemplo ../pecas/00-exemplo/saida/exemplo.png --frame=60 --public-dir=../pecas/00-exemplo/public

import {Composition} from 'remotion';
import React from 'react';
import {SomTolerante} from './colagem/som-tolerante';
import {Marca} from './Marca';
import * as Exemplo from './pecas/_modelo/Peca';

/**
 * O exemplo não tem narração gravada: SÓ ELE toca apenas o áudio que existir em public/.
 * Peça nova entra com `component={P01.Peca}` direto, e exige todos os arquivos.
 */
const ExemploSemNarracao: React.FC = () => (
  <SomTolerante>
    <Exemplo.Peca />
  </SomTolerante>
);

export const Raiz: React.FC = () => (
  <>
    {/* A peça modelo (src/pecas/_modelo/) com os dados de motion/pecas/00-exemplo/: é a
        conferência do motor depois do plantio e o esqueleto de toda peça nova. */}
    <Composition id="Exemplo" component={ExemploSemNarracao} durationInFrames={Exemplo.DURACAO}
      fps={Exemplo.FPS} width={1080} height={1920} />

    {/* Conferência da identidade (motion/marca/identidade.json): cores, fontes, logos e
        pílula numa tela. Um quadro só. */}
    <Composition id="Marca" component={Marca} durationInFrames={1} fps={30} width={1080} height={1920} />
  </>
);
