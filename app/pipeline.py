"""End-to-end orchestration: question -> SQL -> validate -> execute -> answer.

On execution/validation failure, the error is fed back to the model for up to
``MAX_SQL_RETRIES`` self-correction attempts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from app import execute, generate, interpret, validate
from app.config import settings
from app.execute import QueryResult
from app.logging_store import log_request


@dataclass
class AskResult:
    question: str
    sql: str | None = None
    notes: str = ""
    answer: str | None = None
    columns: list[str] = field(default_factory=list)
    rows: list[list] = field(default_factory=list)
    attempts: int = 0
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _attempt(question: str, retry: dict | None) -> tuple[str, str, QueryResult]:
    """One generate -> validate -> explain -> run cycle. Raises on failure."""
    gen = generate.generate_sql(question, retry=retry)

    ok, err = validate.validate_sql(gen.sql)
    if not ok:
        raise _SqlFailure(gen.sql, f"Validation failed: {err}")

    ok, err = execute.explain(gen.sql)
    if not ok:
        raise _SqlFailure(gen.sql, f"EXPLAIN failed: {err}")

    try:
        result = execute.run(gen.sql)
    except Exception as exc:  # noqa: BLE001
        raise _SqlFailure(gen.sql, f"Execution failed: {exc}") from exc

    return gen.sql, gen.notes, result


class _SqlFailure(Exception):
    def __init__(self, sql: str, error: str):
        super().__init__(error)
        self.sql = sql
        self.error = error


def ask(question: str) -> AskResult:
    out = AskResult(question=question)
    retry: dict | None = None
    last_error: str | None = None

    for attempt in range(settings.max_sql_retries + 1):
        out.attempts = attempt + 1
        try:
            sql, notes, result = _attempt(question, retry)
        except _SqlFailure as fail:
            last_error = fail.error
            retry = {"sql": fail.sql, "error": fail.error}
            out.sql = fail.sql
            continue
        except Exception as exc:  # noqa: BLE001 - generation/parse failure
            last_error = str(exc)
            break

        out.sql, out.notes = sql, notes
        out.columns, out.rows = result.columns, result.rows
        out.answer = interpret.interpret(question, result)
        out.error = None
        _log(out)
        return out

    out.error = last_error
    _log(out)
    return out


def _log(out: AskResult) -> None:
    log_request(
        {
            "backend": settings.llm_backend,
            "question": out.question,
            "sql": out.sql,
            "attempts": out.attempts,
            "row_count": len(out.rows),
            "error": out.error,
        }
    )
