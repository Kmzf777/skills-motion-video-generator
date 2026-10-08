#!/usr/bin/env python3
"""Planta a semente estudio-reels num repositório, ou atualiza a cópia já plantada.

    python plantar.py <repo> --marca "<Nome>" [--semente <dir>] [--atualizar]

PLANTIO (primeira vez no repositório)
  - copia SKILL.md (com name/description da marca), fases/, navegador/, copy/ e licoes.md
    para <repo>/.claude/skills/estudio-reels-<slug>/ e cria licoes-empresa.md e SEMENTE;
  - copia modelo/remotion (sem node_modules) para motion/remotion e modelo/ferramentas
    para motion/ferramentas;
  - cria as pastas de motion/ do contrato C2, a biblioteca vazia, a identidade de exemplo
    ("exemplo": true, a fase 01 substitui) e a peça motion/pecas/00-exemplo/;
  - acrescenta as linhas do .gitignore e a seção do CLAUDE.md, uma vez só;
  - grava motion/.plantio.json com o sha256 do que a semente plantou (por último: sem ele,
    o plantio não terminou).
  Arquivo que já existe no repositório nunca é sobrescrito: fica como está e a saída lista.
  Recusa se o repositório já tem uma cópia .claude/skills/estudio-reels-*/ registrada (use
  --atualizar). Cópia da mesma marca SEM motion/.plantio.json é plantio interrompido: o mesmo
  comando o retoma, sem sobrescrever o que a rodada anterior gravou.

ATUALIZAÇÃO (--atualizar) compara, arquivo a arquivo, a versão que a semente plantou
(registrada em motion/.plantio.json), a do repositório e a da semente nova:
  - só a semente mudou            -> copia a nova
  - só o repositório mudou        -> mantém; não há o que juntar
  - os dois mudaram, diferentes   -> CONFLITO: mantém a do repositório e grava a da semente
                                     ao lado, como <arquivo>.semente-<versão>, para juntar
  - a semente apagou o arquivo    -> apaga se o repositório não mexeu; senão mantém e avisa
  Só escreve ou apaga arquivo da semente dentro da cópia da skill, de motion/remotion/ e de
  motion/ferramentas/. Fora deles, grava só o .gitignore e o CLAUDE.md (o que faltar, uma vez
  só), o SEMENTE da cópia (versão nova) e o motion/.plantio.json (se algo mudou). Nunca toca
  em licoes-empresa.md, motion/marca/, motion/pecas/, motion/biblioteca/,
  motion/concorrencia/ nem motion/referencias/.

Toda gravação é inteira ou nenhuma (arquivo temporário + troca): um erro no meio não deixa
.gitignore nem CLAUDE.md pela metade. Erro de sistema vira mensagem, não traceback; rodar o
mesmo comando de novo continua de onde parou.

Só biblioteca padrão; Python 3.10+.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

SEMENTE_PADRAO = Path(__file__).resolve().parent.parent

PREFIXO_SKILL = "estudio-reels-"
LIMITE_NOME_SKILL = 64  # limite do campo name de uma skill

DESCRICAO_DA_MARCA = (
    "Use when producing or auditing any Reel, motion or vertical video for {marca} in this "
    "repository — copy, narração ElevenLabs, sincronia de legenda, assets de colagem, render "
    "Remotion, conferência, descrição do post — or when the reels skill of this repo must "
    "learn from a failure."
)

# Pastas da semente que viajam inteiras para a cópia da skill (com SKILL.md e licoes.md).
PASTAS_DA_SKILL = ("fases", "navegador", "copy")

# Contrato C2 com os acréscimos do orquestrador, mais o cache que as ferramentas (import
# de _ffmpeg.py) e o pytest deixam em motion/: o commit do plantio é `git add motion`, e nem
# todo repositório ignora __pycache__. Cada linha entra uma vez só, na ordem desta lista.
LINHAS_GITIGNORE = [
    "motion/remotion/node_modules/",
    "motion/remotion/out/",               # saída padrão do Remotion sem caminho explícito
    "motion/.venv/",
    "motion/biblioteca/**/*.png",
    "motion/biblioteca/brutos/",          # .jpg de banco livre e folhas cruas
    # De public/ da peça, só a narração final vai ao git: é dela que saem os tempos do
    # palavras.json, e num clone sem ela a peça não se refaz. A ordem importa: cada linha
    # desfaz parte da anterior, e o git não reinclui arquivo de pasta já excluída inteira.
    "motion/pecas/*/public/*",
    "!motion/pecas/*/public/fonte/",
    "motion/pecas/*/public/fonte/*",
    "!motion/pecas/*/public/fonte/narracao.mp3",
    "motion/pecas/*/saida/",
    "motion/concorrencia/videos/",        # vídeo de terceiro baixado para estudo (fase 02)
    "motion/ferramentas/whisper.cpp/",
    "motion/**/__pycache__/",
    "motion/**/.pytest_cache/",
]
CABECALHO_GITIGNORE = "# estudio-reels: dependências, venv, brutos, vídeos de estudo e saídas das peças"

SECAO_CLAUDE = """\
## Reels (estudio-reels)

