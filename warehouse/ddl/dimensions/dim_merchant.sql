-- ==========================================================
-- Table: warehouse.dim_merchant
-- Layer: Analytics Warehouse
-- Purpose:
-- Stores customer attributes for analytical reporting.
--
-- Grain:
-- One row represents one version of one merchant (SCD Type 2).
--
-- Author: Alize
-- ==========================================================

CREATE TABLE warehouse.dim_merchant (
  merchant_key BIGINT PRIMARY KEY,

  merchant_id VARCHAR(50) NOT NULL,
  
  merchant_name VARCHAR(255) NOT NULL,
  
  merchant_category VARCHAR(50) NOT NULL,
  
  merchant_segment VARCHAR(50) NOT NULL,
  
  city VARCHAR(100),
  
  country VARCHAR(100) NOT NULL,
  
  merchant_status VARCHAR(20) NOT NULL,
  
  onboarding_date DATE NOT NULL,
  
  effective_date DATE NOT NULL,
  
  expiry_date DATE,
  
  is_current BOOLEAN NOT NULL,
);
