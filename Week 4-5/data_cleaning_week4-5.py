import pandas as pd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")
sold = pd.read_csv(data_p / "CRMLSSold_with_MortgageRates.csv", low_memory=False, encoding="utf-8")
listing = pd.read_csv(data_p / "CRMLSListing_with_MortgageRates.csv", low_memory=False, encoding="utf-8")

# Counts before cleaning
print(f"Sold rows before cleaning:    {len(sold)}")
print(f"Sold columns before cleaning: {len(sold.columns)}")
print(f"Listing rows before cleaning:    {len(listing)}")
print(f"Listing columns before cleaning: {len(listing.columns)}")


#Datetime Conversion
#Allows for math operations and comparisons on date fields to be done properly. The "mixed" format allows for different date formats to be handled in the same column.
date_cols = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]
 
for col in date_cols:
    sold[col] = pd.to_datetime(sold[col], format="mixed")
    listing[col] = pd.to_datetime(listing[col], format="mixed")
 
print("\nDate field dtypes after conversion:")
print(sold[date_cols].dtypes)

# Date Consitency Check
# Logical order: ListingContractDate -> PurchaseContractDate -> CloseDate
# Stay as flags for now
print("\nSold date consistency flags:")
sold["listing_after_close_flag"] = sold["ListingContractDate"] > sold["CloseDate"]
print(f"  Listing after close:        {sold['listing_after_close_flag'].sum()}")
sold["purchase_after_close_flag"] = sold["PurchaseContractDate"] > sold["CloseDate"]
print(f"  Purchase after close:       {sold['purchase_after_close_flag'].sum()}")
sold["negative_timeline_flag"] = sold["listing_after_close_flag"] | sold["purchase_after_close_flag"]
print(f"  Negative timeline (either): {sold['negative_timeline_flag'].sum()}")
sold["purchase_after_listing_flag"] = sold["ListingContractDate"] > sold["PurchaseContractDate"]
print(f"  Purchase after listing:     {sold['purchase_after_listing_flag'].sum()}")
 
print("\nListing date consistency flags:")
listing["listing_after_close_flag"] = listing["ListingContractDate"] > listing["CloseDate"]
print(f"  Listing after close:        {listing['listing_after_close_flag'].sum()}")
listing["purchase_after_close_flag"] = listing["PurchaseContractDate"] > listing["CloseDate"]
print(f"  Purchase after close:       {listing['purchase_after_close_flag'].sum()}")
listing["negative_timeline_flag"] = listing["listing_after_close_flag"] | listing["purchase_after_close_flag"]
print(f"  Negative timeline (either): {listing['negative_timeline_flag'].sum()}")
listing["purchase_after_listing_flag"] = listing["ListingContractDate"] > listing["PurchaseContractDate"]
print(f"  Purchase after listing:     {listing['purchase_after_listing_flag'].sum()}")

 
#sold = sold[~sold["listing_after_close_flag"] & ~sold["purchase_after_close_flag"]]
 

 
#listing = listing[~listing["listing_after_close_flag"] & ~listing["purchase_after_close_flag"]]

# Georgraphical Consistency Check
# Missing coordinates (null Latitude or Longitude)
sold["missing_coords"] = sold["Latitude"].isna() | sold["Longitude"].isna()
listing["missing_coords"] = listing["Latitude"].isna() | listing["Longitude"].isna()
print(f"\nSold missing coordinates:    {sold['missing_coords'].sum()}")
print(f"Listing missing coordinates: {listing['missing_coords'].sum()}")
 
sold["zero_coords"] = (sold["Latitude"] == 0) | (sold["Longitude"] == 0)
listing["zero_coords"] = (listing["Latitude"] == 0) | (listing["Longitude"] == 0)
print(f"Sold zero coordinates:       {sold['zero_coords'].sum()}")
print(f"Listing zero coordinates:    {listing['zero_coords'].sum()}")
 
