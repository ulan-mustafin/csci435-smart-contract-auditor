import json
from pathlib import Path

import pytest

from smart_contract_auditor.benchmark import run_benchmark
from smart_contract_auditor.dataset import Sample, load_dataset


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = iter(responses)
        self.prompts: list[str] = []

    def ask(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return next(self.responses)


def test_benchmark_continues_after_parse_failure(tmp_path: Path) -> None:
    samples = [
        Sample("a.sol", "contract A {}", {"reentrancy"}),
        Sample("b.sol", "contract B {}", {"integer_overflow"}),
        Sample("c.sol", "contract C {}", set()),
    ]
    client = FakeClient([
        '{"vulnerabilities": [{"type": "reentrancy"}]}',
        "invalid",
        '{"vulnerabilities": []}',
    ])

    findings = run_benchmark(samples, "{code}", client, tmp_path)

    assert len(client.prompts) == 3
    assert [finding.parse_failed for finding in findings] == [False, True, False]
    results = json.loads((tmp_path / "results.json").read_text())
    assert results["overall"]["true_positives"] == 1
    assert results["overall"]["false_negatives"] == 1
    assert results["parse_failures"] == 1


@pytest.mark.parametrize("template, duplicate", [("missing placeholder", False), ("{code}", True)])
def test_invalid_inputs_do_not_call_client(tmp_path: Path, template: str, duplicate: bool) -> None:
    samples = [Sample("a.sol", "contract A {}", set())] * (2 if duplicate else 1)
    client = FakeClient([])
    output = tmp_path / "reports"

    with pytest.raises(ValueError):
        run_benchmark(samples, template, client, output)

    assert client.prompts == []
    assert not output.exists()


def test_client_failure_does_not_write_partial_report(tmp_path: Path) -> None:
    samples = [Sample("a.sol", "", set()), Sample("b.sol", "", set())]
    client = FakeClient(['{"vulnerabilities": []}'])
    output = tmp_path / "reports"

    with pytest.raises(StopIteration):
        run_benchmark(samples, "{code}", client, output)

    assert not output.exists()


def test_repository_benchmark(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    samples = load_dataset(root / "data/raw/labels.json", root)
    client = FakeClient([
        json.dumps({"vulnerabilities": [{"type": label} for label in sorted(sample.vulnerabilities)]})
        for sample in samples
    ])

    run_benchmark(samples, "{code}", client, tmp_path)

    results = json.loads((tmp_path / "results.json").read_text())
    assert results["contracts"] == 6
    assert results["overall"]["precision"] == 1.0
    assert results["overall"]["recall"] == 1.0
