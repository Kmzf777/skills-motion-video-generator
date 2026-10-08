# Instagram — busca, perfil, Reels, views, legenda, comentários, quadros

Leitura pelo Instagram logado do usuário: o perfil da empresa (fase 01), a busca de candidatos e
o estudo de concorrentes e referências de formato (fase 02), as sugestões de busca da descrição
(fase 09). Fora da publicação (fase 09, só com OK explícito na hora), **só leitura** — nunca
seguir, curtir, comentar, salvar, abrir stories ou mandar mensagem (`chrome.md`, travas). O que
não traz marca foi medido em sessão logada (set/2026); *(a validar no piloto)* = não visto.
Rolar a grade e tirar quadro **exigem janela visível** (`chrome.md` §1): não têm rota por JS.

## Volume baixo — a conta é do usuário

Navegação pesada rende bloqueio temporário, e quem leva é a conta logada.

- **Candidato** da fase 02 (passo 2): só a aba Reels, lida na grade — nenhum reel aberto.
  **Perfil confirmado**: até **3 reels** abertos. Rolar só até cobrir a janela da fase: fase 02,
  reels publicados há 7–90 dias (até 180 se faltarem); fase 01, os últimos 36 itens.
- Poucas buscas; alguns segundos entre páginas; nada de abrir perfil "só para ver".
- "Tente novamente mais tarde", desafio de segurança, pedido de login ou de confirmação →
  **pare e avise**. Não insista, não troque de conta.
- Não use a API interna (`/api/v1/...`): respondeu **429 com corpo em HTML**, erro com cara de
  página (medido numa coleta pelo Chrome, set/2026). Leia o DOM já renderizado.

## Busca e hashtag (fase 02, passo 1; fase 09, passo 1)

- **Busca:** ícone "Pesquisar" do menu lateral → digite o termo no campo (`computer type`, sem
  Enter) → leia a lista que abre (contas, hashtags, sugestões de termo) por `get_page_text`
  *(a validar no piloto)*. É a mesma lista que a fase 09 lê para ver como o público escreve.
  Campo que não abre ou não reage → screenshot, `find` "Pesquisar", e registre a lição.
