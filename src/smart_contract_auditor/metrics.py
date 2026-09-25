from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Metrics:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float


def calculate_metrics(
    expected: Mapping[str, set[str]], findings: Mapping[str, set[str]]
) -> Metrics:
    expected_pairs = {
        (contract, vulnerability)
        for contract, vulnerabilities in expected.items()
        for vulnerability in vulnerabilities
    }
    finding_pairs = {
        (contract, vulnerability)
        for contract, vulnerabilities in findings.items()
        for vulnerability in vulnerabilities
    }

    true_positives = len(expected_pairs & finding_pairs)
    false_positives = len(finding_pairs - expected_pairs)
    false_negatives = len(expected_pairs - finding_pairs)
    precision = true_positives / (true_positives + false_positives) if finding_pairs else 0.0
    recall = true_positives / (true_positives + false_negatives) if expected_pairs else 0.0

    return Metrics(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=precision,
        recall=recall,
    )
