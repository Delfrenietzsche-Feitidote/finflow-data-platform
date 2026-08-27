FROM apache/airflow:2.10.5

USER airflow

RUN pip install --no-cache-dir \
    "psycopg[binary]>=3.3.4" \
    "psycopg2-binary>=2.9,<3" \
    "pydantic-settings>=2.15.0"