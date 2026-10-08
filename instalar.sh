#!/usr/bin/env bash
# Instalador da skill estudio-reels (macOS, Linux e Git Bash).
#
#   curl -fsSL https://raw.githubusercontent.com/Kmzf777/skills-motion-video-generator/main/instalar.sh | bash
#
# Clona o repositório em ~/.claude/skills/estudio-reels ou, se já for um clone dele, atualiza
# com `git pull --ff-only`. Nunca apaga nada: pasta existente que não é clone deste repositório
# faz o instalador parar e dizer como resolver. Não instala Node nem Python; só avisa.
#
# Variáveis de ambiente (para teste):
#   ESTUDIO_REELS_DESTINO  pasta de destino no lugar de ~/.claude/skills/estudio-reels
#   ESTUDIO_REELS_URL      repositório a clonar no lugar do GitHub
set -euo pipefail

URL="${ESTUDIO_REELS_URL:-https://github.com/Kmzf777/skills-motion-video-generator.git}"
DESTINO="${ESTUDIO_REELS_DESTINO:-$HOME/.claude/skills/estudio-reels}"

normalizar() {
  # minúsculas, barra normal, sem barra final nem .git final
  local u
  u="$(printf '%s' "$1" | tr '\\' '/' | tr '[:upper:]' '[:lower:]')"
  u="${u%/}"
  u="${u%.git}"
  printf '%s' "${u%/}"
}

versao_ok() {
  # versao_ok <tem> <precisa>: 0 se <tem> >= <precisa> (números separados por ponto)
  local IFS=.
  local -a a=($1) b=($2)
  local i
  for i in 0 1 2; do
    local x="${a[i]:-0}" y="${b[i]:-0}"
    x="${x%%[!0-9]*}"; y="${y%%[!0-9]*}"
    x="${x:-0}"; y="${y:-0}"
    if ((10#$x > 10#$y)); then return 0; fi
    if ((10#$x < 10#$y)); then return 1; fi
  done
  return 0
}

conferir_requisitos() {
  # Só avisa: nada aqui instala ou altera o sistema.
  if command -v node >/dev/null 2>&1; then
    local v
    v="$(node --version 2>/dev/null || true)"
    v="${v#v}"
    if [ -n "$v" ] && versao_ok "$v" 22.12.0; then
      echo "Node $v ok."
    else
      echo "AVISO: Node ${v:-?} encontrado; a skill precisa de Node >= 22.12."
    fi
  else
    echo "AVISO: Node.js não encontrado. A skill precisa de Node >= 22.12 (https://nodejs.org)."
  fi

  local py="" pv=""
  for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then
      pv="$("$c" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || true)"
      if [ -n "$pv" ]; then py="$c"; break; fi
    fi
  done
  if [ -z "$py" ]; then
    echo "AVISO: Python não encontrado. A skill precisa de Python >= 3.10 (https://www.python.org)."
  elif versao_ok "$pv" 3.10.0; then
    echo "Python $pv ok."
  else
    echo "AVISO: Python $pv encontrado; a skill precisa de Python >= 3.10."
  fi
}

# Tudo dentro de main: com `curl | bash`, o bash lê o script inteiro antes de rodar a primeira
# linha, e nenhum comando consome o resto do script pela entrada padrão.
main() {
  echo "estudio-reels: instalando em $DESTINO"

  if ! command -v git >/dev/null 2>&1; then
    echo "ERRO: git não encontrado. Instale o git e rode de novo." >&2
    exit 1
  fi

  if [ ! -e "$DESTINO" ]; then
    mkdir -p "$(dirname "$DESTINO")"
    if ! git clone --depth 1 "$URL" "$DESTINO"; then
      echo "ERRO: git clone falhou. Nada foi apagado." >&2
      exit 1
    fi
    echo "Clone novo feito."
  else
    ORIGEM=""
    if [ -e "$DESTINO/.git" ]; then
      ORIGEM="$(git -C "$DESTINO" remote get-url origin 2>/dev/null || true)"
    fi
    if [ -z "$ORIGEM" ] || [ "$(normalizar "$ORIGEM")" != "$(normalizar "$URL")" ]; then
      echo "PAROU: $DESTINO já existe e não é um clone de $URL." >&2
      if [ -n "$ORIGEM" ]; then echo "  (é um repositório git com origem $ORIGEM)" >&2; fi
      echo "  Nada foi apagado. Para resolver, escolha um:" >&2
      echo "  - guarde o que houver de seu e renomeie a pasta: mv \"$DESTINO\" \"$DESTINO-antiga\"" >&2
      echo "    e rode o instalador de novo;" >&2
      echo "  - ou, se já é uma cópia sua da semente, aponte a origem:" >&2
      echo "    git -C \"$DESTINO\" remote add origin $URL   (ou remote set-url) e rode de novo." >&2
      exit 2
    fi
    if ! git -C "$DESTINO" pull --ff-only; then
      echo "ERRO: git pull --ff-only falhou em $DESTINO (mudança local ou histórico divergente)." >&2
      echo "  Nada foi apagado. Veja com: git -C \"$DESTINO\" status" >&2
      exit 1
    fi
    echo "Atualizado."
  fi

  VERSAO="?"
  if [ -f "$DESTINO/VERSAO" ]; then VERSAO="$(head -n 1 "$DESTINO/VERSAO" | tr -d '[:space:]')"; fi
  echo
  echo "estudio-reels $VERSAO instalada em $DESTINO"

  conferir_requisitos

  echo
  echo "Próximo passo: abra o Claude Code na pasta do repositório da empresa e peça um reel."
  echo "Na primeira vez a skill se planta (fase 00). Repositório já plantado, traga a versão nova com:"
  echo "  python \"$DESTINO/modelo/plantar.py\" . --atualizar"
}

main "$@"
