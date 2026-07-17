import pandas as pd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

sold = pd.read_csv(data_p / "ConcatenatedCRMLSSold.csv", low_memory=False, encoding="utf-8")

# Residential vs other property type share 
print("Property type share (%):")
print(sold["PropertyType"].value_counts(normalize=True).mul(100).round(2))

# Row counts before and after Residential filter
print("\nRows before Residential filter:", len(sold))
sold = sold[sold["PropertyType"] == "Residential"]
print("Rows after Residential filter:", len(sold))

# Dataset Characteristicsß
row_count = len(sold)
col_count = len(sold.columns)
print(f"Row count: {row_count}")
print(f"Column count: {col_count}")

# Unique data types in the dataset
dtypes = sold.dtypes.astype(str).unique().tolist()
print(f"Data types: {dtypes}")

# Unique property types in the dataßset
prop_types = sold['PropertyType'].unique()
print(f"Property types: {prop_types}")

# Residential property vs other
print(sold["PropertyType"].value_counts(normalize=True).mul(100).round(2))

# Residential Filter
sold = sold[sold["PropertyType"] == "Residential"]
print("\nRows after Residential filter:", len(sold))

# MISSING VALUES

null_summary = pd.DataFrame({
    "Null Count": sold.isna().sum(),
    "Null %": (sold.isna().mean() * 100).round(2)
}).sort_values("Null %", ascending=False)
 
# Flag columns with >90% missing
null_summary["Flag >90%"] = null_summary["Null %"] > 90
 
print("\nMissing value report:")
print(null_summary)
 
print("\nFlagged columns (>90% missing):")
print(null_summary.index[null_summary["Flag >90%"]].tolist())

cols_to_drop = null_summary.index[null_summary["Flag >90%"]].tolist()
sold = sold.drop(columns=cols_to_drop)
print(f"\nDropped {len(cols_to_drop)} columns, {len(sold.columns)} remaining")

# ADDING LISTING FOR FUTURE ANALYSIS
listing = pd.read_csv(data_p / "ConcatenatedCRMLSListing.csv", low_memory=False, encoding="utf-8")

listing = listing[listing["PropertyType"] == "Residential"]

# Missing value report
listing_null_summary = pd.DataFrame({
    "Null Count": listing.isna().sum(),
    "Null %": (listing.isna().mean() * 100).round(2)
}).sort_values("Null %", ascending=False)

listing_null_summary["Flag >90%"] = listing_null_summary["Null %"] > 90

print("\nListing flagged columns (>90% missing):")
print(listing_null_summary.index[listing_null_summary["Flag >90%"]].tolist())

# Drop >90% null columns
listing_cols_to_drop = listing_null_summary.index[listing_null_summary["Flag >90%"]].tolist()
listing = listing.drop(columns=listing_cols_to_drop)

listing.to_csv(data_p / "CRMLSListing_Clean.csv", index=False)


#Summary Stats for ClosePrice, LivingArea, and DaysOnMarket
summary_stats = sold[["ClosePrice", "LivingArea", "DaysOnMarket"]].describe(percentiles=[.10, .25, .50, .75, .90])
print(summary_stats)

# Further Analysis

# Median and average close price
print("\nMedian close price:", sold["ClosePrice"].median())
print("Average close price:", sold["ClosePrice"].mean().round(2))
 
# Days on market distribution
print("\nDays on market summary:")
print(sold["DaysOnMarket"].describe())
 
# Homes sold above vs below list price
above_list = (sold["ClosePrice"] > sold["ListPrice"]).sum()
below_list = (sold["ClosePrice"] <= sold["ListPrice"]).sum()
print(f"\nSold above list price: {above_list} ({round(above_list / len(sold) * 100, 2)}%)")
print(f"Sold at or below list price: {below_list} ({round(below_list / len(sold) * 100, 2)}%)")
 
# Date consistency check: flag rows where CloseDate is before ListingContractDate
sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")
sold["ListingContractDate"] = pd.to_datetime(sold["ListingContractDate"], errors="coerce")
date_flag = sold[sold["CloseDate"] < sold["ListingContractDate"]]
print(f"\nRows where CloseDate is before ListingContractDate: {len(date_flag)}")
 
# Counties with highest median close price
print("\nTop 5 counties by median close price:")
print(sold.groupby("CountyOrParish")["ClosePrice"].median().sort_values(ascending=False).head(5))

sold.to_csv(data_p / "CRMLSSold_Clean.csv", index=False)

# ------------ FINAL RESULTS
# Property type share (%):
# Residential: 66.92%
# Non-Residential: 33.08%

# Rows before Residential filter: 680885
# Rows after Residential filter: 455658

# Row count: 455658
# Column count: 79
# Data types: str, object, float64, int64
# Unique property types: ['Residential', 'ResedentialLease', 'CommercialSale', 'CommericalLease', 'ManufacturedInPark', 'BusinessOpportunity', 'Land'] 

# Flagged columns (>90% missing):
# TaxYear, MiddleOrJuniorSchoolDistrict, FireplacesTotal,
# AboveGradeFinishedArea, TaxAnnualAmount, CoveredSpaces,
# BusinessType, ElementarySchoolDistrict, WaterfrontYN,
# BelowGradeFinishedArea, BasementYN, LotSizeDimensions,
# BuilderName, BuildingAreaTotal, CoBuyerAgentFirstName

# ClosePrice   - min: $525 | max: $110,000,000 | mean: $1,124,047 | median: $815,000 |
# LivingArea   - min: 0 | max: 17,021,320 | mean: 1,900 | median: 1,643 |
# DaysOnMarket - min: -288 | max: 12,430 | mean: 38 | median: 19 |

# Median close price: $815,000
# Average close price: $1,124,047
# Sold above list price: 180,042 (39.51%)
# Sold at or below list price: 275,614 (60.49%)
# Date consistency issues (CloseDate before ListingContractDate): 81 rows

# Top 5 counties by median close price:
# Del Norte:     $6,742,500
# San Mateo:     $1,650,000
# Santa Clara:   $1,540,000
# Santa Cruz:    $1,180,000
# Orange:        $1,175,000

# Outliers 
# DaysOnMarket min of -288 (negative days)
# LivingArea max of 17,021,320 sq ft 
# Del Norte median of $6,742,500 (small n)