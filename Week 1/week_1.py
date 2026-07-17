import pandas as pd
from pathlib import Path

# CSV folder
data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

# SOLD
# Find every CRMLSSold*.csv file in the folder and read each one into a
# df, then stack them all into a single combined df.

sold_data = sorted(data_p.glob("CRMLSSold*.csv"))
sold_data = [pd.read_csv(f, low_memory=False, encoding="windows-1252") for f in sold_data]
df_sold = pd.concat(sold_data, ignore_index=True)

print("Sold dataset total rows before concatenation:")
print(sum(len(f) for f in sold_data))
print("Sold dataset total rows after concatenation:")
print(len(df_sold))

# Filter Residential properties
df_sold_f = df_sold[df_sold.PropertyType == "Residential"]
print("Sold dataset total rows after filtering:")
print(len(df_sold_f))

df_sold.to_csv(data_p / "ConcatenatedCRMLSSold.csv", index=False)

# LISTING
# Same process as Sold above
listing_data = sorted(data_p.glob("CRMLSListing*.csv"))
listing_data = [pd.read_csv(f, low_memory=False, encoding="windows-1252") for f in listing_data]
df_listing = pd.concat(listing_data, ignore_index=True)

print("Listing dataset total rows before concatenation:")
print(sum(len(f) for f in listing_data))
print("Listing dataset total rows after concatenation:")
print(len(df_listing))

df_listing_f = df_listing[df_listing.PropertyType == "Residential"]
print("Listing dataset total rows after filtering:")
print(len(df_listing_f))

df_listing.to_csv(data_p / "ConcatenatedCRMLSListing.csv", index=False)

# FINAL RESULTS
# Sold dataset total rows before concatenation :680885
# Sold dataset total rows after concatenation :680885
# Sold dataset total rows after filtering :455658
# Listing dataset total rows before concatenation :766706
# Listing dataset total rows after concatenation :766706
# Listing dataset total rows after filtering :504466ß