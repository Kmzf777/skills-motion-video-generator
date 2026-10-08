// Declarações para o TypeScript do que o bundler do Remotion resolve sozinho.
//
// 1. Import de arquivo de fonte. O bundler tem regra `asset/resource` para
//    woff/woff2/otf/ttf/eot (e para png/svg/jpg/webp/...): `import url from './x.ttf'`
//    devolve a URL do arquivo já emitido dentro do bundle -- sem rede, e sem depender de
//    `--public-dir`, que cada peça aponta para a própria pasta.
//
// 2. `require.context`, do webpack: é como `identidade/arquivos-marca.ts` põe no bundle
//    os logos e fontes de `motion/marca/`. Não existe fora do bundle (vitest, Node).

declare module '*.ttf' {
  const url: string;
  export default url;
}
declare module '*.otf' {
  const url: string;
  export default url;
}
declare module '*.woff' {
  const url: string;
  export default url;
}
declare module '*.woff2' {
  const url: string;
  export default url;
}

declare namespace NodeJS {
  interface Require {
    context(
      diretorio: string,
      recursivo: boolean,
      filtro: RegExp,
    ): {
      keys(): string[];
      (chave: string): unknown;
    };
  }
}
