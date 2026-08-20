from finflow.database.connection import get_connection


def transform_staging_transactions() -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO core.customers (customer_id)
                SELECT DISTINCT customer_id
                FROM staging.stg_transactions
                ON CONFLICT (customer_id) DO NOTHING;
                """
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
                ON CONFLICT (account_id) DO NOTHING;
                """
            )

            cursor.execute(
                """
                INSERT INTO core.merchants (merchant_id)
                SELECT DISTINCT merchant_id
                FROM staging.stg_transactions
                ON CONFLICT (merchant_id) DO NOTHING;
                """
            )

            cursor.execute(
                """
                INSERT INTO core.payment_methods (
                    payment_method_code
                )
                SELECT DISTINCT payment_method_code
                FROM staging.stg_transactions
                ON CONFLICT (payment_method_code) DO NOTHING;
                """
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
                ON CONFLICT (transaction_id) DO NOTHING;
                """
            )

            inserted_count = cursor.rowcount

        conn.commit()

    return inserted_count