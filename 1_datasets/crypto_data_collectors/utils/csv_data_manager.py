"""
CSV Data Storage Utility
========================

This module provides utilities for storing and managing P2P cryptocurrency market data
using CSV files. All data throughout the project lifecycle will be stored in CSV format
for simplicity, portability, and ease of analysis.

Features:
- Standardized CSV schema for P2P advertisements
- Daily file organization with automatic directory creation
- Data validation and cleaning
- Batch processing and collection tracking
- Exchange rate integration
- Country-based data organization

File Structure:
data/
├── raw/                    # Raw scraped data
│   ├── 2025-07-29/
│   │   ├── binance_p2p_SD_2025-07-29.csv
│   │   ├── binance_p2p_VE_2025-07-29.csv
│   │   └── okx_p2p_NG_2025-07-29.csv
├── processed/              # Cleaned and enriched data
│   ├── daily_summaries/
│   │   └── summary_2025-07-29.csv
│   ├── premium_calculations/
│   │   └── premiums_2025-07-29.csv
├── exchange_rates/         # Fiat exchange rates
│   └── rates_2025-07-29.csv
└── metadata/              # Collection logs and tracking
    └── collection_log.csv

Author: Clement MUGISHA
License: MIT
"""

import csv
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any
import json
from pathlib import Path


