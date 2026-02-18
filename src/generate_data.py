#Generate Users Table

import numpy as np
import pandas as pd
import sqlite3

random_seed=42

n_users=2000
cities=["London","Manchester","Leeds","Bristol","Glasgow","Edinburgh","Leicester","Liverpool","Birmingham","Cambridge","Norwich"]
city_p=[0.35,0.07,0.10,0.06,0.07,0.06,0.04,0.06,0.15,0.02,0.02]


devices = ["mobile", "desktop", "tablet"]
device_p = [0.70, 0.25, 0.05]

# % of transactions to turn into anomalies (plus burst creates extra rows)
ANOMALY_RATE = 0.02

# "Today" for simulation (use current date in real run)
TODAY = pd.Timestamp("2026-02-16")  # matches your project timeframe

np.random.seed(random_seed)

def weighted_choice(options,p,size=None):
    """
    Pick from options using probabilities
    """
    return np.random.choice(options,p=p,size=size)

# # lognormal gives 'right-skewed' vvalues (many small,few large)
# def clipped_lognormal(mu,sigma,low,high,size=None):
#     x=np.random.lognormal(mean=mu,sigma=sigma,size=size)
#     return np.clip(x,low,high)  #np.clip forces values into [low,high]

def random_timestamp_between(start_ts, end_ts):
    """
    Pick a random timestamp uniformly between start_ts and end_ts.
    Safer beginner version: sample in seconds (int64-safe), then convert.
    """
    if start_ts >= end_ts:
        return start_ts
    return start_ts + (end_ts - start_ts) * np.random.random()



# CREATE USERS TABLE
user_id=[f"U{u:06d}" for u in range (n_users)]

home_city=weighted_choice(cities,city_p,size=n_users)
preferred_device=weighted_choice(devices,device_p,size=n_users)


# account age in days: uses a simple clipped exponential-like distribution
# (more small ages, fewer large ages), then clipped to [0, 2000]
account_age_days = np.random.exponential(scale=250, size=n_users).astype(int)
account_age_days = np.clip(account_age_days, 0, 2000)

signup_date = (TODAY - pd.to_timedelta(account_age_days, unit="D")).normalize()

# IP risk band correlated with account age (simple rules)
ip_risk_band = []
for age in account_age_days:
    if age < 14:
        ip_risk_band.append(weighted_choice(["low","medium","high"], [0.70,0.20,0.10]))
    elif age < 60:
        ip_risk_band.append(weighted_choice(["low","medium","high"], [0.80,0.17,0.03]))
    else:
        ip_risk_band.append(weighted_choice(["low","medium","high"], [0.88,0.10,0.02]))

ip_risk_band = np.array(ip_risk_band)

# Baseline spend per user (still useful for anomalies)
baseline_mean = np.random.lognormal(mean=4.3, sigma=0.55, size=n_users)  # skewed
baseline_mean = np.clip(baseline_mean, 5, 800)

baseline_std = baseline_mean * np.random.uniform(0.20, 0.40, size=n_users)
baseline_std = np.clip(baseline_std, 2, 400)


is_night_owl = (np.random.rand(n_users) < 0.12).astype(int)

users = pd.DataFrame({
    "user_id": user_id,
    "home_city": home_city,
    "preferred_device": preferred_device,
    "account_age_days": account_age_days,
    "signup_date": signup_date,
    "ip_risk_band": ip_risk_band,
    "baseline_tx_mean_gbp": np.round(baseline_mean, 2),
    "baseline_tx_std_gbp": np.round(baseline_std, 2),
    "is_night_owl": is_night_owl,
})

# -----------------------------
# CREATE TRANSACTIONS TABLE 
# -----------------------------
tx_rows = []
tx_id_counter = 0

for i in range(n_users):
    uid = users.at[i, "user_id"]
    age = int(users.at[i, "account_age_days"])
    mu_amt = float(users.at[i, "baseline_tx_mean_gbp"])
    sd_amt = float(users.at[i, "baseline_tx_std_gbp"])
    home = users.at[i, "home_city"]
    pref_dev = users.at[i, "preferred_device"]
    risk = users.at[i, "ip_risk_band"]

    start = pd.Timestamp(users.at[i, "signup_date"])
    end = TODAY

    # How many transactions this user has (simple age-based rule)
    if age < 14:
        lam = 6
    elif age < 60:
        lam = 14
    else:
        lam = 22

    n_tx = np.random.poisson(lam=lam)
    if n_tx == 0:
        continue

    # failure probability depends on risk
    if risk == "low":
        fail_p = 0.02
    elif risk == "medium":
        fail_p = 0.04
    else:
        fail_p = 0.08

    for _ in range(n_tx):
        tx_id_counter += 1
        tx_id = f"T{tx_id_counter:09d}"

        ts = random_timestamp_between(start, end)

        # Amount around user's baseline (normal distribution), clipped
        amt = np.random.normal(loc=mu_amt, scale=sd_amt)
        amt = float(np.clip(amt, 1.0, 10000.0))

        # City: mostly home, sometimes travel
        if np.random.rand() < 0.90:
            city = home
        else:
            city = weighted_choice(cities, city_p)

        # Device: mostly preferred, sometimes mismatch
        if np.random.rand() < 0.85:
            device = pref_dev
        else:
            device = weighted_choice(devices,device_p)

        status = "fail" if (np.random.rand() < fail_p) else "success"

        tx_rows.append({
            "transaction_id": tx_id,
            "user_id": uid,
            "timestamp": ts,
            "amount_gbp": round(amt, 2),
            "city": city,
            "device": device,
            "status": status,
            "anomaly_type": None,
            "is_anomaly": 0,
        })

