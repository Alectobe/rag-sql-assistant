"""Turn a query result into a natural-language answer (Russian)."""
from __future__ import annotations

from app import llm
from app.config import settings
from app.execute import QueryResult

SYSTEM_PROMPT = """\
Ты — продуктовый аналитик. Тебе дают вопрос пользователя и результат \
SQL-запроса (таблица). Кратко и по делу ответь на вопрос на русском языке, \
опираясь только на данные из результата. Не выдумывай цифры. Если результат \
пустой — так и скажи. Не показывай SQL.
"""

_MAX_ROWS_IN_PROMPT = 50


def _render_table(result: QueryResult) -> str:
    if result.row_count == 0:
        return "(пустой результат)"
    header = " | ".join(result.columns)
    body_rows = result.rows[:_MAX_ROWS_IN_PROMPT]
    body = "\n".join(" | ".join(str(c) for c in row) for row in body_rows)
    suffix = ""
    if result.row_count > _MAX_ROWS_IN_PROMPT:
        suffix = f"\n... (ещё {result.row_count - _MAX_ROWS_IN_PROMPT} строк)"
    return f"{header}\n{body}{suffix}"


def interpret(question: str, result: QueryResult) -> str:
    user = f"Вопрос:\n{question}\n\nРезультат запроса:\n{_render_table(result)}"
    return llm.complete(
        SYSTEM_PROMPT, user, model=settings.interpretation_model, max_tokens=1000
    )
