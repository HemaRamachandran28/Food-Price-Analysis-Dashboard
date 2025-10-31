import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="India Food Price Dashboard", layout="wide")

processed_path = Path("data/processed/")

# Load datasets
try:
    df = pd.read_parquet(processed_path / "monthly_prices.parquet")
except FileNotFoundError:
    st.error("❌ monthly_prices.parquet not found in data/processed/")
    st.stop()

try:
    top5 = pd.read_csv(processed_path / "top5_impact.csv")
except FileNotFoundError:
    st.warning("⚠️ top5_impact.csv not found — showing only main chart.")
    top5 = None

st.title("📊 India Food Price Trends Dashboard")

# ---- Main Price Chart ----
states = sorted(df["state"].unique())
commodities = sorted(df["commodity"].unique())

col1, col2 = st.columns(2)
selected_state = col1.selectbox("Select State", states)
selected_commodity = col2.selectbox("Select Commodity", commodities)

filtered = df[(df["state"] == selected_state) & (df["commodity"] == selected_commodity)]

st.line_chart(filtered, x="month", y="price", height=400)
st.caption(f"Showing average monthly price for {selected_commodity} in {selected_state}")

# ---- Top 5 Chart ----
if top5 is not None and not top5.empty:
    st.subheader("🔥 Top 5 Commodities by Average Inflation (YoY)")
    st.bar_chart(top5.set_index("commodity")["avg_inflation_yoy"])
else:
    st.info("Top 5 commodities chart unavailable — waiting for processed data.")

st.divider()
st.caption("Data Source: Agmarknet & Mandi Portal")
