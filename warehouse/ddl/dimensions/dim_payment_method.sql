-- ==========================================================
-- Table: warehouse.dim_payment_method
-- Layer: Analytics Warehouse
-- Purpose:
-- Stores payment_method attributes for analytical reporting.
--
-- Grain:
-- One row represents one payment method.
--
-- Author: Alize
-- ==========================================================

CREATE TABLE warehouse.dim_payment_method (

    payment_method_key BIGINT PRIMARY KEY,

    payment_method_code VARCHAR(50) NOT NULL,

    payment_method_name VARCHAR(100) NOT NULL,

    payment_type VARCHAR(30) NOT NULL,

    provider VARCHAR(100),

    is_digital BOOLEAN NOT NULL

);
