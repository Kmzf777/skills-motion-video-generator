# Fase 05 — Tempo das palavras

O `palavras.json` diz quando cada palavra começa e termina, e tudo na montagem lê dele. O
usuário julga a peça pela sincronia voz × legenda × movimento antes de qualquer outra coisa:
é nesta fase que ela se ganha ou se perde.

> Bash, da raiz do repositório, cada bloco numa chamada só (variável de shell não sobrevive
> entre chamadas). `python` é sempre o do `motion/.venv` (fase 00): `motion/.venv/Scripts/python`
> no Windows, `motion/.venv/bin/python` no macOS/Linux.

## Quando

Logo depois da fase 04, e **de novo toda vez que `public/fonte/narracao.mp3` mudar**: outra
tomada, aceleração, regravação, até um corte de 0,1 s no começo. Todo tempo se mede no arquivo
final; tempo de outra versão do áudio nunca se reaproveita.

Variações (modo `oferta`): alinhe em cada `NN-tema-gK` sobre a junção; nunca some a duração do gancho.

## Entradas

- `motion/pecas/<NN-tema>/public/fonte/narracao.mp3` (o final, já acelerado se for) e `roteiro.txt`.
- whisper.cpp com o modelo `small` em `motion/ferramentas/whisper.cpp/` e torch/torchaudio no
  `motion/.venv` (fase 00). O modelo de alinhamento (MMS_FA, ~1,2 GB) baixa na primeira
  execução do passo 3, para o cache do torch: avise o usuário do tamanho antes.
- Seção Voz do dossiê: se esta voz, nesta velocidade, já teve a fusão conferida.

## Por que três ferramentas

Nenhum alinhador sozinho presta. Medido na peça de origem contra 109 ataques lidos à mão:

| Fonte do tempo | Mediana | Máximo | Defeito |
|---|---:|---:|---|
| whisper | 0,10 s | 0,76 s | desliza em fala contínua, sem cair em pausa nenhuma |
| CTC (alinhamento forçado) | 0,09 s | 0,39 s | ~0,1 s tarde na frase; às vezes a frase inteira, depois de pausa |
| fusão (`alinhar_forcado.py`) | **0,02 s** | **0,15 s** | — |

O **texto** vem sempre do `roteiro.txt` (com `-ml 1` o whisper corta o UTF-8 no meio do
acento — "você" sai "voc" e um caractere inválido — e junta número falado num token só); o
**tempo**, da fusão; a **prova**, do áudio.

## Passos

1. **WAV 16 kHz e whisper com tempo por palavra.** `-ml 1 -sow` = um segmento por palavra (sem
   as duas, o tempo é de frase). `-l` = duas letras de `idioma` (`pt-BR` → `pt`); `.en` é só inglês.

   ```bash
   P=motion/pecas/<NN-tema>; WD=motion/ferramentas/whisper.cpp; mkdir -p $P/saida
   L=$(python -c "import json; print(json.load(open('motion/marca/identidade.json', encoding='utf-8'))['idioma'][:2])")
   FF=$(python -c "import sys; sys.path.insert(0, 'motion/ferramentas'); from _ffmpeg import ffmpeg; print(ffmpeg())")
   for WB in $WD/whisper-cli $WD/build/bin/whisper-cli $WD/main; do [ -f "$WB" ] || [ -f "$WB.exe" ] && break; done
   MOD=$(find $WD -maxdepth 2 -name 'ggml-small.bin' | head -1)
   "$FF" -y -v error -i $P/public/fonte/narracao.mp3 -ar 16000 -ac 1 -c:a pcm_s16le $P/saida/n16k.wav
   "$WB" -m "$MOD" -f $P/saida/n16k.wav -l $L -ml 1 -sow -oj -of $P/saida/whisper
   ```

