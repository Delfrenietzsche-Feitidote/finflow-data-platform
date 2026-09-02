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

    customer_key BIGINT PRIMARY KEY,

    customer_id VARCHAR(50) NOT NULL,

    customer_name VARCHAR(255) NOT NULL,

    customer_segment VARCHAR(50),

    city VARCHAR(100),

    country VARCHAR(100) NOT NULL,

    customer_status VARCHAR(20) NOT NULL,

    effective_date DATE NOT NULL,

    expiry_date DATE,

    is_current BOOLEAN NOT NULL

);
