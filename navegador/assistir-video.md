# Assistir vídeo de referência

Como estudar um vídeo que não é nosso — reel de concorrente (Instagram, TikTok), referência no
YouTube (VSL, anúncio, aula) ou arquivo local. Serve à fase 02 e às referências de copy (fase 03,
quando o modo pedir). Regras comuns em `chrome.md`. O que não traz marca foi conferido nesta
máquina ou no código da `watch` (out/2026); *(a validar no piloto)* = rota não testada de ponta a
ponta.

Quem lê a estrutura (gancho, tempos, cortes, sistemas de texto) é você, nos quadros e na
transcrição; `varrer_movimento.py` mede os cortes. Nenhum serviço externo assiste por você.

## Travas

- Vídeo de terceiro baixado fica em `motion/concorrencia/videos/` (fora do git) e é **apagado
  depois do estudo**. Nunca vira pixel do nosso vídeo; nunca sobe ao ChatGPT nem a outro serviço.
- Volume baixo: no máximo 3 reels por perfil (`instagram.md`).
- Referência de copy (VSL, anúncio) serve para destrinchar a estrutura: resuma blocos, tempos e
  viradas; não transcreva o texto inteiro para dentro da peça.

`<id>` = `<perfil>_<shortcode>` (Instagram) ou `<canal>_<id-do-video>` (YouTube, TikTok).

## 1. Quadros pela skill `watch`, se instalada

Ela aparece na lista de skills da sessão. Confira o estado antes de usar:

```bash
python "<pasta-da-watch>/scripts/setup.py" --json
```

Leia `engine`, `missing_binaries`, `whisper_backend` e `has_api_key`. A semente usa **sempre**
`--engine local --no-whisper`, mesmo que haja chave no ambiente, no config da `watch` ou no
`.env` do repositório: se o `--json` mostrar `engine: gemini`, o `--engine local` da chamada
resolve. A fala vem do whisper.cpp da semente (§4). Nunca rode o assistente de primeira execução
da `watch`, nunca peça nem cole chave. Binário faltando: diga ao usuário o que falta.
Cookies (`--cookies-from-browser` ou `WATCH_COOKIES_FROM_BROWSER`) só com OK na hora (§3).

Os ~10 quadros da fase 02: 0,5/1/2/3/5 s mais 4–5 no resto (meio, virada, CTA, fim), da duração
`D` (o `video.duration` do reel ou `ffprobe` no arquivo) — 40%, 60%, 80% e `D − 0,5`:

```bash
D=<duração em s>
T=$(python -c "import sys; d=float(sys.argv[1]); print(','.join(f'{t:.1f}' for t in sorted({0.5,1,2,3,5,round(.4*d,1),round(.6*d,1),round(.8*d,1),round(d-.5,1)}) if 0<t<d))" "$D")
python "<pasta-da-watch>/scripts/watch.py" "<URL ou arquivo>" --engine local --no-whisper \
  --detail transcript --timestamps "$T" --out-dir "motion/concorrencia/videos/<id>"
```

Com `--detail transcript`, os quadros de `--timestamps` são os únicos (ajuda da própria opção).
Pela URL, a `watch` baixa no máximo 720 px de altura e não amplia: no reel vertical o quadro sai
com ~405 px de largura, e `--resolution` maior não muda isso. YouTube e TikTok vão pela URL; o
Instagram exige sessão (§3).

## 2. yt-dlp fora do PATH

A `watch` acha o yt-dlp por `shutil.which('yt-dlp')`. Instalado por pip, ele pode ficar fora do
PATH — medido: `%APPDATA%\Python\Python312\Scripts\yt-dlp.exe`, com `python -m yt_dlp --version`
respondendo. Ajuste o PATH **só na chamada**; nunca mexa no PATH do sistema:

```bash
S="$(python -c "import os, sysconfig; print(sysconfig.get_path('scripts', 'nt_user' if os.name == 'nt' else 'posix_user'))")"
PATH="$S:$PATH" python "<pasta-da-watch>/scripts/watch.py" "<URL>" --engine local --no-whisper ...
```

PowerShell, na mesma linha: `$env:PATH = "<pasta>;" + $env:PATH; python "<pasta-da-watch>\scripts\watch.py" ...`
Medido: sem o ajuste, o `setup.py --json` acusa `missing_binaries: ["yt-dlp"]`; com ele, `[]`.

## 3. Instagram exige sessão — duas rotas *(a validar no piloto)*

**(a) Pela sessão do Chrome**, sem levar cookie para fora do navegador:
1. Abra o reel numa aba nova e deixe tocar, mudo (`instagram.md`, passo 5).
2. `read_network_requests` filtrando `.mp4`: pegue a URL do **maior** arquivo e tire os
   parâmetros `bytestart`/`byteend`, se houver.
3. `fetch` dessa URL na própria página e salve como blob com nome escolhido (receita do
   `chatgpt.md`, passo 9, com a URL no lugar do `img.src`); mova para
   `motion/concorrencia/videos/<id>.mp4` (`chrome.md` §4).
4. Confira com `ffprobe` que há trilha de áudio: imagem e som podem vir em arquivos separados, e
   o maior costuma ser só imagem. Sem áudio, baixe também o `.mp4` de áudio e transcreva-o.

**(b) `yt-dlp --cookies-from-browser chrome`** (ou o mesmo na `watch`): só com OK do usuário
**naquela hora**, porque usa a conta dele. No Windows, o Chrome recente pode impedir a leitura
dos cookies: falhou → rota (a); não procure contorno.

## 4. Depois de baixado

- **Onde está o vídeo.** Pela `watch` na URL: numa subpasta `watch-*` de
  `motion/concorrencia/videos/<id>/` — o caminho exato é a linha "Local media" do relatório. Pela
  rota (a) do §3: `motion/concorrencia/videos/<id>.mp4`.
- **Fala**: whisper.cpp da semente, sem `-ml 1 -sow` (aqui não há roteiro para casar; vale o
  texto). `FF`, `WB` e `MOD` como no passo 1 da fase 05:
  ```bash
  WD=motion/ferramentas/whisper.cpp
  V="<caminho do vídeo, sem o .mp4>"   # o "Local media" da watch, ou motion/concorrencia/videos/<id>
  "$FF" -y -v error -i "$V.mp4" -ar 16000 -ac 1 -c:a pcm_s16le "$V.wav"
  "$WB" -m "$MOD" -f "$V.wav" -l <idioma do vídeo> -otxt -oj -of "$V"
  ```
- **Cortes**: `python motion/ferramentas/varrer_movimento.py "$V.mp4"` lista os picos de
  diferença entre quadros; confira três no quadro antes de contar e dividir pela duração.
- **Sem `watch`**: quadros pelo Chrome (`instagram.md`, passo 7: `currentTime` + screenshot, no
  máximo 10 por vídeo, janela visível) e fala pelo whisper.cpp no arquivo baixado. Sem arquivo,
  não há transcrição: registre só o texto que aparece na tela e anote a falta.

## 5. Fim do estudo

Apague `motion/concorrencia/videos/<id>*` (vídeo, quadros, WAV, TXT, JSON). No repositório fica
só o texto do estudo, com link e data (`motion/concorrencia/estudo-<AAAA-MM-DD>.md`).
