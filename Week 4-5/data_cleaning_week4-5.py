import pandas as pd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")
sold = pd.read_csv(data_p / "CRMLSSold_with_MortgageRates.csv", low_memory=False, encoding="utf-8")
listing = pd.read_csv(data_p / "CRMLSListing_with_MortgageRates.csv", low_memory=False, encoding="utf-8")

print(f"Sold rows before cleaning: {len(sold)}")
print(f"Listing rows before cleaning: {len(listing)}")

#Datetime Conversion
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
print("\nSold date flags:")
sold["listing_after_close_flag"] = sold["CloseDate"] < sold["ListingContractDate"]
print(f"Listing after close:        {sold['listing_after_close_flag'].sum()}")
sold["purchase_after_close_flag"] = sold["CloseDate"] < sold["PurchaseContractDate"]
print(f"Purchase after close:       {sold['purchase_after_close_flag'].sum()}")
sold["negative_timeline_flag"] = sold["listing_after_close_flag"] | sold["purchase_after_close_flag"]
print(f"Negative timeline (either): {sold['negative_timeline_flag'].sum()}")
 
# Remove rows that violate date order
#sold = sold[~sold["listing_after_close_flag"] & ~sold["purchase_after_close_flag"]]
 
print("\nListing date flags:")
listing["listing_after_close_flag"] = listing["CloseDate"] < listing["ListingContractDate"]
print(f"Listing after close:        {listing['listing_after_close_flag'].sum()}")
listing["purchase_after_close_flag"] = listing["CloseDate"] < listing["PurchaseContractDate"]
print(f"Purchase after close:       {listing['purchase_after_close_flag'].sum()}")
listing["negative_timeline_flag"] = listing["listing_after_close_flag"] | listing["purchase_after_close_flag"]
print(f"Negative timeline (either): {listing['negative_timeline_flag'].sum()}")
 
# Remove rows that violate date order
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

# Results as of Now
#Date field dtypes after conversion:
#CloseDate                   datetime64[us]
#PurchaseContractDate        datetime64[us]
#ListingContractDate         datetime64[us]
#ContractStatusChangeDate    datetime64[us]
#dtype: object

#Sold date flags:
#Listing after close:        81
#Purchase after close:       92
#Negative timeline (either): 169

#Listing date flags:
#Listing after close:        82
#Purchase after close:       94
#Negative timeline (either): 171

#Sold missing coordinates:    53637
#Listing missing coordinates: 49467
#Sold zero coordinates:       44
#Listing zero coordinates:    62
#Sold positive longitude:     34
#Listing positive longitude:  69
#Sold out-of-range coords:    114
#Listing out-of-range coords: 226


# TO DO : Numerical Consistency Check, Dropping Useless Columns, Creating Figures, etc.