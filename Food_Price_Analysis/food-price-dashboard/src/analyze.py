import pandas as pd
from pathlib import Path

processed_path = Path("data/processed/")
df = pd.read_parquet(processed_path / "monthly_prices.parquet")

# Compute Year-over-Year and Month-over-Month changes
df['year'] = df['month'].dt.year
df['month_num'] = df['month'].dt.month

df['yoy_change'] = df.groupby(['state','commodity'])['price'].pct_change(12)
df['mom_change'] = df.groupby(['state','commodity'])['price'].pct_change(1)

metrics = df[['month', 'state', 'commodity', 'price', 'yoy_change', 'mom_change']].dropna()
metrics.to_csv(processed_path / "yoy_mom_metrics.csv", index=False)

# Top 5 commodities by average yearly inflation
top5 = (
    metrics.groupby('commodity')['yoy_change']
    .mean()
    .nlargest(5)
    .reset_index()
)
top5.to_csv(processed_path / "top5_impact.csv", index=False)

print("✅ Analysis complete: metrics and top5 saved.")
