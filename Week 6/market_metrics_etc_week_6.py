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
# the most commonly referenced in real estate searches.
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
sold["DistrictName"] = sold_with_district["DistrictName"].values

print(f"Sold district matched:   {sold['DistrictName'].notna().sum()}")
print(f"Sold district unmatched: {sold['DistrictName'].isna().sum()}")

# Listing spatial join
listing_geo = gpd.GeoDataFrame(
    listing,
    geometry=gpd.points_from_xy(listing["Longitude"], listing["Latitude"]),
    crs="EPSG:4326"
)
listing_with_district = gpd.sjoin(listing_geo, school_districts[["DistrictName", "geometry"]], how="left", predicate="within")
listing["DistrictName"] = listing_with_district["DistrictName"].values

print(f"Listing district matched:   {listing['DistrictName'].notna().sum()}")
print(f"Listing district unmatched: {listing['DistrictName'].isna().sum()}")

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

for df in [sold, listing]:
    # Price Ratio: how close to original list price the property sold.
    # > 1 means sold above asking -- measures negotiation strength.
    df["price_ratio"] = (df["ClosePrice"] / df["OriginalListPrice"]).round(4)

    # Close to Original List Ratio: same formula -- captures full price
    # reduction history from original list price to final close price.
    df["close_to_original_list_ratio"] = (df["ClosePrice"] / df["OriginalListPrice"]).round(4)

    # Price Per Square Foot: normalizes price across different property
    # sizes for apples-to-apples market comparisons.
    df["price_per_sqft"] = (df["ClosePrice"] / df["LivingArea"]).round(2)

    # Year, Month, YrMo: derived from CloseDate for time-series analysis.
    # YrMo format (e.g. "202401") enables monthly grouping in Tableau.
    df["year"] = df["CloseDate"].dt.year
    df["month"] = df["CloseDate"].dt.month
    df["yr_mo"] = df["CloseDate"].dt.strftime("%Y%m")

    # Listing to Contract Days: time from listing date to accepted offer.
    # Measures how quickly properties go under contract in the market.
    df["listing_to_contract_days"] = (
        df["PurchaseContractDate"] - df["ListingContractDate"]
    ).dt.days

    # Contract to Close Days: escrow and closing period duration.
    # Time from accepted offer to final recorded close.
    df["contract_to_close_days"] = (
        df["CloseDate"] - df["PurchaseContractDate"]
    ).dt.days

print("\nEngineered metrics sample (Sold):")
print(sold[[
    "ClosePrice", "OriginalListPrice", "LivingArea",
    "price_ratio", "price_per_sqft", "yr_mo",
    "listing_to_contract_days", "contract_to_close_days"
]].head(10).to_string())

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

# Segment by PropertySubType
subtype_summary = sold.groupby("PropertySubType").agg(
    total_sales=("ClosePrice", "count"),
    median_close_price=("ClosePrice", "median"),
    median_price_per_sqft=("price_per_sqft", "median"),
    median_days_on_market=("DaysOnMarket", "median")
).round(2).sort_values("total_sales", ascending=False)

print("\nSegment summary by PropertySubType:")
print(subtype_summary)

# Segment by ListOfficeName (top 10 by volume)
office_summary = sold.groupby("ListOfficeName").agg(
    total_listings=("ClosePrice", "count"),
    median_close_price=("ClosePrice", "median"),
    median_price_ratio=("price_ratio", "median")
).round(2).sort_values("total_listings", ascending=False).head(10)

print("\nTop 10 listing offices by volume:")
print(office_summary)

# Segment by BuyerOfficeName (competitive intelligence -- top 10)
buyer_office_summary = sold.groupby("BuyerOfficeName").agg(
    total_purchases=("ClosePrice", "count"),
    median_close_price=("ClosePrice", "median"),
    median_price_ratio=("price_ratio", "median")
).round(2).sort_values("total_purchases", ascending=False).head(10)

print("\nTop 10 buyer offices by volume:")
print(buyer_office_summary)

#Save enriched datasets
sold.to_csv(data_p / "CRMLSSold_Engineered.csv", index=False)
listing.to_csv(data_p / "CRMLSListing_Engineered.csv", index=False)

# Results:
#
# Sold district unmatched: 147693
#Listing district matched:   348203
#Listing district unmatched: 155788
#Listing district matched:   348203
#Listing district unmatched: 155788

