import numpy as np
import pandas as pd
import sqlite3


try:
    user_df=pd.read_csv('data/raw/users.csv') #users data
    t_df=pd.read_csv('data/raw/transactions.csv') #transactions data
    print(f'Succesfully read data: Users {user_df.shape}, transactions: {t_df.shape}')
except Exception as e:
    print('Error loading the data {e}')



t_df["timestamp"]=pd.to_datetime(t_df["timestamp"])

# sort values 
t_df=t_df.sort_values(["user_id","timestamp"])

# time since previous transactions
t_df["time_since_prev_min"] = (
    t_df
    .groupby("user_id")["timestamp"]
    .diff()
    .dt.total_seconds() / 60
)


# check for night transactions (unsual hours)
t_df["hour"] = t_df["timestamp"].dt.hour
t_df["is_night_tx"] = t_df["hour"].between(0, 5).astype(int)

# High Amount flags 
threshold = t_df["amount_gbp"].quantile(0.95)
t_df["is_high_amount"] = (t_df["amount_gbp"] > threshold).astype(int)

# cities changed feature
t_df["prev_city"] = t_df.groupby("user_id")["city"].shift(1)
t_df["city_changed"] = (t_df["prev_city"] != t_df["city"]).astype(int)

# velocity feature
t_df["time_bucket"] = t_df["timestamp"].dt.floor("10min")

t_df["tx_count_10min"] = (
    t_df.groupby(["user_id", "time_bucket"])["transaction_id"]
    .transform("count")
)


#Risk Score
t_df["risk_score"] = (
    t_df["is_high_amount"] * 3
    + t_df["is_night_tx"] * 2
    + t_df["city_changed"] * 2
    + (t_df["tx_count_10min"] >= 3).astype(int)*3 
)

# Risk Band
t_df["risk_band"] = pd.cut(
    t_df["risk_score"],
    bins=[-1, 2, 5, 10],
    labels=["Low", "Medium", "High"]
)

# Save processed data
t_df.to_csv("data/processed/transactions_features.csv", index=False)

conn = sqlite3.connect("data/raw/risk_project.db")  # reuse same DB file
t_df.to_sql("transactions_features", conn, if_exists="replace", index=False)
conn.close()

print("Saved transactions_features to SQLite as table: transactions_features")


print(t_df[["is_anomaly", "risk_score"]].groupby("is_anomaly").mean())
