// Normalização de loudness da entrega: -14 LUFS integrado com teto de -1 dBTP.
//
// ---------------------------------------------------------------------------
// POR QUE ESTE ARQUIVO EXISTE
//
// Medido no motor de origem (30/09/2026): o primeiro reel entregue saiu com
//
//   integrado  -23,02 LUFS   (alvo -14)   ->  9,0 LU abaixo
//   pico real   -3,44 dBTP   (teto  -1)
//
// No feed, 9 LU abaixo é tocar quase mudo ao lado de qualquer outro reel. O alvo
// estava declarado (`AUDIO`) e nenhum arquivo o aplicava.
//
// ---------------------------------------------------------------------------
// DEPOIS DO RENDER, NÃO ANTES
//
// Este módulo normaliza o MP4 FINAL, já renderizado, e não a narração de origem:
//
//   1. O número que importa é o do arquivo que vai ao ar. Entre a fonte e a saída
//      tem a mixagem (narração + trilha + efeitos) e o encode de áudio do Remotion.
//      Corrigir um arquivo e publicar outro é conferir o passo, não o efeito.
//   2. A peça é uma MISTURA: trilha e efeitos mudam o loudness. Medir depois vale;
//      medir antes, não.
//   3. `-c:v copy`: o fluxo de vídeo sai bit a bit igual ao que o Remotion escreveu.
//      Nenhum pixel muda.
//
// O preço é um reencode do ÁUDIO (o vídeo é copiado). Por isso a função é IDEMPOTENTE:
// se o arquivo já está dentro da tolerância, ela não reencoda, só relata.
//
// ---------------------------------------------------------------------------
// DUAS PASSADAS NÃO BASTAM: ITERA
//
// `loudnorm` numa passada só não acerta o alvo (não sabe o integrado antes de ouvir o
// arquivo inteiro): medido, passada única pedindo -14 devolveu -15,81, com exit 0. A
// receita de duas passadas chega perto, mas no modo dinâmico também não fecha:
//
//   -23,02  --1a correção-->  -14,67   (0,67 LU de erro)
//   -14,67  --2a correção-->  -14,27   (0,27 LU, dentro da EBU R128)
//
// Então a correção ITERA até cair na tolerância -- em WAV PCM, onde repetir não custa,
// e o AAC é escrito uma vez só, no fim. E no fim uma medição sobre o MP4 ESCRITO: o
// que foi medido no WAV não prova nada sobre o que saiu do encoder.
//
// ---------------------------------------------------------------------------
// TETO PEDIDO ≠ TETO VERIFICADO (a margem do AAC)
//
// O limitador entrega o pico pedido em PCM, e o encode AAC DEPOIS dele sobe o pico de
// novo. Medido (07/10/2026): mixagem com pico de +0,05 dBTP (carimbo + thump + pops
// empilhados), pedido -1 dBTP, PCM em -1, MP4 em -0,62 dBTP -- recusado. Então o teto
// PEDIDO ao loudnorm fica `MARGEM_AAC_DB` (0,6 dB) abaixo do VERIFICADO, e se o MP4
// escrito ainda passar, a tentativa seguinte pede mais baixo pelo excesso MEDIDO.
//
// ---------------------------------------------------------------------------
// LINEAR OU DINÂMICO
//
// `linear=true` aplica um ganho único e preserva a dinâmica, mas só cabe quando o ganho
// não estoura o teto de pico. Fala tem fator de crista alto (medido: 19,6 dB entre pico
// e loudness); chegar a -14 LUFS com teto de -1 dBTP exige limitador, e o `loudnorm`
// cai sozinho para o modo dinâmico. O modo usado sai no relatório (`tipo`): uma peça
// que virou dinâmica sem ninguém saber pode ter bombeado -- ouça.
//
// ---------------------------------------------------------------------------
// `ebur128` NÃO EXISTE NESTE FFMPEG
//
// O ffmpeg que vem com o Remotion é build mínima (sem `ebur128`, `fps`, `tile`):
//
//   $ ffmpeg -i x.mp4 -vn -af ebur128 -f null -
//   [AVFilterGraph] No such filter: 'ebur128'
//
// A medição é feita pelo próprio `loudnorm` em modo de análise (`print_format=json`),
// a mesma implementação de EBU R128 do libavfilter: `input_i` (LUFS) e `input_tp` (dBTP).
//
// ---------------------------------------------------------------------------
// POR QUE ESTE MÓDULO NÃO IMPORTA NADA DO PROJETO
//
// Ele é carregado por `scripts/normalizar-audio.mjs` sob `--experimental-strip-types`,
// e o type stripping do Node não resolve import local sem extensão. Então o ALVO entra
// por parâmetro -- quem chama lê `AUDIO` de `src/audio/alvo.ts` e passa.
//
// O ffmpeg/ffprobe vem de `node_modules/@remotion/compositor-*`; para usar outro, aponte
// MOTION_FFMPEG / MOTION_FFPROBE para o executável.

