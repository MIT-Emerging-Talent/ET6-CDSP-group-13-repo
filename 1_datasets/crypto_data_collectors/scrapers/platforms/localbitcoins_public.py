"""
LocalBitcoins Public API Scraper
===============================

LocalBitcoins provides public APIs for current P2P Bitcoin trading data
without requiring authentication. This is perfect for immediate data collection.

Public endpoints available:
- /bitcoins/places/{country}/.json - Geographic trading data
- /buy-bitcoins-online/{country}/.json - Buy offers by country
- /sell-bitcoins-online/{country}/.json - Sell offers by country
- /bitcoins/trades/{currency}/.json - Recent trades (limited)

Author: Clement MUGISHA
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

import requests

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.country_profiles import load_profiles
from utils.csv_data_manager import CSVDataManager


class LocalBitcoinsPublicScraper:
    """
    Scraper for LocalBitcoins public P2P Bitcoin data (no authentication required).
    """

    def __init__(self):
        self.base_url = "https://localbitcoins.com"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.csv_manager = CSVDataManager()

    def get_country_ads(self, country_code: str, trade_type: str = "both") -> List[Dict[str, Any]]:
        """
        Get P2P Bitcoin ads for a specific country.

        Parameters:
        -----------
        country_code : str
            ISO country code (e.g., 'SD', 'VE', 'AR')
        trade_type : str
            'buy', 'sell', or 'both'

        Returns:
        --------
        list
            List of P2P advertisement dictionaries
        """

        all_ads = []

        if trade_type in ["buy", "both"]:
            buy_ads = self._get_ads_by_type(country_code, "buy")
            all_ads.extend(buy_ads)

        if trade_type in ["sell", "both"]:
            sell_ads = self._get_ads_by_type(country_code, "sell")
            all_ads.extend(sell_ads)

        return all_ads

    def _get_ads_by_type(self, country_code: str, trade_type: str) -> List[Dict[str, Any]]:
        """Get ads for specific trade type."""

        if trade_type == "buy":
            url = f"{self.base_url}/buy-bitcoins-online/{country_code}/.json"
        else:
            url = f"{self.base_url}/sell-bitcoins-online/{country_code}/.json"

        try:
            print(f"🔍 Fetching {trade_type.upper()} ads from LocalBitcoins for {country_code}...")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            data = response.json()

            # Extract ads from response
            ads = []
            if "data" in data and "ad_list" in data["data"]:
                raw_ads = data["data"]["ad_list"]
                print(f"📊 Found {len(raw_ads)} {trade_type} ads")

                for raw_ad in raw_ads:
                    ad_data = raw_ad.get("data", {})

                    # Extract key information
                    processed_ad = {
                        "platform": "localbitcoins",
                        "country_code": country_code,
                        "asset": "BTC",
                        "fiat": ad_data.get("currency", "USD"),
                        "trade_type": trade_type.upper(),
                        "price": self._safe_float(ad_data.get("temp_price")),
                        "min_amount": self._safe_float(ad_data.get("min_amount")),
                        "max_amount": self._safe_float(ad_data.get("max_amount")),
                        "payment_method": ad_data.get("online_provider", ""),
                        "payment_method_detail": ad_data.get("msg", ""),
                        "advertiser": ad_data.get("profile", {}).get("username", ""),
                        "advertiser_trades": self._safe_int(
                            ad_data.get("profile", {}).get("trade_count")
                        ),
                        "advertiser_feedback": self._safe_float(
                            ad_data.get("profile", {}).get("feedback_score")
                        ),
                        "ad_id": ad_data.get("ad_id", ""),
                        "created_at": ad_data.get("created_at", ""),
                        "is_local_office": ad_data.get("location_string", "") != "",
                        "location": ad_data.get("location_string", ""),
                        "timestamp": datetime.now().isoformat(),
                        "collection_date": datetime.now().strftime("%Y-%m-%d"),
                    }

                    ads.append(processed_ad)

            return ads

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error fetching {trade_type} ads for {country_code}: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error for {country_code}: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error for {country_code}: {e}")
            return []

    def _safe_float(self, value):
        """Safely convert value to float."""
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _safe_int(self, value):
        """Safely convert value to int."""
        try:
            return int(value) if value is not None else 0
        except (ValueError, TypeError):
            return 0

    def collect_country_data(self, country_code: str) -> Dict[str, Any]:
        """
        Collect comprehensive P2P data for a country.

        Returns:
        --------
        dict
            Collection results with ads and metadata
        """

        print(f"\n🌍 LOCALBITCOINS: Collecting data for {country_code}")
        print("-" * 50)

        # Get all ads for country
        ads = self.get_country_ads(country_code, "both")

        if ads:
            # Save to CSV
            filename = f"localbitcoins_p2p_{country_code}_{datetime.now().strftime('%Y-%m-%d')}.csv"
            self.csv_manager.save_raw_ads(ads, filename)

            # Log collection
            self.csv_manager.log_collection_run(
                platform="localbitcoins",
                country_name=self._get_country_name(country_code),
                ads_collected=len(ads),
            )

            # Calculate summary stats
            buy_ads = [ad for ad in ads if ad["trade_type"] == "BUY"]
            sell_ads = [ad for ad in ads if ad["trade_type"] == "SELL"]

            print(f"✅ Collected {len(ads)} ads for {country_code}")
            print(f"   📈 Buy ads: {len(buy_ads)}")
            print(f"   📉 Sell ads: {len(sell_ads)}")

            if ads:
                avg_price = sum(ad["price"] for ad in ads if ad["price"] > 0) / len(
                    [ad for ad in ads if ad["price"] > 0]
                )
                print(f"   💰 Average price: {avg_price:.2f} {ads[0]['fiat']}")

                # Payment method analysis
                payment_methods = [ad["payment_method"] for ad in ads if ad["payment_method"]]
                unique_methods = set(payment_methods)
                print(f"   🏦 Payment methods: {len(unique_methods)} unique")
                if unique_methods:
                    print(f"      Top methods: {list(unique_methods)[:3]}")

            return {
                "success": True,
                "ads_collected": len(ads),
                "buy_ads": len(buy_ads),
                "sell_ads": len(sell_ads),
                "filename": filename,
                "payment_methods": len(
                    set(ad["payment_method"] for ad in ads if ad["payment_method"])
                ),
            }
        else:
            print(f"❌ No ads found for {country_code}")
            # Note: LocalBitcoins may not support all countries or API might be deprecated

            return {"success": False, "ads_collected": 0, "error": "No ads found"}

    def _get_country_name(self, country_code: str) -> str:
        """Get country name from code."""
        country_map = {
            "SD": "Sudan",
            "AF": "Afghanistan",
            "VE": "Venezuela",
            "NG": "Nigeria",
            "ZW": "Zimbabwe",
            "AR": "Argentina",
        }
        return country_map.get(country_code, country_code)

    def collect_all_countries(self) -> Dict[str, Any]:
        """
        Collect data for all target countries.

        Returns:
        --------
        dict
            Complete collection results
        """

        # Load countries using the available function
        countries = load_profiles()

        print("🌍 LOCALBITCOINS P2P DATA COLLECTION")
        print("=" * 50)

        results = {
            "platform": "localbitcoins",
            "total_ads": 0,
            "countries_processed": 0,
            "countries_successful": 0,
            "country_results": {},
            "errors": [],
        }

        for country in countries:
            try:
                country_code = country["country_code"]
                result = self.collect_country_data(country_code)
                results["country_results"][country_code] = result
                results["countries_processed"] += 1

                if result["success"]:
                    results["total_ads"] += result["ads_collected"]
                    results["countries_successful"] += 1

                # Rate limiting - be nice to the API
                time.sleep(2)

            except Exception as e:
                error_msg = f"Error collecting {country.get('country_code', 'unknown')}: {e}"
                print(f"❌ {error_msg}")
                results["errors"].append(error_msg)

        print("\n🎉 LOCALBITCOINS COLLECTION COMPLETE!")
        print(f"📊 Total ads: {results['total_ads']}")
        print(
            f"🌍 Countries successful: {results['countries_successful']}/{results['countries_processed']}"
        )

        return results


def test_localbitcoins_scraper():
    """Test the LocalBitcoins scraper with our target countries."""

    print("🧪 TESTING LOCALBITCOINS PUBLIC API SCRAPER")
    print("=" * 60)

    scraper = LocalBitcoinsPublicScraper()

    # Test with Sudan first
    print("\\n🇸🇩 Testing Sudan (SD)...")
    result = scraper.collect_country_data("SD")
    print(f"Result: {result}")

    # Test with Venezuela
    print("\\n🇻🇪 Testing Venezuela (VE)...")
    result = scraper.collect_country_data("VE")
    print(f"Result: {result}")

    print("\\n✅ LocalBitcoins test complete!")


if __name__ == "__main__":
    test_localbitcoins_scraper()
