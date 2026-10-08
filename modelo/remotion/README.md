# Motor de colagem (`motion/remotion/`)

Motor Remotion da semente `estudio-reels`: Reels 9:16 em motion de colagem narrado, com
câmera 2.5D, legenda em dois sistemas (A = pílula, B = colagem) e todo tempo lido da
narração. Portado do motor da peça de origem da semente (aprovada pelo cliente em
07/10/2026) e generalizado: nenhuma cor, fonte, logo ou fato de marca no código — tudo vem
de `motion/marca/identidade.json`.

O plantio (`modelo/plantar.py`) copia esta pasta para `<repo>/motion/remotion/` (sem
`node_modules`). Fora de um repositório plantado ela **não compila**: `tokens.ts` importa
`../../../marca/identidade.json` e o esqueleto importa
`../../../../pecas/00-exemplo/palavras.json` (contrato C3/C5).

## Requisitos

- **Node ≥ 22.12** e npm. O `vitest` 5 exige Node `^22.12 || ^24 || >=26`, e
  `scripts/normalizar-audio.mjs` carrega TypeScript com `--experimental-strip-types`
  (Node ≥ 22.6). Node abaixo de 22.12 (18, 20 ou 22.0–22.11) instala, mas os testes não rodam.
- `npm install` **com o `package-lock.json` que vem junto**. Versões exatas (Remotion
  4.0.530 em todos os `@remotion/*`). Sem o lock, o npm 10 quebra com `Cannot read
  properties of null (reading 'edgesOut')` ao resolver os peers opcionais do vitest
  (medido em 08/10/2026): não apague o lock.
- O `ffmpeg`/`ffprobe` vêm com o Remotion (`node_modules/@remotion/compositor-*`); é build
  mínima (sem `ebur128`, `fps`, `tile`).

## O que mora onde

| Caminho | Papel |
|---|---|
| `src/index.ts` · `src/Raiz.tsx` | registra as composições: `Exemplo` (1080×1920, 30 fps, a peça modelo) e `Marca` (conferência da identidade, 1 quadro) |
| `src/identidade/identidade.ts` | formato e **validação** do `identidade.json` (C3): cor fora de `#RRGGBB`, papel faltando, fonte padrão com família trocada, logo fora de `logo-*.png\|svg\|webp` — tudo vira erro com o nome do campo |
| `src/identidade/tokens.ts` | `IDENTIDADE`, `COR` (`escuro/claro/profundo/acento/apoio`), `TIPO`, `AUDIO` |
| `src/identidade/tipografia.ts` · `guarda-fonte.ts` · `fontes/` | carrega as 3 famílias (`arquivo: null` = Archivo Black 400, Inter 700, IBM Plex Mono 500, OFL, empacotadas) e **prova** cada uma: largura contra o fallback e glifos do idioma (`ÁÂÃÀÇÉÊÍÓÔÕÚ…` no pt). Reprovou = `cancelRender` |
| `src/identidade/arquivos-marca.ts` | logos e fontes próprias de `motion/marca/` entram no bundle (`require.context`): lugar único e versionado, vale para toda composição |
| `src/identidade/cor.ts` | `rgba`, `misturar`, `contraste` (WCAG), `tintaPara` (letra clara ou escura conforme o fundo) |
| `src/audio/alvo.ts` · `src/audio/normalizar.ts` | alvo −14 LUFS / −1 dBTP e o normalizador (itera em PCM, um AAC só, mede o MP4 escrito, teto pedido 0,6 dB abaixo e novas tentativas pelo excesso medido) |
| `src/colagem/camera.ts` · `palco.tsx` | câmera 2.5D (chaves, `deriva`, `pulso`, `tremor`, `cameraCena`) e planos de profundidade; chicote com blur direcional |
| `src/colagem/legenda.ts` | `Roteiro` (`b`/`mudo`/`t`, `em`, `depois`) e `blocosA` (pílula: ≤ 4 palavras, ≤ 16 caracteres, sem fechar em palavra fraca) |
| `src/colagem/tipos.tsx` | `Dymo`, `Serifa`, `Marcador` (`dur={fala(faixa)}`), `Recortadas`, `Pilula` |
| `src/colagem/grafismos.tsx` | `Elipse`, `Seta`, `Sublinhado`, `Xis`, `Check`, `Asterisco`, `Brilho`, `Cruz` |
| `src/colagem/pecas.tsx` | `Recorte`, `Troca`, `Fita`, `Tachinha` (de `public/colagem/`), `Carimbo`, `Manchete`, `Rotulo`, `Tira`, `ProdutoRecortado`, `LogoMarca` |
| `src/colagem/atmosfera.tsx` | `Fundo` (papel procedural ou textura), `GraoFilme` (procedural), `Vinheta`, `Foco`, `Sombra`, `Cobertura`, `Divisoria`, `Rodape` |
| `src/colagem/area-segura.ts` | `AREA_SEGURA` (orgânico e anúncio) e `yDaPilula` |
| `src/colagem/chicote.ts` | tempo do chicote (`chicoteEm`, `cenaEm`, `problemasDosChicotes`) |
| `src/colagem/sons.ts` · `som-tolerante.tsx` | nomes dos efeitos que `motion/ferramentas/sons.py` grava e as regras de tempo do som; a tolerância a áudio ausente, só da composição de exemplo |
| `src/colagem/movimento-colagem.ts` · `semente.ts` · `papel.ts` · `fontes-colagem.ts` | gestos em stop-motion, aleatoriedade com semente, cores de material, Instrument Serif + Permanent Marker |
| `src/pecas/_modelo/` | o esqueleto: `roteiro.ts`, `apoio.tsx` (relógio `fq`/`fala` + kit), `cenas.tsx` (gancho, conteúdo, fecho), `Peca.tsx` (chicote colado, pílula, grão), `Sons.tsx` |
| `scripts/contato.mjs` | folha de contato com o instante escrito em cada célula |
| `scripts/normalizar-audio.mjs` | passo de áudio da conferência |
| `tests/` | câmera e legenda, limites da pílula (com mutação), área segura, movimento, chicote, identidade, o portão de A/B da peça modelo e o portão "nenhum segundo digitado" (`modelo-tempos.test.ts`, as duas varreduras da fase 07) |

