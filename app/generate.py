"""Text-to-SQL generation step.

Asks the model for a strict JSON object ``{"sql": ..., "notes": ...}`` and
parses it. JSON-via-prompt is used (rather than provider-specific structured
output) so the exact same code path works on Claude and on a local Qwen.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app import llm
from app.config import settings
from app.context import build_context

SYSTEM_PROMPT = """\
Ты — эксперт по аналитике и ClickHouse SQL. По вопросу пользователя на русском \
языке ты пишешь ОДИН SELECT-запрос к ClickHouse, используя ТОЛЬКО таблицы и \
поля из предоставленного контекста схемы.

Правила:
- Только SELECT. Никаких INSERT/UPDATE/ALTER/DROP/CREATE и нескольких запросов.
- Используй только реально существующие в контексте таблицы и колонки. Не \
выдумывай поля.
- Стиль ClickHouse: ключевые слова в нижнем регистре, при необходимости CTE \
(with ... as), функции дат ClickHouse (today(), toStartOfDay, и т.п.).
- Всегда указывай базу данных в имени таблицы (database.table).
- Если вопрос неоднозначен, выбери самую частую разумную трактовку метрики из \
контекста.

Верни СТРОГО JSON-объект без markdown-обёртки:
{"sql": "<один SELECT-запрос>", "notes": "<короткое пояснение трактовки на русском>"}
"""

_RETRY_TEMPLATE = """\
Предыдущий запрос завершился ошибкой при проверке/выполнении в ClickHouse.

Запрос:
{sql}

Ошибка:
{error}

Исправь запрос. Верни СТРОГО тот же JSON-формат.
"""


@dataclass
class Generation:
    sql: str
    notes: str
    raw: str


def _extract_json(text: str) -> dict:
    """Best-effort extraction of the JSON object from a model response."""
    # Strip ```json fences if present.
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else text
    # Fall back to the first {...} span.
    if not fenced:
        brace = re.search(r"\{.*\}", candidate, re.DOTALL)
        if brace:
            candidate = brace.group(0)
    return json.loads(candidate)


def _build_user_prompt(question: str, retry: dict | None) -> str:
    context = build_context(question)
    base = f"Контекст схемы:\n{context}\n\nВопрос пользователя:\n{question}"
    if retry:
        base += "\n\n" + _RETRY_TEMPLATE.format(sql=retry["sql"], error=retry["error"])
    return base


def generate_sql(question: str, retry: dict | None = None) -> Generation:
    """Generate SQL for a question. ``retry`` carries the prior failed sql+error."""
    user = _build_user_prompt(question, retry)
    raw = llm.complete(SYSTEM_PROMPT, user, model=settings.generation_model)
    try:
        data = _extract_json(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Could not parse model output as JSON: {exc}\n---\n{raw}") from exc
    sql = (data.get("sql") or "").strip().rstrip(";")
    if not sql:
        raise ValueError(f"Model returned empty SQL.\n---\n{raw}")
    return Generation(sql=sql, notes=(data.get("notes") or "").strip(), raw=raw)