# Positive longitude 
sold["positive_lon_flag"] = sold["Longitude"] > 0
listing["positive_lon_flag"] = listing["Longitude"] > 0
print(f"Sold positive longitude:     {sold['positive_lon_flag'].sum()}")
print(f"Listing positive longitude:  {listing['positive_lon_flag'].sum()}")
 
# Out-of-range coordinates for California
sold["bad_coords_flag"] = (
    (sold["Latitude"] < 32) | (sold["Latitude"] > 42) |
    (sold["Longitude"] < -124) | (sold["Longitude"] > -114)
)
listing["bad_coords_flag"] = (
    (listing["Latitude"] < 32) | (listing["Latitude"] > 42) |
    (listing["Longitude"] < -124) | (listing["Longitude"] > -114)
)
print(f"Sold out-of-range coords:    {sold['bad_coords_flag'].sum()}")
print(f"Listing out-of-range coords: {listing['bad_coords_flag'].sum()}")

# Numeric Validation Checks
# Logically impossible values for numeric fields flagged
#Counted before removal

print("\nSold invalid numeric flags:")
sold["closeprice_flag"] = sold["ClosePrice"] <= 0
print(f"  Invalid ClosePrice (<= 0):   {sold['closeprice_flag'].sum()}")
sold["livingarea_flag"] = sold["LivingArea"] <= 0
print(f"  Invalid LivingArea (<= 0):   {sold['livingarea_flag'].sum()}")
sold["dom_flag"] = sold["DaysOnMarket"] < 0
print(f"  Negative DaysOnMarket:       {sold['dom_flag'].sum()}")
sold["neg_rooms_flag"] = (sold["BathroomsTotalInteger"] < 0) | (sold["BedroomsTotal"] < 0)
print(f"  Negative Bedrooms/Bathrooms: {sold['neg_rooms_flag'].sum()}")
 
# Remove rows with invalid numeric values
sold_before_numeric = len(sold)
sold = sold[
    ~sold["closeprice_flag"] &
    ~sold["livingarea_flag"] &
    ~sold["dom_flag"] &
    ~sold["neg_rooms_flag"]
].copy()
print(f"  Rows removed: {sold_before_numeric - len(sold)}")
 
print("\nListing invalid numeric flags:")
listing["closeprice_flag"] = listing["ClosePrice"] <= 0
print(f"  Invalid ClosePrice (<= 0):   {listing['closeprice_flag'].sum()}")
listing["livingarea_flag"] = listing["LivingArea"] <= 0
print(f"  Invalid LivingArea (<= 0):   {listing['livingarea_flag'].sum()}")
listing["dom_flag"] = listing["DaysOnMarket"] < 0
print(f"  Negative DaysOnMarket:       {listing['dom_flag'].sum()}")
listing["neg_rooms_flag"] = (listing["BathroomsTotalInteger"] < 0) | (listing["BedroomsTotal"] < 0)
print(f"  Negative Bedrooms/Bathrooms: {listing['neg_rooms_flag'].sum()}")
 
# Remove rows with invalid numeric values
listing_before_numeric = len(listing)
listing = listing[
    ~listing["closeprice_flag"] &
    ~listing["livingarea_flag"] &
    ~listing["dom_flag"] &
    ~listing["neg_rooms_flag"]
].copy()
print(f"  Rows removed: {listing_before_numeric - len(listing)}")


# Numeric field dtypes confirmation
num_cols = [
    "AssociationFee", "BathroomsTotalInteger", "BedroomsTotal",
    "ClosePrice", "DaysOnMarket", "GarageSpaces", "Latitude",
    "ListingKeyNumeric", "ListPrice", "LivingArea", "Longitude",
    "LotSizeAcres", "LotSizeArea", "LotSizeSquareFeet",
    "MainLevelBedrooms", "OriginalListPrice", "ParkingTotal",
    "Stories", "StreetNumberNumeric", "YearBuilt"
]
 
