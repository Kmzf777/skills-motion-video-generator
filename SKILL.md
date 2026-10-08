---
name: estudio-reels
description: Use when the user wants Reels, motion, vertical video or narrated collage content for the company of the current repository and the repository has no estudio-reels-<marca> skill yet, or when asked to plant, update or promote the estudio-reels skill.
---

# estudio-reels — Reels em motion de colagem narrado

Produz, para a empresa do repositório aberto, Reels narrados em motion de colagem no padrão
da peça de origem (a peça 07 do repositório de origem, 79 s, aprovada pelo cliente como
"impecável"). Opera ChatGPT, ElevenLabs, Instagram e bancos de imagem pelo Chrome logado do
usuário (Claude in Chrome) e monta no Remotion. **Nenhuma API, nenhuma chave, nenhum cadastro.**

`<SEMENTE>` = `~/.claude/skills/estudio-reels` (no PowerShell, `$HOME/.claude/skills/estudio-reels`).

## Primeiro: quem comanda

Este arquivo existe em dois lugares. Veja de que pasta ele foi aberto:

| Pasta | O que é |
|---|---|
| `<SEMENTE>` | a **semente**: uma por máquina, versão em `VERSAO` |
| `<repo>/.claude/skills/estudio-reels-<marca>/` | a **cópia plantada**: uma por repositório, evolui com as lições da marca; o arquivo `SEMENTE` diz de que versão nasceu |

1. **Aberto da semente, e o repositório tem `.claude/skills/estudio-reels-*/`: pare e use
   aquela cópia** (leia o `SKILL.md` dela). Ela é a versão evoluída; a semente não sabe o que
   a marca já aprendeu.
2. **Aberto da semente, sem cópia no repositório**: fase 00, plantio. Vale também para
   repositório que já tem `motion/` sem a cópia: o plantio não sobrescreve o que existe.
3. **Aberto da cópia**: é ela que comanda. Se `<SEMENTE>/VERSAO` for mais nova que o arquivo
   `SEMENTE` daqui, ofereça atualizar (`fases/10-retrospectiva.md`, parte C).

## As fases

Leia cada fase **só quando chegar nela**: ler adiantado gasta contexto com o que a peça não precisa.

| Fase | Arquivo | Sai dela |
|---|---|---|
| 00 Plantio | `fases/00-plantio.md` | cópia da skill + `motion/` instalado e conferido |
| 01 Contexto | `fases/01-contexto.md` | `motion/marca/`: dossiê com fatos marcados, identidade, logo, banco de imagens |
| 02 Concorrência | `fases/02-concorrencia.md` | `motion/concorrencia/estudo-<data>.md` |
| 03 Roteiro | `fases/03-roteiro.md` | modo escolhido + `roteiro.txt` + texto com tags (+ 3 Big Ideas em `oferta`/`vsl`); **PARADA** |
| 04 Narração | `fases/04-narracao.md` | `public/fonte/narracao.mp3` (3 tomadas, uma escolhida) |
| 05 Tempo | `fases/05-tempo.md` | `palavras.json` conferido contra o áudio |
| 06 Assets | `fases/06-assets.md` | biblioteca + `public/colagem/` da peça |
| 07 Montagem | `fases/07-montagem.md` | composição Remotion da peça |
| 08 Conferência | `fases/08-conferencia.md` | `saida/reel.mp4` conferido em imagem, sincronia e áudio |
| 09 Publicação | `fases/09-publicacao.md` | `legenda-post.md` (orgânico) ou `anuncio.md` (modo oferta); publicar só com OK na hora |
| 10 Retrospectiva | `fases/10-retrospectiva.md` | lições, regras, commit; promoção e atualização |

01 e 02 só na primeira peça ou quando ficarem velhas; peça nova começa na 03, em `motion/pecas/NN-<tema>/`.

| Arquivo | O que é e quando ler |
|---|---|
| `navegador/` | mecânica de cada site: `chrome.md` (regras comuns) e a página do site (`instagram.md`, `chatgpt.md`, `elevenlabs.md`, `referencias.md`, `bancos-livres.md`, `meta-anuncios.md`); lidos antes de qualquer passo no Chrome |
| `copy/` | método de copy Kishōtenketsu por modo — educativo, oferta, vsl, geral —, oferta e criativo de anúncio; lido na fase 03 conforme o modo |
| `licoes.md` | lições universais; a seção "Onde olhar" diz que tema ler em cada fase |
| `licoes-empresa.md` | só na cópia: lições da marca, que nunca sobem, e universais que o usuário recusou promover, marcadas `[universal recusada em AAAA-MM-DD]`, que podem ser propostas de novo; lido inteiro antes de cada peça |

