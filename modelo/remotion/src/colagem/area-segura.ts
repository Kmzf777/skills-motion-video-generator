// ÁREA SEGURA do quadro 1080x1920, em px, por formato de veiculação.
//
//   organico -- Reel no feed: a interface do app cobre os 5% do topo (y < 96) e os 16% da
//               base (y > 1613); texto em x 140–940 com a câmera em repouso (ela anda até
//               ~120 px e amplia até ~1,16×).
//   anuncio  -- Reel patrocinado: o rodapé do anúncio (CTA, nome, texto) sobe mais; texto em
//               y 269–1248 e x 65–1015.
//
// Módulo puro: a Pílula (legenda A) e os testes leem daqui.

export type Formato = 'organico' | 'anuncio';
export type Area = {x0: number; x1: number; y0: number; y1: number};

export const AREA_SEGURA: Record<Formato, Area> = {
  organico: {x0: 140, x1: 940, y0: 96, y1: 1613},
  anuncio: {x0: 65, x1: 1015, y0: 269, y1: 1248},
};

/** Altura da pílula (corpo 46 px + 16 + 14 de respiro), em px. */
export const ALTURA_PILULA = 76;

/** Centro padrão da pílula em cada formato: 1500 no orgânico; colada no limite de baixo no anúncio. */
const Y_PADRAO: Record<Formato, number> = {
  organico: 1500,
  anuncio: AREA_SEGURA.anuncio.y1 - ALTURA_PILULA / 2,
};

/**
 * y do CENTRO da pílula: o pedido (ou o padrão do formato), trazido para dentro da área
 * segura do formato -- a pílula inteira fica entre y0 e y1.
 */
export function yDaPilula(formato: Formato = 'organico', y?: number): number {
  const a = AREA_SEGURA[formato];
  const meio = ALTURA_PILULA / 2;
  return Math.min(a.y1 - meio, Math.max(a.y0 + meio, y ?? Y_PADRAO[formato]));
}
