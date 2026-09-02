import json
from decimal import Decimal

from finflow.common.config import settings
from finflow.ingestion.models.transaction import TransactionRecord
from finflow.ingestion.pipeline import run_ingestion


def test_run_ingestion(tmp_path, monkeypatch):
    raw_path = tmp_path / "raw"
    rejected_path = tmp_path / "rejected"

    monkeypatch.setattr(
        settings.storage,
        "raw_path",
        f"{raw_path}/",
    )

    monkeypatch.setattr(
        settings.storage,
        "rejected_path",
        f"{rejected_path}/",
    )

    run_ingestion(10)

    output_file = (
        raw_path
        / "transactions"
        / str(settings.pipeline.batch_date)
        / "transactions.json"
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_run_ingestion_rejects_invalid_transactions(
    tmp_path,
    monkeypatch,
):
    raw_path = tmp_path / "raw"
    rejected_path = tmp_path / "rejected"

    monkeypatch.setattr(
        settings.storage,
        "raw_path",
        f"{raw_path}/",
    )

    monkeypatch.setattr(
        settings.storage,
        "rejected_path",
        f"{rejected_path}/",
    )

    transactions = [
        TransactionRecord(
            transaction_id="TX-DQ-VALID-20260824-001",
            customer_id="C001",
            account_id="A001",
            merchant_id="M001",
            currency_code="THB",
            payment_method_code="CARD",
            transaction_timestamp="2026-08-24T10:00:00",
            transaction_amount=Decimal("100.00"),
            transaction_fee=Decimal("2.50"),
            exchange_rate=Decimal("0.029"),
        ),
        TransactionRecord(
            transaction_id="TX-DQ-INVALID",
            customer_id="C002",
            account_id="A002",
            merchant_id="M002",
            currency_code="THB",
            payment_method_code="CARD",
            transaction_timestamp="2026-08-24T10:01:00",
            transaction_amount=Decimal("0"),
            transaction_fee=Decimal("-1.00"),
            exchange_rate=Decimal("0"),
        ),
    ]

    monkeypatch.setattr(
    "finflow.ingestion.pipeline.generate_transactions",
    lambda count, start_id=1, **kwargs: transactions,
    )

    monkeypatch.setattr(
    "finflow.ingestion.pipeline.write_transactions",
    lambda transactions: len(list(transactions)),
    )

    database_written = run_ingestion(2)

    assert database_written == 1

    raw_file = (
        raw_path
        / "transactions"
        / str(settings.pipeline.batch_date)
        / "transactions.json"
    )

    rejected_file = (
        rejected_path
        / "transactions"
        / str(settings.pipeline.batch_date)
        / "rejected.json"
    )

    assert raw_file.exists()
    assert rejected_file.exists()

    with rejected_file.open("r", encoding="utf-8") as file:
        rejected_data = json.load(file)

    assert len(rejected_data) == 1
    assert rejected_data[0]["transaction_id"] == "TX-DQ-INVALID"

    assert "transaction_amount must be greater than 0" in rejected_data[0]["errors"]
    assert "transaction_fee cannot be negative" in rejected_data[0]["errors"]
    assert "exchange_rate must be greater than 0" in rejected_data[0]["errors"]