"""
Exchange Rate Data Collection
============================

Collects official fiat currency exchange rates for calculating
crypto price premiums during crisis periods.

Key Features:
- Multiple rate sources for reliability
- Historical rate collection for trend analysis
- Crisis-period focused data collection
- Premium calculation utilities

Sources:
- xe.com (reliable, good historical data)
- openexchangerates.org (API access)
- fixer.io (EU-based rates)
- Country-specific sources (dolarhoy.com for Argentina, etc.)

Author: Clement MUGISHA
License: MIT
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.country_profiles import get_profile_by_country_code, list_supported_countries
from utils.csv_data_manager import CSVDataManager


class ExchangeRateCollector:
    """
    Collects official exchange rates for premium calculation.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the exchange rate collector.

        Parameters:
        -----------
        api_key : str, optional
            API key for premium services (openexchangerates.org)
        """
        self.api_key = api_key
        self.csv_manager = CSVDataManager()

        # API endpoints
        self.endpoints = {
            "openexchangerates": {
                "current": "https://openexchangerates.org/api/latest.json",
                "historical": "https://openexchangerates.org/api/historical/{date}.json",
            },
            "fixer": {
                "current": "http://data.fixer.io/api/latest",
                "historical": "http://data.fixer.io/api/{date}",
            },
            "exchangerate_api": {
                "current": "https://api.exchangerate-api.com/v4/latest/USD"
            },
        }

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "CryptoAnalysis/1.0 (Research Project)",
            "Accept": "application/json",
        })

    def get_current_rates(self, base_currency: str = "USD") -> Dict[str, float]:
        """
        Get current exchange rates for all target currencies.

        Parameters:
        -----------
        base_currency : str
            Base currency (usually USD)

        Returns:
        --------
        dict
            Currency code -> exchange rate mapping
        """

        rates = {}

        # Try multiple sources for reliability
        sources = ["exchangerate_api", "openexchangerates", "fixer"]

        for source in sources:
            try:
                print(f"📊 Fetching current rates from {source}...")
                source_rates = self._fetch_from_source(source, base_currency)

                if source_rates:
                    rates.update(source_rates)
                    print(f"✅ Got {len(source_rates)} rates from {source}")
                    break  # Use first successful source

            except Exception as e:
                print(f"❌ Error fetching from {source}: {e}")
                continue

        return rates

    def get_historical_rates(
        self, date: str, base_currency: str = "USD"
    ) -> Dict[str, float]:
        """
        Get historical exchange rates for a specific date.

        Parameters:
        -----------
        date : str
            Date in YYYY-MM-DD format
        base_currency : str
            Base currency

        Returns:
        --------
        dict
            Currency code -> exchange rate mapping
        """

        print(f"🕐 Fetching historical rates for {date}...")

        # Try sources with historical data
        historical_sources = ["openexchangerates", "fixer"]

        for source in historical_sources:
            try:
                if source == "openexchangerates" and self.api_key:
                    url = self.endpoints[source]["historical"].format(date=date)
                    params = {"app_id": self.api_key}
                elif source == "fixer":
                    url = self.endpoints[source]["historical"].format(date=date)
                    params = {"access_key": self.api_key} if self.api_key else {}
                else:
                    continue

                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get("rates"):
                    print(f"✅ Got historical rates from {source}")
                    return data["rates"]

            except Exception as e:
                print(f"❌ Error fetching historical data from {source}: {e}")
                continue

        print("⚠️  No historical rates available, using fallback method")
        return {}

    def _fetch_from_source(self, source: str, base_currency: str) -> Dict[str, float]:
        """Fetch rates from a specific source."""

        if source == "exchangerate_api":
            url = self.endpoints[source]["current"]
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("rates", {})

        elif source == "openexchangerates":
            if not self.api_key:
                return {}
            url = self.endpoints[source]["current"]
            params = {"app_id": self.api_key}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("rates", {})

        elif source == "fixer":
            url = self.endpoints[source]["current"]
            params = {"access_key": self.api_key} if self.api_key else {}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("rates", {})

        return {}

    def collect_crisis_period_rates(
        self, country_code: str, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Collect exchange rates for a crisis period.

        Parameters:
        -----------
        country_code : str
            ISO country code
        start_date : str
            Start date (YYYY-MM-DD)
        end_date : str
            End date (YYYY-MM-DD)

        Returns:
        --------
        list
            List of daily exchange rate records
        """

        try:
            profile = get_profile_by_country_code(country_code)
            fiat = profile["fiat"]

            print(f"📊 Collecting exchange rates for {profile['name']} ({fiat})")
            print(f"📅 Period: {start_date} to {end_date}")

            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            rates_data = []
            current_dt = start_dt

            while current_dt <= end_dt:
                date_str = current_dt.strftime("%Y-%m-%d")

                # Get rates for this date
                if current_dt.date() == datetime.now().date():
                    # Use current rates for today
                    rates = self.get_current_rates()
                else:
                    # Get historical rates
                    rates = self.get_historical_rates(date_str)

                if fiat in rates:
                    rate_record = {
                        "timestamp": f"{date_str}T12:00:00Z",
                        "fiat_currency": fiat,
                        "usd_rate": rates[fiat],
                        "source": "api_composite",
                        "collection_id": self.csv_manager.generate_collection_id(),
                    }
                    rates_data.append(rate_record)
                    print(f"✅ {date_str}: 1 USD = {rates[fiat]} {fiat}")
                else:
                    print(f"⚠️  No rate available for {fiat} on {date_str}")

                # Move to next day, but sample weekly for longer periods
                days_to_add = 7 if (end_dt - start_dt).days > 90 else 1
                current_dt += timedelta(days=days_to_add)

                time.sleep(0.5)  # Rate limiting

            # Save to CSV
            if rates_data:
                self.csv_manager.save_exchange_rates(rates_data)
                print(f"💾 Saved {len(rates_data)} exchange rate records")

            return rates_data

        except ValueError as e:
            print(f"❌ Exchange rate error: {e}")
            return []

    def calculate_premium(
        self, crypto_price: float, official_rate: float, base_value: float = 1.0
    ) -> float:
        """
        Calculate the premium percentage of crypto price vs official rate.

        Parameters:
        -----------
        crypto_price : float
            P2P crypto price in local currency
        official_rate : float
            Official USD/local currency rate
        base_value : float
            Base crypto value in USD (usually 1 for stablecoins)

        Returns:
        --------
        float
            Premium percentage (positive = premium, negative = discount)
        """

        if official_rate == 0:
            return 0.0

        implied_usd_price = crypto_price / official_rate
        premium_pct = ((implied_usd_price - base_value) / base_value) * 100

        return round(premium_pct, 2)

    def collect_all_current_rates(self) -> List[Dict[str, Any]]:
        """
        Collect current exchange rates for all target countries.

        Returns:
        --------
        list
            Current exchange rate records
        """

        countries = list_supported_countries()
        current_rates = self.get_current_rates()

        rates_data = []
        collection_id = self.csv_manager.generate_collection_id()

        for country in countries:
            fiat = country["fiat"]

            if fiat in current_rates:
                rate_record = {
                    "timestamp": datetime.now().isoformat() + "Z",
                    "fiat_currency": fiat,
                    "usd_rate": current_rates[fiat],
                    "source": "api_current",
                    "collection_id": collection_id,
                }
                rates_data.append(rate_record)
                print(
                    f"💱 {country['country_code']}: 1 USD = {current_rates[fiat]} {fiat}"
                )

        # Save to CSV
        if rates_data:
            self.csv_manager.save_exchange_rates(rates_data)
            print(f"💾 Saved current rates for {len(rates_data)} currencies")

        return rates_data


def main():
    """
    Test the exchange rate collector.
    """
    collector = ExchangeRateCollector()

    print("🧪 Testing Exchange Rate Collector...")

    # Test current rates
    print("\n📊 Collecting current rates for all countries...")
    current_rates = collector.collect_all_current_rates()

    if current_rates:
        print(f"✅ Collected {len(current_rates)} current exchange rates")

    # Test premium calculation
    print("\n🧮 Testing premium calculation...")
    # Example: USDT trading at 2900 SDG when official rate is 600 SDG/USD
    premium = collector.calculate_premium(2900, 600, 1.0)
    print(f"Premium example: {premium}% (USDT at 2900 SDG vs 600 official rate)")


if __name__ == "__main__":
    main()
