"""Biblioteca de peças de colagem da marca: cada peça entra uma vez e serve a qualquer Reel.

Rode da raiz do repositório:

    python motion/ferramentas/biblioteca.py buscar <termos...>
    python motion/ferramentas/biblioteca.py listar [categoria]
    python motion/ferramentas/biblioteca.py publicar <NN-tema> <ids...>
    python motion/ferramentas/biblioteca.py registrar <nome> <categoria> <arq...> --tags a,b --origem <origem>
        [--bruto F] [--prompt T] [--fonte URL] [--dia AAAA-MM-DD] [--nota T] [--substituir]

Onde as coisas ficam:

    motion/biblioteca/
      indice.json                          <- versionado; a busca lê isto
      categorias.json                      <- categorias válidas (lista, ou {nome: descrição})
      brutos/AAAA-MM-DD_<folha>.<ext>      folha original, bytes intactos com o EXIF (o recortar_folha guarda)
      pecas/<categoria>/AAAA-MM-DD_<nome>-b0.png   (b0/b1/b2 = bordas do boil)

Os PNG e os brutos não vão para o git; o índice vai. Numa máquina nova o índice lista peças
cujo PNG não está lá (`listar` marca "SEM PNG"): refaça a partir do `bruto` e do `prompt`.

Orientação: a peça é gravada como EXIBE. Arquivo com EXIF `Orientation` (foto de celular
grava deitada e exibe em pé) é girado ao registrar, e `dimensoes` é a de exibição. Quem lê
um bruto aplica o EXIF (ImageOps.exif_transpose), porque ele guarda os bytes originais.

O id é `<dia>_<nome>`. `registrar` recusa id que já existe (sobrescreveria o PNG que outra
peça usa); `--substituir` só para a MESMA peça refeita. `publicar` copia as variantes para
`motion/pecas/<NN-tema>/public/colagem/<nome>-bN.png` — o caminho que o motor lê — e recusa
duas peças de mesmo nome no mesmo projeto, porque o projeto lê pelo NOME, não pelo id.

Origens: gerado-chatgpt (exige --prompt: sem ele a próxima sessão não consegue refazer
uma folha parecida), real-verificada, real-nao-verificada, banco-livre (exige --fonte, a
URL da página da foto), codigo.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

MOTION = Path("motion")
RAIZ = MOTION / "biblioteca"
INDICE = RAIZ / "indice.json"
CATEGORIAS = RAIZ / "categorias.json"
BRUTOS = RAIZ / "brutos"
PECAS = RAIZ / "pecas"
PROJETOS = MOTION / "pecas"

ORIGENS = ("gerado-chatgpt", "real-verificada", "real-nao-verificada", "banco-livre", "codigo")
# O mesmo padrão que o plantio grava (lista). O arquivo também aceita {nome: descrição}.
# produto = produto da MARCA: só recorte de foto real, nunca gerado (ver validar_registro).
CATEGORIAS_PADRAO = ["objeto", "utensilio", "natureza", "alimento", "produto",
                     "foto-real", "textura", "papelaria", "grafismo", "maos"]
NOME_VALIDO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _conferir_raiz() -> None:
    if not MOTION.is_dir():
        raise SystemExit(f"não achei a pasta motion/ em {Path.cwd()}: rode da raiz do repositório onde a "
                         "estudio-reels foi plantada (python motion/ferramentas/biblioteca.py ...)")


def categorias() -> dict[str, str]:
    """Categorias válidas, lidas de `motion/biblioteca/categorias.json` (lista ou dicionário).

    Se o arquivo não existe, cria com o padrão. Para criar uma categoria, acrescente-a ao arquivo.
    """
    _conferir_raiz()
    if not CATEGORIAS.exists():
        RAIZ.mkdir(parents=True, exist_ok=True)
        CATEGORIAS.write_text(json.dumps(CATEGORIAS_PADRAO, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dados = json.loads(CATEGORIAS.read_text(encoding="utf-8"))
    if isinstance(dados, list):
        return {str(c): "" for c in dados}
    if isinstance(dados, dict):
        return {str(c): str(d) for c, d in dados.items()}
    raise SystemExit(f"{CATEGORIAS.as_posix()} tem de ser uma lista de nomes ou um objeto {{nome: descrição}}")


def carregar() -> list[dict]:
    _conferir_raiz()
    if not INDICE.exists():
        return []
    return json.loads(INDICE.read_text(encoding="utf-8"))


def salvar(itens: list[dict]) -> None:
    _conferir_raiz()
    RAIZ.mkdir(parents=True, exist_ok=True)
    itens.sort(key=lambda i: (i["categoria"], i["id"]))
    INDICE.write_text(json.dumps(itens, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def _caminho_relativo(p: str | Path) -> str:
    """Caminho em posix, relativo à raiz do repositório quando está dentro dela."""
    p = Path(p)
    try:
        return p.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return p.resolve().as_posix()


def nome_de_arquivo(s: str) -> str:
    """'Imagem do ChatGPT 07 out' -> 'imagem-do-chatgpt-07-out' (sem acento, para nome de arquivo)."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "bruto"


