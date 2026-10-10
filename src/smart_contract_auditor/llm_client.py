"""Clients that send a prompt to an LLM and return its raw text answer."""

import json
import os
import urllib.error
import urllib.request
from typing import Protocol


class LLMClient(Protocol):
    """Anything with an ``ask`` method can be used, including fakes in tests."""

    def ask(self, prompt: str) -> str: ...


class OpenAIClient:
    """Calls the OpenAI API. The key is read from ``OPENAI_API_KEY``."""

    def __init__(self, model: str, temperature: float = 0.0) -> None:
        self.model = model
        self.temperature = temperature

    def ask(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiClient:
    """Calls the Gemini REST API. The key is read from ``GEMINI_API_KEY``."""

    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, model: str, temperature: float = 0.0, timeout: float = 60.0) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set; add it to the .env file")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self._api_key = api_key

    def ask(self, prompt: str) -> str:
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "responseMimeType": "application/json",
            },
        }
        request = urllib.request.Request(
            self.URL.format(model=self.model),
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": self._api_key},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"Gemini API error {error.code}: {error.read().decode()}") from error

        parts = data["candidates"][0]["content"]["parts"]
        return "".join(part.get("text", "") for part in parts)
