from collections.abc import Iterable

from finflow.database.connection import get_connection
from finflow.ingestion.models.transaction import TransactionRecord

INSERT_TRANSACTION = """
INSERT INTO staging.stg_transactions (
    transaction_id,
    customer_id,
    account_id,
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
    %(account_id)s,
    %(merchant_id)s,
    %(currency_code)s,
    %(payment_method_code)s,
    %(transaction_timestamp)s,
    %(transaction_amount)s,
    %(transaction_fee)s,
    %(exchange_rate)s
)
ON CONFLICT (transaction_id) DO NOTHING
RETURNING transaction_id
"""


def write_transactions(
    transactions: Iterable[TransactionRecord],
) -> list[str]:
    records = [transaction.model_dump() for transaction in transactions]

    if not records:
        return []

    inserted_ids = []

    with get_connection() as conn:
        with conn.cursor() as cursor:
            for record in records:
                cursor.execute(INSERT_TRANSACTION, record)

                row = cursor.fetchone()

                if row:
                    inserted_ids.append(row[0])

        conn.commit()

    return inserted_ids
