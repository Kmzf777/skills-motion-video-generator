# Fase 04 — Narração

A narração é a régua da peça: legenda, colagem, câmera e som leem o tempo das palavras deste
áudio. Ela é gerada na ElevenLabs (modelo v4) pelo Chrome do usuário, em 3 tomadas do texto
inteiro, e a skill escolhe sozinha a tomada fiel ao roteiro.

> Bash, da raiz do repositório, cada bloco numa chamada só (variável de shell não sobrevive
> entre chamadas). `python` é sempre o do `motion/.venv` (fase 00): `motion/.venv/Scripts/python`
> no Windows, `motion/.venv/bin/python` no macOS/Linux.

## Quando

Logo depois do OK do roteiro (fase 03). Narração nova depois disso (outra tomada, aceleração,
regravação) obriga a refazer a fase 05 inteira; palavra mudada volta à parada da fase 03.

## Entradas

- `motion/pecas/<NN-tema>/roteiro.txt` (a fala exata, sem tags) e `roteiro-tags.txt` (fase 03).
- `motion/marca/identidade.json` → `voz.nome`, `voz.modelo` (`v4`) e `idioma`; a seção Voz do
  dossiê (nome exato, rótulo do modelo na tela, ajustes já usados).
- A duração estimada na fase 03 (palavras ÷ 2,6 = segundos na velocidade normal).
- `navegador/chrome.md` e `navegador/elevenlabs.md`: a mecânica do site, o download e as travas.

## Passos

1. **Confira o texto antes de gastar crédito.** Regras da v4:
   - uma tag por trecho, em inglês, entre colchetes, no começo do trecho (linha própria ou
     início da linha); a emoção vale até a próxima tag;
   - reticências desaceleram; `[pause]` respira; a troca de registro (tensão → amigável na
     interjeição que acalma) é de propósito: é ela que segura o gancho;
   - número, sigla e símbolo por extenso, como a voz deve ler. O que a tela precisa mostrar
     diferente ("350 g") vira colagem B na fase 07, não algarismo no texto da voz;
   - modo `oferta`: sem `[pause]`, poucas reticências.

   Exemplo genérico (não é fala de marca nenhuma):

   ```text
   [low, tense, slow, almost a whisper, suspenseful]
   Tem uma coisa no rótulo… que quase ninguém lê.
   [pause]
   [cold, deliberate] E ela muda tudo.
   [warm, friendly, smiling, like talking to a friend] Ei, respira. Até o fim do vídeo você vai saber onde olhar.
   ```

   **`roteiro.txt` = a mesma fala, sem as tags.** É ele que a fase 05 usa como verdade e que
   vira legenda. Os arquivos podem ter mudado desde a parada: rode de novo o portão do passo 10
   da fase 03 (`conferir_roteiro.py`, salvo de novo na pasta temporária se ela foi limpa), que
   compara os dois fora das tags e acusa algarismo, símbolo, sigla e tag no arquivo errado.
   Só gere com `OK`.

2. **Prepare a ElevenLabs** numa aba nova (`navegador/elevenlabs.md`, passos 1–6):
   - **saldo**: 3 tomadas custam ~3× o texto *(a validar no piloto: se as tags contam)*. Sem
     saldo, pare e avise. Nunca compre crédito nem troque de plano;
   - **modelo**: a v4 pela regra do `elevenlabs.md` (rótulo com "v4" é ela; sem ele, o de tags e
     expressividade). Anote o rótulo exato. Nada corresponde com clareza → pare e pergunte;
   - **voz**: a de `voz.nome`, pelo nome exato. Ainda `null` → faça os passos 17–18 da fase 01
     antes (a voz da série é escolha do usuário, uma vez);
   - **ajustes**: os do dossiê; não mexa. Mesmo modelo, voz e ajustes nas três tomadas.

3. **Gere 3 tomadas do texto inteiro** (`navegador/elevenlabs.md`, passos 7–11: gerar, baixar,
   mover, ler o saldo de novo, fechar a aba). Sempre `roteiro-tags.txt` completo: gerar em partes
   muda a entonação entre os cortes. Gere até ter 3 tomadas; se uma geração trouxer mais de uma
   variante, cada variante conta como tomada *(a validar no piloto)*. Cada arquivo se identifica
   pelo nome ou pela diferença da listagem, nunca "o arquivo mais novo" (outra sessão grava na
   mesma pasta), e vai para `motion/pecas/<NN-tema>/public/fonte/narracao-tomada-<n>.mp3`, n = 1,
   2, 3 na ordem de geração. Voz e modelo de cada tomada se conferem pelo que a tela e o nome do
   arquivo mostram *(a validar no piloto)*.

