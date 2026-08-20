from decimal import Decimal

import pytest
from pydantic import ValidationError

from finflow.ingestion.models.transaction import TransactionRecord


def test_valid_transaction():
    transaction = TransactionRecord(
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

    assert transaction.transaction_id == "TX001"
    assert transaction.account_id == "A001"
    assert transaction.transaction_amount == Decimal("100.00")


def test_invalid_transaction_timestamp():
    with pytest.raises(ValidationError):
        TransactionRecord(
            transaction_id="TX001",
            customer_id="C001",
            account_id="A001",
            merchant_id="M001",
            currency_code="THB",
            payment_method_code="CARD",
            transaction_timestamp="invalid-date",
            transaction_amount=Decimal("100.00"),
            transaction_fee=Decimal("2.50"),
            exchange_rate=Decimal("0.029"),
        )