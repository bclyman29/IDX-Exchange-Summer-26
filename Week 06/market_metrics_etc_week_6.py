import pandas as pd
import geopandas as gpd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

sold = pd.read_csv(data_p / "CRMLSSold_Final.csv", low_memory=False, encoding="utf-8",
                   parse_dates=["CloseDate", "PurchaseContractDate", "ListingContractDate"])
listing = pd.read_csv(data_p / "CRMLSListing_Final.csv", low_memory=False, encoding="utf-8",
                      parse_dates=["CloseDate", "PurchaseContractDate", "ListingContractDate"])

print(f"Sold rows loaded:    {len(sold)}")
print(f"Listing rows loaded: {len(listing)}")

# School District Mapping
# Match each property to its Unified School District using a spatial
# join on Latitude/Longitude. Unified districts cover K-12 and are
# Source: CA Open Data School District Areas 2024-25 (Shapefile)

# Load and filter school district GeoJSON
school_districts = gpd.read_file(data_p / "DistrictAreas2526_-284845464123469011.geojson")
school_districts = school_districts[school_districts["DistrictType"] == "Unified"].reset_index(drop=True)
school_districts = school_districts.to_crs(epsg=4326)

# Sold spatial join
sold_geo = gpd.GeoDataFrame(
    sold,
    geometry=gpd.points_from_xy(sold["Longitude"], sold["Latitude"]),
    crs="EPSG:4326"
)
sold_with_district = gpd.sjoin(sold_geo, school_districts[["DistrictName", "geometry"]], how="left", predicate="within")
sold_with_district = sold_with_district.drop_duplicates(subset="ListingKey")[["ListingKey", "DistrictName"]]
sold = sold.merge(sold_with_district, on="ListingKey", how="left")

print(f"Sold district matched:   {sold['DistrictName'].notna().sum()}")
print(f"Sold district unmatched: {sold['DistrictName'].isna().sum()}")

# Listing spatial join
listing_geo = gpd.GeoDataFrame(
    listing,
    geometry=gpd.points_from_xy(listing["Longitude"], listing["Latitude"]),
    crs="EPSG:4326"
)
listing_with_district = gpd.sjoin(listing_geo, school_districts[["DistrictName", "geometry"]], how="left", predicate="within")
listing_with_district = listing_with_district.drop_duplicates(subset="ListingKey")[["ListingKey", "DistrictName"]]
listing = listing.merge(listing_with_district.rename(columns={"DistrictName": "DistrictName_listing"}), on="ListingKey", how="left")
listing["DistrictName"] = listing["DistrictName_listing"]
listing = listing.drop(columns=["DistrictName_listing"])

# Listing spatial join
listing_geo = gpd.GeoDataFrame(
    listing,
    geometry=gpd.points_from_xy(listing["Longitude"], listing["Latitude"]),
    crs="EPSG:4326"
)
listing_with_district = gpd.sjoin(listing_geo, school_districts[["DistrictName", "geometry"]], how="left", predicate="within")

# Use _right suffix since listing already has DistrictName column from Sold step
listing["DistrictName"] = listing_with_district["DistrictName_right"].values

print(f"Listing district matched:   {listing['DistrictName'].notna().sum()}")
print(f"Listing district unmatched: {listing['DistrictName'].isna().sum()}")

#Engineer key market metrics
# All metrics derived from existing fields per deliverable spec.
# Applied to both datasets in sequence.

# Sold metrics
sold["price_ratio"] = (sold["ClosePrice"] / sold["OriginalListPrice"]).round(4)
sold["close_to_original_list_ratio"] = (sold["ClosePrice"] / sold["OriginalListPrice"]).round(4)
sold["price_per_sqft"] = (sold["ClosePrice"] / sold["LivingArea"]).round(2)
sold["year"] = sold["CloseDate"].dt.year
sold["month"] = sold["CloseDate"].dt.month
sold["yr_mo"] = sold["CloseDate"].dt.to_period("M").astype(str)
sold["listing_to_contract_days"] = (sold["PurchaseContractDate"] - sold["ListingContractDate"]).dt.days
sold["contract_to_close_days"] = (sold["CloseDate"] - sold["PurchaseContractDate"]).dt.days

print("\nSold sample of engineered metrics:")
print(sold[[
    "ListingKey", "ClosePrice", "OriginalListPrice", "LivingArea",
    "price_ratio", "price_per_sqft", "yr_mo",
    "listing_to_contract_days", "contract_to_close_days"
]].head())

# Listing metrics
listing["price_ratio"] = (listing["ClosePrice"] / listing["OriginalListPrice"]).round(4)
listing["close_to_original_list_ratio"] = (listing["ClosePrice"] / listing["OriginalListPrice"]).round(4)
listing["price_per_sqft"] = (listing["ClosePrice"] / listing["LivingArea"]).round(2)
listing["year"] = listing["CloseDate"].dt.year
listing["month"] = listing["CloseDate"].dt.month
listing["yr_mo"] = listing["CloseDate"].dt.to_period("M").astype(str)
listing["listing_to_contract_days"] = (listing["PurchaseContractDate"] - listing["ListingContractDate"]).dt.days
listing["contract_to_close_days"] = (listing["CloseDate"] - listing["PurchaseContractDate"]).dt.days

