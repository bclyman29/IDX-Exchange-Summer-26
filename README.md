# IDX-Exchange-Summer-Internship-Summer-2026

# Overview 
This is a summary of the following project for the 12-week summer internship at IDX exchange. The project is finding real estate market intelligence through analytical interaction with MLS data.

# Progress
Week 0

- Run extraction scripts to retrieve up to date CRMLS sold and listing data.
--------------------------
WEEK 1

Objectives:
- Combine each month's CRMLSListing and CRMLSSold CSVs into two unified datasets.
Filter both datasets down to Residential property types only.

How to Run:
- Set the filepath of data_p to the folder containing the monthly CSV files. Run the script with python3 week_1.py. Upon completion, ConcatenatedCRMLSListing.csv and ConcatenatedCRMLSSold.csv will be output to the folder the script is run from.
--------------------------
WEEK 2

Objectives:
- Inspect strucutre of combined Sold dataset
- Find missing values per column, flagging any with above 90% null. 
- Create a numeric distribtuion summary for ClosePrice, LivingArea, and DaysOnMarket
- Discover key insights such outliers, sold above/below listed price, etc.

How to Run:
- Set data_p to the folder containing the monthly CSV files. Run the script with python3 filter_data_week2.py. The filtered datasets will be saved as CRMLSSold_Clean.csv and CRMLSListing_Clean.csv in the same folder.
--------------------------
WEEK 3

Objectives:
- Fetch the FRED MORTGAGE30US 30-year fixed mortgage rate series directly from the St. Louis Federal Reserve.
- Resample the weekly rate data to monthly averages and merge onto both the Sold and Listing datasets using a year-month key.
- Validate the merge by confirming zero null rate values across both enriched datasets. 

How to Run:
- Set data_p to the folder containing the concatenated CSV files from Week 1. Ensure an internet connection is available for the FRED fetch. Run the script with python3 fred_intergration_week3.py. Upon completion, CRMLSSold_with_MortgageRates.csv and CRMLSListing_with_MortgageRates.csv will be saved to the same folder.
--------------------------
WEEKS 4-5

Objectives: 
- Convert date fields to datetime format (CloseDate, PurchaseContractDate, ListingContractDate, ContractStatusChangeDate).
- Create boolean flag columns for date consistency violations: listing_after_close_flag, purchase_after_close_flag, purchase_after_listing_flag, and negative_timeline_flag.
- Flag geographic data quality issues including missing coordinates, zero coordinates, positive longitude, and out-of-range California coordinates.
- Flag and remove invalid numeric values: LivingArea <= 0, DaysOnMarket < 0, ClosePrice <= 0, and negative Bedrooms or Bathrooms.
- Confirm all key numeric fields are properly typed.

How to Run:
Run the script with "python3 data_cleaning_week4-5.py". Upon completion, "CRMLSSold_Final.csv" and "CRMLSListing_Final.csv" will be saved to the same folder as before
