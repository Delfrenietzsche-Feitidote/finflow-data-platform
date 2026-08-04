-- ==========================================================
-- Table: warehouse.dim_currency
-- Layer: Analytics Warehouse
-- Purpose:
-- Stores currency attributes for analytical reporting.
--
-- Grain:
-- One row represents one currency.
--
-- Author: Alize
-- ==========================================================


 CREATE TABLE warehouse.dim_currency (

    currency_key BIGINT PRIMARY KEY,

    currency_code VARCHAR(3) NOT NULL,

    currency_name VARCHAR(255) NOT NULL,

    country VARCHAR(100) NOT NULL,

    country_code VARCHAR(2) NOT NULL,

);
