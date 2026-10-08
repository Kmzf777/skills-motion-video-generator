# Fase 07 — Montagem no Remotion

A peça é código: um `roteiro.ts` que dá destino a cada fala, cenas com câmera e planos,
chicote em toda troca e um som por entrada, tudo lendo o tempo do `palavras.json`. Monte direto
no código, sem storyboard, e vá cedo para a fase 08: o usuário julga pelo vídeo.

> Bash, da raiz do repositório. `python` é sempre o do `motion/.venv` (fase 00):
> `motion/.venv/Scripts/python` no Windows, `motion/.venv/bin/python` no macOS/Linux. `npx` e
> `node` em subshell, `(cd motion/remotion && …)`, porque o `cwd` do Bash da sessão persiste
> (PowerShell: `Push-Location motion/remotion; …; Pop-Location`).

## Quando

Com o `palavras.json` conferido (fase 05) e os assets publicados (fase 06).

## Entradas

- `motion/pecas/<NN-tema>/`: `palavras.json`, `fontes.md` (frases de abertura de bloco),
  `public/fonte/narracao.mp3` e `public/colagem/`; `motion/marca/` (identidade e logos).
- O esqueleto `motion/remotion/src/pecas/_modelo/` e o motor `motion/remotion/src/colagem/`.

## Passos

1. **Copie o esqueleto e os dois testes dele, e ligue os três à peça:**

   ```bash
   cp -r motion/remotion/src/pecas/_modelo motion/remotion/src/pecas/<NN-tema>
   cp motion/remotion/tests/modelo-roteiro.test.ts motion/remotion/tests/<NN-tema>-roteiro.test.ts
   cp motion/remotion/tests/modelo-tempos.test.ts motion/remotion/tests/<NN-tema>-tempos.test.ts
   ```

   - `grep -rn "00-exemplo" motion/remotion/src/pecas/<NN-tema>/` só acha o `roteiro.ts`: troque
     ali `00-exemplo` por `<NN-tema>` no import do `palavras.json`. Só a composição `Exemplo`
     passa por `<SomTolerante>` (`Raiz.tsx`); a peça exige o áudio, e sem `narracao.mp3` cai com 404.
   - No teste copiado (o portão de A/B), troque `_modelo` por `<NN-tema>` no import e ponha o
     `FIM` da peça no `expect(FIM).toBe(…)`; refaça-o a cada aceleração ou realinhamento.
   - No teste de tempos copiado (o portão "nenhum segundo digitado" do passo 3), troque só
     `'_modelo'` por `'<NN-tema>'` na constante `PASTA`. As duas exceções (`['batimento', 0.05, …]`
     e `const base = 0.2;`) continuam valendo; se a peça não tiver uma delas, o teste segue
     passando. Exceção nova não entra em `EXCECOES` sem a mesma justificativa escrita no
     comentário: tempo que não anda quando a narração é realinhada.

   O `FIM` esperado sai deste cálculo:

   ```bash
   python -c "import json, math, sys; P = json.load(open(sys.argv[1], encoding='utf-8')); print(math.ceil((P[-1]['fim'] + 0.5) * 10) / 10)" motion/pecas/<NN-tema>/palavras.json
   ```

2. **Dê destino a cada fala no `roteiro.ts`, na ordem da narração.** O que não for declarado
   vai para a pílula (sistema A).

   | Chamada | Destino da fala |
   |---|---|
   | `r.b('trecho')` | vira colagem (sistema B) e sai da pílula |
   | `r.mudo('trecho')` | a colagem já disse por outro nome; não aparece em lugar nenhum |
   | `r.t('trecho')` | só marca tempo (gesto, câmera, som); a fala continua na pílula |

   Os trechos são procurados **em ordem**, a partir do último achado (palavra repete): fora de
   ordem, pegam a ocorrência errada ou lançam `não encontrado a partir da palavra N`. **Uma fala
   vai para A ou para B, nunca para as duas**, e a pílula some no quadro em que um B entra — o
   motor garante isso para o que está em `b`. Vai para B o conceito, o número, a frase
   repetível, a prova da marca; nas referências, ~3 entradas por segundo no gancho.

