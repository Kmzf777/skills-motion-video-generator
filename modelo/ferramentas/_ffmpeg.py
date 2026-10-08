"""Acha o ffmpeg e o ffprobe que o Remotion já instala, e lê áudio e vídeo com eles.

    from _ffmpeg import ffmpeg, ffprobe, carregar_audio, sondar_video

O `npm install` em `motion/remotion` traz uma build de ffmpeg/ffprobe em
`motion/remotion/node_modules/@remotion/compositor-<plataforma>/`:

    Windows  compositor-win32-x64-msvc/ffmpeg.exe
    macOS    compositor-darwin-arm64/ffmpeg   ou  compositor-darwin-x64/ffmpeg
    Linux    compositor-linux-x64-gnu/ffmpeg  (ou -musl; idem arm64)

Ordem de busca:
  1. `<raiz>/motion/remotion/...` — raiz = a pasta atual, porque as ferramentas rodam da
     raiz do repositório;
  2. a pasta `remotion` irmã desta (`motion/ferramentas/../remotion`), para quando o
     script roda de outra pasta;
  3. o PATH (com aviso em stderr dizendo qual binário foi usado).
Sem nenhum dos três, para dizendo o que fazer. Compositor de outra plataforma (um
`node_modules` copiado de outra máquina) é ignorado: o binário de lá não roda aqui.

Prefira o do Remotion: builds diferentes reamostram o áudio de forma diferente. Medido
(07/10/2026): a mesma narração lida pelo ffmpeg 9.0.2 do sistema em vez do do Remotion
mudou 4 de 259 palavras do alinhamento forçado, em até 0,02 s.

Cuidado medido: a build do Remotion é MÍNIMA. Não tem os filtros `fps` nem `tile` (e o
erro de `fps=2` parece de sintaxe: "No option name near '2'"), e não escreve s16le em
pipe — por isso o áudio passa por um WAV temporário. Antes de depurar a sintaxe de um
filtro, confira se ele existe nesta build: `ffmpeg -filters`.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_AVISADOS: set[str] = set()  # avisa uma vez por processo quando cai no binário do PATH


def _plataforma() -> str:
    return "linux" if sys.platform.startswith("linux") else sys.platform  # win32, darwin, linux


def _arquitetura() -> str:
    return "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "x64"


def _preferencia(pasta: str) -> int | None:
    """Quão bem um compositor serve nesta máquina: menor é melhor; None = não serve."""
    prefixo = f"compositor-{_plataforma()}-"
    if not pasta.startswith(prefixo):
        return None
    resto = pasta[len(prefixo):].split("-")  # x64-msvc · arm64 · x64-gnu · arm64-musl
    pontos = 0 if resto[0] == _arquitetura() else 2  # x64 no Mac arm64 ainda roda (Rosetta)
    if _plataforma() == "linux":
        libc = "gnu" if platform.libc_ver()[0] == "glibc" else "musl"
        pontos += 0 if resto[-1] == libc else 1
    return pontos


def _pastas_remotion(raiz: Path | str | None) -> list[Path]:
    if raiz is not None:
        return [Path(raiz) / "motion" / "remotion"]
    return [Path.cwd() / "motion" / "remotion", AQUI.parent / "remotion"]


def _achar(nome: str, raiz: Path | str | None) -> str:
    binario = nome + (".exe" if sys.platform == "win32" else "")
    for remotion in _pastas_remotion(raiz):
        base = remotion / "node_modules" / "@remotion"
        if not base.is_dir():
            continue
        achados = []
        for d in base.iterdir():
            pref = _preferencia(d.name)
            f = d / binario
            if pref is not None and f.is_file() and os.access(f, os.X_OK):
                achados.append((pref, d.name, str(f)))
        if achados:
            return min(achados)[2]
    no_path = shutil.which(nome)
    if no_path:
        if nome not in _AVISADOS:
            _AVISADOS.add(nome)
            print(f"aviso: não achei o {nome} em motion/remotion/node_modules; usando o do PATH: {no_path}",
                  file=sys.stderr)
        return no_path
    raise SystemExit(
        f"{nome} não encontrado: nem em motion/remotion/node_modules/@remotion/compositor-*/ nem no PATH. "
        "Rode `python motion/ferramentas/instalar.py` da raiz do repositório (o npm install do Remotion "
        f"traz um) ou instale o {nome} no sistema.")


def ffmpeg(raiz: Path | str | None = None) -> str:
    """Caminho do ffmpeg. `raiz` = raiz do repositório-alvo (padrão: a pasta atual)."""
    return _achar("ffmpeg", raiz)


def ffprobe(raiz: Path | str | None = None) -> str:
    """Caminho do ffprobe. `raiz` = raiz do repositório-alvo (padrão: a pasta atual)."""
    return _achar("ffprobe", raiz)


def _wav_direto(caminho: Path, sr: int):
    """Lê um WAV PCM 16 bits mono na taxa `sr` sem ffmpeg; qualquer outro formato devolve None."""
    import numpy as np

    if caminho.suffix.lower() != ".wav":
        return None
    try:
        with wave.open(str(caminho)) as w:
            if w.getnchannels() != 1 or w.getsampwidth() != 2 or w.getframerate() != sr:
                return None
            dados = w.readframes(w.getnframes())
    except (wave.Error, EOFError):
        return None
    return np.frombuffer(dados, dtype="<i2").astype(np.float32) / 32768


def carregar_audio(audio: Path | str, sr: int = 16000, raiz: Path | str | None = None):
    """Áudio mono em float32 (-1 a 1) na taxa `sr`.

    WAV que já está em PCM 16 bits mono na taxa pedida é lido direto; o resto passa pelo
    ffmpeg para um WAV temporário (a build do Remotion não escreve s16le em pipe).
    """
    audio = Path(audio)
    if not audio.is_file():
        raise SystemExit(f"áudio não encontrado: {audio}")
    x = _wav_direto(audio, sr)
    if x is not None:
        return x
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        r = subprocess.run([ffmpeg(raiz), "-v", "error", "-y", "-i", str(audio), "-ac", "1", "-ar", str(sr),
                            "-c:a", "pcm_s16le", str(wav)], capture_output=True, text=True, errors="replace")
        if r.returncode != 0:
            raise SystemExit(f"o ffmpeg não conseguiu ler {audio}: {r.stderr.strip()}")
        x = _wav_direto(wav, sr)
    if x is None:
        raise SystemExit(f"o ffmpeg não devolveu WAV 16 bits mono a {sr} Hz para {audio}")
    return x


def _numero(v) -> float | None:
    """Campo numérico do ffprobe, que pode vir ausente, vazio ou "N/A"."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x > 0 else None


