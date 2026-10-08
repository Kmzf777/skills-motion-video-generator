# Meta — Biblioteca de Anúncios (pública) e Gerenciador (só leitura)

A **Biblioteca de Anúncios** mostra os criativos pagos do nicho: é estudo da fase 02 nos modos
`oferta` e `vsl`. O **Gerenciador de Anúncios** mostra o resultado das variações da marca: é
leitura da fase 10, e **só leitura**. Regras comuns em `chrome.md`; o que fazer com os números,
em `copy/criativos-anuncio.md`. Sem marca = visto em sessão real (08/10/2026, Biblioteca
deslogada, país Brasil); *(a validar no piloto)* = tela não vista por quem escreveu esta página.

## Biblioteca de Anúncios

Pública e **sem login**: abriu deslogada, com o botão "Entrar" à vista, sem pedir nada. Não
entre: a leitura não precisa de conta, e a conta é do usuário.

1. **Abrir com a busca na URL**, numa aba nova (`tabs_create_mcp`):
   `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BR&media_type=video&q=<termo>&search_type=keyword_unordered`
   - `country` é o país do público da marca (`BR` aparece como "Brasil"); `active_status=active`
     deixa só os ativos; `media_type=video`, só vídeo.
   - A página acrescenta sozinha `sort_data[mode]=total_impressions&sort_data[direction]=desc`.
   - Cookie: se aparecer banner, a opção mais restritiva (na sessão medida não apareceu).
2. **Buscar por termo ou por anunciante**: o campo "Pesquisar por palavra-chave ou anunciante"
   aceita os dois. Por anunciante, escolha a página certa na lista de sugestões *(a validar no
   piloto)*; o painel "Filtros" também tem o filtro "Anunciante".
3. **Filtros** (botão "Filtros"): Idioma · Anunciante · Plataforma (Facebook, Instagram, Audience
   Network, Messenger, WhatsApp, Threads) · Tipo de mídia (inclui "Vídeos" e "Palavra-chave na
   transcrição do vídeo ou no texto do anúncio") · Status online (Ativos e inativos, Anúncios
   ativos, Anúncios inativos) · Impressões por data. A busca na **transcrição** acha o anúncio
   pelo que se fala nele: procure a frase típica de gancho do nicho.
4. **Ordem** ("Classificar por"): "Impressões: do mais alto ao mais baixo" (o padrão) ou "Mais
   recentes". A ordem por impressões não mostra o número: é sinal de alcance, não de resultado.
5. **Ler os cartões** com `get_page_text`. Cada um traz: "Ativo" · "Identificação da biblioteca"
   · "Veiculação iniciada em <data>" · Plataformas · "Esse anúncio tem várias versões" · "N
   anúncios usam esse criativo e esse texto" · anunciante · texto principal · domínio da página ·
   título · descrição · botão (o CTA).
   - "Ver resumo" abre o "Resumo de dados": as N versões com a mesma imagem ou vídeo e texto, com
     datas de início, localizações ou orçamentos diferentes (texto da própria Meta).
   - "Ver detalhes do anúncio" abre o anúncio com as versões navegáveis ("1 de 3") e "Sobre o
     anunciante".
   - Com a aba oculta, `.click()` por JS abriu esses painéis, o filtro e a ordem: é controle de
     estado local (lição `NAV-4`). Feche o painel com o "Fechar" dele.
