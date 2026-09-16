import pandas as pd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

sold = pd.read_csv(data_p / "CRMLSSold_IQR_Clean.csv", low_memory=False, encoding="utf-8")
listing = pd.read_csv(data_p / "CRMLSListing_IQR_Clean.csv", low_memory=False, encoding="utf-8")

# Filter to Sacramento
sac_sold = sold[sold["CountyOrParish"] == "Sacramento"].copy()
sac_listing = listing[listing["CountyOrParish"] == "Sacramento"].copy()

print(f"Sacramento sold records: {len(sac_sold)}")
print(f"Sacramento listing records: {len(sac_listing)}")

# Market Overview
print("\n--- MARKET OVERVIEW ---")
print(f"Median close price: ${sac_sold['ClosePrice'].median():,.0f}")
print(f"Average days on market: {sac_sold['DaysOnMarket'].mean():.1f}")

# Pricing Trends
print("\n--- PRICING TRENDS ---")
print(f"Median price per sqft: ${sac_sold['price_per_sqft'].median():,.2f}")
print(f"Avg sold-to-list ratio: {sac_sold['close_to_original_list_ratio'].mean():.4f}")

# Market Activity
print("\n--- MARKET ACTIVITY ---")
print(f"Total closed sales: {len(sac_sold)}")
print(f"Total new listings: {len(sac_listing)}")

# Competitive Landscape
print("\n--- TOP 10 LISTING AGENTS ---")
print(sac_sold.groupby("ListAgentFullName")["ClosePrice"].agg(["count", "sum"]).sort_values("sum", ascending=False).head(10))

print("\n--- TOP 10 LISTING OFFICES ---")
print(sac_sold.groupby("ListOfficeName")["ClosePrice"].agg(["count", "sum"]).sort_values("sum", ascending=False).head(10))