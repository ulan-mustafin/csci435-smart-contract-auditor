import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from smart_contract_auditor import cli


def create_inputs(root: Path) -> None:
    (root / "contract.sol").write_text("contract A {}", encoding="utf-8")
    (root / "labels.json").write_text(
        json.dumps([{"contract": "contract.sol", "vulnerabilities": []}]), encoding="utf-8"
    )
    (root / "prompts").mkdir()
    (root / "prompts/vulnerability_audit.txt").write_text("{code}", encoding="utf-8")


def arguments(root: Path) -> list[str]:
    return ["--root", str(root), "--labels", "labels.json", "--model", "test-model"]


def test_cli_runs_benchmark(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    create_inputs(tmp_path)
    calls: list[str] = []

    class FakeClient:
        def __init__(self, model: str) -> None:
            calls.append(model)

        def ask(self, prompt: str) -> str:
            calls.append(prompt)
            return '{"vulnerabilities": []}'

    monkeypatch.setattr(cli, "GeminiClient", FakeClient)
    output = tmp_path / "custom"

    assert cli.main(arguments(tmp_path) + ["--output", str(output)]) == 0
    assert calls == ["test-model", "contract A {}"]
    assert json.loads((output / "results.json").read_text())["contracts"] == 1


def test_cli_missing_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    create_inputs(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    assert cli.main(arguments(tmp_path)) == 1
    assert "GEMINI_API_KEY" in capsys.readouterr().err
    assert not (tmp_path / "reports").exists()


@pytest.mark.parametrize("invalid", ["labels", "template", "empty"])
def test_cli_validates_before_creating_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, invalid: str) -> None:
    create_inputs(tmp_path)
    if invalid == "labels":
        (tmp_path / "labels.json").unlink()
    elif invalid == "empty":
        (tmp_path / "labels.json").write_text("[]", encoding="utf-8")
    else:
        (tmp_path / "prompts/vulnerability_audit.txt").write_text("invalid", encoding="utf-8")

    def unexpected_client(model: str) -> None:
        pytest.fail("Client created before validation")

    monkeypatch.setattr(cli, "GeminiClient", unexpected_client)

    assert cli.main(arguments(tmp_path)) == 1
    assert not (tmp_path / "reports").exists()


def test_cli_requires_model() -> None:
    with pytest.raises(SystemExit) as error:
        cli.main([])
    assert error.value.code == 2


def test_cli_handles_client_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    create_inputs(tmp_path)

    class FailingClient:
        def __init__(self, model: str) -> None:
            pass

        def ask(self, prompt: str) -> str:
            raise RuntimeError("Service unavailable")

    monkeypatch.setattr(cli, "GeminiClient", FailingClient)

    assert cli.main(arguments(tmp_path)) == 1
    assert "Service unavailable" in capsys.readouterr().err
    assert not (tmp_path / "reports").exists()


def test_cli_uses_openrouter_provider(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    create_inputs(tmp_path)
    models: list[str] = []

    class FakeOpenRouter:
        def __init__(self, model: str) -> None:
            models.append(model)

        def ask(self, prompt: str) -> str:
            return '{"vulnerabilities": []}'

    monkeypatch.setattr(cli, "OpenRouterClient", FakeOpenRouter)
    monkeypatch.setattr(cli, "GeminiClient", lambda model: pytest.fail("Wrong provider"))

    assert cli.main(arguments(tmp_path) + ["--provider", "openrouter"]) == 0
    assert models == ["test-model"]


def test_cli_reads_key_from_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    create_inputs(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.delenv("OPENROUTER_API_KEY")
    (tmp_path / ".env").write_text("OPENROUTER_API_KEY=from-file\n", encoding="utf-8")
    keys: list[str | None] = []

    class FakeOpenRouter:
        def __init__(self, model: str) -> None:
            keys.append(os.environ.get("OPENROUTER_API_KEY"))

        def ask(self, prompt: str) -> str:
            return '{"vulnerabilities": []}'

    monkeypatch.setattr(cli, "OpenRouterClient", FakeOpenRouter)

    assert cli.main(arguments(tmp_path) + ["--provider", "openrouter"]) == 0
    assert keys == ["from-file"]


@pytest.mark.parametrize("entrypoint", [["-m", "smart_contract_auditor"], ["main.py"]])
def test_entrypoint_help(entrypoint: list[str]) -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, *entrypoint, "--help"], cwd=root, capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "--model" in result.stdout
