# Contrato da semente estudio-reels

O que a semente contém, o que o plantio grava num repositório e a interface de cada
ferramenta e do motor. Fonte: o plano da semente no repositório de origem, atualizado na integração (Tarefa 9, 08/10/2026) a partir do código, não do plano.
Mudou comando, pasta ou arquivo plantado: atualize esta página no mesmo commit.

### C1. Raiz da semente

`<SEMENTE>` = `~/.claude/skills/estudio-reels` (no PowerShell, `$HOME/.claude/skills/estudio-reels`).
Clone do repositório público da semente (endereço no `README.md`), feito e atualizado por
`instalar.ps1`/`instalar.sh` (`git pull --ff-only`); o `.gitignore` dela exclui
`modelo/remotion/node_modules/`, `__pycache__/`, `*.pyc` e `.pytest_cache/`.

```
estudio-reels/
  README.md             página do GitHub: o que faz, instalação em uma linha, requisitos
  instalar.ps1          instalador Windows (clone ou pull em $HOME\.claude\skills\estudio-reels)
  instalar.sh           instalador macOS/Linux (clone ou pull em ~/.claude/skills/estudio-reels)
  .gitattributes        texto sempre com fim de linha LF (o plantio compara bytes)
  SKILL.md              maestro: quem comanda (semente ou cópia), fases, travas, ciclo
  VERSAO                versão da semente (1.0.0)
  fases/                00-plantio · 01-contexto · 02-concorrencia · 03-roteiro · 04-narracao ·
                        05-tempo · 06-assets · 07-montagem · 08-conferencia · 09-publicacao ·
                        10-retrospectiva (.md)
  navegador/            chrome.md (regras comuns) · instagram.md · chatgpt.md · elevenlabs.md ·
                        referencias.md · bancos-livres.md · assistir-video.md · meta-anuncios.md
  copy/                 kishotenketsu.md (modos educativo/oferta/vsl/geral) · oferta.md ·
                        criativos-anuncio.md
  licoes.md             lições universais (IMG, NAV, VID, AUD, MET) e "Onde olhar" por fase
  modelo/
    CONTRATO.md         esta página
    plantar.py          plantio e --atualizar (só biblioteca padrão, Python >= 3.10)
    tests/              test_plantar.py
    exemplo/            identidade.json de exemplo e a peça 00-exemplo (palavras.json,
                        roteiro.txt, sons.json; tempos fabricados)
    ferramentas/        ferramentas Python (C4) + requirements.txt + tests/
    remotion/           motor (C5), com package-lock.json, sem node_modules
```

### C2. O que o plantio grava no repositório-alvo `<repo>`

`python <SEMENTE>/modelo/plantar.py <repo> --marca "<Nome>" [--semente <dir>]`; depois,
`python <SEMENTE>/modelo/plantar.py <repo> --atualizar` (comparação de três versões; conflito
vira `<arquivo>.semente-<versão>` ao lado). `<slug>`: minúsculas, `[a-z0-9-]`, sem acento,
tirado do nome da marca, com o nome da skill (`estudio-reels-<slug>`) em até 64 caracteres.

```
<repo>/.claude/skills/estudio-reels-<slug>/
  SKILL.md                 o maestro com name/description da marca (corpo igual ao da semente)
  fases/  navegador/  copy/  licoes.md
  licoes-empresa.md        só o cabeçalho: lições da marca e universais recusadas,
                           marcadas [universal recusada em AAAA-MM-DD]; nunca sobe
  SEMENTE                  versão da semente de origem, ex.: 1.0.0
<repo>/motion/
  .plantio.json            sha256 de cada arquivo plantado (base do --atualizar); gravado por último
  remotion/                cópia de modelo/remotion (sem node_modules)
  ferramentas/             cópia de modelo/ferramentas
  marca/identidade.json    de exemplo ("exemplo": true, logo null); a fase 01 substitui
  marca/fontes/.gitkeep    fontes livres da marca (fase 01); logos em marca/logo-*.png|svg|webp
  concorrencia/.gitkeep    estudo-AAAA-MM-DD.md (fase 02); videos/ só no disco, apagado no fim
  referencias/.gitkeep     descritores de referência de terceiro (fase 06)
  biblioteca/indice.json   [] ; biblioteca/categorias.json (padrão abaixo)
  biblioteca/pecas/.gitkeep   pecas/<categoria>/AAAA-MM-DD_<nome>-bN.png (só no disco)
  biblioteca/brutos/       só no disco: folhas e originais com os bytes intactos
  pecas/00-exemplo/        palavras.json, roteiro.txt, sons.json;
                           public/{fonte,colagem,sfx}/ e saida/ só no disco
```