def caminho_do_bruto(origem: str | Path, dia: str) -> Path:
    """Onde o original fica guardado: `brutos/<dia>_<nome>.<ext original>`; já guardado, ele mesmo."""
    origem = Path(origem)
    if origem.resolve().parent == BRUTOS.resolve():
        return Path(_caminho_relativo(origem))
    return BRUTOS / f"{dia}_{nome_de_arquivo(origem.stem)}{origem.suffix.lower()}"


def conferir_bruto(origem: str | Path, dia: str, substituir: bool = False) -> Path:
    """Recusa, antes de qualquer cópia, um bruto de mesmo nome com OUTRO conteúdo."""
    origem, alvo = Path(origem), caminho_do_bruto(origem, dia)
    if not origem.is_file():
        raise SystemExit(f"original não encontrado: {origem}")
    if (alvo.exists() and not substituir and alvo.resolve() != origem.resolve()
            and alvo.read_bytes() != origem.read_bytes()):
        raise SystemExit(f"já existe outro original em {alvo.as_posix()}: renomeie o arquivo ou use --substituir "
                         "se é o mesmo original refeito")
    return alvo


def guardar_bruto(origem: str | Path, dia: str, substituir: bool = False) -> str:
    """Copia o original para `motion/biblioteca/brutos/` com os bytes intactos (EXIF incluído) e
    devolve o caminho relativo à raiz. O índice é versionado: nunca guarda caminho de fora do
    repositório, que só existe na máquina de quem registrou (a pasta Downloads, por exemplo)."""
    alvo = conferir_bruto(origem, dia, substituir)
    alvo.parent.mkdir(parents=True, exist_ok=True)
    if alvo.resolve() != Path(origem).resolve():
        shutil.copy2(origem, alvo)
    return alvo.as_posix()


GIRAM = (5, 6, 7, 8)  # orientações EXIF que trocam largura e altura


def orientacao(im: Image.Image) -> int:
    """`Orientation` do EXIF (1 = exibe como está gravado)."""
    try:
        return int(im.getexif().get(0x0112, 1) or 1)
    except Exception:  # EXIF corrompido: trata como sem rotação
        return 1


def tamanho_de_exibicao(caminho: Path) -> tuple[int, int]:
    """(largura, altura) como a imagem EXIBE, não como está gravada (foto de celular com
    Orientation 6 grava deitada e exibe em pé)."""
    with Image.open(caminho) as im:
        w, h = im.size
        return (h, w) if orientacao(im) in GIRAM else (w, h)


def _copiar_png(origem: Path, destino: Path) -> None:
    """Grava a peça como PNG NA ORIENTAÇÃO DE EXIBIÇÃO: PNG sem rotação no EXIF vai byte a byte;
    o resto é girado pelo EXIF e regravado sem ele — o motor desenha o pixel como está."""
    with Image.open(origem) as im:
        direto = origem.suffix.lower() == ".png" and orientacao(im) == 1
        if not direto:
            ImageOps.exif_transpose(im).save(destino, "PNG")
    if direto:
        shutil.copy2(origem, destino)


