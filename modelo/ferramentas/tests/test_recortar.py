"""`recortar_folha`: folha sobre branco → peças com filete de papel e 3 bordas (boil)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageOps

cv2 = pytest.importorskip("cv2", reason="opencv-python-headless não instalado neste Python (está no requirements.txt)")

import recortar_folha as R  # noqa: E402

VERMELHO, VERDE, AZUL = (200, 30, 30), (30, 160, 60), (30, 60, 200)


def folha_sintetica(caminho: Path) -> Path:
    """1200x800 branca, três formas coloridas afastadas, na mesma linha."""
    im = Image.new("RGB", (1200, 800), "white")
    d = ImageDraw.Draw(im)
    d.ellipse((100, 250, 350, 500), fill=VERMELHO)
    d.rectangle((500, 260, 720, 480), fill=VERDE)
    d.polygon([(950, 250), (1100, 500), (800, 500)], fill=AZUL)
    im.save(caminho)
    return caminho


def cor_dominante(png: Path) -> np.ndarray:
    a = np.asarray(Image.open(png).convert("RGBA")).astype(float)
    opaco = a[..., 3] > 250
    return a[opaco][:, :3].mean(axis=0)


def test_tres_pecas_tres_variantes_do_mesmo_tamanho(tmp_path: Path) -> None:
    folha = folha_sintetica(tmp_path / "folha.png")
    pecas = R.recortar(folha, ["redondo", "quadrado", "triangulo"], destino=tmp_path / "pecas")
    assert list(pecas) == ["redondo", "quadrado", "triangulo"]  # ordem de leitura
    for nome, arqs in pecas.items():
        assert len(arqs) == 3
        tamanhos = {Image.open(a).size for a in arqs}
        assert len(tamanhos) == 1, f"{nome}: variantes de tamanhos diferentes {tamanhos}"
        rgba = np.asarray(Image.open(arqs[0]))
        assert rgba.shape[2] == 4
        assert rgba[0, 0, 3] == 0  # canto fora do filete é transparente
    # o nome certo pegou o objeto certo
    assert np.argmax(cor_dominante(pecas["redondo"][0])) == 0
    assert np.argmax(cor_dominante(pecas["quadrado"][0])) == 1
    assert np.argmax(cor_dominante(pecas["triangulo"][0])) == 2
    # o boil mexe só no contorno: as 3 bordas diferem entre si
    b0, b1 = (np.asarray(Image.open(a))[..., 3] for a in pecas["redondo"][:2])
    assert (b0 != b1).any()


def test_contagem_errada_de_nomes_falha_com_mensagem(tmp_path: Path) -> None:
    folha = folha_sintetica(tmp_path / "folha.png")
    with pytest.raises(SystemExit, match="achei 3 objetos, esperava 2"):
        R.recortar(folha, ["a", "b"], destino=tmp_path / "pecas")


def test_lente_fica_quase_transparente(tmp_path: Path) -> None:
    """Anel escuro com miolo branco (a lente de uma lupa): o miolo vira ~10% de opacidade."""
    im = Image.new("RGB", (600, 600), "white")
    ImageDraw.Draw(im).ellipse((150, 150, 450, 450), outline=(40, 40, 40), width=30)
    folha = tmp_path / "lupa.png"
    im.save(folha)
    pecas = R.recortar(folha, ["lupa"], destino=tmp_path / "pecas", lentes=["lupa"], filete=6)
    a = np.asarray(Image.open(pecas["lupa"][0]))[..., 3]
    h, w = a.shape
    assert a[h // 2, w // 2] < 60  # miolo: quase transparente
    assert a[h // 2, 20:60].max() == 255  # aro: opaco


def test_convexo_fecha_a_reentrancia() -> None:
    m = np.zeros((100, 100), np.float32)
    m[20:80, 20:40] = 1  # um "C" grosso
    m[20:35, 20:80] = 1
    m[65:80, 20:80] = 1
    assert m[50, 60] == 0
    assert R.convexo(m)[50, 60] > 0.9


def folha_jpeg_deitada(caminho: Path) -> Path:
    """A folha como se VÊ: 600x800 em pé, um objeto azul 300x500 com um quadrado vermelho no canto
    superior esquerdo. Gravada deitada (girada 90° anti-horário) com EXIF Orientation 6, como sai
    de celular."""
    vista = Image.new("RGB", (600, 800), "white")
    d = ImageDraw.Draw(vista)
    d.rectangle((150, 150, 450, 650), fill=(30, 60, 160))
    d.rectangle((150, 150, 230, 230), fill=(220, 20, 20))
    exif = Image.Exif()
    exif[0x0112] = 6
    vista.transpose(Image.Transpose.ROTATE_90).save(caminho, "JPEG", quality=95, exif=exif.tobytes())
    with Image.open(caminho) as im:  # confere a montagem: bytes deitados, exibição em pé
        assert im.size == (800, 600) and ImageOps.exif_transpose(im).size == (600, 800)
    return caminho


def em_pe_com_vermelho_no_canto(png: Path) -> tuple[int, int]:
    rgba = np.asarray(Image.open(png).convert("RGBA")).astype(int)
    h, w = rgba.shape[:2]
    assert h > w, f"peça deitada: {w}x{h}"
    vermelho = (rgba[..., 0] > 150) & (rgba[..., 1] < 90) & (rgba[..., 2] < 90) & (rgba[..., 3] > 250)
    ys, xs = np.nonzero(vermelho)
    assert len(ys) > 1000
    assert xs.mean() < w / 2 and ys.mean() < h / 2, "o quadrado vermelho saiu do canto superior esquerdo"
    return w, h


def test_folha_com_exif_6_sai_em_pe_com_a_forma_no_lugar(tmp_path: Path) -> None:
    folha = folha_jpeg_deitada(tmp_path / "IMG_0001.JPG")
    [arqs] = R.recortar(folha, ["objeto"], destino=tmp_path / "pecas").values()
    assert len({Image.open(a).size for a in arqs}) == 1
    em_pe_com_vermelho_no_canto(arqs[0])


def test_cli_guarda_bytes_originais_e_quem_rele_o_bruto_aplica_o_exif(repo: Path) -> None:
    folha = folha_jpeg_deitada(repo / "IMG_0001.JPG")
    args = ["--nomes", "objeto", "--categoria", "objeto", "--tags", "t", "--prompt", "p", "--dia", "2026-10-07"]
    R.main([str(folha), *args])
    [item] = json.loads(Path("motion/biblioteca/indice.json").read_text(encoding="utf-8"))
    bruto = Path(item["bruto"])
    assert bruto.read_bytes() == folha.read_bytes()  # procedência: os bytes originais, EXIF incluído
    tamanho = em_pe_com_vermelho_no_canto(Path(item["arquivos"][0]))
    assert item["dimensoes"] == list(tamanho)
    R.main([str(bruto), *args, "--substituir"])  # recortar de novo a partir do bruto guardado
    [item2] = json.loads(Path("motion/biblioteca/indice.json").read_text(encoding="utf-8"))
    assert item2["bruto"] == item["bruto"] and item2["dimensoes"] == item["dimensoes"]
    em_pe_com_vermelho_no_canto(Path(item2["arquivos"][0]))


def test_cli_recorta_e_registra_na_biblioteca(repo: Path) -> None:
    folha = folha_sintetica(repo / "Folha Teste.png")
    R.main([str(folha), "--nomes", "redondo,quadrado,triangulo", "--categoria", "objeto",
            "--tags", "forma,teste", "--prompt", "três formas coloridas sobre branco #FFFFFF",
            "--dia", "2026-10-07"])
    itens = json.loads(Path("motion/biblioteca/indice.json").read_text(encoding="utf-8"))
    assert sorted(i["id"] for i in itens) == ["2026-10-07_quadrado", "2026-10-07_redondo", "2026-10-07_triangulo"]
    for i in itens:
        assert i["origem"] == "gerado-chatgpt"
        assert i["prompt"] == "três formas coloridas sobre branco #FFFFFF"
        assert len({Image.open(a).size for a in i["arquivos"]}) == 1
        assert Path(i["bruto"]).exists()  # a folha original foi guardada em brutos/
    assert itens[0]["bruto"] == "motion/biblioteca/brutos/2026-10-07_folha-teste.png"


def test_cli_contagem_errada_nao_registra_nada(repo: Path) -> None:
    folha = folha_sintetica(repo / "folha.png")
    with pytest.raises(SystemExit, match="esperava 4"):
        R.main([str(folha), "--nomes", "a,b,c,d", "--categoria", "objeto", "--tags", "t",
                "--prompt", "p", "--dia", "2026-10-07"])
    assert json.loads(Path("motion/biblioteca/indice.json").read_text(encoding="utf-8")) == []
    assert not list(Path("motion/biblioteca").rglob("*.png"))


def test_cli_recusa_id_que_ja_existe_antes_de_recortar(repo: Path) -> None:
    folha = folha_sintetica(repo / "folha.png")
    args = [str(folha), "--nomes", "redondo,quadrado,triangulo", "--categoria", "objeto", "--tags", "t",
            "--prompt", "p", "--dia", "2026-10-07"]
    R.main(args)
    with pytest.raises(SystemExit, match="já existe"):
        R.main(args)
    R.main(args + ["--substituir"])  # a mesma folha refeita
