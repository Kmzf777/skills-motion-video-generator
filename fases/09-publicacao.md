# Fase 09 — Publicação

A descrição trabalha junto com o vídeo: a busca do Instagram lê a descrição [F2], e o Google
indexa post público de conta profissional [F3]. Publicar é ação pública na conta do usuário: a
skill prepara tudo e **só publica com OK explícito, dado na hora**. As fontes `[Fn]` estão no fim.

## Quando

- O `reel.mp4` passou na fase 08. O rascunho pode ser escrito enquanto o render final roda.
- Modo `oferta`: no lugar da descrição, `motion/pecas/NN-tema/anuncio.md` (molde em
  `copy/criativos-anuncio.md`) e a conformidade de `copy/oferta.md`; os passos abaixo valem só
  para o orgânico. **A skill nunca sobe nem impulsiona anúncio**: o usuário sobe.

## Entradas

- `motion/pecas/<NN-tema>/roteiro.txt` e `fontes.md` (a tabela fato → fonte da fase 03)
- `motion/marca/dossie.md`: tom, o que a marca não pode afirmar, localização, conta
- as camadas do banco de imagens (fase 01): o que, na peça, veio da camada 1 (própria verificada)
- `motion/concorrencia/estudo-<data>.md`: como o nicho escreve e que hashtags usa

## Passos

1. **A busca.** Reescreva a promessa A do roteiro como a pergunta que as pessoas digitam:
   pergunta, não assunto, porque é a descrição que a busca lê [F2] [F3]. Para ver como o
   público escreve, digite o começo dela na busca do Instagram e do Google pelo Chrome e leia
   as sugestões (poucas buscas: a conta é a do usuário).
2. **Primeira linha ≤ ~55 caracteres**, o trecho que aparece sobre o Reel [F1]. Emoji e
   espaço contam. Conte, não estime: `python -c "import sys; print(len(sys.argv[1]))" "<linha>"`.
   Escreva também duas alternativas para testar em peças futuras. *Exemplo **inventado**:
   "Como saber se o seu mel é puro de verdade", seguida de espaço e um emoji: 41 caracteres
   sem os dois, 43 com eles (na peça de origem, a linha tinha 46 sem e 48 com).*
3. **Corpo = a colinha do vídeo**, em blocos curtos: o que a pessoa manda por DM para alguém.
   Envio é um dos sinais que Mosseri confirmou, com tempo assistido e curtidas, e pesa mais
   que salvar [F4]. Só fatos já verificados no roteiro. Fato novo que a descrição acrescente
   passa pela mesma tabela da fase 03 (só [oficial] ou [medido]) ou não entra.
4. **A marca.** A prova da empresa, com os mesmos fatos verificados. Diga o que é real ("as
   fotos de <lugar> no vídeo são nossas") **só** se a imagem veio da camada 1 (própria
   verificada) do dossiê: com IA em toda parte, provar o que é real passa a valer mais que
   marcar o gerado [F7]. Foto de banco livre nunca é apresentada como da marca; asset gerado
   nunca como foto.
5. **Fecho.** "Salva pra <uso concreto>" (prática da casa, sem fonte de plataforma) +
   **pergunta aberta** sobre a experiência de quem lê. Nunca "comenta X que eu te mando": o
   Instagram deixa de recomendar post que pede comentário com palavra específica [F5].
6. **Fontes** numa linha, pelo nome do documento (link na descrição não é clicável).
7. **No máximo 5 hashtags**, limite da plataforma desde dez/2025 [F6], como rótulo de
   assunto: assunto, lugar, nicho, marca. Nada de tag genérica de alcance.
8. **Grave `motion/pecas/<NN-tema>/legenda-post.md`** com: a primeira linha recomendada e as
   alternativas; a descrição completa num bloco de código, para copiar e colar; uma versão
   curta (3–4 linhas); a tabela fato → fonte do que a descrição acrescenta ao vídeo; o
   checklist do passo 9. Limite da plataforma: 2.200 caracteres.
