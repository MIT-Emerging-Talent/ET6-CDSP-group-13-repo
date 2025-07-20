# Data Preparation

This folder contains scripts used to clean and prepare raw datasets before
analysis. The goal is to take datasets from `1_datasets/raw_datasets/` and
process them into consistent, analysis-ready formats in
`2_data_preparation/processed/`.

## How This Folder Works

Each script here:

1. Reads raw data from `raw_datasets/`
2. Processes and standardizes the data (e.g. column formats, volume
   aggregation, filtering)
3. Saves a new file into `2_data_preparation/processed/`, preserving the
   original raw files

Important: Never modify or overwrite raw data files. All outputs should be
written as new files in the processed folder with clear names.

## Scripts and What They Do

### `aggregate_volumes.py`

- **Input:**
  - All raw OHLCV volume CSVs for USDT/USDC from Binance, Bybit, OKX, Coinbase,
    and Kraken
- **Process:**
  - Reads OHLCV data for all trading pairs where quote is USDT or USDC
  - Aggregates base volume × close price to get quote volume in USD
  - Summarizes daily volume per exchange
- **Output:**
  - `central_exchange_daily_volume_2019-24.csv` in
    `2_data_preparation/processed/`

### `clean_cex_policy.py` (TODO)

## Where Files Are Stored

| Folder                        | Purpose                                 |
|-------------------------------|------------------------------------------|
| `raw_datasets/`               | Raw unmodified input data               |
| `2_data_preparation/processed/` | Cleaned, formatted, and aggregated data |
| `2_data_preparation/`         | Scripts that convert raw to processed   |

## Contribution Guide

If you are cleaning or transforming data:

- Place your script here
- Clearly log the input and output files
- Add a short section like the above for your script in this README

Keep it reproducible and transparent for everyone working on different parts
of the project.
