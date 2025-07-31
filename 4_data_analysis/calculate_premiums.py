"""
Premium Calculator for Current Data
===================================

Calculate cryptocurrency premiums vs official exchange rates
to demonstrate the immediate impact we can measure.

Author: Clement MUGISHA
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Direct imports from utility files
CSVDataManager = None
ExchangeRateCollector = None

try:
    # Import data management utilities directly from files
    project_root = Path(__file__).parent.parent
    csv_manager_path = (
        project_root
        / "1_datasets"
        / "crypto_data_collectors"
        / "utils"
        / "csv_data_manager.py"
    )
    exchange_rates_path = (
        project_root
        / "1_datasets"
        / "crypto_data_collectors"
        / "utils"
        / "exchange_rates.py"
    )

    if csv_manager_path.exists():
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "csv_data_manager", csv_manager_path
        )
        csv_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(csv_module)
        CSVDataManager = csv_module.CSVDataManager

    if exchange_rates_path.exists():
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "exchange_rates", exchange_rates_path
        )
        exchange_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exchange_module)
        ExchangeRateCollector = exchange_module.ExchangeRateCollector

except Exception as e:
    print(f"⚠️ Could not load required modules: {e}")


def calculate_premiums():
    """Calculate premiums for all collected data and save to proper folders."""

    if CSVDataManager is None or ExchangeRateCollector is None:
        print("❌ Required modules not available")
        return

    print("💰 CRYPTOCURRENCY PREMIUM ANALYSIS")
    print("=" * 50)

    csv_manager = CSVDataManager()
    rate_collector = ExchangeRateCollector()

    # Set up paths relative to repository structure
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "1_datasets" / "processed" / "premium_calculations"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all P2P data
    all_data = csv_manager.load_raw_ads()

    if all_data.empty:
        print("❌ No P2P data found")
        return

    # Load current exchange rates - update path to match repository structure
    rates_file = (
        project_root
        / "1_datasets"
        / "raw_datasets"
        / "exchange_rates"
        / "rates_2025-07-30.csv"
    )
    if not rates_file.exists():
        # Try alternative location
        rates_file = (
            project_root
            / "1_datasets"
            / "crypto_data_collectors"
            / "data"
            / "exchange_rates"
            / "rates_2025-07-30.csv"
        )
        if not rates_file.exists():
            print(f"❌ Exchange rates file not found. Tried: {rates_file}")
            return

    rates_data = pd.read_csv(rates_file)
    rates_dict = dict(zip(rates_data["fiat_currency"], rates_data["usd_rate"]))

    print(f"📊 Analyzing {len(all_data)} P2P advertisements")
    print(f"💱 Official rates available for: {list(rates_dict.keys())}")

    # Calculate premiums by country
    results = []

    for country_code in all_data["country_code"].unique():
        country_data = all_data[all_data["country_code"] == country_code]
        fiat = country_data["fiat"].iloc[0]

        if fiat not in rates_dict:
            print(f"⚠️  No exchange rate for {country_code} ({fiat})")
            continue

        official_rate = rates_dict[fiat]

        # Calculate average prices
        avg_price = country_data["price"].mean()
        median_price = country_data["price"].median()

        # Calculate premiums (assuming USDT = $1)
        premium_avg = rate_collector.calculate_premium(avg_price, official_rate, 1.0)
        premium_median = rate_collector.calculate_premium(
            median_price, official_rate, 1.0
        )

        # Market structure
        total_ads = len(country_data)
        buy_ads = len(country_data[country_data["trade_type"] == "BUY"])
        sell_ads = len(country_data[country_data["trade_type"] == "SELL"])

        result = {
            "country_code": country_code,
            "fiat": fiat,
            "total_ads": total_ads,
            "buy_ads": buy_ads,
            "sell_ads": sell_ads,
            "avg_price": avg_price,
            "median_price": median_price,
            "official_rate": official_rate,
            "premium_avg": premium_avg,
            "premium_median": premium_median,
        }
        results.append(result)

        print(f"\n🌍 {country_code} ({fiat}):")
        print(f"  📊 Market: {total_ads} ads ({buy_ads} buy, {sell_ads} sell)")
        print(f"  💰 Avg Price: {avg_price:,.2f} {fiat}")
        print(f"  💱 Official Rate: {official_rate:,.2f} {fiat}/USD")
        print(
            f"  🔥 Premium: {premium_avg:+.1f}% (avg), {premium_median:+.1f}% (median)"
        )

        # Market interpretation
        if sell_ads > buy_ads * 3:
            print(f"  📈 Market: Heavy sell pressure (people exiting {fiat})")
        elif buy_ads > sell_ads * 3:
            print(f"  📉 Market: Heavy buy pressure (people acquiring {fiat})")
        else:
            print("  ⚖️  Market: Balanced trading")

    # Summary
    print("\n🎯 IMPACT SUMMARY")
    print("=" * 30)

    if results:
        avg_premium = sum(r["premium_avg"] for r in results) / len(results)
        max_premium_country = max(results, key=lambda x: x["premium_avg"])
        min_premium_country = min(results, key=lambda x: x["premium_avg"])

        print(f"📊 Average premium across all countries: {avg_premium:+.1f}%")
        print(
            f"🔥 Highest premium: {max_premium_country['country_code']} ({max_premium_country['premium_avg']:+.1f}%)"
        )
        print(
            f"🔥 Lowest premium: {min_premium_country['country_code']} ({min_premium_country['premium_avg']:+.1f}%)"
        )

        total_ads = sum(r["total_ads"] for r in results)
        print(f"📈 Total market activity: {total_ads} advertisements")
        print(f"🌍 Countries with active P2P markets: {len(results)}/6")

        # Save detailed results to CSV
        results_df = pd.DataFrame(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save to premium calculations folder
        premium_file = output_dir / f"premium_analysis_{timestamp}.csv"
        results_df.to_csv(premium_file, index=False)
        print(f"\n💾 Detailed results saved: {premium_file}")

        # Save to analysis folder for reporting
        analysis_dir = Path("data/analysis/reports")
        analysis_dir.mkdir(parents=True, exist_ok=True)
        summary_file = analysis_dir / f"premium_summary_{timestamp}.csv"
        results_df.to_csv(summary_file, index=False)
        print(f"📊 Summary report saved: {summary_file}")

        # Return results for further analysis
        return results_df

    return None


if __name__ == "__main__":
    calculate_premiums()
