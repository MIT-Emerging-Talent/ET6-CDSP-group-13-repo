"""
Crisis Visualization Engine - Clean Version
Cryptocurrency Crisis Analysis Plotting Module
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class CrisisVisualizationEngine:
    """Professional visualization engine for cryptocurrency crisis analysis."""

    def __init__(self, output_dir="data/analysis/plots"):
        """Initialize the visualization engine."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set professional style
        plt.style.use("seaborn-v0_8-whitegrid")
        sns.set_palette("husl")

        # Country color mapping for consistency
        self.country_colors = {
            "SD": "#E74C3C",  # Red - High Crisis
            "ZW": "#8E44AD",  # Purple - Severe Crisis
            "VE": "#F39C12",  # Orange - Economic Crisis
            "NG": "#27AE60",  # Green - Oil Crisis
            "AR": "#3498DB",  # Blue - Stable
            "AF": "#E67E22",  # Orange-red - Conflict
        }

    def plot_premium_analysis(self, premium_data, save_path=None):
        """Create comprehensive premium analysis visualization."""
        if save_path is None:
            save_path = self.output_dir / "premium_analysis.png"

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Handle different column names
        premium_col = "premium_avg" if "premium_avg" in premium_data.columns else "premium_pct"

        countries = premium_data["country_code"].tolist()
        premiums = premium_data[premium_col].tolist()
        colors = [self.country_colors.get(c, "#95A5A6") for c in countries]

        # Premium bar chart
        bars = ax1.bar(countries, premiums, color=colors, alpha=0.8, edgecolor="white", linewidth=2)
        ax1.set_title(
            "💰 Cryptocurrency Premiums by Country",
            fontweight="bold",
            fontsize=14,
            pad=20,
        )
        ax1.set_ylabel("Premium (%)", fontweight="bold")
        ax1.grid(True, alpha=0.3)

        # Add value labels
        for bar, premium in zip(bars, premiums):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{premium:+.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=11,
            )

        # Market activity scatter (if available)
        if "total_ads" in premium_data.columns:
            market_sizes = premium_data["total_ads"].tolist()
            ax2.scatter(
                market_sizes,
                premiums,
                c=colors,
                s=200,
                alpha=0.7,
                edgecolors="white",
                linewidths=2,
            )

            for i, country in enumerate(countries):
                ax2.annotate(
                    country,
                    (market_sizes[i], premiums[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontweight="bold",
                )

            ax2.set_xlabel("Market Activity (Number of Ads)", fontweight="bold")
            ax2.set_ylabel("Premium (%)", fontweight="bold")
            ax2.set_title("📊 Market Activity vs Premium", fontweight="bold", fontsize=14, pad=20)
            ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()
        print(f"📊 Premium analysis plot saved: {save_path}")
        return fig

    def plot_historical_correlation(self, correlation_data, save_path=None):
        """Create historical correlation analysis visualization."""
        if save_path is None:
            save_path = self.output_dir / "historical_correlation.png"

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Convert date column
        df = correlation_data.copy()
        df["event_date"] = pd.to_datetime(df["event_date"])

        # Volatility timeline
        colors = [self.country_colors.get(c, "#95A5A6") for c in df["country_code"]]
        ax1.scatter(
            df["event_date"],
            df["BTC_volatility"],
            c=colors,
            s=100,
            alpha=0.7,
            edgecolors="white",
            linewidths=2,
        )
        ax1.set_title(
            "📈 Bitcoin Volatility During Crisis Events",
            fontweight="bold",
            fontsize=14,
            pad=20,
        )
        ax1.set_ylabel("BTC Volatility (%)", fontweight="bold")
        ax1.grid(True, alpha=0.3)

        # Format dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax1.xaxis.set_major_locator(mdates.YearLocator())

        # Country volatility comparison
        country_volatility = (
            df.groupby("country_code")["BTC_volatility"].mean().sort_values(ascending=False)
        )
        bars = ax2.bar(
            country_volatility.index,
            country_volatility.values,
            color=[self.country_colors.get(c, "#95A5A6") for c in country_volatility.index],
            alpha=0.8,
            edgecolor="white",
            linewidth=2,
        )

        ax2.set_title("🌍 Average Volatility by Country", fontweight="bold", fontsize=14, pad=20)
        ax2.set_ylabel("Average BTC Volatility (%)", fontweight="bold")
        ax2.grid(True, alpha=0.3)

        # Add value labels
        for bar, value in zip(bars, country_volatility.values):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=11,
            )

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()
        print(f"📈 Historical correlation plot saved: {save_path}")
        return fig

    def plot_market_structure(self, market_data, save_path=None):
        """Create market structure analysis visualization."""
        if save_path is None:
            save_path = self.output_dir / "market_structure.png"

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        countries = market_data["country_code"].tolist()
        colors = [self.country_colors.get(c, "#95A5A6") for c in countries]

        # Buy vs Sell distribution
        if "buy_ads" in market_data.columns and "sell_ads" in market_data.columns:
            buy_counts = market_data["buy_ads"].tolist()
            sell_counts = market_data["sell_ads"].tolist()

            x = np.arange(len(countries))
            width = 0.35

            ax1.bar(
                x - width / 2,
                buy_counts,
                width,
                label="Buy Orders",
                color="#2ECC71",
                alpha=0.8,
            )
            ax1.bar(
                x + width / 2,
                sell_counts,
                width,
                label="Sell Orders",
                color="#E74C3C",
                alpha=0.8,
            )

            ax1.set_title(
                "🏗️ Buy vs Sell Order Distribution",
                fontweight="bold",
                fontsize=14,
                pad=20,
            )
            ax1.set_ylabel("Number of Advertisements", fontweight="bold")
            ax1.set_xticks(x)
            ax1.set_xticklabels(countries)
            ax1.legend()
            ax1.grid(True, alpha=0.3)

        # Total market size
        total_ads = market_data["total_ads"].tolist()
        bars = ax2.bar(
            countries,
            total_ads,
            color=colors,
            alpha=0.8,
            edgecolor="white",
            linewidth=2,
        )
        ax2.set_title(
            "📊 Total Market Activity by Country",
            fontweight="bold",
            fontsize=14,
            pad=20,
        )
        ax2.set_ylabel("Total Advertisements", fontweight="bold")
        ax2.grid(True, alpha=0.3)

        # Add value labels
        for bar, total in zip(bars, total_ads):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{total}",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=11,
            )

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()
        print(f"🏗️ Market structure plot saved: {save_path}")
        return fig

    def plot_comprehensive_dashboard(
        self, premium_data, correlation_data=None, market_data=None, save_path=None
    ):
        """Create a comprehensive dashboard with improved layout and no text overlap."""
        if save_path is None:
            save_path = self.output_dir / "comprehensive_dashboard.png"

        try:
            # Create clean 2x2 grid layout with better spacing
            fig = plt.figure(figsize=(20, 16))

            # Use GridSpec for better control over spacing
            from matplotlib.gridspec import GridSpec

            gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.2)

            # Main title with proper spacing
            fig.suptitle(
                "🚀 COMPREHENSIVE CRISIS IMPACT ANALYSIS DASHBOARD",
                fontsize=20,
                fontweight="bold",
                y=0.95,
            )

            # Handle premium column names
            premium_col = "premium_avg" if "premium_avg" in premium_data.columns else "premium_pct"
            countries = premium_data["country_code"].tolist()
            premiums = premium_data[premium_col].tolist()
            colors = [self.country_colors.get(c, "#95A5A6") for c in countries]

            # Top Left: Premium Analysis
            ax1 = fig.add_subplot(gs[0, 0])
            bars = ax1.bar(
                countries,
                premiums,
                color=colors,
                alpha=0.8,
                edgecolor="white",
                linewidth=2,
            )
            ax1.set_title("💰 CRYPTOCURRENCY PREMIUMS", fontweight="bold", fontsize=14)
            ax1.set_ylabel("Premium (%)", fontweight="bold")
            ax1.grid(True, alpha=0.3)

            # Clean value labels
            for bar, premium in zip(bars, premiums):
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 1,
                    f"{premium:+.1f}%",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                )

            # Top Right: Market Activity vs Premium (if available)
            ax2 = fig.add_subplot(gs[0, 1])
            if "total_ads" in premium_data.columns:
                market_sizes = premium_data["total_ads"].tolist()
                ax2.scatter(
                    market_sizes,
                    premiums,
                    c=colors,
                    s=150,
                    alpha=0.7,
                    edgecolors="white",
                    linewidths=2,
                )

                # Simple labels without overlap checking for cleaner display
                for i, country in enumerate(countries):
                    ax2.annotate(
                        country,
                        (market_sizes[i], premiums[i]),
                        xytext=(5, 5),
                        textcoords="offset points",
                        fontweight="bold",
                        fontsize=10,
                    )

                ax2.set_xlabel("Market Activity (Ads)", fontweight="bold")
                ax2.set_ylabel("Premium (%)", fontweight="bold")
                ax2.set_title("📊 MARKET ACTIVITY vs PREMIUM", fontweight="bold", fontsize=14)
                ax2.grid(True, alpha=0.3)

            # Bottom Left: Historical Correlation (if available)
            ax3 = fig.add_subplot(gs[1, 0])
            if correlation_data is not None and not correlation_data.empty:
                df = correlation_data.copy()
                df["event_date"] = pd.to_datetime(df["event_date"])
                colors_corr = [self.country_colors.get(c, "#95A5A6") for c in df["country_code"]]

                ax3.scatter(
                    df["event_date"],
                    df["BTC_volatility"],
                    c=colors_corr,
                    s=80,
                    alpha=0.7,
                    edgecolors="white",
                    linewidths=1,
                )
                ax3.set_title("📈 BITCOIN VOLATILITY TIMELINE", fontweight="bold", fontsize=14)
                ax3.set_ylabel("BTC Volatility (%)", fontweight="bold")
                ax3.grid(True, alpha=0.3)

                # Clean date formatting
                ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
                ax3.xaxis.set_major_locator(mdates.YearLocator())

            # Bottom Right: Key Insights Panel
            ax4 = fig.add_subplot(gs[1, 1])
            ax4.axis("off")

            # Generate clean insights text
            insights_text = self._generate_insights_text(
                premium_data, correlation_data, market_data
            )
            ax4.text(
                0.05,
                0.95,
                insights_text,
                transform=ax4.transAxes,
                fontsize=11,
                verticalalignment="top",
                fontfamily="monospace",
                linespacing=1.5,
                bbox=dict(
                    boxstyle="round,pad=0.8",
                    facecolor="#f8f9fa",
                    alpha=0.9,
                    edgecolor="#dee2e6",
                    linewidth=1,
                ),
            )
            ax4.set_title("📊 KEY INSIGHTS", fontweight="bold", fontsize=14, y=0.95)

            # Final layout adjustments
            plt.savefig(
                save_path,
                dpi=300,
                bbox_inches="tight",
                facecolor="white",
                edgecolor="none",
                pad_inches=0.2,
            )
            plt.show()

            print(f"🚀 Comprehensive dashboard saved: {save_path}")
            return fig

        except Exception as e:
            print(f"❌ Error creating comprehensive dashboard: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _generate_insights_text(self, premium_data, correlation_data, market_data):
        """Generate clean insights text for the dashboard."""
        insights = []

        # Premium analysis insights
        if not premium_data.empty:
            premium_col = "premium_avg" if "premium_avg" in premium_data.columns else "premium_pct"

            max_premium = premium_data.loc[premium_data[premium_col].idxmax()]
            min_premium = premium_data.loc[premium_data[premium_col].idxmin()]
            avg_premium = premium_data[premium_col].mean()

            insights.append("🔥 PREMIUM ANALYSIS")
            insights.append("─" * 20)
            insights.append(
                f"Highest: {max_premium['country_code']} ({max_premium[premium_col]:+.1f}%)"
            )
            insights.append(
                f"Lowest:  {min_premium['country_code']} ({min_premium[premium_col]:+.1f}%)"
            )
            insights.append(f"Average: {avg_premium:+.1f}%")
            insights.append("")

        # Market structure insights
        if market_data is not None and not market_data.empty:
            total_market = market_data["total_ads"].sum()
            largest_market = market_data.loc[market_data["total_ads"].idxmax()]

            insights.append("📊 MARKET OVERVIEW")
            insights.append("─" * 20)
            insights.append(f"Total Activity: {total_market} ads")
            insights.append(f"Largest Market: {largest_market['country_code']}")
            insights.append(f"Countries: {len(market_data)}")
            insights.append("")

        # Crisis correlation insights
        if correlation_data is not None and not correlation_data.empty:
            max_volatility = correlation_data.loc[correlation_data["BTC_volatility"].idxmax()]
            avg_volatility = correlation_data["BTC_volatility"].mean()

            insights.append("📈 CRISIS CORRELATION")
            insights.append("─" * 20)
            insights.append(f"Max Volatility: {max_volatility['country_code']}")
            insights.append(f"Average Vol: {avg_volatility:.1f}%")
            insights.append(f"Events: {len(correlation_data)}")
            insights.append("")

        # Key recommendations
        insights.append("💡 RECOMMENDATIONS")
        insights.append("─" * 20)
        insights.append("• Monitor high-premium markets")
        insights.append("• Track volatility patterns")
        insights.append("• Analyze market pressure")
        insights.append("• Update crisis timeline")

        return "\n".join(insights)

    def create_all_plots(self, data_dir="data"):
        """Generate all available plots from data directory."""
        data_path = Path(data_dir)
        plots_created = []

        print("🎨 GENERATING COMPREHENSIVE VISUALIZATION SUITE")
        print("=" * 50)

        try:
            # Load premium data
            premium_files = list((data_path / "analysis/reports").glob("premium_summary_*.csv"))
            if premium_files:
                latest_premium = max(premium_files, key=lambda x: x.stat().st_mtime)
                premium_data = pd.read_csv(latest_premium)

                self.plot_premium_analysis(premium_data)
                plots_created.append("Premium Analysis")
                print("✅ Premium analysis plots created")

            # Load correlation data
            correlation_files = list(
                (data_path / "analysis/crisis_correlations").glob("historical_correlation_*.csv")
            )
            if correlation_files:
                latest_correlation = max(correlation_files, key=lambda x: x.stat().st_mtime)
                correlation_data = pd.read_csv(latest_correlation)

                self.plot_historical_correlation(correlation_data)
                plots_created.append("Historical Correlation")
                print("✅ Historical correlation plots created")
            else:
                correlation_data = pd.DataFrame()

            # Load market structure data
            market_files = list(
                (data_path / "processed/country_aggregates").glob("market_structure_*.csv")
            )
            if market_files:
                latest_market = max(market_files, key=lambda x: x.stat().st_mtime)
                market_data = pd.read_csv(latest_market)

                self.plot_market_structure(market_data)
                plots_created.append("Market Structure")
                print("✅ Market structure plots created")
            else:
                market_data = pd.DataFrame()

            # Create comprehensive dashboard
            if not premium_data.empty:
                self.plot_comprehensive_dashboard(premium_data, correlation_data, market_data)
                plots_created.append("Comprehensive Dashboard")
                print("✅ Comprehensive dashboard created")

            print("\n🎯 VISUALIZATION COMPLETE!")
            print(f"📁 Plots saved to: {self.output_dir}")
            print(f"📊 Total plots created: {len(plots_created)}")
            for plot in plots_created:
                print(f"   • {plot}")

        except Exception as e:
            print(f"❌ Error creating plots: {e}")
            return False

        return True


def main():
    """Main function to generate all plots."""
    print("🚀 CRISIS IMPACT VISUALIZATION ENGINE")
    print("=" * 40)

    # Initialize visualization engine
    visualizer = CrisisVisualizationEngine()

    # Generate all available plots
    success = visualizer.create_all_plots()

    if success:
        print("\n✅ All visualizations generated successfully!")
        print(f"📁 Check the plots directory: {visualizer.output_dir}")
    else:
        print("\n❌ Some visualizations failed to generate")
        print("Please ensure analysis data is available in the data directory")


if __name__ == "__main__":
    main()
