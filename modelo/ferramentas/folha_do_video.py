"""Folha de contato tirada do MP4 FINAL, por número de quadro.

    python motion/ferramentas/folha_do_video.py <video.mp4> <saida.png> <q1,q2,...> [colunas]

O `contato.mjs` do motor renderiza stills pelo Remotion — serve antes do render. Esta folha
lê o arquivo que vai ao ar, depois do encode: é a que prova o chicote (pegue dois quadros
DENTRO de cada janela, q-2 e q+1 da troca) e que a normalização do áudio não mexeu no
vídeo. Cada célula leva o quadro e o segundo escritos em cima. Colunas: 10 por padrão.

A taxa de quadros sai do próprio vídeo (ffprobe). O seek mira meio quadro ANTES do quadro
pedido: com `-ss` antes do `-i`, o ffmpeg descarta todo quadro cujo pts é menor que o alvo e
entrega o primeiro que sobra. Medido (07/10/2026, MP4 do Remotion a 30 fps): mirar o MEIO do
quadro, (q+0,5)/fps, entregava o quadro q+1 com o rótulo de q, e o último quadro saía vazio;
mirar (q−0,5)/fps entrega exatamente q, com meio quadro de folga para os dois lados.

Quadro inexistente é recusado ANTES de extrair, contado pelo `nb_frames` do fluxo de vídeo
— não pela duração do contêiner, que é a do áudio quando ele é mais longo (no reel de
origem: contêiner 79,1 s, vídeo 2370 quadros = 79,000 s).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

from _ffmpeg import ffmpeg, sondar_video

W = 216  # largura de cada célula; a altura segue a proporção do vídeo


def instante(q: int, fps: float) -> float:
    """Alvo do seek que entrega exatamente o quadro q (ver a nota no topo)."""
    return max(0.0, (q - 0.5) / fps)


def folha(video: str, saida: str, quadros: list[int], cols: int = 10) -> str:
    info = sondar_video(video)
    fps, total = info["fps"], info["quadros"]  # quadros do FLUXO de vídeo, não do contêiner
    h = max(1, round(W * info["altura"] / info["largura"]))
    fora = [q for q in quadros if q < 0 or (total is not None and q >= total)]
    if fora:
        faixa = f"0 a {total - 1}" if total else "nenhum"
        raise SystemExit(f"quadro(s) {fora} não existem em {video}: o vídeo tem {total} quadros ({faixa}) a {fps:g} fps"
                         + (f"; o contêiner dura {info['duracao_formato']:.3f} s porque o áudio é mais longo"
                            if info.get("duracao_formato") and info["duracao_formato"] > info["duracao"] + 1 / fps else ""))
    imgs = []
    with tempfile.TemporaryDirectory() as d:
        for q in quadros:
            out = os.path.join(d, f"{q}.png")
            r = subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{instante(q, fps):.6f}", "-i", video,
                                "-frames:v", "1", "-vf", f"scale={W}:{h}", out],
                               capture_output=True, text=True, errors="replace")
            if r.returncode != 0 or not os.path.exists(out):
                raise SystemExit(f"o ffmpeg não extraiu o quadro {q}: {r.stderr.strip()}")
            with Image.open(out) as im:
                imgs.append((q, im.convert("RGB")))
    linhas = (len(imgs) + cols - 1) // cols
    tela = Image.new("RGB", (min(cols, len(imgs)) * (W + 4), linhas * (h + 22)), (30, 30, 30))
    desenho = ImageDraw.Draw(tela)
    for k, (q, im) in enumerate(imgs):
        x, y = (k % cols) * (W + 4), (k // cols) * (h + 22)
        tela.paste(im, (x, y + 20))
        desenho.text((x + 4, y + 4), f"q{q}  {q / fps:.2f}s", fill=(255, 255, 255))
    tela.save(saida)
    print(saida)
    return saida


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="folha_do_video.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", help="o MP4 final")
    ap.add_argument("saida", help="PNG da folha")
    ap.add_argument("quadros", help="números de quadro separados por vírgula, ex.: 169,172,410,413")
    ap.add_argument("colunas", nargs="?", type=int, default=10, help="colunas da folha (padrão 10)")
    a = ap.parse_args(argv)
    try:
        quadros = [int(q) for q in a.quadros.split(",") if q.strip()]
    except ValueError:
        raise SystemExit(f"quadros inválidos: '{a.quadros}' (números inteiros separados por vírgula)") from None
    if not quadros or a.colunas < 1:
        raise SystemExit("dê ao menos um quadro e colunas >= 1")
    folha(a.video, a.saida, quadros, a.colunas)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # SystemExit e avisos saem aqui
    main()
