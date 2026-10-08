"""Efeitos sonoros de colagem e a trilha em seções cravadas nas FRASES da narração.

    python motion/ferramentas/sons.py motion/pecas/<NN-tema>

Lê `sons.json` e `palavras.json` da peça e grava `public/sfx/*.wav` (44,1 kHz, mono, 16
bits): um arquivo por efeito — o motor põe UM em cada entrada de colagem (pop no texto,
papel no recorte, caneta no traço, carimbo no Dymo) — e a `trilha.wav`.

Tudo sintetizado aqui, com semente fixa por efeito: rodar de novo dá os mesmos bytes. Não
entra trilha licenciada, e som de papel, carimbo e caneta é exatamente o que síntese
simples resolve bem. Filtros por máscara de FFT (sem scipy).

`sons.json`:

    {"bpm": 88, "secoes": [
      {"frase": "Calma", "tipo": "groove"},
      {"frase": "E aqui vem", "tipo": "respiro"},
      {"frase": "Por isso a gente", "tipo": "groove"},
      {"frase": "Salva esse vídeo", "tipo": "fecho"}
    ]}

Cada seção começa no início da `frase` na narração, procurada em `palavras.json` sem
acento nem pontuação e DEPOIS da seção anterior (as seções seguem a ordem da fala). Nenhum
segundo é digitado: quando a narração é realinhada, a trilha anda junto.

    antes da 1ª seção  tensão: a trilha fica muda (drone.wav e batimento.wav fazem a tensão)
    groove             Rhodes em Dmaj7 · Bm7 · Gmaj7 · A7, baixo e bateria lo-fi com swing leve
    respiro            os mesmos acordes abafados, sem bateria
    fecho              acordes sem bateria e fade até o fim; só pode ser a última seção

A troca de seção cai na barra de compasso (a primeira que começa depois da frase). A
trilha dura DUR = fim da última palavra + 0,5 s, arredondado para cima ao décimo — a mesma
regra do FIM do roteiro no motor. O `drone.wav` dura até a primeira seção + 0,6 s (com fade
nesses 0,6 s), para cobrir a tensão inteira.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
import wave
from pathlib import Path

import numpy as np

SR = 44100
TIPOS = ("groove", "respiro", "fecho")
EFEITOS_PADRAO = ("thump", "tick", "tink", "rasgo", "slide", "pop", "carimbo", "ding", "whoosh", "vento",
                  "nota1", "nota2", "nota3", "nota4", "batimento", "rabisco", "fita", "digitacao", "golinho",
                  "graos", "brilho", "chicote", "drone")


def _rng(nome: str) -> np.random.Generator:
    return np.random.default_rng(int(hashlib.sha256(f"sons#{nome}".encode()).hexdigest()[:8], 16))


def t(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def ruido(dur: float, r: np.random.Generator) -> np.ndarray:
    return r.standard_normal(int(dur * SR))


def banda(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Passa-banda por máscara suave na FFT."""
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    m = 1 / (1 + (lo / np.maximum(fr, 1)) ** 4) * 1 / (1 + (fr / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def env(dur: float, ataque: float, decai: float) -> np.ndarray:
    tt = t(dur)
    a = np.clip(tt / max(ataque, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(tt - ataque, 0) / decai)


def norm(x: np.ndarray, pico: float = 0.8) -> np.ndarray:
    return x / (np.max(np.abs(x)) + 1e-9) * pico


# ------------------------------------------------------------------ efeitos

def thump() -> np.ndarray:
    """Baque grave: impacto, carimbo forte."""
    r = _rng("thump")
    tt = t(0.45)
    f = 70 * np.exp(-tt * 6) + 38
    corpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.45, 0.003, 0.12)
    clique = banda(ruido(0.45, r), 800, 4000) * env(0.45, 0.001, 0.008) * 0.3
    return norm(corpo + clique, 0.9)


def tick() -> np.ndarray:
    r = _rng("tick")
    return norm(banda(ruido(0.05, r), 1800, 6000) * env(0.05, 0.0005, 0.006), 0.5)


def tink() -> np.ndarray:
    """Toque metálico de louça."""
    tt = t(1.4)
    parc = [(2210, 1.0, 0.45), (3470, 0.5, 0.3), (5130, 0.3, 0.18), (7020, 0.15, 0.1)]
    s = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) for f, a, d in parc)
    return norm(s * np.clip(tt / 0.002, 0, 1), 0.55)


