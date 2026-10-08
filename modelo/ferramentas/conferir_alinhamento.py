"""Confere o tempo das palavras contra o ÁUDIO, não contra outro alinhador.

Dois modos:

    python motion/ferramentas/conferir_alinhamento.py pausas <palavras.json> <audio>
        Lista cada ataque de voz depois de uma pausa funda e a palavra do JSON mais perto
        dele. Delta acima de ±0,06 s é suspeito (marcado <<<): é a primeira conferência, a
        que pega o alinhador deslizando (na peça de origem o whisper chegou a 0,7 s).

    python motion/ferramentas/conferir_alinhamento.py faixa <palavras.json> <audio> 1.2-3.4 [...] [--com outro.json]
        Desenha o envelope do áudio em caracteres de 20 ms e marca embaixo o início de cada
        palavra (^texto). Com `--com`, uma segunda linha de marcas para comparar (ex.:
        palavras-whisper.json). É assim que se lê o ataque real à mão:
            ' ' < -50 dB (silêncio)  '.' -50..-40  ':' -40..-30  '|' -30..-22  '#' > -22
        Oclusiva (p, t, k) começa por um silêncio curto; fricativa (s, f, x) é '.' ou ':'
        antes da vogal; vogal tônica é '#'. Respiro antes da frase também é '.'/':' — não
        confunda com a palavra.

Por que existe: a fusão whisper + CTC (`alinhar_forcado.py`) foi validada contra 109
ataques lidos assim (mediana 0,02 s, máximo 0,15 s). Os limiares da fusão foram calibrados
NAQUELA voz; voz nova, ou a mesma em outra velocidade, pede nova leitura de pelo menos um
ataque por frase antes de confiar.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

import numpy as np

from _ffmpeg import carregar_audio

SR = 16000


def db(x: np.ndarray, hop: float) -> np.ndarray:
    jan = int(SR * hop)
    n = len(x) // jan
    return 20 * np.log10(np.sqrt((x[: n * jan].reshape(n, jan) ** 2).mean(axis=1)) + 1e-9)


def ascii_(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def ataques(x: np.ndarray) -> list[tuple[float, float]]:
    """(início da pausa, ataque) de cada pausa funda (< -52 dB, ≥ 60 ms abaixo de -45 dB)."""
    e = db(x, 0.01)
    ev, i = [], 0
    while i < len(e):
        if e[i] < -52:
            j = i
            while j < len(e) and e[j] < -45:
                j += 1
            if j - i >= 6 and j < len(e):
                ev.append((i * 0.01, j * 0.01))
            i = j + 1
        else:
            i += 1
    return ev


def pausas(P: list[dict], x: np.ndarray) -> list[dict]:
    """Casa cada ataque depois de pausa com a palavra mais perto; imprime e devolve a lista."""
    if not P:
        raise SystemExit("o palavras.json está vazio")
    saida = []
    for a, o in ataques(x):
        k = min(range(len(P)), key=lambda k: abs(P[k]["inicio"] - o))
        d = o - P[k]["inicio"]
        suspeito = abs(d) >= 0.06
        saida.append({"pausa": (a, o), "ataque": o, "indice": k, "texto": P[k]["texto"],
                      "inicio": P[k]["inicio"], "delta": d, "suspeito": suspeito})
        print(f"pausa {a:6.2f}-{o:6.2f}  ataque {o:6.2f}  -> {k:3d} {ascii_(P[k]['texto']):14s} "
              f"inicio {P[k]['inicio']:6.2f}  delta {d:+.2f}{'  <<<' if suspeito else ''}")
    n = sum(e["suspeito"] for e in saida)
    print(f"\n{len(saida)} ataques depois de pausa; {n} com |delta| >= 0,06 s (leia esses com `faixa`)")
    return saida


def faixa(P: list[dict], x: np.ndarray, faixas: list[str], outro: list[dict] | None) -> None:
    hop = 0.02
    e = db(x, hop)

    def marcas(L: list[dict], t0: float, n: int, rotulo: str) -> str:
        lab = [" "] * n
        for p in L:
            k = int(round((p["inicio"] - t0) / hop))
            if 0 <= k < n:
                for j, c in enumerate("^" + ascii_(p["texto"])):
                    if k + j < n and lab[k + j] == " ":
                        lab[k + j] = c
        return rotulo + " " + "".join(lab)

    for f in faixas:
        try:
            t0, t1 = (float(v.replace(",", ".")) for v in f.split("-"))
        except ValueError:
            raise SystemExit(f"faixa '{f}' inválida: use início-fim em segundos, ex.: 23.1-25.3") from None
        if t1 <= t0:
            raise SystemExit(f"faixa '{f}' inválida: o fim tem de vir depois do início")
        # round, não int: 2.3/0.02 dá 114.99999999999999 (medido; idem 4.1, 5.1), e int() punha o
        # envelope 20 ms fora da régua e das marcas
        a, b = int(round(t0 / hop)), int(round(t1 / hop))
        t0 = a * hop
        linha = "".join(" " if v < -50 else "." if v < -40 else ":" if v < -30 else "|" if v < -22 else "#" for v in e[a:b])
        regua = "".join(str(int(round((t0 + i * hop) * 10)) % 10) if i % 5 == 0 else "-" for i in range(b - a))
        print(f"{t0:.2f}..{t1:.2f}  (1 caractere = 20 ms; dígito = décimo de segundo)")
        print("  " + regua)
        print("  " + linha)
        print(marcas(P, t0, b - a, "A"))
        if outro:
            print(marcas(outro, t0, b - a, "B"))
        print()


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="conferir_alinhamento.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="modo", required=True)
    p1 = sub.add_parser("pausas", help="ataques depois de pausa contra as palavras")
    p1.add_argument("palavras", help="palavras.json da peça")
    p1.add_argument("audio", help="a narração final")
    p2 = sub.add_parser("faixa", help="envelope do áudio com as marcas das palavras")
    p2.add_argument("palavras", help="palavras.json da peça")
    p2.add_argument("audio", help="a narração final")
    p2.add_argument("faixas", nargs="+", help="trechos em segundos, ex.: 23.1-25.3")
    p2.add_argument("--com", metavar="OUTRO.json", help="segunda linha de marcas (ex.: palavras-whisper.json)")
    a = ap.parse_args(argv)
    P = json.loads(Path(a.palavras).read_text(encoding="utf-8"))
    x = carregar_audio(a.audio, SR)
    if a.modo == "pausas":
        pausas(P, x)
    else:
        outro = json.loads(Path(a.com).read_text(encoding="utf-8")) if a.com else None
        faixa(P, x, a.faixas, outro)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # SystemExit e avisos saem aqui
    main()
