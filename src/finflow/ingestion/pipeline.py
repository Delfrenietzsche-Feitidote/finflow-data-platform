from finflow.ingestion.loaders.raw_writer import write_raw_transactions
from finflow.ingestion.loaders.rejected_writer import write_rejected_transactions
from finflow.ingestion.sources.transactions import generate_transactions
from finflow.ingestion.validators.batch import validate_transactions


def run_ingestion(
    count: int = 10,
    batch_date: str = "2026-08-10",
) -> None:
    # 1. Extract
    transactions = generate_transactions(count)

    # 2. Validate
    valid_transactions, rejected_transactions = validate_transactions(
        transactions
    )

    # 3. Write valid records
    write_raw_transactions(
        valid_transactions,
        f"data/raw/transactions/{batch_date}/transactions.json",
    )

    # 4. Write rejected records
    if rejected_transactions:
        write_rejected_transactions(
            rejected_transactions,
            f"data/rejected/transactions/{batch_date}/rejected.json",
        )

    print(f"Extracted: {len(transactions)}")
    print(f"Valid: {len(valid_transactions)}")
    print(f"Rejected: {len(rejected_transactions)}")