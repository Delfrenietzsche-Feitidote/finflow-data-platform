FinFlow Transaction Analytics Dashboard

Overview
========

The FinFlow Transaction Analytics Dashboard provides a business-facing view of transaction activity, transaction value, fees, and merchant performance.

The dashboard is built on analytical data transformed through dbt and stored in Google BigQuery.

Data Flow
=========

Source Data
    |
Python Ingestion
    |
BigQuery RAW
    |
dbt Staging
    |
dbt Intermediate
    |
dbt Analytical Marts
    |
Looker Studio Dashboard


Dashboard Data Sources
======================

1. analytics.fct_transactions

Purpose:
Transaction-level analysis.

Provides:
- Transaction ID
- Customer ID
- Account ID
- Merchant ID
- Payment method
- Currency
- Transaction timestamp
- Transaction amount
- Transaction fee
- Net transaction amount
- Exchange rate


2. analytics.daily_transaction_metrics

Purpose:
Daily aggregated transaction metrics.

Provides:
- Transaction count
- Total transaction amount
- Total transaction fee
- Average transaction amount
- Average transaction fee
- Total net transaction amount


Key Performance Indicators
==========================

- Total Transactions
  Total number of transactions.

- Transaction Value
  Total transaction amount.

- Total Fees
  Total transaction fees.

- Net Transaction Value
  Transaction value after fees.

- Average Transaction Value
  Average transaction amount per transaction.


Dashboard Visualizations
========================

Daily Transaction Count
-----------------------
Shows transaction volume over time and helps identify changes in daily transaction activity.

Daily Transaction Value
-----------------------
Shows total transaction value by date and highlights significant changes or spikes in transaction activity.

Payment Method Analysis
-----------------------
Shows transaction value and transaction count by payment method.

Top Merchants by Transaction Value
----------------------------------
Ranks merchants based on total transaction value and highlights the merchants contributing the most transaction volume.


Filters
=======

The dashboard supports filtering by:

- Date range
- Payment method
- Merchant


Data Quality
============

Dashboard metrics are sourced from the dbt analytical layer rather than directly from RAW data.

The dbt pipeline applies data-quality checks including:

- Required-field validation
- Transaction ID uniqueness
- Transaction ID not-null validation
- Staging deduplication


Screenshot
==========

The dashboard screenshot is stored alongside this documentation:

finflow-dashboard.png


Technology Stack
================

- Google BigQuery
- dbt
- Looker Studio
- Python
- PostgreSQL
- Apache Airflow
- GitHub Actions
