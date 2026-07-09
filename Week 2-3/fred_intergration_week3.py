import pandas as pd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

sold = pd.read_csv(data_p / "ConcatenatedCRMLSSold.csv", low_memory=False, encoding="utf-8")
listing = pd.read_csv(data_p / "ConcatenatedCRMLSListing.csv", low_memory=False, encoding="utf-8")

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


sold_merged.to_csv(data_p / "CRMLSSold_with_MortgageRates.csv", index=False)
listing_merged.to_csv(data_p / "CRMLSListing_with_MortgageRates.csv", index=False)

# No null values in the merged datasets, indicating successful merge of mortgage rates with sold and listing data.