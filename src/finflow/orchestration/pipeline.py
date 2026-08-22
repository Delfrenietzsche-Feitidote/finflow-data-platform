from finflow.analytics.daily_metrics import build_daily_transaction_metrics
from finflow.analytics.transactions import transform_core_transactions_to_fact
from finflow.common.logging import get_logger
from finflow.ingestion.pipeline import run_ingestion
from finflow.transformation.transactions import transform_staging_transactions


logger = get_logger(__name__)


def run_pipeline(
    count: int = 10,
    start_id: int = 1,
) -> dict[str, int]:
    logger.info("FinFlow pipeline started")

    run_ingestion(
        count=count,
        start_id=start_id,
    )

    core_written = transform_staging_transactions()

    logger.info(
        "Core transformation completed | inserted=%s",
        core_written,
    )

    fact_written = transform_core_transactions_to_fact()

    logger.info(
        "Fact transformation completed | inserted=%s",
        fact_written,
    )

    metrics_written = build_daily_transaction_metrics()

    logger.info(
        "Daily metrics transformation completed | affected=%s",
        metrics_written,
    )

    result = {
        "core": core_written,
        "fact": fact_written,
        "metrics": metrics_written,
    }

    logger.info(
        "FinFlow pipeline completed | %s",
        result,
    )

    return result
