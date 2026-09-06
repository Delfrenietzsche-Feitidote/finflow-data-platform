# ADR-001: Platform Architecture

## Status

Accepted

## Context

FinFlow is a production-inspired financial data platform designed around cloud-native data engineering patterns. It must ingest financial transaction data, support reliable analytical workloads, and provide a foundation for future machine learning use cases.

## Decision

The target platform architecture will use:

- Python for ingestion
- Google Cloud Storage as a raw-data layer
- PostgreSQL for operational staging
- Apache Airflow for orchestration
- BigQuery as the analytical warehouse
- dbt for SQL transformations
- Looker Studio for dashboards

The currently implemented repository focuses on the Python, PostgreSQL,
Airflow, BigQuery, and dbt portions of this architecture. Google Cloud
Storage and expanded cloud infrastructure are documented as target
architecture components rather than claimed as fully implemented services.

## Consequences

### Advantages

- Clear separation of responsibilities
- Replayable pipelines
- Scalable analytics
- Maintainable transformations
- Strong support for testing and documentation

### Trade-offs

- More services increase operational complexity.
- Cloud resources introduce costs.
- ELT requires familiarity with SQL and dbt.
