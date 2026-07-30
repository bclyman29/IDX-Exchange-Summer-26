import pandas as pd
import geopandas as gpd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

sold = pd.read_csv(data_p / "CRMLSSold_Final.csv", low_memory=False, encoding="utf-8")
listing = pd.read_csv(data_p / "CRMLSListing_Final.csv", low_memory=False, encoding="utf-8")

# Fix datetime conversion

date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate"]
 
for col in date_cols:
    sold[col] = pd.to_datetime(sold[col], errors="coerce")
    listing[col] = pd.to_datetime(listing[col], errors="coerce")

# Key Market Metrics
# Price Ratio: measures negotiation strength -- how close to original
# list price the property actually sold for. > 1 means sold above asking.
sold["price_ratio"] = sold["ClosePrice"] / sold["OriginalListPrice"]
listing["price_ratio"] = listing["ClosePrice"] / listing["OriginalListPrice"]
 
# Close to Original List Ratio: same as price ratio -- captures the full
# price reduction history from original list to final close price.
sold["close_to_original_list_ratio"] = sold["ClosePrice"] / sold["OriginalListPrice"]
listing["close_to_original_list_ratio"] = listing["ClosePrice"] / listing["OriginalListPrice"]
 
# Price Per Square Foot: normalizes price across different property sizes
# making apples-to-apples comparisons possible across the market.
sold["price_per_sqft"] = sold["ClosePrice"] / sold["LivingArea"]
listing["price_per_sqft"] = listing["ClosePrice"] / listing["LivingArea"]
 
# Days on Market: raw field -- time-to-sell indicator.
# Already exists in the dataset, confirming presence here.
print(f"\nSold DaysOnMarket sample:\n{sold['DaysOnMarket'].describe()}")
 
# Year, Month, YrMo: derived from CloseDate for time-series analysis.
# YrMo (e.g. 202401) enables monthly grouping and trend charting.
sold["year"] = sold["CloseDate"].dt.year
sold["month"] = sold["CloseDate"].dt.month
sold["yr_mo"] = sold["CloseDate"].dt.to_period("M").astype(str)
 
listing["year"] = listing["CloseDate"].dt.year
listing["month"] = listing["CloseDate"].dt.month
listing["yr_mo"] = listing["CloseDate"].dt.to_period("M").astype(str)
 
# Listing to Contract Days: time from listing date to accepted offer --
# measures how quickly properties go under contract.
sold["listing_to_contract_days"] = (
    sold["PurchaseContractDate"] - sold["ListingContractDate"]
).dt.days
listing["listing_to_contract_days"] = (
    listing["PurchaseContractDate"] - listing["ListingContractDate"]
).dt.days
 
# Contract to Close Days: escrow and closing period duration --
# time from accepted offer to final close.
sold["contract_to_close_days"] = (
    sold["CloseDate"] - sold["PurchaseContractDate"]
).dt.days
listing["contract_to_close_days"] = (
    listing["CloseDate"] - listing["PurchaseContractDate"]
).dt.days
 
print("\nEngineered metrics sample (Sold):")
print(sold[[
    "ClosePrice", "OriginalListPrice", "LivingArea",
    "price_ratio", "price_per_sqft", "yr_mo",
    "listing_to_contract_days", "contract_to_close_days"
]].head(10))

# School District Mapping
school_districts = gpd.read_file(data_p / "ca_school_districts_2024_25.geojson")
 
print(f"\nSchool district columns: {school_districts.columns.tolist()}")
print(f"District types: {school_districts['DistrictType'].unique()}")
 
# Filter to Unified districts only
school_districts = school_districts[school_districts["DistrictType"] == "Unified"].copy()
print(f"Unified districts: {len(school_districts)}")
 
# Reproject to WGS84 to match MLS lat/lon coordinates
if school_districts.crs.to_epsg() != 4326:
    school_districts = school_districts.to_crs(epsg=4326)
 
# Sold spatial join
sold_geo = sold.dropna(subset=["Latitude", "Longitude"]).copy()
sold_geo = gpd.GeoDataFrame(
    sold_geo,
    geometry=gpd.points_from_xy(sold_geo["Longitude"], sold_geo["Latitude"]),
    crs="EPSG:4326"
)
sold_geo = gpd.sjoin(
    sold_geo,
    school_districts[["DistrictName", "geometry"]],
    how="left",
    predicate="within"
)
sold = sold.merge(
    sold_geo[["ListingKey", "DistrictName"]].drop_duplicates("ListingKey"),
    on="ListingKey",
    how="left"
)
print(f"\nSold district matched:   {sold['DistrictName'].notna().sum()}")
print(f"Sold district unmatched: {sold['DistrictName'].isna().sum()}")
 
# Listing spatial join
listing_geo = listing.dropna(subset=["Latitude", "Longitude"]).copy()
listing_geo = gpd.GeoDataFrame(
    listing_geo,
    geometry=gpd.points_from_xy(listing_geo["Longitude"], listing_geo["Latitude"]),
    crs="EPSG:4326"
)
listing_geo = gpd.sjoin(
    listing_geo,
    school_districts[["DistrictName", "geometry"]],
    how="left",
    predicate="within"
)
listing = listing.merge(
    listing_geo[["ListingKey", "DistrictName"]].drop_duplicates("ListingKey"),
    on="ListingKey",
    how="left"
)
print(f"Listing district matched:   {listing['DistrictName'].notna().sum()}")
print(f"Listing district unmatched: {listing['DistrictName'].isna().sum()}")
