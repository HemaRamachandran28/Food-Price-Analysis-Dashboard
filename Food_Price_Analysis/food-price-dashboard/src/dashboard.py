import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="India Food Price Dashboard", layout="wide")

processed_path = Path("data/processed/")

# Load monthly data
df = pd.read_parquet(processed_path / "monthly_prices.parquet")

# Try loading top5 file safely
top5_file = processed_path / "top5_impact.csv"
if top5_file.exists() and top5_file.stat().st_size > 0:
    top5 = pd.read_csv(top5_file)
else:
    top5 = pd.DataFrame({"commodity": [], "price": []})
    st.warning("⚠️ 'top5_impact.csv' is empty or missing. Showing main chart only.")

st.title("📊 India Food Price Trends Dashboard")

# Filters
states = sorted(df["state"].unique())
commodities = sorted(df["commodity"].unique())

col1, col2 = st.columns(2)
selected_state = col1.selectbox("Select State", states, index=states.index("Kerala"))
selected_commodity = col2.selectbox("Select Commodity", commodities, index=commodities.index("Onion"))

# Filter data
filtered = df[(df["state"] == selected_state) & (df["commodity"] == selected_commodity)]
filtered = filtered.sort_values("month")
st.line_chart(filtered, x="month", y="price", height=400)
st.caption(f"Showing average monthly price for {selected_commodity} in {selected_state}")

# Show top 5 chart only if data available
if not top5.empty:
    st.subheader("🔥 Top 5 Commodities by Average Inflation (YoY)")
    st.bar_chart(top5.set_index("commodity"))
else:
    st.info("Top 5 commodities chart unavailable — waiting for processed data.")

st.info("Data Source: Agmarknet & Mandi portal")
