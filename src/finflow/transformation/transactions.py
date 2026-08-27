from datetime import date

from psycopg import cursor

from finflow.database.connection import get_connection


def transform_staging_transactions(
    transaction_date: date | None = None,
) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO core.customers (customer_id)
                SELECT DISTINCT customer_id
                FROM staging.stg_transactions
                WHERE (
                    %s::date IS NULL
                    OR transaction_timestamp::date = %s::date
                )
                ON CONFLICT (customer_id) DO NOTHING;
                """,
                (transaction_date, transaction_date),
            )

            cursor.execute(
                """
                INSERT INTO core.accounts (
                    account_id,
                    customer_id,
                    account_type
                )
                SELECT DISTINCT
                    account_id,
                    customer_id,
                    'PAYMENT'
                FROM staging.stg_transactions
                WHERE (
                    %s::date IS NULL
                    OR transaction_timestamp::date = %s::date
                )
                ON CONFLICT (account_id) DO NOTHING;
                """,
                (transaction_date, transaction_date),
            )

            cursor.execute(
                """
                INSERT INTO core.merchants (merchant_id)
                SELECT DISTINCT merchant_id
                FROM staging.stg_transactions
                WHERE (
                    %s::date IS NULL
                    OR transaction_timestamp::date = %s::date
                )
                ON CONFLICT (merchant_id) DO NOTHING;
                """,
                (transaction_date, transaction_date),
            )
            cursor.execute(
                """
                INSERT INTO core.payment_methods (
                    payment_method_code
                )
                SELECT DISTINCT payment_method_code
                FROM staging.stg_transactions
                WHERE (
                    %s::date IS NULL
                    OR transaction_timestamp::date = %s::date
                )
                ON CONFLICT (payment_method_code) DO NOTHING;
                """,
                (transaction_date, transaction_date),
            )

            cursor.execute(
                """
                INSERT INTO core.transactions (
                    transaction_id,
                    customer_id,
                    account_id,
                    merchant_id,
                    payment_method_code,
                    currency_code,
                    transaction_timestamp,
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
                    transaction_amount,
                    transaction_fee,
                    exchange_rate
                FROM staging.stg_transactions
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
                    transaction_amount = EXCLUDED.transaction_amount,
                    transaction_fee = EXCLUDED.transaction_fee,
                    exchange_rate = EXCLUDED.exchange_rate
                WHERE
                    core.transactions.customer_id IS DISTINCT FROM EXCLUDED.customer_id
                    OR core.transactions.account_id IS DISTINCT FROM EXCLUDED.account_id
                    OR core.transactions.merchant_id IS DISTINCT FROM EXCLUDED.merchant_id
                    OR core.transactions.payment_method_code IS DISTINCT FROM EXCLUDED.payment_method_code
                    OR core.transactions.currency_code IS DISTINCT FROM EXCLUDED.currency_code
                    OR core.transactions.transaction_timestamp IS DISTINCT FROM EXCLUDED.transaction_timestamp
                    OR core.transactions.transaction_amount IS DISTINCT FROM EXCLUDED.transaction_amount
                    OR core.transactions.transaction_fee IS DISTINCT FROM EXCLUDED.transaction_fee
                    OR core.transactions.exchange_rate IS DISTINCT FROM EXCLUDED.exchange_rate
                RETURNING transaction_id;
                """,
                (transaction_date, transaction_date),
            )

            inserted_count = len(cursor.fetchall())

            conn.commit()

    return inserted_count