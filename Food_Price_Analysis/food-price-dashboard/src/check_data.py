import os
import pandas as pd

# Folder where all CSV files are stored
data_dir = "data/raw"

# Get all CSV files in the folder
csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

if not csv_files:
    print("No CSV files found in", data_dir)
    exit()

# Combine all CSVs into one DataFrame
df_list = []
for file in csv_files:
    path = os.path.join(data_dir, file)
    try:
        df = pd.read_csv(path)
        df_list.append(df)
    except Exception as e:
        print(f"Error reading {file}: {e}")

if df_list:
    df = pd.concat(df_list, ignore_index=True)
    print("✅ Total Rows:", len(df))
    print("✅ Columns:", list(df.columns))
    print(df.head())
else:
    print("No valid data loaded!")
