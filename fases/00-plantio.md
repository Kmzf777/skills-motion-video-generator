# Fase 00 — Plantio

Cria no repositório a cópia da skill (`.claude/skills/estudio-reels-<slug>/`) e o `motion/`
(motor Remotion, ferramentas Python, pastas da marca, biblioteca vazia e a peça de exemplo),
instala as dependências e confere que o motor compila e desenha. É a única fase que roda a
partir da semente: daqui em diante quem comanda é a cópia.

> Comandos em bash, da raiz do repositório. Na sessão, o **diretório atual do Bash persiste**
> entre chamadas (variável de shell, não): um `cd` solto deixa a próxima chamada fora da raiz.
> Por isso todo `cd` vai num subshell, `(cd motion/remotion && ...)`; no PowerShell,
> `Push-Location motion/remotion; ...; Pop-Location`. `<SEMENTE>` = `~/.claude/skills/estudio-reels`
> (no PowerShell, `$HOME/.claude/skills/estudio-reels`). Até o passo 5, `python` é o do sistema
> (`python3` no macOS/Linux); depois dele, as ferramentas rodam com o do `motion/.venv`.

## Quando

- Primeira vez da skill num repositório: não existe `.claude/skills/estudio-reels-*/`.
- Repositório que já tem `motion/` mas não tem a cópia: plantio normal. Nada que existe é
  sobrescrito; a saída lista o que ficou como estava.
- Clone novo ou máquina nova de um repositório já plantado: **não plante**. Faça só os passos 5
  (instalar) e 6 (conferir): `node_modules`, `motion/.venv` e o whisper.cpp não viajam pelo git,
  nem as pastas que ele ignora (recrie com
  `mkdir -p motion/pecas/00-exemplo/public motion/pecas/00-exemplo/saida motion/biblioteca/brutos`).
- Semente mais nova que a cópia: não é aqui, é o `--atualizar` (fase 10, parte C).

## Pré-requisitos

| Precisa | Como conferir |
|---|---|
| Chrome com a extensão Claude in Chrome conectada | carregar as ferramentas do Chrome numa busca só e listar as abas (`navegador/chrome.md`). Não trava o plantio; trava da fase 01 em diante |
| Contas logadas no Chrome: Instagram; ChatGPT com geração de imagem; ElevenLabs com crédito; Pinterest (opcional) | cada fase confere a sua ao abrir o site |
| Node ≥ 22.12 e npm (o motor declara `engines.node >=22.12.0`) | `node --version` · `npm --version` |
| Python ≥ 3.10 | `python --version` (macOS/Linux: `python3 --version`) |
| ~3 GB livres no disco do repositório | o comando abaixo |
| git | `git --version`: a fase 10 faz commit, e no macOS/Linux o whisper.cpp é clonado com ele |
| só macOS/Linux: `make` e compilador C/C++ | `make --version` · `cc --version`: lá o whisper.cpp é compilado na instalação (no Windows vem pronto) |

```bash
node --version; npm --version; python --version; git --version
python -c "import shutil; print(shutil.disk_usage('.').free // 2**30, 'GB livres')"
```

## Passos

1. **Vá para a raiz do repositório**: `git rev-parse --show-toplevel`. É ali que o Claude Code
   procura `.claude/skills/`; plantada numa subpasta, a cópia não é achada. Sem git
   (`not a git repository`), pergunte ao usuário qual é a pasta do projeto.
