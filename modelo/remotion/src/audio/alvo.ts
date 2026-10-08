// O alvo de loudness da entrega: -14 LUFS integrado, teto de -1 dBTP (pico real).
//
// É o padrão de entrega para Reels/Shorts/TikTok: abaixo disso a peça toca quase muda
// ao lado das outras no feed; acima, a plataforma abaixa sozinha.
//
// Mora num arquivo SEM import nenhum de propósito: `scripts/normalizar-audio.mjs` roda
// no Node com `--experimental-strip-types`, que não resolve import local sem extensão
// nem importa JSON sem atributo -- e `identidade/tokens.ts` (que reexporta este AUDIO)
// importa o identidade.json. Então o script lê daqui.

export const AUDIO = {lufs: -14, picoDbtp: -1} as const;
