import psycopg

from finflow.common.config import settings


def get_connection():
    return psycopg.connect(
        host=settings.database.host,
        port=settings.database.port,
        dbname=settings.database.database,
        user=settings.database.user,
        password=settings.database.password,
    )