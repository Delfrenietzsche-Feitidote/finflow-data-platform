# FinFlow

> Production-inspired financial data platform for reliable ingestion, data quality, analytics, and machine learning readiness.

FinFlow is an end-to-end **financial data engineering platform** designed to demonstrate how modern data pipelines can ingest, validate, process, transform, and serve financial transaction data for analytics.

The project focuses on production-oriented engineering practices including **data quality, incremental processing, idempotency, retry strategies, observability, automated testing, CI/CD, and architecture documentation**.

---

## Portfolio Showcase

> **FinFlow demonstrates production-oriented Data Engineering — not just data movement.**

### What I Built

An end-to-end financial data platform that ingests, validates, stages, incrementally processes, transforms, and serves transaction data for analytics.

    Financial Transactions
            │
            ▼
     Python Ingestion
            │
            ▼
     Data Validation
            │
            ▼
     PostgreSQL Staging
            │
            ▼
     Incremental Detection
            │
            ▼
     Apache Airflow
            │
            ▼
     BigQuery
            │
            ▼
     dbt Transformations
            │
            ▼
     Analytics / BI

### Engineering Highlights

| Capability | Implementation |
|------------|----------------|
| **Data Quality** | Validation rules prevent malformed financial transactions from reaching downstream systems |
| **Incremental Processing** | Only newly inserted transactions are sent downstream |
| **Idempotency** | Duplicate transaction IDs are prevented during staging and BigQuery jobs use deterministic identifiers |
| **Reliability** | External writes use retry handling with exponential backoff |
| **Orchestration** | Apache Airflow manages pipeline execution |
| **Warehouse** | BigQuery provides analytical storage |
| **Transformation** | dbt manages SQL-based warehouse transformations |
| **Testing** | 57 automated tests covering pipeline and reliability behavior |
| **CI/CD** | GitHub Actions runs Ruff, pytest, PostgreSQL integration, and Docker validation |

### Why It Stands Out

FinFlow goes beyond a basic ETL project by treating **reliability, data quality, incremental processing, observability, testing, and CI/CD as first-class engineering concerns**.

It demonstrates how I approach Data Engineering from both sides:

**Build the pipeline → make it reliable → make it testable → make it maintainable.**

---

## Project Status

**Project Status: Portfolio Release Complete**

| Sprint     | Area                         | Status         |
| ---------- | ---------------------------- | -------------- |
| Sprint 0   | Foundation                   | ✅ Complete     |
| Sprint 1   | Data Modeling                | ✅ Complete     |
| Sprint 2   | Warehouse Design             | ✅ Complete     |
| Sprint 3   | Python Ingestion             | ✅ Complete     |
| Sprint 4   | PostgreSQL Staging           | ✅ Complete     |
| Sprint 5   | Airflow & Observability      | ✅ Complete     |
| Sprint 6   | BigQuery & dbt               | ✅ Complete     |
| Sprint 7   | Analytics                    | ✅ Complete     |
| Sprint 8.1 | Data Quality & Monitoring    | ✅ Complete     |
| Sprint 8.2 | Incremental Processing       | ✅ Complete     |
| Sprint 8.3 | Production Reliability       | ✅ Complete     |
| Sprint 8.4 | CI/CD Improvements           | ✅ Complete     |
| Sprint 8.5 | Architecture & Documentation | ✅ Complete     |
| Sprint 8.6 | Final Portfolio Polish       | ✅ Complete     |

---

## 1. Overview

FinFlow simulates a financial data platform that processes transaction data from multiple operational sources and prepares trusted datasets for analytical workloads.

The platform demonstrates a modern **ELT-oriented data engineering architecture**, separating ingestion, staging, orchestration, transformation, warehouse storage, and analytics responsibilities.

The primary engineering goal is not simply to move data from A to B, but to make the pipeline:

* Reliable
* Testable
* Incremental
* Idempotent
* Observable
* Maintainable
* Production-oriented

---

## 2. Business Scenario

A digital financial platform receives large volumes of transaction data from multiple operational systems.

Business teams need reliable data to understand:

* Transaction activity
* Customer behavior
* Merchant performance
* Payment methods
* Currency and exchange-rate effects
* Financial trends

Data scientists and machine learning engineers also require consistent historical datasets that can be reused for downstream modeling.

