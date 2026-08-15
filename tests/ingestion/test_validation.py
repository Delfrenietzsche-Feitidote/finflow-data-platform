from decimal import Decimal

from finflow.ingestion.models.transaction import TransactionRecord
from finflow.ingestion.validators.transaction import validate_transaction


def create_transaction(
    amount="100.00",
    fee="2.50",
    exchange_rate="0.029",
):
    return TransactionRecord(
        transaction_id="TX001",
        customer_id="C001",
        merchant_id="M001",
        currency_code="THB",
        payment_method_code="CARD",
        transaction_timestamp="2026-08-10T10:00:00",
        transaction_amount=Decimal(amount),
        transaction_fee=Decimal(fee),
        exchange_rate=Decimal(exchange_rate),
    )


def test_valid_transaction_has_no_errors():
    transaction = create_transaction()

    errors = validate_transaction(transaction)

    assert errors == []


def test_negative_amount_is_rejected():
    transaction = create_transaction(amount="-100.00")

    errors = validate_transaction(transaction)

    assert "transaction_amount must be greater than 0" in errors


def test_negative_fee_is_rejected():
    transaction = create_transaction(fee="-5.00")

    errors = validate_transaction(transaction)

    assert "transaction_fee cannot be negative" in errors


def test_invalid_exchange_rate_is_rejected():
    transaction = create_transaction(exchange_rate="0")

    errors = validate_transaction(transaction)

    assert "exchange_rate must be greater than 0" in errors