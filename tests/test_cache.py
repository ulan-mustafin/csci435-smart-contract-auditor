import json
from pathlib import Path

import pytest

from smart_contract_auditor.cache import CachedClient, prompt_hash


class CountingClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def ask(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return f"answer {len(self.prompts)}"


def test_stores_and_reuses_responses(tmp_path: Path) -> None:
    path = tmp_path / "raw" / "responses.jsonl"
    client = CountingClient()

    first = CachedClient(path, "gemini:m", client)
    assert first.ask("p1") == "answer 1"
    assert first.ask("p1") == "answer 1"

    reloaded = CachedClient(path, "gemini:m", client)
    assert reloaded.ask("p1") == "answer 1"
    assert client.prompts == ["p1"]

    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["model"] == "gemini:m"
    assert record["run"] == 1
    assert record["prompt_sha256"] == prompt_hash("p1")
    assert record["response"] == "answer 1"


def test_model_and_run_are_part_of_the_key(tmp_path: Path) -> None:
    path = tmp_path / "responses.jsonl"
    client = CountingClient()

    CachedClient(path, "gemini:m", client).ask("p")
    CachedClient(path, "openrouter:m", client).ask("p")
    CachedClient(path, "gemini:m", client, run=2).ask("p")

    assert len(client.prompts) == 3
    assert len(path.read_text(encoding="utf-8").splitlines()) == 3


def test_offline_mode(tmp_path: Path) -> None:
    path = tmp_path / "responses.jsonl"
    CachedClient(path, "gemini:m", CountingClient()).ask("known")
    offline = CachedClient(path, "gemini:m")

    assert offline.ask("known") == "answer 1"
    with pytest.raises(RuntimeError, match="No stored response"):
        offline.ask("unknown")
