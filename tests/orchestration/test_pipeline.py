from unittest import result

from finflow.database.connection import get_connection
from finflow.orchestration.pipeline import run_pipeline


TEST_START_ID = 9001
TEST_COUNT = 3


def cleanup_test_data():
    transaction_ids = [
        f"TX{i:06d}"
        for i in range(
            TEST_START_ID,
            TEST_START_ID + TEST_COUNT,
        )
    ]

    with get_connection() as conn:
        with conn.cursor() as cursor:
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
                DELETE FROM core.accounts
                WHERE account_id = ANY(%s);
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
                DELETE FROM core.customers
                WHERE customer_id = ANY(%s);
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
                DELETE FROM core.merchants
                WHERE merchant_id = ANY(%s);
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

        conn.commit()


def test_run_pipeline():
    cleanup_test_data()

    try:
        result = run_pipeline(
            count=TEST_COUNT,
            start_id=TEST_START_ID,
        )

        assert result["ingested"] == TEST_COUNT
        assert result["core"] == TEST_COUNT
        assert result["fact"] == TEST_COUNT
        assert result["metrics"] >= 1

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
                            f"TX{i:06d}"
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
        )

        second_result = run_pipeline(
            count=TEST_COUNT,
            start_id=TEST_START_ID,
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
                            f"TX{i:06d}"
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