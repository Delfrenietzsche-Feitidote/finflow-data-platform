from finflow.ingestion.models.transaction import TransactionRecord
from finflow.ingestion.validators.transaction import validate_transaction


def validate_transactions(
    transactions: list[TransactionRecord],
) -> tuple[list[TransactionRecord], list[dict]]:
    valid_transactions = []
    rejected_transactions = []

    seen_transaction_ids = set()

    for transaction in transactions:
        errors = validate_transaction(transaction)

        if transaction.transaction_id in seen_transaction_ids:
            errors.append("duplicate transaction_id")

        seen_transaction_ids.add(transaction.transaction_id)

        if errors:
            rejected_transactions.append(
                {
                    "transaction_id": transaction.transaction_id,
                    "errors": errors,
                }
            )
        else:
            valid_transactions.append(transaction)

    return valid_transactions, rejected_transactions