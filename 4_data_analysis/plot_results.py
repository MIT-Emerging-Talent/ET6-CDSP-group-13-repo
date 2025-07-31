#!/usr/bin/env python3
"""
Crisis Analysis Plotting Script
==============================

Standalone script to generate all visualizations from existing analysis data.
Run this after completing the comprehensive analysis to create plots.

Usage:
    python plot_results.py

Author: Clement MUGISHA
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "3_data_exploration" / "crypto_visualizations"))


def main():
    """Main function to generate all plots."""
    print("🎨 CRISIS ANALYSIS VISUALIZATION GENERATOR")
    print("=" * 50)

    try:
        # Load visualization engine using absolute path
        import importlib.util
        import os

        viz_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "3_data_exploration",
            "crypto_visualizations",
            "crisis_plots.py",
        )
        spec = importlib.util.spec_from_file_location("crisis_plots", viz_path)
        viz_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(viz_module)
        CrisisVisualizationEngine = viz_module.CrisisVisualizationEngine

        # Initialize visualization engine
        print("🚀 Initializing visualization engine...")
        visualizer = CrisisVisualizationEngine()

        # Generate all available plots
        print("📊 Generating comprehensive visualizations...")
        success = visualizer.create_all_plots()

        if success:
            print("\n✅ SUCCESS! All visualizations generated")
            print(f"📁 Plots saved to: {visualizer.output_dir}")
            print("\n📋 Available plots:")
            print("   • Premium Analysis Charts")
            print("   • Historical Correlation Plots")
            print("   • Market Structure Analysis")
            print("   • Comprehensive Dashboard")
            print(
                "\n💡 Tip: Open the plots directory to view all generated visualizations"
            )
        else:
            print("\n❌ FAILED! Some visualizations could not be generated")
            print("💡 Make sure analysis data is available in the data directory")

    except ImportError as e:
        print(f"❌ ERROR: Missing dependencies - {e}")
        print("💡 Install required packages:")
        print("   pip install matplotlib seaborn")
        return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
