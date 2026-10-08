# Instalador da skill estudio-reels (Windows, PowerShell 5.1 ou mais novo).
#
#   irm https://raw.githubusercontent.com/Kmzf777/skills-motion-video-generator/main/instalar.ps1 | iex
#
# Clona o repositorio em $HOME\.claude\skills\estudio-reels ou, se ja for um clone dele,
# atualiza com `git pull --ff-only`. Nunca apaga nada: pasta existente que nao e clone deste
# repositorio faz o instalador parar e dizer como resolver. Nao instala Node nem Python; so avisa.
#
# Arquivo so em ASCII de proposito: o PowerShell 5.1 le .ps1 sem BOM na pagina de codigo do
# sistema, e acento viraria lixo. Variaveis de ambiente (para teste):
#   ESTUDIO_REELS_DESTINO  pasta de destino no lugar de $HOME\.claude\skills\estudio-reels
#   ESTUDIO_REELS_URL      repositorio a clonar no lugar do GitHub

function Instalar-EstudioReels {
    $url = 'https://github.com/Kmzf777/skills-motion-video-generator.git'
    if ($env:ESTUDIO_REELS_URL) { $url = $env:ESTUDIO_REELS_URL }
    $destino = Join-Path $HOME '.claude\skills\estudio-reels'
    if ($env:ESTUDIO_REELS_DESTINO) { $destino = $env:ESTUDIO_REELS_DESTINO }

    Write-Host "estudio-reels: instalando em $destino"

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host 'ERRO: git nao encontrado. Instale o git (https://git-scm.com/download/win) e rode de novo.' -ForegroundColor Red
        return 1
    }

    if (-not (Test-Path -LiteralPath $destino)) {
        $pai = Split-Path -Parent $destino
        if (-not (Test-Path -LiteralPath $pai)) { New-Item -ItemType Directory -Path $pai -Force | Out-Null }
        git clone --depth 1 $url $destino | Out-Host
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERRO: git clone falhou (codigo $LASTEXITCODE). Nada foi apagado." -ForegroundColor Red
            return 1
        }
        Write-Host 'Clone novo feito.'
    }
    else {
        $origem = $null
        if (Test-Path -LiteralPath (Join-Path $destino '.git')) {
            $origem = git -C $destino remote get-url origin 2>$null
            if ($LASTEXITCODE -ne 0) { $origem = $null }
        }
        if (-not $origem -or ((Normalizar-Url $origem) -ne (Normalizar-Url $url))) {
            Write-Host "PAROU: $destino ja existe e nao e um clone de $url." -ForegroundColor Yellow
            if ($origem) { Write-Host "  (e um repositorio git com origem $origem)" }
            Write-Host '  Nada foi apagado. Para resolver, escolha um:'
            Write-Host "  - guarde o que houver de seu e renomeie a pasta: Rename-Item `"$destino`" estudio-reels-antiga"
            Write-Host '    e rode o instalador de novo;'
            Write-Host "  - ou, se ja e uma copia sua da semente, aponte a origem: git -C `"$destino`" remote add origin $url"
            Write-Host '    (ou remote set-url) e rode de novo.'
            return 2
        }
        git -C $destino pull --ff-only | Out-Host
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERRO: git pull --ff-only falhou em $destino (mudanca local ou historico divergente)." -ForegroundColor Red
            Write-Host "  Nada foi apagado. Veja com: git -C `"$destino`" status"
            return 1
        }
        Write-Host 'Atualizado.'
    }

    $versao = '?'
    $arqVersao = Join-Path $destino 'VERSAO'
    if (Test-Path -LiteralPath $arqVersao) { $versao = (Get-Content -LiteralPath $arqVersao -TotalCount 1).Trim() }
    Write-Host ''
    Write-Host "estudio-reels $versao instalada em $destino" -ForegroundColor Green

    Conferir-Requisitos

    Write-Host ''
    Write-Host 'Proximo passo: abra o Claude Code na pasta do repositorio da empresa e peca um reel.'
    Write-Host 'Na primeira vez a skill se planta (fase 00). Repositorio ja plantado, traga a versao nova com:'
    Write-Host "  python `"$destino\modelo\plantar.py`" . --atualizar"
    return 0
}

function Normalizar-Url([string]$u) {
    $u = $u.Trim().Replace('\', '/').TrimEnd('/')
    if ($u.ToLower().EndsWith('.git')) { $u = $u.Substring(0, $u.Length - 4) }
    return $u.TrimEnd('/').ToLower()
}

function Conferir-Requisitos {
    # So avisa: nada aqui instala ou altera o sistema.
    $node = Get-Command node -ErrorAction SilentlyContinue
    if (-not $node) {
        Write-Host 'AVISO: Node.js nao encontrado. A skill precisa de Node >= 22.12 (https://nodejs.org).' -ForegroundColor Yellow
    }
    else {
        $v = (node --version) -replace '^v', ''
        $ok = $false
        try { $ok = ([version]$v -ge [version]'22.12.0') } catch { $ok = $false }
        if ($ok) { Write-Host "Node $v ok." }
        else { Write-Host "AVISO: Node $v encontrado; a skill precisa de Node >= 22.12." -ForegroundColor Yellow }
    }

    $pyVersao = $null
    foreach ($cmd in @('python', 'py')) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            $saida = & $cmd -c "import sys; print('%d.%d.%d' % sys.version_info[:3])" 2>$null
            if ($LASTEXITCODE -eq 0 -and $saida) { $pyVersao = "$saida".Trim(); break }
        }
    }
    if (-not $pyVersao) {
        Write-Host 'AVISO: Python nao encontrado. A skill precisa de Python >= 3.10 (https://www.python.org).' -ForegroundColor Yellow
    }
    else {
        $ok = $false
        try { $ok = ([version]$pyVersao -ge [version]'3.10.0') } catch { $ok = $false }
        if ($ok) { Write-Host "Python $pyVersao ok." }
        else { Write-Host "AVISO: Python $pyVersao encontrado; a skill precisa de Python >= 3.10." -ForegroundColor Yellow }
    }
}

$codigo = Instalar-EstudioReels
# Rodando como arquivo (-File), devolve o codigo de saida. Via `irm | iex` nao ha $PSCommandPath,
# e um `exit` fecharia a janela do usuario.
if ($PSCommandPath) { exit $codigo }
