"""Testes do plantio da semente estudio-reels (modelo/plantar.py).

Rodar da raiz da semente:

    python -m pytest modelo/tests/test_plantar.py -q

A semente usada nos testes é FABRICADA em tmp_path: eles não dependem do motor
(modelo/remotion) nem das ferramentas (modelo/ferramentas) existirem. O plantio é
chamado pela linha de comando, como as fases mandam rodar. Os testes do fim leem a semente
REAL (SKILL.md e fase 00) e plantam a semente real, este último pulado enquanto ela estiver
incompleta.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

MODELO = Path(__file__).resolve().parents[1]
SEMENTE_REAL = MODELO.parent
PLANTAR = MODELO / "plantar.py"

SKILL = ".claude/skills/estudio-reels-cafe-teste"

# Contrato C2 com os acréscimos do orquestrador (brutos/ guarda .jpg de banco livre;
# concorrencia/videos/ guarda vídeo de terceiro; de public/ só a narração final entra no
# git, porque é dela que saem os tempos do palavras.json): linhas do .gitignore.
LINHAS_NARRACAO = [  # a ordem importa: cada linha desfaz parte da anterior
    "motion/pecas/*/public/*",
    "!motion/pecas/*/public/fonte/",
    "motion/pecas/*/public/fonte/*",
    "!motion/pecas/*/public/fonte/narracao.mp3",
]
LINHAS_GITIGNORE = [
    "motion/remotion/node_modules/",
    "motion/remotion/out/",
    "motion/.venv/",
    "motion/biblioteca/**/*.png",
    "motion/biblioteca/brutos/",
    *LINHAS_NARRACAO,
    "motion/pecas/*/saida/",
    "motion/concorrencia/videos/",
    "motion/ferramentas/whisper.cpp/",
]
# Além do C2: cache que as ferramentas e o pytest deixam dentro de motion/ (o commit do
# plantio é `git add motion`, e nem todo repositório ignora __pycache__).
LINHAS_GITIGNORE_CACHE = [
    "motion/**/__pycache__/",
    "motion/**/.pytest_cache/",
]

# Contrato C4: categorias padrão da biblioteca.
CATEGORIAS = [
    "objeto", "utensilio", "natureza", "alimento", "produto",
    "foto-real", "textura", "papelaria", "grafismo", "maos",
]

DESCRICAO_DA_MARCA = (
    "description: Use when producing or auditing any Reel, motion or vertical video for "
    "Café Teste in this repository — copy, narração ElevenLabs, sincronia de legenda, "
    "assets de colagem, render Remotion, conferência, descrição do post — or when the "
    "reels skill of this repo must learn from a failure."
)

SKILL_DA_SEMENTE = (
    "---\n"
    "name: estudio-reels\n"
    "description: Use when the user wants Reels for the company of the current repository.\n"
    "---\n"
    "\n"
    "# estudio-reels\n"
    "\n"
    "Corpo do maestro, igual na semente e na cópia.\n"
)

IDENTIDADE_EXEMPLO = {
    "marca": "Nome da Marca",
    "slug": "nome-da-marca",
    "idioma": "pt-BR",
    "cores": {"escuro": "#121417", "claro": "#F3F3F0"},
    "exemplo": False,
}

PALAVRAS_EXEMPLO = '[{"palavra": "Oi", "inicio": 0.1, "fim": 0.4}]\n'


# ---------------------------------------------------------------- utilidades

def escrever(raiz: Path, arquivos: dict[str, str]) -> None:
    """Grava texto em UTF-8 com fim de linha LF (o Windows trocaria por CRLF)."""
    for rel, texto in arquivos.items():
        caminho = raiz / rel
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(texto, encoding="utf-8", newline="\n")


def ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def fabricar_semente(raiz: Path, versao: str = "1.0.0") -> Path:
    semente = raiz / "semente"
    escrever(semente, {
        "VERSAO": versao + "\n",
        "SKILL.md": SKILL_DA_SEMENTE,
        "fases/00-plantio.md": "# 00 plantio v1\n",
        "fases/03-roteiro.md": "# 03 roteiro v1\n",
        "fases/05-tempo.md": "# 05 tempo v1\n",
        "navegador/chrome.md": "# chrome v1\n",
        "navegador/velho.md": "# velho v1\n",
        "copy/kishotenketsu.md": "# copy v1\n",
        "licoes.md": "# licoes v1\n",
        "modelo/remotion/package.json": '{"name": "motor", "versao": 1}\n',
        "modelo/remotion/src/index.ts": "export const v = 1;\n",
        "modelo/remotion/node_modules/lixo/index.js": "// nunca copiar\n",
        "modelo/ferramentas/biblioteca.py": "# biblioteca v1\n",
        "modelo/ferramentas/instalar.py": "# instalar v1\n",
        "modelo/ferramentas/__pycache__/biblioteca.cpython-312.pyc": "lixo\n",
        "modelo/exemplo/identidade.json": json.dumps(IDENTIDADE_EXEMPLO, ensure_ascii=False, indent=2) + "\n",
        "modelo/exemplo/00-exemplo/palavras.json": PALAVRAS_EXEMPLO,
        "modelo/exemplo/00-exemplo/roteiro.txt": "Oi.\n",
        "modelo/exemplo/00-exemplo/sons.json": '{"bpm": 88, "secoes": []}\n',
    })
    return semente


def rodar(repo: Path, *args: str, semente: Path | None = None) -> subprocess.CompletedProcess:
    comando = [sys.executable, str(PLANTAR), str(repo), *args]
    if semente is not None:
        comando += ["--semente", str(semente)]
    ambiente = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        comando, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=ambiente, timeout=120,
    )


def plantar_ok(repo: Path, *args: str, semente: Path | None = None) -> subprocess.CompletedProcess:
    resultado = rodar(repo, *args, semente=semente)
    assert resultado.returncode == 0, (
        f"plantar.py saiu {resultado.returncode}\n"
        f"--- stdout\n{resultado.stdout}\n--- stderr\n{resultado.stderr}"
    )
    return resultado


def retrato(raiz: Path, pastas: tuple[str, ...]) -> dict[str, bytes]:
    """Arquivos e bytes de cada um sob as pastas: igualdade = nada criado, apagado ou mudado."""
    return {
        caminho.relative_to(raiz).as_posix(): caminho.read_bytes()
        for pasta in pastas
        for caminho in sorted((raiz / pasta).rglob("*"))
        if caminho.is_file()
    }


def carregar_plantar():
    spec = importlib.util.spec_from_file_location("plantar", PLANTAR)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = modulo  # @dataclass procura o módulo aqui
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture
def ambiente(tmp_path: Path) -> tuple[Path, Path]:
    semente = fabricar_semente(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    return semente, repo


# ---------------------------------------------------------------- plantio

def test_planta_a_skill_com_o_nome_da_marca(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    skill = ler(repo / SKILL / "SKILL.md")
    linhas = skill.splitlines()
    assert linhas[0] == "---"
    assert "name: estudio-reels-cafe-teste" in linhas
    assert DESCRICAO_DA_MARCA in linhas
    assert "name: estudio-reels" not in linhas
    assert skill.endswith("Corpo do maestro, igual na semente e na cópia.\n")

    for rel in ("fases/00-plantio.md", "fases/03-roteiro.md", "navegador/chrome.md",
                "copy/kishotenketsu.md", "licoes.md"):
        assert (repo / SKILL / rel).read_bytes() == (semente / rel).read_bytes(), rel
    licoes_empresa = ler(repo / SKILL / "licoes-empresa.md")
    assert licoes_empresa.startswith("# ")
    assert "[universal recusada em AAAA-MM-DD]" in licoes_empresa


def test_copia_motor_e_ferramentas_sem_node_modules_nem_cache(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    assert (repo / "motion/remotion/package.json").read_bytes() == (
        semente / "modelo/remotion/package.json").read_bytes()
    assert (repo / "motion/remotion/src/index.ts").is_file()
    assert (repo / "motion/ferramentas/biblioteca.py").is_file()
    assert (repo / "motion/ferramentas/instalar.py").is_file()
    assert not (repo / "motion/remotion/node_modules").exists()
    assert not (repo / "motion/ferramentas/__pycache__").exists()


def test_arquivo_semente_guarda_a_versao_lida_de_versao(tmp_path):
    semente = fabricar_semente(tmp_path, versao="1.4.2")
    repo = tmp_path / "repo"
    repo.mkdir()
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    assert ler(repo / SKILL / "SEMENTE").strip() == "1.4.2"


def test_identidade_de_exemplo_e_peca_00_existem_depois_do_plantio(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    identidade = json.loads(ler(repo / "motion/marca/identidade.json"))
    assert identidade["exemplo"] is True
    assert identidade["marca"] == "Café Teste"
    assert identidade["slug"] == "cafe-teste"
    assert identidade["cores"] == IDENTIDADE_EXEMPLO["cores"]
    assert ler(repo / "motion/pecas/00-exemplo/palavras.json") == PALAVRAS_EXEMPLO
    assert (repo / "motion/pecas/00-exemplo/roteiro.txt").is_file()
    assert (repo / "motion/pecas/00-exemplo/sons.json").is_file()


def test_cria_as_pastas_de_c2_a_biblioteca_vazia_e_as_categorias_padrao(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    for pasta in ("motion/marca/fontes", "motion/concorrencia", "motion/referencias",
                  "motion/biblioteca/pecas"):
        assert (repo / pasta / ".gitkeep").is_file(), pasta
    # brutos/ é ignorado pelo git inteiro: existe no disco, sem .gitkeep que nunca entraria
    assert (repo / "motion/biblioteca/brutos").is_dir()
    assert not (repo / "motion/biblioteca/brutos/.gitkeep").exists()
    # public/ da peça: só o que alguma ferramenta grava (o publicar põe tudo em colagem/)
    for pasta in ("fonte", "colagem", "sfx"):
        assert (repo / "motion/pecas/00-exemplo/public" / pasta).is_dir(), pasta
    assert not (repo / "motion/pecas/00-exemplo/public/assets").exists()
    assert json.loads(ler(repo / "motion/biblioteca/indice.json")) == []
    assert json.loads(ler(repo / "motion/biblioteca/categorias.json")) == CATEGORIAS


def test_registro_do_plantio_guarda_o_sha256_de_cada_arquivo_copiado(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    registro = json.loads(ler(repo / "motion/.plantio.json"))
    assert registro["semente"] == "1.0.0"
    assert registro["marca"] == "Café Teste"
    assert registro["slug"] == "cafe-teste"
    arquivos = registro["arquivos"]
    esperados = {
        f"{SKILL}/SKILL.md", f"{SKILL}/fases/03-roteiro.md", f"{SKILL}/navegador/chrome.md",
        f"{SKILL}/copy/kishotenketsu.md",
        f"{SKILL}/licoes.md", "motion/remotion/package.json", "motion/remotion/src/index.ts",
        "motion/ferramentas/biblioteca.py", "motion/marca/identidade.json",
        "motion/pecas/00-exemplo/palavras.json",
    }
    assert esperados <= set(arquivos)
    for rel, sha in arquivos.items():
        assert sha == hashlib.sha256((repo / rel).read_bytes()).hexdigest(), rel
    assert not any("node_modules" in rel or "__pycache__" in rel for rel in arquivos)


def test_gitignore_recebe_as_linhas_de_c2_uma_vez_so(ambiente):
    semente, repo = ambiente
    escrever(repo, {".gitignore": "node_modules/\nmotion/.venv/\n"})

    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    plantar_ok(repo, "--atualizar", semente=semente)

    linhas = [linha.strip() for linha in ler(repo / ".gitignore").splitlines()]
    assert linhas[0] == "node_modules/"
    for linha in LINHAS_GITIGNORE + LINHAS_GITIGNORE_CACHE:
        assert linhas.count(linha) == 1, linha
    posicoes = [linhas.index(linha) for linha in LINHAS_NARRACAO]
    assert posicoes == sorted(posicoes)  # fora de ordem, a negação não desfaz nada


@pytest.mark.skipif(shutil.which("git") is None, reason="git ausente nesta máquina")
def test_gitignore_guarda_no_git_so_a_narracao_final_de_public(ambiente):
    semente, repo = ambiente
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    ignorado = {
        "motion/pecas/01-tema/public/colagem/x.png": True,
        "motion/pecas/01-tema/public/fonte/narracao-tomada-1.mp3": True,
        "motion/pecas/01-tema/public/sfx/pop.wav": True,
        "motion/pecas/01-tema/saida/reel.mp4": True,
        "motion/concorrencia/videos/terceiro.mp4": True,
        "motion/biblioteca/brutos/foto.jpg": True,
        "motion/remotion/out/Exemplo.mp4": True,
        "motion/pecas/01-tema/public/fonte/narracao.mp3": False,
        "motion/pecas/01-tema/palavras.json": False,
    }
    escrever(repo, {rel: "x\n" for rel in ignorado})

    for rel, esperado in ignorado.items():
        resultado = subprocess.run(["git", "-C", str(repo), "check-ignore", "-q", rel],
                                   capture_output=True, text=True)
        assert resultado.returncode in (0, 1), resultado.stderr  # 128 seria erro do git
        assert (resultado.returncode == 0) is esperado, rel


def test_gitignore_sem_quebra_de_linha_no_fim_nao_gruda_a_primeira_linha(ambiente):
    semente, repo = ambiente
    escrever(repo, {".gitignore": "dist/"})

    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    linhas = [linha.strip() for linha in ler(repo / ".gitignore").splitlines()]
    assert "dist/" in linhas
    assert all(linha in linhas for linha in LINHAS_GITIGNORE)


def test_claude_md_ganha_a_secao_uma_vez_so(ambiente):
    semente, repo = ambiente
    escrever(repo, {"CLAUDE.md": "# Projeto\n\nRegras da casa.\n"})

    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    plantar_ok(repo, "--atualizar", semente=semente)

    texto = ler(repo / "CLAUDE.md")
    assert texto.startswith("# Projeto\n\nRegras da casa.\n")
    assert texto.count("## Reels (estudio-reels)") == 1
    assert ".claude/skills/estudio-reels-cafe-teste/" in texto


def test_claude_md_e_criado_quando_nao_existe(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    assert "## Reels (estudio-reels)" in ler(repo / "CLAUDE.md")


def test_plantar_de_novo_sem_atualizar_recusa_e_nao_toca_na_copia(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    escrever(repo, {f"{SKILL}/fases/03-roteiro.md": "# 03 evoluído no repo\n"})

    resultado = rodar(repo, "--marca", "Café Teste", semente=semente)

    assert resultado.returncode == 1
    assert "--atualizar" in resultado.stderr
    assert ler(repo / SKILL / "fases/03-roteiro.md") == "# 03 evoluído no repo\n"


def test_plantar_outra_marca_num_repo_ja_plantado_recusa(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    resultado = rodar(repo, "--marca", "Outra Marca", semente=semente)

    assert resultado.returncode == 1
    assert "estudio-reels-cafe-teste" in resultado.stderr
    assert not (repo / ".claude/skills/estudio-reels-outra-marca").exists()


def test_repo_com_motion_e_sem_a_copia_planta_sem_sobrescrever_o_que_existe(ambiente):
    semente, repo = ambiente
    escrever(repo, {
        "motion/marca/identidade.json": '{"marca": "Café Teste", "exemplo": false}\n',
        "motion/remotion/package.json": '{"name": "motor-do-repo"}\n',
        "motion/biblioteca/indice.json": '[{"id": "x"}]\n',
    })

    resultado = plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    assert ler(repo / "motion/marca/identidade.json") == '{"marca": "Café Teste", "exemplo": false}\n'
    assert ler(repo / "motion/remotion/package.json") == '{"name": "motor-do-repo"}\n'
    assert ler(repo / "motion/biblioteca/indice.json") == '[{"id": "x"}]\n'
    assert (repo / SKILL / "SKILL.md").is_file()
    assert (repo / "motion/remotion/src/index.ts").is_file()
    assert "motion/remotion/package.json" in resultado.stdout

    # e uma atualização depois continua tratando o arquivo como do repositório
    escrever(semente, {"VERSAO": "1.1.0\n", "modelo/remotion/package.json": '{"name": "motor", "versao": 2}\n'})
    plantar_ok(repo, "--atualizar", semente=semente)
    assert ler(repo / "motion/remotion/package.json") == '{"name": "motor-do-repo"}\n'
    assert ler(repo / "motion/remotion/package.json.semente-1.1.0") == '{"name": "motor", "versao": 2}\n'


# ---------------------------------------------------------------- atualização

def test_atualizar_puxa_o_que_a_semente_mudou_e_preserva_o_que_e_do_repo(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)

    # o repositório evolui por conta própria
    escrever(repo, {
        f"{SKILL}/licoes-empresa.md": "# Lições da marca\n\n1. Lição que só vale aqui.\n",
        f"{SKILL}/fases/00-plantio.md": "# 00 evoluído no repo\n",   # só o repo mudou
        f"{SKILL}/fases/05-tempo.md": "# 05 evoluído no repo\n",      # os dois mudam
        "motion/marca/identidade.json": '{"marca": "Café Teste", "exemplo": false}\n',
        "motion/pecas/01-tema/roteiro.txt": "Fala da peça 1.\n",
        "motion/biblioteca/indice.json": '[{"id": "2026-10-07_xicara"}]\n',
        "motion/biblioteca/categorias.json": '["objeto", "embalagem"]\n',
    })
    protegidas = ("motion/marca", "motion/pecas", "motion/biblioteca")
    antes = retrato(repo, protegidas)
    # a semente ganha versão nova
    escrever(semente, {
        "VERSAO": "1.1.0\n",
        "fases/03-roteiro.md": "# 03 roteiro v2\n",
        "fases/05-tempo.md": "# 05 tempo v2\n",
        "navegador/instagram.md": "# instagram novo\n",
        "copy/kishotenketsu.md": "# copy v2\n",
        "copy/oferta.md": "# oferta nova\n",
        "licoes.md": "# licoes v2\n",
        "modelo/remotion/src/index.ts": "export const v = 2;\n",
        "modelo/ferramentas/biblioteca.py": "# biblioteca v2\n",
        "modelo/ferramentas/sons.py": "# sons novo\n",
        "modelo/exemplo/identidade.json": '{"marca": "Exemplo v2", "exemplo": true}\n',
        "modelo/exemplo/00-exemplo/palavras.json": "[]\n",
    })

    resultado = plantar_ok(repo, "--atualizar", semente=semente)

    # puxou o que só a semente mudou e o que é novo
    assert ler(repo / SKILL / "fases/03-roteiro.md") == "# 03 roteiro v2\n"
    assert ler(repo / SKILL / "navegador/instagram.md") == "# instagram novo\n"
    assert ler(repo / SKILL / "copy/kishotenketsu.md") == "# copy v2\n"
    assert ler(repo / SKILL / "copy/oferta.md") == "# oferta nova\n"
    assert ler(repo / SKILL / "licoes.md") == "# licoes v2\n"
    assert ler(repo / "motion/remotion/src/index.ts") == "export const v = 2;\n"
    assert ler(repo / "motion/ferramentas/biblioteca.py") == "# biblioteca v2\n"
    assert ler(repo / "motion/ferramentas/sons.py") == "# sons novo\n"
    assert ler(repo / SKILL / "SEMENTE").strip() == "1.1.0"
    assert json.loads(ler(repo / "motion/.plantio.json"))["semente"] == "1.1.0"

    # não tocou no que é do repositório: nem um byte, nem um arquivo a mais ou a menos
    assert retrato(repo, protegidas) == antes
    assert ler(repo / SKILL / "licoes-empresa.md") == "# Lições da marca\n\n1. Lição que só vale aqui.\n"
    assert ler(repo / "motion/marca/identidade.json") == '{"marca": "Café Teste", "exemplo": false}\n'
    assert ler(repo / "motion/pecas/00-exemplo/palavras.json") == PALAVRAS_EXEMPLO
    assert ler(repo / "motion/pecas/01-tema/roteiro.txt") == "Fala da peça 1.\n"
    assert ler(repo / "motion/biblioteca/indice.json") == '[{"id": "2026-10-07_xicara"}]\n'
    assert ler(repo / SKILL / "fases/00-plantio.md") == "# 00 evoluído no repo\n"

    # conflito: os dois lados mudaram -> fica o do repo, o da semente vai ao lado, a saída lista
    assert ler(repo / SKILL / "fases/05-tempo.md") == "# 05 evoluído no repo\n"
    assert ler(repo / SKILL / "fases/05-tempo.md.semente-1.1.0") == "# 05 tempo v2\n"
    assert "conflito" in resultado.stdout.lower()
    assert f"{SKILL}/fases/05-tempo.md" in resultado.stdout

    # só o repositório mudou: não há o que juntar, não é conflito
    assert not (repo / SKILL / "fases/00-plantio.md.semente-1.1.0").exists()


def test_atualizar_nao_mexe_no_exemplo_que_o_repo_nao_tocou_mesmo_com_a_semente_mudando(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    protegidas = ("motion/marca", "motion/pecas", "motion/biblioteca")
    antes = retrato(repo, protegidas)
    escrever(semente, {
        "VERSAO": "1.1.0\n",
        "modelo/exemplo/identidade.json": '{"marca": "Exemplo v2", "exemplo": true}\n',
        "modelo/exemplo/00-exemplo/palavras.json": "[]\n",
        "modelo/exemplo/00-exemplo/novo.txt": "arquivo novo do exemplo\n",
    })

    plantar_ok(repo, "--atualizar", semente=semente)

    assert retrato(repo, protegidas) == antes
    assert not list((repo / "motion").rglob("*.semente-*"))


def test_atualizar_traz_o_corpo_novo_do_skill_md_com_o_frontmatter_da_marca(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    escrever(semente, {
        "VERSAO": "1.1.0\n",
        "SKILL.md": SKILL_DA_SEMENTE.replace("Corpo do maestro", "Corpo novo do maestro"),
    })

    plantar_ok(repo, "--atualizar", semente=semente)

    skill = ler(repo / SKILL / "SKILL.md")
    linhas = skill.splitlines()
    assert "name: estudio-reels-cafe-teste" in linhas
    assert DESCRICAO_DA_MARCA in linhas
    assert "name: estudio-reels" not in linhas
    assert skill.endswith("Corpo novo do maestro, igual na semente e na cópia.\n")
    assert not (repo / SKILL / "SKILL.md.semente-1.1.0").exists()


def test_atualizar_de_novo_na_mesma_versao_nao_muda_nada(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    escrever(repo, {f"{SKILL}/fases/05-tempo.md": "# 05 evoluído no repo\n"})
    escrever(semente, {"VERSAO": "1.1.0\n", "fases/05-tempo.md": "# 05 tempo v2\n"})
    plantar_ok(repo, "--atualizar", semente=semente)
    antes = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()}
    time.sleep(1.1)  # um carimbo de hora regravado à toa mudaria de segundo

    resultado = plantar_ok(repo, "--atualizar", semente=semente)

    depois = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()}
    assert depois == antes  # inclusive motion/.plantio.json: rodada sem mudança não suja o git
    # o conflito ainda não resolvido continua visível, e não como "nada a juntar"
    pendencias = resultado.stdout.split("pendentes", 1)
    assert len(pendencias) == 2, resultado.stdout
    assert "fases/05-tempo.md.semente-1.1.0" in pendencias[1]
    assert f"{SKILL}/fases/05-tempo.md\n" not in pendencias[0]


def test_atualizar_apaga_o_que_a_semente_removeu_so_se_o_repo_nao_mexeu(ambiente):
    semente, repo = ambiente
    escrever(semente, {"navegador/outro-velho.md": "# outro velho v1\n"})
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    escrever(repo, {f"{SKILL}/navegador/outro-velho.md": "# mexido no repo\n"})
    (semente / "navegador/velho.md").unlink()
    (semente / "navegador/outro-velho.md").unlink()
    escrever(semente, {"VERSAO": "1.1.0\n"})

    resultado = plantar_ok(repo, "--atualizar", semente=semente)

    assert not (repo / SKILL / "navegador/velho.md").exists()
    assert ler(repo / SKILL / "navegador/outro-velho.md") == "# mexido no repo\n"
    assert f"{SKILL}/navegador/outro-velho.md" in resultado.stdout


def test_atualizar_arquivo_que_o_repo_apagou_so_volta_ao_lado_se_a_semente_mudou(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    (repo / SKILL / "fases/03-roteiro.md").unlink()   # a semente vai mudar este
    (repo / SKILL / "navegador/velho.md").unlink()    # e não vai mudar este
    escrever(semente, {"VERSAO": "1.1.0\n", "fases/03-roteiro.md": "# 03 roteiro v2\n"})

    resultado = plantar_ok(repo, "--atualizar", semente=semente)

    assert not (repo / SKILL / "fases/03-roteiro.md").exists()
    assert ler(repo / SKILL / "fases/03-roteiro.md.semente-1.1.0") == "# 03 roteiro v2\n"
    assert f"{SKILL}/fases/03-roteiro.md" in resultado.stdout.split("CONFLITOS", 1)[1]
    assert not (repo / SKILL / "navegador/velho.md").exists()
    assert not (repo / SKILL / "navegador/velho.md.semente-1.1.0").exists()


def test_atualizar_nunca_apaga_fora_das_pastas_da_semente_mesmo_com_registro_adulterado(ambiente, tmp_path):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    fora = tmp_path / "fora.txt"
    fora.write_bytes(b"importante\n")
    (repo / "README.md").write_bytes(b"leia-me\n")
    caminho = repo / "motion/.plantio.json"
    registro = json.loads(ler(caminho))
    registro["arquivos"]["../fora.txt"] = hashlib.sha256(b"importante\n").hexdigest()
    registro["arquivos"]["README.md"] = hashlib.sha256(b"leia-me\n").hexdigest()
    registro["arquivos"][f"{SKILL}/../../../README.md"] = hashlib.sha256(b"leia-me\n").hexdigest()
    caminho.write_text(json.dumps(registro), encoding="utf-8")

    plantar_ok(repo, "--atualizar", semente=semente)

    assert fora.read_bytes() == b"importante\n"
    assert (repo / "README.md").read_bytes() == b"leia-me\n"


def test_atualizar_recusa_registro_com_slug_que_sai_da_pasta_das_skills(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    caminho = repo / "motion/.plantio.json"
    registro = json.loads(ler(caminho))
    registro["slug"] = "../../fora"
    caminho.write_text(json.dumps(registro), encoding="utf-8")

    resultado = rodar(repo, "--atualizar", semente=semente)

    assert resultado.returncode == 1
    assert "slug" in resultado.stderr


def test_atualizar_nao_confunde_fim_de_linha_do_git_com_mudanca_do_repo(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    alvo = repo / SKILL / "fases/03-roteiro.md"
    alvo.write_bytes(alvo.read_bytes().replace(b"\n", b"\r\n"))  # core.autocrlf no checkout
    escrever(semente, {"VERSAO": "1.1.0\n", "fases/03-roteiro.md": "# 03 roteiro v2\n"})

    plantar_ok(repo, "--atualizar", semente=semente)

    assert alvo.read_bytes() == b"# 03 roteiro v2\n"
    assert not (repo / SKILL / "fases/03-roteiro.md.semente-1.1.0").exists()


def test_atualizar_sem_marca_usa_a_gravada_e_com_outra_marca_recusa(ambiente):
    semente, repo = ambiente
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    escrever(semente, {"VERSAO": "1.1.0\n", "licoes.md": "# licoes v2\n"})

    recusado = rodar(repo, "--atualizar", "--marca", "Outra Marca", semente=semente)
    assert recusado.returncode == 1
    assert "Café Teste" in recusado.stderr
    assert ler(repo / SKILL / "licoes.md") == "# licoes v1\n"

    plantar_ok(repo, "--atualizar", semente=semente)
    assert ler(repo / SKILL / "licoes.md") == "# licoes v2\n"


def test_atualizar_recusa_semente_mais_velha_que_a_do_repo(tmp_path):
    semente = fabricar_semente(tmp_path, versao="1.2.0")
    repo = tmp_path / "repo"
    repo.mkdir()
    plantar_ok(repo, "--marca", "Café Teste", semente=semente)
    escrever(semente, {"VERSAO": "1.1.9\n", "fases/03-roteiro.md": "# 03 antigo\n"})

    resultado = rodar(repo, "--atualizar", semente=semente)

    assert resultado.returncode == 1
    assert "1.1.9" in resultado.stderr and "1.2.0" in resultado.stderr
    assert ler(repo / SKILL / "fases/03-roteiro.md") == "# 03 roteiro v1\n"


def test_atualizar_sem_plantio_recusa(ambiente):
    semente, repo = ambiente

    resultado = rodar(repo, "--atualizar", semente=semente)

    assert resultado.returncode == 1
    assert "motion/.plantio.json" in resultado.stderr
    assert not (repo / "motion").exists()


# ---------------------------------------------------------------- recusas e slug

@pytest.mark.parametrize("parte, citada", [
    ("modelo/exemplo/identidade.json", "identidade.json"),
    ("copy/kishotenketsu.md", "copy/"),
])
def test_semente_incompleta_recusa_antes_de_escrever_qualquer_coisa(ambiente, parte, citada):
    semente, repo = ambiente
    (semente / parte).unlink()

    resultado = rodar(repo, "--marca", "Café Teste", semente=semente)

    assert resultado.returncode == 1
    assert "semente incompleta" in resultado.stderr  # recusa do plantar.py, não traceback
    assert citada in resultado.stderr
    assert list(repo.iterdir()) == []


def test_plantio_interrompido_avisa_sem_traceback_e_o_mesmo_comando_retoma(ambiente, monkeypatch, capsys):
    semente, repo = ambiente
    plantar = carregar_plantar()
    gravar_de_verdade = plantar.gravar

    def gravar_que_trava(destino, conteudo):
        if "motion/ferramentas" in Path(destino).as_posix():
            raise PermissionError(13, "arquivo em uso pelo sincronizador", str(destino))
        gravar_de_verdade(destino, conteudo)

    monkeypatch.setattr(plantar, "gravar", gravar_que_trava)
    plantio = [str(repo), "--marca", "Café Teste", "--semente", str(semente)]

    assert plantar.main(plantio) == 1
    erro = capsys.readouterr().err
    assert "parou no meio" in erro and "Traceback" not in erro
    assert (repo / SKILL / "SKILL.md").is_file()           # parte ficou gravada
    assert not (repo / "motion/.plantio.json").exists()    # o registro não

    # o --atualizar não manda de volta para o plantio sem saída: aponta a retomada
    assert plantar.main([str(repo), "--atualizar", "--semente", str(semente)]) == 1
    assert "--marca" in capsys.readouterr().err

    monkeypatch.setattr(plantar, "gravar", gravar_de_verdade)
    assert plantar.main(plantio) == 0                      # o mesmo comando retoma
    assert "retomando" in capsys.readouterr().out
    assert (repo / "motion/.plantio.json").is_file()
    assert ler(repo / "motion/ferramentas/biblioteca.py") == "# biblioteca v1\n"
    assert ler(repo / SKILL / "SEMENTE").strip() == "1.0.0"


def test_gravar_e_tudo_ou_nada_um_erro_no_meio_deixa_o_arquivo_antigo(tmp_path, monkeypatch):
    plantar = carregar_plantar()
    alvo = tmp_path / ".gitignore"
    alvo.write_bytes(b"dist/\n")

    def troca_que_falha(origem, destino):
        raise PermissionError(13, "arquivo em uso pelo sincronizador", str(destino))

    monkeypatch.setattr(plantar.os, "replace", troca_que_falha)
    with pytest.raises(PermissionError):
        plantar.gravar(alvo, b"dist/\nmotion/.venv/\n")

    assert alvo.read_bytes() == b"dist/\n"
    assert [p.name for p in tmp_path.iterdir()] == [".gitignore"]  # nenhum temporário largado


def test_recusa_plantar_numa_pasta_que_contem_a_semente(tmp_path):
    semente = fabricar_semente(tmp_path)

    resultado = rodar(tmp_path, "--marca", "Café Teste", semente=semente)

    assert resultado.returncode == 1
    assert "semente" in resultado.stderr
    assert not (tmp_path / "motion").exists()
    assert not (tmp_path / ".claude").exists()


def test_recusa_plantar_dentro_da_propria_semente(ambiente):
    semente, _ = ambiente

    resultado = rodar(semente, "--marca", "Café Teste", semente=semente)

    assert resultado.returncode == 1
    assert "semente" in resultado.stderr
    assert not (semente / "motion").exists()


def test_marca_sem_letra_nem_numero_recusa(ambiente):
    semente, repo = ambiente

    resultado = rodar(repo, "--marca", "!!!", semente=semente)

    assert resultado.returncode == 1
    assert "!!!" in resultado.stderr
    assert list(repo.iterdir()) == []


@pytest.mark.parametrize("marca, esperado", [
    ("Café Teste", "cafe-teste"),
    ("  Açaí & Cia. Ltda  ", "acai-cia-ltda"),
    ("Loja #1: Moda", "loja-1-moda"),
    ("SÃO JOÃO DO PÃO", "sao-joao-do-pao"),
    ("Über Café", "uber-cafe"),
    ("Straße & Søn", "strasse-son"),
])
def test_slug_minusculo_sem_acento_so_letra_numero_e_hifen(marca, esperado):
    assert carregar_plantar().slug(marca) == esperado


def test_slug_longo_cabe_no_limite_de_64_do_nome_da_skill():
    slug = carregar_plantar().slug("Palavra " * 20)
    assert len("estudio-reels-" + slug) <= 64
    assert slug.startswith("palavra-")
    assert not slug.endswith("-")


def test_frontmatter_continua_yaml_valido_com_marca_cheia_de_simbolo(ambiente):
    yaml = pytest.importorskip("yaml")
    semente, repo = ambiente

    plantar_ok(repo, "--marca", 'Loja #1: "Moda"', semente=semente)

    texto = ler(repo / ".claude/skills/estudio-reels-loja-1-moda/SKILL.md")
    meta = yaml.safe_load(texto.split("---\n")[1])
    assert meta["name"] == "estudio-reels-loja-1-moda"
    assert 'video for Loja #1: "Moda" in this repository' in meta["description"]


# ---------------------------------------------------------------- semente real

FASES = [
    "00-plantio.md", "01-contexto.md", "02-concorrencia.md", "03-roteiro.md",
    "04-narracao.md", "05-tempo.md", "06-assets.md", "07-montagem.md",
    "08-conferencia.md", "09-publicacao.md", "10-retrospectiva.md",
]

DESCRICAO_DA_SEMENTE = (
    "description: Use when the user wants Reels, motion, vertical video or narrated collage "
    "content for the company of the current repository and the repository has no "
    "estudio-reels-<marca> skill yet, or when asked to plant, update or promote the "
    "estudio-reels skill."
)

PARTES_DA_SEMENTE = [
    "VERSAO", "SKILL.md", "licoes.md", "fases/00-plantio.md", "navegador/chrome.md",
    "copy/kishotenketsu.md", "modelo/remotion/package.json", "modelo/ferramentas/biblioteca.py",
    "modelo/exemplo/identidade.json", "modelo/exemplo/00-exemplo/palavras.json",
]


def test_skill_md_da_semente_tem_o_frontmatter_e_cabe_em_120_linhas():
    linhas = ler(SEMENTE_REAL / "SKILL.md").splitlines()
    assert len(linhas) <= 120
    assert linhas[0] == "---"
    fim = linhas.index("---", 1)
    assert "name: estudio-reels" in linhas[1:fim]
    assert DESCRICAO_DA_SEMENTE in linhas[1:fim]


def test_skill_md_da_semente_aponta_as_11_fases():
    texto = ler(SEMENTE_REAL / "SKILL.md")
    for fase in FASES:
        assert f"fases/{fase}" in texto, fase


def test_skill_md_da_semente_aponta_copy_e_as_travas_de_anuncio_oferta_e_terceiros():
    texto = " ".join(ler(SEMENTE_REAL / "SKILL.md").split())  # sem quebra de linha no meio
    assert "`copy/`" in texto
    assert "Kishōtenketsu" in texto
    assert "meta-anuncios.md" in texto
    assert "`legenda-post.md` (orgânico) ou `anuncio.md` (modo oferta)" in texto
    assert "[universal recusada em AAAA-MM-DD]" in texto
    # anúncio
    assert "nunca cria, sobe, impulsiona nem edita campanha, nem gasta verba" in texto
    assert "o Gerenciador de Anúncios é só leitura" in texto
    # oferta (spec §7.2)
    assert "urgência e escassez só se forem reais" in texto
    assert "depoimento só real e autorizado" in texto
    assert "promessa só com prova [oficial]/[medido]" in texto
    assert "segue a regra do setor" in texto
    assert "`copy/oferta.md`" in texto
    # conteúdo de outro perfil nunca sobe ao ChatGPT; imagem genérica pode, como referência
    assert "Conteúdo de outro perfil" in texto and "vira só texto e link" in texto
    assert "(Pinterest, Google, Instagram)" not in texto


def test_fase_00_cita_os_comandos_do_plantio_e_da_conferencia():
    texto = ler(SEMENTE_REAL / "fases/00-plantio.md")
    for trecho in ("modelo/plantar.py", "--marca", "motion/ferramentas/instalar.py",
                   "npx tsc --noEmit", "npx vitest run", "pytest motion/ferramentas/tests",
                   "--atualizar"):
        assert trecho in texto, trecho
    # o diretório do Bash persiste entre chamadas: cd só dentro de subshell
    assert "persiste" in "\n".join(texto.splitlines()[:15])
    assert "(cd motion/remotion && npx tsc --noEmit && npx vitest run)" in texto
    assert "(cd motion/remotion && npx remotion still" in texto
    assert "Push-Location" in texto and "Pop-Location" in texto
    sem_subshell = [linha for linha in texto.splitlines()
                    if "cd motion/remotion" in linha and "(cd motion/remotion" not in linha]
    assert sem_subshell == []


def test_planta_a_semente_real_com_a_semente_padrao(tmp_path):
    faltando = [parte for parte in PARTES_DA_SEMENTE if not (SEMENTE_REAL / parte).exists()]
    if faltando:
        pytest.skip("semente real ainda incompleta: " + ", ".join(faltando))
    repo = tmp_path / "repo"
    repo.mkdir()

    plantar_ok(repo, "--marca", "Café Teste")  # sem --semente: a pasta acima de modelo/

    assert "name: estudio-reels-cafe-teste" in ler(repo / SKILL / "SKILL.md").splitlines()
    assert ler(repo / SKILL / "SEMENTE").strip() == ler(SEMENTE_REAL / "VERSAO").strip()
    for fase in FASES:
        assert (repo / SKILL / "fases" / fase).is_file(), fase
    assert (repo / SKILL / "copy/kishotenketsu.md").is_file()
    assert (repo / "motion/remotion/package.json").is_file()
    assert not (repo / "motion/remotion/node_modules").exists()
    assert json.loads(ler(repo / "motion/marca/identidade.json"))["exemplo"] is True
    assert (repo / "motion/pecas/00-exemplo/palavras.json").is_file()