9. **Checklist de publicação** (vai no `legenda-post.md`):
   - [ ] **rótulo de IA ligado** (Configurações avançadas → rótulo de IA): a narração é voz
     sintética, áudio realista gerado por IA, e a Meta exige o rótulo [F8]; no post ele
     aparece como "Informações de IA" [F9]. Na dúvida, rotule. Política de IA do repositório,
     se houver, vale também.
   - [ ] **localização**: o lugar real da marca, do dossiê.
   - [ ] **capa**: quadro com texto legível no centro, conferido no corte 3:4 da grade do
     perfil (os 1080×1440 do meio: somem 240 px em cima e embaixo). Da raiz do repositório:
     ```bash
     python -c "import subprocess,sys; sys.path.insert(0,'motion/ferramentas'); from _ffmpeg import ffmpeg; from PIL import Image; v,s,d=sys.argv[1:4]; subprocess.run([ffmpeg(),'-v','error','-y','-ss',s,'-i',v,'-frames:v','1',d+'/capa.png'],check=True); Image.open(d+'/capa.png').crop((0,240,1080,1680)).save(d+'/capa-3x4.png')" motion/pecas/<NN-tema>/saida/reel.mp4 <segundo> motion/pecas/<NN-tema>/saida
     ```
     `capa.png` é a que sobe; `capa-3x4.png` é para conferir. Apague as duas depois de publicar.
   - [ ] **"aparecer em mecanismos de pesquisa" ligado** (conta profissional pública) [F3].
     Só confira: ligar é configuração de conta, então diga ao usuário e só mude com OK.
   - [ ] recorte do vídeo **original 9:16**, nem 1:1 nem 4:5.
   - [ ] descrição colada inteira, a do `legenda-post.md`; ≤ 5 hashtags; nenhum "comenta X".
10. **Mostre ao usuário** a descrição, a capa e o checklist, e ajuste o texto até o OK.
11. **Escolha a rota pelo tamanho do `reel.mp4`.** O `file_upload` do Claude in Chrome só aceita
    **menos de 10 MB somados por chamada**. Meça em bytes e deixe folga:
    `python -c "import os,sys; print(os.path.getsize(sys.argv[1]), 'bytes')" motion/pecas/<NN-tema>/saida/reel.mp4`
    - **9.500.000 bytes ou mais** (o normal: o da peça de origem tem 122.613.382 bytes, 116,9 MiB):
      entregue `reel.mp4`, `capa.png` e `legenda-post.md` prontos, com o checklist, e o usuário
      publica pelo app. É também a rota quando a versão web não mostra o rótulo de IA.
    - **Abaixo de 9.500.000 bytes**: pelo Chrome, só com OK explícito na hora. Pergunte "Publico agora em
      @<conta>?": OK do roteiro, de outro dia ou de outra peça não vale. Com o sim: aba nova,
      instagram.com → Criar → `reel.mp4` por `file_upload` (`navegador/chrome.md`) → recorte
      original → capa → descrição → localização → Configurações avançadas → rótulo de IA.
      Screenshot da tela preenchida e conferência campo a campo; algo diferente do aprovado,
      pare e pergunte. Só então Compartilhar. A tela está **a validar no piloto**: screenshot
      antes de cada clique, e a mecânica que funcionar vai para `navegador/instagram.md` (fase 10).
12. **Depois de publicar** (pela skill ou pelo usuário). Abra o post e confira descrição, capa
    e o selo "Informações de IA" [F9]; grave data e URL no `legenda-post.md`. Responder os
    comentários da primeira hora no tom da marca ajuda: redija as respostas, mas responder em
    nome da marca é ação pública, só com OK de cada uma (ou o usuário responde).

## Molde da descrição

```text
<a pergunta da busca, ≤ ~55 caracteres>

<uma frase que reabre a promessa e anuncia a colinha>

<marcador> <bloco 1: título curto>
<o dado do vídeo, com número, unidade e o que ele quer dizer>

<marcador> <bloco 2: título curto>
<idem>

<marcador> O que quase ninguém conta
<a virada do roteiro, com a frase feita para ser repetida>

<a prova da marca: só fato [oficial]/[medido]; "as fotos são nossas" só se forem>

<marcador> Salva pra <uso concreto>.
<pergunta aberta sobre a experiência de quem lê>

Fontes: <documento 1> · <documento 2> · <documento 3>

#<assunto> #<assunto> #<lugar> #<nicho> #<marca>
```

Fonte de cada regra do molde: primeira linha com a pergunta e ≤ ~55 caracteres [F1] [F2] [F3]
· colinha que se manda por DM [F4] · pergunta aberta, sem "comenta X" [F5] · até 5 hashtags
[F6] · "as fotos são nossas" só com prova [F7] · rótulo de IA [F8] [F9]. "Salva pra…" é
prática da casa, sem fonte de plataforma.

