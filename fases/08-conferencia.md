# Fase 08 — Conferência

Mede o arquivo que vai ao ar (imagem, tempo e som) com testes, folhas e scripts. Portão é
necessário, não suficiente: script não vê composição, e o olho não vê 0,1 s de dessincronia.

## Quando

- Depois da montagem (fase 07), e de novo depois de **qualquer** correção (palavras, cena,
  câmera, som): volte ao passo 1. Todo render refeito sai com o áudio cru: o passo 6 também.

## Entradas

- `<Comp>` registrada em `Raiz.tsx`, `motion/remotion/src/pecas/<NN-tema>/` e o teste de roteiro da peça (fase 07)
- em `motion/pecas/<NN-tema>/`: `palavras.json`, `palavras-whisper.json` e `public/` completa
  (`fonte/narracao.mp3`, `colagem/`, `sfx/`)

Onde rodar: `python motion/ferramentas/...` **da raiz**, com o Python do `motion/.venv` (fase 00);
`npx`/`node` **em subshell**, `(cd motion/remotion && …)`, porque o `cwd` do Bash da sessão persiste.
No PowerShell 5.1 não existe `&&`; a forma é explícita, por exemplo
`Push-Location motion/remotion; npx tsc --noEmit; if ($?) { npx vitest run }; Pop-Location`. Motor 1080×1920 a 30 fps:
varredura e folha em **quadros**; `contato.mjs` e `conferir_alinhamento faixa` em **segundos** (trocar dá folha errada, calada).

## Passos

| # | O quê | Prova de que passou |
|---|---|---|
| 1 | tipos e testes | `tsc` limpo e `vitest` verde, com o teste de roteiro da peça |
| 2 | alinhamento | todo `<<<` do `pausas` lido no `faixa` e explicado |
| 3 | stills dirigidos | cada célula da folha olhada, ampliada |
| 4 | render de teste + `varrer_movimento` | `0 salto(s)` isolados; o usuário já viu o vídeo |
| 5 | render final | só depois de corrigir tudo o que o teste mostrou |
| 6 | normalizar | −14 ±0,5 LUFS e pico ≤ −0,7 dBTP (teto −1 + folga 0,3) no MP4; se `dynamic`, ouvido |
| 7 | `folha_do_video` + ffprobe | chicotes limpos no arquivo final; 1080×1920, 30 fps, duração = `FIM` |
| 8 | entrega cedo e limpeza | usuário com o vídeo; só `reel.mp4` em `saida/`; commit |

### 1. Tipos e testes

```bash
(cd motion/remotion && npx tsc --noEmit && npx vitest run)
```

O teste de roteiro é o portão de A/B (nada em A e B juntos, toda palavra em A, B ou mudo, pílula
no limite, `FIM` derivado). Faça-o imprimir os quadros das trocas, que os passos 3, 4 e 7 usam:
`[...CENA_INICIO.slice(1), ...Object.values(TROCA)].map((s) => Math.round(s * 30))` (nomes do `roteiro.ts`).

### 2. Alinhamento

```bash
python motion/ferramentas/conferir_alinhamento.py pausas motion/pecas/<NN-tema>/palavras.json motion/pecas/<NN-tema>/public/fonte/narracao.mp3
python motion/ferramentas/conferir_alinhamento.py faixa motion/pecas/<NN-tema>/palavras.json motion/pecas/<NN-tema>/public/fonte/narracao.mp3 <ini>-<fim> --com motion/pecas/<NN-tema>/palavras-whisper.json
```

Todo `<<<` se lê no `faixa` (ex.: `23.1-25.3`), contra o arquivo que o render toca; régua da
fusão: mediana ~0,02 s, máximo ~0,15 s. Narração mudou depois da fase 05? Volte à fase 05.

### 3. Stills dirigidos

```bash
(cd motion/remotion && node scripts/contato.mjs <Comp> <NN-tema> <s1,s2,...> --saida=stills-1.png)
```

Os instantes vêm do risco: colagem que entra em 4,23 s pede `4.17,4.20,4.23`; troca no quadro
`q`, os segundos `(q − 2)/30` e `(q + 1)/30`. Olhe cada célula ampliada (caminho na linha `folha:`).

