
-- ==========================================================
-- Table: warehouse.dim_date
-- Layer: Analytics Warehouse
-- Purpose:
-- Stores calendar attributes for analytical reporting.
--
-- Grain:
-- One row represents one calendar date.
--
-- Refresh Strategy:
-- Static (generated once, updated annually if needed)
-- ==========================================================

CREATE TABLE warehouse.dim_date (

    date_key INT PRIMARY KEY,

    full_date DATE NOT NULL,

    day INT NOT NULL,

    day_name VARCHAR(10) NOT NULL,

    day_of_week INT NOT NULL,

    week_of_year INT NOT NULL,

    month_number INT NOT NULL,

    month_name VARCHAR(10) NOT NULL,

    quarter INT NOT NULL,

    year INT NOT NULL,

    is_weekend BOOLEAN NOT NULL,

    is_holiday BOOLEAN NOT NULL

);
