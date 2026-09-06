import hashlib
import os
from collections.abc import Iterable
from datetime import datetime, timezone

from google.cloud import bigquery

from finflow.ingestion.models.transaction import TransactionRecord


DATASET_ID = "raw"
TABLE_ID = "transactions"


def _build_job_id(transactions: list[TransactionRecord]) -> str:
    batch_key = "|".join(
        transaction.model_dump_json()
        for transaction in sorted(
            transactions,
            key=lambda transaction: transaction.transaction_id,
        )
    )

    digest = hashlib.sha256(
        batch_key.encode("utf-8")
    ).hexdigest()[:32]

    return f"finflow_transactions_{digest}"


def write_transactions_to_bigquery(
    transactions: Iterable[TransactionRecord],
) -> int:
    project_id = os.environ["FINFLOW_GCP_PROJECT_ID"]

    transactions = list(transactions)

    if not transactions:
        return 0

    ingested_at = datetime.now(timezone.utc).isoformat()

    records = []

    for transaction in transactions:
        record = transaction.model_dump(mode="json")
        record["created_at"] = ingested_at
        records.append(record)

    client = bigquery.Client(project=project_id)

    table_ref = f"{project_id}.{DATASET_ID}.{TABLE_ID}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_json(
        records,
        table_ref,
        job_config=job_config,
        job_id=_build_job_id(transactions),
    )

    job.result()

    return len(records)