def rasgo() -> np.ndarray:
    """Papel rasgando."""
    r = _rng("rasgo")
    dur = 0.55
    n = ruido(dur, r)
    estalos = (r.random(len(n)) < 0.012).astype(float) * r.standard_normal(len(n)) * 6
    s = banda(n + estalos, 1200, 9000)
    e = np.interp(t(dur), [0, 0.04, 0.4, dur], [0, 1, 0.7, 0])
    return norm(s * e, 0.6)


def slide() -> np.ndarray:
    """Papel deslizando sobre papel."""
    r = _rng("slide")
    dur = 0.32
    e = np.interp(t(dur), [0, 0.12, dur], [0, 1, 0])
    return norm(banda(ruido(dur, r), 900, 5000) * e, 0.35)


def pop() -> np.ndarray:
    """Estalo curto: letra ou texto que entra."""
    tt = t(0.09)
    f = 520 * np.exp(-tt * 30) + 180
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.09, 0.001, 0.025), 0.5)


def carimbo() -> np.ndarray:
    r = _rng("carimbo")
    tt = t(0.3)
    corpo = np.sin(2 * np.pi * 95 * tt) * env(0.3, 0.001, 0.05)
    madeira = banda(ruido(0.3, r), 300, 2500) * env(0.3, 0.0005, 0.02)
    return norm(corpo * 0.8 + madeira, 0.95)


def ding() -> np.ndarray:
    tt = t(1.8)
    s = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d)
            for f, a, d in [(1318.5, 1, 0.9), (2637, 0.35, 0.5), (3955, 0.15, 0.3)])
    return norm(s * np.clip(tt / 0.003, 0, 1), 0.5)


def whoosh() -> np.ndarray:
    r = _rng("whoosh")
    dur = 0.7
    n = ruido(dur, r)
    out = np.zeros_like(n)
    blocos = 14
    tam = len(n) // blocos
    for i in range(blocos):
        c = 3000 * (1 - i / blocos) + 400
        out[i * tam:(i + 1) * tam] = banda(n, c * 0.5, c * 1.5)[i * tam:(i + 1) * tam]
    e = np.interp(t(dur), [0, 0.3, dur], [0, 1, 0])
    return norm(out * e, 0.45)


def vento() -> np.ndarray:
    r = _rng("vento")
    dur = 7.2
    s = banda(ruido(dur, r), 150, 900)
    mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t(dur))
    e = np.interp(t(dur), [0, 1.2, dur - 1.5, dur], [0, 1, 1, 0])
    return norm(s * mod * e, 0.25)


def nota(freq: float) -> np.ndarray:
    tt = t(0.7)
    s = np.sin(2 * np.pi * freq * tt) + 0.25 * np.sin(2 * np.pi * freq * 4 * tt) * np.exp(-tt / 0.05)
    return norm(s * env(0.7, 0.002, 0.22), 0.45)


def batimento() -> np.ndarray:
    """Coração: dois baques abafados (tensão)."""
    k = thump()[: int(0.32 * SR)]
    out = np.zeros(int(0.75 * SR))
    out[: len(k)] += k * 0.9
    i = int(0.22 * SR)
    out[i: i + len(k)] += k * 0.6
    return norm(banda(out, 25, 400), 0.85)


def rabisco() -> np.ndarray:
    """Caneta riscando: traço, círculo, sublinhado."""
    r = _rng("rabisco")
    d = 0.38
    n = banda(ruido(d, r), 1500, 7000)
    zig = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 11 * t(d)))
    return norm(n * zig * env(d, 0.01, 0.2), 0.35)


def fita() -> np.ndarray:
    """Fita adesiva puxada."""
    r = _rng("fita")
    d = 0.32
    n = ruido(d, r)
    estalos = (r.random(len(n)) < 0.02) * r.standard_normal(len(n)) * 5
    e = np.interp(t(d), [0, 0.02, 0.25, d], [0, 1, 0.6, 0])
    return norm(banda(n + estalos, 2000, 11000) * e, 0.45)


def digitacao(n: int = 9, intervalo: float = 1 / 30) -> np.ndarray:
    """Teclas de máquina de etiqueta (o Dymo datilografa 1 letra por quadro)."""
    r = _rng("digitacao")
    out = np.zeros(int((n * intervalo + 0.2) * SR))
    for k in range(n):
        c = banda(ruido(0.03, r), 1800, 8000) * env(0.03, 0.0005, 0.006)
        corpo = np.sin(2 * np.pi * (180 + r.random() * 60) * t(0.03)) * env(0.03, 0.0005, 0.01) * 0.5
        i = int(k * intervalo * SR * (1 + (r.random() - 0.5) * 0.2))
        out[i: i + len(c)] += c + corpo
    return norm(out, 0.4)


