"""Folha de objetos sobre branco → peças de colagem com filete de papel e 3 bordas (boil).

    python motion/ferramentas/recortar_folha.py <folha.png> --nomes a,b,c --categoria C --tags t1,t2 --prompt "..."
        [--limiar 22] [--juntar 24] [--area-min 2500] [--convexo a,b] [--lente a] [--filete 9]
        [--reticula] [--dia AAAA-MM-DD] [--substituir] [--origem gerado-chatgpt]

`--origem` é gerado-chatgpt por padrão (e então o --prompt é obrigatório). Foto REAL de um
produto sobre fundo branco também se recorta aqui, com `--origem real-verificada`: produto
da marca entra só como pixel real, nunca gerado (a biblioteca recusa categoria `produto`
com origem gerado-chatgpt).

Entrada: a folha gerada no ChatGPT com os objetos AFASTADOS sobre branco liso #FFFFFF
(sem texto, sem embalagem, sem rosto). Saída: para cada objeto, três PNG `<nome>-b0/b1/b2`
com o objeto e um filete de papel de borda irregular, um por variante do "boil" de
stop-motion que o motor alterna a cada 3 quadros; a folha original vai para
`motion/biblioteca/brutos/` e cada peça é registrada na biblioteca com o prompt. Depois:
`python motion/ferramentas/biblioteca.py publicar <NN-tema> <ids...>`.

Por que recorte local e não um removedor de fundo on-line: a folha nasce sobre branco liso
de propósito, o que torna a separação exata em resolução cheia (o plano grátis desses
sites entrega prévia de baixa resolução, e o seletor de arquivo nativo não é operável).

Como acertar a separação (ela recusa quando acha um número de objetos diferente de --nomes):
  --limiar   distância ao branco para virar objeto (22). Sombra suave entrando no recorte e
             virando mancha → suba (ex.: 55).
  --juntar   px para unir partes de um mesmo objeto (24). Um objeto partido em dois → suba;
             dois objetos vizinhos colados → desça.
  --area-min área mínima de um objeto em px (2500); sujeira menor que isso é ignorada.
  --convexo  peças preenchidas pelo casco convexo: objeto branco sobre branco (prato,
             pires) perde metade da borda no limiar, e o casco o devolve inteiro.
  --lente    peças com vidro: o miolo claro (a lente de uma lupa) fica quase transparente.
  --filete   espessura do papel em px (9; 0 = sem filete, ex.: peça que vai desfocada à frente).
  --reticula pontos de retícula de revista sobre o objeto (padrão: foto limpa).
Os nomes casam com os objetos na ORDEM DE LEITURA: linhas de cima para baixo, cada linha da
esquerda para a direita. Confira os PNG antes de publicar.

A folha é lida NA ORIENTAÇÃO DE EXIBIÇÃO (EXIF aplicado): foto de celular gravada deitada
com `Orientation 6` exibe em pé, e é assim que a peça tem de sair (sem isso, uma folha que
exibe 3000x4000 virou peça deitada de 2423x1024). O bruto guardado em `brutos/` conserva os
bytes originais, EXIF incluído, por procedência — e quem o relê aplica o EXIF, como aqui.

Tudo determinístico: a borda de cada variante sai de uma semente pelo nome da peça.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from datetime import date
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

import biblioteca as B

PAPEL = np.array([241, 236, 224], np.float32)  # cor do papel do filete (off-white neutro)


def rng(nome: str) -> np.random.Generator:
    return np.random.default_rng(int(hashlib.sha256(nome.encode()).hexdigest()[:8], 16))


# ---------------------------------------------------------------- separação

def mascara_objetos(rgb: np.ndarray, limiar: int = 22) -> np.ndarray:
    """Objeto = tudo que se afasta do branco. Sombra suave clara fica de fora."""
    dist = 255 * 3 - rgb.astype(np.int32).sum(axis=2)
    m = (dist > limiar * 3).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    # fecha buracos internos (xícara branca dentro do pires branco)
    cont, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cheia = np.zeros_like(m)
    cv2.drawContours(cheia, cont, -1, 1, thickness=cv2.FILLED)
    return cheia


def convexo(alfa: np.ndarray) -> np.ndarray:
    """Preenche o contorno convexo: objeto branco sobre fundo branco (pires) perde
    metade da borda no limiar, e o pires é redondo -- o casco o devolve inteiro."""
    m = (alfa > 0.5).astype(np.uint8)
    pts = cv2.findNonZero(m)
    casco = np.zeros_like(m)
    if pts is not None:
        cv2.fillConvexPoly(casco, cv2.convexHull(pts), 1)
    return cv2.GaussianBlur(casco.astype(np.float32), (3, 3), 0.8)


def separar(folha: Path, nomes: list[str], juntar_px: int = 24, area_min: int = 2500,
            limiar: int = 22) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Separa os objetos da folha, na ordem de leitura, e devolve {nome: (rgb, alfa)}."""
    with Image.open(folha) as im:  # na orientação de exibição: o EXIF manda girar foto de celular
        rgb = np.array(ImageOps.exif_transpose(im).convert("RGB"))
    m = mascara_objetos(rgb, limiar)
    grosso = cv2.dilate(m, np.ones((juntar_px, juntar_px), np.uint8))
    n, rot, stats, cent = cv2.connectedComponentsWithStats(grosso)
    comps = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= area_min]
    if len(comps) != len(nomes):
        raise SystemExit(f"{Path(folha).name}: achei {len(comps)} objetos, esperava {len(nomes)} "
                         f"(áreas {[int(stats[i, cv2.CC_STAT_AREA]) for i in comps]}). Objeto partido em dois: "
                         "suba --juntar; vizinhos colados: desça --juntar; sombra virando objeto: suba --limiar; "
                         "sujeira: suba --area-min.")
    # ordem de leitura: linhas por centro y (tolerância de ~0,9 altura mediana), depois x
    alt = np.median([stats[i, cv2.CC_STAT_HEIGHT] for i in comps])
    comps.sort(key=lambda i: (round(cent[i][1] / (alt * 0.9)), cent[i][0]))
    out = {}
    for nome, i in zip(nomes, comps):
        x, y, w, h = stats[i, :4]
        p = 8
        x0, y0, x1, y1 = max(x - p, 0), max(y - p, 0), min(x + w + p, rgb.shape[1]), min(y + h + p, rgb.shape[0])
        alfa = ((rot[y0:y1, x0:x1] == i) & (m[y0:y1, x0:x1] > 0)).astype(np.float32)
        alfa = cv2.GaussianBlur(alfa, (3, 3), 0.8)
        out[nome] = (rgb[y0:y1, x0:x1].copy(), alfa)
    return out


