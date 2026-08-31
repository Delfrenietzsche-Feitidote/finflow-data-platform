from datetime import date

from finflow.database.connection import get_connection
from finflow.quality.pipeline_runs import (
    complete_pipeline_run,
    start_pipeline_run,
)


def cleanup_test_runs():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM metadata.pipeline_runs
                WHERE pipeline_name = 'finflow_transaction_pipeline'
                  AND batch_date = DATE '2026-08-25';
                """
            )

        conn.commit()


def test_pipeline_run_can_be_started_and_completed():
    cleanup_test_runs()

    try:
        run_id = start_pipeline_run(
            date(2026, 8, 25),
        )

        assert run_id > 0

        complete_pipeline_run(
            run_id,
            status = "SUCCESS",
            ingested_count=10,
            validated_count=10,
            core_count=10,
            fact_count=10,
            metrics_count=1,
        )

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        pipeline_name,
                        batch_date,
                        status,
                        ingested_count,
                        validated_count,
                        core_count,
                        fact_count,
                        metrics_count,
                        completed_at,
                        error_message
                    FROM metadata.pipeline_runs
                    WHERE run_id = %s;
                    """,
                    (run_id,),
                )

                row = cursor.fetchone()

        assert row[0] == "finflow_transaction_pipeline"
        assert row[1] == date(2026, 8, 25)
        assert row[2] == "SUCCESS"
        assert row[3] == 10
        assert row[4] == 10
        assert row[5] == 10
        assert row[6] == 10
        assert row[7] == 1
        assert row[8] is not None
        assert row[9] is None

    finally:
        cleanup_test_runs()

def test_failed_pipeline_run_defaults_counts_to_zero():
    cleanup_test_runs()

    try:
        run_id = start_pipeline_run(
            date(2026, 8, 25),
        )

        complete_pipeline_run(
            run_id,
            status="FAILED",
            error_message="transform_fact failed",
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
                        error_message
                    FROM metadata.pipeline_runs
                    WHERE run_id = %s;
                    """,
                    (run_id,),
                )

                row = cursor.fetchone()

        assert row[0] == "FAILED"
        assert row[1] == 0
        assert row[2] == 0
        assert row[3] == 0
        assert row[4] == 0
        assert row[5] == 0
        assert row[6] == "transform_fact failed"

    finally:
        cleanup_test_runs()