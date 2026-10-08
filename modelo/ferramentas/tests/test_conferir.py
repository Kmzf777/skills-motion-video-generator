"""`conferir_alinhamento`: confere o tempo das palavras contra o ÁUDIO."""

from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
import pytest

import _ffmpeg
import conferir_alinhamento as C

SR = 16000


def wav_sintetico(caminho: Path) -> None:
    """silêncio 0,5 s · tom 1,0 s · silêncio 0,5 s · tom 1,0 s → ataques em 0,5 s e 2,0 s."""
    sil = np.zeros(int(0.5 * SR))
    tom = 0.3 * np.sin(2 * np.pi * 220 * np.arange(int(1.0 * SR)) / SR)
    x = np.concatenate([sil, tom, sil, tom])
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


@pytest.fixture
def caso(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    # WAV já em 16 kHz mono 16 bits é lido direto: o teste prova que nem chama o ffmpeg
    def sem_ffmpeg(*_a, **_k):
        raise AssertionError("não devia chamar o ffmpeg para um WAV 16 kHz mono")
    monkeypatch.setattr(_ffmpeg, "ffmpeg", sem_ffmpeg)
    audio = tmp_path / "narracao.wav"
    wav_sintetico(audio)
    palavras = [
        {"i": 0, "texto": "Olá", "inicio": 0.50, "fim": 1.40},
        {"i": 1, "texto": "de", "inicio": 1.00, "fim": 1.45},
        {"i": 2, "texto": "novo", "inicio": 2.10, "fim": 3.00},  # 0,1 s atrasada: suspeita
    ]
    arq = tmp_path / "palavras.json"
    arq.write_text(json.dumps(palavras, ensure_ascii=False), encoding="utf-8")
    return arq, audio


def test_pausas_acha_os_dois_ataques(caso) -> None:
    arq, audio = caso
    P = json.loads(arq.read_text(encoding="utf-8"))
    ev = C.pausas(P, _ffmpeg.carregar_audio(audio))
    assert [e["ataque"] for e in ev] == pytest.approx([0.5, 2.0], abs=0.011)
    assert [e["indice"] for e in ev] == [0, 2]
    assert [e["suspeito"] for e in ev] == [False, True]


def test_pausas_pela_linha_de_comando(caso, capsys) -> None:
    arq, audio = caso
    C.main(["pausas", str(arq), str(audio)])
    out = capsys.readouterr().out
    assert "2 ataques depois de pausa; 1 com |delta| >= 0,06 s" in out
    assert "<<<" in out


def test_faixa_desenha_envelope_e_marcas(caso, capsys) -> None:
    arq, audio = caso
    C.main(["faixa", str(arq), str(audio), "0.3-1.2", "--com", str(arq)])
    out = capsys.readouterr().out
    linhas = out.splitlines()
    assert any(linha.startswith("A ") and "^Ola" in linha for linha in linhas)
    assert any(linha.startswith("B ") and "^Ola" in linha for linha in linhas)
    assert "#" in out  # o tom aparece como voz forte
