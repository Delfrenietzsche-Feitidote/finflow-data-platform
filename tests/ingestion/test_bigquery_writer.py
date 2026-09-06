from decimal import Decimal

from finflow.ingestion.loaders.bigquery_writer import (
    _build_job_id,
    write_transactions_to_bigquery,
)
from finflow.ingestion.models.transaction import TransactionRecord


def make_transaction(transaction_id: str) -> TransactionRecord:
    return TransactionRecord(
        transaction_id=transaction_id,
        customer_id="C001",
        account_id="A001",
        merchant_id="M001",
        currency_code="THB",
        payment_method_code="CARD",
        transaction_timestamp="2026-08-10T10:00:00",
        transaction_amount=Decimal("100.00"),
        transaction_fee=Decimal("2.50"),
        exchange_rate=Decimal("0.029"),
    )


def test_bigquery_writer_uses_deterministic_job_id(monkeypatch):
    captured = {}

    class MockJob:
        def result(self):
            return None

    class MockClient:
        def __init__(self, project):
            captured["project"] = project

        def load_table_from_json(
            self,
            records,
            table_ref,
            job_config,
            job_id,
        ):
            captured["records"] = records
            captured["table_ref"] = table_ref
            captured["job_id"] = job_id
            return MockJob()

    monkeypatch.setenv(
        "FINFLOW_GCP_PROJECT_ID",
        "test-project",
    )

    monkeypatch.setattr(
        "finflow.ingestion.loaders.bigquery_writer.bigquery.Client",
        MockClient,
    )

    transactions = [
        make_transaction("TX002"),
        make_transaction("TX001"),
    ]

    result = write_transactions_to_bigquery(transactions)

    assert result == 2
    assert captured["project"] == "test-project"
    assert captured["table_ref"] == "test-project.raw.transactions"
    assert captured["job_id"].startswith(
        "finflow_transactions_"
    )
    assert len(captured["job_id"]) == (
        len("finflow_transactions_") + 32
    )


def test_bigquery_job_id_is_independent_of_transaction_order():
    transactions_a = [
        make_transaction("TX001"),
        make_transaction("TX002"),
    ]

    transactions_b = [
        make_transaction("TX002"),
        make_transaction("TX001"),
    ]

    assert _build_job_id(transactions_a) == _build_job_id(
        transactions_b
    )


def test_bigquery_writer_returns_zero_for_empty_batch(
    monkeypatch,
):
    class FailingClient:
        def __init__(self, project):
            raise AssertionError(
                "BigQuery client should not be created"
            )

    monkeypatch.setenv(
        "FINFLOW_GCP_PROJECT_ID",
        "test-project",
    )

    monkeypatch.setattr(
        "finflow.ingestion.loaders.bigquery_writer.bigquery.Client",
        FailingClient,
    )

    assert write_transactions_to_bigquery([]) == 0
