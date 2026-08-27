from datetime import date

from finflow.database.connection import get_connection


def transform_core_transactions_to_fact(
    transaction_date: date | None = None,
) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO analytics.fact_transactions (
                    transaction_id,
                    customer_id,
                    account_id,
                    merchant_id,
                    payment_method_code,
                    currency_code,
                    transaction_timestamp,
                    transaction_date,
                    transaction_amount,
                    transaction_fee,
                    exchange_rate
                )
                SELECT
                    transaction_id,
                    customer_id,
                    account_id,
                    merchant_id,
                    payment_method_code,
                    currency_code,
                    transaction_timestamp,
                    transaction_timestamp::DATE,
                    transaction_amount,
                    transaction_fee,
                    exchange_rate
                FROM core.transactions
                WHERE (
                    %s::date IS NULL
                    OR transaction_timestamp::date = %s::date
                )
                ON CONFLICT (transaction_id) DO UPDATE
                SET
                    customer_id = EXCLUDED.customer_id,
                    account_id = EXCLUDED.account_id,
                    merchant_id = EXCLUDED.merchant_id,
                    payment_method_code = EXCLUDED.payment_method_code,
                    currency_code = EXCLUDED.currency_code,
                    transaction_timestamp = EXCLUDED.transaction_timestamp,
                    transaction_date = EXCLUDED.transaction_date,
                    transaction_amount = EXCLUDED.transaction_amount,
                    transaction_fee = EXCLUDED.transaction_fee,
                    exchange_rate = EXCLUDED.exchange_rate
                WHERE
                    analytics.fact_transactions.customer_id IS DISTINCT FROM EXCLUDED.customer_id
                    OR analytics.fact_transactions.account_id IS DISTINCT FROM EXCLUDED.account_id
                    OR analytics.fact_transactions.merchant_id IS DISTINCT FROM EXCLUDED.merchant_id
                    OR analytics.fact_transactions.payment_method_code IS DISTINCT FROM EXCLUDED.payment_method_code
                    OR analytics.fact_transactions.currency_code IS DISTINCT FROM EXCLUDED.currency_code
                    OR analytics.fact_transactions.transaction_timestamp IS DISTINCT FROM EXCLUDED.transaction_timestamp
                    OR analytics.fact_transactions.transaction_date IS DISTINCT FROM EXCLUDED.transaction_date
                    OR analytics.fact_transactions.transaction_amount IS DISTINCT FROM EXCLUDED.transaction_amount
                    OR analytics.fact_transactions.transaction_fee IS DISTINCT FROM EXCLUDED.transaction_fee
                    OR analytics.fact_transactions.exchange_rate IS DISTINCT FROM EXCLUDED.exchange_rate
                RETURNING transaction_id;
                """,
                (transaction_date, transaction_date),
            )

            inserted_count = len(cursor.fetchall())

        conn.commit()

    return inserted_count