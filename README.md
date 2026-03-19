 # Anomaly Detection & Risk Scoring on Synthetic Transaction Data
Built an end-to-end fraud monitoring analytics project using SQL, Python, SQLite, and Power BI on 40,000+ synthetic UK banking transactions. I engineered behavioural risk indicators, investigated suspicious patterns with SQL window functions, and developed an interactive dashboard to help prioritise high-risk activity for analyst review. The project simulates how a junior data analyst could support fraud operations with KPI reporting, anomaly investigation, and decision-ready insight.

## 📌 Business Problem

Financial institutions and digital platforms process thousands of transactions daily. Identifying suspicious or anomalous behaviour early is critical for:

- Fraud prevention
- Operational risk monitoring
- Customer protection
- Reducing financial losses

This project simulates a real-world transaction monitoring system by generating synthetic behavioural data and building a rule-based risk scoring framework to detect anomalous activity.

The goal is not just to flag anomalies, but to demonstrate how an analyst would:
- Engineer behavioural risk signals
- Validate their effectiveness
- Investigate patterns using SQL
- Communicate insights through dashboards

## 🧱 Project Overview

This is an end-to-end analytics project including:

- Synthetic data generation (~40,000+ transactions)
- Behavioural feature engineering
- SQL investigation with window functions
- Risk scoring and band classification
- Interactive Power BI dashboard
- Analytical validation via Python notebook

### Dataset Summary
- ~2,000 users
- ~40k+ transactions
- 30-day activity window
- ~2% anomaly injection rate
- UK cities, device types, risk bands

Each transaction includes:
- `transaction_id`
- `user_id`
- `timestamp`
- `amount_gbp`
- `city`
- `device`
- `ip_risk_band`
- `is_anomaly` (ground truth)

## 🔍 How the Data Was Generated

The dataset was built in three stages:

### 1️⃣ User Simulation
Each user is assigned:
- Home city (weighted distribution)
- Preferred device
- Account age
- Baseline transaction behaviour
- IP risk band

User spending follows a skewed (log-normal) distribution to mimic real financial activity.

### 2️⃣ Transaction Generation
For each user:
- Transaction count sampled using a Poisson distribution
- Transactions generated within a 30-day window
- City and device stable ~85–90% of the time
- Amounts centered around user-specific baseline
- Timestamps distributed realistically

### 3️⃣ Anomaly Injection (~2%)
Four anomaly patterns were injected:
- High-value spike (extreme transaction amount)
- Velocity burst (3–6 transactions within 10 minutes)
- Night-time activity (00:00–05:00)
- Geographical jump (sudden city change)

Velocity bursts create additional rows to simulate realistic fraud clusters.

## ⚙️ Feature Engineering

Behavioural signals were engineered to support risk scoring:

- `time_since_prev_min` – minutes since previous user transaction
- `tx_count_10min` – velocity indicator (transactions in 10-minute bucket)
- `is_night_tx` – 00:00–05:00 activity
- `is_high_amount` – above 95th percentile
- `city_changed` – change from previous transaction location

### Risk Score Formula
A rule-based score combines behavioural signals:

**risk_score =** 
- **(is_high_amount × 3)** + 
- **(is_night_tx × 2)** + 
- **(city_changed × 2)** + 
- **((tx_count_10min ≥ 3) × 3)**


Risk bands:
- Low
- Medium
- High

This simulates how rule-based fraud systems often operate in early-stage monitoring.

## 🗄 SQL Investigation

The dataset was loaded into SQLite and analysed using SQL.

### Key SQL techniques used:
- Aggregations for KPI calculation
- Window functions (LAG, ROW_NUMBER)
- Behavioural sequence analysis
- Risk band performance evaluation

### Example analysis performed:
- Overall anomaly rate
- Anomaly rate by city and device
- Top risky users (minimum sample size filter)
- Rapid + high-risk events (<5 minute gaps)
- Velocity cluster detection

This demonstrates strong analytical SQL skills beyond simple SELECT statements.

## 📊 Dashboard (Power BI)

Two main report pages were created:

### Executive Overview
- Total transactions
- Total anomalies
- Anomaly rate %
- Average risk score
- Monthly anomaly trend
- Breakdown by city and device

### Investigation View
- Scatter clustering of risk_score vs amount
- High-risk users table
- Velocity band distribution
- Hourly activity heatmap

# Anomaly Detection & Risk Scoring on Synthetic Transaction Data

