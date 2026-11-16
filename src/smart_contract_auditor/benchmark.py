from pathlib import Path

from smart_contract_auditor.auditor import Finding, audit
from smart_contract_auditor.dataset import Sample
from smart_contract_auditor.llm_client import LLMClient
from smart_contract_auditor.prompts import build_prompt
from smart_contract_auditor.report import write_report


def run_benchmark(
    samples: list[Sample], template: str, client: LLMClient, out_dir: Path
) -> list[Finding]:
    if len({sample.contract for sample in samples}) != len(samples):
        raise ValueError("Duplicate contracts")
    build_prompt(template, "")
    findings = [audit(sample, template, client) for sample in samples]
    write_report(samples, findings, out_dir)
    return findings