| Onde | Instantes | O que procurar |
|---|---|---|
| palavra que vira colagem (B) | o quadro em que ela entra e os 2 antes | a pílula já saiu? a colagem entra com a voz? |
| marcador | o fim de cada frase escrita | terminou junto com a fala, não depois |
| movimento de câmera | o meio e o fim de cada movimento | texto em x ≈ 140–940, fora dos 5% do topo e dos 16% da base |
| chicote | dois quadros DENTRO da janela | as duas imagens coladas, nenhuma faixa de fundo |
| recorte de produto ou logo | onde há texto perto dele | texto nunca sobre logo nem selo |
| anúncio (modo `oferta`) | o meio e o fim de cada movimento, com a área desenhada (comando em `copy/criativos-anuncio.md`) | nada toca a moldura magenta |

### 4. Render de teste e varredura

```bash
(cd motion/remotion && npx remotion render src/index.ts <Comp> ../pecas/<NN-tema>/saida/teste.mp4 --public-dir=../pecas/<NN-tema>/public)
```

- Render **sempre em segundo plano** (no Claude Code, `run_in_background`): ~12–16 min por
  80 s numa máquina comum; rascunhe a descrição (fase 09) enquanto isso, sem `sleep` em laço.
  Antes, confira `public/`: arquivo ausente só aparece no meio do render, como 404, e mata a rodada.
- **Mostre o vídeo ao usuário assim que existir**, com defeito e a lista do que ainda muda:
  ele julga pelo vídeo, e a sincronia voz × legenda × movimento é o que ele vê primeiro.
- Varredura, da raiz:
  `python motion/ferramentas/varrer_movimento.py motion/pecas/<NN-tema>/saida/teste.mp4 <quadros das trocas>`.
  "Saltos de câmera isolados" (câmera anda muito num quadro, vizinhos parados) **tem que sair
  `0 salto(s)`**; salto é chave sem transição ou troca sem chicote nem cobertura. Os "picos de
  MAD" incluem movimento rápido intencional: confira cada um no vídeo.
- Passe como conhecidas só as trocas reais (chicotes, coberturas, batidas com tremor): a
  varredura ignora ±7 quadros em volta de cada uma, e quadro conhecido demais esconde defeito.

### 5. Render final

Só depois de corrigir o que o teste mostrou; a correção se confere num trecho (o comando do
passo 4 com `--frames=600-780` e saída `trecho.mp4`). Mexeu em câmera ou troca? Varra de novo.

```bash
(cd motion/remotion && npx remotion render src/index.ts <Comp> ../pecas/<NN-tema>/saida/reel.mp4 --public-dir=../pecas/<NN-tema>/public)
```

Modo `oferta`: render 1440×2560 com escala derivada (`VID-3`) em `saida/anuncio.mp4`; o ffprobe
tem que dar `h264` 1440×2560 e `aac` estéreo (comandos em `copy/criativos-anuncio.md`).

### 6. Normalizar o áudio

```bash
(cd motion/remotion && node scripts/normalizar-audio.mjs --arquivo=../pecas/<NN-tema>/saida/reel.mp4)
```

- Critério do script: −14 ±0,5 LUFS e pico real ≤ −0,7 dBTP no MP4 (o teto de −1 dBTP mais
  **a folga de 0,3 dB**, `FOLGA_PICO_DB`). Já nessa faixa, ele não reencoda: sai só a linha
  `antes` ("já estava no alvo"), e a medida é ela; senão, vale a `depois`, do MP4 escrito.
- A margem de pico do AAC já é dele: pede ao `loudnorm` um teto 0,6 dB abaixo e, se o MP4
  passar, refaz do mesmo PCM com a margem aumentada pelo excesso medido, até 3 tentativas; é
  determinístico, rodar de novo não muda nada. Só a `FALHA` "passou do teto de pico … depois de
  3 tentativas" quer dizer mixagem quente (efeitos empilhados): baixe o volume dos efeitos no
  `Sons.tsx` da peça, renderize e normalize de novo, sem afrouxar a folga. Outra `FALHA`
  (arquivo ausente, erro de LUFS, ffmpeg) se lê pela mensagem. O vídeo é copiado sem reencode.
- `modo loudnorm: dynamic` (aviso `ATENÇÃO`) = houve limitação: **ouça** a peça, nos impactos.

### 7. O arquivo que vai ao ar

```bash
python motion/ferramentas/folha_do_video.py motion/pecas/<NN-tema>/saida/reel.mp4 motion/pecas/<NN-tema>/saida/folha-final.png 15,<q-2>,<q+1>,...,<ultimo>
python -c "import subprocess,sys; sys.path.insert(0,'motion/ferramentas'); from _ffmpeg import ffprobe; subprocess.run([ffprobe(),'-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,duration,nb_frames','-of','compact',sys.argv[1]])" motion/pecas/<NN-tema>/saida/reel.mp4
```

