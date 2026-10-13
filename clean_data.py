
from pathlib import Path
import pandas as pd
import re

# Project folders
BASE = Path(__file__).parent
DATA_FOLDER = BASE / "data"
OUTPUT_FOLDER = BASE / "outputs"
OUTPUT_FOLDER.mkdir(exist_ok=True)

print("CARE TRANSITION DATA CLEANING")
print("=" * 35)

# Find dataset files
files = [
    f for f in DATA_FOLDER.iterdir()
    if f.is_file()
    and f.suffix.lower() in [".csv", ".xlsx", ".xls"]
]

if not files:
    raise FileNotFoundError(
        "No CSV or Excel file found inside the data folder."
    )

if len(files) > 1:
    print("Multiple data files found:")
    for i, f in enumerate(files, start=1):
        print(f"{i}. {f.name}")
    raise ValueError(
        "Keep only your main dataset in data, "
        "or select the correct file in this code."
    )

file = files[0]
print("Reading:", file.name)

# Read the original dataset
if file.suffix.lower() == ".csv":
    try:
        df = pd.read_csv(file, sep=None, engine="python")
    except UnicodeDecodeError:
        df = pd.read_csv(
            file, sep=None, engine="python", encoding="latin-1"
        )
else:
    df = pd.read_excel(file)

# Remove extra spaces from column names
df.columns = [str(c).strip() for c in df.columns]

# Match column names even if spaces/capitalization differ
def normalize(text):
    return re.sub(r"[^a-z0-9]", "", str(text).lower())

expected_columns = {
    "date": "Date",
    "childrenapprehendedandplacedincbpcustody":
        "Children apprehended and placed in CBP custody",
    "childrenincbpcustody":
        "Children in CBP custody",
    "childrentransferredoutofcbpcustody":
        "Children transferred out of CBP custody",
    "childreninhhscare":
        "Children in HHS Care",
    "childrendischargedfromhhscare":
        "Children discharged from HHS Care",
}

rename_columns = {}

for column in df.columns:
    key = normalize(column)
    if key in expected_columns:
        rename_columns[column] = expected_columns[key]

df = df.rename(columns=rename_columns)

print("\nColumns found:")
for column in df.columns:
    print("-", column)

# Check required columns
required = list(expected_columns.values())
missing_columns = [
    column for column in required if column not in df.columns
]

if missing_columns:
    print("\nSome expected columns were not found:")
    for column in missing_columns:
        print("-", column)

    print("\nPlease check the actual column names.")
    print("No cleaned dataset was saved.")
    raise ValueError("Required columns are missing.")

# Record the original row count
original_rows = len(df)

# Convert dates
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

invalid_dates = int(df["Date"].isna().sum())

# Convert counts to numbers
count_columns = required[1:]

for column in count_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Check problems before making changes
missing_values = int(df[required].isna().sum().sum())
duplicate_dates = int(df["Date"].dropna().duplicated().sum())

negative_counts = {}
for column in count_columns:
    negative_counts[column] = int((df[column] < 0).sum())

# Remove rows that have no valid date
df = df.dropna(subset=["Date"]).copy()

# Sort dates in chronological order
df = df.sort_values("Date").reset_index(drop=True)

# Do not delete duplicate dates or fill missing counts automatically.
# They need to be reviewed before further analysis.

# Save the cleaned data
cleaned_path = OUTPUT_FOLDER / "cleaned_data.csv"
df.to_csv(cleaned_path, index=False, date_format="%Y-%m-%d")

# Create a quality report
report = [
    ("Original row count", original_rows),
    ("Rows with invalid/missing dates", invalid_dates),
    ("Rows after removing invalid dates", len(df)),
    ("Missing values in required columns", missing_values),
    ("Duplicate dates detected", duplicate_dates),
]

for column, count in negative_counts.items():
    report.append((f"Negative values: {column}", count))

report_df = pd.DataFrame(report, columns=["Check", "Result"])
report_path = OUTPUT_FOLDER / "data_quality_report.csv"
report_df.to_csv(report_path, index=False)

print("\nCLEANING SUMMARY")
print("-" * 35)
print(report_df.to_string(index=False))

print("\nFiles saved successfully:")
print(cleaned_path)
print(report_path)

print("\nNext step: review the data quality report.")
