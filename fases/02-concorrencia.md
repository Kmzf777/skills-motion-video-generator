# Fase 02 — Concorrência e referências de formato

Mede no quadro o que o nicho já entrega em Reels e onde ficam as lacunas que a marca pode
ocupar. A fase 03 escolhe a pauta a partir das lacunas deste estudo. **De concorrente e de
referência de formato, só texto e link**: reel, post e anúncio de outro perfil nunca viram
pixel do vídeo nem sobem ao ChatGPT como imagem. (Imagem genérica de Pinterest ou Google é
outra regra: `navegador/referencias.md`.)

## Quando

- Primeira peça; o estudo mais novo em `motion/concorrencia/` tem mais de 90 dias; a marca
  mudou de nicho ou de público; ou o usuário pediu.
- Existe estudo recente: pule a fase e leia o estudo.

## Entradas

- `motion/marca/dossie.md`: nicho e termos de busca, região, público, produtos foco.
- Chrome logado no Instagram: `navegador/chrome.md` e `navegador/instagram.md`.
- `navegador/assistir-video.md`: como baixar, assistir e medir um vídeo (com ou sem a skill
  `watch`), transcrever com o whisper.cpp e contar cortes com o `varrer_movimento`.
- `navegador/meta-anuncios.md` nos modos `oferta` e `vsl`.

## Passos

### Sugerir e confirmar
1. Levante candidatos por três caminhos: a **busca do Instagram** com 2–3 dos termos de
   busca do dossiê (seção Nicho; também termo + região), aba de contas; os perfis de
   empresa nos posts de topo de 1–2 **hashtags** do nicho; o **Google**, com
   `melhores <nicho> instagram` e `<nicho> <região> instagram`.
2. Filtre: mesmo nicho e faixa de preço; reel publicado nos últimos 30 dias; ao menos um
   reel muito acima da mediana de views do próprio perfil. Misture 1–2 maiores (o teto do
   nicho), 2–3 do tamanho da marca e quem disputa o mesmo nome ou a mesma região. Fique com
   **3 a 6**. Tamanho não é tração: perfil grande com views baixas sai.
3. Referências de **formato**, 1 a 3: contas de qualquer nicho, estudadas pela técnica, não
   pelo assunto. Onde procurar, nesta ordem: as contas que o usuário já admira (exemplo: no
   repositório de origem, o usuário trouxe um perfil de motion de colagem que admirava); a
   busca do Instagram e do Google por termos de formato (`motion design reels`, `colagem animada`, `collage animation`,
   `kinetic typography reels`); 1–2 hashtags de formato (ex.: `#collageanimation`,
   `#motiondesign`). Critério: motion de colagem ou tipografia cinética, com views altas
   para o tamanho da conta (reel com mais views que a conta tem de seguidores, ou muito
   acima da mediana do próprio perfil). Referência de formato ou de copy que está no
   YouTube se estuda do mesmo jeito, pela mesma página (`navegador/assistir-video.md`).
4. Mostre a tabela (perfil, seguidores, papel nicho ou formato, o porquê em uma linha) e
   confirme com AskUserQuestion: "Confirmo a lista" · "Quero trocar ou acrescentar" (campo
   livre, também para contas de formato que o usuário admira). A pergunta avisa que os
   reels estudados serão baixados para `motion/concorrencia/videos/` e apagados ao fim do
   estudo. Só perfil confirmado é estudado.

### Medir
5. Por perfil, na aba Reels: seguidores e, dos reels publicados **há 7 a 90 dias** (sem os
   fixados; a data sai do shortcode, `navegador/instagram.md`), as views. Escolha os **3 de
   topo por views por dia** (views ÷ dias desde a publicação): views brutas premiam o reel
   mais antigo. Menos de 3 na janela: estenda até 180 dias e anote. Nada de curtir,
   seguir, comentar, salvar ou abrir stories.
6. Assista a cada reel pela página `navegador/assistir-video.md`: ela diz como usar a
   `watch` sempre com o motor local (`--engine local --no-whisper`), o que fazer com o
   yt-dlp fora do PATH, como baixar pela sessão do Chrome e como rodar o whisper.cpp da
   semente e o `varrer_movimento.py`. O estudo é sempre quadros + transcrição pelo
   whisper.cpp + `varrer_movimento.py`; o motor gemini nunca se usa. Desta fase valem duas
   regras:
   - **no máximo 3 reels por perfil** e, por reel, no máximo ~10 quadros: 0,5 · 1 · 2 · 3 ·
     5 s e 4–5 no resto (meio, virada, CTA, fim);
   - o vídeo de terceiro baixado fica em `motion/concorrencia/videos/<id>`, com o `<id>` da
     página (`<perfil>_<shortcode>`), e `motion/concorrencia/videos/<id>*` é **apagado ao
     fim do estudo**; nunca vira pixel do vídeo nem sobe ao ChatGPT.
