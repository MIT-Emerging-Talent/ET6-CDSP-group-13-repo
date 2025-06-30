# Global Findex Dataset (World Bank, Country-Level)

## Source

- **Organization:** The World Bank  
- **URL:**  
  [World Bank – Global Findex](https://www.worldbank.org/en/publication/globalfindex/Data)  
- **File:** `DatabankWide.raw.xlsx`  
- **Years:** 2011, 2014, 2017, 2021  
- **Format:** Excel (`.xlsx`)

## Sheets

### `Data`

- Each row = one country in one year  
- Over 1200 indicators on financial inclusion  
- Key columns:  
  - `Country name`, `Year`, `Adult population`, `Income group`, `Region`  
  - Indicators: account ownership, mobile money usage, saving, borrowing,  
    digital access

### `Series table`

- Maps column codes to indicator definitions  
- Fields include: short/long definition, topic, unit, aggregation method

### `Updates`

- Notes on changed or updated variables across survey years

## Storage Guidelines

- **Original filename:** `DatabankWide.raw.xlsx`  
- **Storage path:** `/datasets/raw_datasets/`  
- ⚠️ Do not edit this raw file. Use copies for data processing or analysis.

## Usage in Project

- Establish baseline financial inclusion in each country  
- Compare traditional finance indicators with crypto adoption data  
- Integrate with conflict or crisis datasets (e.g. UNHCR, ACLED)  
- Analyze differences by gender, income, location (urban/rural), labor force

## Key Indicators (examples)

- **Account (% age 15+):**  
  % of adults with any financial account

- **Mobile money account (% age 15+):**  
  % with a registered mobile money account

- **Saved at financial institution (% age 15+):**  
  % saving at formal institutions

- **Used internet/mobile to access account:**  
  % accessing accounts via digital means

## Documentation

- **Definitions:** See `Series table` sheet  
- **Methodology PDF:**  
  [Global Findex 2021 Methodology]  
  (<https://globalfindex.worldbank.org/sites/globalfindex/files/2022-06/Global%20Findex%20Database%202021%20Methodology.pdf>)

## Research Questions

- How has account ownership changed in crisis regions from 2011 to 2021?  
- Do mobile money usage rates correlate with crypto adoption?  
- Is digital access higher among younger or urban populations?

## Summary

A critical dataset for understanding financial behavior and inclusion  
globally. Provides a solid foundation for comparing traditional and  
emerging (crypto) financial tools in underbanked and crisis-affected  
countries.