FinFlow addresses these requirements by creating a structured data pipeline that validates incoming transactions, stores operational staging data, processes only new records, and prepares analytical datasets.

---

## 3. Project Objectives

FinFlow was designed to demonstrate the following capabilities:

* Build an end-to-end financial data platform
* Ingest transaction data using Python
* Validate incoming records before persistence
* Store data in PostgreSQL staging tables
* Prevent duplicate transaction processing
* Process incremental transaction batches
* Load analytical data into BigQuery
* Transform warehouse data using dbt
* Orchestrate pipelines with Airflow
* Add structured logging and failure visibility
* Implement retry handling for external writes
* Automate code-quality checks with Ruff
* Automate testing through CI/CD
* Document architecture and engineering decisions

---

## 4. System Architecture

The platform follows a layered architecture:

```text
                    ┌─────────────────────┐
                    │   Source Systems    │
                    │ Transactions / FX   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Python Ingestion   │
                    │ Extract + Validate   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ PostgreSQL Staging  │
                    │ Deduplication        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Airflow         │
                    │   Orchestration     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      BigQuery       │
                    │ Analytical Storage  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │        dbt          │
                    │   Transformations   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Analytics / BI / ML │
                    └─────────────────────┘
```

For the detailed architecture and design decisions:

* [System Architecture](docs/architecture/system-architecture.md)
* [Architecture Decision Record](docs/adr/001-platform-architecture.md)

---

## 5. Technology Stack

| Category           | Technology     | Purpose                           |
| ------------------ | -------------- | --------------------------------- |
| Language           | Python 3.11    | Data ingestion and pipeline logic |
| Package Management | uv             | Dependency management             |
| Database           | PostgreSQL     | Operational staging               |
| Warehouse          | BigQuery       | Analytical storage                |
| Orchestration      | Apache Airflow | Pipeline scheduling and execution |
| Transformation     | dbt            | SQL-based transformations         |
| Containerization   | Docker         | Reproducible local environment    |
| CI/CD              | GitHub Actions | Automated quality and test checks |
| Code Quality       | Ruff           | Linting and formatting            |
| Testing            | pytest         | Automated testing                 |
| Version Control    | Git / GitHub   | Source control and collaboration  |

---

## 6. Data Pipeline

The core pipeline follows:

```text
Extract
   │
   ▼
Validate
   │
   ├── Invalid → Reject / Record Failure
   │
   ▼
PostgreSQL Staging
   │
   ▼
Incremental Detection
   │
   ▼
BigQuery
   │
   ▼
dbt Transformations
   │
   ▼
Analytics
```

The ingestion layer separates valid and invalid transactions before writing them to downstream systems.

Validation includes checks such as:

* Required transaction identifiers
* Required account identifiers
* Valid currency codes
* Valid payment methods
* Transaction amount greater than zero
* Transaction fee greater than or equal to zero
* Transaction fee not exceeding transaction amount
* Exchange rate greater than zero

### Example Pipeline Walkthrough

A typical FinFlow ingestion run processes a batch through the following lifecycle:

1. **Generate / receive transactions** — the ingestion layer receives a batch of financial transaction records.
2. **Validate records** — transaction identifiers, accounts, currencies, payment methods, amounts, fees, and exchange rates are validated.
3. **Separate invalid records** — malformed transactions are rejected before reaching downstream systems.
4. **Stage in PostgreSQL** — valid transactions are written to PostgreSQL, where existing transaction IDs are ignored.
5. **Detect new transactions** — PostgreSQL returns the IDs that were actually inserted, allowing the pipeline to identify the incremental batch.
6. **Load BigQuery** — only newly inserted transactions are sent to BigQuery. Deterministic job IDs help protect retried loads from duplicate jobs.
7. **Transform with dbt** — warehouse data is transformed into analytics-ready datasets.
8. **Serve analytics** — trusted transformed data becomes available for analytical and future machine-learning workloads.

```text
Transaction Batch
       │
       ▼
   Validation
       │
       ├── Invalid ──→ Reject
       │
       ▼
PostgreSQL Staging
       │
       ▼
New IDs Returned
       │
       ▼
Incremental Batch
       │
       ▼
    BigQuery
       │
       ▼
      dbt
       │
       ▼
Analytics / BI
```

