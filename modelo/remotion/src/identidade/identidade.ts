// A IDENTIDADE da marca: o formato de `motion/marca/identidade.json` (contrato C3) e a
// validação dele.
//
// Módulo PURO -- sem React, sem Remotion, sem efeito colateral -- para rodar tanto no
// bundle (via tokens.ts) quanto no vitest (tests/identidade.test.ts).
//
// POR QUE VALIDAR
//
// O JSON é escrito na fase 01, à mão ou por um agente. Uma cor com o nome errado
// ("fundo" em vez de "escuro") viraria `undefined`, e `background: undefined` no CSS é
// fundo transparente: sem erro, sem aviso, render com exit 0. Uma família de fonte que
// não bate com o arquivo empacotado registraria Archivo Black com o nome de outra
// fonte, e a guarda de tipografia aprovaria. Aqui o erro aparece no primeiro bundle (e
// no `npx vitest run`), com o campo e o valor.

export type PapelCor = 'escuro' | 'claro' | 'profundo' | 'acento' | 'apoio';
export type PapelFonte = 'manchete' | 'corpo' | 'dado';

export const PAPEIS_COR: readonly PapelCor[] = ['escuro', 'claro', 'profundo', 'acento', 'apoio'];
export const PAPEIS_FONTE: readonly PapelFonte[] = ['manchete', 'corpo', 'dado'];

export type Fonte = {familia: string; arquivo: string | null; peso: number};

export type Identidade = {
  marca: string;
  slug: string;
  idioma: string;
  cores: Record<PapelCor, string>;
  fontes: Record<PapelFonte, Fonte>;
  logo: {sobre_claro: string | null; sobre_escuro: string | null};
  voz: {plataforma: string; nome: string | null; modelo: string};
  /** true = identidade de EXEMPLO (cores de demonstração, sem logo); a fase 01 substitui. */
  exemplo: boolean;
};

/**
 * As fontes empacotadas no motor (`src/identidade/fontes/`, OFL): é o que
 * `"arquivo": null` quer dizer. Com `arquivo: null`, família e peso TÊM que ser estes,
 * porque o arquivo é um peso só de uma família só.
 */
export const FONTES_PADRAO: Record<PapelFonte, {familia: string; peso: number; arquivo: string}> = {
  manchete: {familia: 'Archivo Black', peso: 400, arquivo: 'ArchivoBlack-Regular.ttf'},
  corpo: {familia: 'Inter', peso: 700, arquivo: 'Inter-Bold.ttf'},
  dado: {familia: 'IBM Plex Mono', peso: 500, arquivo: 'IBMPlexMono-Medium.ttf'},
};

const HEX = /^#[0-9A-Fa-f]{6}$/;
const SLUG = /^[a-z0-9-]+$/;
/** Nome de arquivo de fonte dentro de `motion/marca/fontes/` (sem pasta). */
const ARQUIVO_FONTE = /^[^/\\]+\.(ttf|otf|woff|woff2)$/;
/** Logo na raiz de `motion/marca/`, com o prefixo do contrato C2 (`logo-*`). */
const ARQUIVO_LOGO = /^logo-[^/\\]+\.(png|svg|webp)$/;

const ehObjeto = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v);
const texto = (v: unknown) => typeof v === 'string' && v.trim().length > 0;
const mostrar = (v: unknown) => JSON.stringify(v) ?? String(v);

/**
 * Valida o conteúdo de identidade.json e devolve o objeto tipado. Lança com TODOS os
 * problemas de uma vez (um por linha), não só o primeiro. Campos a mais são ignorados.
 */
