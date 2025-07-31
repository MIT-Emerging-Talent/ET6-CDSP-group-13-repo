"""
Binance P2P Data Scraper
========================

This module collects live P2P trading advertisements from Binance's public API.
Uses the country profiles to dynamically filter by target regions and currencies.

Key Features:
- Fetches live buy/sell ads for USDT against target fiat currencies
- Integrates with country profiles for automatic parameter setting
- Calculates price premiums against official exchange rates
- Standardized output format for time-series storage

Author: Clement MUGISHA
License: MIT
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.country_profiles import list_supported_countries, get_profile_by_country_code
from utils.csv_data_manager import CSVDataManager


class BinanceP2PScraper:
    """
    Scraper for Binance P2P market data using their public API.
    """

    def __init__(self):
        self.base_url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        self.csv_manager = CSVDataManager()

    def get_ads(
        self,
        asset: str = "USDT",
        fiat: str = "USD",
        trade_type: str = "BUY",
        page: int = 1,
        rows: int = 20,
        timestamp: str = None,
    ) -> Dict[str, Any]:
        """
        Fetch P2P advertisements from Binance.

        Parameters:
        -----------
        asset : str
            Cryptocurrency asset (default: USDT)
        fiat : str
            Fiat currency code (e.g., SDG, VES, NGN)
        trade_type : str
            Either "BUY" or "SELL"
        page : int
            Page number for pagination
        rows : int
            Number of results per page (max 20)
        timestamp : str, optional
            Historical timestamp (experimental)

        Returns:
        --------
        dict
            JSON response from Binance API
        """

        payload = {
            "page": page,
            "rows": rows,
            "payTypes": [],
            "countries": [],
            "publisherType": None,
            "asset": asset,
            "fiat": fiat,
            "tradeType": trade_type,
        }

        # Add timestamp if provided (for historical data testing)
        if timestamp:
            payload["timestamp"] = timestamp

        try:
            response = self.session.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Binance P2P data: {e}")
            return {}

    def standardize_ad(
        self, ad_data: Dict, country_code: str, trade_type: str
    ) -> Dict[str, Any]:
        """
        Convert Binance API response to standardized format.

        Parameters:
        -----------
        ad_data : dict
            Raw advertisement data from Binance API
        country_code : str
            ISO country code for location tagging
        trade_type : str
            BUY or SELL

        Returns:
        --------
        dict
            Standardized advertisement data
        """

        adv = ad_data.get("adv", {})
        advertiser = ad_data.get("advertiser", {})

        return {
            "platform": "binance",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "asset": adv.get("asset", ""),
            "fiat": adv.get("fiatUnit", ""),
            "price": float(adv.get("price", 0)),
            "min_amount": float(adv.get("minSingleTransAmount", 0)),
            "max_amount": float(adv.get("dynamicMaxSingleTransAmount", 0)),
            "available_amount": float(adv.get("surplusAmount", 0)),
            "trade_type": trade_type,
            "country_code": country_code,
            "payment_methods": [
                method.get("tradeMethodName", "")
                for method in adv.get("tradeMethods", [])
            ],
            "advertiser_name": advertiser.get("nickName", ""),
            "completion_rate": float(advertiser.get("monthFinishRate", 0)),
            "order_count": int(advertiser.get("monthOrderCount", 0)),
            "ad_id": adv.get("advNo", ""),
            "premium_pct": None,  # Will be calculated later with exchange rates
        }

    def collect_country_data(
        self, country_code: str, asset: str = "USDT", save_to_csv: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Collect all P2P advertisements for a specific country.

        Parameters:
        -----------
        country_code : str
            ISO country code (e.g., 'SD', 'VE')
        asset : str
            Cryptocurrency asset to collect
        save_to_csv : bool
            Whether to automatically save data to CSV

        Returns:
        --------
        list
            List of standardized advertisement dictionaries
        """

        try:
            profile = get_profile_by_country_code(country_code)
            fiat = profile["fiat"]

            all_ads = []
            buy_count = 0
            sell_count = 0

            # Generate collection ID for this run
            collection_id = self.csv_manager.generate_collection_id()

            # Collect both BUY and SELL advertisements
            for trade_type in ["BUY", "SELL"]:
                print(f"Collecting {trade_type} ads for {profile['name']} ({fiat})...")

                page = 1
                while page <= 5:  # Limit to first 5 pages (100 ads max per type)
                    response = self.get_ads(
                        asset=asset, fiat=fiat, trade_type=trade_type, page=page
                    )

                    if not response or not response.get("data"):
                        break

                    ads = response["data"]
                    if not ads:
                        break

                    # Standardize each advertisement
                    for ad in ads:
                        standardized = self.standardize_ad(ad, country_code, trade_type)
                        all_ads.append(standardized)

                        if trade_type == "BUY":
                            buy_count += 1
                        else:
                            sell_count += 1

                    page += 1
                    time.sleep(0.5)  # Be respectful to the API

            # Save to CSV if requested
            if save_to_csv and all_ads:
                self.csv_manager.save_raw_ads(
                    all_ads, "binance", country_code, collection_id
                )

                # Log the collection run
                self.csv_manager.log_collection_run(
                    platform="binance",
                    country_code=country_code,
                    country_name=profile["name"],
                    fiat_currency=fiat,
                    ads_collected=len(all_ads),
                    buy_ads=buy_count,
                    sell_ads=sell_count,
                    status="success",
                    collection_id=collection_id,
                )

            print(
                f"✅ Collected {len(all_ads)} ads for {profile['name']} (Buy: {buy_count}, Sell: {sell_count})"
            )
            return all_ads

        except ValueError as e:
            print(f"❌ Error: {e}")
            return []

    def collect_all_countries(self) -> List[Dict[str, Any]]:
        """
        Collect P2P data for all supported countries.

        Returns:
        --------
        list
            Combined list of advertisements from all countries
        """

        countries = list_supported_countries()
        all_data = []

        print(f"🚀 Starting data collection for {len(countries)} countries...")

        for country in countries:
            country_code = country["country_code"]
            country_name = country["name"]

            print(f"\n📊 Processing {country_name} ({country_code})...")
            ads = self.collect_country_data(country_code)
            all_data.extend(ads)

            # Brief pause between countries
            time.sleep(1)

        print(f"\n🎉 Collection complete! Total ads collected: {len(all_data)}")
        return all_data

    def test_historical_capability(self, country_code: str = "NG") -> bool:
        """
        Test if Binance API supports historical data collection.

        Parameters:
        -----------
        country_code : str
            Country to test with

        Returns:
        --------
        bool
            True if historical data is accessible
        """

        print(f"🕐 Testing Binance historical data capabilities for {country_code}...")

        try:
            profile = get_profile_by_country_code(country_code)
            fiat = profile["fiat"]

            # Test with various timestamp formats
            test_timestamps = [
                "2021-02-05T00:00:00Z",  # Nigeria crypto ban date
                "1612483200000",  # Unix timestamp for same date
                "2021-02-05",  # Simple date format
                None,  # Current data for comparison
            ]

            for i, timestamp in enumerate(test_timestamps):
                timestamp_label = timestamp if timestamp else "current"
                print(f"  📅 Test {i + 1}: {timestamp_label}")

                response = self.get_ads(
                    asset="USDT", fiat=fiat, trade_type="SELL", timestamp=timestamp
                )

                if response and response.get("data"):
                    ads = response["data"]
                    print(f"    ✅ Got {len(ads)} ads")

                    if ads and timestamp:
                        # Check if data looks different from current
                        sample_ad = ads[0].get("adv", {})
                        print(
                            f"    📊 Sample price: {sample_ad.get('price', 'N/A')} {fiat}"
                        )
                else:
                    print("    ❌ No data returned")

                time.sleep(1)  # Rate limiting

            print("⚠️  Binance P2P API appears to only provide current data")
            print(
                "🔄 For historical analysis, we'll need web scraping or archived data"
            )
            return False

        except Exception as e:
            print(f"❌ Historical test failed: {e}")
            return False


def main():
    """
    Main execution function for testing the scraper.
    """
    scraper = BinanceP2PScraper()

    # Test current data collection
    print("🧪 Testing Binance P2P scraper with Sudan...")
    sudan_ads = scraper.collect_country_data("SD")

    if sudan_ads:
        print("\n📋 Sample advertisement:")
        print(json.dumps(sudan_ads[0], indent=2))

    # Test historical data capabilities
    print("\n🕐 Testing historical data capabilities...")
    scraper.test_historical_capability("NG")  # Test with Nigeria

    # Uncomment to test all countries:
    # all_ads = scraper.collect_all_countries()


if __name__ == "__main__":
    main()
