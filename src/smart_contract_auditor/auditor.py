"""Audit a single contract: clean code -> build prompt -> ask LLM -> parse."""

from dataclasses import dataclass

from smart_contract_auditor.dataset import Sample
from smart_contract_auditor.llm_client import LLMClient


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
    raise NotImplementedError
