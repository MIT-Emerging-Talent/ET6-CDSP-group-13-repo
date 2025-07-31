"""
Master Data Collection Orchestrator
===========        # Initialize working platform scrapers only
        self.scrapers = {
            'binance': BinanceP2PScraper(),
            # 'okx': OKXPPScraper(),  # REMOVED - currencies not supported
            # 'paxful': PaxfulHistoricalScraper()  # REMOVED - no accessible data
        }==================

Coordinates data collection across all platforms and sources for
comprehensive crisis impact analysis.

Features:
- Multi-platform data collection
- Crisis-period focused sampling
- Exchange rate integration
- Premium calculation
- Data quality validation
- Progress tracking and resumption

Author: Clement MUGISHA
License: MIT
"""

import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.binance_p2p import BinanceP2PScraper
from scrapers.platforms.coingecko_free import CoinGeckoScraper
from scrapers.platforms.cryptocompare_free import CryptoCompareScraper
from utils.country_profiles import get_profile_by_country_code, list_supported_countries
from utils.csv_data_manager import CSVDataManager
from utils.exchange_rates import ExchangeRateCollector

# Removed non-working scrapers:
# from scrapers.platforms.okx_p2p import OKXPPScraper
# from scrapers.platforms.paxful_historical import PaxfulHistoricalScraper