#Engineered metrics sample (Sold):
#   ClosePrice  OriginalListPrice  LivingArea  price_ratio  price_per_sqft   yr_mo  listing_to_contract_days  contract_to_close_days
#0   5000000.0          5000000.0      4354.0       1.0000         1148.37  202401                       0.0                    63.0
#1    858000.0                NaN      1995.0          NaN          430.08  202401                       0.0                     0.0
#2   1890500.0          1890500.0      3194.0       1.0000          591.89  202401                       0.0                     0.0
#3   2100000.0          2100000.0      3736.0       1.0000          562.10  202401                       0.0                    48.0
#4   2340000.0                NaN      2442.0          NaN          958.23  202401                       0.0                     0.0
#5   1485000.0          1550000.0      1601.0       0.9581          927.55  202401                       1.0                    21.0
#6   1130000.0           999000.0      2136.0       1.1311          529.03  202401                       1.0                    17.0
#7   1060000.0          1050000.0      1917.0       1.0095          552.95  202401                      34.0                     6.0
#8   2150000.0                NaN      2200.0          NaN          977.27  202401                       0.0                     0.0
#9   2000000.0                NaN      1690.0          NaN         1183.43  202401                       0.0                     0.0

#Segment summary by County (top 10):
#                total_sales  median_close_price  median_price_per_sqft  median_days_on_market  median_price_ratio
#CountyOrParish                                                                                                   
#Del Norte                 2           6742500.0                4778.79                  160.0                0.81
#San Mateo              6855           1650000.0                1035.71                   12.0                1.01
#Santa Clara           16604           1540000.0                 944.44                   10.0                1.02
#Orange                51109           1180000.0                 673.50                   14.0                0.99
#Santa Cruz             3101           1180000.0                 731.38                   17.0                0.98
#San Francisco           945           1175000.0                 895.03                   17.0                1.00
#Marin                   161           1155000.0                 679.65                   21.0                0.98
#Alameda               21473           1125000.0                 697.28                   14.0                1.02
#Alpine                    1           1100000.0                 267.12                  231.0                0.67
#Mono                     18           1030000.0                 618.92                   68.0                0.94

#Segment summary by PropertySubType:
#                       total_sales  median_close_price  median_price_per_sqft  median_days_on_market
#PropertySubType                                                                                     
#SingleFamilyResidence       340021            882000.0                 526.85                   17.0
#Condominium                  75801            625000.0                 562.07                   24.0
#Townhouse                    26615            795000.0                 554.49                   18.0
#ManufacturedOnLand            5965            322000.0                 225.69                   31.0
#Duplex                        2567            910000.0                 540.96                   21.0
#StockCooperative              1793            360000.0                 396.53                   21.0
#Cabin                          524            240500.0                 287.76                   47.5
#Triplex                        381           1135000.0                 466.51                   29.0
#MixedUse                       228            700000.0                 449.81                   52.0
#Quadruplex                     159           1275000.0                 376.95                   34.0
#BoatSlip                        93            185000.0                1750.00                   26.0
#OwnYourOwn                      66            273500.0                 504.78                   41.0
#ManufacturedHome                56            287500.0                 186.40                   42.5
#MobileHome                      44            555000.0                 656.80                   63.5
#Loft                            33            680000.0                 523.81                   22.0
#Timeshare                       22            555000.0                 187.64                   58.0
#CoOwnership                     18            424999.5                 426.28                   18.5
#Farm                            14           1500000.0                 767.48                   20.5
#Studio                          11            322000.0                 675.21                   18.0
#DeededParking                    6            577500.0                 348.40                   12.0

#Top 10 listing offices by volume:
#                                                    total_listings  median_close_price  median_price_ratio
#ListOfficeName                                                                                            
#Compass                                                      31785           1330000.0                1.00
#Coldwell Banker Realty                                       19919           1160000.0                0.99
#Keller Williams Realty                                        9012            870000.0                1.00
#First Team Real Estate                                        6341            960000.0                1.00
#Berkshire Hathaway HomeServices California Prop...            5917            950000.0                0.98
#Real Broker                                                   5435            845000.0                1.00
#eXp Realty of California Inc                                  5285            780000.0                1.00
#Intero Real Estate Services                                   4250           1311500.0                1.01
#eXp Realty of California, Inc.                                4041            755000.0                1.00
#Equity Union                                                  3961            850000.0                0.98

#Top 10 buyer offices by volume:
#                                                    total_purchases  median_close_price  median_price_ratio
#BuyerOfficeName                                                                                            
#Compass                                                       29769           1310335.0                1.00
#Coldwell Banker Realty                                        16029           1165000.0                0.99
#NONMEMBER MRML                                                10031            500000.0                0.99
#Keller Williams Realty                                         7131            834990.0                1.00
#Real Broker                                                    7043            800000.0                1.00
#First Team Real Estate                                         5753            899900.0                1.00
#eXp Realty of California Inc                                   5751            825000.0                1.00
#eXp Realty of California, Inc.                                 5276            725000.0                1.00
#Berkshire Hathaway HomeServices California Prop...             4603            980470.0                0.99
#Redfin Corporation