def lente_transparente(rgb: np.ndarray, alfa: np.ndarray) -> np.ndarray:
    """A lente de vidro nasce branca (fundo visto pelo vidro). No vídeo ela passa por cima
    de outras peças, então o miolo claro vira quase transparente (10%)."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    claro = (hsv[..., 2] > 228) & (hsv[..., 1] < 22)
    n, rot, st, _ = cv2.connectedComponentsWithStats(claro.astype(np.uint8))
    h, w = claro.shape
    # o fundo branco em volta do recorte também é "claro" e é o maior componente:
    # a lente é o maior claro que NÃO encosta na borda
    internos = [i for i in range(1, n)
                if st[i, cv2.CC_STAT_LEFT] > 0 and st[i, cv2.CC_STAT_TOP] > 0
                and st[i, cv2.CC_STAT_LEFT] + st[i, cv2.CC_STAT_WIDTH] < w
                and st[i, cv2.CC_STAT_TOP] + st[i, cv2.CC_STAT_HEIGHT] < h]
    if not internos:
        print("aviso: --lente não achou miolo claro fechado; a peça fica opaca", file=sys.stderr)
        return alfa
    maior = max(internos, key=lambda i: st[i, cv2.CC_STAT_AREA])
    miolo = cv2.erode((rot == maior).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    alfa = alfa.copy()
    alfa[miolo] = 0.10
    return alfa


# ---------------------------------------------------------------- estética

def reticula(rgb: np.ndarray, celula: int = 7, satur: float = 0.8, forca: float = 0.55) -> np.ndarray:
    """Retícula de revista: pontos a 45° com raio pela escuridão, multiplicando a cor."""
    h, w = rgb.shape[:2]
    lum = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 1] *= satur
    base = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    base = base * 0.82 + PAPEL * 0.18  # papel por baixo da tinta
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx + yy) / np.sqrt(2) / celula
    v = (xx - yy) / np.sqrt(2) / celula
    du, dv = u - np.round(u), v - np.round(v)
    d = np.sqrt(du ** 2 + dv ** 2)  # 0 no centro da célula, ~0,7 no canto
    escuro = cv2.GaussianBlur(1 - lum, (0, 0), celula * 0.5)
    raio = np.sqrt(np.clip(escuro, 0, 1)) * 0.62
    ponto = np.clip((raio - d) * celula * 1.2 + 0.5, 0, 1)  # anti-aliased
    mult = 1 - forca * ponto[..., None]
    return np.clip(base * mult, 0, 255)


def ruido_suave(shape: tuple[int, int], escala: float, r: np.random.Generator) -> np.ndarray:
    h, w = shape
    pequeno = r.standard_normal((max(2, int(h / escala)), max(2, int(w / escala)))).astype(np.float32)
    grande = cv2.resize(pequeno, (w, h), interpolation=cv2.INTER_CUBIC)
    return grande / (np.abs(grande).max() + 1e-6)


def peca(rgb: np.ndarray, alfa: np.ndarray, nome: str, filete: int, com_reticula: bool = False,
         destino: Path | None = None) -> list[Path]:
    """Grava <nome>-b0..b2: objeto + filete de papel de borda irregular. Devolve os 3 caminhos.

    As três variantes são cortadas pela MESMA caixa (a união das três). Cortar cada uma
    justa na própria borda dava tamanhos diferentes (até 2,4%), e como o motor desenha as
    três com a mesma largura, o objeto inteiro pulsava de tamanho e escorregava a cada 3
    quadros. O boil só pode mexer no contorno de papel, nunca no objeto.
    """
    destino = Path(destino or ".")
    pad = filete * 2 + 6
    rgb = cv2.copyMakeBorder(rgb, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    alfa = cv2.copyMakeBorder(alfa, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    obj = reticula(rgb) if com_reticula else rgb.astype(np.float32)
    dentro = (alfa > 0.5).astype(np.uint8)
    dist_fora = cv2.distanceTransform(1 - dentro, cv2.DIST_L2, 5)
    variantes = []
    for b in range(3):
        r = rng(f"{nome}#{b}")
        # borda de tesoura: raio do filete oscila em baixa frequência + picote fino
        raio = filete * (1 + 0.35 * ruido_suave(dentro.shape, 60, r) + 0.12 * ruido_suave(dentro.shape, 9, r))
        fil = np.clip(raio - dist_fora + 0.5, 0, 1)
        fil = np.maximum(fil, alfa)
        cor = PAPEL[None, None, :] * (1 - alfa[..., None]) + obj * alfa[..., None]
        variantes.append(np.dstack([np.clip(cor, 0, 255), fil * 255]).astype(np.uint8))
    uniao = np.max([v[..., 3] for v in variantes], axis=0) > 5
    ys, xs = np.where(uniao)
    if not len(ys):
        raise SystemExit(f"{nome}: a peça ficou vazia (alfa zerado)")
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    destino.mkdir(parents=True, exist_ok=True)
    arqs = []
    for b, rgba in enumerate(variantes):
        arq = destino / f"{nome}-b{b}.png"
        Image.fromarray(rgba[y0:y1, x0:x1], "RGBA").save(arq, optimize=True)
        arqs.append(arq)
    print(f"{nome:20s} {x1 - x0}x{y1 - y0}")
    return arqs


def recortar(folha: Path, nomes: list[str], destino: Path, limiar: int = 22, juntar: int = 24,
             area_min: int = 2500, convexos: list[str] | tuple[str, ...] = (),
             lentes: list[str] | tuple[str, ...] = (), filete: int = 9,
             com_reticula: bool = False) -> dict[str, list[Path]]:
    """Separa a folha e grava as 3 variantes de cada peça em `destino`. Devolve {nome: [b0, b1, b2]}."""
    saida = {}
    for nome, (rgb, a) in separar(Path(folha), nomes, juntar_px=juntar, area_min=area_min, limiar=limiar).items():
        if nome in convexos:
            a = convexo(a)
        if nome in lentes:
            a = lente_transparente(rgb, a)
        saida[nome] = peca(rgb, a, nome, filete=filete, com_reticula=com_reticula, destino=destino)
    return saida


def _lista(v: str | None) -> list[str]:
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="recortar_folha.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folha", help="a folha baixada do ChatGPT (PNG sobre branco)")
    ap.add_argument("--nomes", required=True, help="um nome por objeto, na ordem de leitura, ex.: xicara,colher")
    ap.add_argument("--categoria", required=True, help="uma das de motion/biblioteca/categorias.json")
    ap.add_argument("--tags", required=True, help="separadas por vírgula; valem para todas as peças da folha")
    ap.add_argument("--prompt", help="o prompt que gerou a folha (fica no índice; obrigatório para gerado-chatgpt)")
    ap.add_argument("--origem", default="gerado-chatgpt",
                    choices=("gerado-chatgpt", "real-verificada", "real-nao-verificada"),
                    help="de onde veio a folha (padrão gerado-chatgpt; foto real de produto sobre branco: "
                         "real-verificada)")
    ap.add_argument("--limiar", type=int, default=22, help="distância ao branco (padrão 22)")
    ap.add_argument("--juntar", type=int, default=24, help="px para unir partes de um objeto (padrão 24)")
    ap.add_argument("--area-min", type=int, default=2500, help="área mínima em px (padrão 2500)")
    ap.add_argument("--convexo", default="", help="peças a preencher pelo casco convexo, ex.: pires")
    ap.add_argument("--lente", default="", help="peças com miolo de vidro quase transparente, ex.: lupa")
    ap.add_argument("--filete", type=int, default=9, help="espessura do papel em px (padrão 9; 0 = sem)")
    ap.add_argument("--reticula", action="store_true", help="aplica retícula de revista sobre o objeto")
    ap.add_argument("--dia", help="AAAA-MM-DD do id (padrão: hoje)")
    ap.add_argument("--substituir", action="store_true", help="refaz peças que já existem com o mesmo id")
    a = ap.parse_args(argv)

    folha = Path(a.folha)
    if not folha.is_file():
        raise SystemExit(f"folha não encontrada: {folha}")
    if not (1 <= a.limiar <= 254 and a.juntar >= 1 and a.area_min >= 1 and a.filete >= 0):
        raise SystemExit("parâmetros fora da faixa: --limiar 1..254, --juntar >= 1, --area-min >= 1, --filete >= 0")
    nomes, convexos, lentes = _lista(a.nomes), _lista(a.convexo), _lista(a.lente)
    if not nomes:
        raise SystemExit("--nomes vazio: um nome por objeto da folha, na ordem de leitura")
    repetidos = sorted({n for n in nomes if nomes.count(n) > 1})
    if repetidos:
        raise SystemExit(f"nomes repetidos em --nomes: {repetidos}")
    soltos = sorted(set(convexos + lentes) - set(nomes))
    if soltos:
        raise SystemExit(f"--convexo/--lente citam peças que não estão em --nomes: {soltos}")
    dia = a.dia or date.today().isoformat()
    # tudo o que pode recusar é conferido ANTES de recortar e de copiar qualquer arquivo
    ids = [B.validar_registro(n, a.categoria, a.origem, a.prompt, None, dia, a.substituir) for n in nomes]
    B.conferir_bruto(folha, dia, a.substituir)  # bytes e extensão originais; o EXIF vai junto
    tags = _lista(a.tags)
    if not tags:
        raise SystemExit("dê ao menos uma tag (--tags): é por elas que a próxima peça acha esta")
    with tempfile.TemporaryDirectory() as tmp:
        pecas = recortar(folha, nomes, Path(tmp), limiar=a.limiar, juntar=a.juntar, area_min=a.area_min,
                         convexos=convexos, lentes=lentes, filete=a.filete, com_reticula=a.reticula)
        bruto = B.guardar_bruto(folha, dia, a.substituir)
        for nome in nomes:
            B.registrar(nome, a.categoria, pecas[nome], tags, a.origem, bruto=bruto,
                        prompt=a.prompt, dia=dia, substituir=a.substituir)
    print(f"\n{len(ids)} peça(s) registrada(s); folha guardada em {bruto}")
    for ident in ids:
        print(f"  {ident}")
    print("Confira os PNG em motion/biblioteca/pecas/ e publique: "
          f"python motion/ferramentas/biblioteca.py publicar <NN-tema> {' '.join(ids)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # SystemExit e avisos saem aqui
    main()