## Comandos (de `motion/remotion/`)

```bash
npm install                    # usa o package-lock.json
npx tsc --noEmit
npx vitest run
npx remotion still src/index.ts Exemplo ../pecas/00-exemplo/saida/exemplo.png --frame=60 --public-dir=../pecas/00-exemplo/public
npx remotion still src/index.ts Marca ../pecas/00-exemplo/saida/marca.png --public-dir=../pecas/00-exemplo/public
npx remotion studio src/index.ts --public-dir=../pecas/<NN-tema>/public
node scripts/contato.mjs <Comp> <NN-tema> <s1,s2,...> [--escala=0.25] [--cols=8] [--saida=nome.png]
npx remotion render src/index.ts <Comp> ../pecas/<NN-tema>/saida/reel.mp4 --public-dir=../pecas/<NN-tema>/public
node scripts/normalizar-audio.mjs --peca=<NN-tema>          # ou --arquivo=<mp4> [--medir]
```

- `contato.mjs` recebe **segundos**; sem lista (ou `-`), um quadro a cada 2,5 s. Stills em
  `../pecas/<NN-tema>/saida/stills/`, folha em `saida/<nome>`; `--saida` com barra é caminho
  (relativo a onde você rodou).
- `normalizar-audio.mjs --arquivo` é relativo a onde você rodou; reescreve o arquivo e é
  idempotente. "modo dynamic" no relatório = houve limitação: ouça a peça.
- **Windows: pasta curta.** O `chrome-headless-shell` falha com `ENOENT` quando o caminho
  passa de 260 caracteres; plante o repositório num caminho curto (ex.: `C:/r/marca`).
- Render em segundo plano. Para abortar no Windows, ache o `node` pela linha de comando que
  cita a composição e derrube a árvore (`taskkill /PID <pid> /T /F`); nunca mate
  `chrome-headless-shell` às cegas.

## Peça nova (fase 07)

1. `cp -r src/pecas/_modelo src/pecas/<NN-tema>` e `grep -rn "00-exemplo" src/pecas/<NN-tema>/`:
   só o `roteiro.ts` aparece; troque `00-exemplo` por `<NN-tema>` no import do
   `palavras.json` (um `sed` na pasta da peça serve).
