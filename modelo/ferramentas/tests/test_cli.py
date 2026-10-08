"""Toda ferramenta responde `--help`, e o `instalar.py` roda só com a biblioteca padrão."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

FERRAMENTAS = Path(__file__).resolve().parent.parent
PRECISAM_CV2 = {"recortar_folha", "foto_papel"}
TODAS = ["alinhar_narracao", "alinhar_forcado", "conferir_alinhamento", "biblioteca", "recortar_folha",
         "foto_papel", "sons", "varrer_movimento", "folha_do_video", "instalar"]


@pytest.mark.parametrize("nome", TODAS)
def test_ajuda(nome: str, capsys) -> None:
    if nome in PRECISAM_CV2:
        pytest.importorskip("cv2", reason="opencv-python-headless não instalado neste Python")
    mod = importlib.import_module(nome)
    with pytest.raises(SystemExit) as fim:
        mod.main(["--help"])
    assert fim.value.code == 0
    assert capsys.readouterr().out.strip()


def test_instalar_ajuda_so_com_a_biblioteca_padrao() -> None:
    # -I isola do ambiente e -S desliga o site-packages: numpy, PIL etc. não existem aqui
    r = subprocess.run([sys.executable, "-I", "-S", str(FERRAMENTAS / "instalar.py"), "--help"],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    assert "--sem-modelos" in r.stdout


def test_requirements_tem_o_que_o_contrato_pede() -> None:
    import instalar
    base, modelos = instalar.separar_requisitos((FERRAMENTAS / "requirements.txt").read_text(encoding="utf-8"))
    nomes = {instalar.nome_do_pacote(r) for r in base}
    assert nomes == {"numpy", "pillow", "opencv-python-headless", "pytest"}
    assert {instalar.nome_do_pacote(r) for r in modelos} == {"torch", "torchaudio"}


def test_plano_sem_modelos_pula_whisper_e_torch() -> None:
    import instalar
    completo = {e.chave for e in instalar.plano(sem_modelos=False)}
    rapido = {e.chave for e in instalar.plano(sem_modelos=True)}
    assert {"venv", "python-base", "npm", "torch", "whisper"} <= completo
    assert "torch" not in rapido and "whisper" not in rapido
    assert {"venv", "python-base", "npm"} <= rapido
    # todo passo que baixa diz quanto
    assert all(e.megabytes is not None for e in instalar.plano(sem_modelos=False) if e.baixa)


def test_plano_nao_instala_nada(repo: Path, capsys) -> None:
    import instalar
    (repo / "motion" / "ferramentas").mkdir()
    (repo / "motion" / "ferramentas" / "requirements.txt").write_text(
        (FERRAMENTAS / "requirements.txt").read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "motion" / "remotion").mkdir()
    (repo / "motion" / "remotion" / "package.json").write_text("{}", encoding="utf-8")
    instalar.main(["--plano"])  # só mostra: não pode lançar nem instalar
    out = capsys.readouterr().out
    assert "MB" in out
    assert not (repo / "motion" / ".venv").exists()
    assert not (repo / "motion" / "remotion" / "node_modules").exists()


def test_instalar_recusa_fora_da_raiz(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import instalar
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit, match="motion"):
        instalar.main(["--plano"])


def _repo_do_motor(repo: Path, engines: str | None) -> None:
    (repo / "motion" / "ferramentas").mkdir(exist_ok=True)
    (repo / "motion" / "ferramentas" / "requirements.txt").write_text(
        (FERRAMENTAS / "requirements.txt").read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "motion" / "remotion").mkdir(exist_ok=True)
    pacote = {"name": "motor"} if engines is None else {"name": "motor", "engines": {"node": engines}}
    (repo / "motion" / "remotion" / "package.json").write_text(json.dumps(pacote), encoding="utf-8")


@pytest.mark.parametrize(("tem", "ok"), [((20, 18, 0), False), ((22, 11, 1), False), ((22, 12, 0), True),
                                         ((24, 0, 0), True)])
def test_node_tem_de_atender_o_engines_do_motor(repo: Path, monkeypatch: pytest.MonkeyPatch, tem, ok) -> None:
    import instalar
    _repo_do_motor(repo, ">=22.12.0")
    monkeypatch.setattr(instalar.shutil, "which", lambda nome: f"/bin/{nome}")
    monkeypatch.setattr(instalar, "_versao_node", lambda node: (tem, "v" + ".".join(map(str, tem))))
    [(item, passou, _)] = [r for r in instalar.requisitos(sem_modelos=True) if r[0].startswith("Node")]
    assert "22.12.0" in item and passou is ok


def test_node_velho_para_antes_de_baixar(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import instalar
    _repo_do_motor(repo, ">=22.12.0")
    monkeypatch.setattr(instalar, "_versao_node", lambda node: ((20, 18, 0), "v20.18.0"))
    monkeypatch.setattr(instalar, "conferir_espaco", lambda *a, **k: None)
    monkeypatch.setattr(instalar, "_rodar", lambda *a, **k: pytest.fail("não podia instalar nada"))
    with pytest.raises(SystemExit, match="Node >= 22.12.0"):
        instalar.main(["--sem-modelos"])
    assert not (repo / "motion" / ".venv").exists()


def test_sem_engines_o_minimo_e_18(repo: Path) -> None:
    import instalar
    _repo_do_motor(repo, None)
    assert instalar.node_exigido() == (18, 0, 0)


def test_modelo_do_whisper_com_tamanho_errado_para(repo: Path) -> None:
    import instalar
    pasta = repo / "motion" / "ferramentas" / "whisper.cpp"
    pasta.mkdir(parents=True)
    instalar.executavel_whisper().write_bytes(b"exe")
    (pasta / "ggml-small.bin").write_bytes(b"truncado")
    with pytest.raises(SystemExit, match="487601967"):
        instalar.conferir_whisper()
