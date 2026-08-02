
# ADR-001: Platform Architecture

## Status

Accepted

## Context

FinFlow is a cloud-native analytics platform for a digital bank. It must ingest data from multiple systems, preserve raw data for replay, support analytics workloads, and prepare features for machine learning.

## Decision

The platform will use:

- Python for ingestion
- Google Cloud Storage as the raw data lake
- PostgreSQL for operational staging
- Apache Airflow for orchestration
- BigQuery as the analytical warehouse
- dbt for SQL transformations
- Looker Studio for dashboards

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
