"""
Crisis Event Timeline Definition
===============================

Defines key crisis events for each target country that likely impacted
cryptocurrency adoption and P2P market dynamics.

This module serves as the foundation for crisis impact analysis by providing:
- Structured crisis event data
- Severity scoring for events
- Timeline coordination for data collection
- Event type categorization for analysis

Event Types:
- coup: Military coups and government overthrows
- sanctions: International economic sanctions
- currency_crisis: Severe devaluation or inflation
- banking_crisis: Bank closures or restrictions
- political_crisis: Major political instability
- policy_change: Crypto-related policy changes

Author: Clement MUGISHA
License: MIT
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root / "1_datasets" / "crypto_data_collectors"))

try:
    from crypto_data_collectors.utils.csv_data_manager import CSVDataManager
except ImportError:
    CSVDataManager = None


@dataclass
class CrisisEvent:
    """
    Represents a crisis event that may have impacted crypto adoption.
    """

    date: str  # YYYY-MM-DD format
    country_code: str  # ISO country code
    event_type: str  # Type of crisis event
    title: str  # Short event title
    description: str  # Detailed description
    impact_severity: int  # 1-5 scale (5 = most severe)
    expected_crypto_impact: str  # 'increase', 'decrease', 'mixed', 'unknown'
    data_collection_priority: int  # 1-5 priority for data collection
    sources: List[str]  # Reference sources


class CrisisTimelineManager:
    """
    Manages crisis event timelines for impact analysis.
    """

    def __init__(self):
        self.csv_manager = CSVDataManager()
        self.crisis_events = self._define_crisis_events()

    def _define_crisis_events(self) -> List[CrisisEvent]:
        """
        Define all crisis events for analysis.

        Returns:
        --------
        list
            Comprehensive list of crisis events
        """

        events = []

        # SUDAN - Conflict and Political Instability
        events.extend(
            [
                CrisisEvent(
                    date="2019-04-11",
                    country_code="SD",
                    event_type="coup",
                    title="Omar al-Bashir Overthrown",
                    description="30-year dictator overthrown by military, economic sanctions remain",
                    impact_severity=4,
                    expected_crypto_impact="increase",
                    data_collection_priority=4,
                    sources=["BBC", "Reuters", "Al Jazeera"],
                ),
                CrisisEvent(
                    date="2019-06-03",
                    country_code="SD",
                    event_type="political_crisis",
                    title="Khartoum Massacre",
                    description="Military attacks protesters, internet cut, banking disrupted",
                    impact_severity=5,
                    expected_crypto_impact="increase",
                    data_collection_priority=5,
                    sources=["Human Rights Watch", "BBC"],
                ),
                CrisisEvent(
                    date="2021-10-25",
                    country_code="SD",
                    event_type="coup",
                    title="Military Coup",
                    description="Military dissolves civilian government, banks closed, internet cut",
                    impact_severity=5,
                    expected_crypto_impact="increase",
                    data_collection_priority=5,
                    sources=["Reuters", "BBC", "Al Jazeera"],
                ),
                CrisisEvent(
                    date="2023-04-15",
                    country_code="SD",
                    event_type="civil_war",
                    title="RSF-SAF Conflict Begins",
                    description="Rapid Support Forces clash with army, banking system collapses",
                    impact_severity=5,
                    expected_crypto_impact="increase",
                    data_collection_priority=5,
                    sources=["UN News", "Reuters", "BBC"],
                ),
            ]
        )

        # AFGHANISTAN - Taliban Takeover and Sanctions
        events.extend(
            [
                CrisisEvent(
                    date="2021-08-15",
                    country_code="AF",
                    event_type="regime_change",
                    title="Taliban Takeover",
                    description="Taliban captures Kabul, government collapses, mass exodus",
                    impact_severity=5,
                    expected_crypto_impact="increase",
                    data_collection_priority=5,
                    sources=["BBC", "Reuters", "CNN"],
                ),
                CrisisEvent(
                    date="2021-08-17",
                    country_code="AF",
                    event_type="sanctions",
                    title="Assets Frozen",
                    description="US freezes $9.5B in Afghan central bank assets",
                    impact_severity=5,
                    expected_crypto_impact="increase",
                    data_collection_priority=5,
                    sources=["Wall Street Journal", "Reuters"],
                ),
                CrisisEvent(
                    date="2021-12-22",
                    country_code="AF",
                    event_type="banking_crisis",
                    title="Banking System Collapse",
                    description="Banks limit withdrawals, cash shortage, humanitarian crisis",
                    impact_severity=5,
                    expected_crypto_impact="increase",
                    data_collection_priority=4,
                    sources=["UN News", "Reuters"],
                ),
            ]
        )

        # VENEZUELA - Hyperinflation and Political Crisis
        events.extend(
            [
                CrisisEvent(
                    date="2019-01-23",
                    country_code="VE",
                    event_type="political_crisis",
                    title="Guaidó Declares Presidency",
                    description="Opposition leader declares himself president, international recognition",
                    impact_severity=4,
                    expected_crypto_impact="increase",
                    data_collection_priority=4,
                    sources=["Reuters", "BBC", "CNN"],
                ),
                CrisisEvent(
                    date="2019-03-07",
                    country_code="VE",
                    event_type="infrastructure_crisis",
                    title="Nationwide Blackout",
                    description="Massive power outage affects 70% of country for days",
                    impact_severity=4,
                    expected_crypto_impact="increase",
                    data_collection_priority=3,
                    sources=["Reuters", "BBC"],
                ),
                CrisisEvent(
                    date="2020-03-26",
                    country_code="VE",
                    event_type="sanctions",
                    title="US Sanctions Intensify",
                    description="Enhanced sanctions target Venezuelan oil industry",
                    impact_severity=4,
                    expected_crypto_impact="increase",
                    data_collection_priority=3,
                    sources=["US Treasury", "Reuters"],
                ),
                CrisisEvent(
                    date="2021-10-01",
                    country_code="VE",
                    event_type="currency_crisis",
                    title="Bolívar Redenomination",
                    description="Venezuela removes 6 zeros from currency due to inflation",
                    impact_severity=3,
                    expected_crypto_impact="increase",
                    data_collection_priority=3,
                    sources=["Reuters", "Bloomberg"],
                ),
            ]
        )

        # NIGERIA - Crypto Bans and Currency Issues
        events.extend(
            [
                CrisisEvent(
                    date="2021-02-05",
                    country_code="NG",
                    event_type="policy_change",
                    title="Central Bank Crypto Ban",
                    description="CBN prohibits banks from facilitating crypto transactions",
                    impact_severity=5,
                    expected_crypto_impact="increase",
                    data_collection_priority=5,
                    sources=["CBN", "Reuters", "BBC"],
                ),
                CrisisEvent(
                    date="2021-10-20",
                    country_code="NG",
                    event_type="political_crisis",
                    title="EndSARS Anniversary",
                    description="Protests anniversary, youth turn to crypto for financial freedom",
                    impact_severity=3,
                    expected_crypto_impact="increase",
                    data_collection_priority=3,
                    sources=["BBC", "Al Jazeera"],
                ),
                CrisisEvent(
                    date="2023-02-01",
                    country_code="NG",
                    event_type="currency_crisis",
                    title="Naira Scarcity Crisis",
                    description="Cash shortages due to new banknote rollout, people turn to digital alternatives",
                    impact_severity=4,
                    expected_crypto_impact="increase",
                    data_collection_priority=4,
                    sources=["Reuters", "Bloomberg", "Punch Nigeria"],
                ),
            ]
        )

        # ZIMBABWE - Recurring Inflation Crises
        events.extend(
            [
                CrisisEvent(
                    date="2019-06-01",
                    country_code="ZW",
                    event_type="currency_crisis",
                    title="USD Usage Banned",
                    description="Government bans USD, enforces RTGS dollar usage",
                    impact_severity=4,
                    expected_crypto_impact="increase",
                    data_collection_priority=3,
                    sources=["Reuters", "Herald Zimbabwe"],
                ),
                CrisisEvent(
                    date="2020-03-01",
                    country_code="ZW",
                    event_type="currency_crisis",
                    title="Inflation Reaches 800%",
                    description="Hyperinflation returns, currency rapidly loses value",
                    impact_severity=5,
                    expected_crypto_impact="increase",
                    data_collection_priority=4,
                    sources=["Reuters", "Bloomberg", "ZIMSTAT"],
                ),
                CrisisEvent(
                    date="2020-03-30",
                    country_code="ZW",
                    event_type="infrastructure_crisis",
                    title="COVID-19 Lockdown",
                    description="Strict lockdown measures, informal economy disrupted",
                    impact_severity=3,
                    expected_crypto_impact="mixed",
                    data_collection_priority=2,
                    sources=["WHO", "Reuters"],
                ),
            ]
        )

        # ARGENTINA - Economic Crises and Capital Controls
        events.extend(
            [
                CrisisEvent(
                    date="2019-08-12",
                    country_code="AR",
                    event_type="currency_crisis",
                    title="Peso Crashes 30%",
                    description="Primary election results trigger massive peso devaluation",
                    impact_severity=5,
                    expected_crypto_impact="increase",
                    data_collection_priority=5,
                    sources=["Reuters", "Bloomberg", "Financial Times"],
                ),
                CrisisEvent(
                    date="2019-10-27",
                    country_code="AR",
                    event_type="political_crisis",
                    title="Presidential Election",
                    description="Alberto Fernández wins, markets fear return to populist policies",
                    impact_severity=4,
                    expected_crypto_impact="increase",
                    data_collection_priority=3,
                    sources=["Reuters", "Bloomberg"],
                ),
                CrisisEvent(
                    date="2020-09-01",
                    country_code="AR",
                    event_type="policy_change",
                    title="Stricter Capital Controls",
                    description="Government tightens dollar purchase restrictions",
                    impact_severity=4,
                    expected_crypto_impact="increase",
                    data_collection_priority=4,
                    sources=["Central Bank of Argentina", "Reuters"],
                ),
                CrisisEvent(
                    date="2022-07-02",
                    country_code="AR",
                    event_type="political_crisis",
                    title="Economy Minister Resigns",
                    description="Martín Guzmán resigns amid economic turmoil",
                    impact_severity=3,
                    expected_crypto_impact="increase",
                    data_collection_priority=3,
                    sources=["Reuters", "Bloomberg", "La Nacion"],
                ),
            ]
        )

        return events

    def get_events_by_country(self, country_code: str) -> List[CrisisEvent]:
        """
        Get all crisis events for a specific country.

        Parameters:
        -----------
        country_code : str
            ISO country code

        Returns:
        --------
        list
            Crisis events for the country, sorted by date
        """
        country_events = [
            e for e in self.crisis_events if e.country_code == country_code
        ]
        return sorted(country_events, key=lambda x: x.date)

    def get_priority_events(self, min_priority: int = 4) -> List[CrisisEvent]:
        """
        Get high-priority crisis events for data collection.

        Parameters:
        -----------
        min_priority : int
            Minimum priority level (1-5)

        Returns:
        --------
        list
            High-priority crisis events
        """
        priority_events = [
            e for e in self.crisis_events if e.data_collection_priority >= min_priority
        ]
        return sorted(
            priority_events,
            key=lambda x: (x.data_collection_priority, x.date),
            reverse=True,
        )

    def get_events_by_type(self, event_type: str) -> List[CrisisEvent]:
        """
        Get all events of a specific type.

        Parameters:
        -----------
        event_type : str
            Type of crisis event

        Returns:
        --------
        list
            Events of the specified type
        """
        return [e for e in self.crisis_events if e.event_type == event_type]

    def save_timeline_to_csv(self) -> str:
        """
        Save the complete crisis timeline to CSV for analysis.

        Returns:
        --------
        str
            Path to the saved CSV file
        """

        timeline_data = []

        for event in self.crisis_events:
            timeline_data.append(
                {
                    "date": event.date,
                    "country_code": event.country_code,
                    "event_type": event.event_type,
                    "title": event.title,
                    "description": event.description,
                    "impact_severity": event.impact_severity,
                    "expected_crypto_impact": event.expected_crypto_impact,
                    "data_collection_priority": event.data_collection_priority,
                    "sources": "; ".join(event.sources),
                }
            )

        # Save to analysis directory
        timeline_file = self.csv_manager.base_dir / "analysis" / "crisis_timeline.csv"

        headers = [
            "date",
            "country_code",
            "event_type",
            "title",
            "description",
            "impact_severity",
            "expected_crypto_impact",
            "data_collection_priority",
            "sources",
        ]

        self.csv_manager._write_csv(timeline_file, timeline_data, headers)

        print(f"💾 Crisis timeline saved to: {timeline_file}")
        print(f"📊 Total events: {len(timeline_data)}")

        return str(timeline_file)

    def generate_country_timelines(self):
        """
        Generate individual timeline CSV files for each country.
        """

        countries = set(event.country_code for event in self.crisis_events)

        for country_code in countries:
            country_events = self.get_events_by_country(country_code)

            if not country_events:
                continue

            timeline_data = []
            for event in country_events:
                timeline_data.append(
                    {
                        "date": event.date,
                        "event_type": event.event_type,
                        "title": event.title,
                        "description": event.description,
                        "impact_severity": event.impact_severity,
                        "expected_crypto_impact": event.expected_crypto_impact,
                        "data_collection_priority": event.data_collection_priority,
                        "sources": "; ".join(event.sources),
                    }
                )

            # Save individual country timeline
            country_file = (
                self.csv_manager.base_dir
                / "analysis"
                / f"crisis_timeline_{country_code}.csv"
            )

            headers = [
                "date",
                "event_type",
                "title",
                "description",
                "impact_severity",
                "expected_crypto_impact",
                "data_collection_priority",
                "sources",
            ]

            self.csv_manager._write_csv(country_file, timeline_data, headers)
            print(
                f"📅 {country_code}: {len(timeline_data)} events saved to {country_file.name}"
            )

    def print_summary(self):
        """
        Print a summary of all crisis events.
        """

        print("🚨 CRISIS TIMELINE SUMMARY")
        print("=" * 50)

        countries = set(event.country_code for event in self.crisis_events)

        for country_code in sorted(countries):
            country_events = self.get_events_by_country(country_code)
            print(f"\n🌍 {country_code}: {len(country_events)} events")

            for event in country_events:
                severity_stars = "⭐" * event.impact_severity
                priority_emoji = "🔥" if event.data_collection_priority >= 4 else "📅"
                print(
                    f"  {priority_emoji} {event.date}: {event.title} {severity_stars}"
                )

        print(
            f"\n📊 TOTAL: {len(self.crisis_events)} crisis events across {len(countries)} countries"
        )

        # Priority summary
        high_priority = self.get_priority_events(4)
        print(
            f"🔥 HIGH PRIORITY: {len(high_priority)} events for immediate data collection"
        )


def main():
    """
    Generate and save crisis timelines.
    """
    print("🚨 Generating Crisis Event Timelines...")

    timeline_manager = CrisisTimelineManager()

    # Print summary
    timeline_manager.print_summary()

    # Save comprehensive timeline
    print("\n💾 Saving timeline files...")
    timeline_manager.save_timeline_to_csv()

    # Generate individual country timelines
    timeline_manager.generate_country_timelines()

    print("\n✅ Crisis timeline generation complete!")


if __name__ == "__main__":
    main()
