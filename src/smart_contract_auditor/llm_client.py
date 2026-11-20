"""Clients that send a prompt to an LLM and return its raw text answer."""

import json
import os
from pathlib import Path
import urllib.error
import urllib.request
from typing import Any, Protocol


class LLMClient(Protocol):
    """Anything with an ``ask`` method can be used, including fakes in tests."""

    def ask(self, prompt: str) -> str: ...


def load_env_file(path: Path) -> None:
    """Copy KEY=VALUE lines from ``path`` into the environment (existing values win)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def _api_key(name: str) -> str:
    api_key = os.environ.get(name)
    if not api_key:
        raise RuntimeError(f"{name} is not set; add it to the .env file")
    return api_key


def _post_json(url: str, body: dict[str, Any], headers: dict[str, str], timeout: float, service: str) -> Any:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **headers},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"{service} API error {error.code}: {error.read().decode()}") from error


class GeminiClient:
    """Calls the Gemini REST API. The key is read from ``GEMINI_API_KEY``."""

    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, model: str, temperature: float = 0.0, timeout: float = 60.0) -> None:
        self._api_key = _api_key("GEMINI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def ask(self, prompt: str) -> str:
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "responseMimeType": "application/json",
            },
        }
        data = _post_json(
            self.URL.format(model=self.model),
            body,
            {"x-goog-api-key": self._api_key},
            self.timeout,
            "Gemini",
        )
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(part.get("text", "") for part in parts)


class OpenRouterClient:
    """Calls the OpenRouter chat completions API. The key is read from ``OPENROUTER_API_KEY``.

    ``model`` is an OpenRouter model id such as ``openai/gpt-4o-mini``.
    """

    URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, model: str, temperature: float = 0.0, timeout: float = 60.0) -> None:
        self._api_key = _api_key("OPENROUTER_API_KEY")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def ask(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
        }
        data = _post_json(
            self.URL,
            body,
            {"Authorization": f"Bearer {self._api_key}"},
            self.timeout,
            "OpenRouter",
        )
        if "error" in data:
            raise RuntimeError(f"OpenRouter API error: {data['error']}")
        return data["choices"][0]["message"]["content"] or ""