export function validarIdentidade(bruto: unknown, origem = 'motion/marca/identidade.json'): Identidade {
  const erros: string[] = [];
  if (!ehObjeto(bruto)) throw new Error(`${origem}: esperava um objeto JSON, veio ${mostrar(bruto)}`);
  const j = bruto;

  if (!texto(j.marca)) erros.push(`"marca" tem que ser texto não vazio, veio ${mostrar(j.marca)}`);
  if (typeof j.slug !== 'string' || !SLUG.test(j.slug)) {
    erros.push(`"slug" tem que ser minúsculas, dígitos e hífen ([a-z0-9-]), veio ${mostrar(j.slug)}`);
  }
  if (!texto(j.idioma)) erros.push(`"idioma" tem que ser texto (ex.: "pt-BR"), veio ${mostrar(j.idioma)}`);

  if (!ehObjeto(j.cores)) {
    erros.push(`"cores" tem que ser objeto com ${PAPEIS_COR.join(', ')}`);
  } else {
    const cores = j.cores;
    for (const papel of PAPEIS_COR) {
      const v = cores[papel];
      if (typeof v !== 'string' || !HEX.test(v)) erros.push(`"cores.${papel}" tem que ser #RRGGBB, veio ${mostrar(v)}`);
    }
  }

  if (!ehObjeto(j.fontes)) {
    erros.push(`"fontes" tem que ser objeto com ${PAPEIS_FONTE.join(', ')}`);
  } else {
    const fontes = j.fontes;
    for (const papel of PAPEIS_FONTE) {
      const f = fontes[papel];
      const onde = `fontes.${papel}`;
      if (!ehObjeto(f)) {
        erros.push(`"${onde}" tem que ser {familia, arquivo, peso}, veio ${mostrar(f)}`);
        continue;
      }
      if (!texto(f.familia)) erros.push(`"${onde}.familia" tem que ser texto, veio ${mostrar(f.familia)}`);
      if (typeof f.peso !== 'number' || !Number.isInteger(f.peso) || f.peso < 1 || f.peso > 1000) {
        erros.push(`"${onde}.peso" tem que ser inteiro de 1 a 1000, veio ${mostrar(f.peso)}`);
      }
      if (f.arquivo === null) {
        const p = FONTES_PADRAO[papel];
        if (f.familia !== p.familia || f.peso !== p.peso) {
          erros.push(`"${onde}" usa "arquivo": null (a fonte padrão empacotada, ${p.familia} ${p.peso}), ` +
            `mas declara ${mostrar(f.familia)} ${mostrar(f.peso)}. Ou use ${p.familia} ${p.peso}, ou ponha o ` +
            `arquivo da fonte em motion/marca/fontes/ e o nome dele em "arquivo".`);
        }
      } else if (typeof f.arquivo !== 'string' || !ARQUIVO_FONTE.test(f.arquivo)) {
        erros.push(`"${onde}.arquivo" tem que ser null ou o nome de um .ttf/.otf/.woff/.woff2 dentro de ` +
          `motion/marca/fontes/ (sem pasta), veio ${mostrar(f.arquivo)}`);
      }
    }
  }

  if (!ehObjeto(j.logo)) {
    erros.push(`"logo" tem que ser {sobre_claro, sobre_escuro}`);
  } else {
    const logo = j.logo;
    for (const lado of ['sobre_claro', 'sobre_escuro'] as const) {
      const v = logo[lado];
      if (v !== null && (typeof v !== 'string' || !ARQUIVO_LOGO.test(v))) {
        erros.push(`"logo.${lado}" tem que ser null ou "logo-<nome>.png|svg|webp" na raiz de motion/marca/, veio ${mostrar(v)}`);
      }
    }
  }

  if (!ehObjeto(j.voz)) {
    erros.push(`"voz" tem que ser {plataforma, nome, modelo}`);
  } else if (!texto(j.voz.plataforma) || !(j.voz.nome === null || texto(j.voz.nome)) || !texto(j.voz.modelo)) {
    erros.push(`"voz" tem que ter plataforma (texto), nome (texto ou null) e modelo (texto), veio ${mostrar(j.voz)}`);
  }

  if (typeof j.exemplo !== 'boolean') erros.push(`"exemplo" tem que ser true ou false, veio ${mostrar(j.exemplo)}`);

  if (erros.length) throw new Error(`${origem} inválido:\n  - ${erros.join('\n  - ')}`);
  return j as unknown as Identidade;
}
