# Lições universais

Erros que já custaram uma rodada de geração, um render ou uma reclamação do cliente, e que
valem para **qualquer empresa**: sites operados pelo Chrome, ferramentas (ffmpeg, whisper,
Remotion, Pillow), o motor de colagem, geração de imagem e método. **Lição não escrita se
repete**: a próxima sessão não tem a memória desta.

A versão 1.0.0 nasce do registro de lições do repositório de origem, o projeto de um cliente
onde a semente foi construída. Das 63 lições de lá ficou o que vale para qualquer empresa (algumas fundidas,
algumas em parte), reescrito sem nome de produto nem de conta e com os números medidos que
provam a regra. A origem de cada uma está na tabela do fim. **As strings e os números citados
nas lições vêm do repositório de origem e são evidência da regra, não fato a aplicar em outra
marca.**

**Formato:** `**TEMA-n.** **sintoma** → causa raiz → **regra**`, em 3 a 8 linhas, com o
número que prova a regra. Leitura que não foi medida vai marcada *(hipótese)*. Sem narrativa
de sessão: data só quando é parte da evidência.

**IDs:** `IMG` geração de imagem · `NAV` Chrome e sites · `VID` vídeo e Remotion · `AUD`
áudio e alinhamento · `MET` método. Um ID **definitivo** nunca muda nem é reaproveitado; o
provisório `TEMA-Pn` (abaixo) muda de propósito na promoção. Lição desmentida por outra ganha
a nota `→ ver TEMA-n` em vez de sumir.

## Manutenção

| A lição vale para… | Onde vai |
|---|---|
| só esta marca: fato de produto, conta, cliente, concorrente, preferência | `licoes-empresa.md` da cópia do repositório. Nunca sobe para a semente |
| qualquer empresa: site, ferramenta, motor, método | este arquivo, **na cópia do repositório**, no fim do tema, com ID provisório `TEMA-P1`, `TEMA-P2`… |

Na retrospectiva (`fases/10-retrospectiva.md`), as provisórias viram a lista de promoção. O
que o usuário aprovar sobe para o `licoes.md` da semente com o próximo número livre do tema
(o `TEMA-Pn` vira ID definitivo), e a `VERSAO` da semente sobe (patch). A universal que o
usuário recusar **sai** daqui e vai para `licoes-empresa.md`, marcada `[universal recusada em
AAAA-MM-DD]`: pode ser proposta de novo numa retrospectiva futura, e este arquivo volta a
espelhar a semente. O resto do `licoes-empresa.md` (lição da marca) nunca sobe.

O `plantar.py --atualizar` só acusa este arquivo como **conflito** quando a cópia **e** a
semente o mudaram: mantém o da cópia e grava o da semente ao lado
(`licoes.md.semente-<versão>`). Como, antes de atualizar, toda provisória já foi promovida ou
movida para `licoes-empresa.md`, no conflito fica a versão da semente: leia o `.semente-*`,
grave-o como `licoes.md` e apague-o. Se só a cópia mudou, ele mantém a versão da cópia, sem
conflito.

Lição que muda procedimento vira também regra na fase ou correção em `motion/` (na semente,
em `modelo/`): a lição guarda o porquê, a fase manda.

## Onde olhar

| Fase | Temas |
|---|---|
| 01 contexto · 02 concorrência | NAV · MET |
| 03 roteiro | MET |
| 04 narração | NAV · AUD |
| 05 tempo | AUD |
| 06 assets | IMG · NAV |
| 07 montagem | VID |
| 08 conferência | VID · AUD · MET |
| 09 publicação | NAV · MET |

---

## Geração de imagem — `IMG`

O que o modelo faz com prompt e referência (ChatGPT e Grok pelo navegador; Gemini e xAI por
API, quando dito) e o tratamento local do pixel.

**IMG-1.** **Logotipo descrito em texto saiu um sósia da marca** → o modelo desenha o que
entendeu, não copia: pode ficar bonito e vai estar errado → **no vídeo, logo e embalagem
entram só como pixel real (recorte com alfa), nunca redesenhados pelo modelo.** *Medição do
repositório de origem, para imagem estática, fora do vídeo e fora do procedimento da
semente:* a edição sobre a foto real (xAI, produto grande no quadro) preservou o rótulo; a
geração com DNA textual blindado (Gemini; cada string citada e soletrada) ainda errou ~1 em
3, e lá se geravam 2 ou 3 para escolher; só a composição local do recorte foi pixel-exata.

**IMG-2.** **Texto pequeno saiu reescrito, até numa troca de fundo que não pedia mudança no
rótulo** (uma palavra curta de letra miúda virou outra, sem sentido; com o objeto
pequeno, uma palavra de 9 letras em caixa alta saiu com 2 letras trocadas) → o modelo redesenha o quadro inteiro, inclusive em "edição", e a fidelidade escala com o
tamanho: 1 acerto em 3 no item de letra menor, 1 em 1 nos dois de letra maior; objeto abaixo
de ~30% da altura do quadro, erro de letra; letra abaixo de ~2% dela não sobrevive → **no
vídeo, a folha de assets se gera sem texto (fase 06); texto que precisa estar certo entra
por composição.** *Na origem, em imagem estática:* gerar 3 e conferir num recorte ampliado
da faixa de texto, porque em miniatura os erros passam. Só a altura não previu tudo (IMG-4).

**IMG-3.** **Nas faces de letra miúda só os acentos sumiram** (um agudo em dois itens, uma
cedilha no terceiro), com os 12 números das notas certos nos três, enquanto a face de letra
grande saiu íntegra → o modelo perde o
**acento** antes de errar o dígito → **na conferência, varra os acentos campo a campo**;
número batendo não prova texto íntegro. O inverso também acontece: uma palavra com um acento a
mais estava **impressa assim na arte real**, e a geração só copiou → antes de acusar a geração,
amplie a fonte. O alvo é fidelidade, não ortografia: não "conserte" o texto no prompt.

