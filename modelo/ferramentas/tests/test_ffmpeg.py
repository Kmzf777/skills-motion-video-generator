"""`_ffmpeg`: acha o ffmpeg/ffprobe que o Remotion instala, na plataforma certa."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

import pytest

import _ffmpeg

EXE = ".exe" if sys.platform == "win32" else ""


def compositor_desta_maquina() -> str:
    """Nome real da pasta que o npm instala para esta máquina (pacotes do Remotion 4)."""
    braco = platform.machine().lower() in ("arm64", "aarch64")
    if sys.platform == "win32":
        return "compositor-win32-x64-msvc"
    if sys.platform == "darwin":
        return "compositor-darwin-arm64" if braco else "compositor-darwin-x64"
    return "compositor-linux-arm64-gnu" if braco else "compositor-linux-x64-gnu"


def fabricar(raiz: Path, pasta: str, binario: str) -> Path:
    d = raiz / "motion" / "remotion" / "node_modules" / "@remotion" / pasta
    d.mkdir(parents=True, exist_ok=True)
    f = d / binario
    f.write_bytes(b"binario de mentira")
    f.chmod(0o755)
    return f


def test_acha_o_ffmpeg_do_remotion(tmp_path: Path) -> None:
    f = fabricar(tmp_path, compositor_desta_maquina(), f"ffmpeg{EXE}")
    achado = _ffmpeg.ffmpeg(raiz=tmp_path)
    assert Path(achado) == f
    assert os.access(achado, os.X_OK)


def test_acha_o_ffprobe_do_remotion(tmp_path: Path) -> None:
    f = fabricar(tmp_path, compositor_desta_maquina(), f"ffprobe{EXE}")
    assert Path(_ffmpeg.ffprobe(raiz=tmp_path)) == f


OUTRA = "compositor-linux-x64-gnu" if sys.platform == "win32" else "compositor-win32-x64-msvc"


def test_ignora_compositor_de_outra_plataforma(tmp_path: Path) -> None:
    # node_modules copiado de outra máquina, com binário de MESMO nome: só o filtro de
    # plataforma separa os dois (a ordem alfabética das pastas não decide nada aqui)
    fabricar(tmp_path, OUTRA, f"ffmpeg{EXE}")
    certo = fabricar(tmp_path, compositor_desta_maquina(), f"ffmpeg{EXE}")
    assert Path(_ffmpeg.ffmpeg(raiz=tmp_path)) == certo


def test_so_compositor_de_outra_plataforma_nao_serve(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fabricar(tmp_path, OUTRA, f"ffmpeg{EXE}")
    monkeypatch.setattr(_ffmpeg.shutil, "which", lambda nome: None)
    with pytest.raises(SystemExit, match="não encontrado"):
        _ffmpeg.ffmpeg(raiz=tmp_path)


def test_sem_remotion_usa_o_do_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    no_path = str(tmp_path / "bin" / f"ffmpeg{EXE}")
    monkeypatch.setattr(_ffmpeg.shutil, "which", lambda nome: no_path if nome == "ffmpeg" else None)
    assert _ffmpeg.ffmpeg(raiz=tmp_path) == no_path


def test_sem_nenhum_falha_dizendo_o_que_fazer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_ffmpeg.shutil, "which", lambda nome: None)
    with pytest.raises(SystemExit, match="instalar.py"):
        _ffmpeg.ffmpeg(raiz=tmp_path)


# o ffprobe do reel real da peça de origem: o contêiner dura o ÁUDIO (79,1 s), o vídeo 79,000 s
REEL = {
    "streams": [{"codec_type": "video", "width": 1080, "height": 1920, "r_frame_rate": "30/1",
                 "avg_frame_rate": "30/1", "duration": "79.000000", "nb_frames": "2370"}],
    "format": {"duration": "79.100000"},
}


def test_sondagem_conta_quadros_pelo_fluxo_de_video_nao_pelo_conteiner() -> None:
    info = _ffmpeg.interpretar_sondagem(REEL)
    assert info["quadros"] == 2370
    assert info["duracao"] == pytest.approx(79.0)
    assert info["duracao_formato"] == pytest.approx(79.1)
    assert (info["largura"], info["altura"], info["fps"]) == (1080, 1920, 30.0)


def test_sondagem_sem_nb_frames_usa_a_duracao_do_fluxo_e_por_ultimo_a_do_conteiner() -> None:
    sem_nb = {"streams": [dict(REEL["streams"][0], nb_frames="N/A")], "format": REEL["format"]}
    assert _ffmpeg.interpretar_sondagem(sem_nb)["quadros"] == 2370  # 79,000 s x 30
    so_formato = {"streams": [{k: v for k, v in REEL["streams"][0].items() if k not in ("nb_frames", "duration")}],
                  "format": REEL["format"]}
    assert _ffmpeg.interpretar_sondagem(so_formato)["quadros"] == 2373  # o único dado que sobrou


def test_sondagem_honra_a_rotacao() -> None:
    deitado = {"streams": [{"width": 1920, "height": 1080, "r_frame_rate": "30/1", "nb_frames": "30",
                            "side_data_list": [{"side_data_type": "Display Matrix", "rotation": -90}]}],
               "format": {}}
    info = _ffmpeg.interpretar_sondagem(deitado)
    assert (info["largura"], info["altura"]) == (1080, 1920)
