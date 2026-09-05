from finflow.analytics.daily_metrics import build_daily_transaction_metrics
from finflow.analytics.transactions import transform_core_transactions_to_fact
from finflow.common.logging import get_logger
from finflow.ingestion.pipeline import run_ingestion
from finflow.transformation.transactions import transform_staging_transactions
from datetime import date
from finflow.quality.pipeline_runs import (
    complete_pipeline_run,
    start_pipeline_run,
)
from finflow.common.config import settings
from finflow.quality.transactions import validate_staging_transactions

logger = get_logger(__name__)

def start_pipeline_run_task(**context):
    execution_date = context["logical_date"].date()

    run_id = start_pipeline_run(execution_date)

    logger.info(
        "Pipeline run started | run_id=%s | batch_date=%s",
        run_id,
        execution_date,
    )

    return run_id


def complete_pipeline_run_task(**context):
    ti = context["ti"]

    run_id = ti.xcom_pull(
        task_ids="start_pipeline_run"
    )

    ingestion_result = ti.xcom_pull(
    task_ids="ingest_transactions"
    )

    if isinstance(ingestion_result, dict):
        ingested_count = ingestion_result.get("count", 0)
    else:
        ingested_count = ingestion_result or 0

    validated_count = ti.xcom_pull(
        task_ids="validate_staging"
    )

    core_count = ti.xcom_pull(
        task_ids="transform_core"
    )

    fact_count = ti.xcom_pull(
        task_ids="transform_fact"
    )

    metrics_count = ti.xcom_pull(
        task_ids="build_daily_metrics"
    )

    logger.info(
        "Completing pipeline run | "
        "run_id=%s | ingested=%s | validated=%s | "
        "core=%s | fact=%s | metrics=%s",
        run_id,
        ingested_count,
        validated_count,
        core_count,
        fact_count,
        metrics_count,
    )

    complete_pipeline_run(
        run_id,
        status="SUCCESS",
        ingested_count=ingested_count or 0,
        validated_count=validated_count or 0,
        core_count=core_count or 0,
        fact_count=fact_count or 0,
        metrics_count=metrics_count or 0,
    )


def fail_pipeline_run_task(**context):
    ti = context["ti"]

    run_id = ti.xcom_pull(
        task_ids="start_pipeline_run"
    )

    if run_id is None:
        logger.error(
            "Unable to mark pipeline run as FAILED: "
            "run_id not found"
        )
        return

    dag_run = context["dag_run"]

    failed_tasks = [
        task_instance
        for task_instance in dag_run.get_task_instances()
        if task_instance.state == "failed"
    ]

    if failed_tasks:
        failed_task_ids = ", ".join(
            task_instance.task_id
            for task_instance in failed_tasks
        )
        error_message = (
            f"Pipeline task(s) failed: {failed_task_ids}"
        )
    else:
        error_message = "Pipeline task failed"

    complete_pipeline_run(
        run_id,
        status="FAILED",
        error_message=error_message,
    )

    logger.error(
        "Pipeline run failed | run_id=%s | error=%s",
        run_id,
        error_message,
    )

