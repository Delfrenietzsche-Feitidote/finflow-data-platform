from datetime import datetime
from decimal import Decimal

from finflow.ingestion.models.transaction import TransactionRecord


def generate_transactions(
    count: int = 10,
    start_id: int = 1,
) -> list[TransactionRecord]:
    transactions = []

    for i in range(start_id, start_id + count):
        transaction = TransactionRecord(
            transaction_id=f"TX{i:06d}",
            customer_id=f"C{i:04d}",
            account_id=f"A{i:04d}",
            merchant_id=f"M{i:04d}",
            currency_code="THB",
            payment_method_code="CARD",
            transaction_timestamp=datetime.now(),
            transaction_amount=Decimal("100.00"),
            transaction_fee=Decimal("2.50"),
            exchange_rate=Decimal("0.029"),
        )

        transactions.append(transaction)

    return transactions