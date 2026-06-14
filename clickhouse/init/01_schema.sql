-- Synthetic schema for local development (MVP-0).
-- Replace with your real DDL (SHOW CREATE TABLE) when available.

CREATE DATABASE IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.users
(
    user_id      UInt64,
    signup_date  Date,
    country      LowCardinality(String),
    plan         LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY user_id;

CREATE TABLE IF NOT EXISTS analytics.sessions
(
    session_id        UInt64,
    user_id           UInt64,
    started_at        DateTime,
    duration_seconds  UInt32,
    platform          LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY (started_at, session_id);

CREATE TABLE IF NOT EXISTS analytics.events
(
    event_date  Date,
    event_time  DateTime,
    user_id     UInt64,
    event_name  LowCardinality(String),
    platform    LowCardinality(String),
    session_id  UInt64
)
ENGINE = MergeTree
ORDER BY (event_date, user_id);