Comandos da raiz do repositório; `npx`/`node` de `motion/remotion`; Python do `motion/.venv` (fase 00).

## Regras que não se negociam

Conta e segurança (a autonomia não desliga nenhuma):

- Nunca publica, envia mensagem, compra crédito ou plano, aceita termos nem muda configuração
  de conta sem OK do usuário **naquele momento**.
- Anúncio: nunca cria, sobe, impulsiona nem edita campanha, nem gasta verba, sem OK do
  usuário na hora; o Gerenciador de Anúncios é só leitura.
- Sem crédito, deslogado ou captcha: para e avisa. Não resolve captcha; não digita senha,
  código nem dado de pagamento. Cookie e consentimento: a opção mais restritiva.

Conteúdo:

- Fato só com fonte **[oficial]** ou **[medido]**; sobre produto, só o que se lê no pixel.
- A pauta não acusa produto da empresa; dado em conflito entre fontes é `não verificável` e vira pergunta.
- Oferta: urgência e escassez só se forem reais (prazo ou lote verdadeiros); depoimento só real
  e autorizado; promessa só com prova [oficial]/[medido]; nicho regulado (saúde, finanças,
  suplemento, cosmético) segue a regra do setor. Detalhe em `copy/oferta.md`.
- Embalagem e logo entram como pixel real (recorte), nunca redesenhados por modelo.
- Rosto de pessoa real nunca é sintetizado.
- Conteúdo de outro perfil (reel, post, anúncio, concorrente ou não) **nunca** sobe ao ChatGPT
  nem vira pixel: vira só texto e link. Imagem genérica de Pinterest ou Google pode subir como
  referência de estilo, luz e paleta, sem rosto identificável, logo ou embalagem de outra marca
  nem marca d'água; o prompt proíbe copiar composição, objeto, texto e logo, o gerado é
  conferido lado a lado contra cópia, e ela nunca vira pixel do vídeo. Onde a regra do
  repositório for mais estrita, vale a do repositório.
- Na publicação, rótulo de IA ligado: a narração é sintética.

## Autonomia

Gera, avalia, refaz e baixa sozinho: narração, folhas de assets, recortes, renders. **Um único
ponto de parada: o roteiro** (fase 03) — em `oferta`/`vsl`, com as 3 Big Ideas e a conformidade
de `copy/oferta.md`. Mostre-o com a tabela fato → fonte e espere o OK antes do crédito de voz.
Fora dele, pergunte só o que a fase 01 não achou e o que as travas exigem; vídeo cedo, no teste.

## O ciclo

1. **Plantar** (fase 00), uma vez por repositório:
   `python <SEMENTE>/modelo/plantar.py . --marca "<Nome>"`.
2. **Produzir** (fases 01–09), uma peça de cada vez.
3. **Retrospectiva** (fase 10) ao fim de toda peça: falha vira lição (sintoma → causa raiz →
   regra); lição que muda procedimento vira regra na fase ou correção em `motion/`; commit.
4. **Promover**: a retrospectiva separa a lição da marca (fica em `licoes-empresa.md`) da
   universal (site, ferramenta, motor, método) e mostra a lista. O aprovado sobe para a semente
   (versão nova, commit no git dela); a universal recusada vai marcada para `licoes-empresa.md`.
5. **Atualizar**: `python <SEMENTE>/modelo/plantar.py . --atualizar` traz o que mudou na
   semente sem tocar em `licoes-empresa.md`, `motion/{marca,pecas,biblioteca}/` nem no que o
   repositório mudou; se os dois mudaram, a da semente fica ao lado (`<arquivo>.semente-<versão>`).

## Sinais de que você está saindo do padrão

| Pensamento | Realidade |
|---|---|
| "O repositório já tem `motion/`, não preciso plantar" | Sem a cópia não há fases nem lições aqui. Plante: o que existe fica. |
| "Rodo o plantio de novo para pegar a versão nova" | Ele recusa, com razão. É `--atualizar`. |
| "Corrijo na semente agora, é rapidinho" | Semente só muda pela promoção da fase 10, com OK do usuário. |
| "Já sei o processo, pulo a leitura da fase" | Cada fase guarda o que já custou uma rodada. Leia ao chegar. |
| "O roteiro está bom, gero a narração e mostro junto" | A parada é antes do crédito de voz. Espere o OK. |
| "O site pediu login, eu entro" | A sessão é do usuário. Pare e peça. |
