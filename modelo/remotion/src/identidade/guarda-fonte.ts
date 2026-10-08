// A GUARDA de fonte: prova, no navegador, que uma família foi aplicada e que ela tem os
// caracteres do idioma da marca.
//
// O modo de falha que isto mata é silencioso: o Chrome headless não tem a fonte da
// marca instalada, cai no default dele (Times New Roman) sem erro e o render sai com
// exit 0. Medido na origem deste motor (30/09/2026): uma legenda "em Inter" saiu com
// serifa de Times em todos os MP4 até ali.
//
// Duas medidas, ambas por largura de texto no canvas:
//   1. APLICADA -- a amostra sob a família contra a mesma amostra sob uma família que
//      não existe (que é, por definição, o fallback). Larguras iguais = não aplicou.
//   2. COBERTURA -- para cada caractere do idioma, a largura sob `"Família", serif` e
//      sob `"Família", monospace` contra `serif` e `monospace` puros. Se a família não
//      tem o glifo, o navegador desenha o fallback e AS DUAS larguras batem com as do
//      fallback; se tem, ao menos uma difere (serif e monospace não têm a mesma largura
//      para a mesma letra). Uma fonte sem "ç" ou "ã" sairia com a letra trocada no
//      meio da palavra, sem aviso.
//
// Sem import de Remotion: quem decide o que fazer com o resultado (cancelRender) é quem
// chama.

const INEXISTENTE = 'FamiliaQueNaoExisteEmLugarNenhum';

/** Caracteres além do ASCII que o idioma da marca exige da fonte. */
export function caracteresDoIdioma(idioma: string): string {
  const base = idioma.toLowerCase().split(/[-_]/)[0];
  if (base === 'pt') return 'ÁÂÃÀÇÉÊÍÓÔÕÚáâãàçéêíóôõú';
  if (base === 'es') return 'ÁÉÍÓÚÑÜáéíóúñü¿¡';
  if (base === 'en') return '';
  return 'ÁÂÃÀÇÉÊÍÓÔÕÚÑÜáâãàçéêíóôõúñü';
}

function ctx2d(): CanvasRenderingContext2D {
  const ctx = document.createElement('canvas').getContext('2d');
  if (!ctx) throw new Error('sem contexto 2d de canvas: não dá para provar que a fonte foi aplicada');
  return ctx;
}

function medir(ctx: CanvasRenderingContext2D, fonte: string, texto: string): number {
  // O shorthand do canvas segue o do CSS: família com espaço precisa de aspas.
  ctx.font = fonte;
  return ctx.measureText(texto).width;
}

export type Medida = {familia: string; estilo: string; peso: number; alvo: number; fallback: number; aplicou: boolean; semGlifo: string[]};

/** Mede a família (já carregada) contra o fallback e lista os glifos que faltam. */
export function medirFamilia(familia: string, estilo: string, peso: number, amostra: string, idioma: string): Medida {
  const ctx = ctx2d();
  const pre = `${estilo} ${peso} 80px`;
  const alvo = medir(ctx, `${pre} "${familia}"`, amostra);
  const fallback = medir(ctx, `${pre} "${INEXISTENTE}"`, amostra);
  const semGlifo = [...caracteresDoIdioma(idioma)].filter((c) =>
    medir(ctx, `${pre} "${familia}", serif`, c) === medir(ctx, `${pre} serif`, c) &&
    medir(ctx, `${pre} "${familia}", monospace`, c) === medir(ctx, `${pre} monospace`, c),
  );
  return {familia, estilo, peso, alvo, fallback, aplicou: alvo !== fallback, semGlifo};
}

/** Mensagem de erro para as medidas reprovadas, ou null se todas passaram. */
export function reprovacao(medidas: Medida[], onde: string): string | null {
  const ruins = medidas.filter((m) => !m.aplicou || m.semGlifo.length > 0);
  if (!ruins.length) return null;
  return (
    `fonte NÃO aplicada corretamente (${onde}): ` +
    ruins
      .map((m) => (!m.aplicou
        ? `${m.familia} ${m.peso} mediu a mesma largura que o fallback do navegador (o Chrome está desenhando a fonte dele)`
        : `${m.familia} ${m.peso} não tem os glifos ${m.semGlifo.join(' ')}`))
      .join('; ') +
    '. Confira o arquivo da fonte e o nome da família em motion/marca/identidade.json.'
  );
}