def golinho() -> np.ndarray:
    """Gole de líquido."""
    r = _rng("golinho")
    d = 0.6
    n = ruido(d, r)
    out = np.zeros_like(n)
    blocos = 12
    tam = len(n) // blocos
    for i in range(blocos):
        c = 600 + 2200 * (i / blocos)
        out[i * tam:(i + 1) * tam] = banda(n, c * 0.6, c * 1.4)[i * tam:(i + 1) * tam]
    turb = 0.6 + 0.4 * np.sin(2 * np.pi * 23 * t(d)) ** 2
    e = np.interp(t(d), [0, 0.05, 0.45, d], [0, 1, 0.8, 0])
    return norm(out * turb * e, 0.4)


def graos(n: int = 26, dur: float = 0.7) -> np.ndarray:
    """Grãos miúdos caindo (sementes, contas, cascalho fino)."""
    r = _rng("graos")
    out = np.zeros(int((dur + 0.1) * SR))
    for _ in range(n):
        i = int(r.random() ** 1.6 * dur * SR)
        f = 1800 + r.random() * 3500
        c = np.sin(2 * np.pi * f * t(0.02)) * env(0.02, 0.0003, 0.004) * (0.3 + r.random() * 0.7)
        out[i: i + len(c)] += c
    return norm(out, 0.5)


def brilho() -> np.ndarray:
    """Cintilar: revelação, número que importa."""
    r = _rng("brilho")
    d = 0.7
    tt = t(d)
    s = np.zeros_like(tt)
    for k, f in enumerate([2349, 2793, 3136, 3729, 4699]):
        a0 = k * 0.05
        e = np.clip((tt - a0) / 0.005, 0, 1) * np.exp(-np.maximum(tt - a0, 0) / 0.18)
        s += np.sin(2 * np.pi * f * tt) * e * 0.4
    return norm(s + banda(ruido(d, r), 6000, 14000) * env(d, 0.01, 0.15) * 0.15, 0.32)


def chicote() -> np.ndarray:
    """O miolo do whoosh: soa 0,16 s antes da troca de cena em chicote."""
    w = whoosh()
    k = int(0.36 * SR)
    return norm(w[len(w) // 2 - k // 2: len(w) // 2 + k // 2] * np.hanning(k), 0.6)


def drone(d: float = 6.3) -> np.ndarray:
    """Zumbido grave da tensão do gancho; some nos últimos 0,6 s."""
    r = _rng("drone")
    tt = t(d)
    s = sum(np.sin(2 * np.pi * f * tt + r.random() * 6) * a for f, a in [(41.2, 1), (55, 0.6), (61.7, 0.35), (82.4, 0.25)])
    ronco = banda(ruido(d, r), 30, 220) * 0.5
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * 0.35 * tt)
    e = np.interp(tt, [0, min(0.8, d - 0.6), d - 0.6, d], [0.35, 1, 1, 0])
    return norm((s + ronco) * trem * e, 0.75)


def efeitos(tensao: float) -> dict[str, np.ndarray]:
    """Todos os efeitos padrão; `tensao` = início da primeira seção (fim do gancho), em s."""
    d = max(math.ceil((tensao + 0.6) * 10) / 10, 1.4)
    fns = {"thump": thump, "tick": tick, "tink": tink, "rasgo": rasgo, "slide": slide, "pop": pop,
           "carimbo": carimbo, "ding": ding, "whoosh": whoosh, "vento": vento,
           "nota1": lambda: nota(587.33), "nota2": lambda: nota(739.99), "nota3": lambda: nota(880.0),
           "nota4": lambda: nota(1174.66), "batimento": batimento, "rabisco": rabisco, "fita": fita,
           "digitacao": digitacao, "golinho": golinho, "graos": graos, "brilho": brilho, "chicote": chicote,
           "drone": lambda: drone(d)}
    assert tuple(fns) == EFEITOS_PADRAO
    return {nome: fn() for nome, fn in fns.items()}


# ------------------------------------------------------------------ trilha

NOTAS = {"D3": 146.83, "F#3": 185.0, "A3": 220.0, "C#4": 277.18, "B2": 123.47, "D4": 293.66, "F#4": 369.99,
         "G2": 98.0, "B3": 246.94, "A2": 110.0, "E3": 164.81, "G3": 196.0, "C#3": 138.59, "E4": 329.63}
ACORDES = [  # Dmaj7 · Bm7 · Gmaj7 · A7 — um compasso cada
    ("D2", ["D3", "F#3", "A3", "C#4"]), ("B1", ["B2", "D3", "F#3", "A3"]),
    ("G1", ["G2", "B2", "D3", "F#3"]), ("A1", ["A2", "C#3", "E3", "G3"]),
]
BAIXO = {"D2": 73.42, "B1": 61.74, "G1": 49.0, "A1": 55.0}


def rhodes(f: float, d: float) -> np.ndarray:
    tt = t(d)
    s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / 0.4)
         + 0.12 * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt / 0.2))
    trem = 1 - 0.18 * (0.5 + 0.5 * np.sin(2 * np.pi * 4.2 * tt))
    return s * trem * np.exp(-tt / 2.2) * np.clip(tt / 0.006, 0, 1)


