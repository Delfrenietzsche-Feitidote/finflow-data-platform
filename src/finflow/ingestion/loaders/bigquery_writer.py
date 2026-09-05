import os
from collections.abc import Iterable
from datetime import datetime, timezone

from google.cloud import bigquery

from finflow.ingestion.models.transaction import TransactionRecord


DATASET_ID = "raw"
TABLE_ID = "transactions"


def write_transactions_to_bigquery(
    transactions: Iterable[TransactionRecord],
) -> int:
    project_id = os.environ["FINFLOW_GCP_PROJECT_ID"]

    ingested_at = datetime.now(timezone.utc).isoformat()

    records = []

    for transaction in transactions:
        record = transaction.model_dump(mode="json")
        record["created_at"] = ingested_at
        records.append(record)

    if not records:
        return 0

    client = bigquery.Client(project=project_id)

    table_ref = f"{project_id}.{DATASET_ID}.{TABLE_ID}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_json(
        records,
        table_ref,
        job_config=job_config,
    )

    job.result()

    return len(records)