2. Copie `tests/modelo-roteiro.test.ts` para `tests/<NN-tema>-roteiro.test.ts`, troque
   `_modelo` por `<NN-tema>` no import e o `FIM` esperado. Copie também
   `tests/modelo-tempos.test.ts` para `tests/<NN-tema>-tempos.test.ts` e troque `'_modelo'` por
   `'<NN-tema>'` na constante `PASTA` (o portão "nenhum segundo digitado"); as duas exceções
   ficam como estão.
3. Escreva o `roteiro.ts` na ordem da fala, as cenas e os `EFEITOS`. **Nenhum segundo
   digitado**: `S1.x.inicio`, `em(faixa, 'palavra')`, `depois(faixa)`, `TROCA`,
   `CENA_INICIO`, `FIM` (derivado: última palavra + 0,5 s, para cima ao décimo — a mesma
   conta do `DUR` do `sons.py`).
4. Registre em `src/Raiz.tsx`:
   `import * as P01 from './pecas/01-tema/Peca';` e
   `<Composition id="P01-tema" component={P01.Peca} durationInFrames={P01.DURACAO} fps={P01.FPS} width={1080} height={1920} />`.
5. `python motion/ferramentas/sons.py motion/pecas/<NN-tema>` (da raiz do repositório), depois
   `tsc`, `vitest` e a folha de contato.

## Regras que o motor carrega

- **Toda troca de enquadramento tem chicote ou cobertura.** Chicote = `CHICOTES` em
  `Peca.tsx`: a imagem que sai e a que entra andam COLADAS, uma tela em 12 quadros, cada uma
  congelada no último/primeiro quadro. Janela fora da peça ou chicotes a menos de 12 quadros
  um do outro derrubam o bundle. Cobertura de papel: 7 quadros, na cor do fundo que entra.
- **Câmera nunca para** (`deriva`), `pulso` nas palavras-colagem, `tremor` só no impacto;
  entradas em stop-motion (`posterizar`), só a câmera é lisa.
- **Área segura** (`src/colagem/area-segura.ts`, `AREA_SEGURA.organico/anuncio`): orgânico,
  texto em x 140–940 em repouso, y 96–1613, pílula em y = 1500; anúncio, y 269–1248 e
  x 65–1015, `<Pilula formato="anuncio">` com centro em 1210. O esqueleto é orgânico.
- **Letra é sempre código**; logo e produto entram como **pixel**, nunca redesenhados. Texto
  nunca cobre logotipo nem selo: meça o bbox do alfa do recorte antes.
- **Assets da peça**: tudo o que a biblioteca publica (recortes, produto, texturas) mora em
  `public/colagem/` (`<nome>-b0|b1|b2.png`, ou `<nome>.png` para peça única).
- **Logo e fontes da marca** vêm de `motion/marca/` pelo bundler, nunca de `public/`:
  `logo.sobre_claro` em fundo claro, `logo.sobre_escuro` em fundo escuro. Sem logo, só a
  identidade de exemplo (`"exemplo": true`) desenha um marcador de lugar; numa marca real o
  render cai com a mensagem do campo.
- **Áudio** (`Sons.tsx`): `public/fonte/narracao.mp3` + `public/sfx/trilha.wav` +
  `public/sfx/<efeito>.wav`. Numa peça real tudo é exigido: arquivo que falta derruba o
  render do vídeo com 404 (still e contato só registram no log). Só a composição `Exemplo`
  (sem narração gravada) toca apenas o que existe: o `Raiz.tsx` a envolve em
  `<SomTolerante>`, e uma peça copiada do `_modelo` não leva isso junto. Nenhuma duração de
  efeito é digitada: o drone e o vento ficam abertos até o fim da peça e acabam sozinhos.
- **Identidade legível**: `tests/identidade.test.ts` exige contraste ≥ 4,5:1 de `claro`
  sobre `escuro` e sobre `profundo` (a pílula); sobre o `acento`, a letra escolhe sozinha a
  tinta que contrasta (`tintaPara`).

## O que mudou em relação à peça de origem

- Cores por papel (`preto→escuro`, `creme→claro`, `terra→profundo`, `verde→apoio`, `acento`)
  lidas do `identidade.json`, validado.
