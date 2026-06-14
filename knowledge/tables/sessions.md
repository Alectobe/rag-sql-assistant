# Таблица `analytics.sessions`

> ⚠️ ШАБЛОН (синтетическая схема). Замени на реальную структуру.

**Назначение:** пользовательские сессии и их длительность.

**Движок:** `MergeTree`, ключ сортировки `(started_at, session_id)`.

## Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `session_id` | `UInt64` | Уникальный ID сессии (первичный) |
| `user_id` | `UInt64` | ID пользователя, ссылается на `analytics.users.user_id` |
| `started_at` | `DateTime` | Время начала сессии |
| `duration_seconds` | `UInt32` | Длительность сессии в секундах |
| `platform` | `LowCardinality(String)` | Платформа |

## Категориальные значения

- `platform`: `ios`, `android`, `web`

## Типичные джойны

- `sessions.user_id = users.user_id`
- `sessions.session_id = events.session_id`
