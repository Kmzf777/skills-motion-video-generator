"""`foto_papel`: foto real como cópia impressa de borda rasgada, honrando o EXIF."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

pytest.importorskip("cv2", reason="opencv-python-headless não instalado neste Python (está no requirements.txt)")

import foto_papel as F  # noqa: E402


def foto_deitada_com_exif_6(caminho: Path) -> Path:
    """Gravada 400x200, mas o EXIF manda girar: exibe 200x400 (em pé), como foto de celular."""
    im = Image.new("RGB", (400, 200), (180, 120, 60))
    exif = Image.Exif()
    exif[0x0112] = 6  # Orientation
    im.save(caminho, "JPEG", exif=exif.tobytes())
    return caminho


def test_honra_a_rotacao_do_exif(tmp_path: Path) -> None:
    foto = foto_deitada_com_exif_6(tmp_path / "IMG_0001.JPG")
    arqs = F.foto_rasgada(foto, "foto-teste", 100, destino=tmp_path / "pecas")
    assert len(arqs) == 3
    tamanhos = {Image.open(a).size for a in arqs}
    assert tamanhos == {(100 + 2 * 18, 200 + 2 * 18)}  # em pé: altura = 2x largura


def test_recorte_em_fracoes(tmp_path: Path) -> None:
    foto = foto_deitada_com_exif_6(tmp_path / "f.jpg")
    arqs = F.foto_rasgada(foto, "metade", 100, recorte=(0.0, 0.0, 1.0, 0.5), destino=tmp_path / "pecas")
    assert Image.open(arqs[0]).size == (136, 136)


def test_cli_registra_com_procedencia(repo: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    # a foto chega de FORA do repositório (a pasta Downloads, por exemplo)
    foto = foto_deitada_com_exif_6(tmp_path_factory.mktemp("downloads") / "Foto Rua.jpg")
    with pytest.raises(SystemExit, match="fonte"):
        F.main([str(foto), "foto-banco", "--tags", "rua", "--origem", "banco-livre", "--dia", "2026-10-07"])
    F.main([str(foto), "foto-banco", "--tags", "rua,cidade", "--origem", "banco-livre",
            "--fonte", "https://unsplash.com/photos/exemplo", "--largura", "120", "--dia", "2026-10-07"])
    [item] = json.loads(Path("motion/biblioteca/indice.json").read_text(encoding="utf-8"))
    assert item["id"] == "2026-10-07_foto-banco"
    assert item["categoria"] == "foto-real"
    assert item["fonte"] == "https://unsplash.com/photos/exemplo"
    # o índice é versionado: o original é copiado para brutos/, bytes intactos, e o caminho é relativo
    assert item["bruto"] == "motion/biblioteca/brutos/2026-10-07_foto-rua.jpg"
    assert Path(item["bruto"]).read_bytes() == foto.read_bytes()
    assert item["dimensoes"] == [120 + 36, 240 + 36]
