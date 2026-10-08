"""Instala o que as ferramentas e o motor precisam, tudo dentro de motion/.

    python motion/ferramentas/instalar.py [--sem-modelos] [--plano]

Rode da raiz do repositório onde a estudio-reels foi plantada, com o Python do sistema
(>= 3.10): este script só usa a biblioteca padrão, porque roda antes do venv existir.

O que faz, nesta ordem, mostrando o tamanho de tudo ANTES de baixar:
  1. cria motion/.venv;
  2. instala no venv os pacotes base do requirements.txt (numpy, pillow,
     opencv-python-headless, pytest);
  3. torch + torchaudio para CPU, usados pelo alinhar_forcado.py   [pulado com --sem-modelos]
  4. npm install em motion/remotion — exige o Node de `engines.node` do package.json do motor
     (maior E menor); traz também o ffmpeg/ffprobe que as ferramentas usam;
  5. whisper.cpp 1.5.5 com o modelo `small` em motion/ferramentas/whisper.cpp/
     [pulado com --sem-modelos]
  6. confere o efeito, não o código de saída: importa os pacotes no venv, acha o ffmpeg do
     Remotion, o executável e o modelo do whisper.

--plano    mostra o que seria baixado, o espaço em disco e os requisitos, e sai sem instalar
           nada. É o que se mostra ao usuário para pedir o OK antes de baixar ~1 GB.
--sem-modelos  pula whisper.cpp, torch e torchaudio (teste rápido do plantio).
torch vem do índice CPU do PyTorch (https://download.pytorch.org/whl/cpu), a mesma build
validada (2.10.0+cpu); no Linux o torch do PyPI traria CUDA (+2 GB) sem uso aqui.

Baixado depois, na primeira vez que for usado (não por este script):
  - o Chrome Headless Shell do Remotion (~270 MB), no primeiro render ou still;
  - o modelo MMS_FA (1.262 MB), no primeiro alinhar_forcado.py, para o cache do torch.

Idempotente: rodar de novo reaproveita o venv, o node_modules e o whisper já instalados.
Whisper: modelo `small` (multilíngue, 487.601.967 bytes). `medium` (1,5 GB) já falhou por
falta de disco; os modelos `.en` só entendem inglês. No Windows o pacote baixa o binário
pronto; no macOS/Linux ele clona o repositório e compila (precisa de git, make e um
compilador C).
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MOTION = Path("motion")
FERRAMENTAS = MOTION / "ferramentas"
REMOTION = MOTION / "remotion"
VENV = MOTION / ".venv"
REQUISITOS = FERRAMENTAS / "requirements.txt"
WHISPER = FERRAMENTAS / "whisper.cpp"
VERSAO_WHISPER = "1.5.5"  # o pacote baixa o binário pronto no Windows só para versão semver
MODELO_WHISPER = "small"
BYTES_MODELO_WHISPER = 487_601_967
INDICE_TORCH_CPU = "https://download.pytorch.org/whl/cpu"
PACOTES_MODELOS = {"torch", "torchaudio"}
WIN = sys.platform == "win32"


@dataclass
class Etapa:
    chave: str
    titulo: str
    baixa: bool
    megabytes: int | None  # download aproximado
    disco_mb: int  # espaço em disco aproximado depois de instalado
    nota: str = ""


def plano(sem_modelos: bool = False) -> list[Etapa]:
    """As etapas da instalação e o tamanho de cada uma.

    Disco medido em 07/10/2026 (Windows x64): numpy 35 MB, pillow 16 MB, cv2 113 MB;
    torch 2.10.0+cpu 479 MB, torchaudio 3,5 MB; node_modules do motor 558 MB (+270 MB do
    Chrome baixado no 1º render); whisper.cpp 471 MB. Download é estimativa (~).
    """
    etapas = [
        Etapa("venv", f"ambiente Python em {VENV.as_posix()}", False, None, 25),
        Etapa("python-base", "numpy, pillow, opencv-python-headless, pytest", True, 60, 180),
    ]
    if not sem_modelos:
        etapas.append(Etapa("torch", "torch + torchaudio para CPU", True, 200, 490, f"índice {INDICE_TORCH_CPU}"))
    etapas.append(Etapa("npm", f"npm install em {REMOTION.as_posix()} (Remotion, React, ffmpeg)", True, 250, 560,
                        "o 1º render ainda baixa o Chrome Headless Shell, ~270 MB"))
    if not sem_modelos:
        etapas.append(Etapa("whisper", f"whisper.cpp {VERSAO_WHISPER} + modelo {MODELO_WHISPER} em {WHISPER.as_posix()}",
                            True, 495, 475,
                            "binário pronto" if WIN else "git clone + make (compila)"))
    return etapas


def depois(sem_modelos: bool) -> list[tuple[str, int]]:
    """O que baixa sozinho mais tarde, no primeiro uso."""
    itens = [("Chrome Headless Shell do Remotion, no 1º render/still", 270)]
    if not sem_modelos:
        ja = (_cache_torch() / "hub" / "checkpoints" / "model.pt").is_file()
        itens.append(("modelo MMS_FA do alinhar_forcado.py, no 1º alinhamento (cache do torch"
                      + ("; parece já estar lá" if ja else "") + ")", 1262))
    return itens


def nome_do_pacote(requisito: str) -> str:
    m = re.match(r"\s*([A-Za-z0-9._-]+)", requisito)
    return m.group(1).lower().replace("_", "-") if m else ""


def separar_requisitos(texto: str) -> tuple[list[str], list[str]]:
    """(base, modelos): torch/torchaudio vão à parte, do índice CPU, e o --sem-modelos os pula."""
    base, modelos = [], []
    for linha in texto.splitlines():
        linha = linha.split("#", 1)[0].strip()
        if not linha:
            continue
        (modelos if nome_do_pacote(linha) in PACOTES_MODELOS else base).append(linha)
    return base, modelos


def _mb(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".") + " MB"


def _livre_mb(caminho: Path) -> float:
    p = caminho.resolve()
    while not p.exists():
        p = p.parent
    return shutil.disk_usage(p).free / 1e6


def _cache_torch() -> Path:
    if os.environ.get("TORCH_HOME"):
        return Path(os.environ["TORCH_HOME"])
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "torch"


def _python_do_venv() -> Path:
    return VENV / ("Scripts/python.exe" if WIN else "bin/python")


def _tripla(v: str) -> tuple[int, int, int]:
    """'v22.12.0' / '>=22.12.0' / '22' -> (22, 12, 0)."""
    m = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", v or "")
    if not m:
        raise ValueError(v)
    return tuple(int(x or 0) for x in m.groups())  # type: ignore[return-value]


def node_exigido() -> tuple[int, int, int]:
    """O mínimo de `engines.node` do package.json do motor (ex.: ">=22.12.0"). Sem o campo, 18."""
    try:
        eng = json.loads((REMOTION / "package.json").read_text(encoding="utf-8")).get("engines", {}).get("node")
    except (OSError, ValueError):
        eng = None
    if not eng:
        return (18, 0, 0)
    if not re.fullmatch(r"\s*(>=|\^)?\s*v?\d+(\.\d+){0,2}\s*", eng):
        raise SystemExit(f"engines.node '{eng}' em {(REMOTION / 'package.json').as_posix()}: só sei ler '>=X.Y.Z'")
    return _tripla(eng)


def _versao_node(node: str) -> tuple[tuple[int, int, int], str]:
    try:
        v = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
        return _tripla(v), v
    except (OSError, ValueError, subprocess.SubprocessError):
        return (0, 0, 0), "?"


def requisitos(sem_modelos: bool) -> list[tuple[str, bool, str]]:
    """(item, ok, detalhe) de cada programa que precisa existir ANTES de instalar."""
    out = [("Python >= 3.10", sys.version_info >= (3, 10), platform.python_version())]
    node = shutil.which("node")
    tem, versao = _versao_node(node) if node else ((0, 0, 0), "não encontrado")
    precisa = node_exigido()  # maior E menor (e patch): Node 22.11 não serve a ">=22.12.0"
    out.append((f"Node >= {'.'.join(map(str, precisa))} (engines.node do motor)", tem >= precisa, versao))
    out.append(("npm", bool(shutil.which("npm")), shutil.which("npm") or "não encontrado"))
    if not sem_modelos and not WIN:
        for prog in ("git", "make"):
            out.append((f"{prog} (compilar o whisper.cpp)", bool(shutil.which(prog)), shutil.which(prog) or "não encontrado"))
        cc = next((c for c in ("cc", "gcc", "clang") if shutil.which(c)), None)
        out.append(("compilador C (cc/gcc/clang)", bool(cc), cc or "não encontrado"))
    return out


def mostrar_plano(etapas: list[Etapa], sem_modelos: bool) -> tuple[float, float]:
    print(f"Plano de instalação em {MOTION.resolve()} (Python {platform.python_version()}, "
          f"{platform.system()} {platform.machine()})")
    for e in etapas:
        baixa = f"baixa ~{_mb(e.megabytes)}" if e.baixa and e.megabytes is not None else "não baixa"
        nota = f"  ({e.nota})" if e.nota else ""
        print(f"  - {e.chave:12s} {e.titulo}\n      {baixa}; disco ~{_mb(e.disco_mb)}{nota}")
    baixar = sum(e.megabytes or 0 for e in etapas if e.baixa)
    disco = sum(e.disco_mb for e in etapas)
    print(f"Agora: baixa ~{_mb(baixar)} e ocupa ~{_mb(disco)} em motion/.")
    print("Depois, no primeiro uso (baixa sozinho):")
    for item, mb in depois(sem_modelos):
        print(f"  - {item}: ~{_mb(mb)}")
    return baixar, disco


def conferir_espaco(etapas: list[Etapa], sem_modelos: bool, parar: bool) -> None:
    precisa = sum(e.disco_mb for e in etapas) + 270 + 300  # + Chrome do 1º render + folga
    livre = _livre_mb(MOTION)
    print(f"Espaço livre no disco de motion/: ~{_mb(livre)} (precisa ~{_mb(precisa)} com folga)")
    if not sem_modelos:
        cache = _cache_torch()
        livre_cache = _livre_mb(cache)
        print(f"Espaço livre no disco do cache do torch ({cache}): ~{_mb(livre_cache)} (o MMS_FA precisa ~1.262 MB)")
        if livre_cache < 1262 + 200:
            print("  ATENÇÃO: falta espaço para o modelo MMS_FA; libere antes do primeiro alinhamento "
                  "(ou aponte TORCH_HOME para outro disco)")
    if livre < precisa and parar:
        raise SystemExit(f"espaço insuficiente: ~{_mb(livre)} livres, precisa ~{_mb(precisa)}. Nada foi baixado. "
                         "Libere espaço (ou rode com --sem-modelos para o teste rápido).")


def _rodar(cmd: list, cwd: Path | None = None, env: dict | None = None, dica: str = "") -> None:
    cmd = [str(c) for c in cmd]
    print("$ " + " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env)
    if r.returncode != 0:
        raise SystemExit(f"falhou (código {r.returncode}): {' '.join(cmd)}" + (f"\n{dica}" if dica else ""))


JS_WHISPER = (
    "const w = require('@remotion/install-whisper-cpp');"
    "(async () => {"
    " const to = process.env.ESTUDIO_WHISPER_DIR;"
    " await w.installWhisperCpp({to, version: process.env.ESTUDIO_WHISPER_VERSAO});"
    " await w.downloadWhisperModel({folder: to, model: process.env.ESTUDIO_WHISPER_MODELO});"
    "})().catch((e) => { console.error(e); process.exit(1); });"
)  # sem aspas duplas nem &&: o argumento passa intacto mesmo se o node for um atalho .cmd


def executavel_whisper() -> Path:
    return WHISPER / ("main.exe" if WIN else "main")  # whisper.cpp < 1.7.4: o binário chama main


def instalar_whisper() -> None:
    exe = executavel_whisper()
    if WHISPER.exists() and not exe.exists():
        raise SystemExit(f"{WHISPER.as_posix()} existe mas sem {exe.name} (instalação interrompida?): "
                         "apague essa pasta e rode de novo.")
    pacote = REMOTION / "node_modules" / "@remotion" / "install-whisper-cpp"
    if not pacote.is_dir():
        raise SystemExit(f"falta {pacote.as_posix()}: o package.json do motor tem de listar "
                         "@remotion/install-whisper-cpp (mesma versão do remotion).")
    env = dict(os.environ, ESTUDIO_WHISPER_DIR=str(WHISPER.resolve()), ESTUDIO_WHISPER_VERSAO=VERSAO_WHISPER,
               ESTUDIO_WHISPER_MODELO=MODELO_WHISPER)
    _rodar([shutil.which("node") or "node", "-e", JS_WHISPER], cwd=REMOTION, env=env,
           dica="" if WIN else "No macOS/Linux o whisper.cpp é compilado: confira git, make e o compilador C.")


def conferir_whisper() -> None:
    """O executável existe e o modelo tem EXATAMENTE o tamanho validado; senão para."""
    exe, modelo = executavel_whisper(), WHISPER / f"ggml-{MODELO_WHISPER}.bin"
    if not exe.is_file() or not modelo.is_file():
        raise SystemExit(f"o whisper não ficou completo: {exe.as_posix()} e {modelo.as_posix()} têm de existir")
    tam = modelo.stat().st_size
    if tam != BYTES_MODELO_WHISPER:
        raise SystemExit(f"{modelo.as_posix()} tem {tam} bytes; o modelo {MODELO_WHISPER} validado tem "
                         f"{BYTES_MODELO_WHISPER}. Download incompleto ou modelo trocado: apague o arquivo e "
                         "rode de novo.")
    print(f"  whisper: {exe.as_posix()} · {modelo.name} {tam} bytes (confere)")


def conferir(sem_modelos: bool) -> None:
    """Confere o EFEITO da instalação: código de saída 0 não prova que o pacote funciona."""
    py = _python_do_venv()
    print("\nConferência:")
    _rodar([py, "-c", "import numpy, PIL, cv2, pytest; print('  pacotes base ok: numpy', numpy.__version__, "
                      "'opencv', cv2.__version__)"])
    if not sem_modelos:
        _rodar([py, "-c", "import torch, torchaudio; import torchaudio.functional as F; "
                          "from torchaudio.pipelines import MMS_FA; F.forced_align; F.merge_tokens; "
                          "print('  torch', torch.__version__, 'torchaudio', torchaudio.__version__, "
                          "'forced_align ok')"],
               dica="o torchaudio instalado não tem forced_align/MMS_FA: fixe a versão validada (2.10).")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _ffmpeg  # só biblioteca padrão no nível do módulo

    ff = _ffmpeg.ffmpeg()
    print(f"  ffmpeg: {ff}")
    if not sem_modelos:
        conferir_whisper()
    print("\nPronto. As ferramentas rodam com o Python do venv, da raiz do repositório:")
    print(f"  {_python_do_venv().as_posix()} motion/ferramentas/<ferramenta>.py --help")
    print(f"  {_python_do_venv().as_posix()} -m pytest motion/ferramentas/tests -q")
    if not sem_modelos:
        print("Transcrição (fase de tempo), com o ffmpeg e o whisper instalados aqui:")
        print(f'  "{ff}" -y -v error -i <narracao.mp3> -ar 16000 -ac 1 -c:a pcm_s16le <n16k.wav>')
        print(f"  {executavel_whisper().as_posix()} -m {WHISPER.as_posix()}/ggml-{MODELO_WHISPER}.bin -f <n16k.wav> "
              "-l pt -ml 1 -sow -oj -of <saida-sem-extensao>   (-l = idioma da narração)")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="instalar.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sem-modelos", action="store_true", help="pula whisper.cpp, torch e torchaudio")
    ap.add_argument("--plano", action="store_true", help="só mostra o que baixaria e o espaço; não instala nada")
    a = ap.parse_args(argv)

    if sys.version_info < (3, 10):
        raise SystemExit(f"Python {platform.python_version()}: as ferramentas pedem 3.10 ou mais novo")
    if not REQUISITOS.is_file() or not (REMOTION / "package.json").is_file():
        raise SystemExit(f"não achei {REQUISITOS.as_posix()} e {(REMOTION / 'package.json').as_posix()} em "
                         f"{Path.cwd()}: rode da raiz do repositório onde a estudio-reels foi plantada.")
    base, modelos = separar_requisitos(REQUISITOS.read_text(encoding="utf-8"))
    etapas = plano(a.sem_modelos)
    mostrar_plano(etapas, a.sem_modelos)
    reqs = requisitos(a.sem_modelos)
    print("Requisitos:")
    for item, ok, detalhe in reqs:
        print(f"  [{'ok' if ok else 'FALTA'}] {item}: {detalhe}")
    conferir_espaco(etapas, a.sem_modelos, parar=not a.plano)
    if a.plano:
        print("\n--plano: nada foi instalado.")
        return
    faltam = [item for item, ok, _ in reqs if not ok]
    if faltam:
        raise SystemExit(f"instale antes: {', '.join(faltam)}. Nada foi baixado.")

    print()
    py = _python_do_venv()
    if not py.exists():
        _rodar([sys.executable, "-m", "venv", VENV], dica="No Debian/Ubuntu instale o módulo venv: "
                                                          "sudo apt install python3-venv")
    pip = [py, "-m", "pip", "install", "--disable-pip-version-check"]
    _rodar(pip + base)
    if not a.sem_modelos:
        _rodar(pip + ["--index-url", INDICE_TORCH_CPU] + modelos)
    npm = shutil.which("npm") or "npm"
    _rodar([npm, "install", "--no-fund", "--no-audit"], cwd=REMOTION)
    if not a.sem_modelos:
        instalar_whisper()
    conferir(a.sem_modelos)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # SystemExit e avisos saem aqui
    main()
