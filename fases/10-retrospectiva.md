# Fase 10 — Retrospectiva

Toda peça termina deixando a skill melhor. Foi assim que a peça de origem (a peça 07 do
repositório de origem) saiu de "fraquinha" para "impecável" numa sessão: erro que custou rodada
virou lição; lição que muda procedimento virou regra na fase ou correção no motor; defeito
que escapou do olho virou ferramenta. Erro não registrado se repete na próxima sessão.

`<SEMENTE>` = `~/.claude/skills/estudio-reels` (PowerShell: `$HOME/.claude/skills/estudio-reels`, ele não
expande `~` em argumento de programa); a cópia é `.claude/skills/estudio-reels-<slug>/`. Comando com `cd` roda
em subshell, `(cd … && …)`, porque o `cwd` do Bash da sessão persiste. No PowerShell 5.1 não existe `&&`:
`Push-Location motion/remotion; npx tsc --noEmit; if ($?) { npx vitest run }; Pop-Location`.

## Quando

- No fim de toda peça, entregue ou publicada.
- **Na hora** em que algo custar uma rodada (render refeito, imagem regerada, download errado,
  reclamação do usuário): escreva já, porque o resumo de contexto da sessão leva o detalhe.
- Promoção: no fim da retrospectiva, se houver lição universal nova.
- Atualização: `VERSAO` da semente maior que o `SEMENTE` da cópia, e logo depois de cada promoção.

## Entradas

- a conversa da peça: o que foi refeito, o que o usuário reprovou ou elogiou, o que se mediu
- da cópia: `licoes-empresa.md`, `licoes.md` (seção "Manutenção"), `fases/`, `navegador/`, `SEMENTE`
- da semente: `VERSAO`, `licoes.md` e o git dela (clone do repositório público, feito pelo
  instalador; a promoção commita nele, e o push é decisão de quem mantém o repositório)

## Passos

### A. Lições da peça

1. **Liste o que custou rodada**: cada render, geração, download ou narração refeitos, cada
   reclamação do usuário, cada suposição que se provou falsa. Mecânica nova de site que
   funcionou também entra: é o que a próxima sessão vai precisar. Modo `oferta`: leia cada
   variação no Gerenciador, só leitura (`navegador/meta-anuncios.md`); grave no `anuncio.md`;
   diagnostique pela tabela de `copy/criativos-anuncio.md`.
2. **Escreva no formato sintoma → causa raiz → regra**, em 3 a 8 linhas, com o número que
   prova a regra:

   ```markdown
   **TEMA-Pn.** **<sintoma: o que se viu, com o número medido>** → <causa raiz: o mecanismo
   que permitiu o erro> → **<regra: o que fazer da próxima vez, de um jeito que se confere>**
   (peça <NN>; <arquivo ou comando envolvido>)
   ```

   Em `licoes-empresa.md`, o mesmo formato com número simples e a fase na frente
   (`**3.** [fase 06] **<sintoma>** → …`).

   *Exemplo (repositório de origem, lição 62):* **O normalizador recusou o render final por 0,08 dB** →
   o `loudnorm` limitou o pico a −1 dBTP em PCM, e o encode AAC devolveu o pico a −0,62 dBTP no
   MP4 → **peça ao `loudnorm` um teto com margem para o AAC e verifique no arquivo escrito**.

   Régua: número medido ou caminho de arquivo ("tomar cuidado" não é regra); causa raiz é
   mecanismo, não "falta de atenção" nem o sintoma reescrito; regra diz o que fazer e como
   conferir; leitura não medida vai *(hipótese)*; relato de subagente é pista, não veredito.
3. **Decida onde a lição mora.**

   | A lição é sobre… | Mora em |
   |---|---|
   | a empresa: fato, produto, conta, voz, preferência do cliente, regra do repositório | `licoes-empresa.md` |
   | site, ferramenta, motor ou método (vale para qualquer empresa) | `licoes.md` da cópia, no fim do tema (`IMG`, `NAV`, `VID`, `AUD`, `MET`), com ID provisório `TEMA-P1`, `TEMA-P2`… |

   Regra da empresa não vai para o texto das fases: vira conflito sempre que a semente mexer na
   mesma fase. Repositório com registro de lições próprio, e lição que vale fora dos Reels: registre lá também.
