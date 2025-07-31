"""
Data Viewer Utility
===================

Simple utility to view and analyze collected P2P crypto data from CSV files.
This script helps you explore the data that has been collected.

Usage:
    python utils/data_viewer.py

Author: Clement MUGISHA
License: MIT
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.csv_data_manager import CSVDataManager
import json


def main():
    """
    Main function to display collected data statistics and samples.
    """
    print("📊 P2P Crypto Data Viewer")
    print("=" * 50)

    csv_manager = CSVDataManager()

    # Show collection log
    print("\n📝 Collection History:")
    log_df = csv_manager.get_collection_log()
    if not log_df.empty:
        print(
            log_df[
                ["timestamp", "platform", "country_name", "ads_collected", "status"]
            ].to_string(index=False)
        )
    else:
        print("No collection history found.")

    # Load all raw data
    print("\n📊 All Collected Data:")
    all_data = csv_manager.load_raw_ads()

    if not all_data.empty:
        print(f"Total advertisements: {len(all_data)}")
        print(f"Platforms: {all_data['platform'].unique().tolist()}")
        print(f"Countries: {all_data['country_code'].unique().tolist()}")
        print(f"Assets: {all_data['asset'].unique().tolist()}")
        print(f"Fiat currencies: {all_data['fiat'].unique().tolist()}")

        # Show summary by country
        print("\n🌍 Summary by Country:")
        country_summary = (
            all_data.groupby(["country_code", "fiat"])
            .agg({
                "ad_id": "count",
                "trade_type": lambda x: f"Buy: {sum(x == 'BUY')}, Sell: {sum(x == 'SELL')}",
                "price": ["min", "max", "mean"],
            })
            .round(2)
        )

        country_summary.columns = [
            "Total_Ads",
            "Buy_Sell_Split",
            "Min_Price",
            "Max_Price",
            "Avg_Price",
        ]
        print(country_summary.to_string())

        # Show sample records
        print("\n📋 Sample Records:")
        sample_data = all_data.head(3)
        for idx, row in sample_data.iterrows():
            print(f"\nRecord {idx + 1}:")
            print(f"  Platform: {row['platform']}")
            print(f"  Country: {row['country_code']} ({row['fiat']})")
            print(f"  Type: {row['trade_type']} {row['asset']}")
            print(f"  Price: {row['price']:,.2f} {row['fiat']}")
            print(f"  Amount: {row['min_amount']:,.0f} - {row['max_amount']:,.0f}")
            if isinstance(row["payment_methods"], str):
                try:
                    methods = json.loads(row["payment_methods"])
                    print(
                        f"  Payment Methods: {', '.join(methods[:3])}{'...' if len(methods) > 3 else ''}"
                    )
                except Exception:
                    print(f"  Payment Methods: {row['payment_methods']}")

        # Check data directory structure
        print("\n📁 Data Directory Structure:")
        data_dir = csv_manager.base_dir
        if data_dir.exists():
            for item in data_dir.rglob("*.csv"):
                relative_path = item.relative_to(data_dir)
                file_size = item.stat().st_size
                print(f"  {relative_path} ({file_size:,} bytes)")

    else:
        print("No data found. Run a scraper first to collect data.")

    print("\n" + "=" * 50)
    print("🎉 Data viewing complete!")


if __name__ == "__main__":
    main()