**IMG-4.** **Texto em arco quebrou nas duas rodadas, e soletrar trocou um erro por outro**
(o `V` corrigiu, o `S` quebrou), enquanto texto pequeno em **linha reta**, no mesmo quadro,
saiu íntegro → *(hipótese, não medida: o preditor pode ser a curvatura da linha de base, não
só a altura da letra)* → **texto curvo vai direto para composição local**: `crop` do pixel
real, casamento do nível de preto (deslocamento medido −2,7/−2,8/−1,7), máscara suave e
`assert` de **0 pixels alterados fora da caixa**. Resolveu em uma passada o que duas gerações
não resolveram.

**IMG-5.** **O carimbo de lote saiu com o mês 23 — e, em outra imagem, com uma data
plausível** → dado variável impresso fora da arte é redesenhado como qualquer texto →
**lote, fabricação, validade, QR e código de barras gerados nunca são confiáveis**: saem do
enquadramento ou entram por composição da foto real. Em peça de venda, isso é informação
regulatória falsa. Plausível é pior que absurdo: o absurdo você vê.

**IMG-6.** **"Mude só o selo", num follow-up no mesmo chat, trocou a cena inteira** → o
follow-up de edição regenera em vez de preservar: 79,2% dos pixels mudaram
(`np.abs(v1-v2).max(axis=2) > 12`) para um pedido que cobria ~1,1% do quadro, mesmo
nomeando a operação e listando o que manter (ChatGPT; a documentação da OpenAI prescreve
*small, single-change follow-ups*, e a medição desmente) → **imagem aprovada não se arrisca
em follow-up**: salve-a e corrija por composição local ou numa conversa nova.

**IMG-7.** **"A referência é só inspiração" — e numa troca de fundo o modelo segurou o
enquadramento** → a conclusão viera de um teste de **cena**, onde ele reconstrói; com o
prompt aberto em `EDIT THE PROVIDED PHOTOGRAPH` + `KEEP THE … PIXEL-FOR-PIXEL IDENTICAL`,
3 de 3 mantiveram posição, escala, vincos e brilho num blend a 50% (Gemini por API), e o
texto pequeno foi reescrito na mesma operação (IMG-2) → **abra o prompt nomeando a operação
e listando o que não muda**: segura o enquadramento, não a letra miúda. *(Hipótese: vale para
a primeira mensagem do ChatGPT com a foto anexada, como prescreve a documentação da OpenAI;
a medição foi no Gemini.)* Follow-up regenera o quadro (IMG-6).

**IMG-8.** **Uma serra de topo plano saiu como pico alpino nos 3 modelos testados** → a
descrição escrita dizia *"jagged peaks"* → **o modelo é obediente: erra exatamente onde a
descrição erra.** Quando todos os modelos erram igual, suspeite do texto antes do modelo e
confira cada adjetivo do prompt contra a foto real.

