"""Audit a single contract: clean code -> build prompt -> ask LLM -> parse."""

from dataclasses import dataclass

from smart_contract_auditor.dataset import Sample
from smart_contract_auditor.llm_client import LLMClient
from smart_contract_auditor.parser import ParseError, parse_findings
from smart_contract_auditor.preprocess import clean_source
from smart_contract_auditor.prompts import build_prompt


@dataclass(frozen=True)
class Finding:
    contract: str
    vulnerabilities: set[str]
    raw_response: str
    parse_failed: bool = False


def audit(sample: Sample, template: str, client: LLMClient) -> Finding:
    """Run the LLM on one sample.

    A response that cannot be parsed gives a ``Finding`` with
    ``parse_failed=True`` and no vulnerabilities instead of raising.
    """
    prompt = build_prompt(template, clean_source(sample.source_code))
    response = client.ask(prompt)
    try:
        vulnerabilities = parse_findings(response)
    except ParseError:
        return Finding(sample.contract, set(), response, parse_failed=True)
    return Finding(sample.contract, vulnerabilities, response)
