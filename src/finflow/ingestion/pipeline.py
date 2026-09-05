from datetime import date
from finflow.ingestion.loaders.bigquery_writer import (
    write_transactions_to_bigquery,
)
from finflow.common.config import settings
from finflow.common.logging import get_logger
from finflow.ingestion.loaders.raw_writer import write_raw_transactions
from finflow.ingestion.loaders.rejected_writer import write_rejected_transactions
from finflow.ingestion.sources.transactions import generate_transactions
from finflow.ingestion.validators.batch import validate_transactions
from finflow.database.writer import write_transactions
from finflow.quality.transactions import validate_staging_transactions


logger = get_logger(__name__)


def run_ingestion(
    count: int = 10,
    start_id: int = 1,
    batch_date: date | None = None,
) -> int:
    logger.info("Ingestion started")

    transactions = generate_transactions(
    count,
    start_id=start_id,
    batch_date=batch_date,
)

    logger.info("Transactions extracted: %s", len(transactions))

    valid_transactions, rejected_transactions = validate_transactions(
        transactions
    )

    logger.info(
        "Validation completed | valid=%s | rejected=%s",
        len(valid_transactions),
        len(rejected_transactions),
    )

    batch_date = batch_date or settings.pipeline.batch_date
    raw_path = settings.storage.raw_path
    rejected_path = settings.storage.rejected_path

    write_raw_transactions(
        valid_transactions,
        f"{raw_path}transactions/{batch_date}/transactions.json",
    )

    logger.info("Raw transactions written: %s", len(valid_transactions))

    database_written = write_transactions(valid_transactions)

    logger.info(
        "Database transactions written: %s",
        database_written,
    )

    bigquery_written = write_transactions_to_bigquery(valid_transactions)

    logger.info(
        "BigQuery transactions written: %s",
        bigquery_written,
    )

    if rejected_transactions:
        write_rejected_transactions(
            rejected_transactions,
            f"{rejected_path}transactions/{batch_date}/rejected.json",
        )

        logger.warning(
            "Rejected transactions written: %s",
            len(rejected_transactions),
        )

    logger.info(
        "Ingestion completed | batch_date=%s | database_written=%s | bigquery_written=%s",
        batch_date,
        database_written,
        bigquery_written,
    )

    return {
        "database_written": database_written,
        "bigquery_written": bigquery_written,
    }