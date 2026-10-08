# Criativo de anúncio vertical (Reels pago)

O anúncio do modo `oferta` (e a VSL que vira anúncio), do formato ao pacote da fase 09, no motor
de colagem. A skill **prepara**; subir, impulsionar e gastar verba é do usuário.

## Quando ler

Modo `oferta`, e `vsl` quando vira anúncio: fases 03 (abertura, ganchos), 04 (corpo uma vez, ganchos à parte),
05 (junção), 07 (área segura, cartão, edição cinética), 08 (stills, render 1440×2560), 09 (`anuncio.md`), 10 (métricas).

## Formato

| Item | Valor | Fonte |
|---|---|---|
| proporção | 9:16; o 4:5 de feed fica para a v2 | [Guia de Anúncios da Meta, Reels](https://www.facebook.com/business/ads-guide/update/video/instagram-reels), lido em 08/10/2026 |
| resolução | 1440×2560 recomendado; largura mínima 250 px (< 30 s) ou 500 px | idem |
| arquivo | MP4 ou MOV, H.264, AAC estéreo ≥ 128 kbps | idem |
| duração | técnica até 15 min; a que rende, 15–30 s, com teto de 60 s no modo `oferta` | idem · *(prática de mercado)*: [cinerads](https://www.cinerads.com/blog/meta-ads-video-creative-best-practices) |
| texto principal | 44 caracteres recomendados (vai no `anuncio.md`) | idem |

## Área segura de anúncio

A Meta pede **14% do topo, 35% da base e 6% de cada lado** livres de texto, logo e elemento importante ([Guia de Anúncios](https://www.facebook.com/business/ads-guide/update/video/instagram-reels)).
O motor desenha em 1080×1920 e o render só amplia, então a conta é em 1080×1920:

| | Orgânico (fase 07) | Anúncio |
|---|---|---|
| vertical | fora de y < 96 e y > 1613 (5% e 16%) | **y 269–1248** |
| horizontal | x ≈ 140–940 em repouso (margem da câmera) | **x 65–1015** no quadro final |
| pílula (A) | `y = 1500` | inteira acima de 1248: centro em `y ≤ 1210` (a pílula tem ~76 px) |
| no motor | `AREA_SEGURA.organico` | `AREA_SEGURA.anuncio`: a pílula lê daqui, e um teste a exige acima de y 1248 |

A área vale no **quadro final**, com a câmera andando: o ponto (X, Y) da cena (plano 1) vai para
(540 + z·(X − 540 − cx), 960 + z·(Y − 960 − cy)), sem a rotação (`transformarPlano`, `src/colagem/camera.ts`).
Duas opções *(cálculo; confira no still)*: **câmera do esqueleto** (zoom 1,10–1,15, até ~90 px;
`VID-9`: ~1,16×, ~120 px) → texto em repouso em **x ≈ 224–856, y ≈ 460–1116**; ou **teto de câmera
para anúncio** (zoom total ≤ 1,08 com chaves + pulso + tremor, deslocamento ≤ 60 px) → **x 160–920,
y 380–1166**. No still do meio e do fim de cada movimento, com a área desenhada, nada toca a moldura.

```bash
(cd motion/remotion && npx remotion still src/index.ts <Comp> ../pecas/<NN-tema-gK>/saida/q<q>.png --frame=<q> --public-dir=../pecas/<NN-tema-gK>/public)
python -c "import sys; from PIL import Image, ImageDraw; im = Image.open(sys.argv[1]).convert('RGB'); k = im.width / 1080; ImageDraw.Draw(im).rectangle([65 * k, 269 * k, 1015 * k, 1248 * k], outline=(255, 0, 255), width=round(4 * k)); im.save(sys.argv[1][:-4] + '-area.png')" motion/pecas/<NN-tema-gK>/saida/q<q>.png
```

## Abertura de 3 s

| Até | O quadro | No motor |
|---|---|---|
| 0,5 s | imagem do produto, da dor ou do resultado, que se sustenta parada e sem som | produto pelo recorte real (fase 06), em cena no quadro 0; a voz começa no 0 s (a junção apara o silêncio) |
| 1,5 s | a promessa **escrita** | colagem B (`Manchete`, `Dymo`) na fonte de manchete da marca |
| 3 s | prova, demonstração ou contraste | dado com fonte, produto em uso, antes e depois só onde é permitido (`copy/oferta.md`) |

**Legenda sempre queimada** (muita gente assiste sem som): toda palavra dita está na tela, na
pílula (A) ou na colagem (B); `mudo` só quando a colagem diz o mesmo com outras palavras ([adriselab](https://adriselab.com/learn/hook-rate) · [vaizle](https://insights.vaizle.com/hook-rate-hold-rate/), *prática de mercado*).

## 3 a 5 ganchos sobre o mesmo corpo

Teste varia **um** elemento: várias aberturas sobre um corpo idêntico; conceito novo vale mais que
retoque, e conta pequena aguenta 2–4 conceitos por semana ([evolut](https://evolutagency.com/meta-creative-testing-in-2026-the-andromeda-era/) · [flighted](https://www.flighted.co/blog/7-meta-ads-creative-strategies-that-work), *prática de mercado*). O corpo é narrado **uma vez**: regerado por variação, muda a entonação e o teste mede duas coisas.

1. **Fase 03**, na pasta base `motion/pecas/NN-tema/`: `roteiro-corpo.txt` e `roteiro-corpo-tags.txt`
   (começando pela própria tag) e, por gancho, `gancho-K.txt` e `gancho-K-tags.txt` (K = 1…5;
   ângulos distintos, das Big Ideas ou dos esqueletos de `copy/kishotenketsu.md`; ~8 palavras, até
   3 s). O corpo não depende do gancho (nada de "isso", "como eu disse"). Monte as variações e
   rode nelas o passo 10 da fase 03:

   ```bash
   P=motion/pecas/NN-tema; for K in 1 2 3; do V=motion/pecas/NN-tema-g$K; mkdir -p $V; { cat $P/gancho-$K.txt; echo; cat $P/roteiro-corpo.txt; } > $V/roteiro.txt; { cat $P/gancho-$K-tags.txt; echo; cat $P/roteiro-corpo-tags.txt; } > $V/roteiro-tags.txt; done
   ```

2. **Fase 04** para o corpo e para cada gancho, com o texto da parte no lugar do `roteiro.txt` (3
   tomadas, mesma voz, modelo e ajustes): `$P/public/fonte/corpo.mp3` e `gancho-K.mp3`.
3. **Junção** com o ffmpeg do motor (a build do Remotion tem `concat`, `atrim`, `apad` e
   `silencedetect`; **não** tem `silenceremove` nem `acrossfade`, medido em 08/10/2026). O script
   apara as pontas do gancho e o início do corpo (< −50 dB, a régua da fase 05) e deixa
   ~0,23 s na emenda (testado em áudio sintético; `WinError 206` = caminho do ffmpeg > 260
   caracteres). Copie o bloco como está, com `EOF` na coluna 0:

```bash
P=motion/pecas/NN-tema; K=1; V=motion/pecas/NN-tema-g$K; mkdir -p $V/public/fonte
python - $P/public/fonte/gancho-$K.mp3 $P/public/fonte/corpo.mp3 $V/public/fonte/narracao.mp3 <<'EOF'
import re, subprocess as sp, sys; sys.path.insert(0, "motion/ferramentas"); from _ffmpeg import ffmpeg, ffprobe
RESPIRO = 0.10  # silêncio acrescentado na emenda (s)
def fala(arq):  # (início, fim, duração) da fala, sem o silêncio < -50 dB das pontas
    dur = float(sp.run([ffprobe(), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq], capture_output=True, text=True).stdout)
    log = sp.run([ffmpeg(), "-hide_banner", "-i", arq, "-af", "silencedetect=noise=-50dB:d=0.05", "-f", "null", "-"], capture_output=True, text=True, errors="replace").stderr
    ini, fim = ([float(x) for x in re.findall(rf"silence_{k}: (-?[\d.]+)", log)] for k in ("start", "end"))
    a = fim[0] if ini and fim and ini[0] < 0.05 else 0.0
    b = ini[-1] if ini and (len(fim) < len(ini) or fim[-1] >= dur - 0.05) else dur
    return max(0.0, a - 0.05), min(dur, b + 0.08), dur
g, c = fala(sys.argv[1]), fala(sys.argv[2])
fmt = "asetpts=PTS-STARTPTS,aresample=44100,aformat=sample_fmts=fltp:channel_layouts=mono"
filtro = f"[0:a]atrim={g[0]:.3f}:{g[1]:.3f},{fmt},apad=pad_dur={RESPIRO}[g];[1:a]atrim=start={c[0]:.3f},{fmt}[c];[g][c]concat=n=2:v=0:a=1[a]"
sp.run([ffmpeg(), "-y", "-v", "error", "-i", sys.argv[1], "-i", sys.argv[2], "-filter_complex", filtro, "-map", "[a]", "-c:a", "libmp3lame", "-q:a", "2", sys.argv[3]], check=True)
print(f"gancho: fala {g[0]:.2f}-{g[1]:.2f} de {g[2]:.2f} s | corpo: desde {c[0]:.2f} de {c[2]:.2f} s | emenda ~{RESPIRO + 0.13:.2f} s")
EOF
```

4. **Fase 05 inteira em cada `NN-tema-gK`**, sobre a `narracao.mp3` da junção e o `roteiro.txt`
   da variação. **Nunca some a duração do gancho** aos tempos do corpo: a junção apara silêncio e
   o MP3 desloca amostras; tempo se mede no arquivo final.
5. **Fases 06 a 08 por variação**: `biblioteca.py publicar NN-tema-gK <ids>`; uma composição por
   variação em `Raiz.tsx`, com id que diz o gancho, `P<NN>-<tema>-g<K>-<angulo>` (ex.:
   `P12-garrafa-g2-preco`); `sons.json` e `sons.py` por variação. As cenas do corpo são o mesmo
   código lendo o `palavras.json` da variação, porque nenhum segundo é digitado (`VID-6`) *(a validar
   no piloto: o esqueleto importa um `palavras.json` só; sem fábrica, um `roteiro.ts` por variação)*.

## Cartão final

Nos últimos 2–3 s, dentro da área segura: a oferta como está na página (preço e condição
idênticos, CDC art. 30), o CTA com o verbo do botão e o **logo como pixel real** (`motion/marca/logo-*`
por `urlDaMarca`, fase 07, passo 8). Entra na frase do CTA (`em(faixa, '<verbo>')`) e fica até `FIM`;
com menos de 2 s, alongue a fala do CTA no roteiro, porque `FIM` não se digita.

## Render 1440×2560

A escala sai da largura alvo, nunca digitada (`VID-3`): `1.333` daria 1439,64×2559,36 e o h264
desceria a 2558 em silêncio; `1440/1080` dá 1440×2560 (medido em Python e JS). O ffprobe tem que dar
`h264` 1440×2560 e `aac` estéreo ≥ 128 kbps (o reel normalizado de origem: ~200 kbps); cole no `anuncio.md`.

```bash
S=$(python -c "s = 1440 / 1080; w, h = round(1080 * s), round(1920 * s); assert (w, h) == (1440, 2560), (w, h); print(repr(s))")
(cd motion/remotion && npx remotion render src/index.ts <Comp> ../pecas/<NN-tema-gK>/saida/anuncio.mp4 --public-dir=../pecas/<NN-tema-gK>/public --scale=$S)
(cd motion/remotion && node scripts/normalizar-audio.mjs --arquivo=../pecas/<NN-tema-gK>/saida/anuncio.mp4)
python -c "import subprocess,sys; sys.path.insert(0,'motion/ferramentas'); from _ffmpeg import ffprobe; subprocess.run([ffprobe(),'-v','error','-show_entries','stream=codec_name,width,height,channels,bit_rate','-of','compact',sys.argv[1]])" motion/pecas/<NN-tema-gK>/saida/anuncio.mp4
```

## Edição cinética ("VSL Japonesa") no motor de colagem

| No vídeo público | No motor |
|---|---|
| sem respiro morto | texto sem `[pause]` e com poucas reticências; a junção apara as pontas; vão > 0,35 s no `palavras.json` (comando abaixo) se resolve regerando a parte ou acelerando (fase 04, passo 8), e a fase 05 se refaz |
| uma frase por tela, fonte forte | `Manchete` (cada palavra num papel, colada quando é dita), na fonte de manchete da marca; a pílula some quando o B entra |
| fundo que muda por frase | uma cena por frase (`CENA_INICIO`), `Fundo` com outra `COR.*`, chicote ou cobertura em toda troca, trocas a ≥ 12 quadros |
| figurinha sobre a palavra, a palavra na cor dela | `Recorte` da biblioteca entrando em `em(faixa, '<palavra>')` e a palavra pintada com a `COR.*` da marca mais próxima da figurinha (cor só por token) |
| quebra de padrão com gente real | 1–2 fotos reais de banco livre (`navegador/bancos-livres.md`; `foto_papel.py --origem banco-livre --fonte <URL>`); **rosto real nunca é sintetizado**, e figurante não é "cliente" *(vídeo de banco: a validar no piloto; o motor de colagem só tem foto)* |
| tremida | `tremor(q, fq(em(faixa, '<palavra>')))` na soma da câmera, só no impacto |
| trilha contínua + impacto | `sons.json` com a 1ª seção na 1ª frase do gancho: antes dela a trilha é muda (a tensão é do `drone`) e a troca cai na barra seguinte, então ouça o começo no render de teste; `thump`, `pop`, `carimbo` nas palavras-chave |

Vãos mortos, da raiz (na peça de origem, orgânica, só 3 passavam de 0,35 s, pausas do gancho):

```bash
python -X utf8 -c 'import json, sys; P = json.load(open(sys.argv[1], encoding="utf-8")); [print("%6.2f -> %6.2f  vão de %.2f s antes de %s" % (a["fim"], b["inicio"], b["inicio"] - a["fim"], b["texto"])) for a, b in zip(P, P[1:]) if b["inicio"] - a["fim"] > 0.35]' motion/pecas/<NN-tema-gK>/palavras.json
```

## Métricas (Gerenciador, só leitura) e diagnóstico

Por anúncio (cada variação), no período em que rodou (a tela está em `navegador/meta-anuncios.md`).
Poucas impressões não decidem nada: combine o mínimo com o usuário antes de ler *(hipótese)*.

| Métrica | Conta | Referência |
|---|---|---|
| taxa de gancho | reproduções de vídeo de 3 s ÷ impressões | > 30% forte; < 20% refazer a abertura (referência de terceiros: [adriselab](https://adriselab.com/learn/hook-rate) · [vaizle](https://insights.vaizle.com/hook-rate-hold-rate/) · [sparkugc](https://www.sparkugc.com/resources/hook-rate-benchmarks-2026)) |
| retenção | ThruPlays ÷ reproduções de 3 s, e a queda em 25/50/75/95/100% | entre as variações |
| CTR de link | cliques no link ÷ impressões | entre as variações |
| CPA, ROAS | se a conta mede conversão | o do usuário |

| Sinal | Leitura | O que fazer |
|---|---|---|
| gancho bom, retenção caindo | o corpo não entrega o que a abertura prometeu | alinhar a promessa da abertura ao corpo, ou refazer o corpo |
| gancho fraco | a abertura | gancho novo sobre o mesmo corpo |
| CTR bom, conversão ruim | a página ou a oferta | conferir a página: preço igual ao do vídeo, carregamento, condição |

## O pacote: `motion/pecas/NN-tema/anuncio.md`

```markdown
# Anúncio — <tema> — AAAA-MM-DD
Objetivo: <vendas | tráfego | leads> · Destino: <URL | WhatsApp | perfil> · Público: <frio | morno | quente>
## Texto principal (até ~44 caracteres)
## Título
## Descrição
## Botão de CTA (o mesmo verbo dito no vídeo: Saiba mais | Comprar agora | Enviar mensagem)
## Variações
| Nome | Pasta | Composição | Gancho (texto exato) | Ângulo | Duração | Arquivo |
| NN-tema-g1-<angulo> | motion/pecas/NN-tema-g1/ | P<NN>-<tema>-g1-<angulo> | … | … | … s | saida/anuncio.mp4 |
## Conformidade (a tabela fato → fonte de `fontes.md` e os itens de `copy/oferta.md`)
## Checklist de área segura
- [ ] texto, logo e preço em y 269–1248 e x 65–1015, no still do meio e do fim de cada movimento
- [ ] pílula inteira acima de y 1248
- [ ] cartão final (oferta + CTA + logo real) nos últimos 2–3 s
- [ ] legenda queimada: toda fala na tela
- [ ] ffprobe: h264 1440×2560, aac 2 canais ≥ 128 kbps
## Resultado (fase 10, só leitura)
| Variação | Impressões | Reproduções de 3 s | Taxa de gancho | ThruPlays | CTR de link | CPA/ROAS | Lido em |
```

## Travas

- A skill **nunca** cria, sobe, impulsiona, duplica nem edita campanha, conjunto ou anúncio, e
  nunca gasta verba, sem OK do usuário naquele momento. Na v1, subir é do usuário: a skill entrega
  o `anuncio.md` e os MP4. O Gerenciador é só leitura (`navegador/meta-anuncios.md`).
- A narração é sintética: a divulgação de IA do anúncio o usuário confere ao subir *(a validar no piloto)*.

## Erros comuns

- Pílula em `y = 1500` no anúncio: cai na faixa da interface, os 35% de baixo.
- Escala digitada (`--scale=1.333`): sai 1440×2558, esticado, com exit 0 (`VID-3`).
- Tempo do corpo somando a duração do gancho, em vez de alinhar a junção.
- Corpo que depende do gancho ("isso que eu falei"), ou regerado por variação; promessa só falada.
- Refazer o corpo quando o gancho é fraco, ou o gancho quando a retenção cai.