def _taxa(v) -> float | None:
    """'30/1' -> 30.0; '0/0' ou ausente -> None."""
    try:
        num, den = str(v).split("/")
        return float(num) / float(den) if float(den) else None
    except (TypeError, ValueError):
        return None


def interpretar_sondagem(j: dict, video: str = "o vídeo") -> dict:
    """Do JSON do ffprobe (`-select_streams v:0 -show_streams -show_format`) às medidas do vídeo.

    Largura e altura são as DE EXIBIÇÃO: honram a matriz de rotação (displaymatrix, ou a tag
    `rotate` de ffprobe antigo) — vídeo de celular gravado 1920x1080 com rotação de -90 graus
    exibe 1080x1920. O ffmpeg gira os quadros sozinho ao decodificar.

    Duração e número de quadros vêm do FLUXO DE VÍDEO: `nb_frames`; senão `duration` do fluxo
    × fps; só por último `format.duration`, que é a do contêiner — a do fluxo mais longo. Medido
    no reel da peça de origem: format 79,1 s (era o áudio), vídeo 79,000 s e nb_frames 2370;
    ler o format primeiro aceitava os quadros 2370 a 2372, que não existem.
    """
    if not j.get("streams"):
        raise SystemExit(f"{video} não tem fluxo de vídeo")
    s = j["streams"][0]
    rot = 0.0
    for sd in s.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = float(sd["rotation"])
    if not rot and "rotate" in (s.get("tags") or {}):
        rot = float(s["tags"]["rotate"])
    largura, altura = int(s["width"]), int(s["height"])
    if round(abs(rot)) % 180 == 90:
        largura, altura = altura, largura
    fps = _taxa(s.get("avg_frame_rate")) or _taxa(s.get("r_frame_rate"))
    if not fps:
        raise SystemExit(f"{video}: o ffprobe não informou a taxa de quadros")
    nb = _numero(s.get("nb_frames"))
    dur_fluxo = _numero(s.get("duration"))
    dur_formato = _numero((j.get("format") or {}).get("duration"))
    if nb:
        quadros = int(nb)
    elif dur_fluxo:
        quadros = int(round(dur_fluxo * fps))
    elif dur_formato:
        quadros = int(round(dur_formato * fps))
    else:
        quadros = None
    duracao = dur_fluxo or (quadros / fps if quadros else None) or dur_formato or 0.0
    return {"largura": largura, "altura": altura, "fps": fps, "quadros": quadros, "duracao": duracao,
            "duracao_formato": dur_formato, "rotacao": rot}


def sondar_video(video: Path | str, raiz: Path | str | None = None) -> dict:
    """Largura e altura de exibição, fps, número de quadros e duração do primeiro fluxo de vídeo
    (ver `interpretar_sondagem`)."""
    video = Path(video)
    if not video.is_file():
        raise SystemExit(f"vídeo não encontrado: {video}")
    r = subprocess.run([ffprobe(raiz), "-v", "error", "-select_streams", "v:0", "-show_streams", "-show_format",
                        "-of", "json", str(video)], capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"o ffprobe não conseguiu ler {video}: {r.stderr.strip()}")
    return interpretar_sondagem(json.loads(r.stdout), str(video))
