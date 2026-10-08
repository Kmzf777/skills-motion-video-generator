// Os ARQUIVOS da marca que entram no bundle: logos (`motion/marca/logo-*.png|svg|webp`)
// e fontes próprias (`motion/marca/fontes/*.ttf|otf|woff|woff2`).
//
// POR QUE PELO BUNDLER E NÃO POR `staticFile()`
//
// `staticFile()` lê do `public/` da peça que está sendo renderizada. Para a marca isso
// seria errado duas vezes:
//   1. a tipografia é GLOBAL (index.ts carrega para toda composição). Se a fonte da
//      marca viesse do public/ de uma peça, renderizar outra peça -- ou o `Exemplo`,
//      que é a conferência do motor -- quebraria;
//   2. `motion/pecas/*/public/` é gitignorado (contrato C2): uma cópia do logo ali some
//      num clone e teria que ser refeita a cada peça. `motion/marca/` é versionado e é
//      o lugar único do logo e das fontes.
// Então os arquivos entram como módulo (regra `asset/resource` do bundler do Remotion
// para png/svg/webp/ttf/otf/woff/woff2) via `require.context`.
//
// SÓ DENTRO DO BUNDLE: `require.context` é do webpack e não existe no vitest. Por isso
// este módulo só é importado por tipografia.ts e por componentes .tsx, nunca por um .ts
// testado.

const contexto = require.context(
  '../../../marca',
  true,
  /^\.\/(logo-[^/]+\.(png|svg|webp)|fontes\/[^/]+\.(ttf|otf|woff|woff2))$/,
);

/** Os arquivos da marca que o bundler achou, como `logo-escura.png` e `fontes/X.ttf`. */
export const arquivosDaMarca = (): string[] => contexto.keys().map((k) => k.replace(/^\.\//, ''));

/**
 * URL (dentro do bundle) de um arquivo de `motion/marca/`, pelo caminho relativo a ela
 * (`logo-escura.png`, `fontes/Marca-Bold.ttf`). Lança, com a lista do que existe, se o
 * arquivo pedido pelo identidade.json não estiver lá.
 */
export function urlDaMarca(relativo: string): string {
  const chave = `./${relativo}`;
  if (!contexto.keys().includes(chave)) {
    const existe = arquivosDaMarca();
    throw new Error(
      `identidade.json pede motion/marca/${relativo}, que não existe (ou não segue o padrão ` +
        `logo-*.png|svg|webp / fontes/*.ttf|otf|woff|woff2). Arquivos da marca encontrados: ` +
        `${existe.length ? existe.join(', ') : 'nenhum'}.`,
    );
  }
  const m = contexto(chave);
  const url = typeof m === 'string' ? m : (m as {default?: unknown} | null)?.default;
  if (typeof url !== 'string') throw new Error(`o bundler não devolveu URL para motion/marca/${relativo}`);
  return url;
}