def validar_registro(nome: str, categoria: str, origem: str, prompt: str | None = None,
                     fonte: str | None = None, dia: str | None = None, substituir: bool = False) -> str:
    """Confere tudo o que dá para conferir antes de gerar ou copiar qualquer arquivo; devolve o id."""
    if not NOME_VALIDO.match(nome):
        raise SystemExit(f"nome '{nome}' inválido: use minúsculas sem acento, dígitos e hífen (ex.: xicara-branca). "
                         "Ele vira nome de arquivo e é por ele que o motor acha a peça.")
    cats = categorias()
    if categoria not in cats:
        raise SystemExit(f"categoria '{categoria}' não existe em {CATEGORIAS.as_posix()}: {sorted(cats)}. "
                         "Use uma delas ou acrescente a nova ao arquivo.")
    if origem not in ORIGENS:
        raise SystemExit(f"origem '{origem}' não existe: {list(ORIGENS)}")
    if categoria == "produto" and origem == "gerado-chatgpt":
        raise SystemExit("produto da marca entra só como pixel real (recorte de foto), nunca gerado: um modelo "
                         "redesenha o rótulo e devolve um sósia da marca. Recorte a foto real "
                         "(recortar_folha.py --origem real-verificada) ou use a categoria objeto para item genérico.")
    if origem == "gerado-chatgpt" and not (prompt or "").strip():
        raise SystemExit("origem gerado-chatgpt exige o prompt (--prompt): sem ele ninguém refaz a folha")
    if origem == "banco-livre" and not (fonte or "").strip():
        raise SystemExit("origem banco-livre exige a fonte (--fonte URL da página da foto, para a licença)")
    dia = dia or date.today().isoformat()
    try:  # o regex antes: no Python 3.11+ fromisoformat aceita 20261007 e 2026-W41-3, e o id sairia torto
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dia):
            raise ValueError
        date.fromisoformat(dia)
    except ValueError:
        raise SystemExit(f"dia '{dia}' inválido: use AAAA-MM-DD") from None
    ident = f"{dia}_{nome}"
    existente = next((i for i in carregar() if i["id"] == ident), None)
    if existente and not substituir:
        raise SystemExit(f"'{ident}' já existe na biblioteca (usado em: {', '.join(existente['usado_em']) or 'nenhum'}). "
                         "Registrar de novo sobrescreveria os PNG. Use outro nome, ou --substituir "
                         "se é a mesma peça refeita.")
    return ident


