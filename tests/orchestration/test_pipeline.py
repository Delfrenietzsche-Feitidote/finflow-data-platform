import pytest

from finflow.database.connection import get_connection
from finflow.orchestration.pipeline import run_pipeline
from finflow.quality.pipeline_runs import get_pipeline_health
from finflow.quality.transactions import DataQualityError
from datetime import date


TEST_START_ID = 9001
TEST_COUNT = 3
TEST_BATCH_DATE = date(2026, 8, 25)


def transaction_ids():
    return [
        f"TX20260825{i:06d}"
        for i in range(
            TEST_START_ID,
            TEST_START_ID + TEST_COUNT,
        )
    ]

def cleanup_test_data():
    transaction_ids = [
        f"TX20260825{i:06d}"
        for i in range(
            TEST_START_ID,
            TEST_START_ID + TEST_COUNT,
        )
    ]

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM metadata.pipeline_runs
                WHERE pipeline_name = 'finflow_transaction_pipeline'
                AND batch_date = %s;
                """,
                (TEST_BATCH_DATE,),
            )

            cursor.execute(
                """
                DELETE FROM core.transactions
                WHERE transaction_id = 'TXDQFAIL001';
                """
            )

            cursor.execute(
                """
                DELETE FROM staging.stg_transactions
                WHERE transaction_id = 'TXDQFAIL001';
                """
            )

            cursor.execute(
                """
                DELETE FROM analytics.daily_transaction_metrics
                WHERE transaction_date IN (
                    SELECT DISTINCT transaction_date
                    FROM analytics.fact_transactions
                    WHERE transaction_id = ANY(%s)
                );
                """,
                (transaction_ids,),
            )

            cursor.execute(
                """
                DELETE FROM analytics.fact_transactions
                WHERE transaction_id = ANY(%s);
                """,
                (transaction_ids,),
            )

            cursor.execute(
                """
                DELETE FROM core.transactions
                WHERE transaction_id = ANY(%s);
                """,
                (transaction_ids,),
            )

            cursor.execute(
                """
                DELETE FROM staging.stg_transactions
                WHERE transaction_id = ANY(%s);
                """,
                (transaction_ids,),
            )

            cursor.execute(
                """
                DELETE FROM core.accounts a
                WHERE a.account_id = ANY(%s)
                AND NOT EXISTS (
                    SELECT 1
                    FROM core.transactions t
                    WHERE t.account_id = a.account_id
                );
                """,
                (
                    [
                        f"A{i:04d}"
                        for i in range(
                            TEST_START_ID,
                            TEST_START_ID + TEST_COUNT,
                        )
                    ],
                ),
            )

            cursor.execute(
                """
                DELETE FROM core.customers c
                WHERE c.customer_id = ANY(%s)
                AND NOT EXISTS (
                    SELECT 1
                    FROM core.transactions t
                    WHERE t.customer_id = c.customer_id
                );
                """,
                (
                    [
                        f"C{i:04d}"
                        for i in range(
                            TEST_START_ID,
                            TEST_START_ID + TEST_COUNT,
                        )
                    ],
                ),
            )

            cursor.execute(
                """
                DELETE FROM core.merchants m
                WHERE m.merchant_id = ANY(%s)
                AND NOT EXISTS (
                    SELECT 1
                    FROM core.transactions t
                    WHERE t.merchant_id = m.merchant_id
                );
                """,
                (
                    [
                        f"M{i:04d}"
                        for i in range(
                            TEST_START_ID,
                            TEST_START_ID + TEST_COUNT,
                        )
                    ],
                ),
            )

            cursor.execute(
                """
                DELETE FROM metadata.pipeline_runs
                WHERE pipeline_name = 'finflow_transaction_pipeline'
                AND batch_date = %s;
                """,
                (TEST_BATCH_DATE,),
            )

        conn.commit()


def test_run_pipeline():
    cleanup_test_data()

    try:
        result = run_pipeline(
            count=TEST_COUNT,
            start_id=TEST_START_ID,
            batch_date=TEST_BATCH_DATE,
        )

        assert result["run_id"] > 0
        assert result["ingested"] == TEST_COUNT
        assert result["validated"] >= TEST_COUNT
        assert result["core"] == TEST_COUNT
        assert result["fact"] == TEST_COUNT
        assert result["metrics"] >= 1

        health = get_pipeline_health(result["run_id"])

        assert health is not None
        assert health["status"] == "SUCCESS"
        assert health["batch_date"] == TEST_BATCH_DATE
        assert health["ingested_count"] == TEST_COUNT
        assert health["validated_count"] >= TEST_COUNT
        assert health["core_count"] == TEST_COUNT
        assert health["fact_count"] == TEST_COUNT
        assert health["metrics_count"] >= 1
        assert health["rejected_count"] == 0
        assert health["validation_success_rate"] == 100.0
        assert health["completed_at"] is not None
        assert health["duration"] is not None
        assert health["error_message"] is None

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM analytics.fact_transactions
                    WHERE transaction_id = ANY(%s);
                    """,
                    (
                        [
                            f"TX20260825{i:06d}"
                            for i in range(
                                TEST_START_ID,
                                TEST_START_ID + TEST_COUNT,
                            )
                        ],
                    ),
                )

                fact_count = cursor.fetchone()[0]

        assert fact_count == TEST_COUNT

    finally:
        cleanup_test_data()

