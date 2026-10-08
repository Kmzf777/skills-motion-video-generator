// As duas vozes tipográficas que a COLAGEM acrescenta à marca, iguais para toda marca:
//
//   Instrument Serif Italic (OFL)  — a serifa editorial solta, entre as caixas
//   Permanent Marker (Apache 2.0)  — a letra de canetão das etiquetas presas no mural
//
// Baixadas de github.com/google/fonts em 07/10/2026, com a licença ao lado (pasta
// `fontes/`). Cobertura de pt-BR conferida na tabela cmap antes do uso.
//
// Mesma guarda de `identidade/tipografia.ts` (ver identidade/guarda-fonte.ts): depois
// de carregar, mede a largura de uma amostra sob a família e sob uma família
// inexistente, e confere os glifos do idioma da marca. Reprovou = `cancelRender`.
//
// Importar este módulo é efeito colateral (abre um delayRender): só os componentes
// .tsx da colagem o importam, nunca um .ts testado pelo vitest.

import {loadFont} from '@remotion/fonts';
import {cancelRender, continueRender, delayRender} from 'remotion';
import {medirFamilia, reprovacao} from '../identidade/guarda-fonte';
import {IDENTIDADE} from '../identidade/tokens';
import arquivoSerifa from './fontes/InstrumentSerif-Italic.ttf';
import arquivoMarcador from './fontes/PermanentMarker-Regular.ttf';

export const PILHA_COLAGEM = {
  serifa: '"Instrument Serif", Georgia, serif',
  marcador: '"Permanent Marker", "Comic Sans MS", cursive',
};

const FAMILIAS = [
  {familia: 'Instrument Serif', estilo: 'italic', url: arquivoSerifa},
  {familia: 'Permanent Marker', estilo: 'normal', url: arquivoMarcador},
] as const;

const AMOSTRA = 'Não é só bonito: ação, açúcar, 2.048 ok';

const espera = delayRender('Colagem: carregando Instrument Serif Italic e Permanent Marker');

(async () => {
  await Promise.all(
    FAMILIAS.map((f) =>
      loadFont({family: f.familia, url: f.url, style: f.estilo, weight: '400', format: 'truetype', display: 'block'}),
    ),
  );
  await document.fonts.ready;
  const medidas = FAMILIAS.map((f) => medirFamilia(f.familia, f.estilo, 400, AMOSTRA, IDENTIDADE.idioma));
  const erro = reprovacao(medidas, 'fontes da colagem');
  if (erro) throw new Error(erro);
  for (const f of FAMILIAS) console.log(`[fonte] colagem ${f.familia} ${f.estilo} ok`);
})().then(
  () => continueRender(espera),
  (e: Error) => cancelRender(e),
);
