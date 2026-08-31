from datetime import date
from typing import Any
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

def get_pipeline_run(run_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    run_id,
                    pipeline_name,
                    batch_date,
                    status,
                    ingested_count,
                    validated_count,
                    core_count,
                    fact_count,
                    metrics_count,
                    started_at,
                    completed_at,
                    error_message,
                    completed_at - started_at AS duration
                FROM metadata.pipeline_runs
                WHERE run_id = %s;
                """,
                (run_id,),
            )

            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "run_id": row[0],
        "pipeline_name": row[1],
        "batch_date": row[2],
        "status": row[3],
        "ingested_count": row[4],
        "validated_count": row[5],
        "core_count": row[6],
        "fact_count": row[7],
        "metrics_count": row[8],
        "started_at": row[9],
        "completed_at": row[10],
        "duration": row[11],
        "error_message": row[12],
    }

def get_pipeline_run_history(
    limit: int = 10,
) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    run_id,
                    pipeline_name,
                    batch_date,
                    status,
                    ingested_count,
                    validated_count,
                    core_count,
                    fact_count,
                    metrics_count,
                    started_at,
                    completed_at,
                    error_message,
                    completed_at - started_at AS duration
                FROM metadata.pipeline_runs
                WHERE pipeline_name = %s
                ORDER BY run_id DESC
                LIMIT %s;
                """,
                (PIPELINE_NAME, limit),
            )

            rows = cursor.fetchall()

    return [
        {
            "run_id": row[0],
            "pipeline_name": row[1],
            "batch_date": row[2],
            "status": row[3],
            "ingested_count": row[4],
            "validated_count": row[5],
            "core_count": row[6],
            "fact_count": row[7],
            "metrics_count": row[8],
            "started_at": row[9],
            "completed_at": row[10],
            "duration": row[11],
            "error_message": row[12],
        }
        for row in rows
    ]

def get_latest_pipeline_run() -> dict[str, Any] | None:
    runs = get_pipeline_run_history(limit=1)

    return runs[0] if runs else None