def run_pipeline(
    count: int = 10,
    start_id: int = 1,
    batch_date: date | None = None,
) -> dict[str, int]:
    logger.info("FinFlow pipeline started")

    batch_date = batch_date or settings.pipeline.batch_date

    run_id = start_pipeline_run(batch_date)

    transaction_ids = [
        f"TX{batch_date:%Y%m%d}{i:06d}"
        for i in range(start_id, start_id + count)
    ]

    ingestion_result = {
        "database_written": 0,
        "bigquery_written": 0,
    }
    validated_count = 0
    core_written = 0
    fact_written = 0
    metrics_written = 0

    try:
        ingestion_result = run_ingestion(
            count=count,
            start_id=start_id,
            batch_date=batch_date,
        )

        database_written = ingestion_result["database_written"]
        bigquery_written = ingestion_result["bigquery_written"]

        validated_count = validate_staging_transactions(
            transaction_date=batch_date,
            transaction_ids=transaction_ids,
        )

        logger.info(
            "Data quality validation completed | validated=%s",
            validated_count,
        )

        core_written = transform_staging_transactions(
            transaction_date=batch_date,
        )

        logger.info(
            "Core transformation completed | inserted=%s",
            core_written,
        )

        fact_written = transform_core_transactions_to_fact(
            transaction_date=batch_date,
        )

        logger.info(
            "Fact transformation completed | inserted=%s",
            fact_written,
        )

        metrics_written = build_daily_transaction_metrics(
            transaction_date=batch_date,
        )

        logger.info(
            "Daily metrics transformation completed | affected=%s",
            metrics_written,
        )

        result = {
            "run_id": run_id,
            "ingested": database_written,
            "bigquery_written": bigquery_written,
            "validated": validated_count,
            "core": core_written,
            "fact": fact_written,
            "metrics": metrics_written,
        }

        complete_pipeline_run(
            run_id,
            status="SUCCESS",
            ingested_count=database_written,
            validated_count=validated_count,
            core_count=core_written,
            fact_count=fact_written,
            metrics_count=metrics_written,
        )
        logger.info(
            "FinFlow pipeline completed | %s",
            result,
        )

        return result

    except Exception as exc:
        complete_pipeline_run(
            run_id,
            status="FAILED",
            ingested_count=database_written,
            validated_count=validated_count,
            core_count=core_written,
            fact_count=fact_written,
            metrics_count=metrics_written,
            error_message=str(exc),
        )

        logger.exception("FinFlow pipeline failed")

        raise

def _normalize_batch_date(
    batch_date: date | str | None,
) -> date | None:
    if isinstance(batch_date, str):
        return date.fromisoformat(batch_date)

    return batch_date


def run_ingestion_task(
    count: int = 10,
    start_id: int = 1,
    batch_date: date | str | None = None,
) -> dict:
    batch_date = _normalize_batch_date(batch_date)
    batch_date = batch_date or settings.pipeline.batch_date

    transaction_ids = [
        f"TX{batch_date:%Y%m%d}{i:06d}"
        for i in range(start_id, start_id + count)
    ]

    ingestion_result = run_ingestion(
        count=count,
        start_id=start_id,
        batch_date=batch_date,
    )

    return {
        "count": ingestion_result["database_written"],
        "database_written": ingestion_result["database_written"],
        "bigquery_written": ingestion_result["bigquery_written"],
        "transaction_ids": transaction_ids,
    }


def run_core_transformation(
    batch_date: date | str | None = None,
) -> int:
    batch_date = _normalize_batch_date(batch_date)

    core_written = transform_staging_transactions(
        transaction_date=batch_date,
    )

    logger.info(
        "Core transformation completed | inserted=%s",
        core_written,
    )

    return core_written


def run_fact_transformation(
    batch_date: date | str | None = None,
) -> int:
    batch_date = _normalize_batch_date(batch_date)

    fact_written = transform_core_transactions_to_fact(
        transaction_date=batch_date,
    )

    logger.info(
        "Fact transformation completed | inserted=%s",
        fact_written,
    )

    return fact_written


def run_daily_metrics(
    batch_date: date | str | None = None,
) -> int:
    batch_date = _normalize_batch_date(batch_date)

    metrics_written = build_daily_transaction_metrics(
        transaction_date=batch_date,
    )

    logger.info(
        "Daily metrics transformation completed | affected=%s",
        metrics_written,
    )

    return metrics_written

def validate_staging_task(**context):
    ti = context["ti"]

    ingestion_result = ti.xcom_pull(
        task_ids="ingest_transactions"
    )

    transaction_ids = ingestion_result["transaction_ids"]

    execution_date = context["logical_date"].date()

    validated_count = validate_staging_transactions(
        transaction_date=execution_date,
        transaction_ids=transaction_ids,
    )

    logger.info(
        "Data quality validation completed | validated=%s | transactions=%s",
        validated_count,
        len(transaction_ids),
    )

    return validated_count