# Data Analysis

This folder contains the final merged datasets, annotated charts, and scripts
for results generation. Each team member's output should live here once data
is ready for visualization or inclusion in the report.

## What Goes Here

- Final cleaned datasets.
- Annotated graphs and outputs.
- Notebooks for producing results and figures.
- Analysis logic and summary tables.

This folder contains final scripts and outputs used to support the research question:
"How liquid and accessible are USDT & USDC on major CEXs, and how do access
rules reshape that liquidity?"

### USDT Volume Timeline + Access

- `usdt_cex_volume_analysis_with_setup.ipynb`: Notebook showing total and
exchange-level USDT volumes. Annotates when Sudan, Nigeria, Lebanon, and
Afghanistan gained access to Binance.
- Supports the conclusion that Binance volume reflects broader accessibility
during FX stress.

### Inputs used

- `/2_data_preparation/processed/central_exchange_daily_volume_2019-24.csv`
- `/2_data_preparation/processed/cex_country_access_expanded.csv`

### Google Trends Analysis (Anas)

- **Files:**
  - `active_wallet_count.csv`
- **Description:** Weekly Google Trends analysis (2020–2025) for Bitcoin,
  Cryptocurrency, Markets, and NFTs across Lebanon, Afghanistan, Sudan, and Nigeria.
  The dataset includes time-series search interest values and summary statistics
  for each topic and country.

## Contribution Guide

- Place final charts, tables, and merged outputs here.
- Keep analysis logic separate from cleaning scripts.
- Reference outputs in your team’s final story map.