def chave(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())


def duracao(palavras: list[dict]) -> float:
    """DUR: fim da última palavra + 0,5 s, para cima ao décimo (a regra do FIM do roteiro)."""
    return math.ceil((palavras[-1]["fim"] + 0.5) * 10) / 10


def inicios_das_secoes(palavras: list[dict], secoes: list[dict]) -> list[float]:
    """Início (s) de cada seção: a primeira ocorrência da frase DEPOIS da seção anterior."""
    chaves = [chave(p["texto"]) for p in palavras]
    inicios: list[float] = []
    desde, anterior = 0, None
    for s in secoes:
        alvo = [c for c in (chave(w) for w in s["frase"].split()) if c]
        if not alvo:
            raise SystemExit(f"seção sem palavras na frase: {s}")
        ultimo = len(chaves) - len(alvo)
        achou = next((i for i in range(desde, ultimo + 1) if chaves[i:i + len(alvo)] == alvo), None)
        if achou is None:
            antes = any(chaves[i:i + len(alvo)] == alvo for i in range(0, min(desde, ultimo + 1)))
            if antes:
                raise SystemExit(f'a frase "{s["frase"]}" só aparece antes da seção "{anterior}": '
                                 "as seções do sons.json seguem a ordem da fala")
            raise SystemExit(f'a frase "{s["frase"]}" não está no palavras.json da peça '
                             "(a busca ignora acento e pontuação; confira as palavras)")
        inicios.append(float(palavras[achou]["inicio"]))
        desde, anterior = achou + 1, s["frase"]
    return inicios


def trilha(palavras: list[dict], bpm: float, secoes: list[dict], inicios: list[float]) -> np.ndarray:
    dur_total = duracao(palavras)
    n = int(dur_total * SR)
    r = _rng("trilha")
    mus = np.zeros(n)
    bat = np.zeros(n)
    batida = 60 / bpm
    compasso = 4 * batida
    ini = inicios[0]
    tem_fecho = secoes[-1]["tipo"] == "fecho"
    fim = inicios[-1] if tem_fecho else dur_total  # a bateria para e o fade começa aqui
    bumbo = thump()[: int(0.25 * SR)] * 0.55

    def tipo_em(tc: float) -> str:
        return secoes[max(k for k, s0 in enumerate(inicios) if s0 <= tc)]["tipo"]

    k, tc = 0, ini
    while tc < (fim + compasso if tem_fecho else dur_total):
        raiz, notas = ACORDES[k % 4]
        dur = compasso + 0.4
        i = int(tc * SR)
        bloco = sum(rhodes(NOTAS[x], dur) for x in notas) * 0.16
        bx = np.sin(2 * np.pi * BAIXO[raiz] * t(dur)) * np.exp(-t(dur) / 1.6) * 0.5
        seg = (bloco + bx)[: max(0, n - i)]
        tipo = tipo_em(tc)
        if tipo == "respiro":
            seg = banda(seg, 40, 700) * 0.8
        mus[i: i + len(seg)] += seg
        if tipo == "groove":
            for b in range(4):
                tb = tc + b * batida
                ib = int(tb * SR)
                if b in (0, 2):
                    bat[ib: ib + len(bumbo)] += bumbo[: max(0, n - ib)]
                if b in (1, 3):
                    sn = banda(ruido(0.18, r), 900, 6000) * env(0.18, 0.001, 0.05) * 0.35
                    bat[ib: ib + len(sn)] += sn[: max(0, n - ib)]
                for h in range(2):
                    ih = int((tb + h * batida / 2 + (0.03 if h else 0)) * SR)  # swing leve
                    hh = banda(ruido(0.04, r), 7000, 14000) * env(0.04, 0.0005, 0.01) * 0.12
                    bat[ih: ih + len(hh)] += hh[: max(0, n - ih)]
        tc += compasso
        k += 1
    vinil = banda(ruido(dur_total, r), 1000, 6000)[:n] * 0.012 + (r.random(n) < 0.0004) * r.standard_normal(n) * 0.15
    out = mus + bat + vinil
    tt = np.arange(n) / SR
    entra = np.clip((tt - (ini - 0.02)) / 0.02, 0, 1)  # muda na tensão, entra na 1ª seção
    if tem_fecho:
        sai = np.where(tt < fim, 1.0, np.clip((dur_total - tt) / max(dur_total - fim, 1e-3), 0, 1))
    else:
        sai = np.clip((dur_total - tt) / 0.5, 0, 1)
    return norm(out * entra * sai, 0.7)