- **Hashtag:** `https://www.instagram.com/explore/tags/<hashtag>/` → posts de topo *(a validar no
  piloto: pode redirecionar para a busca)*. O autor costuma vir no `alt` da miniatura ("Foto de
  <conta>…") *(a validar no piloto)*; sem isso, abra só os de topo (até ~9). Perfil de empresa
  do nicho vira candidato.

## Passo a passo do perfil

1. **Perfil.** `tabs_create_mcp` → `https://www.instagram.com/<usuario>/`.
   - Procure: nome, bio, link, contadores (posts, seguidores, seguindo).
   - Confira: logado (sem "Entrar" no topo) e o @ certo — perfil muda de nome.
   - Leia: `document.querySelector('meta[property="og:description"]')?.content` traz os
     contadores numa frase *(a validar no piloto)*; senão, `get_page_text` no cabeçalho.
   - Se falhar: "Esta página não está disponível" → @ errado ou perfil removido: pergunte.
2. **Grade.** A do perfil (`/<usuario>/`) tem posts e reels (fase 01); a aba Reels
   (`/<usuario>/reels/`) tem só reels, com a contagem de reproduções sobre a miniatura
   *(a validar no piloto)* (fase 02).
   - Para carregar mais: **roda real** (`computer scroll`) com o cursor **sobre a grade** —
     `window.scrollTo` não carrega nada, e sobre os destaques a rolagem vira horizontal.
   - Confira: o número de itens lidos (passo 3) cresce a cada rolagem.
3. **Ler a grade** por JS, depois de rolar:
   ```js
   (() => {
     const ALFA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
     const data = sc => { let id = 0n;   // o shortcode carrega a data de publicação
       for (const c of sc.slice(0, 11)) id = id * 64n + BigInt(ALFA.indexOf(c));
       return new Date(Number(id >> 23n) + 1314220021721).toISOString().slice(0, 10); };
     const num = s => { const m = s.match(/(\d[\d.,]*)\s*(mil|mi|bi|k|m|b)?\b/i);
       const k = {mil: 1e3, k: 1e3, mi: 1e6, m: 1e6, bi: 1e9, b: 1e9}[(m[2] || '').toLowerCase()] || 1;
       return Math.round((k === 1 ? +m[1].replace(/[.,]/g, '') : +m[1].replace(',', '.')) * k); };
     const vistos = new Set();
     return [...document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]')].map(a => {
       const m = a.getAttribute('href').match(/\/(p|reel)\/([\w-]+)/);
       if (!m || vistos.has(m[2])) return null; vistos.add(m[2]);
       return {sc: m[2], tipo: m[1] === 'p' ? 'post' : 'reel', data: data(m[2]),
         numeros: (a.innerText.match(/\d[\d.,]*\s*(?:mil|mi|bi|k|m|b)?\b/gi) || []).map(num),
         fixado: !!a.querySelector('svg[aria-label*="ixad"], svg[aria-label*="inned"]')};
     }).filter(Boolean);
   })()
   ```
   - `data`: bateu com `<time datetime>` em 4 posts e com o carimbo de um post raspado (mesmo
     dia, 26 s de diferença). `num` lê "1,2 mil", "3,4 mi", "1.234", "1.2K", "3M".
   - `numeros` na aba Reels, sem hover: as reproduções *(a validar no piloto)*. Curtidas e
     comentários entram com **hover sintético** e uma 2ª leitura (medido na grade de posts):
     ```js
     document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]').forEach(a => {
       a.dispatchEvent(new PointerEvent('pointerover', {bubbles: true}));
       a.dispatchEvent(new MouseEvent('mouseover', {bubbles: true})); });
     ```
   - `fixado` procura o ícone de fixado pelo `aria-label` *(a validar no piloto)*.
   - Se falhar: `numeros` vazio em todos → a contagem não está no `innerText`: screenshot, ache
     onde ela está (`aria-label`, `span`, atributo), adapte e registre a lição.
4. **Ordenar**, **sem os fixados**, pela regra da fase: fase 02, **views por dia** (views ÷ dias
   desde a publicação, data pelo shortcode) dentro da janela de 7–90 dias — views brutas premiam
   o reel antigo; fase 01, cada post contra a **mediana do seu tipo** (curtidas nos posts, views
   nos reels). Abra os de topo que a fase pede — **só de perfil confirmado**.
5. **Abrir o reel** numa aba nova: `https://www.instagram.com/reel/<shortcode>/`. Silencie:
   `document.querySelectorAll('video').forEach(v => { v.muted = true; })`.
   - Leia: a legenda (o texto do autor no topo dos comentários; `get_page_text`, ou
     `meta[property="og:title"]` *(a validar no piloto)*), a data (`time[datetime]`) e a
     duração (`document.querySelector('video').duration`) *(a validar no piloto)*.
   - Confira: o texto lido é do autor do perfil, não de um comentário.
6. **Comentários** (fase 02, passo 8: os 3 reels de topo do nicho): os primeiros aparecem ao lado
   do vídeo, e o botão de carregar mais traz os seguintes *(a validar no piloto)*. Leia os 10
   primeiros por `get_page_text`; anote a ideia (pergunta, objeção), nunca quem comentou.
7. **Quadros para estudo.** O caminho completo — `watch`, download e transcrição — está em
   `assistir-video.md`. Sem a `watch`, pelo Chrome *(a validar no piloto)*:
   ```js
   (async t => { const v = document.querySelector('video'); v.muted = true; v.pause();
     v.currentTime = t;
     await new Promise(r => { v.addEventListener('seeked', r, {once: true}); setTimeout(r, 5000); });
     return v.currentTime; })(0.5)
   ```
   e screenshot (escala 0,3–0,5 basta) em 0,5, 1, 2, 3 e 5 s — os tempos da fase 02 —, até 10
   quadros por vídeo.
   - Confira: o quadro muda entre dois tempos (vídeo que não carregou devolve sempre o mesmo).
8. **Registrar só texto** no estudo da fase (`motion/concorrencia/estudo-<AAAA-MM-DD>.md`, ou o
   dossiê na fase 01): URL, data, views, duração, legenda resumida, o que se vê em cada quadro.

## Publicar (fase 09)

`file_upload` aceita no máximo 10 MB por chamada (`chrome.md` §3), e um Reel costuma passar
disso. O limite exato e o que fazer de cada lado dele (entregar ao usuário para publicar pelo app,
ou publicar com OK na hora) estão na fase 09 (9.500.000 bytes). A tela de criação não foi medida
*(a validar no piloto)*: screenshot antes de cada clique, e a mecânica que funcionar entra aqui.

## Terceiro é só texto

Reel, quadro, legenda e capa de outro perfil são estudo: viram descrição e número. Nunca pixel
do vídeo, nunca referência enviada ao ChatGPT, nem como estilo (`referencias.md`). Vídeo baixado
para estudo fica em `motion/concorrencia/videos/` e é apagado depois (`assistir-video.md`).
Número lido na tela muda com o tempo: escreva "lido em AAAA-MM-DD" ao lado de views e seguidores.