2. **Confira os pré-requisitos.** Faltou algum: pare e siga [Se algo faltar](#se-algo-faltar).
3. **Ache o nome da marca**: o que o público vê, não o nome da pasta. Procure no README, no
   `package.json`, no `CLAUDE.md` e no site. Na dúvida, uma pergunta ao usuário
   (AskUserQuestion, com os nomes que você achou como opções). O nome entra na descrição da
   cópia e dele sai o `<slug>`: "Café Teste" → `.claude/skills/estudio-reels-cafe-teste/`.
4. **Plante**:

   ```bash
   python "$HOME/.claude/skills/estudio-reels/modelo/plantar.py" . --marca "<Nome>"
   ```

   O script lê a semente inteira antes de escrever: semente incompleta, nome sem letra nem
   número, semente dentro do destino (ou o contrário) e cópia já plantada recusam com código 1,
   sem tocar em nada. Leia a saída:
   - o que entrou: skill, motor, ferramentas, exemplo, linhas do `.gitignore`, seção
     "Reels (estudio-reels)" do `CLAUDE.md` (criado se não existia);
   - **mantidos**: arquivos que já existiam com outro conteúdo e ficaram como estavam. Mostre
     a lista ao usuário: daqui em diante a semente os trata como do repositório;
   - recusa por cópia já plantada: é `--atualizar` (fase 10, parte C). Nunca apague a cópia
     para plantar de novo: ela guarda o que a marca aprendeu;
   - **parou no meio** (arquivo preso pelo sincronizador, caminho longo, disco cheio): corrija
     a causa e rode o mesmo comando. A cópia sem `motion/.plantio.json` é reconhecida como
     plantio interrompido e retomada, sem sobrescrever o que a rodada anterior gravou.
5. **Instale as dependências.** Diga ao usuário o que vai baixar antes (o `--plano` mostra os
   itens e o tamanho de cada um sem instalar nada) e rode a instalação em segundo plano, porque
   leva minutos. Repositório em pasta sincronizada (OneDrive, Dropbox): avise também que esses
   ~2 GB ficam dentro dela e o sincronizador vai subir tudo.

   ```bash
   python motion/ferramentas/instalar.py --plano
   python motion/ferramentas/instalar.py
   ```

   Ele cria `motion/.venv` com o `requirements.txt` (numpy, pillow, opencv, torch, torchaudio,
   pytest), roda `npm install` em `motion/remotion` e põe o whisper.cpp `small` (~490 MB) em
   `motion/ferramentas/whisper.cpp/`. O modelo de alinhamento (~1,2 GB) baixa depois, na
   primeira fase 05. `--sem-modelos` pula whisper.cpp, torch e torchaudio: serve para teste
   rápido, não para produzir, porque a fase 05 precisa dos três.

   Daqui em diante, `python motion/ferramentas/...` nas fases quer dizer o Python do venv:
   `motion/.venv/Scripts/python` no Windows, `motion/.venv/bin/python` no macOS/Linux.
6. **Conferência.** Tudo verde antes de seguir:

   ```bash
   (cd motion/remotion && npx tsc --noEmit && npx vitest run)
   ```

   ```bash
   motion/.venv/Scripts/python -m pytest motion/ferramentas/tests -q   # Windows
   motion/.venv/bin/python -m pytest motion/ferramentas/tests -q       # macOS/Linux
   ```

   ```bash
   (cd motion/remotion && npx remotion still src/index.ts Exemplo ../pecas/00-exemplo/saida/exemplo.png --frame=60 --public-dir=../pecas/00-exemplo/public)
   ```

   No PowerShell, o mesmo sem sair da raiz:

   ```powershell
   Push-Location motion/remotion; npx tsc --noEmit; if ($?) { npx vitest run }; Pop-Location
   Push-Location motion/remotion; npx remotion still src/index.ts Exemplo ../pecas/00-exemplo/saida/exemplo.png --frame=60 --public-dir=../pecas/00-exemplo/public; Pop-Location
   ```

   Abra o PNG e olhe: 1080×1920, a colagem de exemplo desenhada, nada em branco nem cortado.
   Vermelho aqui é defeito da instalação ou do motor: leia o erro e resolva agora. Motor
   quebrado só aparece de novo na fase 07, com a peça inteira montada em cima dele.
7. **A identidade ainda é de exemplo.** `motion/marca/identidade.json` sai com
   `"exemplo": true` e as cores e fontes do exemplo, porque sem ele o motor não compila. A
   fase 01 o troca pelo da marca; enquanto houver `"exemplo": true`, nenhuma peça vai ao ar.
8. **Ofereça o commit do plantio**, só com o que foi plantado:

   ```bash
   git add .claude/skills/estudio-reels-<slug> motion .gitignore CLAUDE.md
   git status --short
   git commit -m "estudio-reels <versão>: plantio para <Nome>"
   ```

   Confira no `status` que nada pesado entrou (`node_modules`, `.venv`, `whisper.cpp`, PNG da
   biblioteca, `__pycache__`: o `.gitignore` plantado cuida deles). O `motion/.plantio.json`
   entra: é a base que o `--atualizar` usa em qualquer clone.
9. **Siga para a fase 01** pelo `fases/01-contexto.md` **da cópia**. Se a cópia ainda não
   aparecer na lista de skills desta sessão, leia os arquivos dela pelo caminho.

## Se algo faltar

Pare e diga ao usuário, numa mensagem só, tudo o que falta e o comando exato para o sistema
dele. Não instale programa no sistema por conta própria. Depois que ele instalar, o PATH novo
só vale num terminal novo: peça para reabrir o Claude Code e confira de novo.

| Falta | O que dizer |
|---|---|
| Node ausente ou < 22.12 | Windows: `winget install OpenJS.NodeJS.LTS` · macOS: `brew install node` · Linux: Node LTS pelo gerenciador da distribuição ou por nodejs.org |
| Python ausente ou < 3.10 | Windows: `winget install Python.Python.3.12` · macOS: `brew install python@3.12` · Debian/Ubuntu: `sudo apt install python3 python3-venv` |
| git | Windows: `winget install Git.Git` · macOS: `xcode-select --install` · Debian/Ubuntu: `sudo apt install git` |
| `make` ou compilador (macOS/Linux) | macOS: `xcode-select --install` · Debian/Ubuntu: `sudo apt install build-essential` |
| espaço em disco | quanto há livre, quanto falta (~3 GB) e para onde vai: dependências do Remotion, whisper.cpp `small` (~490 MB), torch/torchaudio e o modelo de alinhamento (~1,2 GB, na fase 05) |
| Chrome ou a extensão | abrir o Chrome, instalar e ativar a extensão Claude in Chrome e conectá-la à sessão. O plantio segue; a fase 01 espera |
| conta deslogada ou sem crédito | quem descobre é a fase que usa o site: pare ali e peça. Nunca digite senha nem compre crédito |
| `instalar.py` falhou | o passo que falhou e a mensagem exata. Não repita às cegas: `ENOSPC` é disco, erro de rede ou proxy é conexão, `venv` ausente no Linux é o `python3-venv` |
| `git add` com `Filename too long` (Windows) | o caminho passou de 260 caracteres; proponha `git config core.longpaths true` neste repositório |
| `erro: o plantio parou no meio (...)` | a causa entre parênteses (arquivo preso pelo sincronizador, caminho longo, disco); depois de resolvida, o mesmo comando retoma |

## Saídas

- `.claude/skills/estudio-reels-<slug>/`: `SKILL.md` com `name` e `description` da marca,
  `fases/`, `navegador/`, `copy/`, `licoes.md`, `licoes-empresa.md` (só o cabeçalho) e
  `SEMENTE` (versão).
- `motion/`: `remotion/` com `node_modules`, `ferramentas/` com whisper.cpp, `.venv/`,
  `marca/identidade.json` de exemplo, `pecas/00-exemplo/`, `biblioteca/indice.json` (`[]`) e
  `categorias.json`, `concorrencia/`, `referencias/` e `.plantio.json` (sha256 do que a semente
  plantou).
- `.gitignore` com o bloco do estudio-reels; `CLAUDE.md` com a seção "Reels (estudio-reels)".

## Pronto quando

- `tsc`, `vitest` e `pytest` verdes, e o still do `Exemplo` aberto e olhado.
- A lista de "mantidos" (se houve) mostrada ao usuário.
- O usuário sabe que a identidade é de exemplo até a fase 01.
- O commit do plantio oferecido.

## Erros comuns

- **Plantar numa subpasta.** A cópia não vira skill do projeto. Raiz do git.
- **Plantar de novo por cima, ou apagar a cópia para plantar limpo.** A cópia guarda o que a
  marca aprendeu. Semente nova se puxa com `--atualizar`.
- **Pular a conferência.** O defeito reaparece na fase 07, debaixo de uma peça inteira.
- **Rodar ferramenta com o Python do sistema.** Falta numpy; e de dentro de `motion/remotion` o
  caminho relativo quebra. Raiz do repositório e Python do `motion/.venv`.
- **Instalar Node, Python ou git por conta própria.** É mudança no sistema do usuário: diga o
  comando, ele instala.
- **Dar `npm install` dentro da semente.** A semente é molde, não projeto; o motor se instala
  em `motion/remotion` do repositório.
