# Fase 01 — Contexto da marca

Monta o que toda peça consome: o dossiê com cada fato marcado pela origem, a identidade que
o motor lê, a voz da marca e o banco de imagens separado pelo que é permitido fazer com cada
arquivo. **Pesquisa primeiro; pergunta só o que a pesquisa não respondeu.**

## Quando

- Primeira peça: não existe `motion/marca/dossie.md`, ou `identidade.json` ainda tem
  `"exemplo": true` (valores de outra marca, postos pelo plantio para o motor compilar).
- Dossiê com mais de 6 meses; produto, preço ou posicionamento mudou; o usuário pediu.
- Só `voz.nome` vazio em `identidade.json`: faça apenas os passos 17 e 18.

## Entradas

- Repositório com a fase 00 concluída; `licoes-empresa.md` desta skill.
- Chrome com Claude in Chrome e as sessões do usuário: `navegador/chrome.md`,
  `navegador/instagram.md`, `navegador/elevenlabs.md`.

## Passos

### Pesquisa
1. **Repositório.** Leia `README*`, `CLAUDE.md`, `docs/` e pastas de marca, marketing ou
   conteúdo. Procure com Glob/Grep, fora de `node_modules`: logos (`**/*logo*`), cores
   (`--color`, `tailwind.config`, `theme`), fontes (`font-family`, `@font-face`,
   `fonts.googleapis`), catálogo de produtos (JSON, CSV, planilha), pastas de foto e regra
   que proíba imagem de terceiro como referência (se houver, vence a desta skill). Cada
   achado entra no dossiê com o caminho como fonte.
2. **Site**, numa aba nova: home, produtos, sobre, contato. Registre produtos e preços com
   a data da leitura; promessas ("desde", "o único", "100%", selos, prêmios); três frases
   que mostram o tom; a região. Cores e fontes pelo DOM (`javascript_tool`):
   `getComputedStyle` de `body`, `header`, `h1`, botões e links; `document.fonts` e as
   folhas carregadas dizem de onde vem cada fonte. Cookie: recuse o não essencial.
3. **Instagram da empresa** (`navegador/instagram.md`): bio e link, seguidores, número de
   posts, cadência (posts por semana nos últimos 30, **sem os fixados** — fixado antigo
   falseia a data do último post), % de reels, mediana de curtidas e **os 9 posts de topo**
   entre os últimos 36, cada um contra a mediana do seu tipo (curtidas nos posts, views nos
   reels: curtida subestima reel). De cada um: data, tipo, tema em uma linha, número. Nunca
   curta, siga, comente nem salve.
4. **Google**: `"<marca>"` na aba Notícias, `<marca> avaliações`, a ficha do Google Maps e o
   site de reclamação do país (no Brasil, Reclame Aqui). Registre o fato com link e o elogio
   e a queixa que se repetem, nas palavras dos clientes — sem nome de avaliador, cliente
   ou funcionário.
5. **Marque cada fato pela origem.** Afirmação sem marca é erro de redação.

   | Marca | O que é | Vira fala? |
   |---|---|---|
   | [oficial] | publicado por quem tem autoridade sobre o fato: lei, norma, órgão público, entidade técnica do setor, a plataforma sobre si mesma; documento formal da empresa (laudo, certificado, ficha técnica); fato da história da empresa confirmado pelo responsável, com nome e data | sim |
   | [medido] | lido ou medido por nós no pixel ou no arquivo: rótulo ampliado, EXIF, preço na página em tal data, contagem de seguidores | sim |
   | [criador] | inferência de quem pratica (criador, agência, curso), sem confirmação | não; vira hipótese de formato |
   | [terciário] | citação do que não abrimos: matéria que cita estudo, site de terceiro, texto interno sem anexo, **promessa do site sem documento** | não, até virar [oficial] ou [medido] |
   | [folclore] | circula como verdade sem base (ex.: "dopamina" como mecanismo de retenção) | nunca; serve para reconhecer e recusar |

   [medido] cobre o que se leu: "o rótulo diz X" deixa a fala dizer o que o rótulo diz,
   não mais. Alegação regulada (ambiental, saúde, composição, prêmio, certificação,
   comparação com concorrente) só com documento. Leitura sua mantém a marca do fato e diz
   que é leitura.

