-- ============================================================
-- Anomaly / Risk Scoring Project
-- SQL Investigation Pack (SQLite)
-- Table: transaction_features
-- ============================================================

-- ------------------------------------------------------------
--  Quick sanity checks (QA)
-- ------------------------------------------------------------


-- Row count
SELECT COUNT(*) AS total_rows
FROM transaction_features;

-- Date range
SELECT
  MIN(timestamp) AS min_ts,
  MAX(timestamp) AS max_ts
FROM transaction_features;

-- Q0.3: Duplicate transaction_id check
SELECT transaction_id, COUNT(*) AS cnt
FROM transaction_features
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- ------------------------------------------------------------
-- KPI / summary queries (aggregations)
-- ------------------------------------------------------------

-- Overall anomaly rate
SELECT
  COUNT(*) AS total_tx,
  SUM(is_anomaly) AS anomaly_count,
  ROUND(SUM(is_anomaly) * 100.0 / COUNT(*), 2) AS anomaly_rate_pct
FROM transaction_features;

-- Anomaly rate by city
SELECT
  city,
  COUNT(*) AS total_tx,
  SUM(is_anomaly) AS anomaly_count,
  ROUND(SUM(is_anomaly) * 100.0 / COUNT(*), 2) AS anomaly_rate_pct
FROM transaction_features
GROUP BY city
ORDER BY anomaly_rate_pct DESC;

-- Anomaly rate by device
SELECT
  device,
  COUNT(*) AS total_tx,
  SUM(is_anomaly) AS anomaly_count,
  ROUND(SUM(is_anomaly) * 100.0 / COUNT(*), 2) AS anomaly_rate_pct
FROM transaction_features
GROUP BY device
ORDER BY anomaly_rate_pct DESC;

-- Risk band distribution + anomaly rate per band
SELECT
  risk_band,
  COUNT(*) AS total_tx,
  SUM(is_anomaly) AS anomaly_count,
  ROUND(SUM(is_anomaly) * 100.0 / COUNT(*), 2) AS anomaly_rate_pct,
  ROUND(AVG(risk_score), 2) AS avg_risk_score
FROM transaction_features
GROUP BY risk_band
ORDER BY avg_risk_score DESC;


-- ------------------------------------------------------------
-- Investigation queries (drill-down)
-- ------------------------------------------------------------

-- Top 20 highest risk transactions
SELECT
  transaction_id,
  user_id,
  timestamp,
  city,
  device,
  amount_gbp,
  risk_score,
  risk_band,
  is_anomaly
FROM transaction_features
ORDER BY risk_score DESC, amount_gbp DESC
LIMIT 20;

-- Top 10 users by anomaly rate (minimum sample size)
SELECT
  user_id,
  COUNT(*) AS total_tx,
  SUM(is_anomaly) AS anomaly_count,
  ROUND(SUM(is_anomaly) * 100.0 / COUNT(*), 2) AS anomaly_rate_pct,
  ROUND(AVG(risk_score), 2) AS avg_risk_score
FROM transaction_features
GROUP BY user_id
HAVING COUNT(*) >= 10
ORDER BY anomaly_rate_pct DESC, avg_risk_score DESC
LIMIT 10;

--Bursts (velocity): list rows where tx_count_10min >= 3
SELECT
  user_id,
  transaction_id,
  timestamp,
  tx_count_10min,
  risk_score,
  is_anomaly
FROM transaction_features
WHERE tx_count_10min >= 3
ORDER BY tx_count_10min DESC, user_id, timestamp;


-- ------------------------------------------------------------
-- Window function queries 
-- ------------------------------------------------------------

-- Minutes since previous transaction (LAG)
-- (This reproduces time_since_prev_min purely in SQL)
SELECT *
FROM (
  SELECT
    user_id,
    transaction_id,
    timestamp,
    amount_gbp,
    (strftime('%s', timestamp) -
     strftime('%s', LAG(timestamp) OVER (
       PARTITION BY user_id
       ORDER BY timestamp
     ))
    ) / 60.0 AS minutes_since_prev
  FROM transaction_features
)
ORDER BY user_id, timestamp;

-- Top 2 risky transactions per user (ROW_NUMBER)
SELECT
  user_id,
  transaction_id,
  timestamp,
  risk_score,
  risk_band,
  is_anomaly
FROM (
  SELECT
    user_id,
    transaction_id,
    timestamp,
    risk_score,
    risk_band,
    is_anomaly,
    ROW_NUMBER() OVER (
      PARTITION BY user_id
      ORDER BY risk_score DESC
    ) AS rn
  FROM transaction_features
)
WHERE rn <= 2
ORDER BY user_id, rn;

-- Rapid + high-risk events (<5 minutes gap AND risk_score >= 5)
SELECT *
FROM (
  SELECT
    user_id,
    transaction_id,
    timestamp,
    risk_score,
    risk_band,
    is_anomaly,
    (strftime('%s', timestamp) -
     strftime('%s', LAG(timestamp) OVER (
       PARTITION BY user_id
       ORDER BY timestamp
     ))
    ) / 60.0 AS minutes_since_prev
  FROM transaction_features
)
WHERE minutes_since_prev < 5
  AND risk_score >= 5
ORDER BY user_id, timestamp;