import {execFile} from 'node:child_process';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {promisify} from 'node:util';

const exec = promisify(execFile);
const require_ = createRequire(import.meta.url);

// ---------------------------------------------------------------------------
// binarios

function candidatosDePacote(): string[] {
  const {platform, arch} = process;
  if (platform === 'win32') return [`@remotion/compositor-win32-${arch}-msvc`];
  if (platform === 'darwin') return [`@remotion/compositor-darwin-${arch}`];
  if (platform === 'linux') {
    return [
      `@remotion/compositor-linux-${arch}-gnu`,
      `@remotion/compositor-linux-${arch}-musl`,
    ];
  }
  return [];
}

function binarioEm(dir: string, nomes: string[]): string | null {
  for (const nome of nomes) {
    const p = path.join(dir, nome);
    if (fs.existsSync(p)) return p;
  }
  return null;
}

function varrerNodeModules(nomes: string[]): string | null {
  let dir = path.dirname(fileURLToPath(import.meta.url));
  for (let i = 0; i < 8; i++) {
    const escopo = path.join(dir, 'node_modules', '@remotion');
    if (fs.existsSync(escopo)) {
      for (const nome of fs.readdirSync(escopo)) {
        if (!nome.startsWith('compositor-')) continue;
        const bin = binarioEm(path.join(escopo, nome), nomes);
        if (bin) return bin;
      }
    }
    const pai = path.dirname(dir);
    if (pai === dir) break;
    dir = pai;
  }
  return null;
}

const cache: Record<string, string> = {};

function acharBinario(
  rotulo: 'ffmpeg' | 'ffprobe',
  variavel: string,
): string {
  const guardado = cache[rotulo];
  if (guardado) return guardado;

  const doAmbiente = process.env[variavel];
  if (doAmbiente) {
    if (!fs.existsSync(doAmbiente)) {
      throw new Error(`${variavel} aponta para nada: ${doAmbiente}`);
    }
    return (cache[rotulo] = doAmbiente);
  }

  const nomes = [`${rotulo}.exe`, rotulo];
  for (const pacote of candidatosDePacote()) {
    try {
      const pkg = require_.resolve(`${pacote}/package.json`);
      const bin = binarioEm(path.dirname(pkg), nomes);
      if (bin) return (cache[rotulo] = bin);
    } catch {
      // pacote de outra plataforma nao instalado: segue
    }
  }

  const varrido = varrerNodeModules(nomes);
  if (varrido) return (cache[rotulo] = varrido);

  throw new Error(
    `${rotulo} nao encontrado. Ele vem com o Remotion em ` +
      `node_modules/@remotion/compositor-*; rode \`npm install\` ou aponte ` +
      `${variavel} para um ${rotulo}.`,
  );
}

export const caminhoFfmpeg = (): string =>
  acharBinario('ffmpeg', 'MOTION_FFMPEG');
export const caminhoFfprobe = (): string =>
  acharBinario('ffprobe', 'MOTION_FFPROBE');

/**
 * Roda o ffmpeg e devolve o stderr, que e onde ele escreve TUDO -- inclusive o
 * JSON do `loudnorm`. Um ffmpeg que falha e erro; um ffmpeg que roda e nao
 * imprime o que esperavamos tambem, e isso quem trata e o chamador.
 */
async function ffmpeg(args: string[], rotulo: string): Promise<string> {
  const bin = caminhoFfmpeg();
  try {
    const {stderr} = await exec(bin, args, {maxBuffer: 64 * 1024 * 1024});
    return stderr;
  } catch (e) {
    const err = e as {stderr?: string; message?: string};
    throw new Error(
      `${rotulo} falhou (${bin}): ${(err.stderr ?? err.message ?? '').trim()}`,
    );
  }
}

