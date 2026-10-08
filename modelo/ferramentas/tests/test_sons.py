"""`sons`: efeitos de colagem e a trilha em seções que começam em FRASES da narração."""

from __future__ import annotations

import json
import math
import re
import wave
from pathlib import Path

import numpy as np
import pytest

import sons as S

FALA = ("Isso parece simples demais Calma que tem mais E aqui vem o segredo "
        "Por isso a gente faz assim Salva esse vídeo agora").split()


def peca(tmp_path: Path, secoes: list[dict], bpm: int = 88) -> Path:
    p = tmp_path / "motion" / "pecas" / "01-teste"
    p.mkdir(parents=True)
    palavras = [{"i": i, "texto": t, "inicio": round(0.2 + 0.3 * i, 3), "fim": round(0.45 + 0.3 * i, 3)}
                for i, t in enumerate(FALA)]
    (p / "palavras.json").write_text(json.dumps(palavras, ensure_ascii=False), encoding="utf-8")
    (p / "sons.json").write_text(json.dumps({"bpm": bpm, "secoes": secoes}, ensure_ascii=False), encoding="utf-8")
    return p


SECOES = [
    {"frase": "Calma", "tipo": "groove"},
    {"frase": "E aqui vem", "tipo": "respiro"},
    {"frase": "Por isso a gente", "tipo": "groove"},
    {"frase": "Salva esse vídeo", "tipo": "fecho"},
]


def ler(arq: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(arq)) as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    return x, sr


def test_gera_trilha_com_duracao_DUR_e_os_efeitos_padrao(tmp_path: Path) -> None:
    p = peca(tmp_path, SECOES)
    S.main([str(p)])
    sfx = p / "public" / "sfx"
    ultima = 0.45 + 0.3 * (len(FALA) - 1)
    dur = math.ceil((ultima + 0.5) * 10) / 10  # a mesma regra do FIM no roteiro.ts
    x, sr = ler(sfx / "trilha.wav")
    assert abs(len(x) / sr - dur) < 1 / sr
    for nome in EFEITOS:
        assert (sfx / f"{nome}.wav").exists(), nome
    # antes da primeira seção é tensão: a trilha fica muda até "Calma"
    calma = 0.2 + 0.3 * FALA.index("Calma")
    assert np.abs(x[: int((calma - 0.05) * sr)]).max() == 0
    assert np.abs(x[int((calma + 0.2) * sr): int((calma + 1.0) * sr)]).max() > 0.05
    # o drone cobre a tensão e some 0,6 s depois da primeira seção
    d, _ = ler(sfx / "drone.wav")
    assert len(d) / sr == pytest.approx(math.ceil((calma + 0.6) * 10) / 10, abs=1 / sr)


# Os 23 nomes que o motor toca (tipo `Efeito` em remotion/src/colagem/sons.ts). Fixos aqui:
# tirar um efeito do gerador tem de quebrar este teste, não o render (404 no meio da peça).
EFEITOS = ("thump", "tick", "tink", "rasgo", "slide", "pop", "carimbo", "ding", "whoosh", "vento",
           "nota1", "nota2", "nota3", "nota4", "batimento", "rabisco", "fita", "digitacao", "golinho",
           "graos", "brilho", "chicote", "drone")


def test_o_gerador_produz_exatamente_os_efeitos_do_motor() -> None:
    assert len(EFEITOS) == 23
    assert sorted(S.EFEITOS_PADRAO) == sorted(EFEITOS)
    sons_ts = Path(__file__).resolve().parents[2] / "remotion" / "src" / "colagem" / "sons.ts"
    if sons_ts.is_file():  # na semente e no repositório plantado o motor fica ao lado
        tipo = re.search(r"export type Efeito\s*=([^;]+);", sons_ts.read_text(encoding="utf-8"))
        assert tipo, f"não achei `export type Efeito` em {sons_ts}"
        assert sorted(re.findall(r"'([^']+)'", tipo.group(1))) == sorted(EFEITOS)


def test_dur_arredonda_para_cima_ao_decimo(tmp_path: Path) -> None:
    """Fim 7,02 s: DUR = ceil(75,2)/10 = 7,6. round daria 7,5 e cortaria o último 0,1 s."""
    p = tmp_path / "pecas" / "02-dur"
    p.mkdir(parents=True)
    palavras = [{"i": 0, "texto": "Calma", "inicio": 0.5, "fim": 1.0},
                {"i": 1, "texto": "fim", "inicio": 6.5, "fim": 7.02}]
    (p / "palavras.json").write_text(json.dumps(palavras), encoding="utf-8")
    (p / "sons.json").write_text(json.dumps({"bpm": 88, "secoes": [{"frase": "Calma", "tipo": "groove"}]}),
                                 encoding="utf-8")
    assert S.duracao(palavras) == pytest.approx(7.6)
    assert round(7.02 + 0.5, 1) == 7.5  # o caso em que round e ceil divergem
    S.main([str(p)])
    x, sr = ler(p / "public" / "sfx" / "trilha.wav")
    assert len(x) == int(7.6 * sr)


def test_mesmos_bytes_ao_rodar_de_novo(tmp_path: Path) -> None:
    p = peca(tmp_path, SECOES)
    S.main([str(p)])
    antes = {f.name: f.read_bytes() for f in (p / "public" / "sfx").glob("*.wav")}
    S.main([str(p)])
    depois = {f.name: f.read_bytes() for f in (p / "public" / "sfx").glob("*.wav")}
    assert antes == depois


def test_frase_que_nao_existe_falha_com_mensagem(tmp_path: Path) -> None:
    p = peca(tmp_path, [{"frase": "Calma", "tipo": "groove"}, {"frase": "Frase inexistente", "tipo": "fecho"}])
    with pytest.raises(SystemExit, match="Frase inexistente"):
        S.main([str(p)])
    assert not (p / "public" / "sfx" / "trilha.wav").exists()


def test_secoes_fora_da_ordem_da_fala_falham(tmp_path: Path) -> None:
    p = peca(tmp_path, [{"frase": "Por isso a gente", "tipo": "groove"}, {"frase": "Calma", "tipo": "respiro"}])
    with pytest.raises(SystemExit, match="ordem"):
        S.main([str(p)])


def test_tipo_invalido_e_fecho_fora_do_fim_falham(tmp_path: Path) -> None:
    p = peca(tmp_path, [{"frase": "Calma", "tipo": "balada"}])
    with pytest.raises(SystemExit, match="tipo"):
        S.main([str(p)])
    p2 = peca(tmp_path / "b", [{"frase": "Calma", "tipo": "fecho"}, {"frase": "E aqui vem", "tipo": "groove"}])
    with pytest.raises(SystemExit, match="fecho"):
        S.main([str(p2)])
