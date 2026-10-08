"""`por_extenso`: a chave que casa o algarismo do whisper com o número por extenso do roteiro.

O whisper escreve "1974"; o roteiro (o que a voz leu) diz "mil novecentos e setenta e
quatro". A chave é o extenso sem espaço nem acento.
"""

from __future__ import annotations

import json

import pytest

from alinhar_narracao import por_extenso, tokens_whisper

CASOS = {
    0: "zero",
    1: "um",
    16: "dezesseis",
    21: "vinteeum",
    80: "oitenta",
    85: "oitentaecinco",
    100: "cem",
    101: "centoeum",
    350: "trezentosecinquenta",
    999: "novecentosenoventaenove",
    1000: "mil",
    1020: "milevinte",
    1100: "milecem",
    1340: "miltrezentosequarenta",
    1974: "milnovecentosesetentaequatro",
    2000: "doismil",
    2026: "doismilevinteeseis",
}


@pytest.mark.parametrize(("n", "esperado"), CASOS.items())
def test_por_extenso(n: int, esperado: str) -> None:
    assert por_extenso(n) == esperado


def test_token_numerico_do_whisper_vira_extenso(tmp_path) -> None:
    """Algarismo, milhar com ponto e porcentagem viram a chave do extenso."""
    whisper = {"transcription": [
        {"text": " 350", "offsets": {"from": 0, "to": 500}},
        {"text": " 1.974", "offsets": {"from": 500, "to": 1200}},
        {"text": " 10%", "offsets": {"from": 1200, "to": 1600}},
        {"text": " café", "offsets": {"from": 1600, "to": 2000}},
    ]}
    arq = tmp_path / "whisper.json"
    arq.write_text(json.dumps(whisper, ensure_ascii=False), encoding="utf-8")
    chaves = [c for _, _, c in tokens_whisper(str(arq))]
    assert chaves == ["trezentosecinquenta", "milnovecentosesetentaequatro", "dezporcento", "cafe"]
