// Aritmética de cor, pura. As cores da marca chegam em #RRGGBB (identidade.json) e os
// componentes precisam delas com transparência ou misturadas -- sem digitar rgba() de
// uma marca específica no código do motor.

function canais(hex: string): [number, number, number] {
  const m = /^#([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})$/.exec(hex);
  if (!m) throw new Error(`cor inválida: ${hex} (esperava #RRGGBB)`);
  return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)];
}

/** `#RRGGBB` com opacidade `alfa` (0..1), como `rgba(r,g,b,a)`. */
export function rgba(hex: string, alfa: number): string {
  const [r, g, b] = canais(hex);
  return `rgba(${r},${g},${b},${alfa})`;
}

/** Mistura `a` com `b` em `t` (0 = só a, 1 = só b). Devolve #rrggbb. */
export function misturar(a: string, b: string, t: number): string {
  const ca = canais(a);
  const cb = canais(b);
  return `#${ca.map((v, i) => Math.round(v + (cb[i] - v) * t).toString(16).padStart(2, '0')).join('')}`;
}

/** Luminância relativa WCAG de #RRGGBB (0 = preto, 1 = branco). */
export function luminancia(hex: string): number {
  const lin = canais(hex).map((v) => {
    const c = v / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
}

/** Razão de contraste WCAG entre duas cores (1 a 21). */
export function contraste(a: string, b: string): number {
  const [l1, l2] = [luminancia(a), luminancia(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}

/**
 * A tinta para escrever sobre `fundo`: a `preferida` se ela tiver ao menos `minimo` de
 * contraste (3:1 = texto grande, WCAG), senão a `alternativa`. Assim um acento claro
 * (amarelo, por exemplo) não recebe letra clara ilegível em cima.
 */
export function tintaPara(fundo: string, preferida: string, alternativa: string, minimo = 3): string {
  return contraste(fundo, preferida) >= minimo ? preferida : alternativa;
}