2. **Texto do roteiro + tempo do whisper:**

   ```bash
   P=motion/pecas/<NN-tema>
   python motion/ferramentas/alinhar_narracao.py $P/saida/whisper.json $P/roteiro.txt $P/saida/n16k.wav $P/palavras-whisper.json
   ```

   Casa as letras sem acento das duas sequências; o algarismo do whisper vira extenso
   (`por_extenso`). Palavra do roteiro que a voz não disse **não dá erro**: herda um tempo
   interpolado dos vizinhos — por isso a fase 04 prova que a fala é o roteiro. Voz que lê um
   número de outro jeito ("zero" × "nenhum"): a exceção vai em `NUMEROS`, no próprio script.
   Idioma que não é português: `por_extenso` não casa os números; leia esses trechos no passo 5.

3. **Fusão com o alinhamento forçado** (sem o terceiro argumento, só imprime a comparação):

   ```bash
   P=motion/pecas/<NN-tema>
   python motion/ferramentas/alinhar_forcado.py $P/palavras-whisper.json $P/public/fonte/narracao.mp3 $P/palavras.json
   ```

   Uma linha por palavra: `i texto antes -> depois (delta) fim conf [regra]`. A regra diz de
   onde veio o tempo: `pausa` (ataque logo depois de pausa), `média` (as fontes concordam), `ctc`
   (o whisper deslizou), `whisper` (a frase do CTC atrasou). `<<<` = a fusão moveu a palavra
   ≥ 0,08 s; `conf` muito abaixo das vizinhas = palavra dita diferente do escrito. Anote as duas.

4. **Confira contra o áudio — ataques depois de pausa:**

   ```bash
   P=motion/pecas/<NN-tema>
   python motion/ferramentas/conferir_alinhamento.py pausas $P/palavras.json $P/public/fonte/narracao.mp3
   ```

   Cada ataque depois de pausa funda, a palavra mais perto e o delta; `<<<` = |delta| ≥ 0,06 s.
   A última linha conta os suspeitos: **todo `<<<` se lê** no passo 5.

5. **Leia os suspeitos no envelope**, de ~0,3 s antes a ~1 s depois da palavra (várias faixas
   numa chamada):

   ```bash
   P=motion/pecas/<NN-tema>
   python motion/ferramentas/conferir_alinhamento.py faixa $P/palavras.json $P/public/fonte/narracao.mp3 23.6-24.6 31.0-32.2 --com $P/palavras-whisper.json
   ```

   Exemplo real da peça de origem, com o whisper 0,65 s atrasado em fala contínua:

   ```text
   23.60..24.60  (1 caractere = 20 ms; dígito = décimo de segundo)
     6----7----8----9----0----1----2----3----4----5----
     ::...      .:|||###|||||####|::.:#|::::||#||:::.
   A            ^Nao         ^e  ^especial.
   B                                             ^Nao
   ```

   - envelope: ` ` silêncio (< −50 dB) · `.` −50..−40 · `:` −40..−30 · `|` −30..−22 · `#` > −22;
     a régua marca o décimo de segundo a cada 5 caracteres; `A` = `palavras.json`, `B` = `--com`;
   - o ataque real: **vogal** = o primeiro `|`/`#` depois do silêncio; **oclusiva** (p, t, k, b,
     d, g) = o fim de um silêncio curto, a oclusão; **fricativa e nasal** (s, f, x, v, z, m, n) =
     o primeiro `.`/`:` antes da vogal;
   - **respiro** antes da frase também é `.`/`:`, mas separado da palavra por silêncio: não é a
     palavra, e é o falso `<<<` mais comum do `pausas`.

   No exemplo, "Não" começa em ~23,82 s (`.:` depois de 0,12 s de silêncio): `A` marcou 23,83,
   certo; `B` marcou 24,48, sem pausa nenhuma no caminho que denunciasse o atraso.

