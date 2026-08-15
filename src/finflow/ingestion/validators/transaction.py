from finflow.ingestion.models.transaction import TransactionRecord


def validate_transaction(transaction: TransactionRecord) -> list[str]:
    errors = []

    if not transaction.transaction_id.strip():
        errors.append("transaction_id is empty")

    if not transaction.customer_id.strip():
        errors.append("customer_id is empty")

    if not transaction.merchant_id.strip():
        errors.append("merchant_id is empty")

    if not transaction.currency_code.strip():
        errors.append("currency_code is empty")

    if not transaction.payment_method_code.strip():
        errors.append("payment_method_code is empty")

    if transaction.transaction_amount <= 0:
        errors.append("transaction_amount must be greater than 0")

    if transaction.transaction_fee < 0:
        errors.append("transaction_fee cannot be negative")

    if transaction.exchange_rate <= 0:
        errors.append("exchange_rate must be greater than 0")

    return errors