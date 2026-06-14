-- Deterministic synthetic data so the pipeline works end-to-end before the
-- real ClickHouse is connected. Replace together with 01_schema.sql.

INSERT INTO analytics.users
SELECT
    number + 1                                            AS user_id,
    toDate('2026-01-01') + toIntervalDay(number % 150)    AS signup_date,
    ['RU','US','DE','FR','BR'][(number % 5) + 1]          AS country,
    ['free','pro','enterprise'][(number % 3) + 1]        AS plan
FROM numbers(500);

INSERT INTO analytics.sessions
SELECT
    number + 1                                                          AS session_id,
    (number % 500) + 1                                                  AS user_id,
    toDateTime('2026-05-01 00:00:00') + toIntervalSecond(number % (30 * 86400)) AS started_at,
    (number % 1800) + 30                                                AS duration_seconds,
    ['ios','android','web'][(number % 3) + 1]                          AS platform
FROM numbers(2000);

INSERT INTO analytics.events
SELECT
    toDate(toDateTime('2026-05-01 00:00:00') + toIntervalSecond(number % (30 * 86400))) AS event_date,
    toDateTime('2026-05-01 00:00:00') + toIntervalSecond(number % (30 * 86400))         AS event_time,
    (number % 500) + 1                                                  AS user_id,
    ['app_open','purchase','add_to_cart','view_item','logout'][(number % 5) + 1] AS event_name,
    ['ios','android','web'][(number % 3) + 1]                          AS platform,
    (number % 2000) + 1                                                AS session_id
FROM numbers(20000);
