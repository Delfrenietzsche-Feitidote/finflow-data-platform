import pytest

from finflow.common.retry import retry


def test_retry_succeeds_after_transient_failure(monkeypatch):
    attempts = 0
    sleep_calls = []

    def operation():
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise RuntimeError("temporary failure")

        return "success"

    monkeypatch.setattr(
        "finflow.common.retry.time.sleep",
        lambda delay: sleep_calls.append(delay),
    )

    result = retry(
        operation,
        max_attempts=3,
        base_delay=1.0,
    )

    assert result == "success"
    assert attempts == 3
    assert sleep_calls == [1.0, 2.0]


def test_retry_raises_after_max_attempts(monkeypatch):
    attempts = 0
    sleep_calls = []

    def operation():
        nonlocal attempts
        attempts += 1
        raise RuntimeError("persistent failure")

    monkeypatch.setattr(
        "finflow.common.retry.time.sleep",
        lambda delay: sleep_calls.append(delay),
    )

    with pytest.raises(RuntimeError, match="persistent failure"):
        retry(
            operation,
            max_attempts=3,
            base_delay=1.0,
        )

    assert attempts == 3
    assert sleep_calls == [1.0, 2.0]


def test_retry_does_not_retry_successful_operation(monkeypatch):
    attempts = 0
    sleep_calls = []

    def operation():
        nonlocal attempts
        attempts += 1
        return "success"

    monkeypatch.setattr(
        "finflow.common.retry.time.sleep",
        lambda delay: sleep_calls.append(delay),
    )

    result = retry(operation)

    assert result == "success"
    assert attempts == 1
    assert sleep_calls == []


def test_retry_rejects_invalid_max_attempts():
    with pytest.raises(ValueError, match="max_attempts must be at least 1"):
        retry(lambda: "success", max_attempts=0)