// ---------------------------------------------------------------------------
// medicao

export type Loudness = {
  /** loudness integrado, LUFS (EBU R128) */
  i: number;
  /** pico real, dBTP */
  tp: number;
  /** faixa de loudness, LU */
  lra: number;
  /** limiar relativo usado na integracao, LUFS */
  thresh: number;
  /** correcao que o loudnorm calculou para a passada seguinte */
  offset: number;
};

type JsonLoudnorm = {
  input_i: string;
  input_tp: string;
  input_lra: string;
  input_thresh: string;
  output_i: string;
  output_tp: string;
  output_lra: string;
  output_thresh: string;
  normalization_type: string;
  target_offset: string;
};

/**
 * Pega o ULTIMO objeto JSON do stderr.
 *
 * Ultimo e nao primeiro de proposito: numa passada de correcao o `loudnorm`
 * imprime o bloco no fim, e se um dia entrar mais de uma instancia do filtro no
 * grafo, o que interessa e a que fechou por ultimo.
 */
function jsonDoStderr(stderr: string, rotulo: string): JsonLoudnorm {
  const blocos = stderr.match(/\{[^{}]*"input_i"[\s\S]*?\}/g);
  if (!blocos || blocos.length === 0) {
    throw new Error(
      `${rotulo}: o loudnorm nao imprimiu o JSON de medicao. O ffmpeg rodou, ` +
        'mas sem a medicao nao da para normalizar nada. stderr:\n' +
        stderr.slice(-2000),
    );
  }
  try {
    return JSON.parse(blocos[blocos.length - 1]) as JsonLoudnorm;
  } catch (e) {
    throw new Error(
      `${rotulo}: o bloco do loudnorm nao e JSON valido: ${(e as Error).message}`,
    );
  }
}

function numero(valor: string, campo: string, rotulo: string): number {
  const n = Number(valor);
  if (!Number.isFinite(n)) {
    // `-inf` e o que o loudnorm devolve para silencio absoluto. Nao e um
    // arquivo que da para normalizar, e fingir um numero aqui seria inventar.
    throw new Error(
      `${rotulo}: ${campo} veio "${valor}", que nao e um numero. Se for ` +
        '"-inf", o arquivo esta mudo -- normalizar silencio nao faz sentido.',
    );
  }
  return n;
}

/**
 * Mede o loudness de um arquivo, em EBU R128, sem escrever nada.
 *
 * `-vn` e obrigatorio: sem ele o muxer `null` precisa de um encoder de video que
 * esta build nao tem, e o erro que volta nao tem nada a ver com audio.
 *
 * `alvo` E OBRIGATORIO PARA QUEM VAI CORRIGIR. Os campos `input_*` sao medicao
 * pura e nao dependem de alvo nenhum, mas `target_offset` depende: ele e a
 * correcao que o loudnorm calcula PARA O ALVO PEDIDO. Medir com o alvo padrao
 * do filtro (-24 LUFS / -2 dBTP) e depois usar aquele offset numa correcao para
 * -14 / -1 e alimentar a segunda passada com um numero de outro alvo. Custou
 * 0,4 LU de erro na primeira versao deste modulo, com exit 0 nas duas passadas.
 */
export async function medir(arquivo: string, alvo?: Alvo): Promise<Loudness> {
  const absoluto = path.resolve(arquivo);
  if (!fs.existsSync(absoluto)) {
    throw new Error(`nao existe o arquivo a medir: ${absoluto}`);
  }
  const filtro = alvo
    ? `loudnorm=I=${alvo.lufs}:TP=${alvo.picoDbtp}:LRA=${LRA_ALVO}:print_format=json`
    : 'loudnorm=print_format=json';
  const stderr = await ffmpeg(
    [
      '-hide_banner',
      '-nostats',
      '-i', absoluto,
      '-vn',
      '-af', filtro,
      '-f', 'null',
      '-',
    ],
    `medicao de loudness de ${path.basename(absoluto)}`,
  );
  const j = jsonDoStderr(stderr, `medicao de ${path.basename(absoluto)}`);
  const r = `medicao de ${path.basename(absoluto)}`;
  return {
    i: numero(j.input_i, 'input_i', r),
    tp: numero(j.input_tp, 'input_tp', r),
    lra: numero(j.input_lra, 'input_lra', r),
    thresh: numero(j.input_thresh, 'input_thresh', r),
    offset: numero(j.target_offset, 'target_offset', r),
  };
}

