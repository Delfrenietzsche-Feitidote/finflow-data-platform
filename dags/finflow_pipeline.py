from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from finflow.orchestration.pipeline import run_pipeline


default_args = {
    "owner": "finflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def run_finflow_pipeline(**context):
    logical_date = context["logical_date"]

    return run_pipeline(
        count=10,
        start_id=1,
        batch_date=logical_date.date(),
    )


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

    run_pipeline_task = PythonOperator(
        task_id="run_finflow_pipeline",
        python_callable=run_finflow_pipeline,
    )