Reels, motion e vídeo vertical desta marca são produzidos pela skill do repositório
`.claude/skills/estudio-reels-{slug}/`, plantada da semente pessoal `estudio-reels`. Leia o
`SKILL.md` dela antes de escrever roteiro, gerar narração, montar ou conferir uma peça: é ela
que comanda o processo (fases, travas e lições). Motor e ferramentas ficam em `motion/`; as
lições que só valem para esta marca, em `.claude/skills/estudio-reels-{slug}/licoes-empresa.md`.
"""

LICOES_EMPRESA = """\
# Lições desta marca

Lições que ficam neste repositório:

- **da marca** (produto, conta, público, fatos conferidos com o cliente): nunca sobem para a
  semente;
- **universais que o usuário recusou promover**, marcadas
  `[universal recusada em AAAA-MM-DD]`: continuam valendo aqui e podem ser propostas de novo
  numa retrospectiva futura, quando houver fato novo.

Formato: **sintoma → causa raiz → regra**, numeradas, a mais nova no fim. Lição universal
nova (site, ferramenta, motor, método) vai para `licoes.md` e entra na lista de promoção da
fase 10.
"""

# Contrato C4.
CATEGORIAS_PADRAO = [
    "objeto", "utensilio", "natureza", "alimento", "produto",
    "foto-real", "textura", "papelaria", "grafismo", "maos",
]

# Pastas do contrato C2 que nascem vazias e precisam de .gitkeep para entrar no git.
PASTAS_COM_GITKEEP = [
    "motion/marca/fontes",
    "motion/concorrencia",
    "motion/referencias",
    "motion/biblioteca/pecas",
]
# Pastas cujo conteúdo o .gitignore exclui (de public/fonte/ só a narração final entra):
# nascem no disco, sem .gitkeep, que seria ignorado. Em public/ só o que alguma ferramenta
# grava: fonte/ (narração), colagem/ (o `biblioteca.py publicar` põe tudo ali, produto
# inclusive) e sfx/ (sons.py).
PASTAS_SO_NO_DISCO = [
    "motion/biblioteca/brutos",
    "motion/pecas/00-exemplo/public/fonte",
    "motion/pecas/00-exemplo/public/colagem",
    "motion/pecas/00-exemplo/public/sfx",
    "motion/pecas/00-exemplo/saida",
]

# O que é do repositório: a atualização não escreve, não apaga e não compara.
PROTEGIDOS = (
    "motion/marca/",
    "motion/pecas/",
    "motion/biblioteca/",
    "motion/concorrencia/",
    "motion/referencias/",
)
# Na cópia, estes também são do repositório.
SO_DO_REPO_NA_COPIA = ("licoes-empresa.md", "SEMENTE")

# Nunca viajam da semente para o repositório.
IGNORAR_PASTAS = {
    "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".git", ".venv", "venv", "whisper.cpp", "out",
}
IGNORAR_ARQUIVOS = {".DS_Store", "Thumbs.db", "desktop.ini"}
IGNORAR_SUFIXOS = (".pyc", ".pyo")

ARQUIVOS_OBRIGATORIOS = [
    "VERSAO",
    "SKILL.md",
    "licoes.md",
    "modelo/remotion/package.json",
    "modelo/exemplo/identidade.json",
    "modelo/exemplo/00-exemplo/palavras.json",
]
PASTAS_OBRIGATORIAS = [*PASTAS_DA_SKILL, "modelo/ferramentas"]

ARQUIVO_LADO = re.compile(r"\.semente-\d+(?:\.\d+)*$")
DEPENDENCIAS = (
    "motion/remotion/package.json",
    "motion/remotion/package-lock.json",
    "motion/ferramentas/requirements.txt",
)


class ErroPlantio(Exception):
    """Recusa com mensagem para quem rodou; nada é escrito depois dela."""


@dataclass
class Item:
    destino: str   # relativo à raiz do repositório, com "/"
    conteudo: bytes
    grupo: str     # skill | motor | ferramentas | exemplo


@dataclass
class Relatorio:
    novos: list[str] = field(default_factory=list)
    atualizados: list[str] = field(default_factory=list)
    removidos: list[str] = field(default_factory=list)
    mantidos: list[str] = field(default_factory=list)
    conflitos: list[tuple[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------- nomes, versões, caminhos

_TROCAS = str.maketrans({"ß": "ss", "æ": "ae", "Æ": "ae", "œ": "oe", "Œ": "oe", "ø": "o", "Ø": "o"})


def slug(marca: str) -> str:
    """Minúsculas, só [a-z0-9-], sem acento; cabe no limite de 64 do nome da skill."""
    texto = unicodedata.normalize("NFKD", marca.translate(_TROCAS))
    texto = "".join(c for c in texto if not unicodedata.combining(c)).lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    limite = LIMITE_NOME_SKILL - len(PREFIXO_SKILL)
    if len(texto) > limite:
        corte = texto[:limite]
        if texto[limite] != "-" and "-" in corte:
            corte = corte[: corte.rfind("-")]  # não corta palavra no meio
        texto = corte.strip("-")
    return texto


def ler_versao(semente: Path) -> str:
    versao = (semente / "VERSAO").read_text(encoding="utf-8").strip()
    _numeros(versao, semente / "VERSAO")
    return versao


def _numeros(versao: str, origem: Path | str) -> tuple[int, ...]:
    if not re.fullmatch(r"\d+(?:\.\d+)*", versao):
        raise ErroPlantio(f'versão inválida "{versao}" em {origem}: use números, ex.: 1.0.0')
    return tuple(int(parte) for parte in versao.split("."))


def assinatura(conteudo: bytes) -> str:
    """sha256 do conteúdo; em arquivo de texto, CRLF conta como LF.

    O core.autocrlf do git no Windows troca LF por CRLF no checkout, e isso não é uma
    mudança que o repositório fez no arquivo.
    """
    if b"\0" not in conteudo[:8192]:
        conteudo = conteudo.replace(b"\r\n", b"\n")
    return hashlib.sha256(conteudo).hexdigest()


def pasta_da_copia(slug_marca: str) -> str:
    return f".claude/skills/{PREFIXO_SKILL}{slug_marca}"


def raizes_gerenciadas(slug_marca: str) -> tuple[str, ...]:
    """As únicas pastas onde a atualização escreve ou apaga."""
    return (pasta_da_copia(slug_marca), "motion/remotion", "motion/ferramentas")


def protegido(rel: str) -> bool:
    return rel.startswith(PROTEGIDOS)


def gerenciado(rel: str, slug_marca: str) -> bool:
    """Caminho que a atualização pode escrever ou apagar.

    O registro é um arquivo do repositório: um caminho dele que saia das pastas da semente
    (`..`, raiz absoluta, `README.md`) nunca é tocado, mesmo que o sha bata.
    """
    partes = rel.split("/")
    return (
        rel.startswith(tuple(raiz + "/" for raiz in raizes_gerenciadas(slug_marca)))
        and not {"", ".", ".."} & set(partes) and "\\" not in rel and ":" not in rel
        and rel.removeprefix(pasta_da_copia(slug_marca) + "/") not in SO_DO_REPO_NA_COPIA
    )


# ---------------------------------------------------------------- leitura da semente

def listar(raiz: Path) -> list[str]:
    """Arquivos sob raiz, relativos e com "/", sem dependência instalada nem cache."""
    arquivos = []
    for atual, pastas, nomes in os.walk(raiz):
        pastas[:] = sorted(p for p in pastas if p not in IGNORAR_PASTAS)
        for nome in sorted(nomes):
            if nome in IGNORAR_ARQUIVOS or nome.endswith(IGNORAR_SUFIXOS):
                continue
            arquivos.append((Path(atual) / nome).relative_to(raiz).as_posix())
    return arquivos


def validar_semente(semente: Path) -> None:
    faltando = [rel for rel in ARQUIVOS_OBRIGATORIOS if not (semente / rel).is_file()]
    faltando += [rel + "/" for rel in PASTAS_OBRIGATORIAS
                 if not (semente / rel).is_dir() or not listar(semente / rel)]
    if faltando:
        raise ErroPlantio(
            f"semente incompleta em {semente}: falta " + ", ".join(faltando)
            + ". Confira a instalação da semente antes de plantar."
        )


def escalar_yaml(texto: str) -> str:
    """Valor de uma linha no frontmatter; entre aspas quando o YAML leria outra coisa."""
    arriscado = (
        ": " in texto or " #" in texto or texto.endswith(":") or "\t" in texto
        or texto[:1] in "!&*{}[]|>'\"%@`#,?-:"
    )
    if not arriscado:
        return texto
    return '"' + texto.replace("\\", "\\\\").replace('"', '\\"') + '"'


def renderizar_skill(texto: str, nome: str, descricao: str) -> str:
    """Troca name e description do frontmatter; o corpo fica byte a byte igual."""
    texto = texto.removeprefix("﻿")
    achado = re.match(r"---(\r?\n)(.*?)(\r?\n)---[ \t]*(?=\r?\n|\Z)", texto, re.S)
    if not achado:
        raise ErroPlantio("o SKILL.md da semente não começa com frontmatter (---)")
    nl = achado.group(1)
    blocos: list[tuple[str | None, list[str]]] = []
    for linha in achado.group(2).splitlines():
        chave = re.match(r"([A-Za-z0-9_-]+):", linha)
        if chave and not linha[:1].isspace():
            blocos.append((chave.group(1), [linha]))
        elif blocos:
            blocos[-1][1].append(linha)  # continuação de valor de várias linhas
        else:
            blocos.append((None, [linha]))
    novos = {"name": f"name: {nome}", "description": f"description: {escalar_yaml(descricao)}"}
    saida: list[str] = []
    for chave, linhas in blocos:
        if chave in novos:
            saida.append(novos.pop(chave))
        elif chave not in ("name", "description"):
            saida.extend(linhas)
    saida.extend(novos.values())  # o que o frontmatter da semente não tinha
    return "---" + nl + nl.join(saida) + achado.group(3) + "---" + texto[achado.end():]


def montar_plano(semente: Path, marca: str, slug_marca: str) -> list[Item]:
    """Tudo o que a semente planta, já lido; nada é escrito aqui."""
    copia = pasta_da_copia(slug_marca)
    descricao = DESCRICAO_DA_MARCA.format(marca=marca)
    if len(descricao) > 1024:
        raise ErroPlantio("o nome da marca é longo demais para a descrição da skill (máx. 1024)")

    skill = (semente / "SKILL.md").read_bytes().decode("utf-8")
    itens = [Item(f"{copia}/SKILL.md",
                  renderizar_skill(skill, PREFIXO_SKILL + slug_marca, descricao).encode("utf-8"),
                  "skill")]
    for pasta in PASTAS_DA_SKILL:
        for rel in listar(semente / pasta):
            itens.append(Item(f"{copia}/{pasta}/{rel}", (semente / pasta / rel).read_bytes(), "skill"))
    itens.append(Item(f"{copia}/licoes.md", (semente / "licoes.md").read_bytes(), "skill"))

    for origem, destino, grupo in (("modelo/remotion", "motion/remotion", "motor"),
                                   ("modelo/ferramentas", "motion/ferramentas", "ferramentas")):
        for rel in listar(semente / origem):
            itens.append(Item(f"{destino}/{rel}", (semente / origem / rel).read_bytes(), grupo))

    caminho = semente / "modelo/exemplo/identidade.json"
    try:
        identidade = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ErroPlantio(f"{caminho} não é JSON válido: {erro}") from erro
    if not isinstance(identidade, dict):
        raise ErroPlantio(f"{caminho} deveria ser um objeto JSON (contrato C3)")
    identidade.update({"marca": marca, "slug": slug_marca, "exemplo": True})
    itens.append(Item("motion/marca/identidade.json",
                      (json.dumps(identidade, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
                      "exemplo"))
    exemplo = semente / "modelo/exemplo/00-exemplo"
    for rel in listar(exemplo):
        itens.append(Item(f"motion/pecas/00-exemplo/{rel}", (exemplo / rel).read_bytes(), "exemplo"))
    return itens


# ---------------------------------------------------------------- escrita no repositório

def gravar(destino: Path, conteudo: bytes) -> None:
    """Grava inteiro ou não grava: um erro no meio deixa o arquivo antigo intacto."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_name(f".{destino.name}.plantando")
    try:
        temporario.write_bytes(conteudo)
        os.replace(temporario, destino)
    except BaseException:
        temporario.unlink(missing_ok=True)
        raise


