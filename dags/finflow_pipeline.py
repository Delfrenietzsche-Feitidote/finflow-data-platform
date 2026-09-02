from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from finflow.orchestration.pipeline import (
    fail_pipeline_run_task,
    complete_pipeline_run_task,
    run_daily_metrics,
    run_fact_transformation,
    run_ingestion_task,
    run_core_transformation,
    start_pipeline_run_task,
    validate_staging_task,
)

default_args = {
    "owner": "finflow",
    "depends_on_past": False,
    "retries": 0,
}


with DAG(
    dag_id="finflow_transaction_pipeline",
    default_args=default_args,
    description="FinFlow transaction ingestion and analytics pipeline",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["finflow", "data-engineering", "etl"],
) as dag:

    start_pipeline_run = PythonOperator(
        task_id="start_pipeline_run",
        python_callable=start_pipeline_run_task,
    )

    ingest_transactions = PythonOperator(
        task_id="ingest_transactions",
        python_callable=run_ingestion_task,
        op_kwargs={
        "count": 10,
        "start_id": 1,
        "batch_date": "{{ ds }}",
        },
    )

    validate_staging = PythonOperator(
        task_id="validate_staging",
        python_callable=validate_staging_task,
    )

    transform_core = PythonOperator(
        task_id="transform_core",
        python_callable=run_core_transformation,
        op_kwargs={
            "batch_date": "{{ ds }}",
        },
    )

    transform_fact = PythonOperator(
        task_id="transform_fact",
        python_callable=run_fact_transformation,
        op_kwargs={
            "batch_date": "{{ ds }}",
        },
    )

    build_daily_metrics = PythonOperator(
        task_id="build_daily_metrics",
        python_callable=run_daily_metrics,
        op_kwargs={
            "batch_date": "{{ ds }}",
        },
    )

    complete_pipeline_run = PythonOperator(
        task_id="complete_pipeline_run",
        python_callable=complete_pipeline_run_task,
    )

    fail_pipeline_run = PythonOperator(
        task_id="fail_pipeline_run",
        python_callable=fail_pipeline_run_task,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    (
        start_pipeline_run
        >> ingest_transactions
        >> validate_staging
        >> transform_core
        >> transform_fact
        >> build_daily_metrics
        >> complete_pipeline_run
    )

    (
        start_pipeline_run
        >> fail_pipeline_run
    )

    (
        ingest_transactions
        >> fail_pipeline_run
    )

    (
        validate_staging
        >> fail_pipeline_run
    )

    (
        transform_core
        >> fail_pipeline_run
    )

    (
        transform_fact
        >> fail_pipeline_run
    )

    (
        build_daily_metrics
        >> fail_pipeline_run
    )