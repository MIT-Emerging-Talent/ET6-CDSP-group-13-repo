# Data Preparation

This folder contains scripts used to clean and prepare raw datasets before
analysis. The goal is to take datasets from `1_datasets/raw_datasets/` and
process them into consistent, analysis-ready formats in
`2_data_preparation/processed/`.

## How This Folder Works

Each script here:

1. Reads raw data from `raw_datasets/`.
2. Processes and standardizes the data (e.g., column formats, volume
   aggregation, filtering).
3. Saves a new file into `2_data_preparation/processed/`, preserving the
   original raw files.

**Important:** Never modify or overwrite raw data files. All outputs should be
written as new files in the processed folder with clear names.

## Scripts and What They Do

### `aggregate_volumes.py`

- **Input:**
  - All raw OHLCV volume CSVs for USDT/USDC from Binance, Bybit, OKX, Coinbase,
    and Kraken.
- **Process:**
  - Reads OHLCV data for all trading pairs where quote is USDT or USDC.
  - Aggregates base volume × close price to get quote volume in USD.
  - Summarizes daily volume per exchange.
- **Output:**
  - `central_exchange_daily_volume_2019-24.csv` in
    `2_data_preparation/processed/`.

### `clean_cex_policy.py` (TODO)

### `active_wallet_count.csv`

- **Input:**
  - `raw_datasets/active_wallet_count.csv` (single file with data for
    Nigeria, Lebanon, Afghanistan, and Sudan).
- **Process:**
  1. Replaces `<1` values with `0`.
  2. Standardizes dates to `YYYY-MM-DD`.
  3. Filters for target countries (ignores others).
  4. Cleans column names (e.g., `bitcoin (nigeria)` → `bitcoin_nigeria`).
- **Output:**
  - Main file: `processed/active_wallet_count_cleaned.csv`.

## Where Files Are Stored

| Folder                          | Purpose                                 |
|---------------------------------|-----------------------------------------|
| `raw_datasets/`                 | Raw unmodified input data               |
| `2_data_preparation/processed/` | Cleaned, formatted, and aggregated data |
| `2_data_preparation/`           | Scripts that convert raw to processed   |

## Contribution Guide

Keep it reproducible and transparent for everyone working on different parts
of the project.