### Dossiê
6. Escreva `motion/marca/dossie.md`: título `# Dossiê — <Marca>`, data, fontes consultadas,
   a régua do passo 5 e estas seções, nesta ordem. Campo sem dado fica `não verificável` ou
   `a perguntar` — nunca vazio, de memória ou por analogia entre produtos.

   | Seção | Conteúdo |
   |---|---|
   | Empresa | o que vende, para quem, onde, desde quando, o que só ela tem; uma frase por linha, com marca |
   | Nicho e termos de busca | categoria do negócio e região; 3 a 5 termos que o público digita para achar o nicho (a fase 02 busca concorrentes com eles) |
   | Produtos | tabela: produto · preço (data) · atributos que uma tese pode tocar · o que o rótulo diz (pixel ampliado) · foto real (caminho) · marca |
   | Promessas e provas | tabela: promessa · prova (arquivo, link, documento) · marca · pode virar fala? |
   | Não afirmar | o que o cliente proibiu; alegação regulada sem documento; regra do repositório sobre imagem |
   | Público, objetivo e tom | público · objetivo dos Reels · produtos foco · tom · palavras da casa e palavras proibidas |
   | Instagram (retrato de AAAA-MM-DD) | conta (@) · bio · seguidores · posts · cadência · % de reels · mediana · os 9 de topo |
   | Fora da empresa | notícia e avaliação: fato com link; elogio e queixa que se repetem |
   | Identidade | cor por papel (hex, origem, contraste) · fonte (família, licença, arquivo) · logos; cada item `marca` ou `exemplo` (ainda do plantio) |
   | Voz | nome exato na ElevenLabs, link, idioma, quem escolheu e quando; a fase 04 acrescenta o rótulo do modelo, os ajustes e a velocidade da série |
   | Banco de imagens | caminho · contagem por camada · pastas ou arquivos de cada camada · decisões com data |
   | Em aberto | conflitos `não verificável` e perguntas sem resposta |

7. **Tom**: não existe tom padrão; ele se pergunta no passo 13. Monte 2 ou 3 opções a partir
   do site e do Instagram, cada uma com uma frase de exemplo no assunto da marca. Uma
   sugestão que pode entrar entre elas: o termo técnico traduzido na mesma frase e o cliente
   no centro (o que ele ganha, como confere sozinho), em vez do elogio da empresa a si
   mesma. Vale o que o usuário escolher, gravado no dossiê com a frase de exemplo.

### Identidade
8. **Cores.** Junte as dominantes do logo (só pixels opacos) e as do site e distribua pelos
   papéis do motor: `escuro` (texto, fundo quase preto), `claro` (papel, fundo claro),
   `profundo` (fundo de cena escuro; é o fundo da pílula), `acento` (a cor da chamada de
   compra), `apoio` (secundária). Contraste WCAG, o mesmo que `tests/identidade.test.ts`
   cobra: `claro` sobre `escuro` e sobre `profundo` ≥ 4,5:1; `acento` ≥ 3:1 contra `claro`
   ou `escuro`. Papel sem cor da marca leva a neutra mais próxima do site; cor inventada, nunca.
9. **Fontes**, por papel (`manchete`, `corpo`, `dado`). Fonte do site com licença livre
   (Google Fonts, OFL, Apache) pode entrar: diga nome, origem e tamanho, baixe com OK para
   `motion/marca/fontes/` e ponha em `arquivo` **só o nome** (ex.: `Fraunces-Bold.ttf`; o
   motor recusa caminho), com `familia` e `peso` daquele arquivo. Fonte comercial ou de
   licença desconhecida **não entra**: fica a padrão, `arquivo: null` com família e peso
   exatos (Archivo Black 400, Inter 700, IBM Plex Mono 500), e o dossiê registra "o site usa
   X, comercial; o motor usa Y". Fonte sem os acentos do idioma reprova na guarda do motor.
