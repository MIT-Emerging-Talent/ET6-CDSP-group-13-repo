"""
Paxful Historical Data Scraper
==============================

Paxful was a major P2P platform until it shut down in 2023.
This scraper attempts to collect historical data through web scraping
and archived snapshots for crisis impact analysis.

Paxful was particularly important for:
- African markets (Nigeria, Kenya, South Africa)
- Payment method diversity
- Smaller transaction volumes
- Gift card trading

Since Paxful is closed, this focuses on:
1. Archived data from Wayback Machine
2. Cached API responses
3. Third-party data aggregators

Author: Clement MUGISHA
License: MIT
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Add project root to path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from utils.country_profiles import get_profile_by_country_code
from utils.csv_data_manager import CSVDataManager


class PaxfulHistoricalScraper:
    """
    Scraper for historical Paxful P2P market data.
    """

    def __init__(self):
        # Wayback Machine API for archived data
        self.wayback_url = "https://web.archive.org/cdx/search/cdx"
        self.paxful_api_base = "https://paxful.com/rest"  # Historical API endpoints

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )
        self.csv_manager = CSVDataManager()

    def get_wayback_snapshots(
        self, url: str, start_date: str, end_date: str
    ) -> List[str]:
        """
        Get available Wayback Machine snapshots for a URL in date range.

        Parameters:
        -----------
        url : str
            Original URL to search for
        start_date : str
            Start date (YYYYMMDD format)
        end_date : str
            End date (YYYYMMDD format)

        Returns:
        --------
        list
            List of available snapshot URLs
        """

        params = {
            "url": url,
            "output": "json",
            "from": start_date,
            "to": end_date,
            "limit": 50,
        }

        try:
            response = self.session.get(self.wayback_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if len(data) > 1:  # First row is headers
                snapshots = []
                for row in data[1:]:  # Skip header row
                    timestamp, original_url = row[1], row[2]
                    snapshot_url = (
                        f"https://web.archive.org/web/{timestamp}/{original_url}"
                    )
                    snapshots.append(snapshot_url)
                return snapshots

        except Exception as e:
            print(f"Error fetching Wayback snapshots: {e}")

        return []

    def scrape_archived_offers(
        self, snapshot_url: str, country_code: str
    ) -> List[Dict[str, Any]]:
        """
        Scrape P2P offers from an archived Paxful page.

        Parameters:
        -----------
        snapshot_url : str
            Wayback Machine snapshot URL
        country_code : str
            ISO country code

        Returns:
        --------
        list
            Extracted offer data
        """

        try:
            print(f"🕐 Scraping archived Paxful data: {snapshot_url}")
            response = self.session.get(snapshot_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            offers = []

            # Look for offer data in various possible formats
            # Paxful used different HTML structures over time

            # Method 1: JSON data in script tags
            script_tags = soup.find_all("script", type="application/json")
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if "offers" in data or "advertisements" in data:
                        offers.extend(
                            self._extract_offers_from_json(data, country_code)
                        )
                except Exception:
                    continue

            # Method 2: HTML table/div parsing
            offer_containers = soup.find_all(
                ["div", "tr"], class_=["offer", "advertisement", "trade-offer"]
            )
            for container in offer_containers:
                try:
                    offer = self._extract_offer_from_html(container, country_code)
                    if offer:
                        offers.append(offer)
                except Exception:
                    continue

            print(f"✅ Extracted {len(offers)} offers from archive")
            return offers

        except Exception as e:
            print(f"❌ Error scraping archived data: {e}")
            return []

    def _extract_offers_from_json(
        self, data: Dict, country_code: str
    ) -> List[Dict[str, Any]]:
        """Extract offer data from JSON structures."""
        offers = []

        # Handle different JSON structures Paxful used
        offer_lists = []
        if "offers" in data:
            offer_lists.append(data["offers"])
        if "advertisements" in data:
            offer_lists.append(data["advertisements"])
        if "data" in data and isinstance(data["data"], list):
            offer_lists.append(data["data"])

        for offer_list in offer_lists:
            if not isinstance(offer_list, list):
                continue

            for offer in offer_list:
                if not isinstance(offer, dict):
                    continue

                standardized = {
                    "platform": "paxful",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "asset": offer.get("cryptocurrency", offer.get("crypto", "BTC")),
                    "fiat": offer.get("fiat_currency", offer.get("currency", "")),
                    "price": float(offer.get("price", offer.get("rate", 0))),
                    "min_amount": float(
                        offer.get("min_amount", offer.get("minimum", 0))
                    ),
                    "max_amount": float(
                        offer.get("max_amount", offer.get("maximum", 0))
                    ),
                    "available_amount": float(offer.get("available", 0)),
                    "trade_type": "BUY" if offer.get("type") == "buy" else "SELL",
                    "country_code": country_code,
                    "payment_methods": [offer.get("payment_method", "")],
                    "advertiser_name": offer.get("username", offer.get("trader", "")),
                    "completion_rate": float(offer.get("completion_rate", 0)),
                    "order_count": int(
                        offer.get("trades", offer.get("feedback_score", 0))
                    ),
                    "ad_id": offer.get("id", offer.get("offer_id", "")),
                    "premium_pct": None,
                }
                offers.append(standardized)

        return offers

    def _extract_offer_from_html(self, container, country_code: str) -> Dict[str, Any]:
        """Extract offer data from HTML elements."""
        # This would need to be customized based on actual Paxful HTML structure
        # Placeholder implementation
        return None

    def collect_historical_data(
        self, country_code: str, start_date: str, end_date: str = "20231231"
    ) -> List[Dict[str, Any]]:
        """
        Collect historical Paxful data for crisis analysis.

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
            Historical P2P data
        """

        try:
            profile = get_profile_by_country_code(country_code)
            fiat = profile["fiat"]

            # Convert dates to Wayback format (YYYYMMDD)
            start_wayback = start_date.replace("-", "")
            end_wayback = end_date.replace("-", "")

            print(
                f"🔍 Searching for Paxful historical data: {profile['name']} ({fiat})"
            )
            print(f"📅 Date range: {start_date} to {end_date}")

            # Search for relevant Paxful URLs
            search_urls = [
                f"https://paxful.com/buy-bitcoin/{fiat.lower()}",
                f"https://paxful.com/sell-bitcoin/{fiat.lower()}",
                f"https://paxful.com/rest/v1/offers?currency={fiat}&type=buy",
                f"https://paxful.com/rest/v1/offers?currency={fiat}&type=sell",
            ]

            all_offers = []

            for url in search_urls:
                print(f"🕐 Searching Wayback Machine for: {url}")
                snapshots = self.get_wayback_snapshots(url, start_wayback, end_wayback)

                if snapshots:
                    print(f"📸 Found {len(snapshots)} snapshots")

                    # Sample a few snapshots to avoid overloading
                    sample_snapshots = snapshots[
                        :: max(1, len(snapshots) // 5)
                    ]  # Take every 5th

                    for snapshot in sample_snapshots:
                        offers = self.scrape_archived_offers(snapshot, country_code)
                        all_offers.extend(offers)
                        time.sleep(2)  # Be respectful to Wayback Machine
                else:
                    print("📭 No snapshots found")

            if all_offers:
                # Save historical data
                collection_id = self.csv_manager.generate_collection_id()
                self.csv_manager.save_raw_ads(
                    all_offers, "paxful", country_code, collection_id
                )

                self.csv_manager.log_collection_run(
                    platform="paxful",
                    country_code=country_code,
                    country_name=profile["name"],
                    fiat_currency=fiat,
                    ads_collected=len(all_offers),
                    buy_ads=sum(1 for o in all_offers if o["trade_type"] == "BUY"),
                    sell_ads=sum(1 for o in all_offers if o["trade_type"] == "SELL"),
                    status="success",
                    collection_id=collection_id,
                )

            print(f"✅ Paxful historical collection complete: {len(all_offers)} offers")
            return all_offers

        except ValueError as e:
            print(f"❌ Paxful Error: {e}")
            return []


def main():
    """
    Test the Paxful historical scraper.
    """
    scraper = PaxfulHistoricalScraper()

    print("🧪 Testing Paxful historical scraper...")
    print("⚠️  Note: This scraper relies on archived data and may be slow")

    # Test with Nigeria (Paxful was popular there)
    nigeria_data = scraper.collect_historical_data("NG", "2020-01-01", "2021-12-31")

    if nigeria_data:
        print(f"\n✅ Collected {len(nigeria_data)} historical Paxful offers")
        print("\n📋 Sample historical offer:")
        print(json.dumps(nigeria_data[0], indent=2))
    else:
        print("⚠️  No historical Paxful data found - may need different approach")


if __name__ == "__main__":
    main()
