# RAG SQL Assistant (MVP-0)

Text-to-SQL ассистент для продуктовых аналитиков поверх ClickHouse.
Вопрос на русском → SQL → выполнение под read-only пользователем → ответ
на естественном языке.

MVP-0: схема целиком кладётся в промпт (без векторного хранилища — это фаза 2).
LLM-слой провайдер-агностичен: **Claude API** (дефолт) или **локальная модель**
через OpenAI-совместимый эндпоинт (Ollama/vLLM с Qwen) — переключается одной
переменной `LLM_BACKEND`.

## Архитектура

```
вопрос → generate (LLM) → validate (sqlglot) → EXPLAIN → run (ClickHouse RO)
        → interpret (LLM) → ответ        ↑__ retry с текстом ошибки (self-correction)
```

| Слой | Файл | Роль |
|------|------|------|
| Конфиг | `app/config.py` | настройки из `.env` |
| LLM | `app/llm.py` | единый `complete()`, бэкенды anthropic / local |
| Контекст | `app/context.py` | сборка схемы из `knowledge/` (точка расширения под RAG) |
| Генерация | `app/generate.py` | вопрос+контекст → SQL (JSON) |
| Валидация | `app/validate.py` | только одиночный SELECT (AST) |
| Выполнение | `app/execute.py` | EXPLAIN + запуск под RO-юзером |
| Интерпретация | `app/interpret.py` | результат → ответ на русском |
| Пайплайн | `app/pipeline.py` | склейка + self-correction |
| Логи | `app/logging_store.py` | jsonl всех запросов |
| API | `app/api.py` | `POST /ask` |
| UI | `ui/streamlit_app.py` | простой чат |
| Оценка | `eval/run_eval.py` | execution accuracy |

## Быстрый старт

```bash
# 1. Зависимости
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Конфиг
cp .env.example .env   # впиши ANTHROPIC_API_KEY (или настрой local-бэкенд)

# 3. Локальный ClickHouse с синтетикой
docker compose up -d

# 4. UI
streamlit run ui/streamlit_app.py
#    или API:
uvicorn app.api:app --reload
```

### Локальная модель вместо API
```bash
ollama pull qwen2.5-coder:7b      # на M2 Pro 16GB идёт комфортно
# в .env:
#   LLM_BACKEND=local
#   GENERATION_MODEL=qwen2.5-coder:7b
#   INTERPRETATION_MODEL=qwen2.5-coder:7b
```

### Оценка качества
```bash
python eval/run_eval.py
```

## Подключение реальной схемы компании
1. Замени `clickhouse/init/01_schema.sql` на реальный DDL (`SHOW CREATE TABLE`).
2. Обнови `knowledge/tables/*.md`, `knowledge/metrics.md`, `knowledge/examples.md`.
3. Расширь `eval/cases.yaml` своими кейсами.
4. Для боевого ClickHouse — поменяй `CLICKHOUSE_*` в `.env` (контейнер не нужен).

## Фаза 2 (не в MVP-0)
pgvector + ретрив (точка расширения — `app/context.py`), value-linking,
гибридный поиск, human-in-the-loop правка SQL, графики, аутентификация.
