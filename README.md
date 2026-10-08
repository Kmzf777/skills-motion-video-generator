# estudio-reels

Skill do [Claude Code](https://claude.com/claude-code) que produz Reels narrados em **motion de
colagem** (9:16, câmera 2.5D, legenda em dois sistemas, tempo lido da narração) para a empresa
do repositório em que você está. Ela pesquisa a marca e os concorrentes, escreve o roteiro com
cada fato amarrado a uma fonte, para para o seu OK, gera a narração e os assets, monta no
[Remotion](https://www.remotion.dev/), confere voz × legenda no áudio e entrega o vídeo com a
descrição do post.

**Nenhuma API, nenhuma chave.** ChatGPT, ElevenLabs, Instagram e bancos de imagem são operados
pelo seu Chrome logado (extensão Claude in Chrome); o resto roda local.

## Instalação

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/Kmzf777/skills-motion-video-generator/main/instalar.ps1 | iex
```

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/Kmzf777/skills-motion-video-generator/main/instalar.sh | bash
```

A skill vai para `~/.claude/skills/estudio-reels` (Windows: `$HOME\.claude\skills\estudio-reels`).
O instalador só clona ou atualiza esse clone: não instala Node, Python nem pacotes, e nunca
apaga uma pasta que já exista ali.

## Requisitos

- Claude Code.
- Google Chrome com a extensão **Claude in Chrome** conectada e as contas logadas: ChatGPT,
  ElevenLabs e Instagram.
- Node.js **≥ 22.12** e npm.
- Python **≥ 3.10**.
- git.
- ~3 GB livres por repositório (motor Remotion, venv com whisper e alinhador, modelos).

## Uso

Abra o Claude Code na pasta do repositório da empresa e peça um reel ("faz um reel sobre…").
Na primeira vez a skill se planta (fase 00): cria `.claude/skills/estudio-reels-<marca>/`, a
cópia que evolui com as lições daquela marca, e `motion/`, com o motor e as ferramentas
instalados e conferidos. Daí em diante as fases seguem até o vídeo; a única parada obrigatória é
o OK do roteiro, antes de qualquer crédito gasto.

## Atualização

Rode de novo a mesma linha de instalação. Depois, em cada repositório que já tem a skill
plantada, traga as mudanças para a cópia:

```bash
python ~/.claude/skills/estudio-reels/modelo/plantar.py . --atualizar
```

(No PowerShell: `python "$HOME\.claude\skills\estudio-reels\modelo\plantar.py" . --atualizar`.)
Arquivo que você mudou na cópia não é sobrescrito: o conflito vira `<arquivo>.semente-<versão>`
ao lado, para você decidir.

A versão instalada está no arquivo `VERSAO`.
