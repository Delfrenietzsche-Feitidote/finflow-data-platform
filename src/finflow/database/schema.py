from finflow.database.connection import get_connection


TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    merchant_id VARCHAR(100) NOT NULL,
    currency_code VARCHAR(10) NOT NULL,
    payment_method_code VARCHAR(50) NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_amount NUMERIC(18, 2) NOT NULL,
    transaction_fee NUMERIC(18, 2) NOT NULL,
    exchange_rate NUMERIC(18, 6) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def initialize_schema():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(TRANSACTIONS_TABLE)
        conn.commit()