class DataCollectionOrchestrator:
    """
    Master coordinator for all data collection activities.
    """

    def __init__(self, exchange_api_key: str = None):
        """
        Initialize the orchestrator with all scrapers and utilities.

        Parameters:
        -----------
        exchange_api_key : str, optional
            API key for exchange rate services
        """
        self.csv_manager = CSVDataManager()
        self.exchange_collector = ExchangeRateCollector(exchange_api_key)

        # Initialize working platform scrapers only
        self.scrapers = {
            "binance": BinanceP2PScraper(),
            # Removed non-working scrapers after testing:
            # "okx": OKXPPScraper(),  # Target currencies not supported
            # "paxful": PaxfulHistoricalScraper(),  # No accessible archived data
        }

        # Initialize free API scrapers for market context
        self.context_scrapers = {
            "coingecko": CoinGeckoScraper(),
            "cryptocompare": CryptoCompareScraper(),
        }

        print("🚀 Data Collection Orchestrator initialized")
        print(f"📊 Available P2P platforms: {list(self.scrapers.keys())}")
        print(f"📈 Available context APIs: {list(self.context_scrapers.keys())}")

    def collect_comprehensive_snapshot(self, countries: List[str] = None) -> Dict[str, Any]:
        """
        Collect comprehensive data including P2P data and market context.

        Parameters:
        -----------
        countries : list, optional
            List of country codes to collect. If None, collects all.

        Returns:
        --------
        dict
            Complete data collection results
        """

        print("\n🌍 COMPREHENSIVE DATA COLLECTION")
        print("=" * 50)

        results = {
            "timestamp": datetime.now().isoformat(),
            "p2p_data": {},
            "market_context": {},
            "exchange_rates": {},
            "total_ads_collected": 0,
            "errors": [],
        }

        # 1. Collect P2P data (our core data)
        print("🔥 Collecting P2P data...")
        p2p_results = self.collect_current_snapshot(countries)
        results["p2p_data"] = p2p_results
        results["total_ads_collected"] = p2p_results.get("total_ads", 0)

        # 2. Collect market context from free APIs
        print("\n📊 Collecting market context data...")
        for api_name, scraper in self.context_scrapers.items():
            try:
                print(f"📈 Collecting from {api_name.upper()}...")
                context_data = scraper.collect_crisis_context_data()
                results["market_context"][api_name] = context_data
                print(f"✅ {api_name.upper()} context data collected")
            except Exception as e:
                error_msg = f"Error collecting {api_name} context: {e}"
                print(f"❌ {error_msg}")
                results["errors"].append(error_msg)

        # 3. Exchange rates are already included in collect_current_snapshot
        results["exchange_rates"] = p2p_results.get("exchange_rates", {})

        print("\n🎉 COMPREHENSIVE COLLECTION COMPLETE!")
        print(f"📊 P2P ads collected: {results['total_ads_collected']}")
        print(f"📈 Context APIs: {len(results['market_context'])} sources")
        print(f"💱 Exchange rates: {len(results.get('exchange_rates', {}))} currencies")

        return results

    def collect_current_snapshot(self, countries: List[str] = None) -> Dict[str, Any]:
        """
        Collect current market snapshot across all platforms.

        Parameters:
        -----------
        countries : list, optional
            List of country codes to collect. If None, collects all.

        Returns:
        --------
        dict
            Collection summary and statistics
        """

        if not countries:
            countries = [c["country_code"] for c in list_supported_countries()]

        print(f"📊 Starting current market snapshot for {len(countries)} countries")
        print(f"🎯 Target countries: {', '.join(countries)}")

        collection_summary = {
            "timestamp": datetime.now().isoformat(),
            "countries_processed": 0,
            "total_ads_collected": 0,
            "platform_stats": {},
            "errors": [],
        }

        # First, collect current exchange rates
        print("\n💱 Collecting current exchange rates...")
        try:
            self.exchange_collector.collect_all_current_rates()
            print("✅ Exchange rates collected")
        except Exception as e:
            error_msg = f"Exchange rate collection failed: {e}"
            print(f"❌ {error_msg}")
            collection_summary["errors"].append(error_msg)

        # Collect from each platform
        for platform_name, scraper in self.scrapers.items():
            print(f"\n🔍 Collecting from {platform_name.upper()}...")
            platform_ads = 0
            platform_countries = 0

            for country_code in countries:
                try:
                    country_profile = get_profile_by_country_code(country_code)
                    print(f"\n📍 {platform_name}: {country_profile['name']} ({country_code})")

                    # Collect data from this platform for this country
                    if hasattr(scraper, "collect_country_data"):
                        ads = scraper.collect_country_data(country_code)
                        platform_ads += len(ads)
                        if ads:
                            platform_countries += 1

                    # Rate limiting between countries
                    time.sleep(1)

                except Exception as e:
                    error_msg = f"{platform_name} failed for {country_code}: {e}"
                    print(f"❌ {error_msg}")
                    collection_summary["errors"].append(error_msg)
                    continue

            collection_summary["platform_stats"][platform_name] = {
                "ads_collected": platform_ads,
                "countries_successful": platform_countries,
            }
            collection_summary["total_ads_collected"] += platform_ads

            print(f"✅ {platform_name}: {platform_ads} ads from {platform_countries} countries")

            # Rate limiting between platforms
            time.sleep(2)

        collection_summary["countries_processed"] = len(countries)

        print("\n🎉 Current snapshot complete!")
        print(f"📊 Total ads collected: {collection_summary['total_ads_collected']}")
        print(f"🌍 Countries processed: {collection_summary['countries_processed']}")

        return collection_summary

    def collect_crisis_period_data(
        self,
        country_code: str,
        crisis_start: str,
        crisis_end: str,
        platforms: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Collect historical data for a specific crisis period.

        Parameters:
        -----------
        country_code : str
            ISO country code
        crisis_start : str
            Crisis start date (YYYY-MM-DD)
        crisis_end : str
            Crisis end date (YYYY-MM-DD)
        platforms : list, optional
            Platforms to collect from. Defaults to all available.

        Returns:
        --------
        dict
            Crisis period collection summary
        """

        if not platforms:
            platforms = list(self.scrapers.keys())

        country_profile = get_profile_by_country_code(country_code)

        print("\n🚨 CRISIS PERIOD DATA COLLECTION")
        print(f"🌍 Country: {country_profile['name']} ({country_code})")
        print(f"📅 Period: {crisis_start} to {crisis_end}")
        print(f"🔍 Platforms: {', '.join(platforms)}")

        crisis_summary = {
            "country_code": country_code,
            "country_name": country_profile["name"],
            "crisis_start": crisis_start,
            "crisis_end": crisis_end,
            "platforms_attempted": platforms,
            "total_historical_ads": 0,
            "exchange_rates_collected": 0,
            "platform_results": {},
            "errors": [],
        }

        # Collect exchange rates for crisis period
        print("\n💱 Collecting exchange rates for crisis period...")
        try:
            rates = self.exchange_collector.collect_crisis_period_rates(
                country_code, crisis_start, crisis_end
            )
            crisis_summary["exchange_rates_collected"] = len(rates)
            print(f"✅ Collected {len(rates)} exchange rate records")
        except Exception as e:
            error_msg = f"Crisis exchange rates failed: {e}"
            print(f"❌ {error_msg}")
            crisis_summary["errors"].append(error_msg)

        # Attempt historical collection from each platform
        for platform in platforms:
            print(f"\n🕐 Collecting historical {platform} data...")

            try:
                scraper = self.scrapers[platform]
                historical_ads = []

                # Different collection methods for different platforms
                if platform == "paxful" and hasattr(scraper, "collect_historical_data"):
                    historical_ads = scraper.collect_historical_data(
                        country_code, crisis_start, crisis_end
                    )
                elif hasattr(scraper, "collect_country_data"):
                    # For platforms without historical API, collect current as baseline
                    print(
                        f"⚠️  {platform} doesn't support historical API, collecting current baseline"
                    )
                    historical_ads = scraper.collect_country_data(country_code)

                crisis_summary["platform_results"][platform] = {
                    "ads_collected": len(historical_ads),
                    "status": "success" if historical_ads else "no_data",
                }
                crisis_summary["total_historical_ads"] += len(historical_ads)

                print(f"✅ {platform}: {len(historical_ads)} historical records")

            except Exception as e:
                error_msg = f"Historical {platform} collection failed: {e}"
                print(f"❌ {error_msg}")
                crisis_summary["errors"].append(error_msg)
                crisis_summary["platform_results"][platform] = {
                    "ads_collected": 0,
                    "status": "error",
                    "error": str(e),
                }

        print("\n🎯 Crisis period collection complete!")
        print(f"📊 Total historical ads: {crisis_summary['total_historical_ads']}")
        print(f"💱 Exchange rates: {crisis_summary['exchange_rates_collected']}")

        return crisis_summary

    def run_comprehensive_collection(self, include_historical: bool = False) -> Dict[str, Any]:
        """
        Run comprehensive data collection across all countries and platforms.

        Parameters:
        -----------
        include_historical : bool
            Whether to attempt historical data collection

        Returns:
        --------
        dict
            Complete collection summary
        """

        print("🚀 COMPREHENSIVE DATA COLLECTION STARTING")
        print("=" * 60)

        start_time = datetime.now()

        comprehensive_summary = {
            "collection_start": start_time.isoformat(),
            "collection_end": None,
            "duration_minutes": 0,
            "current_snapshot": {},
            "historical_collections": [],
            "total_ads_collected": 0,
            "countries_processed": 0,
            "errors": [],
        }

        # Step 1: Current market snapshot
        print("\n📊 STEP 1: Current Market Snapshot")
        print("-" * 40)
        try:
            snapshot_results = self.collect_current_snapshot()
            comprehensive_summary["current_snapshot"] = snapshot_results
            comprehensive_summary["total_ads_collected"] += snapshot_results["total_ads_collected"]
        except Exception as e:
            error_msg = f"Current snapshot failed: {e}"
            print(f"❌ {error_msg}")
            comprehensive_summary["errors"].append(error_msg)

        # Step 2: Historical crisis data (if requested)
        if include_historical:
            print("\n🕐 STEP 2: Historical Crisis Data")
            print("-" * 40)

            # Define key crisis periods for priority collection
            priority_crises = [
                ("SD", "2021-10-01", "2022-04-01"),  # Sudan coup
                ("AF", "2021-08-01", "2022-02-01"),  # Afghanistan Taliban
                ("VE", "2019-01-01", "2020-12-31"),  # Venezuela hyperinflation
                ("NG", "2021-02-01", "2021-08-01"),  # Nigeria crypto ban
            ]

            for country_code, start_date, end_date in priority_crises:
                try:
                    print(f"\n🎯 Priority crisis: {country_code} ({start_date} to {end_date})")
                    crisis_results = self.collect_crisis_period_data(
                        country_code, start_date, end_date
                    )
                    comprehensive_summary["historical_collections"].append(crisis_results)
                    comprehensive_summary["total_ads_collected"] += crisis_results[
                        "total_historical_ads"
                    ]

                except Exception as e:
                    error_msg = f"Crisis collection {country_code} failed: {e}"
                    print(f"❌ {error_msg}")
                    comprehensive_summary["errors"].append(error_msg)

        # Calculate final summary
        end_time = datetime.now()
        comprehensive_summary["collection_end"] = end_time.isoformat()
        comprehensive_summary["duration_minutes"] = round(
            (end_time - start_time).total_seconds() / 60, 2
        )
        comprehensive_summary["countries_processed"] = len(list_supported_countries())

        print("\n" + "=" * 60)
        print("🎉 COMPREHENSIVE COLLECTION COMPLETE!")
        print(f"⏱️  Duration: {comprehensive_summary['duration_minutes']} minutes")
        print(f"📊 Total ads collected: {comprehensive_summary['total_ads_collected']}")
        print(f"🌍 Countries processed: {comprehensive_summary['countries_processed']}")
        print(f"❌ Errors encountered: {len(comprehensive_summary['errors'])}")

        return comprehensive_summary


def main():
    """
    Main function for collecting comprehensive data from all supported countries.
    Uses comprehensive collection to avoid duplication.
    """
    print("🚀 SYSTEMATIC DATA COLLECTION FOR ALL COUNTRIES")
    print("=" * 60)

    orchestrator = DataCollectionOrchestrator()

    # Use country_profiles utility to get all supported countries
    from utils.country_profiles import list_supported_countries

    try:
        # Get all countries from our config
        all_countries = list_supported_countries()
        country_codes = [country["country_code"] for country in all_countries]

        print(f"📊 Target countries from config: {', '.join(country_codes)}")
        print(f"🎯 Total countries to collect: {len(country_codes)}")
        print("=" * 60)

        # Use comprehensive collection (includes P2P + market context - NO DUPLICATION)
        print(f"\n🔍 Running comprehensive collection for all {len(country_codes)} countries...")
        results = orchestrator.collect_comprehensive_snapshot(country_codes)

        print("\n📊 COMPREHENSIVE COLLECTION RESULTS:")
        print(f"📈 P2P ads collected: {results['total_ads_collected']}")
        print(f"📊 Market context sources: {len(results.get('market_context', {}))}")
        print(f"🌍 Countries processed: {len(country_codes)}")

        # Show P2P platform breakdown
        if "p2p_data" in results and "platform_stats" in results["p2p_data"]:
            print(f"📊 P2P Platform stats: {results['p2p_data']['platform_stats']}")

        if results.get("errors"):
            print(f"\n⚠️  Errors encountered: {len(results['errors'])}")
            for error in results["errors"][:3]:  # Show first 3 errors
                print(f"   ❌ {error}")

        # Show success summary
        if results["total_ads_collected"] > 0:
            print(f"\n✅ SUCCESS: Collected {results['total_ads_collected']} total P2P ads")
            print(f"� Plus market context from {len(results.get('market_context', {}))} APIs")
            print(f"�💾 Data saved to: data/raw/{orchestrator.today}/ and data/analysis/")
        else:
            print("\n⚠️  No P2P ads collected - check country currency support")

    except Exception as e:
        print(f"❌ Error loading countries from config: {e}")
        print("📝 Falling back to manual country list...")

        # Fallback to manual list if config fails
        fallback_countries = ["SD", "VE", "AR", "AF", "NG", "ZW"]
        print(f"🔄 Using fallback countries: {', '.join(fallback_countries)}")
        results = orchestrator.collect_comprehensive_snapshot(fallback_countries)

        print("\n📊 Fallback Results:")
        print(f"P2P ads: {results['total_ads_collected']}")
        print(f"Context APIs: {len(results.get('market_context', {}))}")


if __name__ == "__main__":
    main()