`<marcador>`: um emoji por bloco, se o tom da marca permitir. *Exemplo (a peça de origem, sem
as falas): a pergunta da busca, duas "provas" com os números do roteiro, a virada, a prova da
marca, "Salva pra conferir na próxima compra" e uma pergunta aberta sobre o produto que o
espectador tem em casa.*

## Saídas

- `motion/pecas/<NN-tema>/legenda-post.md`; na rota do app, também `capa.png` em `saida/`
- depois de publicado: data e URL do post, no mesmo arquivo
- modo `oferta`: `motion/pecas/NN-tema/anuncio.md` (molde em `copy/criativos-anuncio.md`) com a
  conformidade de `copy/oferta.md`; a skill nunca sobe nem impulsiona — o usuário sobe

## Pronto quando

- primeira linha contada (≤ ~55) e com a pergunta da busca
- todo fato da descrição com fonte [oficial] ou [medido]; "o que é real" só da camada 1
- pergunta aberta no fecho; no máximo 5 hashtags
- `legenda-post.md` com descrição completa, versão curta e checklist; texto aprovado
- publicado pelo Chrome com OK dado na hora (abaixo de 9.500.000 bytes), ou entregue pronto
  para o usuário publicar pelo app; URL gravada depois

## Erros comuns

- **Isca de comentário** ("comenta PALAVRA que eu te mando"): o post deixa de ser
  recomendado [F5]. Pergunta aberta.
- **Primeira linha com o assunto** ("Tudo sobre X") em vez da pergunta: a busca casa a
  pergunta que as pessoas digitam.
- **Hashtag de enfeite**: mais de 5, ou genéricas. Hashtag aqui é rótulo de assunto.
- **Fato novo sem fonte** só porque "é descrição, não é o vídeo".
- **"Nossas fotos" sobre foto de banco livre** ou sobre asset gerado.
- **Publicar sem o rótulo de IA porque "é só a voz"**: voz sintética realista é exatamente
  o caso que a Meta manda rotular [F8].
- **Tomar um OK antigo como OK de publicação.** Publicar pede OK daquela peça, naquela hora.
- **Subir pelo Chrome um Reel de 9.500.000 bytes ou mais**: o `file_upload` só leva menos de
  10 MB por chamada; rota do app.
- **Capa escolhida no 9:16** cujo texto some no corte 3:4 da grade.
- **Copiar a descrição de um concorrente**: o estudo da fase 02 é referência de formato.

## Fontes da pesquisa

- [F1] ~55 caracteres da descrição aparecem sobre o Reel. ClipSpeed:
  <https://www.clipspeed.ai/blog/instagram-reels-captions.html>
- [F2] A busca do Instagram lê a descrição. Instagram:
  <https://about.instagram.com/blog/announcements/break-down-how-instagram-search-works/>
- [F3] Google indexa posts públicos de contas profissionais desde 10/07/2025. PPC Land:
  <https://ppc.land/instagram-content-becomes-searchable-on-google-starting-july-10/>
- [F4] Sinais confirmados por Mosseri: tempo assistido, envios por DM e curtidas; o envio pesa
  mais que salvar. Kompozy:
  <https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance> · Dataslayer:
  <https://www.dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers>
- [F5] Diretriz contra pedir comentário com palavra específica. Social Media Today, jun/2024:
  <https://www.socialmediatoday.com/news/instagram-clarifies-advice-single-word-ctas-longer-reels/718151/>
- [F6] Limite de 5 hashtags por post. Social Media Today, dez/2025:
  <https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/>
- [F7] Dizer o que é real (Mosseri, 31/12/2025). Engadget:
  <https://www.engadget.com/social-media/instagram-chief-ai-is-so-ubiquitous-it-will-be-more-practical-to-fingerprint-real-media-than-fake-media-202620080.html>
- [F8] Rótulo obrigatório para áudio realista gerado por IA. Meta, fev/2024:
  <https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/>
- [F9] Rótulo "Informações de IA". Meta, abr/2024:
  <https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/>

Regra de plataforma muda. Se a fonte tiver mais de ~6 meses quando você for afirmar a regra
ao usuário, confira de novo pelo Chrome; mudança confirmada vira lição universal (fase 10).
