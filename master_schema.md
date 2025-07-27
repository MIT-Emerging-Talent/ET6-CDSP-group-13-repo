<!-- markdownlint-disable MD013 -->
# CDSP Master Schema
>
> **Live editable version:** <https://docs.google.com/document/d/1VdDuq_X13sRhN6YWIcenJlNuQqqFbR8zvOzRm7iCVQA/edit?usp=sharing>

| Table (source owner)              | Primary keys (likely)           | Important columns (draft)                           | Notes                                 |
|-----------------------------------|---------------------------------|-----------------------------------------------------|---------------------------------------|
| **central_exchange_daily_volume_2019-24.csv** (Ahmed) | `date`           | `usdt_volume`, `usdc_volume`,                     | CSV of major exchanges, ✔ header confirmed                      |
| **capital_controls** (Emre)       | `country_iso`, `date`           | `restriction_type`, `exchange`, `detail`            | text-coded events                     |
| **crisis_severity** (Mustafa)     | `country_iso`, `year`           | `inform_score`, `gdp_pc`, `inflation`, …            | one row per country-year              |
| **fx_black_market_rates** (Clement) | `country_iso`, `date`           | `fx_spread_pct`, `black_rate`, `official_rate`      | *TBD – awaiting header list*          |
| **on_chain_activity** (Anas)      | `chain`, `date`                 | `active_addresses`, `tx_count`, `transfer_volume`   | Cleaned CSV ready ✔ header confirmed         |
