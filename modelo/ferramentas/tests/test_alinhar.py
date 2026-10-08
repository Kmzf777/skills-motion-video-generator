"""Alinhamento: texto do roteiro + tempo do whisper, e a fusão whisper + CTC sem torch."""

from __future__ import annotations

import importlib
import json
import sys
import wave
from pathlib import Path

import numpy as np
import pytest

SR = 16000


def gravar_wav(caminho: Path, trechos: list[tuple[str, float]], sr: int = SR) -> np.ndarray:
    """WAV mono 16 bits: cada trecho é ('silencio' | 'tom', duração em s)."""
    partes = []
    for tipo, dur in trechos:
        n = int(round(dur * sr))
        if tipo == "tom":
            partes.append(0.3 * np.sin(2 * np.pi * 220 * np.arange(n) / sr))
        else:
            partes.append(np.zeros(n))
    x = np.concatenate(partes)
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    return x.astype(np.float32)


def test_alinhar_usa_o_texto_do_roteiro_e_espalha_o_numero(tmp_path: Path) -> None:
    import alinhar_narracao as A

    # o whisper quebra o acento ("Caf�") e junta "trezentos e cinquenta" num token "350"
    whisper = {"transcription": [
        {"text": " Caf�", "offsets": {"from": 100, "to": 400}},
        {"text": " custa", "offsets": {"from": 450, "to": 800}},
        {"text": " 350", "offsets": {"from": 850, "to": 1600}},
        {"text": " reais", "offsets": {"from": 1650, "to": 2100}},
    ]}
    (tmp_path / "whisper.json").write_text(json.dumps(whisper), encoding="utf-8")
    # a tag da ElevenLabs não é falada e não pode virar palavra
    (tmp_path / "roteiro.txt").write_text("[calm] Café custa trezentos e cinquenta reais.", encoding="utf-8")
    gravar_wav(tmp_path / "n16k.wav", [("silencio", 0.1), ("tom", 2.0), ("silencio", 0.5)])

    res = A.alinhar(str(tmp_path / "whisper.json"), str(tmp_path / "roteiro.txt"), str(tmp_path / "n16k.wav"))

    assert [r["texto"] for r in res] == ["Café", "custa", "trezentos", "e", "cinquenta", "reais."]
    assert [r["inicio"] for r in res] == pytest.approx([0.10, 0.45, 0.85, 1.10, 1.35, 1.65], abs=1e-3)
    inicios = [r["inicio"] for r in res]
    assert inicios == sorted(inicios)
    assert all(r["fim"] > r["inicio"] for r in res)


def test_alinhar_cli_grava_saida(tmp_path: Path) -> None:
    import alinhar_narracao as A

    whisper = {"transcription": [{"text": " Olá", "offsets": {"from": 200, "to": 600}}]}
    (tmp_path / "w.json").write_text(json.dumps(whisper), encoding="utf-8")
    (tmp_path / "r.txt").write_text("Olá", encoding="utf-8")
    gravar_wav(tmp_path / "a.wav", [("silencio", 0.2), ("tom", 0.5), ("silencio", 0.3)])
    A.main([str(tmp_path / "w.json"), str(tmp_path / "r.txt"), str(tmp_path / "a.wav"), str(tmp_path / "p.json")])
    saida = json.loads((tmp_path / "p.json").read_text(encoding="utf-8"))
    assert saida == [{"i": 0, "texto": "Olá", "inicio": 0.2, "fim": pytest.approx(0.8, abs=1e-3)}]


@pytest.fixture
def sem_torch(monkeypatch: pytest.MonkeyPatch):
    """Simula a máquina sem torch/torchaudio (o `--sem-modelos` do instalar)."""
    for nome in ("torch", "torchaudio", "torchaudio.functional", "torchaudio.pipelines"):
        monkeypatch.setitem(sys.modules, nome, None)
    monkeypatch.delitem(sys.modules, "alinhar_forcado", raising=False)
    return importlib.import_module("alinhar_forcado")


def test_alinhar_forcado_importa_e_mostra_ajuda_sem_torch(sem_torch, capsys) -> None:
    with pytest.raises(SystemExit) as fim:
        sem_torch.main(["--help"])
    assert fim.value.code == 0
    assert "palavras-whisper" in capsys.readouterr().out


def test_alinhar_forcado_sem_torch_falha_dizendo_o_que_instalar(sem_torch) -> None:
    x = np.zeros(SR, np.float32)
    with pytest.raises(SystemExit, match="instalar.py"):
        sem_torch.alinhar([{"i": 0, "texto": "oi", "inicio": 0.1, "fim": 0.3}], x)


def test_fundir_regras_sem_modelo(tmp_path: Path, sem_torch) -> None:
    """A fusão é numpy puro: ataque depois de pausa, média e CTC quando o whisper desliza."""
    x = gravar_wav(tmp_path / "f.wav", [("silencio", 0.5), ("tom", 0.5), ("silencio", 0.3), ("tom", 0.7)])
    whisper = [
        {"i": 0, "texto": "um", "inicio": 0.52, "fim": 0.9},
        {"i": 1, "texto": "dois", "inicio": 1.45, "fim": 1.6},
        {"i": 2, "texto": "três", "inicio": 1.62, "fim": 1.8},
        {"i": 3, "texto": "quatro", "inicio": 2.50, "fim": 2.6},  # o whisper deslizou 0,65 s
    ]
    ctc = [
        {"i": 0, "texto": "um", "inicio": 0.55, "fim": 0.9, "confianca": 0.9},
        {"i": 1, "texto": "dois", "inicio": 1.32, "fim": 1.6, "confianca": 0.9},
        {"i": 2, "texto": "três", "inicio": 1.70, "fim": 1.8, "confianca": 0.9},
        {"i": 3, "texto": "quatro", "inicio": 1.85, "fim": 1.95, "confianca": 0.9},
    ]
    res = sem_torch.fundir(whisper, ctc, x)
    assert [r["inicio"] for r in res] == pytest.approx([0.50, 1.30, 1.62, 1.81], abs=1e-3)
    assert [r["regra"].split(" ")[0] for r in res] == ["pausa", "pausa", "média", "ctc"]
