"""
CryptoCompare Free API Scraper
==============================

CryptoCompare provides cryptocurrency price data through a free API.
Free tier: 100,000 calls/month (about 3,200 calls/day)

Useful for:
- Current prices in multiple fiat currencies (including our target countries)
- Historical price data
- Exchange-specific price data
- Market context for crisis analysis

Author: Clement MUGISHA
"""

import requests
import time
from datetime import datetime
from typing import List, Dict, Any
import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from utils.csv_data_manager import CSVDataManager


class CryptoCompareScraper:
    """
    Scraper for CryptoCompare cryptocurrency price data (free tier, no auth required).
    """

    def __init__(self):
        self.base_url = "https://min-api.cryptocompare.com/data"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.csv_manager = CSVDataManager()

        # Rate limiting for free tier (conservative approach)
        self.rate_limit_delay = 1.0

    def get_current_prices(
        self, cryptocurrencies: List[str], fiat_currencies: List[str]
    ) -> Dict[str, Any]:
        """
        Get current cryptocurrency prices in multiple fiat currencies.

        Parameters:
        -----------
        cryptocurrencies : list
            List of crypto symbols (e.g., ['BTC', 'ETH', 'USDT'])
        fiat_currencies : list
            List of fiat currency codes (e.g., ['USD', 'SDG', 'VES'])

        Returns:
        --------
        dict
            Price data for each crypto/fiat pair
        """

        results = {}

        for crypto in cryptocurrencies:
            fiat_list = ",".join(fiat_currencies)

            url = f"{self.base_url}/price"
            params = {"fsym": crypto, "tsyms": fiat_list}

            try:
                print(f"🔍 Fetching {crypto} prices vs {fiat_list}")
                response = self.session.get(url, params=params, timeout=15)
                response.raise_for_status()

                data = response.json()

                # Check for error response
                if "Response" in data and data["Response"] == "Error":
                    print(
                        f"❌ CryptoCompare error for {crypto}: {data.get('Message', 'Unknown error')}"
                    )
                    continue

                results[crypto] = {
                    "prices": data,
                    "timestamp": datetime.now().isoformat(),
                    "source": "cryptocompare",
                }

                print(f"✅ Got {crypto} prices in {len(data)} currencies")

                # Rate limiting
                time.sleep(self.rate_limit_delay)

            except requests.exceptions.RequestException as e:
                print(f"❌ Network error fetching {crypto} prices: {e}")
            except Exception as e:
                print(f"❌ Error fetching {crypto} prices: {e}")

        return results

    def get_historical_daily(
        self, crypto: str, fiat: str, days: int = 30
    ) -> Dict[str, Any]:
        """
        Get daily historical price data.

        Parameters:
        -----------
        crypto : str
            Cryptocurrency symbol (e.g., 'BTC', 'USDT')
        fiat : str
            Fiat currency code (e.g., 'USD', 'SDG')
        days : int
            Number of days to fetch (max 2000 for free tier)

        Returns:
        --------
        dict
            Historical price data
        """

        url = f"{self.base_url}/histoday"
        params = {
            "fsym": crypto,
            "tsym": fiat,
            "limit": min(days - 1, 2000),  # API uses limit as days-1
        }

        try:
            print(f"🔍 Fetching {days} days of {crypto}/{fiat} history")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            if data.get("Response") == "Error":
                print(f"❌ CryptoCompare error: {data.get('Message', 'Unknown error')}")
                return {}

            result = {
                "crypto": crypto,
                "fiat": fiat,
                "days_requested": days,
                "data_points": len(data.get("Data", [])),
                "historical_data": data.get("Data", []),
                "timestamp": datetime.now().isoformat(),
                "source": "cryptocompare",
            }

            print(f"✅ Retrieved {result['data_points']} daily price points")
            return result

        except Exception as e:
            print(f"❌ Error fetching historical data: {e}")
            return {}

    def get_exchange_prices(
        self, crypto: str, fiat: str, exchange: str = None
    ) -> Dict[str, Any]:
        """
        Get prices from specific exchanges (useful for P2P platforms).

        Parameters:
        -----------
        crypto : str
            Cryptocurrency symbol
        fiat : str
            Fiat currency code
        exchange : str
            Exchange name (optional)

        Returns:
        --------
        dict
            Exchange-specific price data
        """

        # Skip exchange-specific data - requires premium API
        print(
            f"🔍 Skipping exchange-specific data for {crypto}/{fiat} (requires premium API)"
        )
        return {}

    def collect_crisis_context_data(self) -> Dict[str, Any]:
        """
        Collect comprehensive price data for crisis analysis.

        Returns:
        --------
        dict
            Collection results with price data
        """

        print("\n🌍 CRYPTOCOMPARE: Collecting crisis context data")
        print("-" * 50)

        # Target cryptocurrencies
        cryptocurrencies = ["BTC", "ETH", "USDT", "USDC"]

        # Target fiat currencies (crisis countries + major currencies)
        fiat_currencies = ["USD", "EUR", "ARS", "VES"]  # Start with supported ones

        results = {
            "timestamp": datetime.now().isoformat(),
            "source": "cryptocompare",
            "current_prices": {},
            "historical_data": {},
            "exchange_data": {},
            "errors": [],
        }

        try:
            # 1. Get current prices for all crypto/fiat pairs
            print("💰 Fetching current cryptocurrency prices...")
            current_prices = self.get_current_prices(cryptocurrencies, fiat_currencies)
            results["current_prices"] = current_prices

            if current_prices:
                # Save current prices
                self._save_current_prices_to_csv(current_prices)

            # 2. Get historical data for supported pairs only (last 30 days)
            print("📊 Fetching historical price data...")
            # Only use pairs that CryptoCompare definitely supports
            key_pairs = [
                ("BTC", "USD"),
                ("USDT", "USD"),
                ("BTC", "EUR"),  # More likely to be supported than ARS
                ("ETH", "USD"),  # Alternative to problematic pairs
            ]

            for crypto, fiat in key_pairs:
                print(f"📈 Getting 30-day history for {crypto}/{fiat}...")
                historical = self.get_historical_daily(crypto, fiat, 30)
                if historical:
                    results["historical_data"][f"{crypto}_{fiat}"] = historical
                    # Save historical data to proper folder
                    self._save_historical_data_to_csv(historical, crypto, fiat)
                else:
                    print(f"⚠️  {crypto}/{fiat} historical data not available")

                time.sleep(self.rate_limit_delay)

            # 3. Skip exchange-specific data (requires premium API)
            print("🏪 Skipping exchange-specific data (premium API required)")
            results["exchange_data"] = {}

            print("✅ CryptoCompare data collection complete!")
            print(
                f"   💰 Current prices: {len(results['current_prices'])} cryptocurrencies"
            )
            print(f"   📊 Historical datasets: {len(results['historical_data'])} pairs")
            print(f"   🏪 Exchange data: {len(results['exchange_data'])} pairs")

            return results

        except Exception as e:
            error_msg = f"Error in CryptoCompare collection: {e}"
            print(f"❌ {error_msg}")
            results["errors"].append(error_msg)
            return results

    def _save_current_prices_to_csv(self, price_data: Dict[str, Any]):
        """Save current price data to CSV."""
        try:
            import pandas as pd

            rows = []
            for crypto, crypto_data in price_data.items():
                timestamp = crypto_data["timestamp"]
                for fiat, price in crypto_data["prices"].items():
                    rows.append(
                        {
                            "timestamp": timestamp,
                            "cryptocurrency": crypto,
                            "fiat_currency": fiat,
                            "price": price,
                            "source": "cryptocompare",
                        }
                    )

            if rows:
                df = pd.DataFrame(rows)
                filename = (
                    f"cryptocompare_prices_{datetime.now().strftime('%Y-%m-%d')}.csv"
                )
                filepath = f"data/analysis/{filename}"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                df.to_csv(filepath, index=False)
                print(f"💾 Saved {len(rows)} price records to {filename}")

        except Exception as e:
            print(f"❌ Error saving prices to CSV: {e}")

    def _save_historical_data_to_csv(
        self, historical_data: Dict[str, Any], crypto: str, fiat: str
    ):
        """Save historical data to proper historical folder."""
        try:
            if (
                "historical_data" in historical_data
                and historical_data["historical_data"]
            ):
                rows = []
                for daily_data in historical_data["historical_data"]:
                    rows.append(
                        {
                            "date": datetime.fromtimestamp(daily_data["time"]).strftime(
                                "%Y-%m-%d"
                            ),
                            "crypto": crypto,
                            "fiat": fiat,
                            "open": daily_data["open"],
                            "high": daily_data["high"],
                            "low": daily_data["low"],
                            "close": daily_data["close"],
                            "volume": daily_data["volumeto"],
                            "source": "cryptocompare",
                        }
                    )

                if rows:
                    df = pd.DataFrame(rows)
                    # Save to historical/cryptocompare folder
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    filename = f"{crypto}_{fiat}_historical_{date_str}.csv"
                    filepath = f"data/historical/cryptocompare/{filename}"
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    df.to_csv(filepath, index=False)
                    print(f"💾 Saved {len(rows)} historical records to {filepath}")

        except Exception as e:
            print(f"❌ Error saving historical data to CSV: {e}")


def test_cryptocompare_scraper():
    """Test the CryptoCompare scraper."""

    print("🧪 TESTING CRYPTOCOMPARE API SCRAPER")
    print("=" * 50)

    scraper = CryptoCompareScraper()

    # Test current prices
    print("\n💰 Testing current price fetching...")
    prices = scraper.get_current_prices(["BTC", "USDT"], ["USD", "EUR", "ARS"])
    print(f"Price results: {list(prices.keys()) if prices else 'None'}")

    # Test historical data
    print("\n📊 Testing historical data...")
    historical = scraper.get_historical_daily("BTC", "USD", 7)
    print(
        f"Historical data points: {historical.get('data_points', 0) if historical else 0}"
    )

    # Test comprehensive collection
    print("\n🌍 Testing comprehensive data collection...")
    results = scraper.collect_crisis_context_data()
    print(f"Collection complete! Results keys: {list(results.keys())}")


if __name__ == "__main__":
    test_cryptocompare_scraper()
