// A gramática de movimento da colagem, em funções puras de quadro.
//
// Fica num .ts e não num .tsx por uma razão mecânica: arquivo que importa
// `identidade/tipografia.ts` (ou qualquer módulo que abre `delayRender`) derruba o
// vitest. Tudo que é testado mora em .ts sem efeito colateral.
//
// Os gestos:
//   assentar -- a peça chega um pouco grande e girada, e pousa sem quicar
//   boil     -- depois de colada, ela "respira" em passo de stop-motion
//   carimbar -- o veredito bate grande e assenta em 3 quadros
//   carimbo  -- o "stamp" das referências: ultrapassa até 12% e volta
//   esmagar  -- squash & stretch de entrada (serifa solta)
//
// Nada de elástico: o único overshoot permitido é o do carimbo (até 12%), e assentar
// nem chega a usá-lo -- o pouso é amortecido.

import {sorteio, semente} from './semente';

export const ASSENTAR_QUADROS = 6;
export const BOIL_PASSO = 3;
export const CARIMBO_QUADROS = 3;

/** ease-out cúbico: rápido no começo, pousa devagar. */
export const saida = (t: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3);

export type Pose = {visivel: boolean; escala: number; rot: number; dy: number; opacidade: number};

const INVISIVEL: Pose = {visivel: false, escala: 1, rot: 0, dy: 0, opacidade: 0};

/**
 * Pose de uma peça que começa a ser colada no quadro `inicio`.
 * A rotação de chegada (2..4 graus, sinal da semente) cai para a rotação de
 * repouso (|r| <= 0,6) em ASSENTAR_QUADROS.
 */
export function assentar(q: number, inicio: number, chave: string): Pose {
  if (q < inicio) return INVISIVEL;
  const s = semente(chave);
  const sinal = s() < 0.5 ? -1 : 1;
  const rotChegada = sinal * (2 + s() * 2);
  const rotRepouso = (s() - 0.5) * 1.2;
  const t = saida((q - inicio) / ASSENTAR_QUADROS);
  return {
    visivel: true,
    escala: 1.04 + (1 - 1.04) * t,
    rot: rotChegada + (rotRepouso - rotChegada) * t,
    dy: -24 * (1 - t),
    opacidade: Math.min(1, (q - inicio + 1) / 2),
  };
}

/**
 * Respiração de stop-motion: troca de estado só a cada BOIL_PASSO quadros
 * (10 "desenhos" por segundo a 30 fps). `variante` escolhe uma das três bordas
 * irregulares pré-renderizadas (`<nome>-b0/b1/b2.png`); `rot` é um tremor de no
 * máximo 0,6 grau.
 */
export function boil(q: number, chave: string): {variante: 0 | 1 | 2; rot: number} {
  const passo = Math.floor(q / BOIL_PASSO);
  const v = Math.floor(sorteio(`${chave}#v${passo}`, 0, 3)) as 0 | 1 | 2;
  return {variante: v, rot: sorteio(`${chave}#r${passo}`, -0.6, 0.6)};
}

/** Carimbo: 1,15 no impacto, 1,00 em CARIMBO_QUADROS. */
export function carimbar(q: number, inicio: number): {visivel: boolean; escala: number} {
  if (q < inicio) return {visivel: false, escala: 1};
  const t = saida((q - inicio) / CARIMBO_QUADROS);
  return {visivel: true, escala: 1.15 + (1 - 1.15) * t};
}

/**
 * Passo de stop-motion: a pose dos recortes só muda a cada `passo` quadros
 * (3 → 10 "desenhos" por segundo a 30 fps), enquanto a câmera anda lisa a 30 fps.
 * É o contraste das referências: gráfico em 8–12 fps sobre câmera contínua.
 */
export function posterizar(q: number, passo = 3, desde = 0): number {
  if (q < desde) return q;
  return desde + Math.floor((q - desde) / passo) * passo;
}

/**
 * Carimbo com ultrapassagem configurável. A colagem tem licença para até 12%
 * (1,12 → 0,97 → 1,00): é o "stamp" das referências. Fora dele, sem elástico.
 */
export function carimbo(q: number, inicio: number, pico = 1.12, quadros = 4): {visivel: boolean; escala: number} {
  if (q < inicio) return {visivel: false, escala: 1};
  const k = q - inicio;
  if (k >= quadros) return {visivel: true, escala: 1};
  const fases = [pico, 1 - (pico - 1) * 0.25, 1 + (pico - 1) * 0.08, 1];
  return {visivel: true, escala: fases[Math.min(fases.length - 1, Math.floor((k / quadros) * fases.length))]};
}

/** Squash & stretch de entrada: chega achatado e largo, assenta em 4 quadros. */
export function esmagar(q: number, inicio: number): {sx: number; sy: number; visivel: boolean} {
  if (q < inicio) return {sx: 1, sy: 1, visivel: false};
  const t = saida((q - inicio) / 4);
  return {visivel: true, sx: 1.35 + (1 - 1.35) * t, sy: 0.55 + (1 - 0.55) * t};
}

/** Progresso 0..1 entre dois quadros, com ease-out. */
export function progresso(q: number, de: number, ate: number): number {
  if (ate <= de) return q >= ate ? 1 : 0;
  return saida((q - de) / (ate - de));
}
