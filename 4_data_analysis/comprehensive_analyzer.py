"""
Comprehensive Crisis Impact Analysis Coordinator
===============================================

This script coordinates all analysis components to extract insights from:
1. P2P trading data (513 ads)
2. Historical cryptocurrency prices (10+ years)
3. Exchange rates for premium calculations
4. Crisis timeline correlations

Outputs are organized into proper folder structure:
- ../1_datasets/processed/premium_calculations/
- ../1_datasets/processed/daily_summaries/
- ../1_datasets/processed/country_aggregates/
- results/reports/
- results/crisis_correlations/

Author: Clement MUGISHA
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Direct imports from local modules
try:
    from calculate_premiums import calculate_premiums
except ImportError as e:
    print(f"⚠️ Could not import calculate_premiums: {e}")
    calculate_premiums = None

try:
    from crypto_analysis.analysis.crisis_timeline import CrisisTimelineManager
except ImportError as e:
    print(f"⚠️ Could not import CrisisTimelineManager: {e}")
    CrisisTimelineManager = None

# Import data management utilities directly from files
CSVDataManager = None
ExchangeRateCollector = None

try:
    # Import CSV data manager from the actual file location
    project_root = Path(__file__).parent.parent
    csv_manager_path = project_root / "1_datasets" / "crypto_data_collectors" / "utils" / "csv_data_manager.py"
    exchange_rates_path = project_root / "1_datasets" / "crypto_data_collectors" / "utils" / "exchange_rates.py"
    
    if csv_manager_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("csv_data_manager", csv_manager_path)
        csv_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(csv_module)
        CSVDataManager = csv_module.CSVDataManager
        print("✅ CSVDataManager loaded successfully")
    else:
        print(f"❌ CSV manager file not found: {csv_manager_path}")

    if exchange_rates_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("exchange_rates", exchange_rates_path)
        exchange_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exchange_module)
        ExchangeRateCollector = exchange_module.ExchangeRateCollector
        print("✅ ExchangeRateCollector loaded successfully")
    else:
        print(f"❌ Exchange rates file not found: {exchange_rates_path}")

except Exception as e:
    print(f"⚠️ Could not load data management modules: {e}")

# Import visualization module
PLOTTING_AVAILABLE = False
try:
    viz_path = project_root / "3_data_exploration" / "crypto_visualizations" / "visualization" / "crisis_plots.py"
    if viz_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("crisis_plots", viz_path)
        viz_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(viz_module)
        CrisisVisualizationEngine = viz_module.CrisisVisualizationEngine
        PLOTTING_AVAILABLE = True
        print("✅ CrisisVisualizationEngine loaded successfully")
    else:
        print(f"❌ Visualization file not found: {viz_path}")
except Exception as e:
    print(f"⚠️ Plotting functionality not available: {e}")


class CrisisImpactAnalyzer:
    """Comprehensive analysis coordinator using all collected data."""

    def __init__(self):
        if CSVDataManager is None or ExchangeRateCollector is None:
            print("⚠️ Required modules not available. Check import paths.")
            return
        
        self.csv_manager = CSVDataManager()
        self.rate_collector = ExchangeRateCollector()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set up paths relative to repository structure
        self.project_root = Path(__file__).parent.parent
        self.data_root = self.project_root / "1_datasets"
        self.results_root = Path(__file__).parent / "results"
        self.viz_root = self.project_root / "3_data_exploration" / "crypto_visualizations" / "generated_plots"

        # Ensure all output directories exist
        self.setup_directories()

    def setup_directories(self):
        """Create all necessary output directories."""
        directories = [
            self.data_root / "processed" / "premium_calculations",
            self.data_root / "processed" / "daily_summaries", 
            self.data_root / "processed" / "country_aggregates",
            self.results_root / "reports",
            self.results_root / "crisis_correlations",
            self.viz_root,
        ]

        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

        print("📁 Output directories prepared")

    def analyze_market_structure(self):
        """Analyze P2P market structure by country."""
        print("\n🏗️ ANALYZING MARKET STRUCTURE")
        print("=" * 40)

        # Load P2P data
        p2p_data = self.csv_manager.load_raw_ads()
        if p2p_data.empty:
            print("❌ No P2P data available")
            return None

        # Country-level aggregates
        country_stats = []

        for country in p2p_data["country_code"].unique():
            country_data = p2p_data[p2p_data["country_code"] == country]
            
            if len(country_data) == 0:
                continue  # Skip empty country data

            stats = {
                "country_code": country,
                "fiat_currency": country_data["fiat"].iloc[0] if not country_data["fiat"].empty else "Unknown",
                "total_ads": len(country_data),
                "buy_ads": len(country_data[country_data["trade_type"] == "BUY"]),
                "sell_ads": len(country_data[country_data["trade_type"] == "SELL"]),
                "avg_price": country_data["price"].mean(),
                "median_price": country_data["price"].median(),
                "price_std": country_data["price"].std(),
                "min_price": country_data["price"].min(),
                "max_price": country_data["price"].max(),
                "avg_amount": country_data["available_amount"].mean(),
                "total_volume": country_data["available_amount"].sum(),
                "unique_traders": country_data["advertiser_name"].nunique(),
                "analysis_timestamp": self.timestamp,
            }

            # Market pattern analysis
            sell_ratio = (
                stats["sell_ads"] / stats["total_ads"] if stats["total_ads"] > 0 else 0
            )
            if sell_ratio > 0.8:
                stats["market_pattern"] = "heavy_sell_pressure"
                stats["crisis_indicator"] = "high"
            elif sell_ratio > 0.6:
                stats["market_pattern"] = "moderate_sell_pressure"
                stats["crisis_indicator"] = "medium"
            elif sell_ratio < 0.3:
                stats["market_pattern"] = "buy_pressure"
                stats["crisis_indicator"] = "low"
            else:
                stats["market_pattern"] = "balanced"
                stats["crisis_indicator"] = "low"

            country_stats.append(stats)

            print(f"🌍 {country}: {stats['total_ads']} ads, {stats['market_pattern']}")

        # Save country aggregates
        country_df = pd.DataFrame(country_stats)
        output_file = (
            self.data_root / "processed" / "country_aggregates"
            / f"market_structure_{self.timestamp}.csv"
        )
        country_df.to_csv(output_file, index=False)
        print(f"💾 Country aggregates saved: {output_file}")

        return country_df

    def correlate_with_historical_data(self):
        """Correlate current P2P patterns with historical crypto price movements."""
        print("\n📈 HISTORICAL CORRELATION ANALYSIS")
        print("=" * 40)

        # Load historical price data
        historical_files = {
            "BTC": self.results_root / "historical" / "yahoo_finance" / "BTC_USD_historical.csv",
            "ETH": self.results_root / "historical" / "yahoo_finance" / "ETH_USD_historical.csv", 
            "USDT": self.results_root / "historical" / "yahoo_finance" / "USDT_USD_historical.csv",
        }

        historical_data = {}
        for crypto, file_path in historical_files.items():
            if Path(file_path).exists():
                df = pd.read_csv(file_path)
                df["Date"] = pd.to_datetime(df["Date"])
                historical_data[crypto] = df
                print(f"📊 Loaded {len(df)} days of {crypto} data")
            else:
                print(f"⚠️ Historical data not found: {file_path}")

        if not historical_data:
            print("❌ No historical data available")
            return None

        # Get crisis events for correlation
        if CrisisTimelineManager is None:
            print("⚠️ CrisisTimelineManager not available")
            return None
            
        timeline_manager = CrisisTimelineManager()
        crisis_events = timeline_manager.crisis_events
        correlations = []

        for event in crisis_events:
            event_date = pd.to_datetime(event.date, utc=True)

            # Analysis window: 30 days before and after crisis
            start_date = event_date - timedelta(days=30)
            end_date = event_date + timedelta(days=30)

            event_analysis = {
                "country_code": event.country_code,
                "event_date": event.date,
                "event_type": event.event_type,
                "event_title": event.title,
                "impact_severity": event.impact_severity,
            }

            # Analyze price movements for each crypto
            for crypto, data in historical_data.items():
                # Ensure timezone compatibility
                data_tz_aware = data.copy()
                data_tz_aware["Date"] = pd.to_datetime(data_tz_aware["Date"], utc=True)

                period_data = data_tz_aware[
                    (data_tz_aware["Date"] >= start_date)
                    & (data_tz_aware["Date"] <= end_date)
                ]

                if len(period_data) > 0:
                    # Calculate volatility and price change
                    pre_crisis = period_data[period_data["Date"] < event_date]["Close"]
                    post_crisis = period_data[period_data["Date"] >= event_date][
                        "Close"
                    ]

                    if len(pre_crisis) > 0 and len(post_crisis) > 0:
                        price_change = (
                            (post_crisis.iloc[0] - pre_crisis.iloc[-1])
                            / pre_crisis.iloc[-1]
                        ) * 100
                        volatility = (
                            period_data["Close"].std()
                            / period_data["Close"].mean()
                            * 100
                        )

                        event_analysis[f"{crypto}_price_change_pct"] = price_change
                        event_analysis[f"{crypto}_volatility"] = volatility
                    else:
                        event_analysis[f"{crypto}_price_change_pct"] = None
                        event_analysis[f"{crypto}_volatility"] = None

            correlations.append(event_analysis)
            print(f"📅 Analyzed: {event.date} - {event.title}")

        # Save correlation analysis
        correlation_df = pd.DataFrame(correlations)
        output_file = (
            self.results_root / "analysis" / "crisis_correlations"
            / f"historical_correlation_{self.timestamp}.csv"
        )
        correlation_df.to_csv(output_file, index=False)
        print(f"💾 Correlation analysis saved: {output_file}")

        return correlation_df

    def generate_comprehensive_report(
        self, premium_data=None, market_data=None, correlation_data=None
    ):
        """Generate comprehensive insights report."""
        print("\n📋 GENERATING COMPREHENSIVE REPORT")
        print("=" * 40)

        report = {
            "analysis_timestamp": self.timestamp,
            "data_sources": {
                "p2p_ads_analyzed": 0,
                "countries_covered": 0,
                "historical_data_span": "10+ years",
                "crisis_events_analyzed": 0,
            },
            "key_findings": {},
            "crisis_indicators": {},
            "recommendations": [],
        }

        # Premium analysis insights
        if premium_data is not None and not premium_data.empty:
            report["data_sources"]["countries_covered"] = len(premium_data)
            report["data_sources"]["p2p_ads_analyzed"] = premium_data["total_ads"].sum()

            # Key premium findings
            max_premium = premium_data.loc[premium_data["premium_avg"].idxmax()]
            min_premium = premium_data.loc[premium_data["premium_avg"].idxmin()]

            report["key_findings"]["highest_premium"] = {
                "country": max_premium["country_code"],
                "premium_pct": max_premium["premium_avg"],
                "interpretation": "Crisis-driven currency flight"
                if max_premium["premium_avg"] > 100
                else "Moderate premium",
            }

            report["key_findings"]["lowest_premium"] = {
                "country": min_premium["country_code"],
                "premium_pct": min_premium["premium_avg"],
                "interpretation": "Stable market conditions"
                if min_premium["premium_avg"] < 10
                else "Normal trading",
            }

        # Market structure insights
        if market_data is not None and not market_data.empty:
            crisis_countries = market_data[market_data["crisis_indicator"] == "high"]
            if len(crisis_countries) > 0:
                report["crisis_indicators"]["high_risk_countries"] = crisis_countries[
                    "country_code"
                ].tolist()
                report["crisis_indicators"]["market_patterns"] = (
                    crisis_countries.set_index("country_code")[
                        "market_pattern"
                    ].to_dict()
                )

        # Historical correlation insights
        if correlation_data is not None and not correlation_data.empty:
            report["data_sources"]["crisis_events_analyzed"] = len(correlation_data)

            # Find most volatile events
            if "BTC_volatility" in correlation_data.columns:
                high_volatility = correlation_data.nlargest(3, "BTC_volatility")
                report["key_findings"]["high_volatility_events"] = [
                    {
                        "date": row["event_date"],
                        "country": row["country_code"],
                        "event": row["event_title"],
                        "btc_volatility": row["BTC_volatility"],
                    }
                    for _, row in high_volatility.iterrows()
                ]

        # Generate recommendations
        if premium_data is not None:
            high_premium_countries = premium_data[premium_data["premium_avg"] > 50]
            if len(high_premium_countries) > 0:
                report["recommendations"].append(
                    f"Monitor {', '.join(high_premium_countries['country_code'])} for ongoing crisis impact"
                )

        if market_data is not None:
            unbalanced_markets = market_data[
                market_data["market_pattern"] != "balanced"
            ]
            if len(unbalanced_markets) > 0:
                report["recommendations"].append(
                    "Heavy sell pressure indicates potential capital flight in crisis-affected regions"
                )

        # Save comprehensive report
        report_file = (
            self.results_root / "analysis" / "reports"
            / f"comprehensive_analysis_{self.timestamp}.json"
        )

        # Convert numpy types to Python native types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif hasattr(obj, "item"):  # numpy scalar
                return obj.item()
            elif hasattr(obj, "tolist"):  # numpy array
                return obj.tolist()
            else:
                return obj

        report = convert_numpy_types(report)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"💾 Comprehensive report saved: {report_file}")

        # Display key insights
        print("\n🎯 KEY INSIGHTS")
        print("=" * 20)

        if "highest_premium" in report["key_findings"]:
            hp = report["key_findings"]["highest_premium"]
            print(
                f"🔥 Highest premium: {hp['country']} ({hp['premium_pct']:+.1f}%) - {hp['interpretation']}"
            )

        if "high_risk_countries" in report["crisis_indicators"]:
            countries = ", ".join(report["crisis_indicators"]["high_risk_countries"])
            print(f"⚠️ Crisis indicators: {countries}")

        if report["recommendations"]:
            print("💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")

        return report

    def generate_visualizations(self):
        """Generate comprehensive visualizations from analysis results."""
        if not PLOTTING_AVAILABLE:
            print(
                "⚠️ Plotting functionality not available. Install matplotlib and seaborn."
            )
            return False

        print("\n🎨 GENERATING VISUALIZATIONS")
        print("=" * 40)

        try:
            visualizer = CrisisVisualizationEngine()
            success = visualizer.create_all_plots()

            if success:
                print("✅ All visualizations generated successfully!")
                return True
            else:
                print("❌ Some visualizations failed to generate")
                return False

        except Exception as e:
            print(f"❌ Error generating visualizations: {e}")
            return False

    def run_full_analysis(self, include_plots=True):
        """Execute complete analysis pipeline."""
        print("🚀 COMPREHENSIVE CRISIS IMPACT ANALYSIS")
        print("=" * 50)
        print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. Calculate premiums (uses exchange rates)
        print("\n1️⃣ CALCULATING PREMIUMS...")
        if calculate_premiums is None:
            print("⚠️ calculate_premiums function not available")
            premium_results = None
        else:
            premium_results = calculate_premiums()

        # 2. Analyze market structure
        print("\n2️⃣ ANALYZING MARKET STRUCTURE...")
        market_results = self.analyze_market_structure()

        # 3. Historical correlation analysis
        print("\n3️⃣ CORRELATING WITH HISTORICAL DATA...")
        correlation_results = self.correlate_with_historical_data()

        # 4. Generate comprehensive insights report
        print("\n4️⃣ GENERATING INSIGHTS REPORT...")
        final_report = self.generate_comprehensive_report(
            premium_results, market_results, correlation_results
        )

        # 5. Generate visualizations (optional)
        if include_plots:
            print("\n5️⃣ GENERATING VISUALIZATIONS...")
            plot_success = self.generate_visualizations()
            if plot_success:
                print("✅ Visualizations generated successfully!")
            else:
                print("⚠️ Visualizations skipped or failed")

        print("\n✅ ANALYSIS COMPLETE!")
        print("📁 All outputs saved to:")
        print(f"   • Data: {self.data_root / 'processed'}")
        print(f"   • Analysis: {self.results_root / 'analysis'}")
        print(f"   • Visualizations: {self.viz_root}")
        print(f"🕒 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return {
            "premium_data": premium_results,
            "market_data": market_results,
            "correlation_data": correlation_results,
            "comprehensive_report": final_report,
            "plots_generated": include_plots
            and "plot_success" in locals()
            and plot_success,
        }


if __name__ == "__main__":
    analyzer = CrisisImpactAnalyzer()
    results = analyzer.run_full_analysis()
