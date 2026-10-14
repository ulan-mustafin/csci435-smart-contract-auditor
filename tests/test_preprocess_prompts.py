from pathlib import Path

import pytest

from smart_contract_auditor.preprocess import clean_source
from smart_contract_auditor.prompts import build_prompt, load_prompt


def test_strip_comments_without_changing_literals_or_line_numbers() -> None:
    source = 'string memory url = "https://example.com/*keep*/"; // hint\n/* secret\nlabel */ uint value = 1;'
    cleaned = clean_source(source)

    assert '"https://example.com/*keep*/"' in cleaned
    assert "hint" not in cleaned and "secret" not in cleaned and "label" not in cleaned
    assert cleaned.count("\n") == source.count("\n")
    assert "uint value = 1;" in cleaned


def test_prompt_uses_literal_braces_and_clean_code() -> None:
    root = Path(__file__).resolve().parents[1]
    template = load_prompt("vulnerability_audit", root / "prompts")
    prompt = build_prompt(template, clean_source("contract C {} // label"))

    assert '{"vulnerabilities":' in prompt
    assert "contract C {}" in prompt
    assert "label" not in prompt
    assert "{code}" not in prompt


def test_prompt_rejects_invalid_name_and_missing_code(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        load_prompt("../other", tmp_path)
    with pytest.raises(ValueError):
        build_prompt("No placeholder", "contract C {}")
