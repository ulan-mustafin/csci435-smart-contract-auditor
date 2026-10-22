"""Turn the LLM's raw JSON answer into a set of vulnerability types."""

import json

from smart_contract_auditor.dataset import VULNERABILITY_TYPES


class ParseError(ValueError):
    pass


def parse_findings(response_text: str) -> set[str]:
    """Extract vulnerability types from a response such as
    ``{"vulnerabilities": [{"type": "reentrancy", ...}]}``.

    Synonyms (e.g. ``"arithmetic"``, ``"underflow"``) are mapped to the names
    in ``dataset.VULNERABILITY_TYPES``; anything else is ignored. Raises
    ``ParseError`` if the text is not valid JSON in the expected shape.
    """
    try:
        data = json.loads(response_text)
    except (json.JSONDecodeError, TypeError) as error:
        raise ParseError("Response is not valid JSON") from error
    if not isinstance(data, dict) or not isinstance(data.get("vulnerabilities"), list):
        raise ParseError("Expected an object with a vulnerabilities list")

    synonyms = {
        "arithmetic": "integer_overflow",
        "overflow": "integer_overflow",
        "underflow": "integer_overflow",
    }
    findings: set[str] = set()
    for entry in data["vulnerabilities"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("type"), str):
            raise ParseError("Each vulnerability must have a string type")
        label = entry["type"].strip().lower().replace("-", "_").replace(" ", "_")
        label = synonyms.get(label, label)
        if label in VULNERABILITY_TYPES:
            findings.add(label)
    return findings