transactions = pd.DataFrame(tx_rows)
transactions["timestamp"] = pd.to_datetime(transactions["timestamp"])
transactions = transactions.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

# -----------------------------
# INJECT ANOMALIES 
# -----------------------------
def inject_high_value(tx_df, idx, users_df):
    uid = tx_df.at[idx, "user_id"]
    u = users_df.loc[users_df["user_id"] == uid].iloc[0]
    base = float(u["baseline_tx_mean_gbp"])
    tx_df.at[idx, "amount_gbp"] = round(float(np.random.uniform(max(1500, base * 8), 8000)), 2)
    tx_df.at[idx, "anomaly_type"] = "high_value"
    tx_df.at[idx, "is_anomaly"] = 1

def inject_night(tx_df, idx):
    ts = tx_df.at[idx, "timestamp"]
    forced = ts.normalize() + pd.Timedelta(
        hours=int(np.random.randint(0, 6)),
        minutes=int(np.random.randint(0, 60)),
        seconds=int(np.random.randint(0, 60))
    )
    tx_df.at[idx, "timestamp"] = forced
    tx_df.at[idx, "anomaly_type"] = "night_activity"
    tx_df.at[idx, "is_anomaly"] = 1

def inject_geo_jump(tx_df, idx):
    current = tx_df.at[idx, "city"]
    other = [c for c in cities if c != current]
    tx_df.at[idx, "city"] = np.random.choice(other)
    tx_df.at[idx, "anomaly_type"] = "geo_jump"
    tx_df.at[idx, "is_anomaly"] = 1

def inject_burst(tx_df, idx):
    """
    Create extra rows within 10 minutes after the chosen transaction.
    This increases total rows (like real burst/velocity fraud).
    """
    base_row = tx_df.loc[idx].to_dict()
    base_ts = base_row["timestamp"]

    n_extra = int(np.random.randint(3, 7))
    extras = []

    global tx_id_counter
    for _ in range(n_extra):
        tx_id_counter += 1
        extra = base_row.copy()
        extra["transaction_id"] = f"T{tx_id_counter:09d}"
        extra["timestamp"] = base_ts + pd.Timedelta(
            minutes=int(np.random.randint(0, 10)),
            seconds=int(np.random.randint(0, 60))
        )
        extra["amount_gbp"] = round(float(np.clip(np.random.normal(25, 15), 1, 500)), 2)
        extra["status"] = "success"
        extra["anomaly_type"] = "burst_velocity"
        extra["is_anomaly"] = 1
        extras.append(extra)

    tx_df.at[idx, "anomaly_type"] = "burst_velocity"
    tx_df.at[idx, "is_anomaly"] = 1
    return extras

# choose 2% rows to become anomalies (burst adds extra rows too)
n_target = int(len(transactions) * ANOMALY_RATE)
candidate_idx = np.random.choice(transactions.index.values, size=n_target, replace=False)

extra_rows = []
for idx in candidate_idx:
    pattern = np.random.choice(
        ["high_value", "night", "burst", "geo_jump"],
        p=[0.40, 0.25, 0.25, 0.10]
    )

    if pattern == "high_value":
        inject_high_value(transactions, idx, users)
    elif pattern == "night":
        inject_night(transactions, idx)
    elif pattern == "geo_jump":
        inject_geo_jump(transactions, idx)
    else:
        extra_rows.extend(inject_burst(transactions, idx))

if extra_rows:
    transactions = pd.concat([transactions, pd.DataFrame(extra_rows)], ignore_index=True)

transactions = transactions.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

# -----------------------------
# SAVE CSV + SQLITE
# -----------------------------
users.to_csv("data/raw/users.csv", index=False)
transactions.to_csv("data/raw/transactions.csv", index=False)

conn = sqlite3.connect("data/raw/risk_project.db")
users.to_sql("users", conn, if_exists="replace", index=False)
transactions.to_sql("transactions", conn, if_exists="replace", index=False)
conn.close()

print("Done.")
print(f"Users: {len(users):,}")
print(f"Transactions: {len(transactions):,}")
print(f"Anomalies: {int(transactions['is_anomaly'].sum()):,} ({transactions['is_anomaly'].mean()*100:.2f}%)")