10. **Logo.** Dois arquivos `logo-*` na raiz de `motion/marca/` (PNG ou WebP transparente,
    ≥ 1000 px no lado maior, ou SVG): `logo-escura.png` vai sobre fundo claro,
    `logo-clara.png` sobre escuro. Busca: repositório → site (baixar só com OK) → usuário.
    Logo de uma cor ganha a versão oposta por código (troca a cor dos pixels opacos,
    preserva o alfa); colorido sem versão para fundo escuro, pergunte. **Nunca** peça a um
    modelo de imagem que redesenhe, limpe ou vetorize o logo.
11. **Grave `motion/marca/identidade.json`** no formato do contrato (C3), com as chaves do
    arquivo plantado: `marca` grafada como no logo, `idioma`, `cores`, `fontes`, `logo`,
    `voz`; `slug` não muda (é o nome da pasta da skill). Com cores, fontes e logo da marca
    (fonte padrão por falta de licença é decisão, não exemplo), troque `"exemplo": true` por
    **`false`** e apague a `_nota`. Com `true`, a peça sai com a cara de outra marca.
12. **Confira no motor**, em `motion/remotion`:
    - `npx vitest run tests/identidade.test.ts` lê o `identidade.json` real: campo errado sai
      com o nome do campo, e o contraste do passo 8 é cobrado ali (o `tsc` não pega isso);
    - `node scripts/contato.mjs Marca 00-exemplo 0 --escala=1 --cols=1 --saida=identidade.png`
      renderiza a composição `Marca` (um quadro só) e grava em
      `motion/pecas/00-exemplo/saida/identidade.png`. Abra e confira as 5 cores, as fontes
      com os acentos do idioma, o logo sobre claro e sobre escuro, a pílula nos dois fundos e
      **nenhuma** faixa "IDENTIDADE DE EXEMPLO". Fonte que não aplica, ou logo que falta com
      `"exemplo": false`, derruba o render com o motivo.

