// Os tokens da marca, lidos de `motion/marca/identidade.json` (contrato C3).
//
// Nada de cor ou família digitada no motor: tudo sai do JSON da marca, validado por
// `validarIdentidade` (um campo errado derruba o bundle com a mensagem do campo, em
// vez de virar `undefined` no CSS).
//
// Os PAPÉIS das cores (contrato C3):
//   escuro   -- fundo escuro, tinta escura, fundo do Dymo
//   claro    -- fundo claro, tinta clara, papel
//   profundo -- a cor escura de apoio (fundo de cena "terra", pílula sobre fundo claro)
//   acento   -- UM acento por cena: elipse, seta, Dymo de destaque
//   apoio    -- a cor secundária (check de aprovação, Dymo alternativo)
//
// O caminho `../../../marca/identidade.json` sai de `motion/remotion/src/identidade/`
// para `motion/marca/`. Fora de um repositório plantado (na própria semente) este
// arquivo não compila, e é isso mesmo: o motor só existe com uma marca.

import identidadeJson from '../../../marca/identidade.json';
import {validarIdentidade, type Identidade, type PapelFonte} from './identidade';

export {AUDIO} from '../audio/alvo';

export const IDENTIDADE: Identidade = validarIdentidade(identidadeJson);

export const COR = IDENTIDADE.cores;

export const TIPO: Record<PapelFonte, {familia: string; peso: number}> = {
  manchete: {familia: IDENTIDADE.fontes.manchete.familia, peso: IDENTIDADE.fontes.manchete.peso},
  corpo: {familia: IDENTIDADE.fontes.corpo.familia, peso: IDENTIDADE.fontes.corpo.peso},
  dado: {familia: IDENTIDADE.fontes.dado.familia, peso: IDENTIDADE.fontes.dado.peso},
};