def _ler_texto(caminho: Path) -> str:
    return caminho.read_bytes().decode("utf-8-sig") if caminho.exists() else ""


def acrescentar_gitignore(repo: Path) -> int:
    """Acrescenta as linhas que faltam; devolve quantas entraram."""
    caminho = repo / ".gitignore"
    texto = _ler_texto(caminho)
    existentes = {linha.strip() for linha in texto.splitlines()}
    faltando = [linha for linha in LINHAS_GITIGNORE if linha not in existentes]
    if not faltando:
        return 0
    nl = "\r\n" if "\r\n" in texto else "\n"
    partes = []
    if texto and not texto.endswith("\n"):
        partes.append(nl)
    if texto.strip():
        partes.append(nl)
    if CABECALHO_GITIGNORE not in existentes:
        partes.append(CABECALHO_GITIGNORE + nl)
    partes.extend(linha + nl for linha in faltando)
    gravar(caminho, (texto + "".join(partes)).encode("utf-8"))
    return len(faltando)


def acrescentar_claude_md(repo: Path, slug_marca: str) -> bool:
    """Acrescenta a seção "Reels (estudio-reels)" se ainda não houver; cria o arquivo se faltar."""
    caminho = repo / "CLAUDE.md"
    texto = _ler_texto(caminho)
    if re.search(r"(?m)^#{1,6}[ \t]*Reels \(estudio-reels\)[ \t]*\r?$", texto):
        return False
    nl = "\r\n" if "\r\n" in texto else "\n"
    secao = SECAO_CLAUDE.format(slug=slug_marca).replace("\n", nl)
    novo = (texto.rstrip("\r\n") + nl + nl + secao) if texto.strip() else secao
    gravar(caminho, novo.encode("utf-8"))
    return True


