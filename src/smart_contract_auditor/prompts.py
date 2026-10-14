"""Load prompt templates from the ``prompts/`` directory and fill them in."""

from pathlib import Path

CODE_PLACEHOLDER = "{code}"


def load_prompt(name: str, prompts_dir: Path) -> str:
    """Return the text of ``prompts_dir/<name>.txt``."""
    if not name or Path(name).name != name or name in {".", ".."}:
        raise ValueError("Prompt name must be a simple filename")
    return (prompts_dir / f"{name}.txt").read_text(encoding="utf-8")


def build_prompt(template: str, source_code: str) -> str:
    """Insert the contract code at ``CODE_PLACEHOLDER``.

    Uses plain string replacement rather than ``str.format`` because
    templates contain JSON examples with literal braces.
    """
    if CODE_PLACEHOLDER not in template:
        raise ValueError(f"Prompt template must contain {CODE_PLACEHOLDER}")
    return template.replace(CODE_PLACEHOLDER, source_code)
