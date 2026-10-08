# ElevenLabs — narração

Gera a narração na conta ElevenLabs do usuário, pelo Chrome. Regras comuns (login, inserir,
baixar, travas) em `chrome.md`; o texto com tags, a escolha da tomada e o `narracao.mp3` final
são da fase 04 (`fases/04-narracao.md`).

**Nenhuma tela da ElevenLabs foi vista pela sessão que escreveu esta página.** Todo passo
marcado *(a validar no piloto)* vem do conhecimento geral do site, não de medição. Na primeira
narração, confira cada um na tela, corrija esta página e registre como lição o que mudou (fase
10). Medido de verdade: o padrão do nome do arquivo baixado (arquivos reais de 2024 e 2026) e
as regras do texto (peça de origem).

## O modelo: "v4"

"v4" é como o usuário chama o modelo **mais expressivo**, o que interpreta **tags de áudio entre
colchetes** (`[warm, friendly]`, `[pause]`). Uma narração de out/2026 saiu com `_v4` no nome do
arquivo: o modelo existe com esse nome.

- **Rótulo com "v4" na tela → é ele**, mesmo com a v3 ao lado. Com v3 e v4 visíveis, escolher a
  v3 é erro.
- Sem "v4" na tela: o modelo que a tela apresenta como o de tags e expressividade; anote o
  rótulo exato na seção Voz do dossiê e registre como lição ("na tela, a v4 se chama …"). Nada
  corresponde com clareza → pare e pergunte.
- Escolhida a v4, o arquivo baixado termina em `_v4.mp3` (passo 8); `_v3` ou `_m2` = tomada do
  modelo errado, descartada.

Prova que não depende de rótulo: **se a voz LER a tag** ("warm, friendly…"), o modelo não é o
de tags. A fase 04 transcreve cada tomada; palavra de tag na transcrição = tomada descartada,
modelo trocado, geração refeita.

## Regras do texto (medidas na peça de origem)

- **Texto inteiro numa geração.** Gerar em partes muda a entonação entre os cortes.
- **3 tomadas** do mesmo texto, mesma voz, mesmos ajustes; quem escolhe é a fase 04.
- As tags são do roteiro, de propósito: não use recurso que "melhora" o texto ou acrescenta
  tags sozinho *(a validar no piloto: se existe um botão assim na tela)*.

## Biblioteca de vozes (fase 01, uma vez)

Para a escolha da voz da série *(a validar no piloto)*:

- `tabs_create_mcp` → `https://elevenlabs.io/app/voice-library`; ou o item de vozes do menu.
- Filtre pelo `idioma` de `identidade.json` (`pt-BR`: português, sotaque brasileiro) e leia
  nome e descrição dos cartões por `get_page_text`. A escolha das 3 candidatas é da fase 01.
- Deixe a aba aberta para o usuário ouvir as prévias — você não ouve; ele decide.
- "Adicionar às minhas vozes" muda a conta: só depois que o usuário escolher e aceitar.
- Grave o nome **exato** em `motion/marca/identidade.json` → `voz.nome` (link e data vão para o
  dossiê, pela fase 01).

## Passo a passo da narração

1. **Abrir.** `tabs_create_mcp` → `https://elevenlabs.io/app/speech-synthesis/text-to-speech`
   *(a validar no piloto)*.
   - Procure: caixa de texto grande, seletor de voz, seletor de modelo, botão de gerar.
   - Se falhar: tela de entrada → pare e peça login (`chrome.md` §1). URL mudou → entre pelo
     item "Text to Speech" do menu do painel; não adivinhe.
2. **Ler o saldo** antes de gerar: créditos restantes no menu da conta/plano ou em
   `https://elevenlabs.io/app/subscription` *(a validar no piloto)*.
   - Confira: saldo ≥ custo de 3 tomadas. O custo cresce com os caracteres do texto *(a validar
     no piloto: se as tags contam)*; se a tela mostrar estimativa perto do botão de gerar, use-a.
   - Se falhar: saldo menor, cota ou convite de upgrade → **pare e avise**. Não compre crédito,
     não troque de plano.
3. **Modelo.** Abra o seletor e escolha pela regra acima *(a validar no piloto)*.
   - Confira: o rótulo exibido depois da escolha (anote-o) e as tags que a tela diz aceitar —
     ajuda, dica ou exemplos do modelo — contra as do texto *(a validar no piloto)*.
   - Se falhar: o modelo não aparece para a conta → pare e pergunte (pode ser do plano). Não
     troque por outro modelo, mais barato ou sem tags, sem perguntar.
