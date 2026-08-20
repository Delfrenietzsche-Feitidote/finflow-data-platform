from collections.abc import Iterable

from finflow.database.connection import get_connection
from finflow.ingestion.models.transaction import TransactionRecord


INSERT_TRANSACTION = """
INSERT INTO transactions (
    transaction_id,
    customer_id,
    merchant_id,
    currency_code,
    payment_method_code,
    transaction_timestamp,
    transaction_amount,
    transaction_fee,
    exchange_rate
)
VALUES (
    %(transaction_id)s,
    %(customer_id)s,
    %(merchant_id)s,
    %(currency_code)s,
    %(payment_method_code)s,
    %(transaction_timestamp)s,
    %(transaction_amount)s,
    %(transaction_fee)s,
    %(exchange_rate)s
)
ON CONFLICT (transaction_id) DO NOTHING
"""


def write_transactions(transactions: Iterable[TransactionRecord]) -> int:
    records = [
        transaction.model_dump()
        for transaction in transactions
    ]

    if not records:
        return 0

    inserted_count = 0

    with get_connection() as conn:
        with conn.cursor() as cursor:
            for record in records:
                cursor.execute(INSERT_TRANSACTION, record)
                inserted_count += cursor.rowcount

        conn.commit()

    return inserted_count