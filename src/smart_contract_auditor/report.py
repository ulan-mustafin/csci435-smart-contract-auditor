"""Write benchmark results to the ``reports/`` directory."""

from pathlib import Path

from smart_contract_auditor.auditor import Finding
from smart_contract_auditor.dataset import Sample


def write_report(samples: list[Sample], findings: list[Finding], out_dir: Path) -> None:
    """Compare findings with labels and save the results in ``out_dir``.

    Planned outputs: ``results.json`` (overall and per-type metrics),
    ``per_contract.csv`` (expected vs found) and ``summary.md``.
    """
    raise NotImplementedError