4. **Decida o destino da regra.** A lição guarda o porquê; a fase, o motor ou a ferramenta mandam.

   | Se a lição… | Vira | Exemplo (peça de origem) |
   |---|---|---|
   | muda o que se faz num passo (passo novo, ordem, número, conferência) | regra no passo da fase onde teria evitado o erro; se nasceu de uma racionalização, linha em "Sinais de que você está saindo do padrão" | 60 tempos digitados à mão teriam ficado para trás num realinhamento de 0,7 s → "nenhum segundo digitado" na montagem |
   | pode ser impedida por código (valor derivado, trava que recusa) | correção em `motion/remotion/` ou `motion/ferramentas/`, com teste que reproduz o erro antes da correção | normalizador recusado por 0,08 dB → margem de pico do AAC no próprio motor |
   | escapou de uma conferência feita no olho | ferramenta nova de conferência | dessincronia que o cliente viu e o teste não pegava → fusão whisper + CTC e `conferir_alinhamento`; faixa preta que só existia dentro do chicote → `folha_do_video` com quadros dentro da janela |
   | é cuidado de contexto, sem mudar procedimento | só a lição | — |

   Regra que depende de lembrar é mais fraca que código que recusa: quando der para
   escolher, prefira a trava.
5. **Teste com agentes quando a mudança for grande** (fase reescrita, passo que muda a ordem,
   ferramenta nova, regra que contraria o texto anterior). Linha de base: um subagente recebe o
   cenário que falhou e a skill **sem** a mudança (`git show HEAD:<arquivo>` numa pasta temporária);
   anote onde ele erra. Depois, o mesmo cenário **com** a mudança: aceite quando ele segue o passo
   novo e cita o comando certo; errou, feche no texto e repita (`superpowers:writing-skills`, se houver).
6. **Commit no repositório**, por caminho, nunca `git add -A`:
   `git add .claude/skills/estudio-reels-<slug>/ <arquivos de motion/ que você mudou>` e
   `git commit -m "Peça <NN>: retrospectiva (lições ..., regra na fase ..., correção em ...)"`.

### B. Promoção para a semente

7. **Liste o que é universal e ainda não subiu**: as provisórias `TEMA-Pn` de `licoes.md`, as
   regras universais em `fases/`, `navegador/` ou `copy/` e as correções em `motion/` que não dependem da
   marca (`git log --oneline` desde o plantio ou a última atualização). Releia também as marcadas
   `[universal recusada em …]` em `licoes-empresa.md`: volta à lista só a que tiver fato novo
   (outra peça repetiu a falha). Tabela: o que é, tipo (site, ferramenta, motor, método), destino, patch ou minor.
8. **Peça OK**, item a item ou em bloco. Sem OK, nada sobe. A universal recusada sai de
   `licoes.md` e vai para `licoes-empresa.md` com a marca `[universal recusada em AAAA-MM-DD]`:
   continua valendo aqui, o `licoes.md` da cópia volta a espelhar o da semente, e ela **pode ser
   proposta de novo** numa retrospectiva futura ("agora não" não é "nunca"). Só a lição da marca nunca sobe.
9. **Aplique na semente**, onde cada parte da cópia tem seu lugar:

   | Na cópia | Na semente |
   |---|---|
   | `fases/`, `navegador/` | `fases/`, `navegador/` |
   | `copy/` | `copy/` |
   | provisória `TEMA-Pn` de `licoes.md` | `licoes.md`, no mesmo tema, com o próximo número livre (ID definitivo nunca muda nem se reaproveita) |
   | corpo do `SKILL.md` | `SKILL.md`, sem mexer no frontmatter da semente |
   | `motion/remotion/`, `motion/ferramentas/` | `modelo/remotion/`, `modelo/ferramentas/`, com o teste |

   - Leia antes o arquivo da semente: outro repositório pode tê-lo mudado desde o seu
     plantio. Aplique sobre a versão atual; nunca copie o arquivo da cópia por cima.
   - Procure se a lição já existe (`grep` em `<SEMENTE>/licoes.md`). Existindo, complete-a
     com o dado novo em vez de duplicar.
   - Tire tudo o que é da empresa (nome, produto, conta, @, caminho do repositório) e mantenha
     os números medidos. Caso concreto só entra marcado como exemplo.
   - Mudou `modelo/`? Conferência numa pasta temporária vazia `<tmp>`: plante primeiro e teste
     com o Python do venv plantado (o do sistema pode não ter pytest, numpy e pillow); no fim,
     abra o `saida.png`. Nunca `npm install` dentro da semente.
     - `(cd <tmp> && git init && python <SEMENTE>/modelo/plantar.py . --marca "Teste" && python motion/ferramentas/instalar.py --sem-modelos)`
     - `<tmp>/motion/.venv/bin/python -m pytest <SEMENTE>/modelo/tests <SEMENTE>/modelo/ferramentas/tests -q` (Windows: `.venv\Scripts\python.exe`)
     - `(cd <tmp>/motion/remotion && npx tsc --noEmit && npx vitest run && npx remotion still src/index.ts Exemplo saida.png --frame=60 --public-dir=../pecas/00-exemplo/public)`