3. **Nenhum segundo digitado — em cena, em `Sons.tsx` nem na trilha** (nomes de exemplo):

   | Precisa de | Use |
   |---|---|
   | início de um trecho | `S3.prova.inicio` |
   | palavra do meio de um trecho | `em(S5.lista, 'segundo')` — lança se não achar; `em(f, 'x', 2)` = a 2ª |
   | até onde vai a fala do trecho | `depois(S2.alivio)` (início da palavra seguinte) |
   | troca de fase dentro de uma cena | `TROCA.x` — a cena e os chicotes leem o mesmo número |
   | início de cena | `CENA_INICIO[i]` |
   | duração da peça | `FIM` — última palavra + 0,5 s, arredondado para cima ao décimo |
   | quadros que a voz leva num trecho | `fala(faixa)` — o `dur` do Marcador |

   Desvio relativo pode (`S7.tese.inicio - 0.13`); número absoluto, não. A varredura cobre o
   `roteiro.ts` (número solto em `CENA_INICIO`, `TROCA` ou constante) e as `.tsx` (`fq(n)` fora de
   soma, `q:`, `ini=`, `fora=`, tempo de efeito e constante decimal), inclusive decimal < 1:

   ```bash
   P=motion/remotion/src/pecas/<NN-tema>
   grep -nE "([[,:=]) *([0-9]*\.[0-9]+|[1-9][0-9]*) *[],};]" $P/roteiro.ts
   grep -nE "(^|[^-+ ]) *fq\( *[0-9]|(^|[^A-Za-z0-9_])q: *[1-9]|(ini|fora)=\{ *[1-9]|\['[a-z0-9-]+', *([0-9]*\.[0-9]*[1-9]|[1-9])|(const|let) +[A-Za-z_][A-Za-z0-9_]* *= *[0-9]*\.[0-9]+ *;" $P/*.tsx
   ```

   No esqueleto recém-copiado saem só duas linhas, legítimas: `['batimento', 0.05, …]`, contado
   do zero da peça, antes da primeira palavra (não anda no realinhamento), e `const base = 0.2`,
   que é volume da trilha. Qualquer outra linha é tempo absoluto: troque por tempo derivado.

4. **Câmera e parallax em TODA cena.** Cada cena é um `<Palco cam={...} id="cN">` com planos
   `<Plano p>`: fundo p 0,5–0,85 · sombra p 0,6 (atrás) ou 1,3 (à frente) · cena p 1 · primeiro
   plano p 2,4 (1–2 peças grandes perto da lente; acima de 1,4 desfoca sozinho). Câmera =
   `cameraCena(q, chaves, 'cN', intensidade, pulsos, tremores)` (`camera.ts`), que soma
   `cameraEm(q, chaves)` + `deriva` + `pulso` + `...tremores.map(tremor)`: chaves
   `{q, x, y, zoom, rot, curva}` em quadros derivados, `deriva` sempre (nunca para), `pulso` nas
   palavras-colagem, `tremor` só no impacto. **O movimento que um texto espera vem durante a frase.**

5. **Toda troca de enquadramento tem chicote ou cobertura** — corte seco de câmera é salto.
   - **Chicote**: `{q, eixo: 'x' | 'y', dir: 1 | -1}` em `CHICOTES`, no `Peca.tsx`, com
     `q = fq(CENA_INICIO[i])` ou `fq(TROCA.x)`. `dir: 1` = a imagem nova entra pela direita
     (eixo x) ou por baixo (eixo y) e a velha sai pelo lado oposto; `dir: -1` inverte. As duas
     andam **coladas**, uma tela em 12 quadros sob borrão direcional; trocas a menos de 12
     quadros se atropelam.
   - **Cobertura de papel**: `Cobertura` do `apoio.tsx`, na cena que sai, 7 quadros na cor do
     fundo da cena que entra, começando em `fq(CENA_INICIO[i]) - 7`.
   - Cada `CENA_INICIO` (menos o 0) e cada `TROCA.x` tem exatamente um dos dois.

