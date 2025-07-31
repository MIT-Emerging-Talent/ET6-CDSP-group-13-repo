"""
CoinGecko Free API Scraper
==========================

CoinGecko provides comprehensive cryptocurrency market data through a free API.
While not specifically P2P focused, it includes some exchange data that may
have P2P components and can provide market context for our crisis analysis.

Free tier: 50 calls/minute
Relevant endpoints:
- /coins/{id}/market_chart - Historical price data
- /exchanges - List of exchanges (some are P2P)
- /simple/price - Current prices with volume data

Author: Clement MUGISHA
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# Add project root to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from utils.csv_data_manager import CSVDataManager


class CoinGeckoScraper:
    """
    Scraper for CoinGecko cryptocurrency market data (free tier, no auth required).
    """

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        self.csv_manager = CSVDataManager()

        # Rate limiting for free tier (50 calls/minute = ~1 call per 1.2 seconds)
        self.rate_limit_delay = 1.5

    def get_current_prices(
        self, cryptocurrencies: List[str], vs_currencies: List[str]
    ) -> Dict[str, Any]:
        """
        Get current cryptocurrency prices against fiat currencies.

        Parameters:
        -----------
        cryptocurrencies : list
            List of crypto IDs (e.g., ['bitcoin', 'tether', 'ethereum'])
        vs_currencies : list
            List of fiat currency codes (e.g., ['usd', 'sdg', 'ves'])

        Returns:
        --------
        dict
            Price data with volume and market cap information
        """

        crypto_ids = ",".join(cryptocurrencies)
        vs_curr = ",".join(vs_currencies)

        url = f"{self.base_url}/simple/price"
        params = {
            "ids": crypto_ids,
            "vs_currencies": vs_curr,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
        }

        try:
            print(f"🔍 Fetching prices from CoinGecko: {crypto_ids} vs {vs_curr}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            # Add metadata
            result = {
                "timestamp": datetime.now().isoformat(),
                "collection_date": datetime.now().strftime("%Y-%m-%d"),
                "source": "coingecko",
                "cryptocurrencies": cryptocurrencies,
                "vs_currencies": vs_currencies,
                "prices": data,
            }

            print(f"✅ Retrieved prices for {len(data)} cryptocurrencies")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error fetching CoinGecko prices: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return {}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {}

    def get_exchanges(self, per_page: int = 50) -> List[Dict[str, Any]]:
        """
        Get list of cryptocurrency exchanges (some may be P2P).

        Parameters:
        -----------
        per_page : int
            Number of exchanges to fetch (max 250)

        Returns:
        --------
        list
            List of exchange information
        """

        url = f"{self.base_url}/exchanges"
        params = {"per_page": min(per_page, 250)}

        try:
            print(f"🔍 Fetching exchanges from CoinGecko...")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            exchanges = response.json()

            # Filter for potentially P2P exchanges
            p2p_keywords = ["p2p", "peer", "local", "otc", "decentralized"]
            p2p_exchanges = []

            for exchange in exchanges:
                name = exchange.get("name", "").lower()
                description = exchange.get("description", "").lower()

                if any(
                    keyword in name or keyword in description
                    for keyword in p2p_keywords
                ):
                    p2p_exchanges.append({
                        "id": exchange.get("id"),
                        "name": exchange.get("name"),
                        "country": exchange.get("country"),
                        "description": exchange.get("description"),
                        "trade_volume_24h_btc": exchange.get("trade_volume_24h_btc"),
                        "trust_score": exchange.get("trust_score"),
                        "url": exchange.get("url"),
                        "timestamp": datetime.now().isoformat(),
                    })

            print(
                f"✅ Found {len(p2p_exchanges)} potential P2P exchanges out of {len(exchanges)} total"
            )
            return p2p_exchanges

        except Exception as e:
            print(f"❌ Error fetching exchanges: {e}")
            return []

    def get_historical_prices(
        self, crypto_id: str, vs_currency: str, days: int = 30
    ) -> Dict[str, Any]:
        """
        Get historical price data for cryptocurrency.

        Parameters:
        -----------
        crypto_id : str
            CoinGecko crypto ID (e.g., 'bitcoin', 'tether')
        vs_currency : str
            Currency to price against (e.g., 'usd')
        days : int
            Number of days of historical data

        Returns:
        --------
        dict
            Historical price data
        """

        url = f"{self.base_url}/coins/{crypto_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days}

        try:
            print(f"🔍 Fetching {days} days of {crypto_id} history vs {vs_currency}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            result = {
                "crypto_id": crypto_id,
                "vs_currency": vs_currency,
                "days": days,
                "timestamp": datetime.now().isoformat(),
                "prices": data.get("prices", []),
                "market_caps": data.get("market_caps", []),
                "total_volumes": data.get("total_volumes", []),
            }

            print(f"✅ Retrieved {len(result['prices'])} price points")
            return result

        except Exception as e:
            print(f"❌ Error fetching historical data: {e}")
            return {}

    def collect_crisis_context_data(self) -> Dict[str, Any]:
        """
        Collect comprehensive cryptocurrency market data for crisis analysis context.

        Returns:
        --------
        dict
            Collection results with market data
        """

        print("\n🌍 COINGECKO: Collecting crisis context data")
        print("-" * 50)

        # Target cryptocurrencies for our analysis
        cryptocurrencies = ["bitcoin", "tether", "ethereum", "binancecoin"]

        # Target fiat currencies (our crisis countries)
        fiat_currencies = [
            "usd",
            "eur",
        ]  # CoinGecko may not support all our target fiats

        results = {
            "timestamp": datetime.now().isoformat(),
            "source": "coingecko",
            "current_prices": {},
            "p2p_exchanges": [],
            "historical_data": {},
            "errors": [],
        }

        try:
            # 1. Get current prices
            print("💰 Fetching current cryptocurrency prices...")
            prices = self.get_current_prices(cryptocurrencies, fiat_currencies)
            if prices:
                results["current_prices"] = prices

                # Save current prices
                filename = f"coingecko_prices_{datetime.now().strftime('%Y-%m-%d')}.csv"
                self._save_prices_to_csv(prices, filename)

            time.sleep(self.rate_limit_delay)

            # 2. Get P2P exchanges
            print("🏪 Fetching potential P2P exchanges...")
            exchanges = self.get_exchanges()
            if exchanges:
                results["p2p_exchanges"] = exchanges

                # Save exchange data
                filename = (
                    f"coingecko_p2p_exchanges_{datetime.now().strftime('%Y-%m-%d')}.csv"
                )
                self._save_exchanges_to_csv(exchanges, filename)

            time.sleep(self.rate_limit_delay)

            # 3. Get some historical context (last 30 days for Bitcoin and Tether)
            for crypto in ["bitcoin", "tether"]:
                print(f"📊 Fetching 30-day history for {crypto}...")
                historical = self.get_historical_prices(crypto, "usd", 30)
                if historical:
                    results["historical_data"][crypto] = historical

                time.sleep(self.rate_limit_delay)

            print(f"✅ CoinGecko data collection complete!")
            print(f"   💰 Current prices: {len(results['current_prices'])} datasets")
            print(f"   🏪 P2P exchanges: {len(results['p2p_exchanges'])} found")
            print(
                f"   📊 Historical data: {len(results['historical_data'])} cryptocurrencies"
            )

            return results

        except Exception as e:
            error_msg = f"Error in CoinGecko collection: {e}"
            print(f"❌ {error_msg}")
            results["errors"].append(error_msg)
            return results

    def _save_prices_to_csv(self, price_data: Dict[str, Any], filename: str):
        """Save price data to CSV format."""
        try:
            import pandas as pd

            # Flatten price data for CSV
            rows = []
            for crypto, currencies in price_data.get("prices", {}).items():
                for currency, value in currencies.items():
                    if currency != "last_updated_at":
                        rows.append({
                            "timestamp": price_data["timestamp"],
                            "cryptocurrency": crypto,
                            "fiat_currency": currency.upper(),
                            "price": value,
                            "source": "coingecko",
                        })

            if rows:
                df = pd.DataFrame(rows)
                filepath = f"data/analysis/{filename}"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                df.to_csv(filepath, index=False)
                print(f"💾 Saved {len(rows)} price records to {filename}")

        except Exception as e:
            print(f"❌ Error saving prices to CSV: {e}")

    def _save_exchanges_to_csv(self, exchanges: List[Dict[str, Any]], filename: str):
        """Save exchange data to CSV format."""
        try:
            import pandas as pd

            if exchanges:
                df = pd.DataFrame(exchanges)
                filepath = f"data/analysis/{filename}"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                df.to_csv(filepath, index=False)
                print(f"💾 Saved {len(exchanges)} P2P exchanges to {filename}")

        except Exception as e:
            print(f"❌ Error saving exchanges to CSV: {e}")


def test_coingecko_scraper():
    """Test the CoinGecko scraper."""

    print("🧪 TESTING COINGECKO API SCRAPER")
    print("=" * 50)

    scraper = CoinGeckoScraper()

    # Test current prices
    print("\n💰 Testing current price fetching...")
    prices = scraper.get_current_prices(["bitcoin", "tether"], ["usd", "eur"])
    print(f"Price result keys: {list(prices.keys()) if prices else 'None'}")

    # Test exchanges
    print("\n🏪 Testing P2P exchange discovery...")
    exchanges = scraper.get_exchanges(20)
    print(f"Found {len(exchanges)} potential P2P exchanges")

    # Test comprehensive collection
    print("\n🌍 Testing comprehensive data collection...")
    results = scraper.collect_crisis_context_data()
    print(f"Collection complete! Results keys: {list(results.keys())}")


if __name__ == "__main__":
    test_coingecko_scraper()