10. **Suba `VERSAO`**: *patch* (1.0.0 → 1.0.1) para lição, regra reescrita numa fase ou
    correção de defeito em ferramenta ou motor; *minor* (1.0.x → 1.1.0) para fase nova,
    ferramenta nova, site novo em `navegador/` ou capacidade nova no motor; *major* só se o
    contrato quebrar (comando renomeado, `motion/` reestruturado), avisado no commit.
11. **Commit e tag no git da semente**. Confira no `status` que só as suas mudanças estão lá;
    se a versão anterior não tem tag, crie-a no commit dela, para o diff da atualização:

    ```bash
    git -C <SEMENTE> status --short
    git -C <SEMENTE> add -A
    git -C <SEMENTE> commit -m "estudio-reels 1.0.1: <o que entrou> (de <slug>, peça <NN>)"
    git -C <SEMENTE> tag v1.0.1
    ```

    Depois, atualize a cópia de origem (seção C): o que subiu volta na forma geral, com ID definitivo.

### C. Atualização de uma cópia

12. **Compare** o arquivo `SEMENTE` da cópia com `<SEMENTE>/VERSAO`. Semente mais nova: mostre ao
    usuário o que mudou (`git -C <SEMENTE> log --oneline v<versão da cópia>..HEAD`) e peça OK.
    Antes, toda provisória `TEMA-Pn` tem que estar promovida ou em `licoes-empresa.md`, e o pendente
    do repositório, commitado: a atualização fica isolada num commit e pode ser desfeita.
13. **Rode, da raiz do repositório**: `python <SEMENTE>/modelo/plantar.py . --atualizar`. Para cada
    arquivo plantado (skill, `motion/remotion/`, `motion/ferramentas/`) ele compara a versão
    plantada, a do repositório e a da semente nova: só a semente mudou → copia; só o repositório
    mudou → mantém; os dois mudaram → **conflito**: mantém o do repositório e grava a nova ao lado,
    `<arquivo>.semente-<versão>`. Nunca toca em `licoes-empresa.md` nem em
    `motion/{marca,pecas,biblioteca,concorrencia,referencias}/`; grava a versão nova no `SEMENTE` da cópia.
14. **Resolva cada conflito** (`git diff --no-index -- <arquivo> <arquivo>.semente-<versão>`):
    grave o resultado em `<arquivo>` e apague o `.semente-*` (o próximo `--atualizar` lista os
    que sobrarem). Conflito de arquivo apagado de um lado: decida se ele ainda faz sentido.

    | O repositório mudou o arquivo porque… | Fique com |
    |---|---|
    | a mudança é universal e foi promovida | a versão da semente |
    | a mudança é universal e não foi promovida | promova (passos 7–11), depois a da semente |
    | a mudança é da empresa | a do repositório, trazendo à mão a mudança da semente; melhor ainda, mova a regra para `licoes-empresa.md` e fique com a da semente |
    | `licoes.md` | a da semente: as provisórias já subiram ou foram para `licoes-empresa.md` |

15. **Confira e registre.** Dependências mudaram (o script avisa)? `python motion/ferramentas/instalar.py`.
    Conferência da fase 00: `(cd motion/remotion && npx tsc --noEmit && npx vitest run)` e, da
    raiz, `python -m pytest motion/ferramentas/tests -q`. Commit, como o próprio script pede, dos
    arquivos listados **mais** o `SEMENTE` da cópia e o `motion/.plantio.json`: sem ele, outro
    clone do repositório ganha conflito falso no próximo `--atualizar`.
    - `git add <arquivos listados> .claude/skills/estudio-reels-<slug>/SEMENTE motion/.plantio.json`
    - `git commit -m "estudio-reels: cópia atualizada para a semente X.Y.Z"`

## Saídas

- lições gravadas (`licoes-empresa.md` e `licoes.md` da cópia), regras e correções aplicadas
- commit no repositório; se aprovado, semente com `VERSAO` nova, commit e tag

## Pronto quando

- toda rodada perdida na peça virou lição, ou foi descartada com o motivo dito ao usuário
- cada lição está no arquivo certo e no formato sintoma → causa raiz → regra
- lição que muda procedimento virou regra na fase, ou correção com teste
- lista de promoção apresentada; o aprovado está na semente (versão nova, commit e tag) e a
  cópia de origem foi atualizada; o recusado está em `licoes-empresa.md` com a marca
  `[universal recusada em AAAA-MM-DD]`

## Erros comuns

- **Lição vaga** ("ter mais cuidado com o chicote"): sem número nem conferência, não muda nada.
- **Subir `VERSAO` sem commit, ou commitar sem subir**: as cópias não percebem a atualização.
- **Copiar o `.semente-*` por cima sem ler** (apaga a evolução da cópia) **ou esquecê-lo no
  repositório** (o arquivo de verdade fica velho e o lixo vai para o commit).
