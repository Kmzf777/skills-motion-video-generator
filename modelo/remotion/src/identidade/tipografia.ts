// A tipografia da marca, carregada de arquivo local e PROVADA antes do primeiro quadro.
//
// NOME: `tipografia.ts`, e não `fontes.ts`, porque neste motor "fonte" também quer dizer
// a mídia de origem (`public/fonte/narracao.mp3`). As pastas `fontes/` guardam os
// arquivos de fonte tipográfica.
//
// DE ONDE VEM CADA FAMÍLIA (identidade.json, contrato C3)
//
//   "arquivo": null      -> a fonte padrão empacotada em `src/identidade/fontes/` (OFL):
//                           Archivo Black 400 (manchete), Inter 700 (corpo), IBM Plex
//                           Mono 500 (dado). A validação exige família e peso iguais.
//   "arquivo": "X.ttf"   -> `motion/marca/fontes/X.ttf`, entra no bundle por
//                           `arquivos-marca.ts`. Fonte comercial sem licença de uso não
//                           entra: a fase 01 troca pela padrão.
//
// ARQUIVO LOCAL, NÃO `@remotion/google-fonts`: buscar fonte por rede durante o render
// torna o render não determinístico e, numa máquina offline, volta a cair no fallback
// em silêncio -- o bug que este arquivo existe para matar.
//
// A GUARDA (ver guarda-fonte.ts): depois de carregar, cada família é medida contra o
// fallback do navegador e contra os caracteres do idioma da marca. Reprovou =
// `cancelRender`: o render morre em vez de entregar Times New Roman achando que
// entregou a fonte da marca.
//
// Importar este módulo é EFEITO COLATERAL (abre um `delayRender`): só o index.ts e
// componentes .tsx o importam, nunca um .ts testado pelo vitest.

import {loadFont} from '@remotion/fonts';
import {cancelRender, continueRender, delayRender} from 'remotion';
import {urlDaMarca} from './arquivos-marca';
import {medirFamilia, reprovacao, type Medida} from './guarda-fonte';
import {FONTES_PADRAO, PAPEIS_FONTE, type PapelFonte} from './identidade';
import {IDENTIDADE, TIPO} from './tokens';

import arquivoManchete from './fontes/ArchivoBlack-Regular.ttf';
import arquivoCorpo from './fontes/Inter-Bold.ttf';
import arquivoDado from './fontes/IBMPlexMono-Medium.ttf';

export type Papel = PapelFonte;

const EMPACOTADA: Record<PapelFonte, string> = {manchete: arquivoManchete, corpo: arquivoCorpo, dado: arquivoDado};

const FORMATO = {ttf: 'truetype', otf: 'opentype', woff: 'woff', woff2: 'woff2'} as const;

function formatoDe(arquivo: string): (typeof FORMATO)[keyof typeof FORMATO] {
  const ext = arquivo.split('.').pop()?.toLowerCase() as keyof typeof FORMATO;
  const f = FORMATO[ext];
  if (!f) throw new Error(`extensão de fonte não suportada: ${arquivo}`);
  return f;
}

/** As três famílias: o NOME vem do identidade.json e os BYTES do arquivo. */
export const FAMILIAS = PAPEIS_FONTE.map((papel) => {
  const f = IDENTIDADE.fontes[papel];
  const daMarca = f.arquivo !== null;
  const arquivo = f.arquivo ?? FONTES_PADRAO[papel].arquivo;
  return {
    papel,
    familia: f.familia,
    peso: f.peso,
    arquivo,
    daMarca,
    origem: daMarca ? `motion/marca/fontes/${arquivo}` : `src/identidade/fontes/${arquivo}`,
  };
});

/** URL do arquivo no bundle. Resolvida DENTRO do carregamento: se faltar, vira cancelRender. */
const urlDe = (f: (typeof FAMILIAS)[number]) => (f.daMarca ? urlDaMarca(`fontes/${f.arquivo}`) : EMPACOTADA[f.papel]);

/**
 * A pilha para usar em `fontFamily`.
 *
 * O fallback existe para o caso de a guarda não rodar (Studio em desenvolvimento, por
 * exemplo): entre errar para uma grotesca e errar para Times New Roman, a grotesca ao
 * menos não desmonta o enquadramento. Ele NÃO substitui a guarda.
 */
export const PILHA: Record<PapelFonte, string> = {
  manchete: `"${TIPO.manchete.familia}", "Arial Black", Impact, sans-serif`,
  corpo: `"${TIPO.corpo.familia}", "Helvetica Neue", Arial, sans-serif`,
  dado: `"${TIPO.dado.familia}", "Courier New", monospace`,
};

/** Amostra medida: o nome da marca, acentos e dígitos. */
const AMOSTRA = `${IDENTIDADE.marca} ação, açúcar e pão: 12,5`;

const espera = delayRender(`Tipografia da marca: carregando ${FAMILIAS.map((f) => f.familia).join(', ')}`);

/**
 * Resolve com as medidas das três famílias, ou rejeita se alguma não aplicou ou não tem
 * os glifos do idioma. O motor não precisa esperar por ela à mão: o `delayRender` acima
 * já segura o primeiro quadro.
 */
export const tipografiaPronta: Promise<Medida[]> = (async () => {
  await Promise.all(
    FAMILIAS.map((f) =>
      loadFont({
        family: f.familia,
        url: urlDe(f),
        weight: String(f.peso),
        format: formatoDe(f.arquivo),
        // `block`, não `swap`: num render não existe "mostrar o fallback enquanto
        // carrega" que não seja um quadro errado gravado no arquivo.
        display: 'block',
      }),
    ),
  );
  await document.fonts.ready;
  const medidas = FAMILIAS.map((f) => medirFamilia(f.familia, 'normal', f.peso, AMOSTRA, IDENTIDADE.idioma));
  const erro = reprovacao(medidas, 'tipografia da marca');
  if (erro) throw new Error(erro);
  return medidas;
})();

tipografiaPronta.then(
  (medidas) => {
    for (const [i, m] of medidas.entries()) {
      // Aparece no log do render: a prova de que carregou, no lugar onde antes não
      // aparecia nada.
      console.log(
        `[fonte] ${FAMILIAS[i].papel.padEnd(8)} ${m.familia} ${m.peso} (${FAMILIAS[i].origem}) - amostra ` +
          `${m.alvo.toFixed(1)}px (fallback seria ${m.fallback.toFixed(1)}px)`,
      );
    }
    continueRender(espera);
  },
  (e: Error) => cancelRender(e),
);