Peça real, `motion/pecas/NN-<tema>/`: `roteiro.txt`, `roteiro-tags.txt`, `fontes.md` (fase 03);
`public/fonte/narracao.mp3` (versionada) e `narracao-tomada-{1,2,3}.mp3` (fase 04);
`palavras-whisper.json`, `palavras.json` (fase 05); `public/colagem/` (fase 06; **não existe
`public/assets/`**: recorte, produto e textura vão todos em `colagem/`); `sons.json`,
`public/sfx/` (fase 07); `saida/reel.mp4` (fase 08); `legenda-post.md` ou, no modo `oferta`,
`anuncio.md` (fase 09). Logo e fontes da marca não passam por `public/`: o motor os lê de
`motion/marca/` pelo bundler. Variação de anúncio: `motion/pecas/NN-<tema>-gK/`.

`.gitignore` do `<repo>`: o bloco abaixo, cada linha uma vez só, na ordem (as quatro de
`public/` liberam só a narração final):

```
# estudio-reels: dependências, venv, brutos, vídeos de estudo e saídas das peças
motion/remotion/node_modules/
motion/remotion/out/
motion/.venv/
motion/biblioteca/**/*.png
motion/biblioteca/brutos/
motion/pecas/*/public/*
!motion/pecas/*/public/fonte/
motion/pecas/*/public/fonte/*
!motion/pecas/*/public/fonte/narracao.mp3
motion/pecas/*/saida/
motion/concorrencia/videos/
motion/ferramentas/whisper.cpp/
motion/**/__pycache__/
motion/**/.pytest_cache/
```

`CLAUDE.md` do `<repo>`: + a seção "Reels (estudio-reels)" apontando para a cópia (criado se
não existe). Arquivo que já existe nunca é sobrescrito no plantio. O `--atualizar` só escreve
na cópia da skill, em `motion/remotion/` e em `motion/ferramentas/`, e nunca toca em
`licoes-empresa.md` nem em `motion/{marca,pecas,biblioteca,concorrencia,referencias}/`.

### C3. `motion/marca/identidade.json`

```json
{
  "marca": "Nome da Marca",
  "slug": "nome-da-marca",
  "idioma": "pt-BR",
  "cores": {"escuro": "#121417", "claro": "#F3F3F0", "profundo": "#2A3038", "acento": "#3E7BDA", "apoio": "#6B7480"},
  "fontes": {
    "manchete": {"familia": "Archivo Black", "arquivo": null, "peso": 400},
    "corpo": {"familia": "Inter", "arquivo": null, "peso": 700},
    "dado": {"familia": "IBM Plex Mono", "arquivo": null, "peso": 500}
  },
  "logo": {"sobre_claro": "logo-escura.png", "sobre_escuro": "logo-clara.png"},
  "voz": {"plataforma": "elevenlabs", "nome": null, "modelo": "v4"},
  "exemplo": false
}
```

- `arquivo: null` = a fonte padrão empacotada no motor, com família e peso exatos acima;
  fonte própria = só o nome do arquivo em `motion/marca/fontes/` (caminho é recusado).
- `logo`: nomes `logo-*.png|svg|webp` na raiz de `motion/marca/`. O exemplo plantado vem com
  `null` nos dois, `"exemplo": true` e uma `_nota`; com `"exemplo": true` o motor desenha um
  marcador de lugar no logo e a faixa "IDENTIDADE DE EXEMPLO"; com `false`, logo ausente
  derruba o render com o nome do campo.
- Validado por `src/identidade/identidade.ts`; `tests/identidade.test.ts` cobra contraste
  ≥ 4,5:1 de `claro` sobre `escuro` e sobre `profundo`.