def gravar_registro(repo: Path, registro: dict) -> None:
    registro["arquivos"] = dict(sorted(registro["arquivos"].items()))
    gravar(repo / "motion/.plantio.json",
           (json.dumps(registro, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def ler_registro(repo: Path) -> dict:
    caminho = repo / "motion/.plantio.json"
    if not caminho.is_file():
        raise ErroPlantio(
            f"não há plantio registrado em {repo} (falta motion/.plantio.json). "
            'Para plantar: plantar.py <repo> --marca "<Nome>"'
        )
    try:
        registro = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ErroPlantio(f"motion/.plantio.json ilegível: {erro}") from erro
    for chave in ("semente", "marca", "slug", "arquivos"):
        if chave not in registro:
            raise ErroPlantio(f'motion/.plantio.json sem o campo "{chave}"')
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(registro["slug"])):
        raise ErroPlantio(f'motion/.plantio.json tem slug inválido: "{registro["slug"]}"')
    if not isinstance(registro["arquivos"], dict):
        raise ErroPlantio('motion/.plantio.json: "arquivos" deveria ser um objeto')
    return registro


def validar_destino(repo: Path, semente: Path) -> Path:
    if not repo.is_dir():
        raise ErroPlantio(f"o repositório {repo} não existe ou não é uma pasta")
    repo_r, semente_r = repo.resolve(), semente.resolve()
    if repo_r == semente_r or semente_r in repo_r.parents:
        raise ErroPlantio(
            f"o destino {repo_r} fica dentro da semente {semente_r}; "
            "plante no repositório da marca, não na semente"
        )
    if repo_r in semente_r.parents:
        raise ErroPlantio(
            f"a semente {semente_r} fica dentro do destino {repo_r} (pasta pessoal ou acima "
            "do repositório?); plante na raiz do repositório da marca"
        )
    return repo_r


def copias_existentes(repo: Path) -> list[str]:
    pasta = repo / ".claude/skills"
    if not pasta.is_dir():
        return []
    return sorted(p.name for p in pasta.iterdir() if p.is_dir() and p.name.startswith(PREFIXO_SKILL))


def pendentes(repo: Path, slug_marca: str) -> list[str]:
    """Arquivos <x>.semente-<versão> ainda não resolvidos nas pastas que a semente gerencia."""
    achados = []
    for raiz in raizes_gerenciadas(slug_marca):
        if (repo / raiz).is_dir():
            achados += [f"{raiz}/{rel}" for rel in listar(repo / raiz) if ARQUIVO_LADO.search(rel)]
    return achados


def _podar_vazias(pasta: Path, limite: Path) -> None:
    while pasta != limite and limite in pasta.parents and not any(pasta.iterdir()):
        pasta.rmdir()
        pasta = pasta.parent


# ---------------------------------------------------------------- plantio

def plantar(repo: Path, semente: Path, marca: str) -> None:
    marca = " ".join(marca.split())
    slug_marca = slug(marca)
    if not slug_marca:
        raise ErroPlantio(f'não dá para tirar um nome de skill de --marca "{marca}": '
                          "use letras ou números")
    validar_semente(semente)
    versao = ler_versao(semente)
    repo = validar_destino(repo, semente)
    copias = copias_existentes(repo)
    retomando = False
    if copias:
        if (repo / "motion/.plantio.json").is_file():
            raise ErroPlantio(
                f"este repositório já tem a cópia .claude/skills/{copias[0]}/, que pode ter "
                "evoluído. Para puxar a versão nova da semente sem perder o que mudou aqui: "
                f"plantar.py {repo} --atualizar"
            )
        if copias != [PREFIXO_SKILL + slug_marca]:
            raise ErroPlantio(
                f"há .claude/skills/{', '.join(copias)}/ sem motion/.plantio.json (plantio "
                f'interrompido de outra marca?). Para retomá-lo, rode com a marca dele; "{marca}" '
                "daria uma segunda cópia neste repositório"
            )
        retomando = True  # cópia desta marca sem registro: a rodada anterior não terminou
    plano = montar_plano(semente, marca, slug_marca)

    registro: dict[str, str] = {}
    escritos: dict[str, int] = {}
    ja_existiam: list[str] = []
    for item in plano:
        destino = repo / item.destino
        registro[item.destino] = assinatura(item.conteudo)
        if destino.exists():
            if assinatura(destino.read_bytes()) != registro[item.destino]:
                ja_existiam.append(item.destino)
            continue
        gravar(destino, item.conteudo)
        escritos[item.grupo] = escritos.get(item.grupo, 0) + 1

    copia = repo / pasta_da_copia(slug_marca)
    if not (copia / "licoes-empresa.md").exists():
        gravar(copia / "licoes-empresa.md", LICOES_EMPRESA.encode("utf-8"))
    gravar(copia / "SEMENTE", f"{versao}\n".encode("utf-8"))
    for pasta in PASTAS_COM_GITKEEP:
        if not (repo / pasta / ".gitkeep").exists():
            gravar(repo / pasta / ".gitkeep", b"")
    for pasta in PASTAS_SO_NO_DISCO:
        (repo / pasta).mkdir(parents=True, exist_ok=True)
    if not (repo / "motion/biblioteca/indice.json").exists():
        gravar(repo / "motion/biblioteca/indice.json", b"[]\n")
    if not (repo / "motion/biblioteca/categorias.json").exists():
        gravar(repo / "motion/biblioteca/categorias.json",
               (json.dumps(CATEGORIAS_PADRAO, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    linhas_gitignore = acrescentar_gitignore(repo)
    secao_nova = acrescentar_claude_md(repo, slug_marca)
    gravar_registro(repo, {
        "semente": versao,
        "marca": marca,
        "slug": slug_marca,
        "plantado_em": datetime.now().isoformat(timespec="seconds"),
        "atualizado_em": None,
        "hash": "sha256; em arquivo de texto, CRLF conta como LF",
        "arquivos": registro,
    })

    if retomando:
        print("retomando plantio interrompido (cópia sem motion/.plantio.json): "
              "o que a rodada anterior gravou ficou como estava")
    print(f'estudio-reels {versao} plantada em {repo} para "{marca}"')
    print(f"  skill da marca: {pasta_da_copia(slug_marca)}/ "
          f"({escritos.get('skill', 0)} arquivos da semente)")
    print(f"  motor:          motion/remotion/ ({escritos.get('motor', 0)} arquivos, sem node_modules)")
    print(f"  ferramentas:    motion/ferramentas/ ({escritos.get('ferramentas', 0)} arquivos)")
    print('  exemplo:        motion/marca/identidade.json ("exemplo": true) e motion/pecas/00-exemplo/')
    print(f"  .gitignore:     {linhas_gitignore} linhas acrescentadas")
    print(f"  CLAUDE.md:      {'seção acrescentada' if secao_nova else 'seção já existia'}")
    if ja_existiam:
        print("  mantidos (já existiam no repositório com outro conteúdo; nada foi sobrescrito):")
        for rel in ja_existiam:
            print(f"    {rel}")
    print("Próximos passos (fases/00-plantio.md):")
    print("  1. python motion/ferramentas/instalar.py   (avisa o tamanho antes de baixar)")
    print("  2. conferência: npx tsc --noEmit e npx vitest run em motion/remotion;")
    print("     pytest em motion/ferramentas/tests")
    print('  3. fase 01: motion/marca/identidade.json ainda é o de EXEMPLO ("exemplo": true)')


# ---------------------------------------------------------------- atualização

def comparar(repo: Path, plano: list[Item], base: dict[str, str], slug_marca: str,
             versao_nova: str) -> tuple[dict[str, str], Relatorio]:
    """Aplica a comparação de três versões; devolve o registro novo e o que aconteceu."""
    novo_registro = {rel: sha for rel, sha in base.items() if protegido(rel)}
    relatorio = Relatorio()
    vistos: set[str] = set()
    for item in plano:
        rel = item.destino
        if protegido(rel) or not gerenciado(rel, slug_marca):
            continue
        vistos.add(rel)
        destino = repo / rel
        lado = f"{rel}.semente-{versao_nova}"
        deles = assinatura(item.conteudo)
        antes = base.get(rel)
        novo_registro[rel] = deles
        if not destino.exists():
            if antes is None:
                gravar(destino, item.conteudo)
                relatorio.novos.append(rel)
            elif deles != antes:  # o repositório apagou e a semente mudou
                gravar(repo / lado, item.conteudo)
                relatorio.conflitos.append((rel, "o repositório apagou este arquivo e a semente o "
                                                 f"alterou; a versão nova está em {lado}: "
                                                 "restaure-a ou apague-a"))
            continue  # apagado no repositório e igual na semente: respeita
        nosso = assinatura(destino.read_bytes())
        if nosso == deles:
            continue
        if antes is not None and nosso == antes:
            gravar(destino, item.conteudo)
            relatorio.atualizados.append(rel)
        elif antes is not None and deles == antes:
            relatorio.mantidos.append(rel)
        else:
            gravar(repo / lado, item.conteudo)
            relatorio.conflitos.append((rel, f"a versão nova da semente está ao lado, em {lado}: "
                                             "junte à mão e apague o .semente-*"))

    for rel, antes in base.items():
        if rel in vistos or protegido(rel) or not gerenciado(rel, slug_marca):
            continue  # fora das pastas da semente: sai do registro, nunca do disco
        destino = repo / rel
        if not destino.is_file():
            continue
        if assinatura(destino.read_bytes()) == antes:
            destino.unlink()
            raiz = next(r for r in raizes_gerenciadas(slug_marca) if rel.startswith(r + "/"))
            _podar_vazias(destino.parent, repo / raiz)
            relatorio.removidos.append(rel)
        else:
            relatorio.conflitos.append((rel, "a semente apagou este arquivo e o repositório o "
                                             "alterou: decida se ainda faz sentido "
                                             "(deixou de ser da semente)"))
    return novo_registro, relatorio


def atualizar(repo: Path, semente: Path, marca_pedida: str | None) -> None:
    repo = validar_destino(repo, semente)
    copias = copias_existentes(repo)
    if copias and not (repo / "motion/.plantio.json").is_file():
        raise ErroPlantio(
            f"há .claude/skills/{copias[0]}/ mas falta motion/.plantio.json: o plantio não "
            "terminou, e não há base para atualizar. Retome com o mesmo comando do plantio "
            f'(plantar.py {repo} --marca "<a mesma marca>"): ele não sobrescreve o que já foi gravado'
        )
    registro = ler_registro(repo)
    marca, slug_marca = registro["marca"], registro["slug"]
    if marca_pedida is not None and slug(" ".join(marca_pedida.split())) != slug_marca:
        raise ErroPlantio(
            f'este repositório foi plantado para "{marca}" ({pasta_da_copia(slug_marca)}/); '
            f'--marca "{marca_pedida}" não confere. Rode --atualizar sem --marca.'
        )
    validar_semente(semente)
    versao_nova = ler_versao(semente)
    versao_repo = str(registro["semente"])
    if _numeros(versao_nova, semente / "VERSAO") < _numeros(versao_repo, "motion/.plantio.json"):
        raise ErroPlantio(
            f"a semente em {semente} está na versão {versao_nova}, mais velha que a {versao_repo} "
            "deste repositório. Atualize a semente desta máquina antes; nada foi alterado."
        )
    copia = repo / pasta_da_copia(slug_marca)
    if not copia.is_dir():
        raise ErroPlantio(
            f"a cópia {pasta_da_copia(slug_marca)}/ não existe mais neste repositório; "
            "para plantar de novo, rode sem --atualizar"
        )
    plano = montar_plano(semente, marca, slug_marca)
    pendentes_antes = set(pendentes(repo, slug_marca))

    base: dict[str, str] = registro["arquivos"]
    novo_registro, relatorio = comparar(repo, plano, base, slug_marca, versao_nova)
    linhas_gitignore = acrescentar_gitignore(repo)
    secao_nova = acrescentar_claude_md(repo, slug_marca)
    mudou = bool(
        relatorio.atualizados or relatorio.novos or relatorio.removidos or relatorio.conflitos
        or linhas_gitignore or secao_nova or versao_nova != versao_repo or novo_registro != base
    )
    if _ler_texto(copia / "SEMENTE").strip() != versao_nova:
        gravar(copia / "SEMENTE", f"{versao_nova}\n".encode("utf-8"))
    if mudou:  # rodada sem mudança não regrava o carimbo de hora (não suja o git)
        registro.update({
            "semente": versao_nova,
            "atualizado_em": datetime.now().isoformat(timespec="seconds"),
            "arquivos": novo_registro,
        })
        gravar_registro(repo, registro)

    print(f'estudio-reels: atualização {versao_repo} -> {versao_nova} em {repo} ("{marca}")')
    if versao_nova == versao_repo:
        print("  (mesma versão: só conferi as diferenças)")
    ainda_pendentes = pendentes(repo, slug_marca)
    _relatar_atualizacao(relatorio, ainda_pendentes, pendentes_antes, linhas_gitignore, secao_nova)
    if not mudou:
        print("Nada mudou no repositório; não há o que commitar.")
        return
    mexidos = set(relatorio.atualizados) | set(relatorio.novos) | {rel for rel, _ in relatorio.conflitos}
    print("Próximos passos:")
    if mexidos & set(DEPENDENCIAS):
        print("  - as dependências mudaram: python motion/ferramentas/instalar.py")
    print("  - conferência da fase 00 (tsc, vitest, pytest) antes de produzir a próxima peça")
    print("  - commit da atualização (os arquivos listados acima, SEMENTE e motion/.plantio.json)")


def _relatar_atualizacao(relatorio: Relatorio, ainda_pendentes: list[str], pendentes_antes: set[str],
                         linhas_gitignore: int, secao_nova: bool) -> None:
    com_lado = {ARQUIVO_LADO.sub("", rel) for rel in ainda_pendentes}
    blocos = [
        ("atualizados (só a semente mudou)", relatorio.atualizados),
        ("novos", relatorio.novos),
        ("removidos (a semente apagou e o repositório não tinha mexido)", relatorio.removidos),
        ("mantidos (só o repositório mudou; não há o que juntar)",
         [rel for rel in relatorio.mantidos if rel not in com_lado]),
    ]
    for titulo, lista in blocos:
        if lista:
            print(f"  {titulo}:")
            for rel in lista:
                print(f"    {rel}")
    if not any(lista for _, lista in blocos) and not relatorio.conflitos:
        print("  nenhum arquivo da semente mudou")
    if linhas_gitignore:
        print(f"  .gitignore: {linhas_gitignore} linhas acrescentadas")
    if secao_nova:
        print("  CLAUDE.md: seção acrescentada")
    if relatorio.conflitos:
        print("  CONFLITOS (os dois lados mudaram; nada do repositório foi sobrescrito):")
        for rel, acao in relatorio.conflitos:
            print(f"    {rel}")
            print(f"      {acao}")
    antigos = sorted(pendentes_antes & set(ainda_pendentes))
    if antigos:
        print("  conflitos pendentes de atualizações anteriores (junte e apague o .semente-*):")
        for rel in antigos:
            print(f"    {rel}")


# ---------------------------------------------------------------- linha de comando

def main(argv: list[str] | None = None) -> int:
    # Saída capturada no Windows sai em cp1252 e o agente que roda isto lê UTF-8.
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    analisador = argparse.ArgumentParser(
        prog="plantar.py",
        description="Planta a semente estudio-reels num repositório, ou atualiza a cópia plantada.",
    )
    analisador.add_argument("repo", type=Path, help="raiz do repositório da marca")
    analisador.add_argument("--marca", help='nome da marca, ex.: "Café Teste" (obrigatório no plantio)')
    analisador.add_argument("--semente", type=Path, default=SEMENTE_PADRAO,
                            help="pasta da semente (padrão: a pasta acima de modelo/)")
    analisador.add_argument("--atualizar", action="store_true",
                            help="puxa da semente o que mudou, sem tocar no que o repositório mudou")
    args = analisador.parse_args(argv)
    if not args.atualizar and args.marca is None:
        analisador.error('--marca é obrigatório no plantio, ex.: --marca "Café Teste"')
    try:
        if args.atualizar:
            atualizar(args.repo, args.semente, args.marca)
        else:
            plantar(args.repo, args.semente, args.marca)
    except ErroPlantio as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1
    except OSError as erro:  # sincronizador com o arquivo preso, caminho longo, disco cheio
        operacao = "a atualização" if args.atualizar else "o plantio"
        print(f"erro: {operacao} parou no meio ({erro}). Corrija a causa e rode o mesmo comando "
              "de novo: ele continua de onde parou, sem sobrescrever o que já foi gravado.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
