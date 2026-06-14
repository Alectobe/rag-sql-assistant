"""ClickHouse execution under the read-only user."""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import clickhouse_connect

from app.config import settings


@dataclass
class QueryResult:
    columns: list[str] = field(default_factory=list)
    rows: list[list] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.rows)


@lru_cache(maxsize=1)
def _client():
    return clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
        database=settings.clickhouse_database,
    )


def explain(sql: str) -> tuple[bool, str | None]:
    """Validate syntax/semantics cheaply via EXPLAIN. Returns (ok, error)."""
    try:
        _client().query(f"EXPLAIN {sql}")
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def run(sql: str) -> QueryResult:
    """Execute SQL and return columns + rows (capped by the read-only profile)."""
    result = _client().query(
        sql,
        settings={
            "max_result_rows": settings.max_result_rows,
            "max_execution_time": settings.query_timeout_seconds,
        },
    )
    rows = [list(r) for r in result.result_rows]
    return QueryResult(columns=list(result.column_names), rows=rows)
