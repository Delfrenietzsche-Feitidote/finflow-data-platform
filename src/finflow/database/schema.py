from psycopg import cursor

from finflow.database.connection import get_connection


CREATE_SCHEMAS = """
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS metadata;
"""


STAGING_TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS staging.stg_transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    account_id VARCHAR(100) NOT NULL,
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

CORE_CUSTOMERS_TABLE = """
CREATE TABLE IF NOT EXISTS core.customers (
    customer_id VARCHAR(100) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


CORE_ACCOUNTS_TABLE = """
CREATE TABLE IF NOT EXISTS core.accounts (
    account_id VARCHAR(100) PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_accounts_customer
        FOREIGN KEY (customer_id)
        REFERENCES core.customers(customer_id)
);
"""


CORE_MERCHANTS_TABLE = """
CREATE TABLE IF NOT EXISTS core.merchants (
    merchant_id VARCHAR(100) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


CORE_PAYMENT_METHODS_TABLE = """
CREATE TABLE IF NOT EXISTS core.payment_methods (
    payment_method_code VARCHAR(50) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


CORE_TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS core.transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,

    customer_id VARCHAR(100) NOT NULL,
    account_id VARCHAR(100) NOT NULL,
    merchant_id VARCHAR(100) NOT NULL,
    payment_method_code VARCHAR(50) NOT NULL,

    currency_code VARCHAR(10) NOT NULL,

    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_amount NUMERIC(18, 2) NOT NULL,
    transaction_fee NUMERIC(18, 2) NOT NULL,
    exchange_rate NUMERIC(18, 6) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_transactions_customer
        FOREIGN KEY (customer_id)
        REFERENCES core.customers(customer_id),

    CONSTRAINT fk_transactions_account
        FOREIGN KEY (account_id)
        REFERENCES core.accounts(account_id),

    CONSTRAINT fk_transactions_merchant
        FOREIGN KEY (merchant_id)
        REFERENCES core.merchants(merchant_id),

    CONSTRAINT fk_transactions_payment_method
        FOREIGN KEY (payment_method_code)
        REFERENCES core.payment_methods(payment_method_code)
);
"""

ANALYTICS_FACT_TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS analytics.fact_transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,

    customer_id VARCHAR(100) NOT NULL,
    account_id VARCHAR(100) NOT NULL,
    merchant_id VARCHAR(100) NOT NULL,
    payment_method_code VARCHAR(50) NOT NULL,

    currency_code VARCHAR(10) NOT NULL,

    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_date DATE NOT NULL,

    transaction_amount NUMERIC(18, 2) NOT NULL,
    transaction_fee NUMERIC(18, 2) NOT NULL,
    exchange_rate NUMERIC(18, 6) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

DAILY_TRANSACTION_METRICS_TABLE = """
CREATE TABLE IF NOT EXISTS analytics.daily_transaction_metrics (
    transaction_date DATE PRIMARY KEY,
    transaction_count INTEGER NOT NULL,
    total_transaction_amount NUMERIC(18, 2) NOT NULL,
    total_transaction_fee NUMERIC(18, 2) NOT NULL,
    average_transaction_amount NUMERIC(18, 2) NOT NULL,
    average_transaction_fee NUMERIC(18, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

PIPELINE_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS metadata.pipeline_runs (
    run_id BIGSERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    batch_date DATE,
    status VARCHAR(20) NOT NULL,
    ingested_count INTEGER NOT NULL DEFAULT 0,
    core_count INTEGER NOT NULL DEFAULT 0,
    fact_count INTEGER NOT NULL DEFAULT 0,
    metrics_count INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);
"""

def initialize_schema():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_SCHEMAS)

            cursor.execute(STAGING_TRANSACTIONS_TABLE)

            cursor.execute(CORE_CUSTOMERS_TABLE)
            cursor.execute(CORE_ACCOUNTS_TABLE)
            cursor.execute(CORE_MERCHANTS_TABLE)
            cursor.execute(CORE_PAYMENT_METHODS_TABLE)
            cursor.execute(CORE_TRANSACTIONS_TABLE)

            cursor.execute(ANALYTICS_FACT_TRANSACTIONS_TABLE)
            cursor.execute(DAILY_TRANSACTION_METRICS_TABLE)
            cursor.execute(
                """
                ALTER TABLE analytics.daily_transaction_metrics
                ADD COLUMN IF NOT EXISTS updated_at
                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
                """
            )

            cursor.execute(PIPELINE_RUNS_TABLE)
        conn.commit()