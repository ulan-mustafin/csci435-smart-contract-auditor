import csv
from dataclasses import asdict
import json
from pathlib import Path

from smart_contract_auditor.auditor import Finding
from smart_contract_auditor.dataset import Sample, VULNERABILITY_TYPES
from smart_contract_auditor.metrics import calculate_metrics, calculate_metrics_by_type


def write_report(samples: list[Sample], findings: list[Finding], out_dir: Path) -> None:
    expected = {sample.contract: sample.vulnerabilities for sample in samples}
    found = {finding.contract: finding.vulnerabilities for finding in findings}
    if len(expected) != len(samples) or len(found) != len(findings):
        raise ValueError("Duplicate contracts")
    if expected.keys() != found.keys():
        raise ValueError("Findings must match dataset contracts")
    if any(finding.parse_failed and finding.vulnerabilities for finding in findings):
        raise ValueError("Failed responses cannot contain findings")
    by_contract = {finding.contract: finding for finding in findings}
    results = {
        "contracts": len(samples),
        "parse_failures": sum(finding.parse_failed for finding in findings),
        "overall": asdict(calculate_metrics(expected, found)),
        "by_type": {
            name: asdict(metrics)
            for name, metrics in calculate_metrics_by_type(
                expected, found, sorted(VULNERABILITY_TYPES)
            ).items()
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    with (out_dir / "per_contract.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["contract", "expected", "found", "parse_failed"])
        for sample in samples:
            finding = by_contract[sample.contract]
            writer.writerow([
                sample.contract,
                ";".join(sorted(sample.vulnerabilities)),
                ";".join(sorted(finding.vulnerabilities)),
                finding.parse_failed,
            ])
