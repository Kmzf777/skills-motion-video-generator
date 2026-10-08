# ChatGPT — folha de assets sobre branco

Geração de imagem pelo ChatGPT do usuário, numa aba do Chrome. Regras comuns (login, inserir,
enviar, baixar, travas) em `chrome.md`; o que pode ir como referência em `referencias.md`; o
conteúdo da folha, o recorte e o registro na fase 06 (`fases/06-assets.md`). Medido em conta
paga com interface em português, out/2026; *(a validar no piloto)* = não visto.

## Regras de toda folha

- **Uma conversa nova por folha.** Várias imagens na mesma conversa reaproveitam estado e
  degradam as seguintes (relatos de usuários); e cada folha com o seu `/c/<id>` é o que permite
  reabri-la noutra aba para baixar de novo.
- **Follow-up de edição regenera o quadro inteiro.** Medido: "mude SOMENTE o selo", pedido que
  cobria ~1,1% da imagem, mudou **79,2% dos pixels** — veio outra cena. Folha boa com um
  detalhe errado → salve-a e corrija **localmente** (o recorte descarta a peça ruim) ou gere de
  novo **numa conversa nova** com o prompt corrigido. Nunca peça "só isso" por cima.
- **Gere em paralelo, mova em série.** Várias abas podem gerar ao mesmo tempo; cada envio relê o
  composer (ele é compartilhado entre abas da conta), e os arquivos entram no repositório um
  por vez.
- **Sem chat temporário** (`?temporary-chat=true`): ligá-lo recarrega a página e leva prompt e
  anexos (medido).

## Passo a passo

1. **Abrir.** `tabs_create_mcp` → `https://chatgpt.com/`.
   - Procure: o composer (`.ProseMirror`) e a conta no canto; nada de "Entrar".
   - Se falhar: pediu login → pare (`chrome.md` §1). Aviso de limite de imagens, oferta de
     plano ou termos novos → pare e avise; não assine nem aceite nada.
2. **Limpar o composer.** Leia o texto do `.ProseMirror` e a lista de anexos.
   - Confira: texto vazio e nenhum anexo que não seja seu.
   - Se falhar: texto alheio → `selectAll` + `delete` (`chrome.md` §2); anexo alheio → o botão
     de remover da própria miniatura, `.click()` por JS (controle local) *(a validar no piloto)*.
3. **Anexar a referência**, se houver: de terceiro, só quando `referencias.md` permitir; do
   banco da empresa, camada 1 ou camada 2 já confirmada (fase 01) — **nunca** a camada 4
   (quarentena). `find` o input "Anexar arquivos" (`input[type=file]`) e `file_upload` com o
   caminho local (até 10 MB por chamada). Mais de um anexo: **um por chamada**, na ordem em que
   o prompt os cita — upload múltiplo já chegou invertido (`chrome.md` §3).
   - Procure: a miniatura no composer. Abriu overlay de edição → `Escape`.
   - Confira, **antes de enviar**: o arquivo certo e, com mais de um, a ordem das miniaturas
     igual à que o prompt cita.
   - Se falhar: ordem errada → remova os anexos e suba de novo, um por chamada; overlay que não
     fecha → `Escape` de novo, nunca o X do canto.
4. **Montar o prompt** — corpo em inglês (o modelo responde melhor), objetos da fase 06 na
   **ordem de leitura** que o `--nomes` do recorte vai usar *(molde a validar no piloto)*:
   ```text
   A sheet of separate objects for a paper-collage animation, shot straight from above
   on a plain, pure white background (#FFFFFF) that fills the whole frame.
   Arrange them in rows, in this exact reading order, left to right and top to bottom:
   1. <objeto — material, cor, tamanho relativo>; 2. <…>; 3. <…> (3 a 6 objetos).
   Every object complete and inside the frame, with wide empty white space between them;
   nothing touching, overlapping or cropped. Soft even light and only a faint contact
   shadow. No text, no letters, no numbers, no logos, no packaging, no faces. Square image.
   ```
   Com referência, acrescente:
   ```text
   The attached image is a STYLE REFERENCE ONLY: take its light, color palette and texture.
   Do not copy its composition, objects, text, logos or layout.
   ```
5. **Inserir.** Foque o `.ProseMirror` e `document.execCommand('insertText', false, prompt)`.
   - Confira: `textContent.length` = tamanho do prompt menos o número de `\n`.
   - Se falhar: comprimento diferente → limpe e insira de novo. Nunca `computer type`.
