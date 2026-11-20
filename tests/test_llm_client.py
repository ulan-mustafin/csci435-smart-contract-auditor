import io
import json
import os
import urllib.request
from pathlib import Path

import pytest

from smart_contract_auditor import llm_client
from smart_contract_auditor.llm_client import OpenRouterClient, load_env_file


def fake_urlopen(answer: dict, requests: list) -> object:
    def urlopen(request: urllib.request.Request, timeout: float) -> io.BytesIO:
        requests.append(request)
        return io.BytesIO(json.dumps(answer).encode())

    return urlopen


def test_openrouter_sends_prompt_and_returns_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    requests: list = []
    answer = {"choices": [{"message": {"content": '{"vulnerabilities": []}'}}]}
    monkeypatch.setattr(llm_client.urllib.request, "urlopen", fake_urlopen(answer, requests))

    result = OpenRouterClient(model="openai/gpt-4o-mini").ask("Review this")

    assert result == '{"vulnerabilities": []}'
    request = requests[0]
    body = json.loads(request.data)
    assert request.full_url == OpenRouterClient.URL
    assert request.get_header("Authorization") == "Bearer test-key"
    assert body["model"] == "openai/gpt-4o-mini"
    assert body["messages"] == [{"role": "user", "content": "Review this"}]
    assert body["temperature"] == 0.0


def test_openrouter_reports_error_in_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    answer = {"error": {"code": 429, "message": "Rate limited"}}
    monkeypatch.setattr(llm_client.urllib.request, "urlopen", fake_urlopen(answer, []))

    with pytest.raises(RuntimeError, match="Rate limited"):
        OpenRouterClient(model="m").ask("x")


def test_openrouter_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        OpenRouterClient(model="m")


def test_load_env_file_keeps_existing_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXISTING_KEY", "from-shell")
    monkeypatch.setenv("NEW_KEY", "")
    monkeypatch.delenv("NEW_KEY")
    env_file = tmp_path / ".env"
    env_file.write_text('# comment\nNEW_KEY="from-file"\nEXISTING_KEY=from-file\n', encoding="utf-8")

    load_env_file(env_file)

    assert os.environ["NEW_KEY"] == "from-file"
    assert os.environ["EXISTING_KEY"] == "from-shell"
