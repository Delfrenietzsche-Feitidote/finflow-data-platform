from finflow.database.connection import get_connection


def transform_core_transactions_to_fact() -> int:
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
                ON CONFLICT (transaction_id) DO NOTHING
                RETURNING transaction_id;
                """
            )

            inserted_count = len(cursor.fetchall())

        conn.commit()

    return inserted_count