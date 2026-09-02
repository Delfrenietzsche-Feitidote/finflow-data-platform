from decimal import Decimal

from finflow.database.connection import get_connection
from finflow.analytics.transactions import (
    transform_core_transactions_to_fact,
)


TEST_IDS = ["TXFACT001", "TXFACT002"]


def insert_test_core_transactions():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO core.customers (customer_id)
                VALUES
                    ('CFACT001'),
                    ('CFACT002')
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
                VALUES
                    ('AFACT001', 'CFACT001', 'PAYMENT'),
                    ('AFACT002', 'CFACT002', 'PAYMENT')
                ON CONFLICT (account_id) DO NOTHING;
                """
            )

            cursor.execute(
                """
                INSERT INTO core.merchants (merchant_id)
                VALUES
                    ('MFACT001'),
                    ('MFACT002')
                ON CONFLICT (merchant_id) DO NOTHING;
                """
            )

            cursor.execute(
                """
                INSERT INTO core.payment_methods (
                    payment_method_code
                )
                VALUES ('FACT_CARD')
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
                VALUES
                    (
                        'TXFACT001',
                        'CFACT001',
                        'AFACT001',
                        'MFACT001',
                        'FACT_CARD',
                        'THB',
                        '2026-08-20 10:00:00',
                        100.00,
                        2.50,
                        0.029
                    ),
                    (
                        'TXFACT002',
                        'CFACT002',
                        'AFACT002',
                        'MFACT002',
                        'FACT_CARD',
                        'THB',
                        '2026-08-20 11:30:00',
                        200.00,
                        5.00,
                        0.029
                    )
                ON CONFLICT (transaction_id) DO NOTHING;
                """
            )

        conn.commit()


def cleanup_test_data():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM analytics.fact_transactions
                WHERE transaction_id IN ('TXFACT001', 'TXFACT002');
                """
            )

            cursor.execute(
                """
                DELETE FROM core.transactions
                WHERE transaction_id IN ('TXFACT001', 'TXFACT002');
                """
            )

            cursor.execute(
                """
                DELETE FROM core.accounts
                WHERE account_id IN ('AFACT001', 'AFACT002');
                """
            )

            cursor.execute(
                """
                DELETE FROM core.customers
                WHERE customer_id IN ('CFACT001', 'CFACT002');
                """
            )

            cursor.execute(
                """
                DELETE FROM core.merchants
                WHERE merchant_id IN ('MFACT001', 'MFACT002');
                """
            )

            cursor.execute(
                """
                DELETE FROM core.payment_methods
                WHERE payment_method_code = 'FACT_CARD';
                """
            )

        conn.commit()


def test_core_transactions_transform_to_fact():
    cleanup_test_data()
    insert_test_core_transactions()

    try:
        inserted = transform_core_transactions_to_fact()

        assert inserted == 2

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        transaction_id,
                        transaction_date,
                        transaction_amount,
                        transaction_fee,
                        exchange_rate
                    FROM analytics.fact_transactions
                    WHERE transaction_id IN (
                        'TXFACT001',
                        'TXFACT002'
                    )
                    ORDER BY transaction_id;
                    """
                )

                rows = cursor.fetchall()

        assert len(rows) == 2

        assert rows[0][0] == "TXFACT001"
        assert str(rows[0][1]) == "2026-08-20"
        assert rows[0][2] == Decimal("100.00")
        assert rows[0][3] == Decimal("2.50")
        assert rows[0][4] == Decimal("0.029000")

    finally:
        cleanup_test_data()


def test_transformation_is_idempotent():
    cleanup_test_data()
    insert_test_core_transactions()

    try:
        first_inserted = transform_core_transactions_to_fact()
        second_inserted = transform_core_transactions_to_fact()

        assert first_inserted == 2
        assert second_inserted == 0

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM analytics.fact_transactions
                    WHERE transaction_id IN (
                        'TXFACT001',
                        'TXFACT002'
                    );
                    """
                )

                count = cursor.fetchone()[0]

        assert count == 2

    finally:
        cleanup_test_data()

def test_existing_fact_transaction_is_updated_from_core():
    cleanup_test_data()
    insert_test_core_transactions()

    try:
        transform_core_transactions_to_fact()

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE core.transactions
                    SET transaction_amount = 150.00
                    WHERE transaction_id = 'TXFACT001';
                    """
                )

            conn.commit()

        updated = transform_core_transactions_to_fact()

        assert updated == 1

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT transaction_amount
                    FROM analytics.fact_transactions
                    WHERE transaction_id = 'TXFACT001';
                    """
                )

                amount = cursor.fetchone()[0]

        assert amount == Decimal("150.00")

    finally:
        cleanup_test_data()