4. **Transcreva cada tomada e meça a duração.** Aqui a transcrição é texto corrido, sem
   `-ml 1`: importa o que foi dito, não o tempo. O `instalar.py` deixa o whisper.cpp e o
   `ggml-small.bin` em `motion/ferramentas/whisper.cpp/` (executável `main`, ou `whisper-cli`
   nas versões novas; o laço abaixo acha o que existir):

   ```bash
   P=motion/pecas/<NN-tema>; T=$P/saida/tomadas; WD=motion/ferramentas/whisper.cpp; mkdir -p $T
   L=$(python -c "import json; print(json.load(open('motion/marca/identidade.json', encoding='utf-8'))['idioma'][:2])")
   FF=$(python -c "import sys; sys.path.insert(0, 'motion/ferramentas'); from _ffmpeg import ffmpeg; print(ffmpeg())")
   FP=$(python -c "import sys; sys.path.insert(0, 'motion/ferramentas'); from _ffmpeg import ffprobe; print(ffprobe())")
   for WB in $WD/whisper-cli $WD/build/bin/whisper-cli $WD/main; do [ -f "$WB" ] || [ -f "$WB.exe" ] && break; done
   MOD=$(find $WD -maxdepth 2 -name 'ggml-small.bin' | head -1)
   for n in 1 2 3; do
     "$FF" -y -v error -i $P/public/fonte/narracao-tomada-$n.mp3 -ar 16000 -ac 1 -c:a pcm_s16le $T/tomada-$n.wav
     "$WB" -m "$MOD" -f $T/tomada-$n.wav -l $L -otxt -of $T/tomada-$n
     echo "tomada $n: $("$FP" -v error -show_entries format=duration -of csv=p=0 $P/public/fonte/narracao-tomada-$n.mp3) s"
   done
   ```

5. **Compare cada transcrição com o roteiro.** O algarismo do whisper ("350", "2.400") vira
   extenso antes da comparação, então número não conta como diferença:

   ```bash
   python - motion/pecas/<NN-tema>/roteiro.txt motion/pecas/<NN-tema>/saida/tomadas/tomada-*.txt <<'EOF'
   import difflib, re, sys, unicodedata
   sys.stdout.reconfigure(encoding="utf-8")
   sys.path.insert(0, "motion/ferramentas")
   try:
       from alinhar_narracao import por_extenso   # 350 -> "trezentosecinquenta"
   except Exception:
       por_extenso = str
   def palavras(s):
       s = re.sub(r"\[[^\]]*\]", " ", s).replace("%", " por cento ")
       s = re.sub(r"(?<=\d)\.(?=\d{3})", "", s)
       s = re.sub(r"\d+", lambda m: f" {por_extenso(int(m.group()))} ", s)
       s = unicodedata.normalize("NFKD", re.sub(r"[^\w\s]", " ", s.lower()))
       return s.encode("ascii", "ignore").decode().split()
   rot = palavras(open(sys.argv[1], encoding="utf-8").read())
   for arq in sys.argv[2:]:
       tom = palavras(open(arq, encoding="utf-8", errors="replace").read())
       ops = difflib.SequenceMatcher(a=rot, b=tom, autojunk=False).get_opcodes()
       dif = [(rot[a0:a1], tom[b0:b1]) for op, a0, a1, b0, b1 in ops
              if op != "equal" and "".join(rot[a0:a1]) != "".join(tom[b0:b1])]
       print(f"{arq}: {len(dif)} diferença(s)")
       for a, b in dif:
           print(f"   roteiro: {' '.join(a) or '-'}  |  tomada: {' '.join(b) or '-'}")
   EOF
   ```

6. **Escolha sozinho.** O usuário optou por geração autônoma: não pergunte qual tomada.
   - **Reprova** a tomada com palavra trocada, pulada, repetida ou inventada, tag lida em voz
     alta (inglês na transcrição: `pause`, `whisper`, `warm`…) ou fim cortado.
   - **Refaça as 3, sem perguntar**, quando a voz ou o modelo saíram errados (passo 3) ou quando
     nenhuma tomada é fiel ao roteiro. Modelo que lê tag não é o de tags (`elevenlabs.md`):
     troque-o antes de gerar de novo.
   - Não confunda com alucinação do whisper *(a validar no piloto)*: frase pronta acrescentada
     no fim, sobre o silêncio ("Legendas pela comunidade…", "Obrigado.") — `roteiro: -` depois
     da última frase dita inteira — não é da voz e não reprova.
   - Entre as aprovadas, a de duração mais perto da estimativa; empate → a mais curta.
   - Duas rodadas sem tomada fiel: o problema é o texto. Grafia para a voz (número por
     extenso, sigla escrita como se fala) muda nos **dois** arquivos; trocar palavra é mudar o
     roteiro aprovado e volta à parada da fase 03.
   - Diga ao usuário numa linha: tomada escolhida, diferenças, duração e estimativa.