**IMG-9.** **Anexada inteira, a foto crua ensinou mais sobre a mesa do que sobre o
produto** → o assunto ocupava ~3% de uma foto de 3072×4096; o resto era mesa e parede →
**recorte antes de anexar.** Uma folha com as vistas reais lado a lado (dois `crop` colados
sobre branco, nada gerado) serve de referência, e o prompt **nega o layout dela** (*"its
two-up split layout and its white border must not appear"*); senão o modelo copia a folha de
contato em vez do objeto.

**IMG-10.** **Uma imagem da série saiu sobre madeira pintada de azul e quebrou a coesão** →
o prompt não proibia superfície pintada → **em série, descreva o cenário compartilhado
explicitamente em cada prompt e negue as variações** que você não quer.

**IMG-11.** **O produto saiu gigante na cena, com o rótulo perfeito** → o prompt pedia
câmera na altura do joelho, nivelada, e o topo do pacote acima das fileiras da plantação; o
horizonte fica na altura da câmera, então, com a lente a ~50 cm, um pacote de ~23 cm só passa
das fileiras se tiver mais de meio metro, e o modelo desenhou ~1 m → **faça a conta da altura
da câmera antes de enviar** (objeto acima do horizonte pede lente quase no chão) **e ponha
uma régua de escala** com o tamanho escrito: uma folha caída (~12 cm) ao lado do pacote de
23 cm. O modelo não sabe o tamanho do produto; a proporção que você não escreveu ele resolve
aumentando o produto.

**IMG-12.** **O objeto reiluminado ficou incoerente com a cena** → a luz foi assumida pela
esquerda e o modelo a renderizou pela direita; direção de luz ditada no prompt é ignorada →
**gere, meça a direção na imagem** (especular de objeto cilíndrico, sentido das sombras)
**e reilumine a partir do medido.** A cena herda a luz da foto-fonte, ou denuncia a montagem
mesmo com o logo perfeito; e a luz do lugar real é dado medido nas fotos reais dele, não
escolha estética.

**IMG-13.** **Cena gerada com desfoque de câmera grande não passa por foto de celular** →
profundidade de campo rasa não se desfaz em pós (tom, ruído, halo e artefato de JPEG se
adicionam depois; foco, não) → **bloco anti-bokeh obrigatório no prompt**, descrevendo a
física: sensor pequeno (1/1,7") a f/1,8 tem profundidade de campo enorme, tudo igualmente
nítido, a distância suaviza por névoa e nunca por desfoque, cantos moles de lente larga
barata.

**IMG-14.** **Cena "arrumada" denuncia render** (derramado composto, objeto atravessado por
cima, mesa posta) → pedir bonito devolve render — comida bonita volta como render de comida —
e objeto que não existe naquele lugar denuncia (utensílio de cozinha numa lavoura) →
**liste os objetos que as fotos reais do lugar mostram e proíba o resto; comida, peça meio
comida** (mordida, farelo, dourado desigual, crosta fosca). O modelo tem viés de deixar o
produto **em pé**: "deitado no chão" costuma ser ignorado.

**IMG-15.** **O passe de calibração "cara de celular" piorou as métricas**: duas calibrações
completas saíram net-negativas, corrigindo uma métrica e estragando três → a correção era
unidirecional e dupla na cor (R para cima *e* B para baixo) → **pós mínimo, só saturação;
correção com sinal, num canal só, sem tocar em métrica dentro da tolerância.** O alvo é o
perfil medido nas fotos de celular da própria empresa, não gosto. E a métrica mede
assinatura de dispositivo, não plausibilidade: comida de formato errado bem calibrada é pior
que comida crível com duas métricas fora.

**IMG-16.** **Recortar os assets da colagem num serviço online não serviu** → o plano grátis
entrega prévia de baixa resolução, o upload não é operável pelo Chrome (NAV-7) e o serviço
anunciava que sai do ar → **peça ao ChatGPT a folha já sobre branco liso #FFFFFF, objetos
afastados, e recorte local** (`recortar_folha.py`: limiar de distância ao branco + componente
conexo, resolução cheia). Medido: objeto branco sobre branco perde metade da borda no limiar
→ casco convexo (`--convexo`); sombra suave entra com limiar baixo e vira mancha de retícula
→ suba o limiar (22 → 55).

**IMG-17.** **A limpeza de uma marca d'água comeu o texto pequeno** (`FABRICADO` virou
`FA8R CADO`) → a marca era vermelho clareado e o texto, creme com anti-aliasing: um pixel de
texto a 50% de cobertura tem exatamente a cor de um pixel da marca, os dois caem na mesma
reta de cor, e nenhum limiar por pixel separa os dois → **limiar conservador (tira a marca
fraca, preserva todo o texto) e preencha à parte só regiões provadas vazias**: conte os
pixels de conteúdo com `assert` antes de pintar; nunca preencha um retângulo no olho.

**IMG-18.** **A arte refeita vazou para fora da embalagem** (foto a 100% da tela, texto por
cima das marcas de corte) → o arquivo de produção foi tratado como tela livre, e ele tem
sangria, marcas de corte, abas de solda e margem de segurança → **antes de recompor arte de
produção, meça os limites no próprio pixel** (painel útil, margem, região editável, blocos a
preservar) **e valide no fim contando os pixels alterados fora do painel: tem que dar 0.**

**IMG-19.** **Ruído aditivo virou névoa leitosa** → `ImageChops.subtract` satura em 0, e
somar 128 depois levanta a imagem inteira → **para ruído centrado em 128, use
`ImageChops.add(imagem, ruido, offset=-128)`.**

**IMG-20.** **O banco de imagens da empresa veio misturado**: duas
`Gemini_Generated_Image_*.jpg` dentro das pastas de produto, e 21 de 40 imagens raspadas do
Instagram em 1281×1611, acima de um mínimo de 1200 px → resolução não é procedência, e nada
no código impede foto de terceiro de virar pixel se alguém a mover de pasta → **separe o
banco por permissão, não por assunto**: própria verificada (EXIF de câmera e GPS) · própria
sem prova · terceiro (IMG-21) · sintética e baixa resolução = quarentena. Sintética em
referência de estilo ensina o look sintético; mudar de camada é decisão humana.

**IMG-21.** **Entre as imagens de terceiros do banco, uma tinha marca d'água e outra o rosto
identificável de quem não autorizou** → raspagem e mood board trazem junto o que a marca não
tem direito de usar → **terceiro nunca vira pixel do vídeo; sobe ao ChatGPT só como
referência de estilo, luz e paleta**, com o prompt proibindo copiar composição, objeto, texto
e logo. **Rosto identificável, logo ou embalagem de outra marca e marca d'água viram só
descritor em texto.** A regra do repositório vence: onde ele proíbe guidance de terceiro, a
cópia obedece.

---

## Chrome e sites — `NAV`

Operar sites pelo Claude in Chrome, na sessão logada do usuário. A mecânica de cada site fica
em `navegador/`; aqui fica o porquê.

**NAV-1.** **A ferramenta respondeu "digitado" e o campo não mudou** → a janela do Chrome com
o grupo de abas do agente estava atrás de outra (`document.visibilityState === 'hidden'`):
clique e digitação são reportados como feitos e não chegam, o screenshot estoura e um
acordeão aberto por JS fica com altura 0; fechar a última aba do grupo recria o grupo numa
janela nova, oculta de novo → **antes de agir por clique, digitação ou screenshot, leia
`visibilityState`; se `hidden`, peça ao usuário para deixar a janela visível e reuse a aba
do grupo.** Quem prova que o texto entrou é o `value` do campo. Aba de fundo: rota JS, NAV-2.

**NAV-2.** **Em aba de fundo, o Enviar não enviou** → ali o `.click()` por JS no botão não
envia, e o clique (por ref ou coordenada) e o screenshot estouram o limite de 45 s → **na aba
da frente, clique na coordenada lida no screenshot (NAV-3); em aba de fundo, insira o texto
com `execCommand('insertText')`, espere ~1 s e envie com
`el.closest('form').requestSubmit()`** — sem a espera o React ainda não registrou o texto e o
envio sai vazio. Confirme pelo efeito: a URL mudou (`/c/<id>` no ChatGPT) e o campo zerou.

**NAV-3.** **Dois cliques na coordenada do botão, e nada** — o `getBoundingClientRect()`
apontava o botão e o `elementFromPoint` confirmava o alvo → depois de um `scrollIntoView`, o
rect reportava certo e o clique real não alcançava → **se o clique por coordenada falha duas
vezes num alvo que o DOM confirma, role a seção, tire screenshot e clique na coordenada lida
no pixel.** O DOM descreve, o screenshot mostra. No ChatGPT, na aba da frente, a coordenada
lida no screenshot enviou na primeira, onde o clique por ref estourou; em aba de fundo, NAV-2.

**NAV-4.** **Gastavam-se 10 s de espera e um screenshot por seção porque "só clique real
funciona"** → medido: `.click()` por JS abre acordeão e exclui item na hora; o que exigiu
clique real foi o **Confirmar** → **JS funciona em controle local de estado (acordeão,
excluir, checkbox) e falha no que submete.** Dois corolários: os `aria-label` mudam a cada
re-render, então uma lista de botões guardada aponta para refs mortos; e um laço síncrono
clica o **mesmo** botão N vezes, porque o React só re-renderiza no fim do tick → uma ação
por chamada, relendo o DOM.

**NAV-5.** **Arrastar para reordenar não respondeu ao mouse** → os itens eram
`draggable="true"` (HTML5 nativo), e o arrasto da ferramenta não dispara `dragstart`/`drop`;
disparar os eventos por JS com um `DataTransfer` compartilhado funcionou, mas a interface
(Vue) só re-renderizou no evento de teclado seguinte, e a primeira tentativa pareceu falhar →
**dispare os eventos por JS e aperte uma tecla neutra (`ArrowLeft`) em seguida; confira a
ordem relendo os `src`, não pela tela.**

**NAV-6.** **Três imagens num só upload chegaram na ordem inversa** (`.6, .8, .7` virou
`.7, .8, .6`: a capa virou o detalhe), e em miniatura de 120 px a inversão não salta aos
olhos → a ordem do upload múltiplo depende do site (no Grok veio na ordem enviada) →
**onde a ordem importa, suba uma imagem por chamada e confira a ordem no DOM antes de
confirmar** — e antes de chamá-las de FIRST/SECOND no prompt.

**NAV-7.** **O upload de um site não era operável** → a página só cria o `input[type=file]`
no clique, e o clique abre o seletor de arquivos nativo do sistema, que o Claude in Chrome não
opera → **`file_upload` precisa de um `input[type=file]` já presente no DOM; se o site só o
cria no clique, não clique: procure outra rota** (para recorte de asset, IMG-16).

**NAV-8.** **Um clique no canto apagou um prompt de 3.840 caracteres já inserido** → o X do
overlay de imagem que abre depois do upload fica sobre o botão de chat temporário; com o
overlay já fechado, o clique ligou o modo temporário, que recarrega a página e leva anexos e
texto junto (ChatGPT) → **feche overlay com `Escape`, nunca com clique no canto.** Num app que
troca o que está sob o cursor, tecla é mais segura que coordenada.

**NAV-9.** **Agentes em abas separadas abriram a aba já com o prompt e os anexos de outro
agente** (3 de 4) → o ChatGPT compartilha o rascunho e os anexos do composer entre abas da
mesma conta → **leia o composer (`.ProseMirror`) e a lista de anexos imediatamente antes de
cada envio, e limpe com selectAll + delete.** Aba separada não é sessão separada: sem essa
leitura, o envio gera a imagem do colega com status de sucesso.

**NAV-10.** **Pegar "o download mais recente" salvou a imagem errada duas vezes, sem erro, e
quase salvou outras duas** → erros: o padrão de nome velho casou com downloads antigos (o
nome já teve três padrões: inglês, português e o título do chat), e um Baixar que não
disparou deixou o anterior como o mais novo, dentro da janela de 180 s; quase-erros: um PNG
de dias antes, barrado só pela trava de idade, e outra sessão gravando na mesma pasta 5 s
antes → **dê o nome você mesmo (`fetch(img.src)` → blob → `<a download="nome.png">` clicado
por JS) e pegue o arquivo por esse nome**: cinco folhas em paralelo, nenhuma trocada. Se o
site nomeia, use o id dele, relido na hora de baixar (pode mudar quando a geração termina).

**NAV-11.** **A segunda leva de downloads, nas mesmas abas, não chegou e nada reclamou** →
o Chrome libera o primeiro download automático de cada aba e segura o segundo esperando
permissão → **um download por aba: para baixar de novo, abra a página (no ChatGPT,
`/c/<id>`) numa aba nova.** Mandar o blob para um servidor local por `fetch` é barrado pela
CSP do site — e CSP não se contorna.

**NAV-12.** **Um site pareceu bloqueado (403) e depois liberado (200), e o 200 era o muro
anti-bot** → o 403 era do User-Agent da ferramenta de fetch; com UA de Chrome veio 200, mas a
página trazia o marcador do muro (`suspicious-traffic-frontend`): conteúdo falso com status
de sucesso → **teste o host com UA de navegador antes de declarar bloqueio, e confira o
conteúdo, não o código.** Dado de site logado se lê pelo Chrome do usuário; contornar
detecção de bot está fora de escopo.

**NAV-13.** **Imagem pré-formatada para uma plataforma foi desfeita por outra** → uma loja
serve o arquivo como ele sobe (quadrar em 1:1 esticando a coluna da borda,
`crop(0,0,1,H).resize(pad,H)`, preserva o gradiente do fundo sem emenda); um marketplace fez
trim da margem branca, guardou 1031×1200 e gerou as próprias variantes quadradas →
**receita de formato não é portátil entre plataformas: suba uma e meça o que ela guardou**
(baixe a versão cheia que ficou no ar) antes de pré-formatar o resto.

**NAV-14.** **Raspagem pesada rende bloqueio temporário, e quem leva é a conta logada**
*(aviso do repositório de origem, não medido)* → o site pune a conta que navega em volume de
robô, não a ferramenta → **na sessão logada do usuário, navegue pouco: poucos perfis, poucos
itens por perfil, com pausa entre aberturas; volume pede conta secundária, decidida pelo
usuário.** Bloqueio não se contorna.

---

## Vídeo e Remotion — `VID`

Sondagem de mídia, ffmpeg, render e a composição de colagem em `motion/remotion`.

**VID-1.** **Vídeo renderizou deitado; foto entrou com a proporção trocada** → leu-se a
dimensão gravada: o vídeo era 1024×576 com `displaymatrix rotation -90` (exibe 576×1024); a
foto, 4096×2304 com EXIF `Orientation 6` (razão de exibição 0,5625, não 1,7778), e a sondagem
só lia o metadado de vídeo → **a dimensão de exibição sai do metadado de rotação, que tem
dois nomes: `side_data_list.rotation` (contêiner de vídeo) e EXIF `Orientation` (JPEG/TIFF).**
`ffprobe -show_frames -read_intervals "%+#1"` traz `frames[0].tags.Orientation` com espaços
(`"    6"`): converta com `trim`; no Python, `ImageOps.exif_transpose`. Numa base
verificada, 12 de 12 packshots e 8 de 26 fotos de campo eram `Orientation 6`.

**VID-2.** **Toda foto parada voltou do ffprobe com 25 fps e 0,04 s de duração** → o demuxer
`image2` inventa esses números para JPEG e PNG → **`format_name === 'image2'` é o sinal de
imagem parada; ali fps e duração são `null`, nunca 25 e 0,04** (MET-12).

**VID-3.** **O render "a 360 px" saiu 360×638 e ninguém reclamou** → `--scale=0.333` dá
359,64×639,36; o still aceita lado ímpar (360×639), mas o h264 exige lado par e o Remotion
desce para 638 em silêncio, com exit 0: 360/638 = 0,5643 contra 0,5625 de 9:16, esticado
0,3% sem aviso → **nunca digite a escala: derive-a da largura alvo (`alvo / largura`) e
recuse lado ímpar antes do render.**

**VID-4.** **O filtro `fps=2,scale=180:-1,tile=6x8` não montou a folha de contato** → o
ffmpeg que vem dentro do Remotion (`node_modules/@remotion/compositor-*/`) é build mínima,
com ~50 filtros e sem `fps` nem `tile`; o erro de `fps=2` é `No option name near '2'`, que
parece sintaxe, e só `fps=fps=2` revelou `No such filter` → **antes de depurar a sintaxe de
um filtro, confirme que ele existe naquela build (`ffmpeg -filters`).** Amostre com `-r`
(opção de saída, não filtro) e monte o mosaico fora do ffmpeg (Node com `pngjs`, ou Python).

**VID-5.** **O render "parado" continuou rodando** (CPU cheia, arquivo de saída travado) →
no Windows, parar a tarefa encerra o shell, mas o `node` do Remotion e os
`chrome-headless-shell` filhos seguem renderizando → **ache o processo pela linha de comando
(que cita a composição) e derrube a árvore dele: `taskkill /PID <pid> /T /F`.** Nunca mate
`chrome-headless-shell` às cegas: outra sessão pode estar renderizando. *(Hipótese para
macOS/Linux: mesmo princípio, achar pela linha de comando e matar o grupo; não medido.)*

**VID-6.** **Tempos digitados à mão teriam ficado para trás** → quando o realinhamento moveu
as palavras 0,7 s, 60 segundos escritos nas cenas e nos sons sairiam do lugar → **nenhum
tempo de cena ou de som é digitado**: tudo lê a palavra (`em(faixa, 'palavra')`,
`depois(faixa)`) ou a troca (`TROCA`, `CENA_INICIO`); desvio relativo pode
(`inicio - 0.13`), número absoluto não; `FIM` é derivado da última palavra.

**VID-7.** **O marcador terminava de escrever depois da fala, e um nem terminava** → escrita
a 2 quadros por letra, fixos: uma frase acabou 0,4 s depois da voz; outra esperou a câmera
pousar (+14 quadros) e o fecho entrou antes da última letra → **a velocidade da escrita sai
da duração da fala (`dur={fala(faixa)}`), e o movimento de câmera que um texto espera
acontece DURANTE a frase**, não antes do texto.

**VID-8.** **O chicote mostrava uma faixa preta de até meia tela, nas 10 trocas** → a cena
que saía andava 520 px sozinha e revelava o fundo da raiz; com borrão, parece falha de
render → **chicote é a imagem que sai e a que entra COLADAS**, andando uma tela inteira sob
borrão direcional, cada uma congelada no seu último/primeiro quadro durante a janela (12
quadros). O defeito só aparece DENTRO da janela: confira com stills lá dentro.

**VID-9.** **Texto de colagem cortado na borda só em alguns quadros** → a câmera 2.5D anda
até ~120 px e amplia até ~1,16×; texto em x=250 saía no meio da cena, e o still do começo não
mostrava → **com câmera em movimento, tipografia em x ≈ 140–940 em repouso** (quadro de
1080), e a conferência tira still no MEIO e no FIM de cada movimento, não só na entrada do
texto.

**VID-10.** **A etiqueta tapou o logotipo da embalagem** → foi posicionada 160 px acima do
selo sem medir o recorte: o PNG tem margem transparente e o produto ocupa só a faixa
0,17–0,75 da altura → **antes de pôr qualquer coisa relativa a um recorte, meça o bbox do
alfa**; texto de colagem nunca cobre logotipo nem selo.

**VID-11.** **Todo objeto da colagem "respirava"** → cada uma das 3 variantes de borda (o
boil) era cortada pelo próprio bbox; os tamanhos diferiam até 2,4%, e a variante alterna a
cada 3 quadros → **as variantes de uma peça são cortadas pela UNIÃO dos bboxes**
(`recortar_folha.py` faz isso; o teste dele exige as 3 do mesmo tamanho).

**VID-12.** **A pílula de legenda quebrou a frase no artigo** ("FIM DESSE / VÍDEO") →
cortar em "3 palavras" é contar, não ler → **orçamento de 16 caracteres e 4 palavras,
partição equilibrada por programação dinâmica e custo alto para bloco que termina em
palavra fraca** (artigo, preposição, `desse`, `seu`, `nosso`), **para bloco-relâmpago
(< 0,3 s na tela) e para bloco que atravessa respiro.** Legenda é leitura; o portão é teste
automatizado, não o olho.

**VID-13.** **Texto sobreposto à foto sumiu: contraste 4,42:1 · 3,43:1 · 1,09:1** → o bloco
atravessava fundo do preto (o produto) ao branco (o ciclorama), e nenhuma cor fixa sobrevive
a essa amplitude; o remédio padrão, scrim escuro, esbarrava numa regra da marca (nada por
cima da embalagem) → **quando a legibilidade esbarra numa regra de marca, mude a geometria,
não a regra**: faixa sólida própria para o texto, contraste constante no molde (11,59:1),
produto intocado. Meça o contraste antes de escolher a cor.

---

## Áudio e alinhamento — `AUD`

Narração, transcrição, tempo das palavras e loudness.

**AUD-1.** **O whisper estragou os acentos da legenda e adiantou palavras para dentro da
pausa** → com `-ml 1` o whisper.cpp parte a palavra em tokens e corta o UTF-8 no meio
(`café` → `caf\ufffd`), e número falado vira um token só ("trezentos e cinquenta" = `350`)
→ **o texto vem do roteiro, o tempo vem do alinhador (AUD-2)**, casados por sequência de
letras sem acento (`alinhar_narracao.py`, que passa o algarismo para `por_extenso`); palavra
do roteiro que cai num token só se espalha pela duração dele. Refine pelo silêncio só quando
o início cai DENTRO dele: com margem de 0,05 s, uma palavra 0,02 s antes da pausa foi puxada
para depois dela.

**AUD-2.** **"Erro de sincronia de voz e legenda" que o cliente viu e o teste não pegou** → o
whisper deslizou 0,5–0,7 s por ~5 s sem cair em silêncio nenhum; o alinhamento forçado CTC
(`torchaudio` MMS_FA) nunca perde a região, mas atrasa ~0,1 s dentro da frase e, depois de
pausa, às vezes a frase inteira em 0,2–0,4 s → **nenhum alinhador sozinho é confiável: funda
e meça** (`alinhar_forcado.py`, conferido no envelope com `conferir_alinhamento.py`). Contra
109 ataques lidos à mão: whisper mediana 0,10 s / máx. 0,76; CTC 0,09 / 0,39; fusão **0,02 /
0,15**. Voz ou velocidade nova: leia o ataque de cada frase; áudio acelerado é áudio novo.

**AUD-3.** **O normalizador recusou o render final por 0,08 dB** → a mixagem saiu com pico de
+0,05 dBTP (efeitos percussivos empilhados); o `loudnorm` limitou para −1 dBTP no PCM, e o
encode AAC, depois do limitador, devolveu o pico a −0,62 dBTP no MP4: fora da folga de 0,3 dB
do verificador (limite −0,7 dBTP) → **separe o teto PEDIDO (0,6 dB abaixo do alvo) do
VERIFICADO (medido no MP4 escrito) e, se passar, refaça pedindo mais baixo pelo excesso
medido**; nunca afrouxe a folga. Medido: `TP=-1.6` em duas passadas deu −14,20 LUFS e
−1,17 dBTP; rajadas de ruído a 0 dBFS pediram 2,3 dB e passaram na segunda tentativa.

---

## Método — `MET`

Como saber que algo funcionou. Vale para qualquer ferramenta, site ou modelo.

**MET-1.** **Sucesso reportado sem efeito nenhum** → uma API de edição recebeu a imagem num
campo de nome errado (quatro nomes plausíveis testados) e devolveu 200 gerando só do texto:
duas rodadas perdidas; página devolve 200 com muro anti-bot (NAV-12); o Remotion encolhe a
altura com exit 0 (VID-3); a ferramenta diz "digitado" e o campo não mudou (NAV-1) → **HTTP
200, exit 0 e "feito" não provam que o parâmetro funcionou: confira o efeito** — a imagem
mudou, o `value` do campo, o nome e o carimbo do arquivo, a dimensão da saída.

**MET-2.** **Todos os testes de sondagem voltaram 422 de uma vez** → um único valor fora do
enum (uma proporção que aquele serviço não tem) envenenou todas as requisições → **valide
cada parâmetro sozinho antes de varrer combinações; quando tudo falha junto, suspeite do que
é comum.** Erro é evidência barata: 400 e 422 não geram, logo não custam, e a mensagem
costuma enumerar os valores válidos — sonde com erro antes de gastar.

**MET-3.** **Concluiu-se que "o modelo não sabe escrever marca"** → o input estava errado: a
referência mandada era o **verso** da embalagem (QR, tabela), e o prompt não descrevia a
arte → **antes de concluir que uma ferramenta não sabe, confira se o input estava certo**: a
face certa (mostre a frente e descreva a identidade elemento por elemento), o modo certo
(IMG-7), o binário certo (VID-4).

**MET-4.** **Três medições deram número para a coisa errada**: "ruído" numa textura de
madeira, "sombra" em cima do próprio objeto, altura de letra com o anel do selo dentro → a
caixa amostrada pegava outra coisa além do alvo, e ninguém olhou o recorte antes de ler o
número → **valide a região amostrada antes de acreditar no número**: olhe o recorte que você
mediu. Número que não mede o que você diz é jogado fora, não "aproximadamente certo".

**MET-5.** **Um portão reprovou todos os títulos por "transbordo"** →
`scrollHeight > clientHeight` com `overflow: visible` mede a folga do glifo (`h1` de 92 px com
`line-height: 1.03`: 198 contra 190) e nada é cortado → **alarme que acende em tudo: imprima o
número cru antes de acreditar**; a condição exige `overflow` diferente de `visible`, e o bloco
de texto ganha altura fixa com `overflow: hidden` para o portão ter o que medir. E portão é
necessário, não suficiente: com os três portões verdes, o olho ainda pegou dois defeitos de
composição — olhe a folha de contato antes de entregar.

**MET-6.** **Valores da referência saíram inventados** (`70/80/80/40` onde a embalagem diz
`7,0/10/10/6,0`), e um agente aprovou um campo que a referência não deixava ler → na foto de
591×1280 não dá para ler (o 10 some em barra cheia, preto sobre preto): o prompt mandava
"copie da foto" e o modelo chutou; o agente converteu "não consigo ler" em "confere" → **só
marque como conferido o que a referência permite ler; ilegível é `não verificável`**:
pergunte o valor e soletre no prompt. "Copie da foto" sem foto legível é convite ao chute.

**MET-7.** **Um gabarito de conferência tinha 2 strings erradas e 4 faltando** (entre as
faltantes, justamente a que quebrava na geração), e outro descrevia "contorno retangular"
onde os três itens usam cantos, com a geração certa e o gabarito errado → os dois foram
escritos sem olhar o pixel: um de memória, o outro por analogia entre itens irmãos →
**gabarito não conferido no pixel é lembrança com cara de dado; quando a geração diverge
dele, o gabarito também é suspeito** — confira os dois contra o pixel antes de decidir quem
errou.

**MET-8.** **Um subagente discordou de um dado e estava certo; outros dois reportaram erros
que não existiam** (acento faltando, objeto encostando, objeto de cabeça para baixo) → relato
é a leitura de outro agente, com ou sem ampliação, e nos três casos só a ampliação decidiu →
**relato de agente é pista, nunca veredito, nos dois sentidos**: confira você mesmo no pixel.
Aceitar a leitura do outro sem olhar é a mesma falha, terceirizada.

**MET-9.** **Quase se descreveu a cor do produto pela ilustração da embalagem** → a arte
desenha o item numa cor; o item real, ampliado 3×, é de outra cor e metálico; num item irmão a arte batia
com o real, e esse acerto quase virou regra → **ilustração é desenho, não medição**: atributo
físico de um item vem da foto do item; sem foto, é `não verificável` e vira pergunta ao
cliente.

**MET-10.** **Quase se "corrigiu" uma foto real para encostar num alvo de saturação 70** → o
alvo era a média de duas populações: fotos de campo, mediana 85,9 (66,8–105,8), e packshots,
mediana 59,1 (17,9–99,6); o mesmo com área estourada, 0,26% no campo e 0,001% no packshot →
**compare cena com cena e packshot com packshot; antes de corrigir uma métrica, meça o grupo
de referência certo.** O alvo também depende da luz: o ponto preto medido veio de sol forte,
e em luz difusa sombra levantada é o comportamento certo. E foto real nunca se calibra contra
o alvo: ela é a fonte da medida.

**MET-11.** **Documentou-se uma garantia que não existia**: "o Instagram entrega no máximo
1080 px, então nada raspado passa como referência" — e ele entregava 1281 px → o número foi
lido errado no próprio contador (era a altura) e virou regra sem conferência no arquivo →
**não transforme em garantia escrita o que você não mediu no arquivo real**; proteção que
depende de um número do fornecedor é acidente. Idem para campo declarado à mão: uma razão de
exibição anotada 1,3333 media 0,75 — campo declarado existe para ser conferido.

**MET-12.** **Um `0` escondeu um defeito** → a sondagem devolvia `rotacao: 0` tanto quando
mediu zero quanto quando não achou metadado, e inventava fps e duração para foto parada →
**"não achei" e "medi zero" são fatos diferentes, e um deles é alarme**: o tipo diz a fonte
(`{fonte: 'displaymatrix' | 'exif' | 'nenhuma', graus}`), e ausência vira `null`, não número
plausível — o chamador é obrigado a tratar.

**MET-13.** **Um seletor de arquivo por nome achou o arquivo errado em vez de falhar** → o
padrão não casou com o download novo, casou com downloads antigos, e "o mais recente deles"
tinha as mesmas dimensões, então a conferência por tamanho não denunciou → **um seletor que
encontra *algo* é pior que um que falha.** Prefira o que falha alto (o nome que você deu, o id
do fornecedor) e confira identidade (nome, carimbo de hora), não forma (dimensões). Nome de
arquivo é seletor que o fornecedor troca sem avisar (NAV-10).

**MET-14.** **Uma imagem com data impossível estava na fila de publicação, apesar de uma
regra escrita proibir** → o pedido era "as laterais", e as seis foram tratadas como um bloco;
abertas uma a uma, eram três coisas diferentes, e o mesmo número de arquivo mostrava faces
diferentes conforme o item, porque a geração não seguiu a nomenclatura → **conjunto não é
unidade: antes de publicar, abra cada peça.** Reduza o escopo dizendo por quê: escopo menor é
decisão do cliente; publicar dado falso não é opção que se possa escolher por ele.

**MET-15.** **Uma linha de LEIA-ME de pasta virou regra de arquitetura** ("X nunca nasce
aqui" lido como "X nunca entra em geração"), contra evidência já no disco: 96 peças
aprovadas feitas exatamente assim → a frase foi lida fora do escopo do arquivo: o LEIA-ME
descrevia a pasta, não o pipeline → **antes de transformar uma frase de documento em
restrição, confira de que escopo ele fala.**

**MET-16.** **O commit de outra sessão caiu na branch desta** → duas sessões do Claude Code
no mesmo diretório git, e trocar de branch troca a da outra debaixo dela → **antes de
`git checkout`, veja se há outra sessão ativa; para trabalhar em paralelo,
`git worktree add ../<repo>-<assunto> -b <branch>`.** Arquivo gitignored (biblioteca de PNG,
`public/` e `saida/` das peças) vive só no diretório principal e não viaja para o worktree:
script que o lê por caminho relativo roda de lá. Commit só dos seus arquivos.

**MET-17.** **Uma ferramenta instalada no venv sumiu depois de `uv sync`** → o sync remove
tudo que não está declarado no `pyproject.toml`, e a ferramenta tinha sido instalada à mão
→ **depois de qualquer sync declarativo, confira as ferramentas que vivem no ambiente sem
estar declaradas — ou declare-as.**

**MET-18.** **Duas das três fotos de um anúncio mostravam a caixa de atacado, com dezenas de
unidades a granel, e o anúncio vendia uma caixa de 10; a terceira era mock-up 2D chapado**,
todas entre 375 e 500 px, abaixo dos 1200 que o marketplace pede para zoom → a auditoria
cuidava de preço, título, frete e ficha, e ninguém abriu as fotos → **numa auditoria ou num
anúncio, a imagem é campo como qualquer outro e mostra exatamente o que se vende:
quantidade, embalagem, versão.** Expectativa visual errada alimenta devolução.

---

## Origem

Número da lição no registro do repositório de origem (`CLAUDE.md` daquele repositório) → ID aqui.

| Origem | Aqui |
|---|---|
| 1 | MET-3 |
| 2 | IMG-8 |
| 3 | MET-1 |
| 4 | MET-2 |
| 5 | IMG-19 |
| 6 | IMG-12 |
| 7 | IMG-15 |
| 8 | IMG-10 |
| 9 | MET-16 (+ skill de vídeo da origem, `colagem.md` §8: commit só dos seus arquivos) |
| 10 | MET-11 |
| 11 | MET-17 |
| 12 | IMG-7 (+ `docs/PESQUISA-REALISMO-GERACAO.md` §3: o padrão de edição que a documentação da OpenAI prescreve) |
| 13 | IMG-2 |
| 14 | IMG-18 — parcial: as coordenadas medidas daquele arquivo de produção ficaram de fora |
| 15 | IMG-17 |
| 16 | NAV-12 |
| 17 | NAV-10 · MET-13 |
| 18 | MET-6 (+ skill de imagem da origem, fase 4: o agente que converteu "não consigo ler" em "confere") |
| 19 | MET-10 |
| 20 | IMG-3 |
| 21 | IMG-3 |
| 22 | IMG-5 (+ skill de imagem da origem, fase 4: QR e código de barras gerados estão sempre errados) |
| 23 | NAV-13 — parcial: a vitrine 1:1 e os limites de upload daquela loja ficaram de fora |
| 24 | NAV-5 — parcial: a função de arrasto e a regra "principal é a posição 0" daquela loja ficaram de fora |
| 25 | VID-1 |
| 26 | VID-3 |
| 27 | VID-4 |
| 28 | VID-1 · VID-2 · MET-11 · MET-12 |
| 29 | MET-15 |
| 30 | MET-7 · MET-8 |
| 31 | VID-13 |
| 32 | MET-9 |
| 33 | IMG-9 |
| 34 | NAV-8 |
| 35 | NAV-10 · MET-13 |
| 36 | NAV-10 |
| 37 | NAV-9 |
| 38 | MET-7 · MET-8 |
| 39 | NAV-13 — parcial: os sufixos de variante do CDN daquele marketplace e a receita de envio para ele ficaram de fora |
| 40 | NAV-3 |
| 41 | NAV-4 — parcial: os seletores e os `aria-label` daquele painel ficaram de fora |
| 42 | NAV-6 — parcial: o seletor do DOM e a conferência pelo CDN daquele marketplace ficaram de fora (+ skill de imagem da origem: a ordem do upload no Grok) |
| 43 | MET-18 — sem os números da conta (taxa de envio incorreto, preço) |
| 44 | MET-14 · IMG-5 |
| 45 | IMG-6 |
| 46 | IMG-4 · MET-4 |
| 47 | MET-5 |
| 48 | IMG-11 |
| 49 | IMG-16 · NAV-7 |
| 50 | NAV-10 · NAV-2 · NAV-3 — parcial: o seletor e a resolução da imagem gerada no ChatGPT ficaram de fora |
| 51 | NAV-10 |
| 52 | NAV-11 · NAV-2 (+ skill de imagem da origem: `insertText` e a confirmação pelo `/c/<id>`) |
| 53 | AUD-1 (+ skill de vídeo da origem, `colagem.md` §3: o algarismo do whisper convertido por `por_extenso`) |
| 54 | VID-12 |
| 55 | VID-9 |
| 56 | AUD-2 · VID-6 (+ skill de vídeo da origem, `colagem.md` §4–§5: conferência no envelope, voz nova, `depois()` e desvio relativo; "Sinais de que você está saindo do padrão": áudio acelerado) |
| 57 | VID-7 |
| 58 | VID-8 |
| 59 | VID-10 |
| 60 | VID-11 |
| 61 | VID-5 |
| 62 | AUD-3 (+ skill de vídeo da origem, `colagem.md`, "Sinais de que você está saindo do padrão": nunca afrouxar a folga) |
| 63 | NAV-1 |

Regras medidas no corpo daquele `CLAUDE.md`, fora do registro:

| Seção | Aqui |
|---|---|
| Regra zero (sósia, três fluxos, fidelidade × tamanho) | IMG-1 · IMG-2 |
| Luz | IMG-12 |
| Foco | IMG-13 |
| Espontaneidade | IMG-14 |
| Perfil de câmera medido | IMG-15 · MET-10 (o ponto preto depende da luz); os valores-alvo são das fotos de lá e ficaram de fora |
| Método (os quatro itens) | MET-1 · MET-2 · MET-3 · MET-4 |
| "Só marque como conferido o que a referência deixa ler" | MET-6 |
| Camadas de permissão da base · O que a raspagem não protege | IMG-20 · IMG-21 (as exceções de uso de IMG-21 seguem a spec da semente, §7.3) |
| Raspagem do Instagram (conta secundária; o bloqueio cai na conta logada) | NAV-14 (aviso, não medido) |
| Duas sessões, um repositório | MET-16 |
| Status: em teste (registrar a lição) | cabeçalho deste arquivo |
| API xAI e Gemini (parâmetros, preços), roteamento entre provedores, motor de imagem e raspador daquele repositório | fora: a semente não usa API nem aquele motor |
