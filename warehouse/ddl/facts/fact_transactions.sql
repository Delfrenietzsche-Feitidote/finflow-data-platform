-- ==========================================================
-- Table: warehouse.fact_transactions
-- Layer: Analytics Warehouse
-- Purpose:
-- Stores transaction attributes for analytical reporting.
--
-- Grain:
-- One row represents one completed financial transaction.
--
-- Author: Alize
-- ==========================================================

CREATE TABLE warehouse.fact_transactions (

    transaction_key BIGINT PRIMARY KEY,

    transaction_id VARCHAR(50) NOT NULL,

    customer_key BIGINT NOT NULL REFERENCES warehouse.dim_customer(customer_key),

    merchant_key BIGINT NOT NULL REFERENCES warehouse.dim_merchant(merchant_key),

    date_key BIGINT NOT NULL REFERENCES warehouse.dim_date(date_key),

    currency_key BIGINT NOT NULL REFERENCES warehouse.dim_currency(currency_key),

    payment_method_key BIGINT NOT NULL REFERENCES warehouse.dim_payment_method(payment_method_key),

    transaction_timestamp TIMESTAMP NOT NULL,

    transaction_amount NUMERIC(18,2) NOT NULL,

    transaction_fee NUMERIC(18,2) NOT NULL,

    exchange_rate NUMERIC(18,2) NOT NULL,

    amount_usd NUMERIC(18,2) NOT NULL

    batch_id VARCHAR(50) NOT NULL,

    source_system VARCHAR(100),

    load_timestamp TIMESTAMP NOT NULL

);

