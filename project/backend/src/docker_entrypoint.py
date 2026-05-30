import os
import subprocess
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError


DATABASE_URL = os.getenv("DATABASE_URL")
MAX_WAIT_SECONDS = int(os.getenv("DB_WAIT_TIMEOUT", "60"))


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def create_database_if_missing() -> None:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    target_url = make_url(DATABASE_URL)
    database_name = target_url.database

    if not database_name:
        raise RuntimeError("DATABASE_URL must include a database name")

    admin_url = target_url.set(database="postgres")
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with engine.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
            {"database_name": database_name},
        ).scalar()

        if exists:
            print(f"Database {database_name!r} already exists", flush=True)
            return

        connection.execute(text(f"CREATE DATABASE {quote_identifier(database_name)}"))
        print(f"Database {database_name!r} created", flush=True)


def wait_for_database() -> None:
    started_at = time.monotonic()

    while True:
        try:
            create_database_if_missing()
            return
        except OperationalError as error:
            elapsed = time.monotonic() - started_at

            if elapsed >= MAX_WAIT_SECONDS:
                raise RuntimeError(
                    f"Database did not become ready after {MAX_WAIT_SECONDS} seconds"
                ) from error

            print("Waiting for database to become ready...", flush=True)
            time.sleep(2)


def run_migrations() -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
    )


def start_api() -> None:
    os.execvp(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
    )


if __name__ == "__main__":
    wait_for_database()
    run_migrations()
    start_api()
