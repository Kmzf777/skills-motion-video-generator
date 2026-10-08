// Cores de MATERIAL da colagem: papel e sombra, não marca.
//
// A colagem é feita de papel de verdade (papel offset, kraft, fita), e papel tem a cor
// dele em qualquer marca. As cores da marca (identidade.json) vão na TINTA, nos fundos
// de cena e nos acentos; estas aqui só no suporte.

export const PAPEL = {
  /** papel offset levemente amarelado: etiqueta de marcador, régua, letra recortada */
  branco: '#F7F2E6',
  /** papel kraft */
  kraft: '#D9C3A0',
  /** trilho vazio de uma barra (Tira) */
  trilho: '#D9D0BD',
} as const;

/** Sombra de papel colado: quente e curta, nunca a mesma em duas camadas. */
export const SOMBRA = {
  caixa: '0 8px 14px rgba(12,8,5,0.38)',
  tira: '0 6px 10px rgba(10,6,4,0.3)',
  filtro: 'drop-shadow(0px 8px 12px rgba(12,8,5,0.38))',
  recorte: 'drop-shadow(0px 10px 12px rgba(12,8,5,0.36))',
} as const;