- `Embalagem` (3 produtos fixos da origem, PNG deitado) → `ProdutoRecortado` (qualquer recorte de
  `public/colagem/`, altura em pé, `giro` opcional em CSS, dimensões lidas do arquivo).
- Logo de `fonte/logo-preta.png` → `LogoMarca`, de `motion/marca/` pelo identidade.json.
- Componentes da peça de origem duplicados entre o motor e a peça (`Recorte`/`Peca`, duas
  `Fita`, `Folha`/`Cobertura`, `Campo`/`Fundo`) viraram um só, no motor; o `apoio.tsx` da
  peça os reexporta. `em()`/`depois()` viraram métodos do `Roteiro`.
- Papel e grão de filme procedurais (semente fixa), para a peça nunca sair em cor chapada
  antes de existir textura na biblioteca; textura real entra por `<Fundo textura=...>`.
- A guarda de fonte passou a conferir também os glifos do idioma.
- `contato.mjs` escreve o instante em cada célula; `normalizar-audio.mjs` recebe `--peca`.

## Verificação (Step 5 da Tarefa 3)

Cópia de trabalho em `%TEMP%/estudio-reels-teste/motion/` (remotion + `marca/identidade.json`
de exemplo + `pecas/00-exemplo/`), fora da semente.

Node 22.16.0 · npm 10.9.2 · Windows 11. Instalação limpa a partir do lock da semente:

```text
$ npm install --no-audit --no-fund
added 288 packages in 31s

$ npx tsc --noEmit
(exit 0)

$ npx vitest run
 Test Files  7 passed (7)
      Tests  64 passed (64)

$ npx remotion still src/index.ts Exemplo saida.png --frame=60 --public-dir=../pecas/00-exemplo/public
Downloading Chrome Headless Shell ... Got Headless Shell        (só no 1º render: 113 MB)
Getting composition
[fonte] colagem Instrument Serif italic ok
[fonte] colagem Permanent Marker normal ok
[fonte] manchete Archivo Black 400 (src/identidade/fontes/ArchivoBlack-Regular.ttf) - amostra 1777.2px (fallback seria 1301.6px)
[fonte] corpo    Inter 700 (src/identidade/fontes/Inter-Bold.ttf) - amostra 1563.5px (fallback seria 1380.5px)
[fonte] dado     IBM Plex Mono 500 (src/identidade/fontes/IBMPlexMono-Medium.ttf) - amostra 1824.0px (fallback seria 1301.6px)
+ saida.png                                                    (exit 0; 1080x1920, aberto e olhado)
```

Conferido também nesta sessão (mesmo código; a marca de teste e os erros numa cópia anterior):

- `contato.mjs Exemplo 00-exemplo` com 18 instantes (incluindo dois DENTRO de cada chicote e
  um na cobertura): as 3 cenas, as duas imagens coladas no chicote, a pílula nas duas versões;
  nenhum 404 no log (o exemplo não exige áudio).
- `Marca`: cores, as 5 famílias com os acentos, logos e pílula; depois com uma marca de teste
  (`exemplo: false`, `logo-escura.png`/`logo-clara.png` e fonte própria em
  `motion/marca/fontes/`): os logos entram como pixel e a fonte própria passa na guarda.
- Erros que têm que derrubar: fonte de `identidade.json` que não existe em
  `motion/marca/fontes/` e logo `null` numa marca real -- os dois caem com a mensagem do campo.
  A guarda de glifos marca 24/24 caracteres faltando numa família inexistente e 0 na Inter.
- Receita de peça nova (`cp -r _modelo 01-teste`, `sed` de `00-exemplo` na pasta da peça,
  teste copiado, `Composition` registrada): `tsc` ok, todos os testes ok; a peça nova EXIGE áudio
  (13 x 404 no log do contato sem `public/`), o exemplo não.
- Render completo do exemplo depois do `sons.py` (sem narração): 1080x1920, 30 fps, 11,95 s,
  h264 + aac, 2m45s nesta máquina. `normalizar-audio.mjs --peca=00-exemplo`: -19,74 -> -14,37
  LUFS, pico -1,59 dBTP medidos no MP4 escrito, 1 tentativa; rodar de novo não reencoda.