// ---------------------------------------------------------------------------
// parametros do audio de origem

export type Audio = {codec: string; taxa: number; canais: number};

/**
 * Le codec, taxa e canais do fluxo de audio.
 *
 * A taxa importa: o `loudnorm` trabalha internamente a 192 kHz (e o
 * sobreamostramento que ele usa para achar o pico REAL, que mora entre as
 * amostras). Se ninguem disser `-ar`, o arquivo sai a 192 kHz -- roda, toca, e
 * e um MP4 de 192 kHz que nenhuma rede social pediu. Entao a taxa de entrada e
 * lida e reimposta na saida.
 */
export async function parametrosDeAudio(arquivo: string): Promise<Audio> {
  const bin = caminhoFfprobe();
  const absoluto = path.resolve(arquivo);
  const {stdout} = await exec(
    bin,
    [
      '-v', 'error',
      '-select_streams', 'a:0',
      '-show_entries', 'stream=codec_name,sample_rate,channels',
      '-of', 'json',
      absoluto,
    ],
    {maxBuffer: 8 * 1024 * 1024},
  );
  const j = JSON.parse(stdout) as {
    streams?: {codec_name?: string; sample_rate?: string; channels?: number}[];
  };
  const s = j.streams?.[0];
  if (!s || !s.sample_rate || !s.channels) {
    throw new Error(
      `${absoluto} nao tem fluxo de audio legivel. Um MP4 sem audio nao se ` +
        'normaliza -- confira se o render incluiu a trilha.',
    );
  }
  return {
    codec: s.codec_name ?? 'desconhecido',
    taxa: Number(s.sample_rate),
    canais: s.channels,
  };
}

// ---------------------------------------------------------------------------
// normalizacao

export type Alvo = {
  /** loudness integrado alvo, LUFS. Vem de `AUDIO.lufs` (src/audio/alvo.ts). */
  lufs: number;
  /** teto de pico real, dBTP. Vem de `AUDIO.picoDbtp` (src/audio/alvo.ts). */
  picoDbtp: number;
};

export type Passo = {
  /** 1, 2, ... */
  iteracao: number;
  antes: Loudness;
  depois: Loudness;
  /** `linear` ou `dynamic`, conforme o loudnorm decidiu sozinho */
  tipo: string;
};

export type Relatorio = {
  entrada: string;
  saida: string;
  alvo: Alvo;
  /** loudness do arquivo de entrada */
  antes: Loudness;
  /** loudness do MP4 REALMENTE escrito, medido depois do encode de AAC */
  depois: Loudness;
  /** ganho integrado total, em LU */
  ganhoLu: number;
  /** o que aconteceu em cada iteracao sobre o WAV */
  passos: Passo[];
  /** modo da ultima correcao: `linear`, `dynamic` ou `nenhum` */
  tipo: string;
  /** true quando nada foi reencodado porque ja estava no alvo */
  pulou: boolean;
  audio: Audio;
  /** quanto abaixo do teto o loudnorm mirou, em dB, e em quantas tentativas */
  margemPicoDb?: number;
  tentativas?: number;
};

/**
 * Faixa de loudness alvo passada ao filtro.
 *
 * 11 LU e o valor de entrega para streaming a -14 LUFS. Fica ACIMA da faixa
 * medida na fonte (5,10 LU) de proposito: o `loudnorm` nao expande dinamica, so
 * a comprime quando o medido passa do alvo, entao um LRA folgado e a forma de
 * dizer "nao comprima". Baixar isso e pedir bombeamento.
 */
const LRA_ALVO = 11;

/**
 * Tolerancia padrao, em LU.
 *
 * 0,5 LU e a tolerancia da EBU R128. Na peca de origem o resultado medido caiu em
 * -14,27 LUFS depois de duas iteracoes, entao 0,5 e alcancavel e serve como
 * portao de verdade -- nao como numero folgado o bastante para nunca reprovar.
 */
