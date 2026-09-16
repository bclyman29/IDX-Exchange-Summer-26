import pandas as pd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

sold = pd.read_csv(data_p / "CRMLSSold_IQR_Clean.csv", low_memory=False, encoding="utf-8")
sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")

sac = sold[sold["CountyOrParish"] == "Sacramento"].copy()
sac["year"] = sac["CloseDate"].dt.year
sac["month"] = sac["CloseDate"].dt.month

# YoY median price by year
print("--- MEDIAN CLOSE PRICE BY YEAR ---")
print(sac.groupby("year")["ClosePrice"].median())

# YoY DOM by year
print("\n--- AVERAGE DOM BY YEAR ---")
print(sac.groupby("year")["DaysOnMarket"].mean().round(1))

# YoY sold-to-list ratio by year
print("\n--- AVG SOLD-TO-LIST RATIO BY YEAR ---")
print(sac.groupby("year")["close_to_original_list_ratio"].mean().round(4))

# Top zip codes by volume
print("\n--- TOP 10 ZIP CODES BY SALES VOLUME ---")
print(sac.groupby("PostalCode").agg(
    units=("ClosePrice", "count"),
    median_price=("ClosePrice", "median"),
    avg_dom=("DaysOnMarket", "mean")
).sort_values("units", ascending=False).head(10).round(1))

# Price change by zip (2024 vs 2025)
print("\n--- MEDIAN PRICE BY ZIP: 2024 vs 2025 (top 10 by volume) ---")
top_zips = sac.groupby("PostalCode")["ClosePrice"].count().nlargest(10).index
zip_yoy = sac[sac["PostalCode"].isin(top_zips)].groupby(["PostalCode", "year"])["ClosePrice"].median().unstack()
zip_yoy["pct_change"] = ((zip_yoy[2025] - zip_yoy[2024]) / zip_yoy[2024] * 100).round(2)
print(zip_yoy)

# Monthly volume trend
print("\n--- MONTHLY SALES VOLUME (showing seasonality) ---")
print(sac.groupby("month")["ClosePrice"].count())