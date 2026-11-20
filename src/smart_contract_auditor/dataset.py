"""Load benchmark contracts together with their vulnerability labels."""

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re

VULNERABILITY_TYPES = frozenset({"reentrancy", "integer_overflow"})
ORIGINS = frozenset({"local", "public"})
_VERSION = re.compile(r"\d+\.\d+\.\d+")


@dataclass(frozen=True)
class Sample:
    contract: str
    source_code: str
    vulnerabilities: set[str]
    origin: str | None = None
    solc_version: str | None = None
    pair_id: str | None = None


def load_dataset(labels_path: Path, root: Path) -> list[Sample]:
    """Read ``labels.json`` and the contract files it lists.

    Contract paths in the labels file are relative to ``root`` (the repository
    root). ``origin``, ``solc_version`` and ``pair_id`` are optional; a
    ``pair_id`` must be shared by exactly two contracts. Raises ``ValueError``
    if a file is missing or a field is invalid.
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
        origin = entry.get("origin")
        solc_version = entry.get("solc_version")
        pair_id = entry.get("pair_id")
        if origin is not None and origin not in ORIGINS:
            raise ValueError(f"Invalid origin for {contract}: {origin!r}")
        if solc_version is not None and (
            not isinstance(solc_version, str) or not _VERSION.fullmatch(solc_version)
        ):
            raise ValueError(f"Invalid solc_version for {contract}: {solc_version!r}")
        if pair_id is not None and (not isinstance(pair_id, str) or not pair_id):
            raise ValueError(f"Invalid pair_id for {contract}: {pair_id!r}")
        path = (root / contract).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"Missing or invalid contract file: {contract}")
        source_code = path.read_text(encoding="utf-8")
        samples.append(
            Sample(contract, source_code, set(vulnerabilities), origin, solc_version, pair_id)
        )
        seen.add(contract)

    pair_sizes = Counter(sample.pair_id for sample in samples if sample.pair_id)
    unmatched = sorted(pair_id for pair_id, size in pair_sizes.items() if size != 2)
    if unmatched:
        raise ValueError(f"Each pair_id must be used by exactly two contracts: {unmatched}")
    return samples
