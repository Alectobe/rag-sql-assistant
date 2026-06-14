# Таблица `analytics.events`

> ⚠️ ШАБЛОН (синтетическая схема для локальной разработки). Замени на реальный
> `SHOW CREATE TABLE` и описания из твоей компании, не меняя формат документа.

**Назначение:** продуктовые события пользователей (открытие приложения, покупки,
просмотры и т.д.). Основная таблица для метрик активности и конверсии.

**Движок:** `MergeTree`, ключ сортировки `(event_date, user_id)`.

## Поля

| Поле | Тип | Описание |
|------|-----|----------|
| `event_date` | `Date` | Дата события (для партиционирования/фильтрации по дням) |
| `event_time` | `DateTime` | Точное время события |
| `user_id` | `UInt64` | ID пользователя, ссылается на `analytics.users.user_id` |
| `event_name` | `LowCardinality(String)` | Тип события |
| `platform` | `LowCardinality(String)` | Платформа |
| `session_id` | `UInt64` | ID сессии, ссылается на `analytics.sessions.session_id` |

## Категориальные значения

- `event_name`: `app_open`, `purchase`, `add_to_cart`, `view_item`, `logout`
- `platform`: `ios`, `android`, `web`

## Типичные джойны

- `events.user_id = users.user_id` — атрибуты пользователя (страна, тариф)
- `events.session_id = sessions.session_id` — длительность сессии
