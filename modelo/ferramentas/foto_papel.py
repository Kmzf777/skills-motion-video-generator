"""Foto real → cópia impressa com margem de papel e borda rasgada, registrada na biblioteca.

    python motion/ferramentas/foto_papel.py <foto> <nome> --tags a,b --origem real-verificada|real-nao-verificada|banco-livre
        [--categoria foto-real] [--fonte URL] [--largura 900] [--recorte x0,y0,x1,y1] [--dia AAAA-MM-DD] [--substituir]

Saída: três PNG `<nome>-b0/b1/b2` (bordas diferentes para o boil), todos do mesmo tamanho,
registrados em `motion/biblioteca/pecas/<categoria>/`. Depois:
`python motion/ferramentas/biblioteca.py publicar <NN-tema> <id>`.

De onde vem a foto:
  real-verificada      banco próprio da empresa, com prova (EXIF de câmera, autoria confirmada)
  real-nao-verificada  própria segundo a empresa, mas sem prova no arquivo
  banco-livre          Unsplash/Pexels baixado em resolução cheia; --fonte com a URL da página
                       da foto é obrigatória (licença e atribuição)
Foto de terceiro (Pinterest, Google, perfil de concorrente) NUNCA entra aqui: é referência,
vira descritor em texto, não pixel do vídeo. Rosto de pessoa real só de foto real com
autorização — nunca sintetizado.

A rotação do EXIF é aplicada antes de tudo: foto de celular gravada deitada com
`Orientation = 6` exibe em pé, e é a de exibição que vale. `--recorte` é em frações (0 a 1)
da largura e da altura JÁ giradas, ex.: 0,0.1,1,0.8 tira 10% de cima e 20% de baixo.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

import biblioteca as B
from recortar_folha import PAPEL, reticula, rng, ruido_suave

ORIGENS_FOTO = ("real-verificada", "real-nao-verificada", "banco-livre")


def foto_rasgada(arquivo: Path, nome: str, larg: int, recorte: tuple[float, float, float, float] | None = None,
                 margem: int = 18, com_reticula: bool = False, destino: Path | None = None) -> list[Path]:
    """Foto real como cópia impressa: retângulo com margem de papel e borda rasgada. Devolve os 3 PNG."""
    destino = Path(destino or ".")
    im = ImageOps.exif_transpose(Image.open(arquivo)).convert("RGB")
    if recorte:
        W, H = im.size
        x0, y0, x1, y1 = recorte
        im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    if im.width < larg:
        print(f"aviso: {Path(arquivo).name} tem {im.width} px de largura (no recorte); ampliar para {larg} "
              "vai amolecer a foto", file=sys.stderr)
    im = im.resize((larg, max(1, int(im.height * larg / im.width))), Image.LANCZOS)
    rgb = np.array(im).astype(np.float32)
    if com_reticula:
        rgb = reticula(rgb.astype(np.uint8), celula=6, satur=0.85, forca=0.4)
    h, w = rgb.shape[:2]
    destino.mkdir(parents=True, exist_ok=True)
    arqs = []
    for b in range(3):
        r = rng(f"{nome}#{b}")
        H2, W2 = h + 2 * margem, w + 2 * margem
        tela = np.tile(PAPEL, (H2, W2, 1))
        tela[margem:margem + h, margem:margem + w] = rgb
        yy, xx = np.mgrid[0:H2, 0:W2]
        dist = np.minimum.reduce([xx, yy, W2 - 1 - xx, H2 - 1 - yy]).astype(np.float32)
        rasgo = 5 + 4 * ruido_suave((H2, W2), 40, r) + 2.5 * ruido_suave((H2, W2), 4, r)
        a = np.clip(dist - rasgo, 0, 1)
        rgba = np.dstack([tela, a * 255]).astype(np.uint8)
        arq = destino / f"{nome}-b{b}.png"
        Image.fromarray(rgba, "RGBA").save(arq, optimize=True)
        arqs.append(arq)
    print(f"{nome:20s} {w + 2 * margem}x{h + 2 * margem} (foto)")
    return arqs


def _recorte(v: str | None) -> tuple[float, float, float, float] | None:
    if not v:
        return None
    try:
        x0, y0, x1, y1 = (float(p) for p in v.split(","))
    except ValueError:
        raise SystemExit(f"--recorte '{v}' inválido: quatro frações x0,y0,x1,y1, ex.: 0,0.1,1,0.8") from None
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise SystemExit(f"--recorte '{v}' fora de 0..1 ou invertido (precisa x0 < x1 e y0 < y1)")
    return x0, y0, x1, y1


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="foto_papel.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("foto", help="a foto real (JPG/PNG)")
    ap.add_argument("nome", help="minúsculas sem acento e hífen, ex.: foto-fachada")
    ap.add_argument("--categoria", default="foto-real", help="padrão foto-real")
    ap.add_argument("--tags", required=True, help="separadas por vírgula")
    ap.add_argument("--origem", required=True, choices=ORIGENS_FOTO)
    ap.add_argument("--fonte", help="URL da página da foto (obrigatória para banco-livre)")
    ap.add_argument("--largura", type=int, default=900, help="largura da foto impressa em px (padrão 900)")
    ap.add_argument("--recorte", help="x0,y0,x1,y1 em frações da foto já girada pelo EXIF")
    ap.add_argument("--dia", help="AAAA-MM-DD do id (padrão: hoje)")
    ap.add_argument("--substituir", action="store_true", help="refaz a mesma peça com o mesmo id")
    a = ap.parse_args(argv)

    foto = Path(a.foto)
    if not foto.is_file():
        raise SystemExit(f"foto não encontrada: {foto}")
    if a.largura < 50:
        raise SystemExit("--largura muito pequena")
    recorte = _recorte(a.recorte)
    dia = a.dia or date.today().isoformat()
    ident = B.validar_registro(a.nome, a.categoria, a.origem, None, a.fonte, dia, a.substituir)
    tags = [t for t in a.tags.split(",") if t.strip()]
    if not tags:
        raise SystemExit("dê ao menos uma tag (--tags): é por elas que a próxima peça acha esta")
    B.conferir_bruto(foto, dia, a.substituir)  # recusa antes de gerar qualquer arquivo
    with tempfile.TemporaryDirectory() as tmp:
        arqs = foto_rasgada(foto, a.nome, a.largura, recorte=recorte, destino=Path(tmp))
        # o original vai para brutos/ (bytes intactos): o índice versionado não guarda caminho de fora
        bruto = B.guardar_bruto(foto, dia, a.substituir)
        B.registrar(a.nome, a.categoria, arqs, tags, a.origem, bruto=bruto,
                    fonte=a.fonte, dia=dia, nota="foto real impressa com borda rasgada", substituir=a.substituir)
    print(f"registrado {ident}. Publique: python motion/ferramentas/biblioteca.py publicar <NN-tema> {ident}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # SystemExit e avisos saem aqui
    main()
