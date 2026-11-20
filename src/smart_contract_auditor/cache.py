"""Store every LLM answer in a JSONL file so a benchmark can be repeated without new API calls."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from smart_contract_auditor.llm_client import LLMClient


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


class CachedClient:
    """Answers from ``path`` when the same model, run and prompt were already asked.

    Otherwise asks ``client`` and appends the answer to ``path``. With no
    ``client`` (offline mode) a missing answer is an error.
    """

    def __init__(self, path: Path, model: str, client: LLMClient | None = None, run: int = 1) -> None:
        self.path = path
        self.model = model
        self.client = client
        self.run = run
        self._responses: dict[tuple[str, int, str], str] = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    record = json.loads(line)
                    key = (record["model"], record["run"], record["prompt_sha256"])
                    self._responses[key] = record["response"]

    def ask(self, prompt: str) -> str:
        key = (self.model, self.run, prompt_hash(prompt))
        if key in self._responses:
            return self._responses[key]
        if self.client is None:
            raise RuntimeError(f"No stored response for {self.model} run {self.run} in {self.path}")
        response = self.client.ask(prompt)
        record = {
            "model": self.model,
            "run": self.run,
            "prompt_sha256": key[2],
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "response": response,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record) + "\n")
        self._responses[key] = response
        return response