export const TOLERANCIA_LU = 0.5;

/**
 * Folga no teto de pico, em dB.
 *
 * O limitador do `loudnorm` mira o teto pedido mas pousa consistentemente uns
 * centesimos acima (medido: -0,93 e -0,96 dBTP contra um teto de -1), e o
 * encode de AAC depois disso mexe de novo no pico real. 0,3 dB cobre os dois
 * efeitos sem deixar passar um arquivo que de fato estoure.
 */
const FOLGA_PICO_DB = 0.3;

/**
 * Margem de pico para o AAC, em dB: o teto PEDIDO ao loudnorm fica isto abaixo do
 * teto VERIFICADO.
 *
 * Medido na peça de origem (07/10/2026): a mixagem saiu do Remotion com pico real de
 * +0,05 dBTP (carimbo + thump + pops empilhados); pedindo -1 dBTP o limitador
 * entregou -1 em PCM e o encode AAC devolveu o pico a -0,62 dBTP no MP4 — 0,08 dB
 * além da folga, e o arquivo foi recusado. Pedindo -1,6 o MP4 mediu -1,17 dBTP e
 * -14,20 LUFS. A folga acima continua sendo a do teto verificado.
 *
 * É só o PONTO DE PARTIDA: quanto o AAC sobe o pico depende do conteúdo (rajada de
 * ruído de 6 ms a 0 dBFS subiu 2,2 dB, medido). Se o MP4 escrito passar do teto, a
 * próxima tentativa pede o teto mais baixo pelo excesso MEDIDO — ver `normalizar`.
 */
const MARGEM_AAC_DB = 0.6;

/** Tentativas de encode com margem corrigida pelo excesso de pico medido. */
const MAX_TENTATIVAS_PICO = 3;

/**
 * Teto de iteracoes.
 *
 * Medido na peca de origem: 1a iteracao -23,02 -> -14,67 (erro 0,67), 2a -> -14,27
 * (erro 0,27). Converge rapido porque o que sobra depois da primeira e ganho
 * quase linear. 4 e teto de seguranca, nao expectativa.
 */
const MAX_ITERACOES = 4;

function dentroDoAlvo(m: Loudness, alvo: Alvo, tolerancia: number): boolean {
  return (
    Math.abs(m.i - alvo.lufs) <= tolerancia &&
    m.tp <= alvo.picoDbtp + FOLGA_PICO_DB
  );
}

/** Uma passada de correcao do loudnorm, com o medido ja na mao. */
function filtroDeCorrecao(m: Loudness, alvo: Alvo): string {
  return (
    `loudnorm=I=${alvo.lufs}:TP=${alvo.picoDbtp}:LRA=${LRA_ALVO}` +
    `:measured_I=${m.i}:measured_TP=${m.tp}` +
    `:measured_LRA=${m.lra}:measured_thresh=${m.thresh}` +
    `:offset=${m.offset}:linear=true:print_format=json`
  );
}

/**
 * Normaliza `entrada` para o alvo e escreve em `saida`.
 *
 * ---------------------------------------------------------------------------
 * POR QUE A ITERACAO ACONTECE EM WAV E NAO NO MP4
 *
 * Uma passada de `loudnorm` nao chega no alvo quando o modo cai para dinamico:
 * medido aqui, -23,02 vira -14,67 e nao -14,00. Uma segunda passada leva a
 * -14,27, dentro da tolerancia da EBU. So que iterar sobre o MP4 significa um
 * encode de AAC POR ITERACAO -- tres gravacoes em cima da mesma voz.
 *
 * Entao o audio sai uma vez para WAV PCM, a iteracao inteira acontece em PCM
 * (onde repetir nao custa nada, porque nao ha compressao com perda no meio) e o
 * AAC e encodado UMA vez so, no fim, junto com `-c:v copy`. O arquivo entregue
 * tem exatamente uma geracao de AAC a mais que o render -- o minimo possivel
 * para mudar o loudness.
 *
 * ---------------------------------------------------------------------------
 * `saida` pode ser igual a `entrada`: nesse caso escreve num temporario ao lado
 * e troca no fim, porque o ffmpeg nao le e escreve o mesmo arquivo.
 *
 * Nao confia no codigo de saida do ffmpeg: RE-MEDE o MP4 escrito, depois do
 * AAC, e joga erro se ele nao caiu dentro da tolerancia. Um encode que roda e
 * erra o alvo e exatamente o modo de falha que este modulo existe para acabar.
 */
