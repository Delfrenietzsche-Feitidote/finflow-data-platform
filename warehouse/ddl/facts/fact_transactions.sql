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

CREATE TABLE warehouse.dim_payment_method (

    transaction_key BIGINT PRIMARY KEY,

    transaction_id VARCHAR(50) NOT NULL,

    FOREIGN KEY (customer_key) REFERENCES warehouse.dim_customer(customer_key),

    FOREIGN KEY (merchant_key) REFERENCES warehouse.dim_customer(merchant_key),

    FOREIGN KEY (date_key) REFERENCES warehouse.dim_customer(date_key),

    FOREIGN KEY (currency_key) REFERENCES warehouse.dim_customer(currency_key),

    FOREIGN KEY (payment_method_key) REFERENCES warehouse.dim_customer(payment_method_key),

    transaction_timestamp DATE NOT NULL,

    transaction_amount DECIMAL(10,2) NOT NULL,

    transaction_fee DECIMAL(10,2) NOT NULL,

    exchange_rate DECIMAL(10,2) NOT NULL,

    amount_usd DECIMAL(10,2) NOT NULL

    batch_id VARCHAR(50) NOT NULL,

    source_system VARCHAR(100),

    load_timestamp DATE NOT NULL

);

