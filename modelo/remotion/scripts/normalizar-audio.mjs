// Passo de áudio da conferência: leva o MP4 renderizado a -14 LUFS / -1 dBTP.
//
//   node scripts/normalizar-audio.mjs --peca=<NN-tema>              (../pecas/<NN-tema>/saida/reel.mp4)
//   node scripts/normalizar-audio.mjs --arquivo=../pecas/<NN-tema>/saida/reel.mp4
//   node scripts/normalizar-audio.mjs --arquivo=... --medir         (só mede, não escreve)
//
// `--arquivo` é relativo à pasta de onde você rodou (ou absoluto); `--peca` é relativo a
// `motion/pecas/`. Reescreve o próprio arquivo.
//
// RODA DEPOIS DO RENDER. O vídeo é copiado com `-c:v copy`, então nenhum pixel muda --
// mas o arquivo passa a ser o que vai ao ar de verdade, já com o áudio certo. Se o render
// for refeito, rode de novo: o MP4 novo sai com o áudio cru outra vez. É idempotente:
// rodar duas vezes no mesmo arquivo não reencoda a segunda.
//
// O teto de pico PEDIDO ao loudnorm fica 0,6 dB abaixo do VERIFICADO (o AAC sobe o pico
// depois do limitador) e, se o MP4 escrito ainda passar, refaz pedindo mais baixo pelo
// excesso medido. "modo dynamic" no relatório = houve limitação: ouça a peça.
//
// POR QUE ESTE SCRIPT SE RELANÇA: o módulo de áudio é TypeScript e o Node só o carrega
// com `--experimental-strip-types` (Node >= 22.6), que não dá para ligar de dentro do
// processo já rodando. E é por isso que o ALVO vem de `src/audio/alvo.ts`, que não
// importa nada: o type stripping não resolve import local sem extensão nem JSON.

import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const FLAG = '--experimental-strip-types';

if (!process.execArgv.includes(FLAG)) {
  const filho = spawn(
    process.execPath,
    [FLAG, '--no-warnings', fileURLToPath(import.meta.url), ...process.argv.slice(2)],
    {stdio: 'inherit'},
  );
  filho.on('close', (codigo) => process.exit(codigo ?? 1));
  filho.on('error', (e) => {
    console.error(`não consegui me relançar com ${FLAG}: ${e.message}`);
    process.exit(1);
  });
} else {
  try {
    await principal();
  } catch (e) {
    console.error(`\nFALHA  ${e.message}`);
    if (process.env.MOTION_PILHA) console.error(e);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------

function argumentos() {
  const a = {peca: '', arquivo: '', medir: false};
  for (const cru of process.argv.slice(2)) {
    if (cru === '--medir') {
      a.medir = true;
      continue;
    }
    const m = /^--([a-zA-Z]+)=(.*)$/.exec(cru);
    if (!m) throw new Error(`argumento não entendido: ${cru}. Use --peca=<NN-tema>, --arquivo=<mp4> ou --medir.`);
    const [, chave, valor] = m;
    if (!(chave in a) || chave === 'medir') {
      throw new Error(`--${chave} não existe. Válidos: --peca=<NN-tema>, --arquivo=<mp4>, --medir.`);
    }
    a[chave] = valor;
  }
  if (!a.peca && !a.arquivo) {
    throw new Error('diga o que normalizar: --peca=<NN-tema> (saida/reel.mp4 da peça) ou --arquivo=<mp4>.');
  }
  return a;
}

// DECLARAÇÃO de função, não `const`: este arquivo tem `await principal()` no topo, e uma
// `const` declarada depois dele ainda está na zona morta quando `principal` roda.
function sinal(v) {
  return v >= 0 ? `+${v.toFixed(2)}` : v.toFixed(2);
}

async function principal() {
  const a = argumentos();
  const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const arquivo = a.arquivo
    ? path.resolve(process.cwd(), a.arquivo)
    : path.resolve(raiz, '..', 'pecas', a.peca, 'saida', 'reel.mp4');
  if (!fs.existsSync(arquivo)) {
    throw new Error(`não existe: ${arquivo}. Renderize antes (fase 08).`);
  }

  const {AUDIO} = await import('../src/audio/alvo.ts');
  const {medir, normalizar} = await import('../src/audio/normalizar.ts');
  const alvo = {lufs: AUDIO.lufs, picoDbtp: AUDIO.picoDbtp};

  console.log(`\n== alvo (src/audio/alvo.ts) ==`);
  console.log(`  ${alvo.lufs} LUFS integrado · teto ${alvo.picoDbtp} dBTP`);
  console.log(`\n== ${arquivo} ==`);

  if (a.medir) {
    const m = await medir(arquivo);
    console.log(`  integrado ${sinal(m.i)} LUFS · pico real ${sinal(m.tp)} dBTP · faixa ${m.lra.toFixed(2)} LU`);
    console.log(`  distância do alvo: ${sinal(alvo.lufs - m.i)} LU`);
    return;
  }

  const r = await normalizar({entrada: arquivo, saida: arquivo, alvo});
  console.log(`  áudio    ${r.audio.codec} ${r.audio.taxa} Hz ${r.audio.canais} canais`);
  console.log(`  antes    ${sinal(r.antes.i)} LUFS · ${sinal(r.antes.tp)} dBTP · faixa ${r.antes.lra.toFixed(2)} LU`);
  if (r.pulou) {
    console.log('  já estava no alvo: não reencodei (evita perda de geração).');
    return;
  }
  for (const p of r.passos) {
    console.log(`  it. ${p.iteracao}    ${sinal(p.antes.i)} -> ${sinal(p.depois.i)} LUFS · ${sinal(p.depois.tp)} dBTP · ${p.tipo}`);
  }
  console.log(`  depois   ${sinal(r.depois.i)} LUFS · ${sinal(r.depois.tp)} dBTP · faixa ${r.depois.lra.toFixed(2)} LU   <- medido no MP4 escrito`);
  console.log(`  ganho    ${sinal(r.ganhoLu)} LU · modo loudnorm: ${r.tipo}`);
  console.log(`  pico     loudnorm mirou ${r.margemPicoDb} dB abaixo do teto (margem para o AAC), ${r.tentativas} tentativa(s)`);
  if (r.tipo !== 'linear') {
    console.log(`  ATENÇÃO: modo ${r.tipo}, não linear -- o ganho necessário não cabia sob o teto de pico, então houve limitação. Ouça a peça.`);
  }
  console.log('\náudio OK. Se o render for refeito, rode isto outra vez.\n');
}
