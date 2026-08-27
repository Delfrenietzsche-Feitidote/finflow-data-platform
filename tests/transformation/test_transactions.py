from decimal import Decimal

from finflow.database.connection import get_connection
from finflow.transformation.transactions import (
    transform_staging_transactions,
)


TEST_IDS = ["TXTEST001", "TXTEST002"]


def insert_test_staging_transactions():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
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
                VALUES
                (
                    'TXTEST001',
                    'CTEST001',
                    'ATEST001',
                    'MTEST001',
                    'THB',
                    'TEST_CARD',
                    '2026-08-10 10:00:00',
                    100.00,
                    2.50,
                    0.029
                ),
                (
                    'TXTEST002',
                    'CTEST002',
                    'ATEST002',
                    'MTEST002',
                    'THB',
                    'TEST_CARD',
                    '2026-08-10 11:00:00',
                    200.00,
                    5.00,
                    0.029
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
                    exchange_rate = EXCLUDED.exchange_rate;
                """
            )

        conn.commit()


def cleanup_test_data():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Delete child records first because core.transactions
            # has foreign keys to the dimension tables.
            cursor.execute(
                """
                DELETE FROM core.transactions
                WHERE transaction_id IN ('TXTEST001', 'TXTEST002');
                """
            )

            cursor.execute(
                """
                DELETE FROM core.accounts
                WHERE account_id IN ('ATEST001', 'ATEST002');
                """
            )

            cursor.execute(
                """
                DELETE FROM core.customers
                WHERE customer_id IN ('CTEST001', 'CTEST002');
                """
            )

            cursor.execute(
                """
                DELETE FROM core.merchants
                WHERE merchant_id IN ('MTEST001', 'MTEST002');
                """
            )

            cursor.execute(
                """
                DELETE FROM core.payment_methods
                WHERE payment_method_code = 'TEST_CARD';
                """
            )

            cursor.execute(
                """
                DELETE FROM staging.stg_transactions
                WHERE transaction_id IN ('TXTEST001', 'TXTEST002');
                """
            )

        conn.commit()



def test_staging_transactions_transform_to_core():
    cleanup_test_data()
    insert_test_staging_transactions()

    try:
        inserted = transform_staging_transactions()

        assert inserted == 2

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        transaction_id,
                        customer_id,
                        account_id,
                        merchant_id,
                        payment_method_code,
                        currency_code,
                        transaction_amount,
                        transaction_fee,
                        exchange_rate
                    FROM core.transactions
                    WHERE transaction_id IN ('TXTEST001', 'TXTEST002')
                    ORDER BY transaction_id;
                    """
                )

                rows = cursor.fetchall()

        assert len(rows) == 2

        assert rows[0][0] == "TXTEST001"
        assert rows[0][1] == "CTEST001"
        assert rows[0][2] == "ATEST001"
        assert rows[0][3] == "MTEST001"
        assert rows[0][4] == "TEST_CARD"
        assert rows[0][5] == "THB"
        assert rows[0][6] == Decimal("100.00")
        assert rows[0][7] == Decimal("2.50")
        assert rows[0][8] == Decimal("0.029000")

    finally:
        cleanup_test_data()


def test_transformation_is_idempotent():
    cleanup_test_data()
    insert_test_staging_transactions()

    try:
        first_inserted = transform_staging_transactions()
        second_inserted = transform_staging_transactions()

        assert first_inserted == 2
        assert second_inserted == 0

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM core.transactions
                    WHERE transaction_id IN ('TXTEST001', 'TXTEST002');
                    """
                )

                count = cursor.fetchone()[0]

        assert count == 2

    finally:
        cleanup_test_data()

def test_existing_core_transaction_is_updated_from_staging():
    cleanup_test_data()
    insert_test_staging_transactions()

    try:
        transform_staging_transactions()

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE staging.stg_transactions
                    SET transaction_amount = 150.00
                    WHERE transaction_id = 'TXTEST001';
                    """
                )
            conn.commit()

        updated = transform_staging_transactions()

        assert updated == 1

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT transaction_amount
                    FROM core.transactions
                    WHERE transaction_id = 'TXTEST001';
                    """
                )

                amount = cursor.fetchone()[0]

        assert amount == Decimal("150.00")

    finally:
        cleanup_test_data()