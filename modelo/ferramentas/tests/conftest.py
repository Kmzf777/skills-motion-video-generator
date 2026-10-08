"""Configuração comum dos testes das ferramentas.

As ferramentas são scripts soltos em `motion/ferramentas/` (não é pacote): os testes
põem essa pasta no `sys.path` para importá-las pelo nome, como o próprio script faz
quando roda (`python motion/ferramentas/x.py` põe a pasta dele no caminho).

Nenhum teste usa rede, whisper ou torch. Só o `test_video.py` usa um ffmpeg real (o do
Remotion no repositório plantado, senão o do PATH) para montar um mp4 sintético, e pula
esses casos se não houver ffmpeg.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

FERRAMENTAS = Path(__file__).resolve().parent.parent
if str(FERRAMENTAS) not in sys.path:
    sys.path.insert(0, str(FERRAMENTAS))


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Repositório-alvo mínimo, como o plantio deixa, com a pasta atual nele.

    As ferramentas rodam da raiz do repositório e leem `motion/...` relativo a ela.
    """
    biblioteca = tmp_path / "motion" / "biblioteca"
    biblioteca.mkdir(parents=True)
    (biblioteca / "indice.json").write_text("[]\n", encoding="utf-8")
    (biblioteca / "categorias.json").write_text(
        json.dumps(["objeto", "textura", "foto-real"], ensure_ascii=False) + "\n", encoding="utf-8")
    (tmp_path / "motion" / "pecas" / "01-teste").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path
