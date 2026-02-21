 # Anomaly Detection & Risk Scoring on Synthetic Transaction Data

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

The dashboard allows interactive filtering by risk band and date range.

Screenshots are available in `/powerbi/screenshots`.

## 📈 Analytical Validation (Notebook)

The notebook validates whether engineered features meaningfully separate anomalies.

### Key findings:
- Anomalies have ~3x higher mean risk_score than normal transactions.
- Velocity (`tx_count_10min`) is the strongest separating signal in this synthetic setup.
- High risk band captures 24.39% anomaly rate across 82 transactions.
- Risk band thresholds may require tuning if Medium band outperforms High in anomaly rate.

The notebook focuses on validation and exploratory analysis — not machine learning — reinforcing analytical reasoning.

## 🧠 Key Insights

- Behavioural features significantly improve anomaly separation.
- Velocity bursts create clear clustering in risk_score distribution.
- Night-time activity and city changes meaningfully increase anomaly likelihood.
- Risk scoring can effectively prioritise investigation workload.

## 📁 Repository Structure
```
data/
├── raw/
│   ├── users.csv
│   ├── transactions.csv
│   └── risk_project.db
├── processed/
│   └── transaction_features.csv
notebooks/
└── analysis.ipynb
sql/
└── queries.sql
powerbi/
└── screenshots/
src/
├── generate_data.py
└── feature_engineering.py
README.md
```


## 🛠 Tools Used

- Python (pandas, numpy, matplotlib)
- SQLite
- SQL (window functions)
- Power BI
- Jupyter Notebook

## ⚠ Limitations

- Synthetic data does not capture all real-world fraud complexity.
- Risk score thresholds are rule-based and not statistically optimised.
- Velocity uses fixed 10-minute bucket approximation.

## 🚀 Next Steps

Potential enhancements:
- Calibrate risk band thresholds using precision/recall analysis
- Add rolling 10-minute window velocity method
- Introduce additional behavioural signals (merchant risk, device fingerprinting)
- Compare rule-based scoring with logistic regression model