print("\nSold numeric dtypes:")
for col in num_cols:
    if col in sold.columns:
        print(f"  {col}: {sold[col].dtype}")
 
print("\nListing numeric dtypes:")
for col in num_cols:
    if col in listing.columns:
        print(f"  {col}: {listing[col].dtype}")


# Final Row count after cleaning 
print(f"\nSold rows after cleaning:    {len(sold)}")
print(f"Sold columns after cleaning: {len(sold.columns)}")
print(f"Listing rows after cleaning:    {len(listing)}")
print(f"Listing columns after cleaning: {len(listing.columns)}")

sold_clean = sold.copy()
sold_clean.to_csv(data_p / "CRMLSSold_Final.csv", index=False)

listing_clean = listing.copy()
listing_clean.to_csv(data_p / "CRMLSListing_Final.csv", index=False)

# Results 
#Sold rows before cleaning:    455658 
#Sold columns before cleaning: 66
#Listing rows before cleaning:    504466
#Listing columns before cleaning: 70

#Date field dtypes after conversion:
#CloseDate                   datetime64[us]
#PurchaseContractDate        datetime64[us]
#ListingContractDate         datetime64[us]
#ContractStatusChangeDate    datetime64[us]
#dtype: object

#Sold date consistency flags:
#  Listing after close:        81
#  Purchase after close:       92
#  Negative timeline (either): 169
#  Purchase after listing:     314

#Listing date consistency flags:
#  Listing after close:        82
#  Purchase after close:       94
#  Negative timeline (either): 171
#  Purchase after listing:     312

#Sold missing coordinates:    53637
#Listing missing coordinates: 49467
#Sold zero coordinates:       44
#Listing zero coordinates:    62
#Sold positive longitude:     34
#Listing positive longitude:  69
#Sold out-of-range coords:    114
#Listing out-of-range coords: 226

#Sold invalid numeric flags:
#  Invalid ClosePrice (<= 0):   0
#  Invalid LivingArea (<= 0):   161
#  Negative DaysOnMarket:       48
#  Negative Bedrooms/Bathrooms: 0
#  Rows removed: 209

#Listing invalid numeric flags:
#  Invalid ClosePrice (<= 0):   0
#  Invalid LivingArea (<= 0):   261
#  Negative DaysOnMarket:       43
#  Negative Bedrooms/Bathrooms: 0
#  Rows removed: 304

#Sold numeric dtypes:
 # AssociationFee: float64
 # BathroomsTotalInteger: float64
 # BedroomsTotal: float64
 # ClosePrice: float64
 # DaysOnMarket: int64
 # GarageSpaces: float64
 # Latitude: float64
#  ListingKeyNumeric: int64
# ListPrice: float64
#  LivingArea: float64
#  Longitude: float64
#  LotSizeAcres: float64
#  LotSizeArea: float64
#  LotSizeSquareFeet: float64
#  MainLevelBedrooms: float64
#  OriginalListPrice: float64
#  ParkingTotal: float64
#  Stories: float64
#  StreetNumberNumeric: float64
 # YearBuilt: float64

#Listing numeric dtypes:
#  AssociationFee: float64
#  BathroomsTotalInteger: float64
#  BedroomsTotal: float64
#  ClosePrice: float64
#  DaysOnMarket: int64
#  GarageSpaces: float64
#  Latitude: float64
#  ListingKeyNumeric: int64
#  ListPrice: float64
#  LivingArea: float64
#  Longitude: float64
#  LotSizeAcres: float64
#  LotSizeArea: float64
#  LotSizeSquareFeet: float64
#  MainLevelBedrooms: float64
#  OriginalListPrice: float64
#  ParkingTotal: float64
#  Stories: float64
 # StreetNumberNumeric: float64
 # YearBuilt: float64

#Sold rows after cleaning:    455449
#Sold columns after cleaning: 78
#Listing rows after cleaning:    504162
#Listing columns after cleaning: 82