export async function normalizar(o: {
  entrada: string;
  saida: string;
  alvo: Alvo;
  /** bitrate do AAC de saida. 192k para estereo e o piso do que nao degrada voz. */
  bitrate?: string;
  toleranciaLu?: number;
  maxIteracoes?: number;
}): Promise<Relatorio> {
  const entrada = path.resolve(o.entrada);
  const saida = path.resolve(o.saida);
  const bitrate = o.bitrate ?? '192k';
  const tolerancia = o.toleranciaLu ?? TOLERANCIA_LU;
  const maxIteracoes = o.maxIteracoes ?? MAX_ITERACOES;

  if (!fs.existsSync(entrada)) {
    throw new Error(`nao existe o arquivo a normalizar: ${entrada}`);
  }
  for (const [nome, v] of [
    ['alvo.lufs', o.alvo.lufs],
    ['alvo.picoDbtp', o.alvo.picoDbtp],
  ] as const) {
    if (!Number.isFinite(v)) throw new Error(`${nome} tem que ser numero, veio ${v}`);
  }
  if (o.alvo.picoDbtp > 0) {
    throw new Error(
      `alvo.picoDbtp = ${o.alvo.picoDbtp}: teto de pico acima de 0 dBTP e ` +
        'distorcao pedida por escrito.',
    );
  }
  if (!Number.isInteger(maxIteracoes) || maxIteracoes < 1) {
    throw new Error(`maxIteracoes tem que ser inteiro >= 1, veio ${maxIteracoes}`);
  }

  const audio = await parametrosDeAudio(entrada);
  const antes = await medir(entrada, o.alvo);

  // Ja esta no alvo: nao reencoda. Cada passagem pelo AAC custa qualidade, e
  // rodar o pipeline duas vezes nao pode degradar a peca.
  if (dentroDoAlvo(antes, o.alvo, tolerancia)) {
    if (entrada !== saida) fs.copyFileSync(entrada, saida);
    return {
      entrada, saida, alvo: o.alvo, antes, depois: antes,
      ganhoLu: 0, passos: [], tipo: 'nenhum', pulou: true, audio,
    };
  }

  const temporarios: string[] = [];
  const temp = (nome: string): string => {
    const p = path.join(
      path.dirname(saida),
      `.${path.basename(saida)}.${nome}.tmp`,
    );
    temporarios.push(p);
    return p;
  };

  try {
    fs.mkdirSync(path.dirname(saida), {recursive: true});

    // --- audio para PCM, uma vez. 24 bits: a iteracao aplica ganho varias
    //     vezes e 16 bits acumularia ruido de quantizacao a toa.
    const wav = temp('a0.wav');
    await ffmpeg(
      [
        '-hide_banner', '-nostats', '-y',
        '-i', entrada,
        '-vn',
        '-c:a', 'pcm_s24le',
        '-ar', String(audio.taxa),
        // extensao real e .tmp: o muxer NAO pode ser inferido, tem que ser dito.
        '-f', 'wav',
        wav,
      ],
      `extracao do audio de ${path.basename(entrada)}`,
    );

    // --- itera em PCM ate cair na tolerancia, pedindo ao loudnorm um teto
    //     `margem` abaixo do verificado: o AAC sobe o pico depois do limitador.
    const iterarEmPcm = async (margem: number, tentativa: number) => {
      const pedido: Alvo = {...o.alvo, picoDbtp: o.alvo.picoDbtp - margem};
      const passos: Passo[] = [];
      let atual = wav;
      let medida = await medir(atual, pedido);
      let tipo = 'nenhum';

      for (let n = 1; n <= maxIteracoes; n++) {
        if (dentroDoAlvo(medida, pedido, tolerancia)) break;

        const proximo = temp(`t${tentativa}a${n}.wav`);
        const stderr = await ffmpeg(
          [
            '-hide_banner', '-nostats', '-y',
            '-i', atual,
            '-af', filtroDeCorrecao(medida, pedido),
            '-c:a', 'pcm_s24le',
            '-ar', String(audio.taxa),
            '-f', 'wav',
            proximo,
          ],
          `correcao de loudness, tentativa ${tentativa}, iteracao ${n}`,
        );
        tipo = jsonDoStderr(stderr, `iteracao ${n}`).normalization_type;

        const depoisDoPasso = await medir(proximo, pedido);
        passos.push({iteracao: n, antes: medida, depois: depoisDoPasso, tipo});

        // Nao adianta insistir se parou de melhorar: isso e o limitador tendo
        // chegado ao teto de pico, e mais uma volta so reencoda por nada.
        const melhorou =
          Math.abs(depoisDoPasso.i - o.alvo.lufs) <
          Math.abs(medida.i - o.alvo.lufs) - 0.05;

        atual = proximo;
        medida = depoisDoPasso;
        if (!melhorou) break;
      }
      return {pcm: atual, passos, tipo};
    };

    // --- UM encode de AAC por tentativa, com o video copiado bit a bit. Se o MP4
    //     escrito passar do teto de pico, a margem cresce pelo excesso MEDIDO e a
    //     tentativa seguinte refaz a partir do PCM original.
    let margem = MARGEM_AAC_DB;
    const excessos: string[] = [];
    for (let tentativa = 1; ; tentativa++) {
      const {pcm, passos, tipo} = await iterarEmPcm(margem, tentativa);
      const mp4 = temp(`saida${tentativa}.mp4`);
      await ffmpeg(
        [
          '-hide_banner', '-nostats', '-y',
          '-i', entrada,
          '-i', pcm,
          '-map', '0:v:0',
          '-map', '1:a:0',
          // Nenhum pixel muda: o video sai bit a bit igual ao do render.
          '-c:v', 'copy',
          '-c:a', 'aac', '-b:a', bitrate,
          '-movflags', '+faststart',
          // O audio corrigido tem a mesma duracao do original, mas se algum dia
          // divergir por um quadro e o video que manda.
          '-shortest',
          // mesmo motivo do '-f wav' acima: a extensao real e .tmp.
          '-f', 'mp4',
          mp4,
        ],
        `remux de ${path.basename(entrada)} com o audio normalizado`,
      );

      // --- a prova: medir o MP4 escrito, DEPOIS do AAC. O que foi medido no WAV
      //     nao vale como garantia do que saiu do encoder.
      const depois = await medir(mp4, o.alvo);
      const erro = Math.abs(depois.i - o.alvo.lufs);
      if (erro > tolerancia) {
        throw new Error(
          `a normalizacao rodou e errou o alvo: pedi ${o.alvo.lufs} LUFS e o ` +
            `MP4 escrito mede ${depois.i} LUFS (${erro.toFixed(2)} LU de erro, ` +
            `tolerancia ${tolerancia} LU) depois de ${passos.length} ` +
            `iteracao(oes). Modo do loudnorm: ${tipo}.`,
        );
      }
      if (depois.tp > o.alvo.picoDbtp + FOLGA_PICO_DB) {
        excessos.push(`margem ${margem.toFixed(2)} dB -> ${depois.tp} dBTP`);
        if (tentativa >= MAX_TENTATIVAS_PICO) {
          throw new Error(
            `a normalizacao passou do teto de pico: pedi ${o.alvo.picoDbtp} dBTP ` +
              `e o MP4 escrito mede ${depois.tp} dBTP (folga permitida ` +
              `${FOLGA_PICO_DB} dB) depois de ${tentativa} tentativas ` +
              `(${excessos.join('; ')}).`,
          );
        }
        margem += depois.tp - o.alvo.picoDbtp + 0.15;
        continue;
      }

      fs.rmSync(saida, {force: true});
      fs.renameSync(mp4, saida);

      return {
        entrada, saida, alvo: o.alvo, antes, depois,
        ganhoLu: Number((depois.i - antes.i).toFixed(2)),
        passos, tipo, pulou: false, audio,
        margemPicoDb: Number(margem.toFixed(2)), tentativas: tentativa,
      };
    }
  } finally {
    // Nunca deixar temporario para tras, nem quando deu errado no meio.
    for (const t of temporarios) fs.rmSync(t, {force: true});
  }
}