If an external PostgreSQL or BigQuery write fails transiently, FinFlow retries the operation using exponential backoff. Pipeline execution and write counts are recorded through structured logging, providing visibility into successful and failed runs.

---

## 7. Incremental Processing & Idempotency

A major production-readiness improvement is preventing duplicate downstream processing.

PostgreSQL uses the transaction identifier as the deduplication key:

```text
Incoming Transactions
        │
        ▼
PostgreSQL
        │
        ├── Existing transaction → Ignore
        │
        └── New transaction
                │
                ▼
        Return inserted IDs
                │
                ▼
        Send only new records
                │
                ▼
             BigQuery
```

Instead of blindly sending an entire batch to BigQuery, the pipeline identifies which transactions were actually inserted into staging and sends only those records downstream.

This makes repeated ingestion runs significantly safer and reduces duplicate analytical records.

---

## 8. Production Reliability

FinFlow includes several reliability mechanisms.

### Retry with Exponential Backoff

External database and warehouse writes are protected by retry handling.

The retry strategy follows:

```text
Attempt 1
   │
   ├── Success → Continue
   │
   └── Failure
         │
         ▼
      Wait 1s
         │
         ▼
Attempt 2
   │
   ├── Success → Continue
   │
   └── Failure
         │
         ▼
      Wait 2s
         │
         ▼
Attempt 3
```

This helps recover from transient failures without immediately terminating the pipeline.

### Deterministic BigQuery Jobs

BigQuery ingestion uses deterministic job identifiers derived from batch contents.

This provides an additional layer of protection against duplicate load jobs when a request result becomes ambiguous after an external failure.

---

## 9. Data Quality & Monitoring

FinFlow treats data quality as part of the ingestion process rather than as an afterthought.

The pipeline tracks:

* Input transaction count
* Valid transaction count
* Invalid transaction count
* Database writes
* BigQuery writes
* Pipeline status
* Pipeline failures
* Retry attempts

Structured logging provides visibility into pipeline execution and failures.

---

## 10. CI/CD

GitHub Actions provides automated quality gates for changes submitted to the repository.

```text
Pull Request
     │
     ▼
Checkout
     │
     ▼
Install Dependencies
     │
     ▼
Ruff Lint
     │
     ▼
Ruff Format Check
     │
     ▼
PostgreSQL Setup
     │
     ▼
Database Initialization
     │
     ▼
Pytest
     │
     ▼
Docker Build
```

Current quality checks include:

* Ruff linting
* Ruff formatting validation
* Automated pytest execution
* PostgreSQL integration environment
* Docker build validation

The current test suite contains **57 automated tests**.

---

## 11. Repository Structure

```text
finflow-data-platform/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── dags/
│   └── Airflow DAG definitions
│
├── dbt/
│   └── dbt transformation project
│
├── docker/
│   └── Docker configuration
│
├── docs/
│   ├── adr/
│   ├── architecture/
│   └── diagrams/
│
├── src/
│   └── finflow/
│       ├── analytics/
│       ├── common/
│       ├── database/
│       ├── ingestion/
│       ├── orchestration/
│       └── transformation/
│
├── tests/
│   ├── ingestion/
│   ├── orchestration/
│   └── ...
│
├── warehouse/
│   └── Warehouse SQL and schema definitions
│
├── .env.example
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## 12. Engineering Highlights

### Data Quality

Implemented validation rules to prevent malformed financial transactions from entering downstream systems.

### Incremental Processing

The pipeline identifies newly inserted transaction IDs and only forwards new records to the analytical warehouse.

### Idempotent Processing

Duplicate transaction IDs are ignored during PostgreSQL staging, reducing the risk of duplicate downstream records.

### Production Reliability

External writes use retry handling with exponential backoff.

### Observability

Structured logs and pipeline metrics provide visibility into successful and failed ingestion runs.

### Automated Testing

The project maintains a growing automated test suite covering ingestion, validation, database writes, BigQuery writes, pipeline behavior, and reliability scenarios.

### CI/CD

Ruff and pytest are integrated into GitHub Actions to prevent quality regressions.

---

## 13. Development Workflow

FinFlow follows a feature-branch workflow:

```text
Create Feature Branch
        │
        ▼