4. **Voz.** A de `motion/marca/identidade.json` → `voz.nome`, pelo nome exato (na 1ª peça quem
   escolhe é o usuário — fase 01) *(a validar no piloto: onde fica o seletor)*.
   - Confira: o nome da voz no seletor, depois de escolhida.
   - Se falhar: a voz não está nas vozes da conta → pare e pergunte; acrescentar voz da
     biblioteca é mudar a conta.
5. **Ajustes.** Os da seção Voz do dossiê; na 1ª peça, os padrões da tela, anotados lá
   *(a validar no piloto: no modelo de tags podem existir só modos prontos)*. Mudar ajuste é
   decisão do usuário.
6. **Colar o texto com tags.** Leia a caixa (pode vir com o texto da última geração), limpe e
   insira o texto inteiro por `insertText` (`chrome.md` §2).
   - Confira: comprimento = tamanho do texto menos o número de `\n` (`chrome.md` §2); as tags
     continuam entre colchetes (o editor pode transformá-las em etiquetas visuais — *a validar
     no piloto*); contador de caracteres dentro do limite da tela.
   - Se falhar: passou do limite → não divida o texto sozinho (muda a entonação): pare e
     pergunte. O editor recusou o `insertText` → screenshot, ache o campo real, tente de novo
     e registre a lição.
7. **Gerar** — botão de gerar *(a validar no piloto: o rótulo, e se uma geração já traz mais
   de uma variante; se trouxer, as variantes contam como tomadas)*.
   - Procure: player novo na página ou item novo no histórico.
   - Confira: duração plausível. Na peça de origem, a fala correu a ~2,6 palavras/s antes da
     aceleração (259 palavras em 78 s já a 1,25×).
   - Se falhar: erro de cota, convite de upgrade, captcha ou fila travada → pare e avise.

   Repita até ter 3 tomadas, sem mudar texto, voz nem ajustes entre elas.
8. **Baixar cada tomada** pelo botão de download do item *(a validar no piloto: no player ou
   no histórico; e se pede formato)*. Se a página tiver `<audio>` com `src` `blob:` ou da mesma
   origem, a receita do blob (`chatgpt.md`, passo 9, com o `<audio>` no lugar da `img`) baixa
   com o seu nome *(a validar no piloto)*. Senão o nome é do site; o padrão medido em 2026 é
   `ElevenLabs_<AAAA-MM-DD>T<HH_MM_SS>_<voz>_<tipo>_sp<NN>_s<NN>_sb<NN>_<modelo>.mp3`
   (v3 e v4; ex.: `…_pvc_sp100_s50_sb75_v4.mp3`):
   - a Multilingual v2 acrescenta estilo e reforço (`…_sb<NN>_se<NN>_b_m2.mp3`); a variante
     antiga, de 2024, não tinha `sp`;
   - o nome da voz traz espaço, vírgula e " - " (`<Nome> - <Descrição, com vírgulas>`): **ponha o
     caminho entre aspas** em todo comando;
   - o carimbo do nome é **UTC** (medido: nome `T04_07_40`, arquivo gravado às 01:08 locais,
     UTC−3) — não compare com o relógio local;
   - `pvc` = clone profissional, `pre` = voz pronta; `sp` = velocidade (100 = 1,0×), `s` =
     estabilidade, `sb` = similaridade; o sufixo é o modelo *(leitura dos códigos: a validar
     no piloto)*;
   - a mesma tomada baixada de novo vira `… (1).mp3` com o **mesmo** carimbo: cópia, não tomada.
   - Confira: um arquivo novo por tomada, carimbos diferentes, sufixo `_v4`, achado pela
     diferença da listagem (`chrome.md` §4, padrão `ElevenLabs_*`).
   - Se falhar: a 2ª tomada não chegou → abra a página (ou o histórico) numa aba nova e baixe
     dali.
9. **Mover** para `motion/pecas/<NN-tema>/public/fonte/narracao-tomada-<n>.mp3` (n = 1, 2, 3 na
   ordem de geração; origem entre aspas) e medir a duração com `ffprobe`
   (`motion/ferramentas/_ffmpeg.py` acha o binário).
   - Confira: 3 arquivos, durações próximas entre si e coerentes com o passo 7.
10. **Ler o saldo de novo** e anotar em `motion/pecas/<NN-tema>/fontes.md` (criado na fase 03)
    uma linha `narração: créditos gastos <N> (saldo <antes> → <depois>)`.
11. **Fechar a aba** e registrar como lição tudo o que a tela mostrou diferente desta página;
    o passo confirmado perde a marca de "a validar no piloto".