6. **Vencedor provável é sinal, não prova.** Ativo há 30–60+ dias **e** com várias versões, ou
   com muitos anúncios usando o mesmo criativo, sugere que dá resultado. A Biblioteca **não mostra
   resultado**: nem gasto, nem cliques, nem vendas ([segwise](https://segwise.ai/blog/meta-ad-library-competitor-research) ·
   [superscale](https://www.superscale.ai/learn/how-to-use-the-meta-ad-library), *prática de mercado*).
7. **Duração e quadro de 0,5 s**: dê play no cartão e leia o `<video>` pela receita de
   `instagram.md`, passo 7 (`currentTime` + screenshot; o estudo completo em `assistir-video.md`)
   *(a validar no piloto: com a aba oculta, o metadado do vídeo não carregou em 6 s; deixe a
   janela visível, `chrome.md` §1)*.
8. **Volume baixo**: 5–12 anunciantes por estudo, poucas buscas. Não clique no botão nem no link
   do anúncio: o domínio já está no cartão.

### O que anotar: só texto e link

Em `motion/concorrencia/estudo-<AAAA-MM-DD>.md`, seção "Anúncios (Biblioteca da Meta)":

| Anunciante | Identificação | Início | Versões / anúncios | Gancho escrito a 0,5 s | 1ª frase falada | Duração | Oferta (preço, bônus, garantia, prazo) | CTA | Domínio | Esqueleto |
|---|---|---|---|---|---|---|---|---|---|---|

- Link de cada anúncio: `https://www.facebook.com/ads/library/?id=<Identificação da biblioteca>`
  *(a validar no piloto)*. Data de leitura ao lado: anúncio ativo hoje sai do ar amanhã.
- Esqueleto, pelos nomes de `copy/kishotenketsu.md`: preço, efeito, dor; problema → solução,
  demonstração, oferta direta; ketsu primeiro ou não.
- **Criativo de terceiro só vira texto e link**: nunca pixel do vídeo, nunca quadro subido ao
  ChatGPT como referência, nunca arquivo no repositório. É a regra da fase 02 para reel de
  concorrente, e pelo mesmo motivo: quadro de anúncio quase sempre tem rosto, logo ou texto de
  outra marca.
- Anote também o que **não** copiar: promessa sem prova, escassez de fachada, atributo pessoal
  ("Você está…?") que a política da Meta proíbe (`copy/oferta.md`).

## Gerenciador de Anúncios — só leitura

A conta de anúncios é do usuário: a skill lê e nunca altera. **Tela toda a validar no piloto.**
Abra só na fase 10, para ler as variações que o usuário subiu, numa aba nova, com a sessão dele.
Pediu login, código ou permissão: pare e peça ao usuário (`chrome.md` §1).

1. `https://adsmanager.facebook.com/` → aba **Anúncios** (não Campanhas: cada variação é um
   anúncio) → o período em que as variações rodaram.
2. Colunas: escolha no menu "Colunas" a **predefinição de vídeo/engajamento que já existe** e leia
   **Impressões**, **Reproduções de vídeo de 3 segundos**, **ThruPlays**, reproduções até 25–100%,
   **CTR (taxa de cliques no link)**, custo por resultado e ROAS, se houver; ou peça ao usuário um
   print ou uma exportação. **Não** clique em "Aplicar" em colunas personalizadas: muda a visão da
   conta. Se for preciso personalizar, peça OK antes.
   - Leia a definição de cada coluna no ícone de informação dela antes de calcular. ThruPlay
     costuma ser "até o fim, ou 15 s" (definição citada por terceiros).
3. Leia a tabela por `get_page_text`, ou peça ao usuário um print ou uma exportação. Calcule as
   taxas de `copy/criativos-anuncio.md` e grave na seção Resultado do `anuncio.md`, com a data.
4. **Nunca clique**: Publicar, Revisar e publicar, Editar, Duplicar, a chave liga/desliga do
   anúncio, Aumentar orçamento, Impulsionar, regras automáticas, recomendações ("Aplicar"). Na
   dúvida sobre um botão, não clique: pergunte.

## Erros comuns

- "Ativo há 60 dias" lido como prova de lucro: é sinal.
- Baixar o vídeo de um anúncio de terceiro, ou subir um quadro dele ao ChatGPT.
- Ler o resultado da campanha inteira: mistura as variações e o teste some.
- Clicar na chave de status achando que é filtro: pausa ou ativa um anúncio de verdade.
- Salvar predefinição de colunas sem OK: é configuração da conta.
- Entrar na Biblioteca com a conta do usuário "para ver mais": ela é pública.
