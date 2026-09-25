from smart_contract_auditor.metrics import calculate_metrics


def test_calculate_metrics_for_partial_findings() -> None:
    expected = {
        "reentrancy.sol": {"reentrancy"},
        "overflow.sol": {"integer_overflow"},
    }
    findings = {
        "reentrancy.sol": {"reentrancy", "integer_overflow"},
    }

    result = calculate_metrics(expected, findings)

    assert result.true_positives == 1
    assert result.false_positives == 1
    assert result.false_negatives == 1
    assert result.precision == 0.5
    assert result.recall == 0.5


def test_calculate_metrics_for_no_findings() -> None:
    result = calculate_metrics({"reentrancy.sol": {"reentrancy"}}, {})

    assert result.precision == 0.0
    assert result.recall == 0.0