6. **Vozes da colagem (B).** Letra é sempre código, nunca imagem gerada.

   | Componente | Para | Como entra |
   |---|---|---|
   | `Dymo` | afirmação seca, dado, rótulo; em escada | caixa batida como carimbo, letras 1 por quadro; `fundo={COR.acento}` na ênfase |
   | `Serifa` | a palavra-conceito, o tom humano | itálica solta; chega esmagada e assenta |
   | `Marcador` | o que a voz diz enquanto ele escreve | papel rasgado; **`dur={fala(faixa)}`** faz a escrita acabar com a voz |
   | `Recortadas` | número, palavra de impacto | cada letra num papel, uma a cada 2 quadros |
   | `Pilula` | sistema A, na raiz | ≤ 4 palavras e 16 caracteres, corte seco, `y = 1500`; `tema` pelo fundo da cena |

   Grafismos: `Elipse`, `Seta`, `Sublinhado`, `Xis`, `Check`, `Asterisco`, `Brilho`, `Cruz`.

7. **Área segura.** Texto em x ≈ 140–940 com a câmera em repouso — ela anda até ~120 px e amplia
   até ~1,16×, e o texto que cabe na entrada sai do quadro no meio do movimento — e fora dos 5%
   do topo (y < 96) e dos 16% da base (y > 1613), onde fica a interface do Reels. Modo `oferta`:
   área de anúncio y 269–1248, x 65–1015 no quadro final (`AREA_SEGURA.anuncio` no motor), pílula
   com centro ≤ 1210; zona de texto com a câmera conforme `copy/criativos-anuncio.md`.

8. **Produto, logo e identidade: pixel real, medido antes.** O produto entra só como o recorte
   da fase 06, sem nada por cima que mude pixel. O PNG tem margem transparente (na origem o
   pacote ocupava só fy 0,17–0,75): **meça o bbox do alfa** antes de pôr qualquer coisa perto.

   ```bash
   python - motion/pecas/<NN-tema>/public/colagem/<produto>.png <<'EOF'
   import sys
   from PIL import Image, ImageOps
   im = ImageOps.exif_transpose(Image.open(sys.argv[1])).convert("RGBA")
   W, H = im.size
   x0, y0, x1, y1 = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
   print(f"{W}x{H}  produto em fx {x0/W:.3f}-{x1/W:.3f}  fy {y0/H:.3f}-{y1/H:.3f}")
   EOF
   ```

   Desenhe-o com `ProdutoRecortado`: `arquivo` é o caminho dentro de `public/`
   (`colagem/<produto>.png`, ou `-b0.png` se veio do `recortar_folha.py`); `giro` só se o PNG
   vier deitado. Com centro `(x, y)` e altura `h` (largura `w = h·W/H`), o produto ocupa x de
   `x − w/2 + fx0·w` a `x − w/2 + fx1·w` e y de `y − h/2 + fy0·h` a `y − h/2 + fy1·h`; logotipo
   e selo se leem no pixel do recorte. **Texto nunca cobre logotipo nem selo.** Logo da marca:
   `LogoMarca` com `fundo="claro"` ou `"escuro"` (lê `logo.sobre_claro`/`logo.sobre_escuro` de
   `motion/marca/` pelo bundler), nunca copiado para `public/` nem reescrito em fonte. Cor só
   por `COR.escuro`, `claro`, `profundo`, `acento` (um por cena) e `apoio`; fonte só pelo motor.
   Modo `oferta`: cartão final nos últimos 2–3 s (oferta igual à da página, verbo do botão, logo
   por `urlDaMarca`); edição cinética pela tabela de `copy/criativos-anuncio.md`.