7. **Grave a escolhida** como a narração da peça (`<n>` = a tomada escolhida):

   ```bash
   P=motion/pecas/<NN-tema>; cp $P/public/fonte/narracao-tomada-<n>.mp3 $P/public/fonte/narracao.mp3
   ```

8. **Aceleração, só se o usuário pedir** (ou se o dossiê registrar uma velocidade para a
   série). Local, com o ffmpeg do motor — `atempo` preserva o tom —, sempre a partir da tomada
   original, nunca de um arquivo já acelerado:

   ```bash
   P=motion/pecas/<NN-tema>
   FF=$(python -c "import sys; sys.path.insert(0, 'motion/ferramentas'); from _ffmpeg import ffmpeg; print(ffmpeg())")
   "$FF" -y -v error -i $P/public/fonte/narracao-tomada-<n>.mp3 -filter:a atempo=1.25 -c:a libmp3lame -q:a 2 $P/public/fonte/narracao.mp3
   ```

   (Exemplo: a peça de origem foi ao ar a 1,25×.) Pedido depois das fases 05–07: refaça a fase
   05 inteira no arquivo novo, rode o `sons.py` de novo e atualize o `FIM` esperado no teste da
   peça (fase 07, passo 1); as cenas não mudam, porque nenhuma tem segundo digitado. Velocidade
   nova para a série vai ao dossiê.

9. **Oferta com variações**: o corpo é narrado uma vez e cada gancho à parte (passos 2–7 com o
   texto da parte, 3 tomadas cada); `corpo.mp3` e `gancho-K.mp3`; junção pelo bloco de
   `copy/criativos-anuncio.md`.

## Saídas

- `motion/pecas/<NN-tema>/public/fonte/narracao.mp3` — a narração final, a que o motor toca e
  a fase 05 mede. Oferta com variações: `corpo.mp3` e `gancho-K.mp3` na peça base e a junção
  em `motion/pecas/NN-tema-gK/public/fonte/narracao.mp3` (`copy/criativos-anuncio.md`).
- `public/fonte/narracao-tomada-{1,2,3}.mp3` e `saida/tomadas/` (WAV e transcrição de cada
  tomada) — guarde até a entrega; `saida/` é limpa na fase 08.
- No dossiê, se mudou: o rótulo do modelo na tela, os ajustes e a velocidade da série.

## Pronto quando

- o portão do passo 10 da fase 03 (rodado de novo no passo 1) dá `OK` para `roteiro.txt` e `roteiro-tags.txt`;
- a tomada escolhida tem 0 diferença contra o roteiro (alucinação de silêncio conferida);
- `public/fonte/narracao.mp3` existe, e a duração dele (ffprobe) está perto da estimativa;
- o usuário recebeu a linha do passo 6.

## Erros comuns

| Sintoma | Causa | Regra |
|---|---|---|
| Entonação muda no meio da peça | texto gerado em partes | o texto inteiro numa geração |
| "pause" ou "warm" falado no áudio | modelo sem suporte a tags (`elevenlabs.md`) | troque o modelo e refaça as 3 |
| Legenda mostra palavra que a voz não disse | `roteiro.txt` diferente da fala | passo 1 e passo 5; o alinhamento não reclama, interpola |
| Número lido de outro jeito | algarismo no texto da voz | por extenso nos dois arquivos; o portão da fase 03 acusa |
| Tomada de outra peça entrou sem erro | "o arquivo mais novo" da pasta de downloads | identificar pelo nome ou pela listagem |
| Legenda fora do tempo depois de acelerar | tempo da versão anterior reaproveitado | acelerou → fase 05 de novo, no arquivo final |
| Voz "quase igual" à da peça anterior | voz ou ajuste trocado | nome exato e ajustes do dossiê |
| Crédito comprado para terminar a peça | — | nunca: sem saldo, pare e avise |

Próxima: fase 05 (`fases/05-tempo.md`).
