# Data Exploration

This folder is used to explore, validate, and check the quality of cleaned
datasets. Team members can use this area to investigate coverage,
distributions, and gaps.

## How This Folder Works

Notebooks or scripts here should:

1. Read data from `1_datasets/raw_datasets/` or `2_data_preparation/processed/`
2. Generate plots or summaries that help check data completeness or structure
3. Save visuals (if needed) to `figures/` or note findings in `guide.md`

## Example Explorations

### Stablecoin Volume Inspection (Ahmed)

- **Goal:** Check if daily CEX volume shows clear periods of drop/growth
- **Output:** 7-day smoothed volume chart, exchange-level comparison
- **Tools:** Python (pandas, matplotlib)

## Contribution Guide

- Use separate notebooks or scripts for each dataset/topic
- Describe what you’re exploring and what you found in `guide.md`
- Use this stage to flag issues before we analyze