6. **Voz nova ou velocidade nova: leia um ataque por frase.** Os limiares da fusão foram
   calibrados na voz da peça de origem, e marca nova é voz nova: na primeira peça de cada voz, e
   a cada mudança de velocidade, os `<<<` não bastam. Liste os inícios de frase com a faixa
   pronta e leia em lotes de 6–8 faixas por chamada:

   ```bash
   python - motion/pecas/<NN-tema>/palavras.json <<'EOF'
   import json, sys
   sys.stdout.reconfigure(encoding="utf-8")
   P = json.load(open(sys.argv[1], encoding="utf-8"))
   for k, p in enumerate(P):
       if k == 0 or P[k - 1]["texto"][-1] in ".!?…:" or p["inicio"] - P[k - 1]["fim"] > 0.25:
           print(f'{p["inicio"]:7.2f}  {p["texto"]:<14} {max(0, p["inicio"] - 0.3):.1f}-{p["inicio"] + 0.8:.1f}')
   EOF
   ```

   Anote, por frase, JSON, lido e delta. Régua da origem: **mediana ~0,02 s, máximo ~0,15 s**.
   Passou: registre na seção Voz do dossiê ("voz X a 1,0×: fusão conferida em N frases, mediana
   Y s, máximo Z s, peça NN"). Peças seguintes com a mesma voz e velocidade: bastam os `<<<` e o
   ataque de cada abertura de cena e de cada palavra B que bate com impacto.

7. **Corrija só com número lido no envelope.** Erro isolado: troque o `inicio` da palavra em
   `palavras.json` pelo ataque lido (maior que o da anterior, menor que o próprio `fim`) e rode
   o `faixa` de novo: o `^` tem que cair no ataque. O mesmo erro em 3 frases ou mais = a fusão
   não serve para esta voz: corrija igual e escreva a lição já (fase 10), com a regra que falhou
   (`[média]`, `[ctc]`…). Rodar o passo 3 de novo apaga as correções à mão.

8. **Feche.** `pausas` de novo (todo `<<<` restante tem explicação: respiro, estalo, correção
   medida) e a prova de que o tempo é deste áudio — o `fim` da última palavra cabe na duração:

   ```bash
   P=motion/pecas/<NN-tema>
   FP=$(python -c "import sys; sys.path.insert(0, 'motion/ferramentas'); from _ffmpeg import ffprobe; print(ffprobe())")
   "$FP" -v error -show_entries format=duration -of csv=p=0 $P/public/fonte/narracao.mp3
   python -c "import json, sys; print(json.load(open(sys.argv[1], encoding='utf-8'))[-1]['fim'])" $P/palavras.json
   ```

## Saídas

- `palavras.json` (fundido e conferido: o que o `roteiro.ts` importa e o `sons.py` lê) e
  `palavras-whisper.json` (a linha `B` do `--com`), na pasta da peça. `palavras.json` novo
  numa peça já montada: rode o `sons.py` de novo e atualize o `FIM` esperado no teste da peça
  (fase 07, passo 1).
- `saida/n16k.wav` e `saida/whisper.json` (intermediários); no dossiê, a voz conferida.

## Pronto quando

- todo `<<<` do `pausas` foi lido no `faixa` e está certo ou explicado;
- voz ou velocidade nova: um ataque por frase lido, mediana ~0,02 s, nenhum acima de ~0,15 s;
- o `fim` da última palavra é menor que a duração do `narracao.mp3` atual;
- nenhuma correção à mão sem número lido no envelope.

## Erros comuns

| Sintoma | Causa | Regra |
|---|---|---|
| Legenda 0,5–0,7 s atrasada num trecho inteiro | whisper deslizou em fala contínua | sempre a fusão; nunca o whisper sozinho |
| Frase inteira 0,2–0,4 s atrasada depois de pausa | CTC sozinho | a fusão usa o fim da pausa; confira no `faixa` |
| "A diferença é 0,1 s, ninguém vê" | — | foi o que o cliente viu e chamou de dessincronia |
| Legenda com acento quebrado ou "350" | texto do whisper na tela | o texto vem do `roteiro.txt` |
| Tempo de frase, não de palavra; transcrição traduzida | sem `-ml 1 -sow`; modelo `.en` ou `-l` errado | as duas flags; `small` multilíngue; `-l` do `identidade.json` |
| `<<<` que some quando você lê | respiro antes da frase | respiro tem silêncio antes da palavra |
| Tudo deslocado depois de acelerar ou trocar a tomada | tempo de outra versão | fase 05 inteira no arquivo final |

Próxima: fase 06 (`fases/06-assets.md`) se ainda falta asset; senão, fase 07.