- Papéis das cores (exemplo da origem): `preto→escuro`, `creme→claro`, `terra→profundo`,
  `acento→acento`, `verde→apoio`.

### C4. Ferramentas Python (`motion/ferramentas/`)

Rodadas **da raiz do `<repo>`**, com o Python do `motion/.venv`
(`motion/.venv/Scripts/python` no Windows, `motion/.venv/bin/python` no macOS/Linux); só o
`instalar.py` roda com o Python do sistema. Assinaturas conferidas no `--help` em 08/10/2026.

| Arquivo | Linha de comando |
|---|---|
| `instalar.py` | `instalar.py [--sem-modelos] [--plano]` — cria `motion/.venv`; instala numpy, pillow, opencv-python-headless, pytest; torch + torchaudio (índice CPU); `npm install` em `motion/remotion` (exige Node de `engines.node`, ≥ 22.12, e usa o lock); whisper.cpp 1.5.5 + `ggml-small.bin` em `motion/ferramentas/whisper.cpp/` (`main.exe`/`main`); confere o efeito no fim. `--plano`: só mostra itens, tamanhos, requisitos e espaço livre. `--sem-modelos`: pula torch, torchaudio e whisper.cpp |
| `_ffmpeg.py` | módulo: `ffmpeg()`, `ffprobe()` — o binário em `motion/remotion/node_modules/@remotion/compositor-*/` (build mínima: sem `fps`, `tile`, `ebur128`, `silenceremove`, `acrossfade`), senão o do PATH |
| `alinhar_narracao.py` | `alinhar_narracao.py <whisper.json> <roteiro.txt> <audio16k.wav> <saida.json>` — texto do roteiro + tempo do whisper; saída `palavras-whisper.json`. Exporta `por_extenso` e `NUMEROS` |
| `alinhar_forcado.py` | `alinhar_forcado.py <palavras-whisper.json> <audio> [saida.json]` — fusão whisper + CTC (torchaudio MMS_FA, ~1,26 GB no 1º uso); sem `saida`, só compara |
| `conferir_alinhamento.py` | `conferir_alinhamento.py pausas <palavras.json> <audio>` · `conferir_alinhamento.py faixa <palavras.json> <audio> <ini-fim> [<ini-fim> ...] [--com outro.json]` |
| `biblioteca.py` | `buscar <termos...>` · `listar [categoria]` · `publicar <NN-tema> <ids...>` (→ `motion/pecas/<NN-tema>/public/colagem/<nome>-bN.png` ou `<nome>.png`) · `registrar <nome> <categoria> <arquivos...> --tags a,b --origem <origem> [--bruto F] [--prompt T] [--fonte URL] [--dia AAAA-MM-DD] [--nota T] [--substituir]` |
| `recortar_folha.py` | `recortar_folha.py <folha> --nomes a,b,c --categoria C --tags t1,t2 [--prompt "..."] [--origem gerado-chatgpt\|real-verificada\|real-nao-verificada] [--limiar 22] [--juntar 24] [--area-min 2500] [--convexo a,b] [--lente a] [--filete 9] [--reticula] [--dia AAAA-MM-DD] [--substituir]` — `--prompt` obrigatório com `gerado-chatgpt` (o padrão); guarda a folha em `brutos/` |
| `foto_papel.py` | `foto_papel.py <foto> <nome> --tags a,b --origem real-verificada\|real-nao-verificada\|banco-livre [--categoria foto-real] [--fonte URL] [--largura 900] [--recorte x0,y0,x1,y1] [--dia AAAA-MM-DD] [--substituir]` — `--fonte` obrigatória com `banco-livre`; `--recorte` em frações da foto já girada pelo EXIF |
| `sons.py` | `sons.py motion/pecas/<NN-tema>` — lê `sons.json` e `palavras.json`; grava `public/sfx/*.wav` e `trilha.wav` |
| `varrer_movimento.py` | `varrer_movimento.py <video.mp4> [q1,q2,...]` — quadros das trocas conhecidas |
| `folha_do_video.py` | `folha_do_video.py <video.mp4> <saida.png> <q1,q2,...> [colunas]` — quadros, não segundos; 10 colunas por padrão |

