# Fase 03 — Roteiro

Escolhe a pauta, escreve a fala sobre a estrutura da peça de origem (a peça 07, o Reel de
colagem do repositório de origem desta skill, aprovado pelo cliente como impecável) com cada fato amarrado a uma
fonte, e **para**. É a parada da geração: depois do OK, narração e assets seguem sozinhos
(com as travas); antes dele, nenhuma narração, asset ou crédito gasto.

## Quando

- Toda peça nova, com o dossiê (fase 01) e o estudo (fase 02) em dia.
- O usuário pediu mudança num roteiro já aprovado: volta aqui e para de novo.

## Entradas

- `motion/marca/dossie.md` e o estudo mais novo em `motion/concorrencia/`.
- O tema pedido pelo usuário, se houver: ele pula a escolha de pauta, nunca a checagem.
- `licoes-empresa.md` desta skill.

## Passos

### Pauta
Escolha o modo (`educativo`, `oferta`, `vsl`, `geral`; tabela em `copy/kishotenketsu.md`) e leia
o `copy/` dele: todo modo `copy/kishotenketsu.md`; `oferta`/`vsl` também `copy/oferta.md`
(briefing e 3 Big Ideas antes da pauta); anúncio, `copy/criativos-anuncio.md`. O modo vai para
o `fontes.md`.

1. Cruze as **lacunas** do estudo com a **força** do dossiê: prova [oficial] ou [medido]
   que só esta marca tem, produto foco, pergunta que os clientes repetem. Escreva 3
   candidatas, cada uma com a tese como **promessa** ("como saber se o seu X é Y", não
   "sobre X"), a lacuna que ocupa, o fato verificado que pode abrir o gancho e os produtos
   que a tese toca.
2. Escolha a de lacuna mais clara e prova mais forte. As outras duas vão à parada em uma
   linha cada.
3. **A pauta não acusa produto da empresa.** Para cada produto do dossiê, confira contra a
   tese os atributos que ela toca (origem, processo de fabricação, ingrediente,
   preparo, preço). Produto contradito: reformule ou troque a pauta. Dado de produto que
   diverge entre fontes é `não verificável`: pergunte ao cliente (AskUserQuestion, uma
   pergunta por vez) **antes de escolher a pauta**, e enquanto não houver resposta a tese
   não pode depender dele. Exemplo da peça de origem: a tese dependia de um ponto do processo
   de um produto da casa, e as fontes divergiam sobre esse ponto — o atributo era
   `não verificável`, então era pergunta, não premissa.

### Fatos
4. Para cada afirmação da fala, abra a fonte primária no Chrome e leia o número lá, não na
   matéria que cita. Monte a tabela fato → fonte com a régua da fase 01:

   | # | Trecho da fala | Fato | Fonte (link, arquivo ou pessoa + data) | Marca | Ressalva |
   |---|---|---|---|---|---|
   | 1 | "Até dois por cento… pode ser água" | até 2% de umidade adicionada permitida no produto X | norma do órgão regulador, nº e ano | [oficial] | — |

   (Linha **inventada**, só para mostrar o formato; na peça de origem o gancho citava uma
   instrução normativa federal.) Só [oficial] e [medido] viram fala.
   Ressalva que muda a frase entra na frase: na peça de origem, a entidade do setor tinha
   trocado o protocolo de avaliação em 2024, então a fala não podia citar a nota de corte
   antiga como "a regra oficial hoje". Sobre
   produto, só o que se lê no pixel da foto real ampliada, campo a campo; o que não se lê é
   `não verificável`, e o valor confirmado pelo usuário se soletra na fala.

### Estrutura
5. Escreva sobre o esqueleto da peça de origem, que segurou 79 s (segundos medidos nas palavras
   do áudio final dela, acelerado a 1,25×; a coluna % vale para qualquer velocidade):

   | Bloco | Na origem | % | Faz |
   |---|---|---|---|
   | Gancho de tensão | 0–5,6 s | 0–7 | fato **verificado** que choca e quebra expectativa; sem saudação nem contexto |
   | Virada de tom + promessa A | 5,7–10,7 s | 7–14 | uma interjeição curta que acalma troca para o tom de amigo e abre a promessa que o fim paga ("até o fim desse vídeo você vai saber se o seu…") |
   | Mito derrubado | 10,8–14,4 s | 14–18 | "X não é Y. É Z." e o mapa do meio ("são duas provas") |
   | Conteúdo | 14,4–49,4 s | 18–63 | blocos que ensinam algo aplicável; **um dado surpreendente a cada 8–10 s**; um pico de densidade (lista rápida) |
   | Virada: promessa B | 49,4–62,8 s | 63–80 | "o que quase ninguém conta" reabre a curiosidade, paga logo e entrega a **frase repetível** |
   | Marca | 62,8–71,7 s | 80–91 | a prova da empresa como consequência da virada ("por isso a gente…"); só fato marcado |
   | Fecho | 71,7–78,5 s | 91–100 | paga a promessa A com uma ação do espectador, mostra o produto real (foto da camada 1 ou 2 do dossiê) e pede o salvar quando a dica ficou útil |

   *(Hipótese a medir no piloto:)* em peça mais curta, gancho e virada de tom mantêm os segundos,
   o conteúdo cai para 2–3 dados, a virada fica em 60–65% da duração e marca e fecho somam
   ~20%. Este esqueleto é o do `educativo`; os outros modos usam o molde de
   `copy/kishotenketsu.md`, que traz também os moldes por duração. Acima de 3 min o reel perde
   a recomendação a não seguidores [oficial].
