# FinFlow Transaction Analytics Dashboard

## Overview

The FinFlow Transaction Analytics Dashboard provides a business-facing view of transaction activity, transaction value, fees, and merchant performance.

The dashboard is built on analytical data transformed through dbt and stored in Google BigQuery.

## Data Flow

```text
Source Data
    ↓
Python Ingestion
    ↓
BigQuery RAW
    ↓
dbt Staging
    ↓
dbt Intermediate
    ↓
dbt Analytical Marts
    ↓
Looker Studio Dashboard