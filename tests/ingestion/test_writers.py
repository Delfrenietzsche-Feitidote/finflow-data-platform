from decimal import Decimal
import json

from finflow.ingestion.loaders.raw_writer import write_raw_transactions
from finflow.ingestion.loaders.rejected_writer import (
    write_rejected_transactions,
)
from finflow.ingestion.models.transaction import TransactionRecord


def test_raw_writer(tmp_path):
    transactions = [
        TransactionRecord(
            transaction_id="TX001",
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
    ]

    output_file = tmp_path / "raw" / "transactions.json"

    write_raw_transactions(
        transactions,
        str(output_file),
    )

    assert output_file.exists()

    with output_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert len(data) == 1
    assert data[0]["transaction_id"] == "TX001"


def test_rejected_writer(tmp_path):
    rejected = [
        {
            "transaction_id": "TX002",
            "errors": [
                "transaction_amount must be greater than 0",
            ],
        }
    ]

    output_file = tmp_path / "rejected" / "rejected.json"

    write_rejected_transactions(
        rejected,
        str(output_file),
    )

    assert output_file.exists()

    with output_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert len(data) == 1
    assert data[0]["transaction_id"] == "TX002"
    assert len(data[0]["errors"]) == 1