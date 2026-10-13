
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

# ----------------------------------
# 1. PAGE SETTINGS
# ----------------------------------

BASE = Path(__file__).parent
DATA_FILE = BASE / "outputs" / "daily_analysis.csv"

st.set_page_config(
    page_title="Care Transition Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Care Transition Efficiency & Placement Outcome Analytics")
st.write(
    "An interactive dashboard to explore daily care pipeline "
    "activity, custody levels, transfers, and discharges."
)

# ----------------------------------
# 2. LOAD THE DATA
# ----------------------------------

@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path, parse_dates=["Date"])
    data = data.sort_values("Date")
    return data

if not DATA_FILE.exists():
    st.error(
        "Dataset not found. Please run clean_data.py "
        "and analysis.py first."
    )
    st.stop()

df = load_data(DATA_FILE)

# Column names
apprehensions = "Children apprehended and placed in CBP custody"
cbp_custody = "Children in CBP custody"
transfers = "Children transferred out of CBP custody"
hhs_care = "Children in HHS Care"
discharges = "Children discharged from HHS Care"

required_columns = [
    "Date", apprehensions, cbp_custody,
    transfers, hhs_care, discharges
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error(f"Missing columns in daily_analysis.csv: {missing}")
    st.stop()

for col in required_columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ----------------------------------
# 3. SIDEBAR DATE FILTER
# ----------------------------------

st.sidebar.header("Dashboard Filters")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select reporting period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = df[
        (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
    ].copy()
else:
    filtered = df.copy()

if filtered.empty:
    st.warning("No records are available for this date range.")
    st.stop()

st.sidebar.success(f"{len(filtered)} daily records selected")

# ----------------------------------
# 4. SUMMARY METRICS
# ----------------------------------

st.header("Key Performance Indicators")

total_apprehensions = filtered[apprehensions].sum()
total_transfers = filtered[transfers].sum()
total_discharges = filtered[discharges].sum()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Apprehensions",
    f"{total_apprehensions:,.0f}"
)

col2.metric(
    "Total Transfers",
    f"{total_transfers:,.0f}"
)

col3.metric(
    "Total Discharges",
    f"{total_discharges:,.0f}"
)

col4, col5 = st.columns(2)

col4.metric(
    "Average CBP Custody",
    f"{filtered[cbp_custody].mean():,.1f}"
)

col5.metric(
    "Average HHS Care",
    f"{filtered[hhs_care].mean():,.1f}"
)

st.caption(
    "These metrics describe recorded activity and custody levels. "
    "They do not measure the time taken for an individual child's transition."
)

st.divider()

# ----------------------------------
# 5. DAILY PIPELINE ACTIVITY
# ----------------------------------

st.header("Daily Care Pipeline Activity")

daily_activity = filtered[
    ["Date", apprehensions, transfers, discharges]
].melt(
    id_vars="Date",
    var_name="Activity",
    value_name="Number of Children"
)

fig_daily = px.line(
    daily_activity,
    x="Date",
    y="Number of Children",
    color="Activity",
    markers=True,
    title="Apprehensions, Transfers, and Discharges Over Time"
)

fig_daily.update_layout(legend_title_text="Activity")
st.plotly_chart(fig_daily, use_container_width=True)

# ----------------------------------
# 6. CUSTODY LEVELS
# ----------------------------------

st.header("Children in Care")

custody_data = filtered[
    ["Date", cbp_custody, hhs_care]
].melt(
    id_vars="Date",
    var_name="Care Location",
    value_name="Number of Children"
)

fig_custody = px.line(
    custody_data,
    x="Date",
    y="Number of Children",
    color="Care Location",
    markers=True,
    title="CBP Custody and HHS Care Levels"
)

st.plotly_chart(fig_custody, use_container_width=True)

# ----------------------------------
# 7. MONTHLY TRENDS
# ----------------------------------

st.header("Monthly Trends")

monthly = filtered.set_index("Date").resample("MS").agg({
    apprehensions: "sum",
    transfers: "sum",
    discharges: "sum"
}).reset_index()

monthly_activity = monthly.melt(
    id_vars="Date",
    var_name="Activity",
    value_name="Monthly Total"
)

fig_monthly = px.bar(
    monthly_activity,
    x="Date",
    y="Monthly Total",
    color="Activity",
    barmode="group",
    title="Monthly Recorded Pipeline Activity"
)

st.plotly_chart(fig_monthly, use_container_width=True)

# ----------------------------------
# 8. ACTIVITY RATIOS
# ----------------------------------

st.header("Transfer and Discharge Activity Ratios")

if "Transfer Efficiency (%)" in filtered.columns:
    transfer_ratio = filtered["Transfer Efficiency (%)"].mean()
else:
    transfer_ratio = float("nan")

if "Discharge Effectiveness (%)" in filtered.columns:
    discharge_ratio = filtered["Discharge Effectiveness (%)"].mean()
else:
    discharge_ratio = float("nan")

ratio1, ratio2 = st.columns(2)

ratio1.metric(
    "Average Transfer Activity Ratio",
    f"{transfer_ratio:.2f}%"
    if pd.notna(transfer_ratio) else "Not available"
)

ratio2.metric(
    "Average Discharge Activity Ratio",
    f"{discharge_ratio:.2f}%"
    if pd.notna(discharge_ratio) else "Not available"
)

st.info(
    "Interpretation: these ratios compare recorded transfers with "
    "CBP custody counts, and recorded discharges with HHS care counts. "
    "They are activity ratios, not individual transition success rates "
    "or measures of waiting time."
)

# ----------------------------------
# 9. DATA TABLE
# ----------------------------------

st.header("Detailed Daily Records")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="care_transition_filtered_data.csv",
    mime="text/csv"
)

st.success("Dashboard loaded successfully!")