6. **Enviar.** Espere ~1 s, releia composer **e** anexos, envie (`chrome.md` §2): clique real em
   "Enviar" com a janela visível; `el.closest('form').requestSubmit()` em aba de fundo.
   - Confira: `location.pathname` passou de `/` para `/c/<id>` **e** o composer zerou. Anote o
     `/c/<id>`.
   - Se falhar: composer ainda cheio → o 1º clique só focou, clique de novo; ref do `find`
     envelheceu → coordenada lida num screenshot novo.
7. **Esperar.** `computer wait` de 10 s em 10 s; nunca laço longo em JS.
   - Procure: `img[alt*="gerada"]` (o alt é "Imagem 1 gerada", não "Imagem gerada"), ou
     `img[alt*="enerated"]` com a interface em inglês.
   - Confira: o botão de parar sumiu e `naturalWidth` não muda entre duas leituras (a quadrada
     sai 1254×1254 — medido).
   - Se falhar: respondeu em texto → pergunta de esclarecimento, responda; recusa ou desvio,
     reescreva o prompt e comece numa conversa nova.
8. **Antes de baixar, só pelo DOM:** a imagem é a desta conversa (a última `img` gerada) e tem
   tamanho cheio. Não confira na tela — `computer zoom` estoura em aba de fundo; a conferência é
   no arquivo (passo 10).
9. **Baixar pelo blob, com nome** — é o 1º download desta aba:
   ```js
   (async () => {
     const img = [...document.querySelectorAll('img[alt*="gerada"], img[alt*="enerated"]')].at(-1);
     const blob = await (await fetch(img.src)).blob();
     const a = Object.assign(document.createElement('a'),
       {href: URL.createObjectURL(blob), download: '<AAAA-MM-DD>_<folha>.png'});
     document.body.append(a); a.click(); a.remove();
     return {w: img.naturalWidth, h: img.naturalHeight, tipo: blob.type, kb: blob.size >> 10};
   })()
   ```
   - Confira: `tipo` = `image/png` e tamanho cheio; o arquivo chegou com o nome exato e hora
     posterior ao disparo (`chrome.md` §4). Mova para
     `motion/biblioteca/brutos/<AAAA-MM-DD>_<folha>.png`.
   - Se falhar: não chegou → 2º download da aba: abra `https://chatgpt.com/c/<id>` numa aba
     **nova** e rode o mesmo trecho lá. `fetch` deu erro → abra a imagem em tela cheia e use
     "Baixar"; aí o nome é do site (já foi "ChatGPT Image…", "Imagem do ChatGPT…" e o título
     da conversa): identifique pela diferença da listagem, nunca pelo mais novo.
10. **Conferir o PNG baixado**, aberto localmente (Read para ver, PIL para medir), nunca na tela:
    ```bash
    python -c "import sys; from PIL import Image; im=Image.open(sys.argv[1]).convert('L'); w,h=im.size; b=[im.getpixel((x,y)) for x in range(w) for y in (0,h-1)]+[im.getpixel((x,y)) for y in range(h) for x in (0,w-1)]; print(w,'x',h,'borda abaixo de 233: %.2f%%' % (100*sum(v<233 for v in b)/len(b)))" "motion/biblioteca/brutos/<AAAA-MM-DD>_<folha>.png"
    ```
    - Borda branca: meça a **fração** da borda abaixo de 233 (255 − o limiar 22 do recorte), não
      o mínimo. Medido: 12 de 13 folhas aprovadas tinham mínimo 253; a 13ª deu 157 porque um
      braço cruza a borda de propósito. Corte: folha sem mão nem braço → **0%**; com mão ou
      braço cruzando a borda → até **~8%** (essa folha deu 5,88%). Acima disso, o fundo vira peça.
    - Objetos inteiros e separados; nenhum texto, logo, embalagem ou rosto; sombra só de contato
      (sombra forte suja o recorte; objeto branco se trata no recorte, `--convexo`, fase 06).
    - A ordem de leitura bate com a lista. Se o modelo trocou a ordem, reordene o `--nomes` pelo
      que se vê — não gere de novo por isso.
    - Se falhar (fundo cinza, objeto cortado ou encostado, texto): gere de novo **em conversa
      nova**, com o prompt corrigido.
11. **Anti-cópia** (só com referência de terceiro): gerado e referência lado a lado (montagem
    na fase 06, regra em `referencias.md`). Reproduziu a composição ou um objeto-assinatura →
    descarte e refaça em conversa nova.
12. **Guardar o prompt exato** para o `--prompt` do `recortar_folha.py` (fase 06): sem ele, a
    próxima sessão não refaz uma folha parecida.