def registrar(nome: str, categoria: str, variantes: list[Path], tags: list[str], origem: str,
              bruto: str | None = None, prompt: str | None = None, fonte: str | None = None,
              dia: str | None = None, nota: str = "", substituir: bool = False) -> dict:
    """Copia as variantes para a biblioteca e grava a entrada no índice.

    O id é `<dia>_<nome>`: registrar de novo um id que já existe SOBRESCREVE os PNG que
    outros projetos usam. Por isso recusa, a menos que `substituir=True` — só para a MESMA
    peça refeita. As variantes do boil têm de ter o mesmo tamanho: cortadas cada uma na
    própria borda, o motor desenha as três com a mesma largura e o objeto pulsa a cada 3
    quadros (medido: até 2,4%).
    """
    dia = dia or date.today().isoformat()
    ident = validar_registro(nome, categoria, origem, prompt, fonte, dia, substituir)
    variantes = [Path(v) for v in variantes]
    if not variantes:
        raise SystemExit("nenhum arquivo para registrar")
    faltam = [v.as_posix() for v in variantes if not v.is_file()]
    if faltam:
        raise SystemExit(f"arquivo não encontrado: {faltam}")
    tamanhos = []
    for v in variantes:
        try:
            tamanhos.append(tamanho_de_exibicao(v))
        except OSError as e:
            raise SystemExit(f"{v.as_posix()} não é uma imagem legível: {e}") from None
    if len(set(tamanhos)) > 1:
        raise SystemExit(f"as variantes têm tamanhos diferentes {tamanhos}: corte as três pela UNIÃO dos bboxes, "
                         "senão o objeto pulsa no boil (o recortar_folha.py já faz assim)")
    tags = sorted({t.strip().lower() for t in tags if t.strip()})
    if not tags:
        raise SystemExit("dê ao menos uma tag (--tags): é por elas que a próxima peça acha esta")
    destino = PECAS / categoria
    destino.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for i, v in enumerate(variantes):
        alvo = destino / (f"{ident}-b{i}.png" if len(variantes) > 1 else f"{ident}.png")
        _copiar_png(v, alvo)
        arquivos.append(alvo.as_posix())
    itens = carregar()
    antigo = next((i for i in itens if i["id"] == ident), None)
    entrada = {
        "id": ident, "nome": nome, "categoria": categoria, "data": dia, "tags": tags, "origem": origem,
        "arquivos": arquivos, "dimensoes": list(tamanhos[0]), "bruto": bruto, "prompt": prompt, "fonte": fonte,
        "usado_em": list(antigo.get("usado_em", [])) if antigo else [], "nota": nota,
    }
    if antigo:
        sobras = [a for a in antigo.get("arquivos", []) if a not in arquivos and Path(a).exists()]
        if sobras:
            print(f"aviso: arquivos da versão anterior de {ident} que sobraram: {sobras}")
        if entrada["usado_em"]:
            print(f"aviso: {ident} está publicado em {entrada['usado_em']}; rode `publicar` de novo para "
                  "atualizar a cópia de cada peça")
    salvar([i for i in itens if i["id"] != ident] + [entrada])
    return entrada


def buscar(termos: list[str]) -> list[dict]:
    t = [x.lower() for x in termos]

    def casa(i: dict) -> bool:
        texto = " ".join([i["id"], i["categoria"], i.get("nota") or "", *i["tags"]]).lower()
        return all(x in texto for x in t)
    return [i for i in carregar() if casa(i)]


def publicar(projeto: str, ids: list[str]) -> list[Path]:
    """Copia as variantes das peças para `motion/pecas/<projeto>/public/colagem/<nome>-bN.png`."""
    _conferir_raiz()
    if Path(projeto).name != projeto or projeto in (".", ".."):
        raise SystemExit(f"'{projeto}' não é nome de peça: use só o nome da pasta em {PROJETOS.as_posix()}/, ex.: 03-tema")
    base = PROJETOS / projeto
    if not base.is_dir():
        existentes = sorted(p.name for p in PROJETOS.iterdir() if p.is_dir()) if PROJETOS.is_dir() else []
        raise SystemExit(f"a peça '{projeto}' não existe em {PROJETOS.as_posix()}/ (existentes: {existentes}). "
                         "Confira o nome; a pasta da peça nasce no roteiro.")
    itens = carregar()
    por_id = {i["id"]: i for i in itens}
    for ident in ids:
        if ident not in por_id:
            raise SystemExit(f"id '{ident}' não está no índice (use `buscar` ou `listar`)")
    # O projeto lê a peça pelo NOME (`colagem/<nome>-bN.png`), não pelo id: duas peças
    # de datas diferentes com o mesmo nome se sobrescreveriam em silêncio.
    pedidos = [por_id[i] for i in ids]
    for it in pedidos:
        rivais = [o["id"] for o in itens if o["nome"] == it["nome"] and o["id"] != it["id"]
                  and (projeto in o["usado_em"] or o in pedidos)]
        if rivais:
            raise SystemExit(f"'{it['id']}' e {rivais} têm o mesmo nome '{it['nome']}' neste projeto: "
                             "um sobrescreveria o outro. Registre com nome distinto.")
    for it in pedidos:
        sem_png = [a for a in it["arquivos"] if not Path(a).is_file()]
        if sem_png:
            raise SystemExit(f"o PNG de '{it['id']}' não está nesta máquina ({sem_png[0]}): os PNG da biblioteca "
                             "não vão para o git. Refaça a peça a partir do bruto e do prompt do índice.")
    pasta = base / "public" / "colagem"
    pasta.mkdir(parents=True, exist_ok=True)
    escritos = []
    for it in pedidos:
        for k, arq in enumerate(it["arquivos"]):
            alvo = pasta / (f"{it['nome']}-b{k}.png" if len(it["arquivos"]) > 1 else f"{it['nome']}.png")
            shutil.copy2(arq, alvo)
            escritos.append(alvo)
        if projeto not in it["usado_em"]:
            it["usado_em"].append(projeto)
        sufixo = "-b*.png" if len(it["arquivos"]) > 1 else ".png"
        print(f"publicado {it['id']} -> {pasta.as_posix()}/{it['nome']}{sufixo}")
    salvar(itens)
    return escritos


