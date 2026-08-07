import pandas as pd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

sold = pd.read_csv(data_p / "CRMLSSold_Engineered.csv", low_memory=False, encoding="utf-8")
listing = pd.read_csv(data_p / "CRMLSListing_Engineered.csv", low_memory=False, encoding="utf-8")
key_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]
# BEFORE FILTERING  
print("Before filtering:")
print(f"Sold size: {len(sold)}")
for col in key_fields:
    print(f"  Sold {col} median: {sold[col].median()}")
 
print(f"Listing size: {len(listing)}")
for col in key_fields:
    print(f"  Listing {col} median: {listing[col].median()}")


# IQR OUTLIER FLAGGING AND FILTERING
# Records outside 1.5x the IQR above Q3 or below Q1 are flagged.
# Flag columns added to original dataset 
# Raw records are preserved as well as filtered datasets with outliers removed.
 
# Sold IQR filter
sold_filtered = sold.copy()
for col in key_fields:
    Q1 = sold[col].quantile(0.25)
    Q3 = sold[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    # Flag outliers in the original dataset
    sold[f"outlier_flagged_{col}"] = (sold[col] < lower) | (sold[col] > upper)
    # Remove outliers from the filtered dataset
    sold_filtered = sold_filtered[(sold_filtered[col] >= lower) & (sold_filtered[col] <= upper)]
 
# Listing IQR filter
listing_filtered = listing.copy()
for col in key_fields:
    Q1 = listing[col].quantile(0.25)
    Q3 = listing[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    # Flag outliers in the original dataset
    listing[f"outlier_flagged_{col}"] = (listing[col] < lower) | (listing[col] > upper)
    # Remove outliers from the filtered dataset
    listing_filtered = listing_filtered[(listing_filtered[col] >= lower) & (listing_filtered[col] <= upper)]

# AFTER FILTERING 
 
print("\nAfter filtering:")
print(f"Sold size: {len(sold_filtered)}")
for col in key_fields:
    print(f"  Sold {col} median: {sold_filtered[col].median()}")
 
print(f"Listing size: {len(listing_filtered)}")
for col in key_fields:
    print(f"  Listing {col} median: {listing_filtered[col].median()}")

sold.to_csv(data_p / "CRMLSSold_Flagged.csv", index=False)
sold_filtered.to_csv(data_p / "CRMLSSold_IQR_Clean.csv", index=False)
listing.to_csv(data_p / "CRMLSListing_Flagged.csv", index=False)
listing_filtered.to_csv(data_p / "CRMLSListing_IQR_Clean.csv", index=False)

# Results

#Before filtering:
#Sold size: 455280
#  Sold ClosePrice median: 815000.0
#  Sold LivingArea median: 1643.0
#  Sold DaysOnMarket median: 19.0
#Listing size: 503991
#  Listing ClosePrice median: 820000.0
#  Listing LivingArea median: 1650.0
#  Listing DaysOnMarket median: 18.0

#After filtering:
#   Sold size: 384,769 (70,511 rows removed)
# #  Sold ClosePrice median: 780000.0
#  Sold LivingArea median: 1570.0
#  Sold DaysOnMarket median: 16.0

#  Listing size: 358,398 (145,593 rows removed)
#  Listing ClosePrice median: 787450.0
#  Listing LivingArea median: 1570.0
#  Listing DaysOnMarket median: 15.0