class CSVDataManager:
    """
    Manages all CSV data storage operations for the P2P crypto market data project.
    """

    def __init__(self, base_data_dir: str = None):
        """
        Initialize the CSV data manager.

        Parameters:
        -----------
        base_data_dir : str
            Base directory for all data storage. If None, uses repository structure.
        """
        if base_data_dir is None:
            # Use repository structure
            project_root = Path(__file__).parent.parent.parent.parent
            self.base_dir = project_root / "1_datasets"
        else:
            self.base_dir = Path(base_data_dir)

        self.raw_dir = self.base_dir / "raw_datasets" / "crypto_p2p"
        self.processed_dir = self.base_dir / "processed" / "crypto_p2p"
        self.exchange_rates_dir = self.base_dir / "raw_datasets" / "exchange_rates"
        self.metadata_dir = self.base_dir / "raw_datasets" / "metadata"

        # Create directory structure
        self._create_directories()

        # Standard CSV headers for P2P advertisements
        self.ad_headers = [
            "platform",
            "timestamp",
            "asset",
            "fiat",
            "price",
            "min_amount",
            "max_amount",
            "available_amount",
            "trade_type",
            "country_code",
            "payment_methods",
            "advertiser_name",
            "completion_rate",
            "order_count",
            "ad_id",
            "premium_pct",
            "official_rate",
            "collection_id",
        ]

        # Headers for collection tracking
        self.collection_headers = [
            "collection_id",
            "timestamp",
            "platform",
            "country_code",
            "country_name",
            "fiat_currency",
            "ads_collected",
            "buy_ads",
            "sell_ads",
            "status",
            "error_message",
        ]

        # Headers for exchange rates
        self.rate_headers = [
            "timestamp",
            "fiat_currency",
            "usd_rate",
            "source",
            "collection_id",
        ]

    def _create_directories(self):
        """Create all necessary directories for data storage."""
        directories = [
            self.raw_dir,
            self.processed_dir / "daily_summaries",
            self.processed_dir / "premium_calculations",
            self.processed_dir / "country_aggregates",
            self.exchange_rates_dir,
            self.metadata_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def generate_collection_id(self) -> str:
        """Generate a unique collection ID for batch tracking."""
        return f"collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def save_raw_ads(
        self,
        ads: List[Dict[str, Any]],
        platform: str,
        country_code: str,
        collection_id: str = None,
    ) -> str:
        """
        Save raw P2P advertisement data to CSV.

        Parameters:
        -----------
        ads : list
            List of standardized advertisement dictionaries
        platform : str
            Platform name (e.g., 'binance', 'okx')
        country_code : str
            ISO country code (e.g., 'SD', 'VE')
        collection_id : str, optional
            Unique collection identifier

        Returns:
        --------
        str
            Path to the saved CSV file
        """
        if not collection_id:
            collection_id = self.generate_collection_id()

        # Create date-based subdirectory
        today = date.today().strftime("%Y-%m-%d")
        date_dir = self.raw_dir / today
        date_dir.mkdir(exist_ok=True)

        # Generate filename
        filename = f"{platform}_p2p_{country_code}_{today}.csv"
        filepath = date_dir / filename

        # Add collection_id to each ad
        for ad in ads:
            ad["collection_id"] = collection_id
            # Convert payment_methods list to JSON string for CSV storage
            if isinstance(ad.get("payment_methods"), list):
                ad["payment_methods"] = json.dumps(ad["payment_methods"])

        # Write to CSV
        self._write_csv(filepath, ads, self.ad_headers)

        print(f"✅ Saved {len(ads)} ads to {filepath}")
        return str(filepath)

    def log_collection_run(
        self,
        platform: str,
        country_code: str,
        country_name: str,
        fiat_currency: str,
        ads_collected: int,
        buy_ads: int,
        sell_ads: int,
        status: str = "success",
        error_message: str = "",
        collection_id: str = None,
    ):
        """
        Log a data collection run to the metadata CSV.

        Parameters:
        -----------
        platform : str
            Platform name
        country_code : str
            ISO country code
        country_name : str
            Full country name
        fiat_currency : str
            Fiat currency code
        ads_collected : int
            Total number of ads collected
        buy_ads : int
            Number of BUY advertisements
        sell_ads : int
            Number of SELL advertisements
        status : str
            Collection status ('success', 'error', 'partial')
        error_message : str
            Error details if applicable
        collection_id : str
            Unique collection identifier
        """
        if not collection_id:
            collection_id = self.generate_collection_id()

        log_entry = {
            "collection_id": collection_id,
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "country_code": country_code,
            "country_name": country_name,
            "fiat_currency": fiat_currency,
            "ads_collected": ads_collected,
            "buy_ads": buy_ads,
            "sell_ads": sell_ads,
            "status": status,
            "error_message": error_message,
        }

        log_file = self.metadata_dir / "collection_log.csv"
        self._append_csv(log_file, [log_entry], self.collection_headers)

        print(
            f"📝 Logged collection run: {ads_collected} ads from {platform} for {country_name}"
        )

    def save_exchange_rates(
        self, rates: List[Dict[str, Any]], collection_id: str = None
    ):
        """
        Save exchange rate data to CSV.

        Parameters:
        -----------
        rates : list
            List of exchange rate dictionaries
        collection_id : str
            Collection identifier for tracking
        """
        if not collection_id:
            collection_id = self.generate_collection_id()

        # Add collection_id to each rate
        for rate in rates:
            rate["collection_id"] = collection_id

        today = date.today().strftime("%Y-%m-%d")
        filename = f"rates_{today}.csv"
        filepath = self.exchange_rates_dir / filename

        self._append_csv(filepath, rates, self.rate_headers)
        print(f"💱 Saved {len(rates)} exchange rates to {filepath}")

    def load_raw_ads(
        self, platform: str = None, country_code: str = None, date_str: str = None
    ) -> pd.DataFrame:
        """
        Load raw advertisement data from CSV files.

        Parameters:
        -----------
        platform : str, optional
            Filter by platform
        country_code : str, optional
            Filter by country
        date_str : str, optional
            Filter by date (YYYY-MM-DD format)

        Returns:
        --------
        pd.DataFrame
            Combined advertisement data
        """
        if date_str:
            date_dir = self.raw_dir / date_str
            if not date_dir.exists():
                print(f"❌ No data found for date: {date_str}")
                return pd.DataFrame()
            search_dirs = [date_dir]
        else:
            search_dirs = [d for d in self.raw_dir.iterdir() if d.is_dir()]

        all_data = []

        for date_dir in search_dirs:
            for csv_file in date_dir.glob("*.csv"):
                # Parse filename for filtering
                parts = csv_file.stem.split("_")
                if len(parts) >= 3:
                    file_platform = parts[0]
                    file_country = parts[2]

                    # Apply filters
                    if platform and file_platform != platform:
                        continue
                    if country_code and file_country != country_code:
                        continue

                try:
                    df = pd.read_csv(csv_file)
                    # Convert payment_methods back from JSON string
                    if "payment_methods" in df.columns:
                        df["payment_methods"] = df["payment_methods"].apply(
                            lambda x: json.loads(x) if pd.notna(x) else []
                        )
                    all_data.append(df)
                except Exception as e:
                    print(f"⚠️ Error reading {csv_file}: {e}")

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"📊 Loaded {len(combined_df)} ads from {len(all_data)} files")
            return combined_df
        else:
            print("❌ No data found matching criteria")
            return pd.DataFrame()

    def get_collection_log(self) -> pd.DataFrame:
        """
        Load the collection log CSV.

        Returns:
        --------
        pd.DataFrame
            Collection history
        """
        log_file = self.metadata_dir / "collection_log.csv"
        if log_file.exists():
            return pd.read_csv(log_file)
        else:
            return pd.DataFrame(columns=self.collection_headers)

    def _write_csv(self, filepath: Path, data: List[Dict], headers: List[str]):
        """Write data to CSV file with proper headers."""
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

    def _append_csv(self, filepath: Path, data: List[Dict], headers: List[str]):
        """Append data to CSV file, creating with headers if necessary."""
        file_exists = filepath.exists()

        with open(filepath, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerows(data)

    def create_daily_summary(self, date_str: str = None) -> str:
        """
        Create a daily summary CSV with aggregated metrics.

        Parameters:
        -----------
        date_str : str, optional
            Date to summarize (YYYY-MM-DD). Defaults to today.

        Returns:
        --------
        str
            Path to the summary CSV file
        """
        if not date_str:
            date_str = date.today().strftime("%Y-%m-%d")

        # Load all data for the specified date
        df = self.load_raw_ads(date_str=date_str)

        if df.empty:
            print(f"❌ No data available for {date_str}")
            return ""

        # Calculate summary metrics
        summary_data = []

        for (platform, country, fiat), group in df.groupby(
            [
                "platform",
                "country_code",
                "fiat",
            ]
        ):
            buy_ads = group[group["trade_type"] == "BUY"]
            sell_ads = group[group["trade_type"] == "SELL"]

            summary = {
                "date": date_str,
                "platform": platform,
                "country_code": country,
                "fiat_currency": fiat,
                "total_ads": len(group),
                "buy_ads": len(buy_ads),
                "sell_ads": len(sell_ads),
                "avg_buy_price": buy_ads["price"].mean() if not buy_ads.empty else 0,
                "avg_sell_price": sell_ads["price"].mean() if not sell_ads.empty else 0,
                "price_spread": (sell_ads["price"].mean() - buy_ads["price"].mean())
                if not buy_ads.empty and not sell_ads.empty
                else 0,
                "total_liquidity": group["available_amount"].sum(),
                "avg_premium": group["premium_pct"].mean()
                if "premium_pct" in group.columns
                else 0,
            }
            summary_data.append(summary)

        # Save summary
        summary_file = (
            self.processed_dir / "daily_summaries" / f"summary_{date_str}.csv"
        )
        summary_headers = list(summary_data[0].keys()) if summary_data else []

        self._write_csv(summary_file, summary_data, summary_headers)
        print(f"📈 Created daily summary: {summary_file}")

        return str(summary_file)


def main():
    """
    Test the CSV data manager functionality.
    """
    print("🧪 Testing CSV Data Manager...")

    # Initialize manager
    csv_manager = CSVDataManager()

    # Test sample data
    sample_ads = [
        {
            "platform": "binance",
            "timestamp": datetime.now().isoformat(),
            "asset": "USDT",
            "fiat": "SDG",
            "price": 1050.25,
            "min_amount": 100,
            "max_amount": 5000,
            "available_amount": 2500,
            "trade_type": "SELL",
            "country_code": "SD",
            "payment_methods": ["MTN", "Bank Transfer"],
            "advertiser_name": "TestUser",
            "completion_rate": 95.5,
            "order_count": 150,
            "ad_id": "test_001",
            "premium_pct": 18.3,
            "official_rate": 890.0,
            "collection_id": "",
        }
    ]

    # Test saving data
    collection_id = csv_manager.generate_collection_id()
    csv_manager.save_raw_ads(sample_ads, "binance", "SD", collection_id)

    # Test logging
    csv_manager.log_collection_run(
        platform="binance",
        country_code="SD",
        country_name="Sudan",
        fiat_currency="SDG",
        ads_collected=1,
        buy_ads=0,
        sell_ads=1,
        collection_id=collection_id,
    )

    # Test loading
    loaded_data = csv_manager.load_raw_ads()
    print(f"✅ Loaded {len(loaded_data)} ads from CSV")

    print("🎉 CSV Data Manager test completed!")


if __name__ == "__main__":
    main()
