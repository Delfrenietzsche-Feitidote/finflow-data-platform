from finflow.common.config import settings
from finflow.common.logging import get_logger
from finflow.ingestion.loaders.raw_writer import write_raw_transactions
from finflow.ingestion.loaders.rejected_writer import write_rejected_transactions
from finflow.ingestion.sources.transactions import generate_transactions
from finflow.ingestion.validators.batch import validate_transactions
from finflow.database.writer import write_transactions


logger = get_logger(__name__)


def run_ingestion(
    count: int = 10,
    start_id: int = 1,
) -> None:
    logger.info("Ingestion started")

    transactions = generate_transactions(count, start_id=start_id)

    logger.info("Transactions extracted: %s", len(transactions))

    valid_transactions, rejected_transactions = validate_transactions(
        transactions
    )

    logger.info(
        "Validation completed | valid=%s | rejected=%s",
        len(valid_transactions),
        len(rejected_transactions),
    )

    batch_date = settings.pipeline.batch_date
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


    if rejected_transactions:
        write_rejected_transactions(
            rejected_transactions,
            f"{rejected_path}transactions/{batch_date}/rejected.json",
        )

        logger.warning(
            "Rejected transactions written: %s",
            len(rejected_transactions),
        )

    
    logger.info("Ingestion completed")

    return database_written