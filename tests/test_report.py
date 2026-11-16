import csv
import json
from pathlib import Path

import pytest

from smart_contract_auditor.auditor import Finding
from smart_contract_auditor.dataset import Sample
from smart_contract_auditor.report import write_report


def test_write_report(tmp_path: Path) -> None:
    samples = [Sample("a.sol", "", {"reentrancy"}), Sample("b.sol", "", set())]
    findings = [Finding("b.sol", set(), "bad", True), Finding("a.sol", {"reentrancy"}, "")]
    output = tmp_path / "reports"

    write_report(samples, findings, output)

    results = json.loads((output / "results.json").read_text())
    assert results["contracts"] == 2
    assert results["parse_failures"] == 1
    assert results["overall"]["precision"] == 1.0
    assert results["by_type"]["reentrancy"]["recall"] == 1.0
    with (output / "per_contract.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert [row["contract"] for row in rows] == ["a.sol", "b.sol"]
    assert rows[1]["parse_failed"] == "True"
    assert {path.name for path in output.iterdir()} == {"results.json", "per_contract.csv"}


@pytest.mark.parametrize("findings", [[], [Finding("b.sol", set(), "")], [Finding("a.sol", set(), "")] * 2, [Finding("a.sol", {"reentrancy"}, "", True)]])
def test_invalid_findings_do_not_write(tmp_path: Path, findings: list[Finding]) -> None:
    output = tmp_path / "reports"
    with pytest.raises(ValueError):
        write_report([Sample("a.sol", "", set())], findings, output)
    assert not output.exists()


def test_empty_report(tmp_path: Path) -> None:
    write_report([], [], tmp_path)
    results = json.loads((tmp_path / "results.json").read_text())
    assert results["contracts"] == 0
    assert results["overall"]["recall"] == 0.0
