from decimal import Decimal

from finflow.ingestion.models.transaction import TransactionRecord
from finflow.ingestion.validators.batch import validate_transactions


def create_transaction(transaction_id: str) -> TransactionRecord:
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


def test_batch_with_unique_transactions():
    transactions = [
        create_transaction("TX001"),
        create_transaction("TX002"),
        create_transaction("TX003"),
    ]

    valid, rejected = validate_transactions(transactions)

    assert len(valid) == 3
    assert len(rejected) == 0


def test_duplicate_transaction_is_rejected():
    transactions = [
        create_transaction("TX001"),
        create_transaction("TX002"),
        create_transaction("TX001"),
    ]

    valid, rejected = validate_transactions(transactions)

    assert len(valid) == 2
    assert len(rejected) == 1
    assert rejected[0]["transaction_id"] == "TX001"


def test_empty_batch():
    valid, rejected = validate_transactions([])

    assert valid == []
    assert rejected == []