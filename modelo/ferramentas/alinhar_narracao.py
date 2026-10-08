"""Alinha a narração ao roteiro: tempo de cada palavra, com o texto CERTO.

    python motion/ferramentas/alinhar_narracao.py <whisper.json> <roteiro.txt> <audio16k.wav> <saida.json>

Por que existe: o whisper.cpp com `-ml 1` parte palavras em tokens e quebra os acentos
(UTF-8 cortado no meio: "café" vira "caf\\ufffd"), e escreve número falado por extenso em
algarismo ("trezentos e cinquenta" vira um token só, "350"). O texto dele não serve para
legenda; o TEMPO serve. Então o texto vem do roteiro (o que a voz leu; as tags entre
colchetes da ElevenLabs são ignoradas) e o tempo vem do whisper, casados por sequência de
letras sem acento. Palavras do roteiro que caem num token só são espalhadas pela duração
dele, em vez de empilhadas no início.

O início de uma palavra só é puxado para o fim de um silêncio (RMS no próprio áudio)
quando o whisper o marcou DENTRO desse silêncio: puxar um início que está fora de pausa
jogaria a palavra para a pausa seguinte. Isso não corrige o whisper que desliza fora de
pausa (medido: até 0,76 s), então a saída daqui é a `palavras-whisper.json` da peça, e o
tempo final sai do `alinhar_forcado.py`, que funde este com o alinhamento CTC.

Número: o whisper escreve "1974" e o roteiro diz "mil novecentos e setenta e quatro"; a
chave que casa os dois é `por_extenso`. Se a voz ler um número de outro jeito (ex.:
"nenhum" em vez de "zero"), acrescente a exceção em `NUMEROS`.

O áudio pode ser o WAV 16 kHz mono que alimentou o whisper (lido direto) ou outro formato
(convertido pelo ffmpeg do Remotion).

Saída: lista de {i, texto, inicio, fim} em segundos.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

from _ffmpeg import carregar_audio

SR = 16000


def sem_acento(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if c.isalnum() and ord(c) < 128).lower()


def palavras_roteiro(texto: str) -> list[str]:
    texto = re.sub(r"\[[^\]]*\]", " ", texto)  # tags da ElevenLabs não são faladas
    return [p for p in re.split(r"\s+", texto.replace("…", " ").strip()) if sem_acento(p)]


UNIDADES = ["zero", "um", "dois", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze",
            "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
DEZENAS = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
CENTENAS = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos",
            "oitocentos", "novecentos"]


def por_extenso(n: int) -> str:
    """Número inteiro (0 a 999.999) por extenso, como a voz lê, sem espaço nem acento:
    350 -> "trezentosecinquenta", 1974 -> "milnovecentosesetentaequatro". O whisper escreve o
    número em algarismo e o roteiro por extenso; é esta chave que casa os dois. Uma tabela
    fixa de números deixaria número novo cair em interpolação, calado."""
    def ate_mil(k: int) -> list[str]:
        if k < 20:
            return [UNIDADES[k]]
        if k < 100:
            d, u = divmod(k, 10)
            return [DEZENAS[d]] + (["e", UNIDADES[u]] if u else [])
        if k == 100:
            return ["cem"]
        c, r = divmod(k, 100)
        return [CENTENAS[c]] + (["e"] + ate_mil(r) if r else [])
    if n < 1000:
        return "".join(ate_mil(n))
    milhar, resto = divmod(n, 1000)
    partes = (["mil"] if milhar == 1 else ate_mil(milhar) + ["mil"])
    if resto:
        # "mil e cem", "mil e vinte"; mas "mil novecentos e setenta e quatro"
        partes += (["e"] if resto < 100 or resto % 100 == 0 else []) + ate_mil(resto)
    return "".join(partes)


NUMEROS = {"0": "zero"}  # exceções à regra de `por_extenso`, se a voz ler diferente


def tokens_whisper(caminho: str) -> list[tuple[float, float, str]]:
    j = json.loads(Path(caminho).read_text(encoding="utf-8", errors="replace"))
    out = []
    for s in j["transcription"]:
        t = s["text"].strip()
        if not t:
            continue
        chave = sem_acento(t.replace("%", " por cento"))
        if re.fullmatch(r"[0-9.,%]+[.,?]?", t):
            digitos = re.sub(r"[^0-9]", "", t)
            chave = NUMEROS.get(digitos) or (por_extenso(int(digitos)) if digitos and len(digitos) <= 6 else chave)
            if "%" in t:
                chave += "porcento"
        out.append((s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000, chave))
    return out


def silencios(x: np.ndarray, sr: int = SR, limiar_db: float = -38, minimo: float = 0.10) -> list[tuple[float, float]]:
    jan = int(sr * 0.01)
    n = len(x) // jan
    db = 20 * np.log10(np.sqrt((x[: n * jan].reshape(n, jan) ** 2).mean(axis=1)) + 1e-9)
    runs, st = [], None
    for i, v in enumerate(db < limiar_db):
        if v and st is None:
            st = i
        if not v and st is not None:
            if (i - st) * 0.01 >= minimo:
                runs.append((st * 0.01, i * 0.01))
            st = None
    return runs


def alinhar(whisper: str, roteiro: str, audio: str) -> list[dict]:
    rot = palavras_roteiro(Path(roteiro).read_text(encoding="utf-8"))
    if not rot:
        raise SystemExit(f"{roteiro} não tem palavras")
    wt = tokens_whisper(whisper)
    if not wt:
        raise SystemExit(f"{whisper} não tem tokens transcritos")
    # sequência de letras do roteiro e do whisper, com o índice de quem é dono de cada letra
    letras_r, dono_r = [], []
    for i, p in enumerate(rot):
        for c in sem_acento(p):
            letras_r.append(c)
            dono_r.append(i)
    letras_w, dono_w = [], []
    for k, (_, _, t) in enumerate(wt):
        for c in t:
            letras_w.append(c)
            dono_w.append(k)
    sm = difflib.SequenceMatcher(a=letras_r, b=letras_w, autojunk=False)
    primeira = {}
    for bloco in sm.get_matching_blocks():
        for d in range(bloco.size):
            i = dono_r[bloco.a + d]
            k = dono_w[bloco.b + d]
            primeira.setdefault(i, k)
    inicios = []
    for i in range(len(rot)):
        if i in primeira:
            inicios.append(wt[primeira[i]][0])
        else:
            inicios.append(None)
    # várias palavras do roteiro num token só ("trezentos e cinquenta" = "350"):
    # espalha as palavras pela duração do token em vez de empilhá-las no início
    i = 0
    while i < len(rot):
        k = primeira.get(i)
        j = i
        while j + 1 < len(rot) and k is not None and primeira.get(j + 1) == k:
            j += 1
        if k is not None and j > i:
            a, b = wt[k][0], wt[k][1]
            for n, idx in enumerate(range(i, j + 1)):
                inicios[idx] = a + (b - a) * n / (j - i + 1)
        i = j + 1
    # palavra sem casamento herda interpolação linear dos vizinhos
    for i, v in enumerate(inicios):
        if v is None:
            ant = next((inicios[j] for j in range(i - 1, -1, -1) if inicios[j] is not None), 0.0)
            pos = next((inicios[j] for j in range(i + 1, len(inicios)) if inicios[j] is not None), ant + 0.3)
            inicios[i] = (ant + pos) / 2
    sil = silencios(carregar_audio(audio, SR), SR)
    refinados = []
    for v in inicios:
        # só puxa para o fim do silêncio quando o whisper marcou o início DENTRO
        # dele (adiantou a palavra para a pausa). Início fora de silêncio fica:
        # puxar para o silêncio seguinte jogaria a palavra na pausa DEPOIS dela.
        dentro = [b for a, b in sil if a <= v <= b + 0.02]
        refinados.append(dentro[0] if dentro else v)
    # monotonia: nenhuma palavra começa antes da anterior
    for i in range(1, len(refinados)):
        refinados[i] = max(refinados[i], refinados[i - 1] + 0.04)
    fins = []
    for i, v in enumerate(refinados):
        prox = refinados[i + 1] if i + 1 < len(refinados) else v + 0.6
        corte = [a for a, b in sil if v < a < prox]
        fins.append(min(corte) if corte else prox)
    return [{"i": i, "texto": rot[i], "inicio": round(refinados[i], 3), "fim": round(fins[i], 3)}
            for i in range(len(rot))]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="alinhar_narracao.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("whisper", help="JSON do whisper.cpp (saída de -oj)")
    ap.add_argument("roteiro", help="roteiro.txt da peça: exatamente o que a voz leu")
    ap.add_argument("audio", help="a narração (o WAV 16 kHz mono que foi ao whisper)")
    ap.add_argument("saida", help="JSON de saída, normalmente motion/pecas/<NN-tema>/palavras-whisper.json")
    a = ap.parse_args(argv)
    res = alinhar(a.whisper, a.roteiro, a.audio)
    Path(a.saida).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    sem = sum(1 for r in res if r["fim"] <= r["inicio"])
    print(f"{len(res)} palavras alinhadas; {sem} com duração nula -> {a.saida}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # SystemExit e avisos saem aqui
    main()
