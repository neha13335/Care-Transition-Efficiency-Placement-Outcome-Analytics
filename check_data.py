
from pathlib import Path
import pandas as pd

# Find the folder containing this Python file
project_folder = Path(__file__).parent
data_folder = project_folder / "data"

print("CARE TRANSITION ANALYTICS")
print("-------------------------")
print("Looking for dataset in:", data_folder)

# Find the files inside the data folder
files = list(data_folder.glob("*"))

print("\nFiles found:")

for file in files:
    if file.is_file():
        print("-", file.name)

# Check whether a CSV or Excel file exists
data_files = [
    file for file in files
    if file.suffix.lower() in [".csv", ".xlsx", ".xls"]
]

if not data_files:
    print("\nERROR: No CSV or Excel dataset found.")
    print("Please check your data folder.")
else:
    dataset_file = data_files[0]

    try:
        if dataset_file.suffix.lower() == ".csv":
            df = pd.read_csv(dataset_file)
        else:
            df = pd.read_excel(dataset_file)

        print("\nDataset opened successfully!")
        print("\nColumn names:")
        print(df.columns.tolist())

        print("\nFirst 5 rows:")
        print(df.head().to_string())

        print("\nDataset size:")
        print("Rows:", df.shape[0])
        print("Columns:", df.shape[1])

    except Exception as error:
        print("\nCould not read the dataset.")
        print("Error:", error)
