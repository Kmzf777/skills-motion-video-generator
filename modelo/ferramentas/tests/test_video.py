"""`varrer_movimento` e `folha_do_video`: a conta pura e um mp4 sintético de ponta a ponta."""

from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import _ffmpeg
import folha_do_video as Fv
import varrer_movimento as V


def test_desloc_mede_o_salto_da_camera_em_pixel_do_quadro_cheio() -> None:
    r = np.random.default_rng(1)
    a = r.random((240, 135)).astype(np.float32)
    b = np.roll(a, shift=(5, -3), axis=(0, 1))  # conteúdo desceu 5 e foi 3 para a esquerda
    dx, dy = V.desloc(b, a, fator=8)
    assert (dx, dy) == (-24, 40)


def test_seek_mira_meio_quadro_antes() -> None:
    # o ffmpeg entrega o 1º quadro com pts >= alvo: (q-0,5)/fps cai entre q-1 e q
    assert Fv.instante(0, 30) == 0.0
    assert Fv.instante(100, 30) == pytest.approx(99.5 / 30)
    assert 99 / 30 < Fv.instante(100, 30) < 100 / 30


@pytest.fixture
def mp4_audio_mais_longo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """30 quadros a 30 fps (1,0 s), quadro k cinza 8k, com 1,5 s de áudio: o contêiner dura mais
    que o vídeo, como no reel real. Usa o ffmpeg que `_ffmpeg` achar (o do Remotion no repo
    plantado); sem ffmpeg, ou sem codificador, o teste é pulado."""
    monkeypatch.chdir(tmp_path)
    try:
        ff = _ffmpeg.ffmpeg()
        _ffmpeg.ffprobe()
    except SystemExit:
        pytest.skip("sem ffmpeg/ffprobe nesta máquina")
    for k in range(30):
        Image.new("RGB", (64, 64), (8 * k,) * 3).save(tmp_path / f"q{k:03d}.png")
    with wave.open(str(tmp_path / "a.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        tom = 0.2 * np.sin(2 * np.pi * 440 * np.arange(24000) / 16000)
        w.writeframes((tom * 32767).astype("<i2").tobytes())
    video = tmp_path / "v.mp4"
    for codec in (["-c:v", "libx264", "-pix_fmt", "yuv420p"], ["-c:v", "mpeg4", "-q:v", "2"]):
        r = subprocess.run([ff, "-v", "error", "-y", "-framerate", "30", "-i", str(tmp_path / "q%03d.png"),
                            "-i", str(tmp_path / "a.wav"), *codec, "-c:a", "aac", str(video)],
                           capture_output=True, text=True, errors="replace")
        if r.returncode == 0:
            return video
    pytest.skip(f"este ffmpeg não codifica o mp4 de teste: {r.stderr.strip()[:200]}")


def test_sondar_le_o_fluxo_de_video_e_nao_o_audio(mp4_audio_mais_longo: Path) -> None:
    info = _ffmpeg.sondar_video(mp4_audio_mais_longo)
    assert info["quadros"] == 30
    assert info["duracao"] == pytest.approx(1.0, abs=0.04)
    assert info["duracao_formato"] > 1.4  # o contêiner dura o áudio


def test_folha_recusa_quadro_que_nao_existe_antes_de_extrair(mp4_audio_mais_longo: Path, tmp_path: Path) -> None:
    saida = tmp_path / "folha.png"
    with pytest.raises(SystemExit, match=r"\[30\] não existem.*30 quadros \(0 a 29\)"):
        Fv.folha(str(mp4_audio_mais_longo), str(saida), [29, 30])
    assert not saida.exists()


def test_folha_entrega_exatamente_o_quadro_pedido(mp4_audio_mais_longo: Path, tmp_path: Path) -> None:
    saida = tmp_path / "folha.png"
    Fv.folha(str(mp4_audio_mais_longo), str(saida), [0, 14, 29], 3)
    f = np.asarray(Image.open(saida).convert("L")).astype(float)
    for k, q in enumerate([0, 14, 29]):  # célula k: x = k*(W+4); a imagem começa em y = 20
        cel = f[20 + 8: 20 + Fv.W - 8, k * (Fv.W + 4) + 8: k * (Fv.W + 4) + Fv.W - 8]
        assert cel.mean() == pytest.approx(8 * q, abs=3), f"célula do quadro {q}"
