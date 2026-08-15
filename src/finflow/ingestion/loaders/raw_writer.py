import json
from pathlib import Path

from finflow.ingestion.models.transaction import TransactionRecord


def write_raw_transactions(
    transactions: list[TransactionRecord],
    output_path: str,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    records = [
        transaction.model_dump(mode="json")
        for transaction in transactions
    ]

    with path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)