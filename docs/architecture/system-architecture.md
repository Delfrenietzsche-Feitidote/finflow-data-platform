# FinFlow System Architecture

## 1. Overview

FinFlow is a production-inspired financial data platform designed to ingest, validate, transform, and serve financial transaction data for analytics and machine learning workloads.

The architecture follows a layered data platform approach, with a clear distinction between the **current implemented pipeline** and the **target architecture**.

### Current Implemented Architecture

```text
Source / Generated Financial Data
              |
              v
       Python Ingestion
              |
              v
       Data Validation
              |
              v
      PostgreSQL Staging
              |
              v
     Incremental Detection
              |
              v
      Airflow Orchestration
              |
              v
           BigQuery
              |
              v
             dbt
              |
              v
        Analytics / BI
```

This represents the architecture currently implemented and validated in the repository.

### Target Architecture

The broader target architecture extends the current implementation with additional cloud-oriented components:

```text
Source Systems
      |
      v
Google Cloud Storage
      |
      v
Python / Airflow
      |
      v
PostgreSQL
      |
      v
BigQuery
      |
      v
dbt
      |
      v
Analytics / ML
```

Google Cloud Storage, expanded ML infrastructure, Kafka, Terraform, Kubernetes, and other platform extensions are considered future or target-state components unless explicitly implemented elsewhere in the repository.

---

## 2. Architecture Layers

### Source Layer

FinFlow receives data from financial data sources.

Current development and testing use generated financial transaction data.

Future integrations may include:

* Transaction systems
* Customer systems
* Merchant systems
* External FX rate APIs

Sources may provide CSV or JSON data and can be processed through batch ingestion workflows.

### Ingestion Layer

Python is responsible for:

* Extracting source data
* Parsing input records
* Validating records
* Rejecting invalid records
* Writing valid records to staging
* Loading new records into downstream systems

The ingestion pipeline separates validation from persistence so invalid data does not enter the analytical pipeline.

### Raw Data Layer

The target architecture includes Google Cloud Storage as a raw-data layer.

Raw data can be preserved as an immutable source layer to support:

* Pipeline replay
* Historical auditing
* Reprocessing
* Debugging
* Recovery from downstream failures

Google Cloud Storage is currently documented as a target architecture component rather than a fully implemented repository dependency.

### Staging Layer

PostgreSQL provides operational staging.

Responsibilities include:

* Temporary persistence
* Schema validation
* Transaction-level deduplication
* Controlled handoff to analytical processing

Transaction identifiers are used to prevent duplicate staging records.

### Orchestration Layer

Apache Airflow provides workflow orchestration for the platform.

Airflow is responsible for:

* Scheduling
* Task dependencies
* Pipeline execution
* Failure visibility
* Retry behavior

The orchestration layer keeps workflow scheduling separate from ingestion and transformation logic.

### Warehouse Layer

BigQuery provides analytical storage.

It is optimized for:

* Large-scale analytical queries
* Historical transaction analysis
* Aggregations
* Reporting
* Machine learning feature preparation

### Transformation Layer

dbt performs SQL-based transformations inside the analytical environment.

Responsibilities include:

* Staging transformations
* Business logic
* Dimensional modeling
* Analytical marts
* Data quality tests
* Version-controlled SQL transformations

### Consumption Layer

The platform exposes trusted datasets to downstream consumers.

Primary consumers include:

* Looker Studio dashboards
* Business analysts
* Data scientists
* Future machine learning workflows

---

## 3. Data Flow

The current implemented batch flow is:

```text
1. Extract
      |
      v
2. Validate
      |
      +---- Invalid ---> Rejected Records
      |
      v
3. PostgreSQL Staging
      |
      v
4. Incremental Detection
      |
      v
5. BigQuery Warehouse
      |
      v
6. dbt Transformations
      |
      v
7. Analytics / BI
```

The target architecture introduces an additional raw-data layer:

```text
Source Systems
      |
      v
Raw Data Layer
Google Cloud Storage
      |
      v
Python / Airflow
      |
      v
PostgreSQL
      |
      v
BigQuery
      |
      v
dbt
      |
      v
Analytics / ML
```

---

## 4. Incremental Processing

FinFlow uses transaction identifiers to avoid processing the same transaction repeatedly.

The staging layer uses conflict handling for duplicate transaction IDs.

The ingestion pipeline then identifies newly inserted transaction IDs and sends only those records to BigQuery.

This prevents repeated ingestion of previously processed transactions during repeated pipeline runs.

```text
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
```

---

## 5. Data Quality

Data quality validation occurs before records enter downstream analytical processing.

Examples of validation rules include:

* Required identifiers must be present
* Currency codes must be present
* Payment methods must be present
* Transaction amount must be positive
* Transaction fee must not be negative
* Transaction fee must not exceed transaction amount
* Exchange rates must be positive

Invalid records are rejected rather than silently propagated.

---

## 6. Reliability

The ingestion pipeline includes retry handling around external persistence operations.

Retry behavior uses exponential backoff:

```text
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
```

BigQuery writes use deterministic job identifiers so repeated submissions of the same batch can reuse the same logical load job.

This reduces the risk of duplicate loads when a request succeeds remotely but the client experiences an ambiguous failure.

---

## 7. Observability

The platform records structured ingestion results including:

* Pipeline status
* Number of records written to PostgreSQL
* Number of records written to BigQuery
* Pipeline failures
* Validation failures
* Retry attempts

These signals provide a foundation for future production monitoring.

---

## 8. CI/CD

GitHub Actions validates changes before they are merged into `main`.

The CI pipeline currently performs:

```text
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
```

This prevents formatting, linting, test, and Docker build regressions from reaching the main branch.

---

## 9. Design Principles

FinFlow follows these principles:

### Separation of Concerns

Each component has a focused responsibility.

### Immutable Raw Data

The target architecture preserves raw source data to support replay and auditing.

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

---

## 10. Architecture Evolution

The current architecture is designed to support future production enhancements:

* Kafka-based streaming ingestion
* Terraform infrastructure
* Kubernetes deployment
* OpenLineage data lineage
* Prometheus monitoring
* Apache Iceberg
* Expanded cloud deployment automation
* Machine learning feature infrastructure

These components are future extensions rather than required dependencies of the current platform.

The architecture is intentionally designed so that additional cloud and production infrastructure can be introduced without fundamentally changing the core ingestion, staging, warehouse, and transformation workflow.
