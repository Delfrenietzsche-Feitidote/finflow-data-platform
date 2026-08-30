from datetime import date

from finflow.database.connection import get_connection


PIPELINE_NAME = "finflow_transaction_pipeline"


def start_pipeline_run(
    batch_date: date | None = None,
) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO metadata.pipeline_runs (
                    pipeline_name,
                    batch_date,
                    status
                )
                VALUES (%s, %s, 'RUNNING')
                RETURNING run_id;
                """,
                (PIPELINE_NAME, batch_date),
            )

            run_id = cursor.fetchone()[0]

        conn.commit()

    return run_id


def complete_pipeline_run(
    run_id: int,
    *,
    status: str,
    ingested_count: int = 0,
    validated_count: int = 0,
    core_count: int = 0,
    fact_count: int = 0,
    metrics_count: int = 0,
    error_message: str | None = None,
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE metadata.pipeline_runs
                SET
                    status = %s,
                    ingested_count = %s,
                    validated_count = %s,
                    core_count = %s,
                    fact_count = %s,
                    metrics_count = %s,
                    completed_at = CURRENT_TIMESTAMP,
                    error_message = %s
                WHERE run_id = %s;
                """,
                (
                    status,
                    ingested_count,
                    validated_count,
                    core_count,
                    fact_count,
                    metrics_count,
                    error_message,
                    run_id,
                ),
            )

        conn.commit()