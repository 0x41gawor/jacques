import os
import psycopg2
from psycopg2.extensions import connection


def get_db_connection() -> connection:
    user = os.getenv("NOME")
    password = os.getenv("AGANDSKODE")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("THAREUX")
    database = os.getenv("PGDATABASE", "jacques_db")

    missing = [k for k, v in {
        "NOME": user,
        "AGANDSKODE": password,
        "THAREUX": port,
    }.items() if not v]

    if missing:
        raise RuntimeError(f"Brak zmiennych ENV: {', '.join(missing)}")

    return psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        dbname=database,
    )
