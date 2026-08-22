from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class PostgresConnection:
    """Compatibility wrapper for the SQLite-style calls used by the Flask MVP."""

    def __init__(self, url: str):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError(
                "Postgres support requires psycopg[binary]. Install backend/requirements.txt."
            ) from exc

        self._connection = psycopg.connect(url, row_factory=dict_row)

    @staticmethod
    def _translate(query: str) -> str:
        if query.lstrip().upper().startswith("INSERT OR IGNORE"):
            query = query.replace("INSERT OR IGNORE", "INSERT", 1)
            query = query.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
        return query.replace("?", "%s")

    def execute(self, query: str, params: tuple[Any, ...] = ()):
        return self._connection.execute(self._translate(query), params)

    def executemany(self, query: str, params: list[tuple[Any, ...]]):
        return self._connection.executemany(self._translate(query), params)

    def commit(self) -> None:
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()


def is_postgres_url(value: str) -> bool:
    return value.startswith(("postgresql://", "postgres://"))


def open_database(database_url: str, sqlite_path: str):
    if is_postgres_url(database_url):
        return PostgresConnection(database_url)

    path = database_url.removeprefix("sqlite:///") if database_url.startswith("sqlite:///") else database_url
    path = path or sqlite_path
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def is_postgres_connection(connection: object) -> bool:
    return isinstance(connection, PostgresConnection)