# ------------------------------------------------------------------ peça

def salvar(destino: Path, nome: str, x: np.ndarray) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    arq = destino / f"{nome}.wav"
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(arq), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return arq


def ler_peca(peca: Path) -> tuple[list[dict], float, list[dict]]:
    """Lê e confere `palavras.json` e `sons.json` da peça."""
    if not peca.is_dir():
        raise SystemExit(f"a pasta da peça não existe: {peca}")
    arq_p, arq_s = peca / "palavras.json", peca / "sons.json"
    if not arq_p.is_file():
        raise SystemExit(f"{arq_p.as_posix()} não existe: alinhe a narração antes (alinhar_forcado.py)")
    palavras = json.loads(arq_p.read_text(encoding="utf-8"))
    if not palavras or not all("texto" in p and "inicio" in p and "fim" in p for p in palavras):
        raise SystemExit(f"{arq_p.as_posix()} vazio ou sem texto/inicio/fim")
    if not arq_s.is_file():
        raise SystemExit(f"{arq_s.as_posix()} não existe: crie com o bpm e as seções (veja --help)")
    j = json.loads(arq_s.read_text(encoding="utf-8"))
    bpm = j.get("bpm", 88)
    if not isinstance(bpm, (int, float)) or not 40 <= bpm <= 200:
        raise SystemExit(f"bpm {bpm!r} inválido no sons.json (entre 40 e 200)")
    secoes = j.get("secoes")
    if not isinstance(secoes, list) or not secoes:
        raise SystemExit("sons.json precisa de \"secoes\": lista com {frase, tipo}")
    for k, s in enumerate(secoes):
        if not isinstance(s, dict) or not isinstance(s.get("frase"), str) or not s["frase"].strip():
            raise SystemExit(f"seção {k} sem frase: {s}")
        if s.get("tipo") not in TIPOS:
            raise SystemExit(f'seção "{s["frase"]}": tipo {s.get("tipo")!r} não existe; use {list(TIPOS)} '
                             "(a tensão é automática antes da primeira seção)")
        if s["tipo"] == "fecho" and k != len(secoes) - 1:
            raise SystemExit(f'seção "{s["frase"]}": fecho só pode ser a última seção')
    return palavras, float(bpm), secoes


def gerar(peca: Path) -> dict[str, Path]:
    peca = Path(peca)
    palavras, bpm, secoes = ler_peca(peca)
    inicios = inicios_das_secoes(palavras, secoes)  # recusa antes de gravar qualquer arquivo
    destino = peca / "public" / "sfx"
    gravados = {}
    for nome, x in efeitos(inicios[0]).items():
        gravados[nome] = salvar(destino, nome, x)
    gravados["trilha"] = salvar(destino, "trilha", trilha(palavras, bpm, secoes, inicios))
    dur_total = duracao(palavras)
    print(f"{len(gravados)} arquivos em {destino.as_posix()}/ · trilha {dur_total:.1f} s a {bpm:g} BPM")
    marcos = [("tensao", 0.0)] + [(s["tipo"], s0) for s, s0 in zip(secoes, inicios)]
    for (tipo, s0), (_, s1) in zip(marcos, marcos[1:] + [("", dur_total)]):
        print(f"  {tipo:8s} {s0:6.2f} -> {s1:6.2f} s")
    return gravados


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="sons.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("peca", help="pasta da peça, ex.: motion/pecas/03-tema (com sons.json e palavras.json)")
    a = ap.parse_args(argv)
    gerar(Path(a.peca))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # SystemExit e avisos saem aqui
    main()
