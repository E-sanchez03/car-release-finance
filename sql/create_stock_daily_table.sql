CREATE DATABASE IF NOT EXISTS stocks_db;

CREATE TABLE IF NOT EXISTS stocks_db.stock_daily
(
    `ticker` String,
    `event_date` Date,
    `open` Float64,
    `high` Float64,
    `low` Float64,
    `close` Float64,
    `volume` UInt64
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (ticker, event_date);