9. **Som: um efeito por entrada, trilha em seções pelas frases.**
   - `Sons.tsx` lista `[efeito, segundo, volume]` com o segundo **derivado**: texto e letra
     recortada → `pop`; recorte e fita → `fita`; Marcador, seta, elipse → `rabisco`; Dymo →
     `carimbo` + `digitacao`; impacto com `tremor` → `thump`; objeto que cruza → `whoosh`;
     cobertura → `rasgo` ~0,2 s antes; chicote → `chicote` **0,16 s antes da troca** (o borrão
     começa 6 quadros antes); `drone` e `batimento` no gancho. Nomes: os de `public/sfx/`.
   - Trilha em `motion/pecas/<NN-tema>/sons.json`: cada seção começa numa frase de abertura de
     bloco (`fontes.md`), procurada depois da anterior. Antes da 1ª, a tensão (trilha muda;
     `drone` e `batimento` seguram); tipos `groove`, `respiro` e `fecho` (só a última). Exemplo:

     ```json
     {"bpm": 88, "secoes": [
       {"frase": "Calma", "tipo": "groove"},
       {"frase": "E aqui vem", "tipo": "respiro"},
       {"frase": "Por isso a gente", "tipo": "groove"},
       {"frase": "Salva esse vídeo", "tipo": "fecho"}
     ]}
     ```

   - `python motion/ferramentas/sons.py motion/pecas/<NN-tema>` grava os efeitos e a
     `trilha.wav` (duração = `FIM`) em `public/sfx/`. Rode de novo a cada `palavras.json` novo.

10. **Registre a composição e prove que monta.** Em `motion/remotion/src/Raiz.tsx`, importe a
    peça e acrescente um `<Composition>` igual ao do `Exemplo` (1080×1920, 30 fps), com `id`
    próprio (`P<NN>-<tema>`: letras, números e hífen) e a duração derivada de `FIM`; oferta com
    variações: uma composição por `NN-tema-gK`, id `P<NN>-<tema>-g<K>-<angulo>`. Depois,
    cada caixa numa chamada (PowerShell: `Push-Location motion/remotion; …; Pop-Location`):

    ```bash
    (cd motion/remotion && npx tsc --noEmit && npx vitest run)
    ```

    ```bash
    (cd motion/remotion && node scripts/contato.mjs <Comp> <NN-tema> <s1,s2,...> --saida=../pecas/<NN-tema>/saida/contato.png)
    ```

    Instantes: início de cada cena + 1 s. A folha só sai se toda imagem carregou; olhe-a e siga.

## Saídas

- `motion/remotion/src/pecas/<NN-tema>/`, a composição em `Raiz.tsx`, o teste da peça, `sons.json` e `public/sfx/`.

## Pronto quando

- `tsc` e `vitest` verdes, com o teste da peça (import e `FIM` dela); a varredura do passo 3
  só acha as duas linhas legítimas do esqueleto;
- toda cena tem câmera e parallax, e toda troca de enquadramento tem chicote ou cobertura;
- a folha de contato sai; texto na área segura; nada encosta em logotipo ou selo;
- o `sons.py` rodou depois do último `palavras.json`.

## Erros comuns

| Sintoma | Causa | Regra |
|---|---|---|
| A peça usa as palavras do exemplo | import do `palavras.json` ainda em `00-exemplo` | trocar o import; o `FIM` do teste da peça pega |
| Colagem na palavra errada, ou `não encontrado…` | trecho declarado fora de ordem | na ordem da fala |
| Colagem 0,7 s fora depois de realinhar | segundo digitado | `em()`, `depois()`, `TROCA`, `CENA_INICIO` |
| Marcador termina depois da voz | sem `dur`, ou câmera esperando o texto | `dur={fala(faixa)}`; movimento durante a frase |
| Faixa de fundo ou salto na troca | cena saindo sozinha; troca sem transição | chicote colado ou cobertura, sempre |
| Etiqueta tapando o logotipo | bbox do alfa não medido | medir antes; nunca sobre logo ou selo |

Próxima: fase 08 (`fases/08-conferencia.md`).
