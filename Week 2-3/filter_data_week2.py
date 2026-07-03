import pandas as pd
from pathlib import Path

data_p = Path("/Users/impossibear04/Downloads/CRMLSListings")

# Load all monthly Sold files (excluding the pre-concatenated file from Week 1)
sold_data = sorted(data_p.glob("CRMLSSold*.csv"))
sold_data = [pd.read_csv(f, low_memory=False, encoding="windows-1252") for f in sold_data
             if "Concatenated" not in f.name]
sold = pd.concat(sold_data, ignore_index=True)

# Residential vs other property type share (requires unfiltered data)
print("Property type share (%):")
print(sold["PropertyType"].value_counts(normalize=True).mul(100).round(2))

# Row counts before and after Residential filter
print("\nRows before Residential filter:", len(sold))
sold = sold[sold["PropertyType"] == "Residential"]
print("Rows after Residential filter:", len(sold))

# Dataset Characteristics
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

sold.to_csv("CRMLSSold_Clean.csv", index=False)

# ------------ FINAL RESULTS
# Property type share (%):
# Residential: 66.85%ß
# Non-Residential: 33.15%

# Rows before Residential filter: 655362
# Rows after Residential filter: 438115

# Row count: 438115
# Column count: 79
# Data types: str, object, float64, int64
# Unique property types: ['Residential', 'ResedentialLease', 'CommercialSale', 'CommericalLease', 'ManufacturedInPark', 'BusinessOpportunity', 'Land'] 

# Flagged columns (>90% missing):
# TaxYear, MiddleOrJuniorSchoolDistrict, FireplacesTotal,
# AboveGradeFinishedArea, TaxAnnualAmount, CoveredSpaces,
# BusinessType, ElementarySchoolDistrict, WaterfrontYN,
# BelowGradeFinishedArea, BasementYN, LotSizeDimensions,
# BuilderName, BuildingAreaTotal, CoBuyerAgentFirstName

# ClosePrice   - min: $525 | max: $110,000,000 | mean: $1,121,740 | median: $815,000 |
# LivingArea   - min: 0 | max: 17,021,320 | mean: 1,900 | median: 1,641 |
# DaysOnMarket - min: -288 | max: 12,430 | mean: 38 | median: 19 |

# Median close price: $815,000
# Average close price: $1,121,740
# Sold above list price: 173,237 (39.54%)
# Sold at or below list price: 264,876 (60.46%)
# Date consistency issues (CloseDate before ListingContractDate): 78 rows

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