6. **Retenção**, conferida no texto (rode também o checklist "Prende até o fim" de
   `copy/kishotenketsu.md`):
   - duas promessas: escreva A e B em uma frase cada e aponte o segundo em que cada uma é
     paga; promessa sem segundo de pagamento é grito sem entrega;
   - um dado a cada 8–10 s do tempo que o espectador ouve: marque os dados no texto e meça
     os intervalos com a taxa do passo 11 que vale para a velocidade final da peça;
   - frase repetível: cabe numa respiração (até ~15 palavras), com antítese, sem jargão
     (exemplo **inventado**, 13 palavras, do tamanho da frase da peça de origem: "O forno pode
     estragar um pão bom… mas não salva um pão ruim.");
   - salvar no fim, ligado ao uso ("Salva esse vídeo pra próxima compra"); nunca "comenta X
     que eu te mando", que tira o post da recomendação.
7. **Gancho**: congelado a 0,5 s, o quadro planejado faz sentido sem som; depois dele o
   espectador consegue formular a pergunta que o vídeo responde (lacuna específica, nem
   vaga nem já respondida); é promessa, não assunto. Reprovam: "fica até o final", "você não
   vai acreditar", saudação, superlativo sem prêmio nomeado, escassez inventada.
8. **Tom e profundidade**: o tom é o que o usuário escolheu na fase 01, gravado no dossiê
   com a frase de exemplo; dossiê sem tom registrado, pergunte antes de escrever (as opções
   do passo 7 da fase 01). Cada bloco ensina algo que o espectador não sabia e consegue
   verificar; frase genérica sai.
   Leia o texto fingindo nunca ter ouvido falar da marca: pronome sem antecedente e nome
   próprio não apresentado são dívida de contexto, e se corrigem.

### Arquivos
9. Crie `motion/pecas/NN-<tema>/` (NN = próximo número em `motion/pecas/`; tema curto,
   minúsculo, sem acento) com:
   - `roteiro.txt` — **a fala exata**, uma frase ou respiro por linha, sem tag nem indicação
     de cena. Números, unidades e símbolos por extenso ("trezentos e cinquenta gramas", "um
     por cento", "vinte e oito reais", "e" no lugar de `&`); sigla escrita como se fala, ou
     evitada; nada de caixa alta para ênfase. É o texto que a fase 05 casa com o áudio:
     palavra diferente aqui quebra o alinhamento.
   - `roteiro-tags.txt` — o mesmo texto com as tags da ElevenLabs v4: **uma tag por
     trecho**, em inglês, entre colchetes, valendo até a próxima; reticências desaceleram;
     `[pause]` respira; a troca de registro é de propósito.

     ```text
     [low, tense, slow, almost a whisper, suspenseful]
     Até dois por cento do mel que você compra… pode ser água.
     [pause]
     [cold, deliberate] E tá tudo dentro da lei.
     [warm, friendly, smiling, relaxed, like talking to a friend]
     Ei, respira. Não precisa largar o mel.
     ```

     (Exemplo **inventado**, com a mesma forma da abertura da peça de origem: tensão sussurrada,
     pausa, frase fria, troca para o tom de amigo.)
   - `fontes.md` — pauta, tese e as duas alternativas; as promessas A e B com o segundo em
     que cada uma é paga; os blocos, cada um com a frase que o abre e o que mostra (foto
     real do banco, produto recortado, objetos a gerar); a tabela fato → fonte; a checagem
     de produto; depois da parada, o registro do OK. A frase que abre cada bloco ancora a
     trilha da fase 07 (a regra da frase está lá).
   - Oferta com variações: `roteiro-corpo.txt` e `gancho-K.txt` (laço em
     `copy/criativos-anuncio.md`); `fontes.md` recebe o briefing e as 3 Big Ideas.
10. Confira os dois arquivos com este trecho, salvo numa pasta temporária (roda igual no
    bash e no PowerShell e aceita arquivo com BOM):

    ```python
    import re, sys, unicodedata
    sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")  # legível em qualquer terminal
    ler = lambda f: unicodedata.normalize("NFC", open(f, encoding="utf-8-sig").read())  # aceita BOM
    fala, comtags = ler(sys.argv[1]), ler(sys.argv[2])
    sem_tags = lambda s: " ".join(re.sub(r"\[[^\]]*\]", "", s).split())
    RUIM = re.compile(
        r"[^\w\s.,!?¡¿;:…—–“”‘’'\"-]"  # nem letra, nem espaço, nem pontuação comum
        r"|[\d_ºª¹²³¼½¾]"               # algarismo, ordinal e fração: tudo por extenso
        r"|[A-ZÀ-Þ]{2,}")               # 2+ maiúsculas seguidas: sigla
    erros = [] if sem_tags(fala) == sem_tags(comtags) else ["DIFERENTE: os dois arquivos diferem fora das tags"]
    erros += [f"linha {n}: {' '.join(RUIM.findall(l))}" for n, l in enumerate(fala.splitlines(), 1) if RUIM.search(l)]
    print("\n".join(erros) or "OK")
    ```

    `python <pasta temporária>/conferir_roteiro.py motion/pecas/NN-<tema>/roteiro.txt motion/pecas/NN-<tema>/roteiro-tags.txt`
    imprime `OK` ou uma linha por problema; corrija até sair `OK` (símbolo derruba o
    alinhamento: o `alinhar_narracao.py` descarta token sem letra).
11. Estime a duração pela velocidade em que o espectador vai ouvir. Narração como sai da
    ElevenLabs: palavras ÷ 2,6 (a peça de origem: 259 palavras ≈ 99 s). Os segundos da tabela do passo 5
    são do áudio acelerado a 1,25×: para comparar com eles, palavras ÷ 3,3 (2,6 × 1,25) — ou
    compare pela coluna %, que não depende da velocidade. A peça só acelera se o usuário
    pedir ou o dossiê registrar velocidade da série (fase 04); sem isso, vale o 2,6. Voz nova:
    troque o 2,6 pelo medido na primeira narração dela.

### Parada
12. **PARADA.** Mostre no chat, sem storyboard: a pauta e o porquê (lacuna × força), as duas
    alternativas, o roteiro por bloco com o segundo estimado e o que cada bloco mostra, a
    tabela fato → fonte, a checagem de produto e a duração; em `oferta`/`vsl`, também as 3 Big
    Ideas (frase, ângulo, prova), a conformidade de `copy/oferta.md` e os ganchos. Pergunte com AskUserQuestion
    ("Aprovo este roteiro" · "Quero mudar", com o campo livre) e **pare**.
13. Mudança pedida: edite os três arquivos, rode o passo 10, mostre só o que mudou e
    pergunte de novo. OK explícito: registre em `fontes.md` ("aprovado por <pessoa>,
    AAAA-MM-DD") e siga para a fase 04. Depois disso, palavra mudada no roteiro volta a esta
    parada.

## Saídas

- Em `motion/pecas/NN-<tema>/`: `roteiro.txt`, `roteiro-tags.txt` e `fontes.md` (com o OK).

## Pronto quando

- O usuário aprovou esta versão, e o OK está em `fontes.md`.
- Todo fato da fala é [oficial] ou [medido] e tem fonte na tabela; nenhum produto é acusado.
- As duas promessas têm segundo de pagamento; há um dado a cada 8–10 s; existe a frase
  repetível; o fecho pede o salvar.
- O passo 10 imprime `OK`.

## Erros comuns

- Gancho com fato [terciário] ou sem fonte ("o mais premiado", "estudos mostram").
- Copy rasa: adjetivo no lugar de dado e mecanismo. O cliente percebe na primeira ouvida.
- Ler o número na matéria que cita, não na fonte primária.
- Tese que contradiz um produto da casa, notada só depois da narração.
- Algarismo, símbolo, sigla, caixa alta ou tag no `roteiro.txt`; palavra diferente entre os
  dois arquivos. O passo 10 pega todos.
- Assumir um tom padrão em vez do que o usuário escolheu.
- "Comenta X que eu te mando" no fecho.
- Baixar método pago de copy em site pirata: use a estrutura pública.
- Seguir para a narração porque "o roteiro está bom", sem o OK.
