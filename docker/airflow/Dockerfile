FROM apache/airflow:2.10.5

USER airflow

RUN pip install --no-cache-dir \
    "psycopg[binary]>=3.3.4" \
    "pydantic-settings>=2.15.0"