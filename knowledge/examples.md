# Эталонные пары «вопрос → SQL» (few-shot)

> ⚠️ ШАБЛОН под синтетическую схему. Замени на запросы в стиле твоей команды.
>
> ИНВАРИАНТ: вопросы здесь НЕ должны совпадать с вопросами из `eval/cases.yaml`.
> Иначе модель видит эталонные ответы в промпте — это утечка train/test и
> завышенная точность. Примеры учат ПАТТЕРНАМ (джойны, группировка, идиомы
> ClickHouse), а не ответам на конкретные кейсы.

### Вопрос: Сколько событий приходится на каждый тариф?
```sql
select u.plan, count() as events_cnt
from analytics.events e
inner join analytics.users u on e.user_id = u.user_id
group by u.plan
order by events_cnt desc
```

### Вопрос: Средняя длительность сессии по странам
```sql
select u.country, avg(s.duration_seconds) as avg_duration
from analytics.sessions s
inner join analytics.users u on s.user_id = u.user_id
group by u.country
order by avg_duration desc
```

### Вопрос: Сколько событий по неделям за последний месяц?
```sql
select toStartOfWeek(event_date) as week, count() as events_cnt
from analytics.events
where event_date >= today() - 30
group by week
order by week
```

### Вопрос: Какая доля событий — просмотры товара?
```sql
select countIf(event_name = 'view_item') / count() as view_item_share
from analytics.events
```

### Вопрос: Сколько уникальных пользователей заходило с каждой платформы?
```sql
select platform, count(distinct user_id) as users
from analytics.events
group by platform
order by users desc
```

### Вопрос: Сколько в среднем событий приходится на одного пользователя?
```sql
select count() / uniq(user_id) as avg_events_per_user
from analytics.events
```
