# Data Exploration

This folder is used to explore, validate, and check the quality of cleaned
datasets. Team members can use this area to investigate coverage,
distributions, and gaps.

## How This Folder Works

Notebooks or scripts here should:

1. Read data from `1_datasets/raw_datasets/` or `2_data_preparation/processed/`
2. Generate plots or summaries that help check data completeness or structure
3. Save visuals (if needed) to `figures/` or note findings in `guide.md`

## USDT Volume Exploration Guide

This folder contains early exploratory charts to help understand USDT trading
volume across centralized exchanges (CEXs) between 2019 and 2024.

## Included Figures

- `usdt_volume_all_exchanges.png`: Total daily USDT volume summed across all exchanges.
- `usdt_volume_binance_only.png`: Daily USDT volume on Binance only.
- `usdt_volume_binance_annotated.png`: Binance volume annotated with key access
dates for:
  - Nigeria (2019-01-01)
  - Sudan (2020-01-01)
  - Lebanon (2020-06-01)
  - Afghanistan (2021-01-01)

These charts provide early evidence that Binance volume correlates with broader
 accessibility across FX-stressed countries.

## Contribution Guide

- Use separate notebooks or scripts for each dataset/topic
- Describe what you’re exploring and what you found in `guide.md`
- Use this stage to flag issues before we analyze