7. O que medir em cada reel:

   | Campo | Como |
   |---|---|
   | views, views por dia, data, duração | grade do perfil e o vídeo |
   | 1ª frase falada | transcrita pelo whisper.cpp (pela página); sem transcrição, `não verificável`. Conte as palavras |
   | gancho a 0,5 s | o que se vê e o texto na tela; o quadro faz sentido sem som? |
   | cortes por segundo | `varrer_movimento` no vídeo baixado (pela página), com três picos conferidos no quadro; só com quadros soltos, o limite inferior ("≥ N") |
   | sistemas de texto | legenda corrida (pílula), palavra que vira objeto, manchete fixa; posição, caixa, cor |
   | estrutura | segundo da promessa, da virada e do pagamento |
   | CTA | texto e segundo; isca ("comenta X que eu te mando") se anota como isca |
   | descrição | primeira linha, lida no post |

   Nas referências de formato, conte também os elementos que entram por segundo no gancho,
   numa folha de contato à parte do limite de ~10 quadros (é uma imagem só):
   `folha_do_video.py` com os instantes de 0 a 3 s a cada ¼ s, gravada em
   `motion/concorrencia/videos/<id>-folha.png` (o `<id>*` a apaga junto). Ela pede quadro, não segundo:
   `q = round(s × fps)`, com o fps lido do vídeo (`ffprobe`, ou a 1ª linha do
   `varrer_movimento.py`, `N quadros a F fps`); a 30 fps, `0,8,15,22,30,...,90`.
8. Nos 3 reels de topo do nicho, leia os 10 primeiros comentários: pergunta e objeção que se
   repetem são pauta. Anote a ideia, não quem comentou.
9. **Modos `oferta`/`vsl`**: Biblioteca de Anúncios da Meta (`navegador/meta-anuncios.md`),
   5–12 anunciantes, país do público, ativos, vídeo. Ativo há 30–60+ dias com várias versões é
   sinal, não prova. Só texto e link.

### Escrever
10. Grave `motion/concorrencia/estudo-<AAAA-MM-DD>.md` neste molde:

   ```markdown
   # Estudo de concorrência — <Marca> — AAAA-MM-DD
   Perfis confirmados por <pessoa> em AAAA-MM-DD. Método: aba Reels, 3 de topo por views por
   dia entre os publicados há 7–90 dias; medição no quadro (`navegador/assistir-video.md`).
   Terceiro: só texto e link.

   ## Perfis
   | Perfil | Papel (nicho/formato) | Seguidores | Reels por semana | Views medianas | Nota |

   ## Reels estudados
   | Perfil | Link | Data | Views (por dia) | Duração | 1ª frase (palavras) | Tela a 0,5 s | Cortes/s | Sistemas de texto | Estrutura (s da promessa, virada, pagamento) | CTA (s) | 1ª linha da descrição |

   ## Padrões
   O que se repete nos reels de topo, com a contagem ("4 de 12"): duração, gancho, ritmo,
   texto, CTA.

   ## Lacunas
   Assunto que o nicho não cobre, cobre raso ou erra; pergunta de comentário sem resposta.
   Uma por linha, com o link do reel que mostra a lacuna. É a entrada da fase 03.

   ## Anúncios (Biblioteca da Meta)
   Só em `oferta`/`vsl`: a tabela de `navegador/meta-anuncios.md` ("O que anotar"), com link e data.

   ## Formato
   Técnicas das referências, medidas: elementos por segundo no gancho, sistemas de texto,
   transições, câmera, som.

   ## Não copiar
   O que não transfere para esta marca: tom, verba, isca de engajamento, dado sem fonte.
   ```

11. Marque a origem com a régua da fase 01: número lido na grade ou no quadro é [medido];
    resumo de modelo e regra de criador não são medição; leitura sua diz que é leitura.

## Saídas

- `motion/concorrencia/estudo-<AAAA-MM-DD>.md`.

## Pronto quando

- A lista de perfis foi confirmada pelo usuário.
- Cada perfil tem 3 reels da janela de 7–90 dias (ou a ampliação anotada, ou o motivo de
  ter menos), com todos os campos preenchidos ou marcados `não verificável`.
- Há pelo menos 3 lacunas, cada uma com o reel que a mostra.
- `motion/concorrencia/videos/` está vazia, e o `git status` mostra que de
  `motion/concorrencia/` só o `estudo-*.md` vai para o commit.

## Erros comuns

- Escolher concorrente por seguidores: base grande feita de sorteio tem views baixas.
  Escolha por tração.
- Guardar vídeo de terceiro depois do estudo, ou subir reel, post ou anúncio de outro perfil
  ao ChatGPT como imagem: conteúdo de outro perfil vira só texto e link.
- Ler saída vazia como "não tem": confira o código de saída e a última linha do erro
  antes de concluir.
- Medir só o gancho: o meio e o fim (virada, CTA) também se medem; é deles que sai a
  estrutura que a fase 03 compara.
- Contar reel fixado, ou ordenar por views brutas: fora da janela de 7–90 dias e sem
  dividir pelos dias, o reel antigo sempre ganha.
- Curtir, seguir ou comentar com a conta do usuário.
