"""Static SQL validation: only a single read-only SELECT is allowed.

This is the AST-level guard (sqlglot). The ClickHouse read-only *user* is the
second, authoritative line of defence at execution time — but rejecting unsafe
SQL here gives a clear error and avoids a pointless round-trip to the DB.
"""
from __future__ import annotations

import sqlglot
from sqlglot import exp

# Statement types that must never appear.
_FORBIDDEN = (
    exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter,
    exp.TruncateTable, exp.Command,  # Command catches DDL/admin sqlglot doesn't model
)


def validate_sql(sql: str) -> tuple[bool, str | None]:
    """Return (ok, error). ok=True means a single safe SELECT."""
    try:
        statements = sqlglot.parse(sql, dialect="clickhouse")
    except Exception as exc:  # noqa: BLE001 - surface parse errors to the caller
        return False, f"SQL parse error: {exc}"

    statements = [s for s in statements if s is not None]
    if len(statements) != 1:
        return False, "Only a single statement is allowed."

    stmt = statements[0]

    # Top-level must be a SELECT (optionally wrapped in a WITH/CTE).
    root = stmt
    if isinstance(root, exp.With):
        root = root.this
    if not isinstance(root, exp.Select):
        return False, "Only SELECT statements are allowed."

    # No forbidden node anywhere in the tree (e.g. subquery INSERT).
    for node in stmt.walk():
        if isinstance(node, _FORBIDDEN):
            return False, f"Forbidden statement type: {type(node).__name__}."

    return True, None
