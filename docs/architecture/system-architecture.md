# FinFlow System Architecture

## 1. Overview

FinFlow is a production-inspired financial data platform designed to ingest, validate, transform, and serve financial transaction data for analytics and machine learning workloads.

The architecture follows a layered data platform approach:

Source Systems
      |
      v
Python Ingestion
      |
      v
Raw Data Storage
Google Cloud Storage
      |
      v
Operational Staging
PostgreSQL
      |
      v
Orchestration
Apache Airflow
      |
      v
Analytical Warehouse
BigQuery
      |
      v
Transformation
dbt
      |
      v
Analytics / ML
Looker Studio
ML Feature Tables


## 2. Architecture Layers

### Source Layer

FinFlow receives data from multiple financial sources:

- Transaction systems
- Customer systems
- Merchant systems
- External FX rate APIs

Sources may provide CSV or JSON data and are processed on a daily batch schedule.

### Ingestion Layer

Python is responsible for:

- Extracting source data
- Parsing input records
- Validating records
- Rejecting invalid records
- Writing valid records to staging
- Loading new records into downstream systems

The ingestion pipeline separates validation from persistence so invalid data does not enter the analytical pipeline.

### Raw Data Layer

Google Cloud Storage acts as the raw data lake.

Raw data is preserved as an immutable source layer to support:

- Pipeline replay
- Historical auditing
- Reprocessing
- Debugging
- Recovery from downstream failures

### Staging Layer

PostgreSQL provides operational staging.

Responsibilities include:

- Temporary persistence
- Schema validation
- Transaction-level deduplication
- Controlled handoff to analytical processing

Transaction identifiers are used to prevent duplicate staging records.

### Orchestration Layer

Apache Airflow manages pipeline execution.

Airflow is responsible for:

- Scheduling
- Task dependencies
- Pipeline execution
- Failure visibility
- Retry behavior

The orchestration layer keeps workflow scheduling separate from ingestion and transformation logic.

### Warehouse Layer

BigQuery provides analytical storage.

It is optimized for:

- Large-scale analytical queries
- Historical transaction analysis
- Aggregations
- Reporting
- Machine learning feature preparation

### Transformation Layer

dbt performs SQL-based transformations inside the analytical environment.

Responsibilities include:

- Staging transformations
- Business logic
- Dimensional modeling
- Analytical marts
- Data quality tests
- Version-controlled SQL transformations

### Consumption Layer

The platform exposes trusted datasets to downstream consumers.

Primary consumers include:

- Looker Studio dashboards
- Business analysts
- Data scientists
- Machine learning workflows


## 3. Data Flow

The standard batch flow is:

1. Extract
   |
   v
2. Validate
   |
   +---- Invalid ---> Rejected Records
   |
   v
3. Raw Storage
   |
   v
4. PostgreSQL Staging
   |
   v
5. Airflow Orchestration
   |
   v
6. BigQuery Warehouse
   |
   v
7. dbt Transformations
   |
   v
8. Analytics Marts
   |
   +----> Looker Studio
   |
   +----> ML Feature Tables


## 4. Incremental Processing

FinFlow uses transaction identifiers to avoid processing the same transaction repeatedly.

The staging layer uses conflict handling for duplicate transaction IDs.

The ingestion pipeline then identifies newly inserted transaction IDs and sends only those records to BigQuery.

This prevents repeated ingestion of previously processed transactions during repeated pipeline runs.

Input Batch
    |
    v
PostgreSQL
    |
    +---- Existing transaction ---> Skip
    |
    +---- New transaction --------> Continue
                                      |
                                      v
                                  BigQuery


## 5. Data Quality

Data quality validation occurs before records enter downstream analytical processing.

Examples of validation rules include:

- Required identifiers must be present
- Currency codes must be present
- Payment methods must be present
- Transaction amount must be positive
- Transaction fee must not be negative
- Transaction fee must not exceed transaction amount
- Exchange rates must be positive

Invalid records are rejected rather than silently propagated.


## 6. Reliability

The ingestion pipeline includes retry handling around external persistence operations.

Retry behavior uses exponential backoff:

Attempt 1
   |
   | failure
   v
Wait
   |
   v
Attempt 2
   |
   | failure
   v
Wait longer
   |
   v
Attempt 3

BigQuery writes use deterministic job identifiers so repeated submissions of the same batch can reuse the same logical load job.

This reduces the risk of duplicate loads when a request succeeds remotely but the client experiences an ambiguous failure.


## 7. Observability

The platform records structured ingestion results including:

- Pipeline status
- Number of records written to PostgreSQL
- Number of records written to BigQuery
- Pipeline failures
- Validation failures
- Retry attempts

These signals provide a foundation for future production monitoring.


## 8. CI/CD

GitHub Actions validates changes before they are merged into main.

The CI pipeline currently performs:

Checkout
   |
   v
Install dependencies
   |
   v
Ruff lint
   |
   v
Ruff format check
   |
   v
PostgreSQL setup
   |
   v
Database initialization
   |
   v
Pytest
   |
   v
Docker build

This prevents formatting, linting, test, and Docker build regressions from reaching the main branch.


## 9. Design Principles

FinFlow follows these principles:

### Separation of Concerns

Each component has a focused responsibility.

### Immutable Raw Data

Raw source data is preserved to support replay and auditing.

### Idempotent Processing

Repeated pipeline execution should not create duplicate transaction records.

### Data Quality First

Invalid records are rejected before downstream processing.

### ELT

Transformation logic is primarily performed in the analytical warehouse using dbt.

### Version Control

Application code, SQL models, pipeline definitions, infrastructure configuration, and documentation are version controlled.

### Automated Validation

Every change is validated through linting, formatting checks, automated tests, and Docker builds.


## 10. Architecture Evolution

The current architecture is designed to support future production enhancements:

- Kafka-based streaming ingestion
- Terraform infrastructure
- Kubernetes deployment
- OpenLineage data lineage
- Prometheus monitoring
- Apache Iceberg
- Expanded cloud deployment automation

These components are future extensions rather than required dependencies of the current platform.
