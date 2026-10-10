"""Turn the LLM's raw JSON answer into a set of vulnerability types."""


class ParseError(ValueError):
    pass


def parse_findings(response_text: str) -> set[str]:
    """Extract vulnerability types from a response such as
    ``{"vulnerabilities": [{"type": "reentrancy", ...}]}``.

    Synonyms (e.g. ``"arithmetic"``, ``"underflow"``) are mapped to the names
    in ``dataset.VULNERABILITY_TYPES``; anything else is ignored. Raises
    ``ParseError`` if the text is not valid JSON in the expected shape.
    """
    raise NotImplementedError
