import pandas as pd
from pathlib import Path

# Define paths
raw_path = Path("D:/Food_Price_Analysis/food-price-dashboard/data/raw/")
processed_path = Path("D:/Food_Price_Analysis/food-price-dashboard/data/processed/")
processed_path.mkdir(parents=True, exist_ok=True)

def load_agmarknet_excel(file_path, state, commodity):
    """Load and standardize Agmarknet Excel file (HTML-like CSV)"""
    try:
        # Attempt to read as HTML table
        tables = pd.read_html(file_path)
        if not tables:
            raise ValueError("No tables found in HTML file.")
        df = tables[0] # Assuming the first table contains the data
    except Exception:
        # Fallback to read as CSV if HTML parsing fails
        df = pd.read_csv(file_path)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Standardize column names for date and price
    # Look for 'price_date' or 'date' for date column
    date_col = next((col for col in df.columns if 'date' in col), None)
    if date_col:
        # Explicitly specify date format for Agmarknet files
        df['date'] = pd.to_datetime(df[date_col], format="%d %b %Y", errors='coerce')
    else:
        # Fallback if no date column found, try first column
        df['date'] = pd.to_datetime(df.iloc[:, 0], format="%d %b %Y", errors='coerce')

    # Look for 'modal_price_(rs./quintal)' or 'modal_price' for price column
    if 'modal_price_(rs./quintal)' in df.columns:
        df['price'] = df['modal_price_(rs./quintal)']
    elif 'modal_price' in df.columns:
        df['price'] = df['modal_price']
    else:
        # Fallback to last column if no specific price column found
        df['price'] = df.iloc[:, -1]

    df['state'] = state
    df['commodity'] = commodity
    df = df[['date', 'price', 'state', 'commodity']].dropna()
    return df


def load_mandi_csv(file_path):
    """Load current mandi CSV"""
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Explicitly specify date format for 'Arrival_Date'
    if 'arrival_date' in df.columns:
        df['date'] = pd.to_datetime(df['arrival_date'], format="%d/%m/%Y", dayfirst=True, errors='coerce')
    else:
        # Fallback if 'arrival_date' not found, try general 'date' column
        date_cols = [c for c in df.columns if 'date' in c]
        if date_cols:
            df['date'] = pd.to_datetime(df[date_cols[0]], errors='coerce') # Let pandas infer for other date columns
        else:
            df['date'] = pd.to_datetime('today') # Fallback to today if no date column at all

    price_cols = [c for c in df.columns if 'price' in c]
    if price_cols:
        df['price'] = df[price_cols[0]]
    else:
        df['price'] = None

    state_cols = [c for c in df.columns if 'state' in c]
    df['state'] = df[state_cols[0]] if state_cols else 'Unknown'

    comm_cols = [c for c in df.columns if 'commodity' in c or 'crop' in c]
    df['commodity'] = df[comm_cols[0]] if comm_cols else 'Unknown'

    return df[['date', 'price', 'state', 'commodity']].dropna()


def main():
    # Load datasets
    df1 = load_agmarknet_excel(raw_path / "agmarknet_kerala_onion_2018.csv", "Kerala", "Onion")
    df2 = load_agmarknet_excel(raw_path / "agmarknet_kerala_onion_2019.csv", "Kerala", "Onion")
    df3 = load_agmarknet_excel(raw_path / "agmarknet_kerala_onion_2020.csv", "Kerala", "Onion")
    df4 = load_agmarknet_excel(raw_path / "agmarknet_maharashtra_wheat_2020.csv", "Maharashtra", "Wheat")
    df5 = load_mandi_csv(raw_path / "Current_Daily_Price_Mandi.csv")

    # Combine all
    combined = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)

    # Convert to monthly averages
    combined['month'] = combined['date'].dt.to_period('M')
    monthly = combined.groupby(['month', 'state', 'commodity'], as_index=False)['price'].mean()
    monthly['month'] = monthly['month'].dt.to_timestamp()

    # Save processed files
    monthly.to_parquet(processed_path / "monthly_prices.parquet")
    combined.to_csv(processed_path / "cleaned_all_data.csv", index=False)

    print("Data cleaned and saved successfully!")


if __name__ == "__main__":
    main()
