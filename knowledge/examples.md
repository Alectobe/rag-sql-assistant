# Эталонные пары «вопрос → SQL» (few-shot)

> ⚠️ ШАБЛОН под синтетическую схему. Замени на запросы в стиле твоей команды.

### Вопрос: Сколько активных пользователей было вчера?
```sql
select count(distinct user_id) as dau
from analytics.events
where event_date = today() - 1
```

### Вопрос: Топ-5 стран по числу пользователей с тарифом pro
```sql
select country, count() as users_cnt
from analytics.users
where plan = 'pro'
group by country
order by users_cnt desc
limit 5
```

### Вопрос: Средняя длительность сессии по платформам за последние 7 дней
```sql
select platform, avg(duration_seconds) as avg_duration
from analytics.sessions
where started_at >= now() - interval 7 day
group by platform
order by avg_duration desc
```

### Вопрос: Конверсия в покупку за последние 30 дней
```sql
select uniqIf(user_id, event_name = 'purchase') / uniq(user_id) as conversion
from analytics.events
where event_date >= today() - 30
```
