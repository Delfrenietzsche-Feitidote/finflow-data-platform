from decimal import Decimal

from finflow.analytics.daily_metrics import (
    build_daily_transaction_metrics,
)
from finflow.database.connection import get_connection


TEST_DATE = "2099-01-01"


def insert_test_fact_transactions():
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
                VALUES
                (
                    'TXMETRIC001',
                    'CMETRIC001',
                    'AMETRIC001',
                    'MMETRIC001',
                    'CARD',
                    'THB',
                    '2099-01-01 10:00:00',
                    '2099-01-01',
                    100.00,
                    2.50,
                    0.029
                ),
                (
                    'TXMETRIC002',
                    'CMETRIC002',
                    'AMETRIC002',
                    'MMETRIC002',
                    'CARD',
                    'THB',
                    '2099-01-01 11:00:00',
                    '2099-01-01',
                    200.00,
                    5.00,
                    0.029
                ),
                (
                    'TXMETRIC003',
                    'CMETRIC003',
                    'AMETRIC003',
                    'MMETRIC003',
                    'CARD',
                    'THB',
                    '2099-01-01 12:00:00',
                    '2099-01-01',
                    300.00,
                    7.50,
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
                DELETE FROM analytics.daily_transaction_metrics
                WHERE transaction_date = %s;
                """,
                (TEST_DATE,),
            )

            cursor.execute(
                """
                DELETE FROM analytics.fact_transactions
                WHERE transaction_id IN (
                    'TXMETRIC001',
                    'TXMETRIC002',
                    'TXMETRIC003'
                );
                """
            )

        conn.commit()


def test_daily_transaction_metrics():
    cleanup_test_data()
    insert_test_fact_transactions()

    try:
        inserted = build_daily_transaction_metrics(
                transaction_date=TEST_DATE
            )

        assert inserted == 1

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        transaction_date,
                        transaction_count,
                        total_transaction_amount,
                        total_transaction_fee,
                        average_transaction_amount,
                        average_transaction_fee
                    FROM analytics.daily_transaction_metrics
                    WHERE transaction_date = %s;
                    """,
                    (TEST_DATE,),
                )

                row = cursor.fetchone()

        assert row is not None

        assert row[0].isoformat() == TEST_DATE
        assert row[1] == 3
        assert row[2] == Decimal("600.00")
        assert row[3] == Decimal("15.00")
        assert row[4] == Decimal("200.00")
        assert row[5] == Decimal("5.00")

    finally:
        cleanup_test_data()


def test_daily_transaction_metrics_is_idempotent():
    cleanup_test_data()
    insert_test_fact_transactions()

    try:
        first_inserted = build_daily_transaction_metrics(
            transaction_date=TEST_DATE
        )
        second_inserted = build_daily_transaction_metrics(
            transaction_date=TEST_DATE
        )

        assert first_inserted == 1
        assert second_inserted == 0

    finally:
        cleanup_test_data()

def test_daily_transaction_metrics_updates_existing_date():
    cleanup_test_data()
    insert_test_fact_transactions()

    try:
        first_inserted = build_daily_transaction_metrics(
            transaction_date=TEST_DATE
        )
        

        assert first_inserted == 1

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
                    VALUES (
                        'TXMETRIC004',
                        'CMETRIC004',
                        'AMETRIC004',
                        'MMETRIC004',
                        'CARD',
                        'THB',
                        '2099-01-01 13:00:00',
                        '2099-01-01',
                        400.00,
                        10.00,
                        0.029
                    )
                    ON CONFLICT (transaction_id) DO NOTHING;
                    """
                )

            conn.commit()

        updated = build_daily_transaction_metrics(
                    transaction_date=TEST_DATE
            )

        assert updated == 1

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        transaction_count,
                        total_transaction_amount,
                        total_transaction_fee,
                        average_transaction_amount,
                        average_transaction_fee
                    FROM analytics.daily_transaction_metrics
                    WHERE transaction_date = %s;
                    """,
                    (TEST_DATE,),
                )

                row = cursor.fetchone()

        assert row is not None

        assert row[0] == 4
        assert row[1] == Decimal("1000.00")
        assert row[2] == Decimal("25.00")
        assert row[3] == Decimal("250.00")
        assert row[4] == Decimal("6.25")

    finally:
        cleanup_test_data()

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM analytics.fact_transactions
                    WHERE transaction_id = 'TXMETRIC004';
                    """
                )
            conn.commit()