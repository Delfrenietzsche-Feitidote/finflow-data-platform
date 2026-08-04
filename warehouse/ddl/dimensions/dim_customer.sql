-- ==========================================================
-- Table: warehouse.dim_customer
-- Layer: Analytics Warehouse
-- Purpose:
-- Stores customer attributes for analytical reporting.
--
-- Grain:
-- One row represents one version of one customer (SCD Type 2).
--
-- Author: Alize
-- ==========================================================

 CREATE TABLE warehouse.dim_customer (
    
    FOREIGN KEY(customer_key) REFERENCES fact_transactions(customer_id),
    
    customer_id INT PRIMARY KEY,
    
    customer_name VARCHAR(64) NOT NULL,
    
    customer_segment VARCHAR(10),
    
    city VARCHAR(64),
    
    country VATCHAR(64) NOT NULL,
    
    customer_status VARCHAR(64) NOT NULL,
    
    effective_date DATE,
    
    expiry_date DATE,
    
    is_current BOOLEAN NOT NULL
    
);
