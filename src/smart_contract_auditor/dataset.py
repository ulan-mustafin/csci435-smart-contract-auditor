"""Load benchmark contracts together with their vulnerability labels."""

from dataclasses import dataclass
import json
from pathlib import Path

VULNERABILITY_TYPES = frozenset({"reentrancy", "integer_overflow"})


@dataclass(frozen=True)
class Sample:
    contract: str
    source_code: str
    vulnerabilities: set[str]


def load_dataset(labels_path: Path, root: Path) -> list[Sample]:
    """Read ``labels.json`` and the contract files it lists.

    Contract paths in the labels file are relative to ``root`` (the repository
    root). Raises ``ValueError`` if a file is missing or a label is not in
    ``VULNERABILITY_TYPES``.
    """
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    if not isinstance(labels, list):
        raise ValueError("Labels must be a list of contracts")

    samples: list[Sample] = []
    seen: set[str] = set()
    for entry in labels:
        if not isinstance(entry, dict):
            raise ValueError("Each label must be an object")
        contract = entry.get("contract")
        vulnerabilities = entry.get("vulnerabilities")
        if not isinstance(contract, str) or not contract or contract in seen:
            raise ValueError(f"Invalid or duplicate contract: {contract!r}")
        if not isinstance(vulnerabilities, list) or any(
            not isinstance(label, str) or label not in VULNERABILITY_TYPES
            for label in vulnerabilities
        ):
            raise ValueError(f"Invalid vulnerabilities for {contract}")
        path = (root / contract).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"Missing or invalid contract file: {contract}")
        samples.append(Sample(contract, path.read_text(encoding="utf-8"), set(vulnerabilities)))
        seen.add(contract)
    return samples
