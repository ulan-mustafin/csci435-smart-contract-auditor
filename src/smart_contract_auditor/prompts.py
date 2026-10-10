"""Load prompt templates from the ``prompts/`` directory and fill them in."""

from pathlib import Path

CODE_PLACEHOLDER = "{code}"


def load_prompt(name: str, prompts_dir: Path) -> str:
    """Return the text of ``prompts_dir/<name>.txt``."""
    raise NotImplementedError


def build_prompt(template: str, source_code: str) -> str:
    """Insert the contract code at ``CODE_PLACEHOLDER``.

    Uses plain string replacement rather than ``str.format`` because
    templates contain JSON examples with literal braces.
    """
    raise NotImplementedError