print("\nListing sample of engineered metrics:")
print(listing[[
    "ListingKey", "ClosePrice", "OriginalListPrice", "LivingArea",
    "price_ratio", "price_per_sqft", "yr_mo",
    "listing_to_contract_days", "contract_to_close_days"
]].head())

#Segment Analysis
#Group by key dimensions to uncover market patterns.

# Segment by CountyOrParish
county_summary = sold.groupby("CountyOrParish").agg(
    total_sales=("ClosePrice", "count"),
    median_close_price=("ClosePrice", "median"),
    median_price_per_sqft=("price_per_sqft", "median"),
    median_days_on_market=("DaysOnMarket", "median"),
    median_price_ratio=("price_ratio", "median")
).round(2).sort_values("median_close_price", ascending=False)

print("\nSegment summary by County (top 10):")
print(county_summary.head(10))

#Save enriched datasets
sold.to_csv(data_p / "CRMLSSold_Engineered.csv", index=False)
listing.to_csv(data_p / "CRMLSListing_Engineered.csv", index=False)

# Results:
# Sold rows loaded:    455,280
# Listing rows loaded: 503,991

# Sold district matched:   307,587 (67.6%)
# Sold district unmatched: 147,693 (32.4%)
# Listing district matched:   348,203 (69.1%)
# Listing district unmatched: 155,788 (30.9%)


#Sold sample of engineered metrics:
#   ListingKey  ClosePrice  OriginalListPrice  LivingArea  price_ratio  price_per_sqft    yr_mo  listing_to_contract_days  contract_to_close_days
#0  1095075487   5000000.0          5000000.0      4354.0          1.0         1148.37  2024-01                       0.0                    63.0
#1  1079166779    858000.0                NaN      1995.0          NaN          430.08  2024-01                       0.0                     0.0
#2  1075037759   1890500.0          1890500.0      3194.0          1.0          591.89  2024-01                       0.0                     0.0
#3  1067652762   2100000.0          2100000.0      3736.0          1.0          562.10  2024-01                       0.0                    48.0
#4  1061988701   2340000.0                NaN      2442.0          NaN          958.23  2024-01                       0.0                     0.0

#Listing sample of engineered metrics:
#   ListingKey  ClosePrice  OriginalListPrice  LivingArea  price_ratio  price_per_sqft    yr_mo  listing_to_contract_days  contract_to_close_days
#0  1159972295         NaN           759000.0      2338.0          NaN             NaN      NaN                       NaN                     NaN
#1  1159871345    320000.0           320000.0      1212.0       1.0000          264.03  2026-05                     851.0                     0.0
#2  1153320466    160000.0           115900.0      1008.0       1.3805          158.73  2026-04                     804.0                    25.0
#3  1146529264   2000000.0          2500000.0      2573.0       0.8000          777.30  2026-04                     785.0                    29.0
#4  1118382573   3200000.0          3200000.0      1381.0       1.0000         2317.16  2025-05                      58.0                   421.0

#                total_sales  
#CountyOrParish                                                                                                   
#Del Norte                 2           
#San Mateo              6855          
#Santa Clara           16604           
#Orange                51109           
#Santa Cruz             3101           
#San Francisco           945          
#Marin                   161           
#Alameda               21473          
#Alpine                    1          
#Mono                     18

# Engineered metrics added:
#   price_ratio, close_to_original_list_ratio, price_per_sqft,
#   year, month, yr_mo, listing_to_contract_days, contract_to_close_days

# Segment summary by County (top 10 by median close price):
#   Del Norte:     $6,742,500 | PPSF: $4,778 | DOM: 160 | price_ratio: 0.81
#   San Mateo:     $1,650,000 | PPSF: $1,036 | DOM: 12  | price_ratio: 1.01
#   Santa Clara:   $1,540,000 | PPSF: $944   | DOM: 10  | price_ratio: 1.02
#   Orange:        $1,180,000 | PPSF: $674   | DOM: 14  | price_ratio: 0.99
#   Santa Cruz:    $1,180,000 | PPSF: $731   | DOM: 17  | price_ratio: 0.98
#   San Francisco: $1,175,000 | PPSF: $895   | DOM: 17  | price_ratio: 1.00
#   Marin:         $1,155,000 | PPSF: $680   | DOM: 21  | price_ratio: 0.98
#   Alameda:       $1,125,000 | PPSF: $697   | DOM: 14  | price_ratio: 1.02
#   Alpine:        $1,100,000 | PPSF: $267   | DOM: 231 | price_ratio: 0.67
#   Mono:          $1,030,000 | PPSF: $619   | DOM: 68  | price_ratio: 0.94

# Notable observations:
#   - Del Norte: only 2 sales, median inflated by small sample size
#   - Santa Clara/Alameda price_ratio > 1.0: homes selling above asking
#   - Alpine: 1 sale, 231 DOM and 0.67 ratio, this is an outlier