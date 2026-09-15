# IDX Exchange – Summer 2026 MLS Analytics Pipeline

`Data Pipeline` | `Tableau Dashboards` | `Market Intelligence` | `CRMLS`

A 12-week analytics internship project building an end-to-end residential real estate 
market intelligence system from raw MLS data. The pipeline ingests monthly CRMLS 
transaction files, engineers market metrics, detects outliers, and delivers interactive 
Tableau dashboards and a Sacramento market intelligence report.

---

## Core Capabilities

- Concatenates monthly CRMLS Sold and Listing CSVs (Jan 2024 – Jun 2026) into unified datasets
- Merges FRED MORTGAGE30US 30-year fixed rate data onto both datasets using a year-month key
- Engineers key market metrics: price ratio, PPSF, YrMo, listing-to-contract days, contract-to-close days
- Maps each property to its Unified School District via spatial join on latitude/longitude
- Detects and flags outliers using IQR filtering across ClosePrice, LivingArea, and DaysOnMarket
- Delivers two interactive Tableau workbooks: market analysis and competitive intelligence
- Produces a 1-page Sacramento County Market Intelligence Report with data-driven insights

---

## Pipeline Overview


Raw monthly CSVs → `ConcatenatedCRMLSSold.csv` / `ConcatenatedCRMLSListing.csv`  
→ `CRMLSSold_Clean.csv` / `CRMLSListing_Clean.csv`  
→ `CRMLSSold_with_MortgageRates.csv` / `CRMLSListing_with_MortgageRates.csv`  
→ `CRMLSSold_Final.csv` / `CRMLSListing_Final.csv`  
→ `CRMLSSold_Engineered.csv` / `CRMLSListing_Engineered.csv`  
→ `CRMLSSold_IQR_Clean.csv` / `CRMLSListing_IQR_Clean.csv`

--- 

## Tableau Public

Interactive dashboards are published and accessible here:  
[Tableau Public Profile](https://public.tableau.com/app/profile/benjamin.lyman/vizzes)

- `market_analysis.twbx` — Market Analysis Dashboards
- `competitive_analysis.twbx` — Competitive Intelligence Dashboards

---

## Weekly Breakdown

### Week 1 – Aggregation
Concatenate all monthly `CRMLSListing` and `CRMLSSold` CSVs into two unified unfiltered datasets.  
**Run:** `python3 week_1.py`  
**Output:** `ConcatenatedCRMLSSold.csv`, `ConcatenatedCRMLSListing.csv`

---

### Week 2 – Dataset Structuring and Validation
Load both concatenated datasets, filter to Residential, drop >90% null columns, and perform EDA on the Sold dataset including missing value report, numeric distribution summary, and key market insights.  
**Run:** `python3 filter_data_week2.py`  
**Output:** `CRMLSSold_Clean.csv`, `CRMLSListing_Clean.csv`

---

### Week 3 – Mortgage Rate Integration
Fetch the FRED MORTGAGE30US series, resample from weekly to monthly averages, and merge onto both datasets using a year-month key. Requires internet connection.  
**Run:** `python3 fred_intergration_week3.py`  
**Output:** `CRMLSSold_with_MortgageRates.csv`, `CRMLSListing_with_MortgageRates.csv`

---

### Weeks 4-5 – Data Cleaning and Preparation
Convert date fields to datetime, flag and remove date consistency violations and invalid numeric values, flag geographic data quality issues, confirm numeric field types. Saves both a flagged copy and a clean final dataset.  
**Run:** `python3 data_cleaning_week4-5.py`  
**Output:** `CRMLSSold_Final.csv`, `CRMLSListing_Final.csv`, `CRMLSSold_Flagged_.csv`, `CRMLSListing_Flagged_.csv`

---

### Week 6 – Feature Engineering and Market Metrics
Map properties to Unified School Districts via spatial join, engineer key market metrics (price ratio, PPSF, YrMo, listing-to-contract days, contract-to-close days), and generate segmented summary tables by county. Requires `geopandas` and the CA School District GeoJSON.  
**Run:** `python3 market_metrics_etc_week_6.py`  
**Output:** `CRMLSSold_Engineered.csv`, `CRMLSListing_Engineered.csv`

---

### Week 7 – Outlier Detection and Data Quality
Apply IQR filtering to ClosePrice, LivingArea, and DaysOnMarket. Flag outliers in the original dataset and save a separate clean filtered dataset for analysis.  
**Run:** `python3 outlier_detection_week7.py`  
**Output:** `CRMLSSold_IQR_Clean.csv`, `CRMLSListing_IQR_Clean.csv`, `CRMLSSold_Flagged.csv`, `CRMLSListing_Flagged.csv`

---

### Weeks 8-10 – Tableau Dashboard Development
Two interactive Tableau workbooks published to Tableau Public.

**market_analysis.twbx** — filterable by city, county, zip code, and PropertySubType:
- Monthly median close price (YoY)
- Average days on market (YoY)
- Average close-to-original-list price ratio (YoY)
- New listings (YoY)
- Closed sales (YoY)
- Median price per square foot (YoY) — custom dashboard

**competitive_analysis.twbx:**
- Top 100 listing agents by sales volume and units
- Top 100 listing offices by sales volume and units
- Zip code heat map of median close prices
- Zip code heat map of homes sold
- Listing office market share over time — custom dashboard

---

### Weeks 11-12 – Market Intelligence Report and Presentation
Sacramento County Market Intelligence Report covering market overview, pricing trends, 
market activity, competitive landscape, and key takeaways. Delivered as a 1-page 
document with a 5-minute live presentation.

**Scripts:**
- `sacramento_report.py` — retrieves key Sacramento market metrics from the cleaned 
  sold dataset including median price, DOM, sold-to-list ratio, top agents, and top offices
- `sac_deep_dive.py` — year-over-year analysis by zip code including price appreciation, 
  DOM trends, and seasonality patterns used to build the final market narrative

**Run:**
```bash
python3 sacramento_report.py
python3 sac_deep_dive.py
```
**Output:** Sacramento County market metrics printed to terminal for use in the final report

---

## Prerequisites

```bash
pip3 install pandas geopandas requests pathlib
```

- Python 3.14
- Monthly CRMLS CSV files in a local data folder
- California School District GeoJSON (2024-25) from CA Open Data
- Tableau Desktop for dashboard development

---

## Data Sources

- **CRMLS via Trestle API** — monthly residential MLS transaction data (Jan 2024 – Jun 2026)
- **FRED MORTGAGE30US** — weekly 30-year fixed mortgage rate (St. Louis Federal Reserve)
- **CA Open Data** — California School District boundary GeoJSON (2024-25)