def test_run_pipeline_is_idempotent():
    cleanup_test_data()

    try:
        first_result = run_pipeline(
            count=TEST_COUNT,
            start_id=TEST_START_ID,
            batch_date=TEST_BATCH_DATE,
        )

        second_result = run_pipeline(
            count=TEST_COUNT,
            start_id=TEST_START_ID,
            batch_date=TEST_BATCH_DATE,
        )

        assert first_result["ingested"] == TEST_COUNT
        assert first_result["core"] == TEST_COUNT
        assert first_result["fact"] == TEST_COUNT

        assert second_result["ingested"] == 0
        assert second_result["core"] == 0
        assert second_result["fact"] == 0

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM analytics.fact_transactions
                    WHERE transaction_id = ANY(%s);
                    """,
                    (
                        [
                            f"TX20260825{i:06d}"
                            for i in range(
                                TEST_START_ID,
                                TEST_START_ID + TEST_COUNT,
                            )
                        ],
                    ),
                )

                fact_count = cursor.fetchone()[0]

        assert fact_count == TEST_COUNT

    finally:
        cleanup_test_data()


def test_run_pipeline_stops_on_data_quality_failure():
    cleanup_test_data()

    try:
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
                    VALUES (
                        'TXDQFAIL001',
                        'CDQFAIL001',
                        'ADQFAIL001',
                        'MDQFAIL001',
                        'THB',
                        'CARD',
                        '2026-08-25 10:00:00',
                        -100.00,
                        2.50,
                        0.029
                    );
                    """
                )

            conn.commit()

        with pytest.raises(DataQualityError):
            run_pipeline(
                count=0,
                start_id=9001,
                batch_date=TEST_BATCH_DATE,
            )

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM core.transactions
                    WHERE transaction_id = 'TXDQFAIL001';
                    """
                )

                core_count = cursor.fetchone()[0]

        assert core_count == 0

    finally:
        cleanup_test_data()

def test_run_pipeline_records_pipeline_run_metadata():
    cleanup_test_data()

    try:
        result = run_pipeline(
            count=TEST_COUNT,
            start_id=TEST_START_ID,
            batch_date=TEST_BATCH_DATE,
        )

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        status,
                        ingested_count,
                        validated_count,
                        core_count,
                        fact_count,
                        metrics_count,
                        completed_at,
                        error_message
                    FROM metadata.pipeline_runs
                    WHERE pipeline_name = 'finflow_transaction_pipeline'
                      AND batch_date = %s
                    ORDER BY run_id DESC
                    LIMIT 1;
                    """,
                    (TEST_BATCH_DATE,),
                )

                row = cursor.fetchone()

        assert row is not None
        assert row[0] == "SUCCESS"
        assert row[1] == result["ingested"]
        assert row[2] == result["validated"]
        assert row[3] == result["core"]
        assert row[4] == result["fact"]
        assert row[5] == result["metrics"]
        assert row[6] is not None
        assert row[7] is None

    finally:
        cleanup_test_data()