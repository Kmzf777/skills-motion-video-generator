"""Varre um MP4 renderizado procurando salto de movimento que ninguém pediu.

    python motion/ferramentas/varrer_movimento.py <video.mp4> [q1,q2,...]

Extrai os quadros em baixa resolução (cinza, 135 px de largura) e mede, quadro a quadro:
  - MAD: diferença média absoluta para o quadro anterior (conteúdo que muda de uma vez);
  - deslocamento global por correlação de fase (a câmera que pula), em pixel do quadro cheio.
Lista o que acontece LONGE (> 7 quadros) das trocas conhecidas — chicotes, coberturas,
batidas com tremor — que se passam como segundo argumento (números de quadro).

Como ler: movimento rápido intencional (foco num detalhe, panorâmica, mergulho num selo)
aparece como sequência de picos de MAD; isso é esperado. O que importa é a segunda lista,
"saltos de câmera isolados": a câmera andou muito num quadro e os vizinhos ficaram parados.
Ela tem de sair vazia.

A taxa de quadros e a largura saem do próprio vídeo (ffprobe, honrando a rotação); nada é
suposto. Usa o ffmpeg do Remotion (`_ffmpeg.py`).
"""

from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

from _ffmpeg import ffmpeg, sondar_video

LARGURA = 135  # px dos quadros analisados


def desloc(a: np.ndarray, b: np.ndarray, fator: float = 1.0) -> tuple[int, int]:
    """Deslocamento (dx, dy) que leva `b` (quadro anterior) a `a` (atual), em px vezes `fator`."""
    A = np.fft.fft2(a - a.mean())
    B = np.fft.fft2(b - b.mean())
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-9
    r = np.fft.ifft2(R).real
    y, x = np.unravel_index(np.argmax(r), r.shape)
    if y > a.shape[0] // 2:
        y -= a.shape[0]
    if x > a.shape[1] // 2:
        x -= a.shape[1]
    return int(round(x * fator)), int(round(y * fator))


def varrer(video: str, conhecidos: list[int]) -> dict:
    info = sondar_video(video)
    fps, fator = info["fps"], info["largura"] / LARGURA
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run([ffmpeg(), "-v", "error", "-i", video, "-vf", f"scale={LARGURA}:-2",
                            os.path.join(d, "q%05d.png")], capture_output=True, text=True, errors="replace")
        if r.returncode != 0:
            raise SystemExit(f"o ffmpeg não extraiu os quadros de {video}: {r.stderr.strip()}")
        Q = [np.asarray(Image.open(a).convert("L"), dtype=np.float32) for a in sorted(glob.glob(os.path.join(d, "*.png")))]
    if len(Q) < 3:
        raise SystemExit(f"{video}: só {len(Q)} quadro(s), pouco para varrer")
    print(f"{len(Q)} quadros a {fps:g} fps ({info['largura']}x{info['altura']})")
    mad = np.array([np.abs(Q[k] - Q[k - 1]).mean() for k in range(1, len(Q))])
    dv = np.array([desloc(Q[k], Q[k - 1], fator) for k in range(1, len(Q))], dtype=float)

    def perto(q: int) -> bool:
        return any(abs(q - c) <= 7 for c in conhecidos)

    med = float(np.median(mad))
    print(f"MAD mediana {med:.2f} · p95 {np.percentile(mad, 95):.2f} · máx {mad.max():.2f}")
    print("picos de MAD longe das trocas conhecidas (quadro, s, MAD) — movimento rápido intencional também cai aqui:")
    picos = []
    for k in range(len(mad)):
        if mad[k] > max(6 * med, 4.0) and not perto(k + 1):
            picos.append(k + 1)
            print(f"  q{k + 1:5d}  {(k + 1) / fps:6.2f}s  {mad[k]:6.2f}")
    print("saltos de câmera isolados (quadro, s, dx, dy) — aqui tem que sair vazio:")
    saltos = []
    escala = fator / 8  # os limiares foram medidos em px de um quadro de 1080 de largura
    for k in range(1, len(dv) - 1):
        m = np.hypot(*dv[k])
        viz = max(np.hypot(*dv[k - 1]), np.hypot(*dv[k + 1]))
        if m >= 40 * escala and m > 3 * (viz + 8 * escala) and not perto(k + 1):
            saltos.append(k + 1)
            print(f"  q{k + 1:5d}  {(k + 1) / fps:6.2f}s  dx {dv[k][0]:+.0f} dy {dv[k][1]:+.0f}  (vizinhos {viz:.0f})")
    print(f"  {len(saltos)} salto(s)")
    return {"quadros": len(Q), "fps": fps, "picos": picos, "saltos": saltos}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="varrer_movimento.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", help="o MP4 renderizado")
    ap.add_argument("conhecidos", nargs="?", default="",
                    help="quadros das trocas intencionais separados por vírgula, ex.: 171,412,690")
    a = ap.parse_args(argv)
    try:
        conhecidos = [int(q) for q in a.conhecidos.split(",") if q.strip()]
    except ValueError:
        raise SystemExit(f"quadros conhecidos inválidos: '{a.conhecidos}' (números inteiros separados por vírgula)") from None
    varrer(a.video, conhecidos)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # SystemExit e avisos saem aqui
    main()
