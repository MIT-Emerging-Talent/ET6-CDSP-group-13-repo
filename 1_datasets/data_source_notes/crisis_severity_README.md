# INFORM Crisis Severity Dataset Summary

## Overview

This dataset provides a country-year-level view of humanitarian crisis severity
using the INFORM Severity Index. Unlike conflict-only datasets, INFORM captures
a broader range of risks — including displacement, economic collapse, disease
outbreaks, and more. This dataset is suitable for tracking global crisis
severity trends and combining with external indicators like crypto adoption or
migration.

---

## Data Source

- **Source:**  
  [INFORM Severity Index – EU DRMKC](https://drmkc.jrc.ec.europa.eu/inform-severity/results-and-data)

- **Files used:**  
  - `inform_severity_-_december_2019.xlsx` *(add if missing)*  
  - `inform_severity_-_december_2020.xlsx`  
  - `inform_severity_-_december_2021.xlsx`  
  - `inform_severity_-_december_2022.xlsx`  
  - `inform_severity_-_december_2023.xlsx`  
  - `inform_severity_-_december_2024.xlsx`

- **Location:**  
  `/1_datasets/raw_datasets/`

- **Sheet name:**  
  `"Crisis Data"` (or whichever contains `ISO3`, `Year`, and `Severity AI`)

---

## Method

- Loaded XLSX files from 2019 to 2024.
- Extracted three columns from each file:
  - `ISO3` (country code)
  - `Year`
  - `Severity AI` (numeric score, 0–5)
- Aggregated to **one row per country-year** by selecting the maximum
  `Severity AI` value if multiple rows existed.
- Created a binary column `crisis_flag`:
  - `1` if `Severity AI ≥ 2.5`
  - `0` otherwise
- Applied quality checks:
  - Removed rows with missing `ISO3`
  - Ensured no duplicate `(ISO3, Year)` combinations
  - Confirmed all `Severity AI` values are between 0 and 5
- Saved the cleaned data to CSV.

---

## Resulting CSV File

- **Filename:**  
  `crisis_severity_2019-24.csv`

- **Location:**  
  `/1_datasets/processed/`

- **Columns:**
  - `ISO3`
  - `Year`
  - `severity_score` *(renamed from “Severity AI”)*
  - `crisis_flag` *(1 if severity_score ≥ 2.5, else 0)*

---

## Usefulness for the Project

This dataset is valuable for:

- Identifying country-years with high humanitarian distress
- Comparing INFORM-derived crisis risk with conflict-only metrics (e.g., ACLED)
- Linking crisis periods with trends in crypto usage, migration, or economic
  data
- Enabling reproducible, cross-country temporal analysis

---

## Files Included in Repo

- `crisis_severity_2019-24.csv`: Processed dataset with one row per country-year
- `process_crisis_data.py`: Python script used to extract and clean the raw data
- `crisis_severity_README.md`: This documentation file
