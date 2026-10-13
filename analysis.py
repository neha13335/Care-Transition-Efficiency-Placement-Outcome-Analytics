
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Find project folders
BASE = Path(__file__).parent
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)

data_file = OUTPUTS / "cleaned_data.csv"

if not data_file.exists():
    raise FileNotFoundError(
        "cleaned_data.csv not found. Run clean_data.py first."
    )

# Load cleaned data
df = pd.read_csv(data_file, parse_dates=["Date"])
df = df.sort_values("Date")

# Column names
apprehensions = "Children apprehended and placed in CBP custody"
cbp_custody = "Children in CBP custody"
transfers = "Children transferred out of CBP custody"
hhs_care = "Children in HHS Care"
discharges = "Children discharged from HHS Care"

required = [
    "Date", apprehensions, cbp_custody,
    transfers, hhs_care, discharges
]

missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")

# Convert numbers safely
for col in required[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Daily activity ratios
df["Transfer Efficiency (%)"] = (
    df[transfers] / df[cbp_custody].replace(0, float("nan")) * 100
)

df["Discharge Effectiveness (%)"] = (
    df[discharges] / df[hhs_care].replace(0, float("nan")) * 100
)

# Daily flow indicators
df["Net CBP Flow"] = df[apprehensions] - df[transfers]
df["Net HHS Flow"] = df[transfers] - df[discharges]

# Save daily metrics
df.to_csv(OUTPUTS / "daily_analysis.csv", index=False)

# Summary statistics
summary = df[required[1:]].agg(["sum", "mean", "min", "max"]).T
summary.columns = ["Total", "Daily Average", "Minimum", "Maximum"]
summary.to_csv(OUTPUTS / "summary_statistics.csv")

print("\nDATA ANALYSIS SUMMARY")
print("=" * 40)
print("Reporting dates:", df["Date"].min().date(),
      "to", df["Date"].max().date())
print("Number of daily records:", len(df))
print("\nSummary statistics:")
print(summary.round(2).to_string())

print("\nAverage transfer activity ratio:",
      round(df["Transfer Efficiency (%)"].mean(), 2), "%")
print("Average discharge activity ratio:",
      round(df["Discharge Effectiveness (%)"].mean(), 2), "%")

# Monthly trends
monthly = df.set_index("Date").resample("MS").agg({
    apprehensions: "sum",
    transfers: "sum",
    discharges: "sum"
})

monthly.to_csv(OUTPUTS / "monthly_trends.csv")

# Chart 1: Daily pipeline activity
plt.figure(figsize=(12, 6))
plt.plot(df["Date"], df[apprehensions], label="Apprehensions")
plt.plot(df["Date"], df[transfers], label="Transfers")
plt.plot(df["Date"], df[discharges], label="Discharges")
plt.title("Daily Care Pipeline Activity")
plt.xlabel("Date")
plt.ylabel("Number of children")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUTS / "daily_pipeline_activity.png", dpi=150)
plt.close()

# Chart 2: Monthly trends
plt.figure(figsize=(12, 6))
plt.plot(monthly.index, monthly[apprehensions],
         marker="o", label="Apprehensions")
plt.plot(monthly.index, monthly[transfers],
         marker="o", label="Transfers")
plt.plot(monthly.index, monthly[discharges],
         marker="o", label="Discharges")
plt.title("Monthly Care Pipeline Trends")
plt.xlabel("Month")
plt.ylabel("Total recorded activity")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUTS / "monthly_trends.png", dpi=150)
plt.close()

# Chart 3: Daily custody counts
plt.figure(figsize=(12, 6))
plt.plot(df["Date"], df[cbp_custody], label="CBP custody")
plt.plot(df["Date"], df[hhs_care], label="HHS care")
plt.title("Children in CBP Custody and HHS Care")
plt.xlabel("Date")
plt.ylabel("Children in care")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUTS / "custody_trends.png", dpi=150)
plt.close()

# Chart 4: Daily activity ratios
plt.figure(figsize=(12, 6))
plt.plot(df["Date"], df["Transfer Efficiency (%)"],
         label="Transfer activity ratio")
plt.plot(df["Date"], df["Discharge Effectiveness (%)"],
         label="Discharge activity ratio")
plt.title("Daily Transfer and Discharge Activity Ratios")
plt.xlabel("Date")
plt.ylabel("Percentage (%)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUTS / "activity_ratios.png", dpi=150)
plt.close()

print("\nAnalysis completed successfully!")
print("Check the outputs folder for CSV files and charts.")
