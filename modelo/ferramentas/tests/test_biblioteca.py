"""`biblioteca`: registrar, buscar e publicar peças de colagem com as travas."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

import biblioteca as B


def variantes(pasta: Path, nome: str, n: int = 3, tam: tuple[int, int] = (40, 30)) -> list[Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    arqs = []
    for k in range(n):
        p = pasta / f"{nome}-b{k}.png"
        Image.new("RGBA", tam, (10 * k, 100, 200, 255)).save(p)
        arqs.append(p)
    return arqs


def indice() -> list[dict]:
    return json.loads(Path("motion/biblioteca/indice.json").read_text(encoding="utf-8"))


def test_registrar_copia_e_grava_no_indice(repo: Path) -> None:
    e = B.registrar("xicara", "objeto", variantes(repo / "tmp", "xicara"), ["Louça", "branca"],
                    "gerado-chatgpt", prompt="uma xícara branca sobre fundo #FFFFFF", dia="2026-10-07")
    assert e["id"] == "2026-10-07_xicara"
    for k in range(3):
        assert (repo / f"motion/biblioteca/pecas/objeto/2026-10-07_xicara-b{k}.png").exists()
    [item] = indice()
    assert item["tags"] == ["branca", "louça"]
    assert item["prompt"].startswith("uma xícara")
    assert item["arquivos"][0] == "motion/biblioteca/pecas/objeto/2026-10-07_xicara-b0.png"
    assert item["dimensoes"] == [40, 30]


def test_recusa_id_repetido_sem_substituir(repo: Path) -> None:
    arqs = variantes(repo / "tmp", "xicara")
    B.registrar("xicara", "objeto", arqs, ["a"], "codigo", dia="2026-10-07")
    B.publicar("01-teste", ["2026-10-07_xicara"])
    with pytest.raises(SystemExit, match="já existe"):
        B.registrar("xicara", "objeto", arqs, ["b"], "codigo", dia="2026-10-07")
    # a mesma peça refeita: substitui e mantém onde ela é usada
    e = B.registrar("xicara", "objeto", arqs, ["b"], "codigo", dia="2026-10-07", substituir=True)
    assert e["tags"] == ["b"]
    assert e["usado_em"] == ["01-teste"]
    assert len(indice()) == 1


def test_publicar_copia_para_a_peca(repo: Path) -> None:
    B.registrar("xicara", "objeto", variantes(repo / "tmp", "xicara"), ["a"], "codigo", dia="2026-10-07")
    B.publicar("01-teste", ["2026-10-07_xicara"])
    for k in range(3):
        assert (repo / f"motion/pecas/01-teste/public/colagem/xicara-b{k}.png").exists()
    assert indice()[0]["usado_em"] == ["01-teste"]


def test_publicar_peca_de_variante_unica_sem_sufixo(repo: Path) -> None:
    B.registrar("papel-kraft", "textura", variantes(repo / "tmp", "kraft", n=1), ["papel"], "codigo", dia="2026-10-07")
    B.publicar("01-teste", ["2026-10-07_papel-kraft"])
    assert (repo / "motion/pecas/01-teste/public/colagem/papel-kraft.png").exists()


def test_publicar_recusa_dois_nomes_iguais_no_mesmo_projeto(repo: Path) -> None:
    B.registrar("xicara", "objeto", variantes(repo / "a", "x"), ["a"], "codigo", dia="2026-10-07")
    B.registrar("xicara", "objeto", variantes(repo / "b", "x"), ["b"], "codigo", dia="2026-10-08")
    with pytest.raises(SystemExit, match="mesmo nome"):
        B.publicar("01-teste", ["2026-10-07_xicara", "2026-10-08_xicara"])
    B.publicar("01-teste", ["2026-10-07_xicara"])
    with pytest.raises(SystemExit, match="mesmo nome"):
        B.publicar("01-teste", ["2026-10-08_xicara"])


def test_publicar_recusa_projeto_inexistente(repo: Path) -> None:
    B.registrar("xicara", "objeto", variantes(repo / "tmp", "x"), ["a"], "codigo", dia="2026-10-07")
    with pytest.raises(SystemExit, match="01-teste"):  # a mensagem lista as peças que existem
        B.publicar("02-nao-existe", ["2026-10-07_xicara"])
    assert not (repo / "motion/pecas/02-nao-existe").exists()


def test_categoria_fora_do_arquivo_recusa(repo: Path) -> None:
    # "alimento" é categoria padrão, mas o categorias.json deste repo não a tem
    with pytest.raises(SystemExit, match="categoria"):
        B.registrar("pao", "alimento", variantes(repo / "tmp", "pao"), ["a"], "codigo", dia="2026-10-07")
    assert indice() == []


def test_categorias_em_formato_de_dicionario(repo: Path) -> None:
    Path("motion/biblioteca/categorias.json").write_text(
        json.dumps({"alimento": "comida, fruta", "objeto": "coisa"}, ensure_ascii=False), encoding="utf-8")
    e = B.registrar("pao", "alimento", variantes(repo / "tmp", "pao"), ["a"], "codigo", dia="2026-10-07")
    assert e["categoria"] == "alimento"


def test_sem_categorias_json_cria_o_padrao_do_contrato(repo: Path) -> None:
    Path("motion/biblioteca/categorias.json").unlink()
    assert list(B.categorias()) == ["objeto", "utensilio", "natureza", "alimento", "produto",
                                    "foto-real", "textura", "papelaria", "grafismo", "maos"]
    assert json.loads(Path("motion/biblioteca/categorias.json").read_text(encoding="utf-8"))[0] == "objeto"


def test_procedencia_obrigatoria(repo: Path) -> None:
    arqs = variantes(repo / "tmp", "x")
    with pytest.raises(SystemExit, match="prompt"):
        B.registrar("x", "objeto", arqs, ["a"], "gerado-chatgpt", dia="2026-10-07")
    with pytest.raises(SystemExit, match="fonte"):
        B.registrar("x", "objeto", arqs, ["a"], "banco-livre", dia="2026-10-07")
    with pytest.raises(SystemExit, match="origem"):
        B.registrar("x", "objeto", arqs, ["a"], "pinterest", dia="2026-10-07")


def test_produto_da_marca_nao_pode_ser_gerado(repo: Path) -> None:
    Path("motion/biblioteca/categorias.json").write_text(json.dumps(["produto"]), encoding="utf-8")
    arqs = variantes(repo / "tmp", "pacote")
    with pytest.raises(SystemExit, match="pixel real"):
        B.registrar("pacote", "produto", arqs, ["a"], "gerado-chatgpt", prompt="um pacote", dia="2026-10-07")
    B.registrar("pacote", "produto", arqs, ["a"], "real-verificada", bruto="fotos/pacote.jpg", dia="2026-10-07")


def test_registrar_grava_na_orientacao_de_exibicao(repo: Path) -> None:
    """Arquivo pronto que chega com EXIF Orientation 6 vira PNG em pé (o PNG não leva o EXIF)."""
    p = repo / "tmp" / "girada.jpg"
    p.parent.mkdir()
    exif = Image.Exif()
    exif[0x0112] = 6
    Image.new("RGB", (40, 30), (200, 50, 50)).save(p, "JPEG", exif=exif.tobytes())  # exibe 30x40
    e = B.registrar("girada", "objeto", [p], ["a"], "codigo", dia="2026-10-07")
    assert e["dimensoes"] == [30, 40]
    assert Image.open(e["arquivos"][0]).size == (30, 40)


def test_variantes_de_tamanhos_diferentes_recusa(repo: Path) -> None:
    arqs = variantes(repo / "a", "x", n=2) + variantes(repo / "b", "y", n=1, tam=(41, 30))
    with pytest.raises(SystemExit, match="tamanho"):
        B.registrar("x", "objeto", arqs, ["a"], "codigo", dia="2026-10-07")


def test_nome_invalido_recusa(repo: Path) -> None:
    with pytest.raises(SystemExit, match="nome"):
        B.registrar("Xícara Branca", "objeto", variantes(repo / "tmp", "x"), ["a"], "codigo", dia="2026-10-07")


def test_dia_fora_do_formato_recusa(repo: Path) -> None:
    for dia in ("20261007", "2026-W41-3", "07/10/2026", "2026-02-30"):
        with pytest.raises(SystemExit, match="AAAA-MM-DD"):
            B.registrar("x", "objeto", variantes(repo / "tmp", "x"), ["a"], "codigo", dia=dia)


def test_fora_da_raiz_do_repositorio_recusa(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit, match="motion"):
        B.carregar()


def test_linha_de_comando(repo: Path, capsys) -> None:
    arqs = [str(p) for p in variantes(repo / "tmp", "folha")]
    B.main(["registrar", "folha-seca", "objeto", *arqs, "--tags", "folha, seca", "--origem", "codigo",
            "--dia", "2026-10-07"])
    B.main(["buscar", "seca"])
    assert "2026-10-07_folha-seca" in capsys.readouterr().out
    B.main(["listar", "textura"])
    assert "2026-10-07_folha-seca" not in capsys.readouterr().out
    B.main(["publicar", "01-teste", "2026-10-07_folha-seca"])
    assert (repo / "motion/pecas/01-teste/public/colagem/folha-seca-b2.png").exists()


def test_registrar_cli_copia_o_bruto_de_fora_do_repositorio(repo: Path, tmp_path_factory) -> None:
    fora = tmp_path_factory.mktemp("downloads") / "Original Folha.png"
    Image.new("RGB", (50, 50), "white").save(fora)
    arqs = [str(a) for a in variantes(repo / "tmp", "x")]
    B.main(["registrar", "folha-x", "objeto", *arqs, "--tags", "t", "--origem", "codigo", "--bruto", str(fora),
            "--dia", "2026-10-07"])
    [item] = indice()
    assert item["bruto"] == "motion/biblioteca/brutos/2026-10-07_original-folha.png"
    assert Path(item["bruto"]).read_bytes() == fora.read_bytes()