Implement Change
        │
        ▼
Run Local Tests
        │
        ▼
Commit
        │
        ▼
Push Branch
        │
        ▼
Open Pull Request
        │
        ▼
CI Validation
        │
        ▼
Code Review
        │
        ▼
Merge
```

Example:

```bash
git checkout main
git pull origin main

git checkout -b feature/<feature-name>

uv run pytest -q
uv run ruff check .
uv run ruff format --check .

git add .
git commit -m "feat: <description>"
git push -u origin feature/<feature-name>
```

---

## 14. Getting Started

### Prerequisites

* Python 3.11
* uv
* Docker Desktop
* Git

### Clone the Repository

```bash
git clone https://github.com/Delfrenietzsche-Feitidote/finflow-data-platform.git

cd finflow-data-platform
```

### Install Dependencies

```bash
uv sync
```

### Start the Local Environment

Start PostgreSQL:

```bash
docker compose -f docker/docker-compose.yml up -d
```

### Start Airflow

```bash
docker compose -f docker/airflow/docker-compose.yml up --build
```

### Run Tests

```bash
uv run pytest -q
```

### Run Code Quality Checks

```bash
uv run ruff check .
uv run ruff format --check .
```

---

## 15. Documentation

### Architecture

* [System Architecture](docs/architecture/system-architecture.md)
* [Platform Architecture ADR](docs/adr/001-platform-architecture.md)

### Architecture & Requirements

* [Business Requirements](docs/architecture/business-requirements.md)
* [Source Systems](docs/architecture/source-systems.md)

Additional documentation is maintained under the `docs/` directory.

---

## 16. Roadmap

Sprint 8 focuses on production readiness and portfolio presentation. Core engineering, architecture documentation, repository cleanup, and final validation are complete; the remaining work is the final portfolio wrap-up.

### Sprint 8.5 — Architecture & Documentation

* [x] System architecture documentation
* [x] README portfolio upgrade
* [x] Architecture consistency review

### Sprint 8.6 — Final Portfolio Polish

* [x] Final documentation review
* [x] Repository cleanup
* [x] Portfolio presentation improvements
* [x] Example pipeline walkthrough
* [x] Final architecture review
* [x] Production-readiness summary

---

## 17. Future Enhancements

Potential future improvements include:

* Kafka-based streaming ingestion
* Infrastructure as Code with Terraform
* Kubernetes deployment
* Expanded cloud deployment automation
* Data lineage with OpenLineage
* Prometheus-based monitoring
* Apache Iceberg for large-scale data storage
* More advanced data-quality monitoring
* ML feature-store integration

These are **future architecture directions**, not necessarily current production implementations.

---

## 18. Lessons Learned

Building FinFlow highlighted several important data engineering principles.

### Data quality must happen early

Invalid data should be detected before it reaches downstream analytical systems.

### Idempotency matters

A production pipeline should be safe to rerun without blindly duplicating data.

### External systems fail

Database and warehouse operations can experience transient failures, so retry strategies are necessary.

### Observability is part of reliability

A pipeline that runs successfully but provides no visibility into what happened is difficult to operate.

### Testing should evolve with the architecture

Every production-readiness improvement should be supported by automated tests.

### Documentation is an engineering artifact

Architecture documentation makes design decisions easier to understand, review, maintain, and extend.

---

## 19. Engineering Principles

FinFlow follows these principles:

* **Separation of concerns**
* **Data quality by design**
* **Incremental processing**
* **Idempotent pipeline behavior**
* **Failure-aware engineering**
* **Observability**
* **Automated testing**
* **Continuous integration**
* **Version-controlled transformations**
* **Documentation-first architecture**
* **Production-oriented design**

---

## 20. Why This Project Matters

FinFlow is designed to demonstrate practical **Data Engineering** skills beyond basic ETL scripting.

The project combines:

```text
Data Ingestion
      +
Data Quality
      +
Database Engineering
      +
Incremental Processing
      +
Orchestration
      +
Warehouse Engineering
      +
ELT / dbt
      +
Reliability
      +
Observability
      +
CI/CD
      =
Production-Oriented Data Platform
```

The goal is to demonstrate the ability to think about a data platform not only from the perspective of **moving data**, but also from the perspective of **operability, reliability, maintainability, and business usability**.
