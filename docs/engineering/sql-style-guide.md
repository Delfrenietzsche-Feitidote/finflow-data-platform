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


| Standard     | Decision                                       |
| ------------ | ---------------------------------------------- |
| Naming       | `snake_case`                                   |
| Tables       | `dim_*`, `fact_*`                              |
| PK           | `<table>_key`                                  |
| Business Key | `<entity>_id`                                  |
| Money        | `NUMERIC(18,2)`                                |
| Dates        | `DATE`                                         |
| Timestamps   | `TIMESTAMP`                                    |
| Boolean      | `BOOLEAN`                                      |
| IDs          | `BIGINT` (surrogate), `VARCHAR(50)` (business) |
| Git          | Conventional Commits                           |
| SQL          | Header comment + consistent formatting         |
