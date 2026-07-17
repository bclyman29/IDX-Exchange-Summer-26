import pandas as pd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

sold = pd.read_csv(data_p / "CRMLSSold_Clean.csv", low_memory=False, encoding="utf-8")
listing = pd.read_csv(data_p / "CRMLSListing_Clean.csv", low_memory=False, encoding="utf-8")

# FRED FETCH
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

mortgage["year_month"] = mortgage["date"].dt.to_period("M")
mortgage_monthly = (
    mortgage.groupby("year_month")["rate_30yr_fixed"]
    .mean()
    .reset_index()
)
 
print("\nMonthly mortgage rates (sample):")
print(mortgage_monthly.tail())


# Matching Key
sold["year_month"] = pd.to_datetime(sold["CloseDate"]).dt.to_period("M")
listing["year_month"] = pd.to_datetime(listing["ListingContractDate"]).dt.to_period("M")

# Merge mortgage rates with sold and listing data
sold_merged = sold.merge(mortgage_monthly, on="year_month", how="left")
listing_merged = listing.merge(mortgage_monthly, on="year_month", how="left")

# Confirm Merge
sold_null_rate = sold_merged["rate_30yr_fixed"].isnull().sum()
listing_null_rate = listing_merged["rate_30yr_fixed"].isnull().sum()
print(f"\nSold dataset rows with missing mortgage rates: {sold_null_rate}")
print(f"Listing dataset rows with missing mortgage rates: {listing_null_rate}")

print(sold_merged[["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]].head())
print(listing_merged[["ListingContractDate", "year_month", "ListPrice", "rate_30yr_fixed"]].head())

sold_merged.to_csv(data_p / "CRMLSSold_with_MortgageRates.csv", index=False)
listing_merged.to_csv(data_p / "CRMLSListing_with_MortgageRates.csv", index=False)

# No null values in the merged datasets, indicating successful merge of mortgage rates with sold and listing data.

# SOLD SAMPLE
# CloseDate year_month  ClosePrice  rate_30yr_fixed
#0  2024-01-18    2024-01   5000000.0           6.6425
#1  2024-01-30    2024-01    858000.0           6.6425
#2  2024-01-29    2024-01   1890500.0           6.6425
#3  2024-01-02    2024-01   2100000.0           6.6425
#4  2024-01-22    2024-01   1950000.0           6.6425

# LISTING SAMPLE
#  ListingContractDate year_month  ListPrice  rate_30yr_fixed
#0          2024-01-27    2024-01   375000.0           6.6425
#1          2024-01-06    2024-01   659000.0           6.6425
#2          2024-01-11    2024-01   320000.0           6.6425
#3          2024-01-01    2024-01     2750.0           6.6425
#4          2024-01-01    2024-01     3599.0           6.6425