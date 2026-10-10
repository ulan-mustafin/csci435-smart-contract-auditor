"""Clients that send a prompt to an LLM and return its raw text answer."""

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
