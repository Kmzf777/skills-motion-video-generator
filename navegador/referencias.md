# Referências — Pinterest e Google Imagens

Imagem de terceiro serve para **descrever** um estilo (luz, paleta, textura, ritmo de
composição) e, dentro das travas abaixo, para subir ao ChatGPT como referência de estilo. Nunca
vira pixel do vídeo. Saída desta página: um descritor em texto, com o link, em
`motion/referencias/`. Regras comuns em `chrome.md`; *(a validar no piloto)* = tela não vista
pela sessão que escreveu a semente.

## Antes de buscar: a regra do repositório vence

Leia o `CLAUDE.md`, os docs do repositório e o `licoes-empresa.md`. Se a casa proíbe imagem de
terceiro como guidance de geração, **toda referência é só texto**, mesmo a que passaria nas
travas desta página.

## Pinterest (opcional — só se o usuário usa)

1. `tabs_create_mcp` → `https://www.pinterest.com/search/pins/?q=<termos>` (pode redirecionar
   para o domínio do país) *(a validar no piloto)*.
   - Procure: a grade de pins.
   - Se falhar: muro de login → pare e pergunte se o usuário quer entrar ou se a busca vai pelo
     Google. Nunca crie conta.
2. Leia 5 a 10 candidatos por JS: link do pin (`a[href*="/pin/"]`), a maior imagem do `srcset`
   e o `alt` *(a validar no piloto)*. Uma ou duas rolagens, não mais.
   - Confira: o link lido abre o pin certo (a grade se reordena enquanto rola).
3. Abra os pins que interessam e anote o **site de origem** (o link de saída), quando houver:
   ele vai no descritor junto do link do pin.

## Google Imagens

1. `tabs_create_mcp` → `https://www.google.com/search?q=<termos>&udm=2` (`udm=2` = aba Imagens)
   *(a validar no piloto)*.
   - Se falhar: banner de consentimento → "Rejeitar tudo". "Tráfego incomum" ou captcha →
     **pare e avise**; nunca resolva.
2. Clique num resultado: o painel lateral mostra a imagem maior e o link da página de origem
   *(a validar no piloto)*. A miniatura da grade é pequena: serve para olhar, não para subir.
3. Anote a página de origem; abra-a só se precisar da imagem em tamanho cheio.

## O descritor — sempre

Um arquivo por busca, `motion/referencias/<AAAA-MM-DD>_<assunto>.md`, um bloco por imagem:

| Campo | O que escrever |
|---|---|
| link | página de origem + link do pin ou do resultado |
| luz | direção, dureza, hora aparente |
| paleta | 3 a 5 cores dominantes (lidas no pixel do screenshot, ou descritas) |
| textura e material | papel, madeira, tecido, brilho, grão |
| composição | ângulo, planos, quanto ar, onde fica o assunto |
| o que NÃO copiar | o arranjo, objeto-assinatura, texto, marca |
| pode subir? | sim / não — e qual trava |
| usada em | o bruto gerado e o veredito da conferência anti-cópia |

## O que pode subir ao ChatGPT e o que nunca sobe

**Pode subir**, como referência de estilo, luz e paleta — só se a regra do repositório permitir e
a imagem não tiver nenhum dos itens abaixo.

**Nunca sobe** (vira só descritor em texto):
- quadro, capa ou print de reel, post ou anúncio de outro perfil — concorrente ou não: só
  texto e link, como na fase 02 (`instagram.md`);
- rosto identificável;
- logo, embalagem ou produto com a marca de outra empresa;
- marca d'água, assinatura ou @ de autor sobre a imagem;
- texto legível que seja o assunto (cartaz, capa, post).

A conta do ChatGPT exige direito sobre o que se envia; o risco é da marca. Na dúvida, texto.

## Como subir

1. **Baixe fora do repositório** (a pasta de downloads serve), com nome escolhido: abra a URL
   direta da imagem numa aba nova e, nela, `fetch(location.href)` + `<a download>` — a mesma
   receita de `chatgpt.md`, passo 9 *(a validar no piloto)*. Confira pelo nome (`chrome.md` §4).
   - Se falhar: a imagem só existe em miniatura → não suba; fica o descritor.
2. **Anexe numa conversa nova** (`chatgpt.md`, passo 3) e declare no prompt:
   ```text
   The attached image is a STYLE REFERENCE ONLY: take its light, color palette and texture.
   Do not copy its composition, objects, text, logos or layout.
   ```
3. **Conferência anti-cópia:** o gerado lado a lado com a referência (a montagem local está na
   fase 06). Mesmo arranjo, mesmo objeto-assinatura ou mesmo enquadramento → descarte e refaça
   em conversa nova, com a referência mais fraca ou só em texto. Escreva o veredito no descritor.
4. **Terceiro nunca é pixel:** não se recorta, não entra na biblioteca (`biblioteca.py` não tem
   origem para ele, de propósito), não vai para `public/`, não entra no git.
5. **Apague a cópia baixada** depois de usar (folha gerada e conferência anti-cópia feitas): no
   repositório fica só o descritor, com o link.

Pinterest e Google genéricos podem subir como referência de estilo, com as travas acima. Quadro
de reel, post ou anúncio de terceiro, **nunca** — nem como referência (`instagram.md`).
