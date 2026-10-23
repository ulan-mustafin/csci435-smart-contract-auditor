from smart_contract_auditor.metrics import calculate_metrics, calculate_metrics_by_type


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


def test_calculate_metrics_by_type() -> None:
    expected = {
        "reentrancy.sol": {"reentrancy"},
        "overflow.sol": {"integer_overflow"},
        "safe.sol": set(),
    }
    findings = {
        "reentrancy.sol": {"reentrancy"},
        "safe.sol": {"integer_overflow"},
    }

    result = calculate_metrics_by_type(expected, findings, ["reentrancy", "integer_overflow"])

    assert result["reentrancy"].precision == 1.0
    assert result["reentrancy"].recall == 1.0
    assert result["integer_overflow"].true_positives == 0
    assert result["integer_overflow"].false_positives == 1
    assert result["integer_overflow"].false_negatives == 1
