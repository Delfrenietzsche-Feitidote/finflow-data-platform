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


def run_pipeline(
    count: int = 10,
    start_id: int = 1,
    batch_date: date | None = None,
) -> dict[str, int]:
    logger.info("FinFlow pipeline started")

    batch_date = batch_date or settings.pipeline.batch_date

    run_id = start_pipeline_run(batch_date)

    try:
        ingestion_result = run_ingestion(
            count=count,
            start_id=start_id,
            batch_date=batch_date,
        )

        validated_count = validate_staging_transactions(
            transaction_date=batch_date,
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
            "ingested": ingestion_result,
            "core": core_written,
            "fact": fact_written,
            "metrics": metrics_written,
        }

        complete_pipeline_run(
            run_id,
            status="SUCCESS",
            ingested_count=ingestion_result,
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
) -> int:
    batch_date = _normalize_batch_date(batch_date)

    return run_ingestion(
        count=count,
        start_id=start_id,
        batch_date=batch_date,
    )


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
    execution_date = context["logical_date"].date()

    validated_count = validate_staging_transactions(
        transaction_date=execution_date,
    )

    logger.info(
        "Data quality validation completed | validated=%s",
        validated_count,
    )

    return validated_count