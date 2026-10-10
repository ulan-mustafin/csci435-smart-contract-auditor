"""Load benchmark contracts together with their vulnerability labels."""

from dataclasses import dataclass
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
    raise NotImplementedError
