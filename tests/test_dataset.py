import json
from pathlib import Path

import pytest

from smart_contract_auditor.dataset import load_dataset


def test_load_repository_samples() -> None:
    root = Path(__file__).resolve().parents[1]
    samples = load_dataset(root / "data/raw/labels.json", root)

    assert len(samples) == 6
    assert {sample.contract: sample.vulnerabilities for sample in samples} == {
        "contracts/reentrancy_vulnerable.sol": {"reentrancy"},
        "contracts/integer_overflow_vulnerable.sol": {"integer_overflow"},
        "contracts/reentrancy_cross_function.sol": {"reentrancy"},
        "contracts/integer_underflow_unchecked.sol": {"integer_overflow"},
        "contracts/reentrancy_safe.sol": set(),
        "contracts/integer_overflow_safe.sol": set(),
    }
    assert all("pragma solidity" in sample.source_code for sample in samples)


@pytest.mark.parametrize(
    "entries",
    [
        [{"contract": "contract.sol", "vulnerabilities": ["unknown"]}],
        [{"contract": "missing.sol", "vulnerabilities": []}],
        [{"contract": "../outside.sol", "vulnerabilities": []}],
        [{"contract": "contract.sol", "vulnerabilities": []}] * 2,
    ],
)
def test_reject_invalid_labels(tmp_path: Path, entries: list[dict]) -> None:
    (tmp_path / "contract.sol").write_text("contract Example {}", encoding="utf-8")
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps(entries), encoding="utf-8")

    with pytest.raises(ValueError):
        load_dataset(labels, tmp_path)
