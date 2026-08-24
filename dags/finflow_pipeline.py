from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from finflow.orchestration.pipeline import (
    run_daily_metrics,
    run_fact_transformation,
    run_ingestion_task,
    run_core_transformation,
)


default_args = {
    "owner": "finflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="finflow_transaction_pipeline",
    default_args=default_args,
    description="FinFlow transaction ingestion and analytics pipeline",
    schedule=timedelta(days=1),
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["finflow", "data-engineering", "etl"],
) as dag:

    ingest_transactions = PythonOperator(
        task_id="ingest_transactions",
        python_callable=run_ingestion_task,
        op_kwargs={
            "count": 10,
            "start_id": 1,
        },
    )

    transform_core = PythonOperator(
        task_id="transform_core",
        python_callable=run_core_transformation,
    )

    transform_fact = PythonOperator(
        task_id="transform_fact",
        python_callable=run_fact_transformation,
    )

    build_daily_metrics = PythonOperator(
        task_id="build_daily_metrics",
        python_callable=run_daily_metrics,
    )

    ingest_transactions >> transform_core >> transform_fact >> build_daily_metrics