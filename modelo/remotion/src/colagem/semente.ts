// Aleatoriedade COM SEMENTE para a colagem.
//
// Render tem que ser determinístico: o mesmo quadro renderizado duas vezes dá o mesmo
// md5. Por isso nada aqui usa `Math.random`. Toda variação "orgânica" da colagem --
// rotação de entrada, boil de borda, tremor de carimbo -- sai daqui, semeada pelo
// NOME da peça. Mesma peça, mesmo tremor, em qualquer render.
//
// FNV-1a transforma a chave em 32 bits; mulberry32 gera a sequência.

export function semente(chave: string): () => number {
  let h = 2166136261;
  for (const c of chave) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  let a = h >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Um número só, em [min, max), para a chave dada. */
export function sorteio(chave: string, min: number, max: number): number {
  return min + semente(chave)() * (max - min);
}
