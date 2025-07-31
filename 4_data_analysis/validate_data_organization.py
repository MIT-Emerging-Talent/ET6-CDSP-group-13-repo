"""
Data Output Validation Report
============================

This script validates that all analysis outputs are going to the correct folders
according to our organized data structure.

Expected Structure:
data/
├── raw/YYYY-MM-DD/              # P2P trading data by date
├── historical/
│   ├── yahoo_finance/           # Historical crypto prices
│   └── cryptocompare/           # CryptoCompare historical data
├── exchange_rates/              # Currency conversion rates
├── analysis/
│   ├── reports/                 # Analysis summary reports
│   └── crisis_correlations/     # Crisis correlation analysis
├── processed/
│   ├── premium_calculations/    # Premium analysis results
│   ├── daily_summaries/         # Daily aggregated data
│   └── country_aggregates/      # Country-level statistics
└── metadata/                    # Collection logs and metadata

Author: Clement MUGISHA
"""

import os
from pathlib import Path
import pandas as pd
from datetime import datetime


def validate_data_organization():
    """Validate that all data is properly organized in expected folders."""

    print("🔍 DATA ORGANIZATION VALIDATION")
    print("=" * 40)

    base_dir = Path("data")

    # Expected folder structure
    expected_structure = {
        "raw": "P2P trading data organized by collection date",
        "historical/yahoo_finance": "Historical crypto prices (10+ years)",
        "historical/cryptocompare": "CryptoCompare historical data",
        "exchange_rates": "Currency conversion rates",
        "analysis/reports": "Analysis summary reports",
        "analysis/crisis_correlations": "Crisis correlation analysis",
        "processed/premium_calculations": "Premium analysis results",
        "processed/daily_summaries": "Daily aggregated data",
        "processed/country_aggregates": "Country-level statistics",
        "metadata": "Collection logs and metadata",
    }

    print("📁 Checking folder structure...")
    for folder, description in expected_structure.items():
        folder_path = base_dir / folder
        exists = folder_path.exists()
        file_count = len(list(folder_path.glob("*"))) if exists else 0

        status = "✅" if exists else "❌"
        print(f"{status} {folder:<35} | {file_count:>3} files | {description}")

    print("\n📋 SCRIPT OUTPUT VALIDATION")
    print("=" * 40)

    # Validate script outputs
    script_validations = []

    # 1. Premium calculations
    premium_folder = base_dir / "processed/premium_calculations"
    premium_files = (
        list(premium_folder.glob("*.csv")) if premium_folder.exists() else []
    )
    script_validations.append({
        "script": "calculate_premiums.py",
        "expected_folder": "processed/premium_calculations/",
        "files_found": len(premium_files),
        "status": "✅" if premium_files else "⚠️",
    })

    # 2. CryptoCompare historical data
    cc_folder = base_dir / "historical/cryptocompare"
    cc_files = list(cc_folder.glob("*.csv")) if cc_folder.exists() else []
    script_validations.append({
        "script": "cryptocompare_free.py",
        "expected_folder": "historical/cryptocompare/",
        "files_found": len(cc_files),
        "status": "✅" if cc_files else "⚠️",
    })

    # 3. CryptoCompare current prices (should be in analysis/)
    cc_current_files = (
        list((base_dir / "analysis").glob("cryptocompare_prices*.csv"))
        if (base_dir / "analysis").exists()
        else []
    )
    script_validations.append({
        "script": "cryptocompare_free.py (current)",
        "expected_folder": "analysis/",
        "files_found": len(cc_current_files),
        "status": "✅" if cc_current_files else "⚠️",
    })

    # 4. Crisis correlations
    crisis_folder = base_dir / "analysis/crisis_correlations"
    crisis_files = list(crisis_folder.glob("*.csv")) if crisis_folder.exists() else []
    script_validations.append({
        "script": "comprehensive_analyzer.py",
        "expected_folder": "analysis/crisis_correlations/",
        "files_found": len(crisis_files),
        "status": "✅" if crisis_files else "⚠️",
    })

    # 5. Analysis reports
    reports_folder = base_dir / "analysis/reports"
    report_files = list(reports_folder.glob("*")) if reports_folder.exists() else []
    script_validations.append({
        "script": "comprehensive_analyzer.py (reports)",
        "expected_folder": "analysis/reports/",
        "files_found": len(report_files),
        "status": "✅" if report_files else "⚠️",
    })

    # 6. Country aggregates
    country_folder = base_dir / "processed/country_aggregates"
    country_files = (
        list(country_folder.glob("*.csv")) if country_folder.exists() else []
    )
    script_validations.append({
        "script": "comprehensive_analyzer.py (country)",
        "expected_folder": "processed/country_aggregates/",
        "files_found": len(country_files),
        "status": "✅" if country_files else "⚠️",
    })

    # Display validation results
    for validation in script_validations:
        status = validation["status"]
        script = validation["script"]
        folder = validation["expected_folder"]
        count = validation["files_found"]
        print(f"{status} {script:<35} → {folder:<30} ({count} files)")

    print("\n📊 RECOMMENDATIONS")
    print("=" * 20)

    issues_found = []

    # Check for missing outputs
    missing_outputs = [v for v in script_validations if v["status"] == "⚠️"]
    if missing_outputs:
        print("⚠️ Missing outputs detected:")
        for missing in missing_outputs:
            print(
                f"   • {missing['script']} should output to {missing['expected_folder']}"
            )
            issues_found.append(f"Run {missing['script']} to generate missing outputs")

    # Check for historical data utilization
    yahoo_folder = base_dir / "historical/yahoo_finance"
    yahoo_files = list(yahoo_folder.glob("*.csv")) if yahoo_folder.exists() else []
    if yahoo_files and not crisis_files:
        issues_found.append(
            "Historical data available but not used in crisis correlation analysis"
        )

    # Check for exchange rates utilization
    rates_folder = base_dir / "exchange_rates"
    rates_files = list(rates_folder.glob("*.csv")) if rates_folder.exists() else []
    if rates_files and not premium_files:
        issues_found.append("Exchange rates available but premium calculations not run")

    if issues_found:
        print("\n🔧 ACTION ITEMS:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ All data is properly organized and utilized!")

    print(f"\n📅 Validation completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return script_validations, issues_found


if __name__ == "__main__":
    validations, issues = validate_data_organization()
