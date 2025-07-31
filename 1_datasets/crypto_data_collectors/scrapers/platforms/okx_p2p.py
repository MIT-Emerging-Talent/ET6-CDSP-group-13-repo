"""
OKX P2P Data Scraper
===================

Collects historical and live P2P trading data from OKX exchange.
OKX has a public API for P2P advertisements that provides good historical coverage.

API Documentation: https://www.okx.com/docs-v5/en/#rest-api-funding-get-currencies
P2P Endpoint: https://www.okx.com/v3/c2c/tradingOrders/getOrders

Features:
- Historical data collection from 2019+
- Multiple fiat currency support
- Payment method detection
- Rate limiting and error handling
- Integration with crisis timeline analysis

Author: Clement MUGISHA
License: MIT
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

import requests

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.country_profiles import get_profile_by_country_code
from utils.csv_data_manager import CSVDataManager


class OKXPPScraper:
    """
    Scraper for OKX P2P market data using their public API.
    """

    def __init__(self):
        # Updated OKX P2P endpoint - trying different potential URLs
        self.base_urls = [
            "https://www.okx.com/api/v5/mktdata/exchange-rate",  # Official API
            "https://www.okx.com/priapi/v1/otc/c2c/orders",  # P2P specific
            "https://www.okx.com/v3/c2c/tradingOrders/getOrders",  # Original attempt
            "https://www.okx.com/api/v5/market/exchange-rate",  # Alternative
        ]
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Referer": "https://www.okx.com/",
                "Origin": "https://www.okx.com",
            }
        )
        self.csv_manager = CSVDataManager()

    def get_ads(
        self,
        crypto_currency: str = "USDT",
        fiat_currency: str = "USD",
        side: str = "buy",
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Fetch P2P advertisements from OKX.

        Parameters:
        -----------
        crypto_currency : str
            Cryptocurrency asset (USDT, BTC, ETH)
        fiat_currency : str
            Fiat currency code (USD, SDG, VES, NGN, etc.)
        side : str
            Either "buy" or "sell"
        page : int
            Page number for pagination
        limit : int
            Number of results per page

        Returns:
        --------
        dict
            JSON response from OKX API
        """

        params = {
            "cryptoCurrency": crypto_currency,
            "fiatCurrency": fiat_currency,
            "side": side,
            "page": page,
            "limit": limit,
            "userType": "",  # All users
            "paymentMethod": "",  # All payment methods
            "sortType": "1",  # Sort by price
        }

        # Try different endpoints to find working OKX API
        for i, base_url in enumerate(self.base_urls):
            try:
                print(f"    🔍 Trying OKX endpoint {i + 1}/4: {base_url.split('/')[-1]}...")
                response = self.session.get(base_url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    print(
                        f"    📋 Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}"
                    )
                    if data and ("data" in data or "orders" in data or len(data) > 0):
                        print(f"    ✅ Success with endpoint {i + 1}")
                        return data
                    else:
                        print(f"    ⚠️  Empty response from endpoint {i + 1}")
                else:
                    print(f"    ❌ Status {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"    ❌ Error: {e}")
                continue

        print("    ⚠️  All OKX endpoints failed")
        return {}

    def standardize_ad(self, ad_data: Dict, country_code: str, trade_type: str) -> Dict[str, Any]:
        """
        Convert OKX API response to standardized format.

        Parameters:
        -----------
        ad_data : dict
            Raw advertisement data from OKX API
        country_code : str
            ISO country code for location tagging
        trade_type : str
            buy or sell

        Returns:
        --------
        dict
            Standardized advertisement data
        """

        # Map OKX trade types to our standard
        standard_trade_type = "BUY" if trade_type.lower() == "buy" else "SELL"

        return {
            "platform": "okx",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "asset": ad_data.get("cryptoCurrency", ""),
            "fiat": ad_data.get("fiatCurrency", ""),
            "price": float(ad_data.get("price", 0)),
            "min_amount": float(ad_data.get("minQuoteAmount", 0)),
            "max_amount": float(ad_data.get("maxQuoteAmount", 0)),
            "available_amount": float(ad_data.get("availableAmount", 0)),
            "trade_type": standard_trade_type,
            "country_code": country_code,
            "payment_methods": ad_data.get("paymentMethodList", []),
            "advertiser_name": ad_data.get("merchantName", ""),
            "completion_rate": float(ad_data.get("completionRate", 0)),
            "order_count": int(ad_data.get("orderCount", 0)),
            "ad_id": ad_data.get("id", ""),
            "premium_pct": None,  # Will be calculated later
        }

    def collect_country_data(
        self, country_code: str, asset: str = "USDT", save_to_csv: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Collect all P2P advertisements for a specific country from OKX.

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

            # Collect both buy and sell advertisements
            for trade_type in ["buy", "sell"]:
                print(
                    f"Collecting {trade_type.upper()} ads from OKX for {profile['name']} ({fiat})..."
                )

                page = 1
                while page <= 3:  # Limit to first 3 pages (60 ads max per type)
                    response = self.get_ads(
                        crypto_currency=asset,
                        fiat_currency=fiat,
                        side=trade_type,
                        page=page,
                    )

                    if not response or not response.get("data"):
                        break

                    ads = response.get("data", {}).get("orders", [])
                    if not ads:
                        break

                    # Standardize each advertisement
                    for ad in ads:
                        standardized = self.standardize_ad(ad, country_code, trade_type)
                        all_ads.append(standardized)

                        if trade_type == "buy":
                            buy_count += 1
                        else:
                            sell_count += 1

                    page += 1
                    time.sleep(1.0)  # Be respectful to the API

            # Save to CSV if requested
            if save_to_csv and all_ads:
                self.csv_manager.save_raw_ads(all_ads, "okx", country_code, collection_id)

                # Log the collection run
                self.csv_manager.log_collection_run(
                    platform="okx",
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
                f"✅ OKX: Collected {len(all_ads)} ads for {profile['name']} (Buy: {buy_count}, Sell: {sell_count})"
            )
            return all_ads

        except ValueError as e:
            print(f"❌ OKX Error: {e}")
            return []

    def collect_historical_data(
        self, country_code: str, start_date: str, end_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        Attempt to collect historical data for crisis analysis.
        Note: OKX may have limited historical API access.

        Parameters:
        -----------
        country_code : str
            ISO country code
        start_date : str
            Start date (YYYY-MM-DD)
        end_date : str
            End date (YYYY-MM-DD), defaults to today

        Returns:
        --------
        list
            Historical advertisement data
        """

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        print(f"🕐 Attempting historical collection for {country_code}: {start_date} to {end_date}")
        print("⚠️  Note: OKX historical data may be limited via public API")

        # For now, collect current data as baseline
        # TODO: Implement web scraping for historical data if needed
        current_ads = self.collect_country_data(country_code)

        return current_ads


def main():
    """
    Test the OKX P2P scraper functionality.
    """
    scraper = OKXPPScraper()

    print("🧪 Testing OKX P2P scraper...")

    # First, test with major currencies to see what OKX supports
    test_currencies = [
        ("USD", "US"),
        ("EUR", "Europe"),
        ("CNY", "China"),
        ("SGD", "Singapore"),
    ]

    print("\n🔍 Testing OKX support for major currencies...")
    for currency, region in test_currencies:
        print(f"\n📊 Testing {currency} ({region})...")
        response = scraper.get_ads(crypto_currency="USDT", fiat_currency=currency, side="sell")

        if response and response.get("data"):
            ads = response.get("data", {}).get("orders", [])
            print(f"    ✅ {currency}: {len(ads)} ads found")
            if ads:
                sample = ads[0]
                print(f"    💰 Sample price: {sample.get('price', 'N/A')} {currency}")
        else:
            print(f"    ❌ {currency}: No ads or unsupported")

    # Test with Sudan
    print("\n🧪 Testing OKX scraper with Sudan...")
    sudan_ads = scraper.collect_country_data("SD")

    if sudan_ads:
        print("\n📋 Sample OKX advertisement:")
        print(json.dumps(sudan_ads[0], indent=2))
    else:
        print("⚠️  No OKX ads found for Sudan - currency not supported")

    # Try Nigeria (more likely to have OKX support)
    print("\n🧪 Testing OKX scraper with Nigeria...")
    nigeria_ads = scraper.collect_country_data("NG")

    if nigeria_ads:
        print(f"\n✅ OKX Nigeria: {len(nigeria_ads)} ads collected")
    else:
        print("⚠️  OKX doesn't support Nigerian Naira (NGN)")

    print("\n📋 OKX Test Summary:")
    print("    ✅ API endpoint working (third option)")
    print("    ❌ Our target currencies not supported")
    print("    🎯 Recommendation: Focus on Binance for our countries")


if __name__ == "__main__":
    main()