Origens (`biblioteca.py registrar --origem`): `gerado-chatgpt` (exige `--prompt`),
`real-verificada`, `real-nao-verificada`, `banco-livre` (exige `--fonte`), `codigo`. Categoria
`produto` com origem `gerado-chatgpt` é recusada. Terceiro (Pinterest, Google, outro perfil)
não tem origem: nunca entra na biblioteca. Categorias: as de `motion/biblioteca/categorias.json`
(lista ou `{nome: descrição}`), plantado com `objeto`, `utensilio`, `natureza`, `alimento`,
`produto`, `foto-real`, `textura`, `papelaria`, `grafismo`, `maos`. Id da peça:
`<AAAA-MM-DD>_<nome>`; `registrar` recusa id repetido sem `--substituir`.

`motion/pecas/<NN-tema>/sons.json`:

```json
{"bpm": 88, "secoes": [
  {"frase": "Calma", "tipo": "groove"},
  {"frase": "E aqui vem", "tipo": "respiro"},
  {"frase": "Por isso a gente", "tipo": "groove"},
  {"frase": "Salva esse vídeo", "tipo": "fecho"}
]}
```

Antes da primeira seção é sempre a tensão (trilha muda; `drone` e `batimento`). `fecho` só na
última. `DUR` = fim da última palavra + 0,5 s, arredondado para cima ao décimo (= `FIM` do motor).

Nenhuma ferramenta chama API nem pede chave. Vídeo de terceiro se estuda com a skill `watch`
só com `--engine local --no-whisper` (nunca o motor Gemini) e a fala pelo whisper.cpp acima
(`navegador/assistir-video.md`).

### C5. Motor Remotion (`motion/remotion/`)

Node ≥ 22.12 (`engines.node`), `npm install` com o `package-lock.json` (obrigatório; sem ele o
npm 10 quebra). Todos os `@remotion/*` em 4.0.530, React 19, TypeScript 7, vitest 5, pngjs.
Comandos de `motion/remotion/`, em subshell `(cd motion/remotion && ...)`.

