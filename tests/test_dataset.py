import json
from pathlib import Path
import re

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


def test_repository_labels_have_metadata() -> None:
    root = Path(__file__).resolve().parents[1]
    samples = load_dataset(root / "data/raw/labels.json", root)

    for sample in samples:
        assert sample.origin in {"local", "public"}
        pragma = re.search(r"pragma solidity\s+\^?([\d.]+)", sample.source_code)
        assert pragma and pragma.group(1) == sample.solc_version, sample.contract

    pairs: dict[str, list] = {}
    for sample in samples:
        if sample.pair_id:
            pairs.setdefault(sample.pair_id, []).append(sample)
    for pair in pairs.values():
        assert sorted(bool(sample.vulnerabilities) for sample in pair) == [False, True]


def test_metadata_fields_are_optional(tmp_path: Path) -> None:
    (tmp_path / "contract.sol").write_text("contract Example {}", encoding="utf-8")
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps([{"contract": "contract.sol", "vulnerabilities": []}]), encoding="utf-8")

    sample = load_dataset(labels, tmp_path)[0]

    assert (sample.origin, sample.solc_version, sample.pair_id) == (None, None, None)


@pytest.mark.parametrize(
    "entries",
    [
        [{"contract": "contract.sol", "vulnerabilities": ["unknown"]}],
        [{"contract": "missing.sol", "vulnerabilities": []}],
        [{"contract": "../outside.sol", "vulnerabilities": []}],
        [{"contract": "contract.sol", "vulnerabilities": []}] * 2,
        [{"contract": "contract.sol", "vulnerabilities": [], "origin": "github"}],
        [{"contract": "contract.sol", "vulnerabilities": [], "solc_version": "^0.8"}],
        [{"contract": "contract.sol", "vulnerabilities": [], "pair_id": "lonely"}],
    ],
)
def test_reject_invalid_labels(tmp_path: Path, entries: list[dict]) -> None:
    (tmp_path / "contract.sol").write_text("contract Example {}", encoding="utf-8")
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps(entries), encoding="utf-8")

    with pytest.raises(ValueError):
        load_dataset(labels, tmp_path)