### Perguntas
13. Pergunte o tom sempre (opções do passo 7) e, do resto, só o que a pesquisa não
    respondeu, nesta ordem: público; objetivo dos Reels; produtos foco; o que não pode ser
    afirmado; as promessas do site que as peças vão usar (cada uma vira [oficial], pede
    documento ou sai); cada conflito entre fontes. **AskUserQuestion, uma pergunta por vez**,
    2 a 4 opções concretas da pesquisa (ex.: "quem já compra · quem compra o genérico ·
    revenda") e o campo livre. Resposta vai ao dossiê "(confirmado por <pessoa>, AAAA-MM-DD)".

### Banco de imagens
14. Pergunte onde estão as fotos da empresa (AskUserQuestion: pasta neste computador ·
    nuvem, e o usuário baixa para uma pasta · só o Instagram · não há). Não mova, não
    renomeie e não copie os originais: a camada de cada arquivo fica escrita no dossiê.
15. Rode este trecho (salvo numa pasta temporária) com o Python do `motion/.venv`, passando a
    pasta do banco:

    ```python
    import sys, pathlib
    from PIL import Image
    EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff"}
    for p in sorted(q for q in pathlib.Path(sys.argv[1]).rglob("*") if q.suffix.lower() in EXT):
        try: im = Image.open(p); ex = im.getexif()
        except Exception as e: print(f"{p}\tERRO {e}"); continue
        w, h = im.size if ex.get(274) not in (5, 6, 7, 8) else im.size[::-1]  # Orientation gira a exibição
        data, gps = ex.get_ifd(0x8769).get(36867, ""), "GPS" if ex.get_ifd(0x8825) else "-"
        print(f"{p}\t{w}x{h}\t{ex.get(271, '')} {ex.get(272, '')}\t{data}\t{gps}\t{ex.get(305, '')}")
    ```

    Saída: arquivo, dimensão de exibição, câmera, data, GPS, `Software`. `ERRO` (HEIC sem
    leitor, arquivo corrompido) se resolve antes de classificar.
16. Distribua em quatro camadas e escreva no dossiê:

    | Camada | Critério | Pixel do vídeo | Referência no ChatGPT | `--origem` |
    |---|---|---|---|---|
    | 1 · própria verificada | EXIF de câmera (fabricante, modelo, data); GPS quando houver | sim | sim | `real-verificada` |
    | 2 · própria sem prova | sem EXIF: WhatsApp, exportada, baixada do próprio Instagram | só depois que o usuário confirmar que é da empresa | depois da confirmação | `real-nao-verificada` |
    | 3 · terceiro: outro perfil | reel, post ou anúncio de outro perfil (concorrente ou não), repost de cliente | **nunca** | **nunca**: só texto e link | — |
    | 3 · terceiro: imagem genérica | Pinterest, Google, banco pago | **nunca** | só como estilo, com as travas de `navegador/referencias.md` | — |
    | 4 · quarentena | sintética (nome de gerador, `Software` de IA, aparência) ou lado menor < 1000 px | **nunca** | **nunca** | — |

    Regra do repositório sobre imagem de terceiro vence esta tabela. Repost de cliente é
    conteúdo de outro perfil: só texto e link, sem exceção. Se o autor autorizar por
    escrito, a foto entra pelo banco da empresa (camada 2, autorização registrada no
    dossiê), não como repost. Foto que cabe em duas camadas fica na mais restrita: a quarentena
    vence (própria com EXIF e 800 px é quarentena). Camada 2 e foto com rosto identificável:
    uma pergunta cada, com a lista de arquivos (rosto só com autorização; nunca
    sintetizado). Produto sem foto real vai para "Em aberto".

### Voz (uma vez, na primeira peça)
17. Na ElevenLabs, numa aba nova (`navegador/elevenlabs.md`), abra a biblioteca de vozes
    filtrada pelo `idioma` de `identidade.json` (`pt-BR`: português do Brasil) e escolha 3
    vozes contrastantes que caibam no tom (ex.: grave e calma · média e calorosa · jovem e
    enérgica); se a conta já usa uma voz, ela é uma das três. Deixe a aba aberta para as prévias.
18. AskUserQuestion com as três (nome exato e uma linha cada), avisando que a escolhida será
    adicionada às vozes da conta se for preciso para usá-la. Grave o nome exato em
    `identidade.json` → `voz.nome`; no dossiê, link e data. A série inteira usa essa voz:
    trocar é decisão do usuário, não de uma peça.

## Saídas

- Em `motion/marca/`: `dossie.md`, `identidade.json` (com `"exemplo": false` e `voz.nome`),
  `logo-escura.*`, `logo-clara.*` e, se entrou fonte livre, `fontes/`.

## Pronto quando

- Todo fato do dossiê tem marca e fonte; nenhuma seção vazia (o que falta está em "Em aberto").
- As perguntas foram feitas uma a uma, com as respostas registradas com nome e data.
- `identidade.json` tem `"exemplo": false` e `voz.nome`, e o passo 12 saiu limpo.
- O tom foi escolhido pelo usuário e está no dossiê com a frase de exemplo.
- O banco tem contagem por camada, e a camada 2 e os rostos têm decisão do usuário.

## Erros comuns

- **Perguntar antes de pesquisar**, perguntar o que o site já responde, ou fazer várias
  perguntas de uma vez sem opções.
- Copiar promessa do site como fato: é [terciário] até confirmação ou documento.
- Ler largura e altura sem a rotação do EXIF: `Orientation` 5 a 8 troca as duas.
- Preencher produto de memória ou por analogia com o produto irmão: cada campo se lê no
  pixel do próprio produto; ilegível é `não verificável`, e o valor confirmado se soletra.
