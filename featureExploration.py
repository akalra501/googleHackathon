import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("charts", exist_ok=True)

df = pd.read_csv("data/dataset1.csv")

# Parse dates
df["contract_start_date"] = pd.to_datetime(
    df["contract_start_date"].astype(str).str.strip(),
    format="%m/%d/%Y",
    errors="coerce"
)
df["contract_end_date"] = pd.to_datetime(
    df["contract_end_date"].astype(str).str.strip(),
    format="%m/%d/%Y",
    errors="coerce"
)

df_valid = df.dropna(subset=["contract_start_date"]).copy()

#Early termination
df_early = df[df["is_churned"] == 1].dropna(subset=["contract_end_date"]).copy()
df_early["year_quarter"] = df_early["contract_end_date"].dt.to_period("Q").astype(str)

early_counts = (
    df_early.groupby("year_quarter")
    .agg(churned_customers=("customer_id", "count"))
    .reset_index()
    .sort_values("year_quarter")
)

q_bounds_early = pd.DataFrame({"year_quarter": early_counts["year_quarter"].unique()})
q_bounds_early["q_start"] = pd.PeriodIndex(q_bounds_early["year_quarter"], freq="Q").start_time

early_risk = []
for _, r in q_bounds_early.sort_values("year_quarter").iterrows():
    mask = (
        (df_valid["contract_start_date"] <= r["q_start"]) &
        (df_valid["contract_start_date"] + pd.DateOffset(years=1) > r["q_start"]) &
        (
            df_valid["contract_end_date"].isna() |
            (df_valid["contract_end_date"] >= r["q_start"])
        )
    )
    early_risk.append({"year_quarter": r["year_quarter"], "at_risk": int(mask.sum())})

early_rate = early_counts.merge(pd.DataFrame(early_risk), on="year_quarter", how="left")
early_rate["churn_rate"] = early_rate["churned_customers"] / early_rate["at_risk"]

plt.figure(figsize=(12, 4))
plt.plot(early_rate["year_quarter"], early_rate["churn_rate"], marker="o")
plt.xticks(rotation=45, ha="right")
plt.xlabel("Year-Quarter")
plt.ylabel("Churn Rate")
plt.title("Quarterly Churn Rate: Early Termination Only")
plt.tight_layout()
plt.savefig("charts/quarterly_churn_early_termination.png", dpi=150)
plt.close()

#Churn and non renewal
df["combined_churn"] = (
    (df["is_churned"] == 1) |
    ((df["is_churned"] == 0) & (df["renewed_flag"] == 0) & df["renewed_flag"].notna())
).astype(int)

df_combined = df[df["combined_churn"] == 1].dropna(subset=["contract_end_date"]).copy()
df_combined["year_quarter"] = df_combined["contract_end_date"].dt.to_period("Q").astype(str)

combined_counts = (
    df_combined.groupby("year_quarter")
    .agg(churned_customers=("customer_id", "count"))
    .reset_index()
    .sort_values("year_quarter")
)

q_bounds_combined = pd.DataFrame({"year_quarter": combined_counts["year_quarter"].unique()})
q_bounds_combined["q_start"] = pd.PeriodIndex(q_bounds_combined["year_quarter"], freq="Q").start_time

combined_risk = []
for _, r in q_bounds_combined.sort_values("year_quarter").iterrows():
    mask = (
        (df_valid["contract_start_date"] <= r["q_start"]) &
        (
            df_valid["contract_end_date"].isna() |
            (df_valid["contract_end_date"] >= r["q_start"])
        )
    )
    combined_risk.append({"year_quarter": r["year_quarter"], "at_risk": int(mask.sum())})

combined_rate = combined_counts.merge(pd.DataFrame(combined_risk), on="year_quarter", how="left")
combined_rate["churn_rate"] = combined_rate["churned_customers"] / combined_rate["at_risk"]

plt.figure(figsize=(12, 4))
plt.plot(combined_rate["year_quarter"], combined_rate["churn_rate"], marker="o")
plt.xticks(rotation=45, ha="right")
plt.xlabel("Year-Quarter")
plt.ylabel("Churn Rate")
plt.title("Quarterly Churn Rate: Early Termination + Non-Renewal")
plt.tight_layout()
plt.savefig("charts/quarterly_churn_combined.png", dpi=150)
plt.close()