> **End-to-end fraud monitoring analytics** — Python ETL pipeline → SQL investigation → Power BI dashboard.
> Built on 40,000+ synthetic UK banking transactions. Anomalies flagged carry **~3× higher risk scores** than normal transactions.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://python.org)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=flat&logo=powerbi)](powerBI/)
[![SQL](https://img.shields.io/badge/SQL-SQLite-003B57?style=flat&logo=sqlite)](src/queries.sql)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=flat)](LICENSE)

---

## 📌 Business Problem

Financial institutions and digital platforms process thousands of transactions daily. Identifying suspicious or anomalous behaviour early is critical for fraud prevention, operational risk monitoring, and customer protection.

This project simulates a real-world transaction monitoring system by generating synthetic behavioural data and building a rule-based risk scoring framework. The goal is to demonstrate how an analyst would:
- Engineer behavioural risk signals from raw transaction data
- Validate their effectiveness statistically
- Investigate patterns using SQL window functions
- Communicate findings through business-facing dashboards

---

## 📊 Dashboard Preview

### Executive Overview
<img width="1200" height="800" alt="17739621076573820979079475303994" src="https://github.com/user-attachments/assets/8917026b-9b06-432b-8f46-f6d7ffd662f8" />

### Investigation View
<img width="1200" height="800" alt="17739620375759114224907800557847" src="https://github.com/user-attachments/assets/ea421c22-6b1d-4402-8066-62b8b6b14ccb" />


> Download the `.pbix` from `/powerBI/` and open in Power BI Desktop for full interactive filtering.

---

## 🧱 Project Overview

| Stage | Detail |
|---|---|
| Data Generation | ~40,000+ synthetic transactions, ~2,000 users, 30-day window |
| Feature Engineering | Velocity, location change, night activity, high-amount flags |
| SQL Investigation | Window functions, aggregations, risk band analysis (SQLite) |
| Risk Scoring | Rule-based weighted score → Low / Medium / High bands |
| Validation | Python notebook confirming ~3× risk score separation |
| Dashboard | Interactive Power BI — Executive + Investigation views |

---

## 🔍 Data Generation

**Users:** home city, preferred device, account age, baseline spending (log-normal distribution)

**Transactions:** Poisson-distributed count per user · city/device stable ~85–90% · realistic 30-day timestamps

**Anomaly injection (~2%):**
- High-value spike (extreme transaction amount)
- Velocity burst (3–6 transactions within 10 minutes)
- Night-time activity (00:00–05:00)
- Geographical jump (sudden city change)

---

## ⚙️ Feature Engineering

| Feature | Description |
|---|---|
| `time_since_prev_min` | Minutes since previous user transaction |
| `tx_count_10min` | Velocity — transactions in 10-minute bucket |
| `is_night_tx` | 1 if transaction 00:00–05:00 |
| `is_high_amount` | 1 if above 95th percentile for that user |
| `city_changed` | 1 if city differs from previous transaction |

**Risk Score Formula:**
```
risk_score = (is_high_amount × 3) + (is_night_tx × 2) + (city_changed × 2) + ((tx_count_10min ≥ 3) × 3)
```
Bands: **Low · Medium · High**

---

## 🗄 SQL Investigation

Key techniques: `LAG()`, `ROW_NUMBER()`, aggregations, subqueries with sample-size filters.

**Example — Rapid high-risk events:**
```sql
SELECT user_id, transaction_id, amount_gbp, risk_score, time_since_prev_min
FROM transaction_features
WHERE time_since_prev_min < 5
  AND risk_score >= 5
ORDER BY risk_score DESC
LIMIT 20;
```

> Full query set in [`src/queries.sql`](src/queries.sql) · SQL output screenshots in [`sql_results/images/`](sql_results/images/)

---

## 📈 Analytical Validation

Key findings from the validation notebook:
- Anomalies have **~3× higher mean risk_score** than normal transactions
- **Velocity** (`tx_count_10min`) is the strongest separating signal
- High risk band captures **24.39% anomaly rate** across 82 transactions
- Rule-based thresholds are conservative — medium band occasionally outperforms high band, flagging threshold calibration as a next step

---

## 🚀 Next Steps

- [ ] Add logistic regression comparison — validate whether engineered features support a predictive model as well as a rule-based one
- [ ] Calibrate risk band thresholds using precision/recall analysis
- [ ] Add rolling 10-minute window velocity (more accurate than fixed bucket)
- [ ] Introduce additional signals: merchant risk, device fingerprinting

---

## ⚠ Limitations

- Synthetic data does not capture full real-world fraud complexity
- Risk score thresholds are rule-based, not statistically optimised
- Velocity uses a fixed 10-minute bucket approximation

---

## 🛠 Setup

```bash
pip install pandas numpy matplotlib scikit-learn jupyter

python src/generate_data.py        # generate synthetic data
python src/feature_engineering.py  # engineer features
jupyter notebook notebooks/analysis.ipynb
```

---

## 📁 Structure

```
data/raw/          → users.csv, transactions.csv, risk_project.db
data/processed/    → transaction_features.csv
notebooks/         → analysis.ipynb
sql_results/images/→ SQL output screenshots
powerBI/           → .pbix file + screenshots/
src/               → generate_data.py, feature_engineering.py, queries.sql
```

---

## 👩‍💻 Author

**Seerat Kaur** — Junior Data Analyst
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/seerat-kaur-4878bb249/)
[![GitHub](https://img.shields.io/badge/GitHub-KaurSeerat-181717?style=flat&logo=github)](https://github.com/KaurSeerat)
