-- ==========================================================
-- Table: dim_customer
-- Layer: Analytics Warehouse
-- Purpose:
-- Stores customer attributes for analytical reporting.
--
-- Grain:
-- One row represents one version of one customer.
--
-- Author: Alize
-- ==========================================================

CREATE TABLE warehouse.dim_customer (
    customer_key,
    customer_id,
    customer_name,
    customer_segment,
    city,
    country,
    customer_status,
    effective_date,
    expiry_date,
    is_current       
)
