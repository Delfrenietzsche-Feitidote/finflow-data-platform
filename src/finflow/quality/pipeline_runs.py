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
        "duration": row[12],
        "error_message": row[11],
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
            "duration": row[12],
            "error_message": row[11],
        }
        for row in rows
    ]

def get_latest_pipeline_run() -> dict[str, Any] | None:
    runs = get_pipeline_run_history(limit=1)

    return runs[0] if runs else None

def get_pipeline_health(run_id: int) -> dict[str, Any] | None:
    run = get_pipeline_run(run_id)

    if run is None:
        return None

    ingested = run["ingested_count"]
    validated = run["validated_count"]
    core = run["core_count"]
    fact = run["fact_count"]

    rejected_count = max(ingested - validated, 0)

    validation_success_rate = (
        (validated / ingested) * 100
        if ingested > 0
        else 0.0
    )

    return {
        "run_id": run["run_id"],
        "pipeline_name": run["pipeline_name"],
        "batch_date": run["batch_date"],
        "status": run["status"],
        "started_at": run["started_at"],
        "completed_at": run["completed_at"],
        "duration": run["duration"],
        "ingested_count": ingested,
        "validated_count": validated,
        "core_count": core,
        "fact_count": fact,
        "metrics_count": run["metrics_count"],
        "rejected_count": rejected_count,
        "validation_success_rate": validation_success_rate,
        "error_message": run["error_message"],
    }