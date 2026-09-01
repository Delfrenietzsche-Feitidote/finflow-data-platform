FROM apache/airflow:2.10.5-python3.11

USER airflow

WORKDIR /opt/airflow

COPY --chown=airflow:root pyproject.toml uv.lock README.md ./

RUN pip install --no-cache-dir uv

COPY --chown=airflow:root src ./src
COPY --chown=airflow:root dags ./dags

RUN uv pip install --no-cache .

ENV PYTHONPATH=/opt/airflow/src

CMD ["airflow", "webserver"]