def _linha(i: dict) -> str:
    uso = ",".join(i["usado_em"]) or "-"
    falta = "" if all(Path(a).is_file() for a in i["arquivos"]) else "  SEM PNG"
    return (f"{i['id']:38s} {i['categoria']:12s} {i['origem']:19s} {i['dimensoes'][0]}x{i['dimensoes'][1]:<5d} "
            f"[{', '.join(i['tags'])}] uso:{uso}{falta}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="biblioteca.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("buscar", help="peças cujas tags, id, categoria ou nota contêm TODOS os termos")
    p.add_argument("termos", nargs="+")
    p = sub.add_parser("listar", help="todas as peças, ou só as de uma categoria")
    p.add_argument("categoria", nargs="?")
    p = sub.add_parser("publicar", help="copia peças para motion/pecas/<NN-tema>/public/colagem/")
    p.add_argument("projeto", help="pasta da peça em motion/pecas, ex.: 03-tema")
    p.add_argument("ids", nargs="+")
    p = sub.add_parser("registrar", help="registra arquivos prontos (variantes b0, b1, b2... nesta ordem)")
    p.add_argument("nome", help="minúsculas sem acento e hífen, ex.: xicara-branca")
    p.add_argument("categoria")
    p.add_argument("arquivos", nargs="+")
    p.add_argument("--tags", required=True, help="separadas por vírgula, ex.: louça,branca")
    p.add_argument("--origem", required=True, choices=ORIGENS)
    p.add_argument("--bruto", help="o original de onde a peça saiu (é copiado para motion/biblioteca/brutos/ com os bytes intactos)")
    p.add_argument("--prompt", help="prompt da geração (obrigatório para gerado-chatgpt)")
    p.add_argument("--fonte", help="URL de origem (obrigatória para banco-livre)")
    p.add_argument("--dia", help="AAAA-MM-DD (padrão: hoje)")
    p.add_argument("--nota", default="", help="observação livre (entra na busca)")
    p.add_argument("--substituir", action="store_true", help="refaz a MESMA peça com o mesmo id")
    a = ap.parse_args(argv)
    if a.cmd == "buscar":
        for i in buscar(a.termos):
            print(_linha(i))
    elif a.cmd == "listar":
        if a.categoria and a.categoria not in categorias():
            raise SystemExit(f"categoria '{a.categoria}' não existe: {sorted(categorias())}")
        for i in carregar():
            if not a.categoria or i["categoria"] == a.categoria:
                print(_linha(i))
    elif a.cmd == "publicar":
        publicar(a.projeto, a.ids)
    else:
        dia = a.dia or date.today().isoformat()
        if a.bruto:  # tudo que pode recusar antes de copiar o original
            validar_registro(a.nome, a.categoria, a.origem, a.prompt, a.fonte, dia, a.substituir)
            conferir_bruto(a.bruto, dia, a.substituir)
        e = registrar(a.nome, a.categoria, [Path(x) for x in a.arquivos], a.tags.split(","), a.origem,
                      bruto=guardar_bruto(a.bruto, dia, a.substituir) if a.bruto else None, prompt=a.prompt, fonte=a.fonte,
                      dia=dia, nota=a.nota, substituir=a.substituir)
        print(f"registrado {e['id']} ({len(e['arquivos'])} arquivo(s), {e['dimensoes'][0]}x{e['dimensoes'][1]})")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # SystemExit e avisos saem aqui
    main()
