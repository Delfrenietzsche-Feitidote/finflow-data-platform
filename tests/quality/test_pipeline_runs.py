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
            status="SUCCESS",
            ingested_count=10,
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
        assert row[6] == 1
        assert row[7] is not None
        assert row[8] is None

    finally:
        cleanup_test_runs()