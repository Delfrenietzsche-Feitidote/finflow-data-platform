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
  
  merchant_name ,
  
  merchant_category ,

  merchant_segment,

  city ,

  country , 

  merchant_status ,

  onboarding_date ,

  effective_date ,

  expiry_date ,

  is_current 
);
