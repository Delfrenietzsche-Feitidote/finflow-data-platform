-- ==========================================================
-- Table: warehouse.dim_merchant
-- Layer: Analytics Warehouse
-- Purpose:
-- Stores customer attributes for analytical reporting.
--
-- Grain:
-- One row represents one version of one customer (SCD Type 2).
--
-- Author: Alize
-- ==========================================================

CREATE TABLE warehouse.dim_merchant (
  merchant_key INT PRIMARY KEY,
  
  merchant_id INT KEY,
  
  merchant_name VARCHAR(64) NOT NULL,
  
  merchant_category VARCHAR(64) NOT NULL,

  merchant_segment VARCHAR(64) NOT NULL,

  city VARCHAR(64),

  country VARCHAR(64) NOT NULL, 

  merchant_status IN (ACTIVE, INACTIVE),

  onboarding_date DATE NOT NULL,

  effective_date  DATE NOT NULL,

  expiry_date DATE NOT NULL,

  is_current BOOLEAN
);
