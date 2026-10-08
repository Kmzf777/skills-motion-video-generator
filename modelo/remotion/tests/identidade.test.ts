// A identidade da marca (motion/marca/identidade.json) é válida e legível.
//
// Roda em todo `npx vitest run`: a fase 01 escreve o JSON, e um campo errado aparece
// aqui com o nome do campo, antes de virar fundo transparente num render.

import {describe, expect, it} from 'vitest';
import identidadeJson from '../../marca/identidade.json';
import {contraste, misturar, rgba, tintaPara} from '../src/identidade/cor';
import {FONTES_PADRAO, validarIdentidade} from '../src/identidade/identidade';

const VALIDA = validarIdentidade(identidadeJson);
const copia = () => JSON.parse(JSON.stringify(identidadeJson)) as Record<string, any>;

describe('identidade.json do repositório', () => {
  it('passa na validação do contrato C3', () => {
    expect(VALIDA.cores.escuro).toMatch(/^#[0-9A-Fa-f]{6}$/);
  });

  it('é legível: claro sobre escuro (Dymo, fundo escuro) e sobre profundo (a pílula)', () => {
    const {escuro, claro, profundo, acento} = VALIDA.cores;
    // 4,5:1 = texto normal (WCAG AA). A pílula é corpo 46 px em movimento: AA no mínimo.
    expect(contraste(claro, escuro), 'claro × escuro: Dymo padrão e fundo escuro').toBeGreaterThanOrEqual(4.5);
    expect(contraste(claro, profundo), 'claro × profundo: a pílula').toBeGreaterThanOrEqual(4.5);
    // O acento recebe a tinta que tiver contraste (tintaPara): basta uma das duas servir.
    expect(Math.max(contraste(acento, claro), contraste(acento, escuro)), 'acento sem tinta legível').toBeGreaterThanOrEqual(3);
  });
});

describe('validarIdentidade', () => {
  it('acusa cor fora de #RRGGBB e papel de cor faltando, todos de uma vez', () => {
    const j = copia();
    j.cores.escuro = 'preto';
    delete j.cores.apoio;
    expect(() => validarIdentidade(j)).toThrow(/cores\.escuro[\s\S]*cores\.apoio/);
  });

  it('recusa "arquivo": null com família diferente da padrão empacotada', () => {
    const j = copia();
    j.fontes.manchete = {familia: 'Montserrat', arquivo: null, peso: 800};
    expect(() => validarIdentidade(j)).toThrow(/fontes\.manchete/);
  });

  it('aceita fonte própria por nome de arquivo e recusa caminho', () => {
    const j = copia();
    j.fontes.corpo = {familia: 'Marca Sans', arquivo: 'MarcaSans-Bold.ttf', peso: 700};
    expect(() => validarIdentidade(j)).not.toThrow();
    j.fontes.corpo.arquivo = 'fontes/MarcaSans-Bold.ttf';
    expect(() => validarIdentidade(j)).toThrow(/fontes\.corpo\.arquivo/);
  });

  it('logo: null ou logo-*.png|svg|webp na raiz de motion/marca/', () => {
    const j = copia();
    j.logo = {sobre_claro: 'logo-escura.png', sobre_escuro: null};
    expect(() => validarIdentidade(j)).not.toThrow();
    j.logo.sobre_escuro = 'marca.png';
    expect(() => validarIdentidade(j)).toThrow(/logo\.sobre_escuro/);
  });

  it('slug só [a-z0-9-] e exemplo booleano', () => {
    const j = copia();
    j.slug = 'Marca Exemplo';
    j.exemplo = 'sim';
    expect(() => validarIdentidade(j)).toThrow(/slug[\s\S]*exemplo/);
  });

  it('as fontes padrão têm família e peso fixos', () => {
    expect(FONTES_PADRAO.manchete).toMatchObject({familia: 'Archivo Black', peso: 400});
    expect(FONTES_PADRAO.corpo).toMatchObject({familia: 'Inter', peso: 700});
    expect(FONTES_PADRAO.dado).toMatchObject({familia: 'IBM Plex Mono', peso: 500});
  });
});

describe('cor', () => {
  it('rgba e mistura', () => {
    expect(rgba('#2A3038', 0.86)).toBe('rgba(42,48,56,0.86)');
    expect(misturar('#000000', '#FFFFFF', 0.5)).toBe('#808080');
    expect(contraste('#000000', '#FFFFFF')).toBeCloseTo(21, 0);
    expect(() => rgba('preto', 1)).toThrow();
  });

  it('tintaPara troca a letra clara pela escura num fundo claro demais', () => {
    expect(tintaPara('#121417', '#F3F3F0', '#121417')).toBe('#F3F3F0');
    expect(tintaPara('#F5D90A', '#FFFFFF', '#121417')).toBe('#121417');
  });
});
