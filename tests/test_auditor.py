import pytest

from smart_contract_auditor.auditor import audit
from smart_contract_auditor.dataset import Sample
from smart_contract_auditor.parser import ParseError, parse_findings


class FakeClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompt = ""

    def ask(self, prompt: str) -> str:
        self.prompt = prompt
        return self.response


def test_audit_cleans_hints_and_parses_response() -> None:
    sample = Sample("example.sol", "contract C {} // REENTRANCY hint", {"reentrancy"})
    client = FakeClient('{"vulnerabilities": [{"type": "reentrancy"}]}')

    finding = audit(sample, "Review: {code}", client)

    assert "hint" not in client.prompt
    assert "contract C {}" in client.prompt
    assert finding.contract == "example.sol"
    assert finding.vulnerabilities == {"reentrancy"}
    assert finding.parse_failed is False


def test_audit_reports_invalid_response_without_crashing() -> None:
    sample = Sample("example.sol", "contract C {}", set())
    finding = audit(sample, "{code}", FakeClient("not json"))

    assert finding.parse_failed is True
    assert finding.vulnerabilities == set()
    assert finding.raw_response == "not json"


def test_parse_synonyms_and_ignore_unrelated_findings() -> None:
    result = parse_findings(
        '{"vulnerabilities": [{"type": "underflow"}, {"type": "OVERFLOW"}, '
        '{"type": "access_control"}]}'
    )
    assert result == {"integer_overflow"}


@pytest.mark.parametrize("response", ['{"vulnerabilities": "none"}', "[]", '{"vulnerabilities": [3]}'])
def test_parse_rejects_invalid_shapes(response: str) -> None:
    with pytest.raises(ParseError):
        parse_findings(response)