| Caminho | Papel |
|---|---|
| `src/index.ts` · `src/Raiz.tsx` | registra `Exemplo` (1080×1920, 30 fps, a peça modelo envolta em `<SomTolerante>`, a única que tolera áudio ausente) e `Marca` (conferência da identidade, 1 quadro) |
| `src/Marca.tsx` | cores, as famílias com os acentos do idioma, logos sobre claro e escuro, pílula nos dois fundos; faixa "IDENTIDADE DE EXEMPLO" enquanto `"exemplo": true` |
| `src/identidade/` | `identidade.ts` (formato e validação do C3), `tokens.ts` (`IDENTIDADE`, `COR`, `TIPO`, `AUDIO`), `tipografia.ts` + `guarda-fonte.ts` (carrega e prova as 3 famílias, glifos do idioma; reprovou = `cancelRender`), `arquivos-marca.ts` (`urlDaMarca`: logos e fontes de `motion/marca/` no bundle), `cor.ts` (`contraste`, `tintaPara`…), `fontes/` (Archivo Black, Inter Bold, IBM Plex Mono Medium, OFL) |
| `src/audio/` | `alvo.ts` (−14 LUFS / −1 dBTP) e `normalizar.ts` (teto pedido 0,6 dB abaixo do verificado, novas tentativas pelo excesso medido, mede o MP4 escrito) |
| `src/colagem/` | `camera.ts` (`cameraCena`, `cameraEm`, `deriva`, `pulso`, `tremor`, `transformarPlano`), `palco.tsx` (`Palco`, `Plano`), `chicote.ts`, `legenda.ts` (`Roteiro` com `b`/`mudo`/`t`/`em`/`depois`, `blocosA`), `tipos.tsx` (`Dymo`, `Serifa`, `Marcador`, `Recortadas`, `Pilula` com `formato`), `grafismos.tsx`, `pecas.tsx` (`Recorte`, `Troca`, `Fita`, `Tachinha`, `Carimbo`, `Manchete`, `Rotulo`, `Tira`, `ProdutoRecortado`, `LogoMarca`), `atmosfera.tsx` (`Fundo`, `GraoFilme`, `Vinheta`, `Foco`, `Sombra`, `Cobertura`, `Divisoria`, `Rodape`), `area-segura.ts` (`AREA_SEGURA.organico` x 140–940 / y 96–1613, pílula em 1500; `AREA_SEGURA.anuncio` x 65–1015 / y 269–1248; `yDaPilula`), `sons.ts`, `som-tolerante.tsx`, `movimento-colagem.ts`, `semente.ts`, `papel.ts`, `fontes-colagem.ts` + `fontes/` (Instrument Serif, Permanent Marker, OFL) |
| `src/pecas/_modelo/` | o esqueleto: `roteiro.ts` (importa `motion/pecas/00-exemplo/palavras.json`; `S1..S3`, `CENA_INICIO`, `TROCA`, `FIM` derivado), `apoio.tsx` (`FPS`, `fq`, `fala` e reexporta o kit), `cenas.tsx` (3 cenas), `Peca.tsx` (`CHICOTES` colados, pílula, grão, `DURACAO`), `Sons.tsx` (`EFEITOS`) |
| `scripts/contato.mjs` | `node scripts/contato.mjs <Comp> <NN-tema> [s1,s2,...\|-] [--escala=0.25] [--cols=8] [--saida=nome.png]` — instantes em segundos; public dir = `../pecas/<NN-tema>/public`; stills em `saida/stills/` |
| `scripts/normalizar-audio.mjs` | `node scripts/normalizar-audio.mjs --peca=<NN-tema>` ou `--arquivo=<mp4> [--medir]` |
| `tests/` | `chicote`, `colagem-camera-legenda`, `colagem-movimento`, `identidade`, `legenda-limites` (inclui a pílula do anúncio acima de y 1248), `modelo-roteiro` (portão de A/B e `FIM`) e `modelo-tempos` (portão "nenhum segundo digitado") |

```bash
npx tsc --noEmit
npx vitest run
npx remotion still src/index.ts Exemplo ../pecas/00-exemplo/saida/exemplo.png --frame=60 --public-dir=../pecas/00-exemplo/public
npx remotion still src/index.ts Marca ../pecas/00-exemplo/saida/marca.png --public-dir=../pecas/00-exemplo/public
npx remotion render src/index.ts <Comp> ../pecas/<NN-tema>/saida/reel.mp4 --public-dir=../pecas/<NN-tema>/public
```

Peça nova (fase 07): copiar `src/pecas/_modelo/` → `src/pecas/<NN-tema>/` e trocar
`00-exemplo` pelo `<NN-tema>` no import do `roteiro.ts`; copiar `tests/modelo-roteiro.test.ts`
→ `tests/<NN-tema>-roteiro.test.ts` (import e `FIM`) e `tests/modelo-tempos.test.ts` →
`tests/<NN-tema>-tempos.test.ts` (`'_modelo'` → `'<NN-tema>'` em `PASTA`); registrar em `Raiz.tsx` com id
`P<NN>-<tema>` (anúncio: `P<NN>-<tema>-g<K>-<angulo>`) e `component={P.Peca}` direto, sem
`<SomTolerante>`. No Windows, repositório em caminho curto: o `chrome-headless-shell` falha
acima de 260 caracteres. O 1º still ou render baixa o Chrome Headless Shell (~113 MB).

### C6. Regras para quem mexe na semente

- Português do Brasil em docs, comentários e mensagens; nomes de arquivos sem acento.
- Nada específico de uma marca fica na semente (fatos de produto, nomes de SKU, @ de
  concorrentes, caminhos de outro repositório), exceto quando citado como **exemplo** marcado.
- Nenhum caminho absoluto de máquina, nome de usuário, e-mail ou chave em arquivo nenhum: a
  semente é publicável.
- Semente só muda pela promoção da fase 10, com OK do usuário, versão nova, commit e tag.
- Mudou `modelo/`: plante numa pasta temporária curta e rode a conferência da fase 10, passo 9.