- Na folha: `q−2` e `q+1` de cada troca; o 15, o gancho a 0,5 s, que tem que fazer sentido
  parado e sem som; e o último, `FIM` × 30 − 1 (o loop emenda nele o primeiro). O `contato.mjs`
  desenha antes do encode; esta folha lê o arquivo final, e é a que prova o chicote.
- No ffprobe: `h264` 1080×1920, `r_frame_rate=30/1`, `nb_frames` = `FIM` × 30; o `aac` pode passar
  ~0,1 s do vídeo (medido na peça de origem: vídeo 79,000 s e 2370 quadros, áudio 79,1 s).

### 8. Entrega cedo e limpeza

- O primeiro vídeo foi ao usuário no passo 4; aqui vai o final, com os números dos passos 6
  e 7, no player (`Invoke-Item` no Windows, `open` no macOS, `xdg-open` no Linux) ou pelo caminho.
- Em `saida/` fica só `reel.mp4` (e `anuncio.mp4`, no modo `oferta`): apague `teste.mp4`,
  `trecho*.mp4`, `stills/`, as folhas e os intermediários da fase 05 (`n16k.wav`, `whisper.json`).
- Commit só dos seus arquivos, por caminho, nunca `git add -A`: `motion/remotion/src/pecas/<NN-tema>/`,
  `Raiz.tsx`, o teste da peça, o não ignorado de `motion/pecas/<NN-tema>/` e `motion/biblioteca/indice.json`.

## Abortar um render

Parar a tarefa de segundo plano encerra o shell, não o render: `node` e `chrome-headless-shell` seguem
(CPU cheia, "arquivo em uso" no render seguinte). Ache a árvore pela linha de comando, que cita a composição,
derrube-a inteira e confira que nada sobrou. Nunca mate `chrome-headless-shell` às cegas: outra sessão pode estar renderizando.

```powershell
# Windows (PowerShell). No Git Bash, /PID vira caminho: taskkill //PID <pid> //T //F
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'remotion' -and $_.CommandLine -match '<Comp>' } | Select-Object ProcessId, ParentProcessId, CommandLine
taskkill /PID <pid> /T /F
```

macOS e Linux: PID por `pgrep -af <Comp>` (Linux) ou `pgrep -lf <Comp>` (macOS); grupo por
`ps -o pgid= -p <pid>`; confira que o grupo só tem este render
(`ps -eo pid,pgid,command | awk '$2 == <pgid>'`) e derrube-o: `kill -TERM -- -<pgid>`. `pkill -P`
pegaria só o filho direto; grupo com mais coisa, desça pelos filhos (`pgrep -P <pid>`).

## Saídas

- `motion/pecas/<NN-tema>/saida/reel.mp4` (1080×1920, 30 fps, −14 ±0,5 LUFS, pico ≤ −0,7 dBTP) e o commit da peça
- modo `oferta`: também `saida/anuncio.mp4` (1440×2560), por variação `NN-tema-gK`

## Pronto quando

As oito provas da tabela de Passos valem para a versão **final** da peça, não para o teste:
o que mudou depois do teste se confere de novo no `reel.mp4`.

## Erros comuns

- **`--public-dir` esquecido ou de outra peça.** Sem ele o render procura em `motion/remotion/public/`
  e morre no primeiro 404; com o de outra peça, sai com os arquivos do vizinho.

## Sinais de que você está saindo do padrão

| Pensamento | Realidade |
|---|---|
| "O whisper já deu os tempos" | Na peça de origem ele deslizou 0,7 s sem cair em pausa. Fusão com o CTC e conferência no envelope. |
| "A diferença é 0,1 s, ninguém vê" | Na peça de origem, foi exatamente o que o cliente viu e chamou de dessincronia. |
| "O still antes e depois do chicote está bom" | O defeito (faixa de fundo) só aparece DENTRO da janela. |
| "Saiu com exit 0, então está certo" | Render esticado em silêncio e parâmetro ignorado também saem com exit 0. Confira o efeito no arquivo. |
| "Reaproveito os tempos da narração anterior" | Áudio acelerado ou regravado = alinhar de novo no arquivo final. |
| "O still já mostrou, pulo o render de teste" | Still não mostra salto de câmera nem dessincronia; o vídeo e a varredura mostram. |
