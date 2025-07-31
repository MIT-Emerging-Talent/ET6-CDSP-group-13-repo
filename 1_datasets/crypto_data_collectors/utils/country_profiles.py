"""
Country Profiles Loader Module
==============================

This module provides utility functions to load and query structured metadata
for target countries involved in P2P cryptocurrency market research.

Each country profile is defined in a YAML configuration file (typically
located at `config/countries.yml`). These profiles include standardized fields
such as country code, fiat currency, commonly used payment methods, exchange
rate sources, and preferred stablecoins. The profiles guide scraping, API usage,
data enrichment, and location inference.

Returned Object Shape:
----------------------
Each profile is returned as a dictionary with the following keys:
- `country_code` (str): ISO 3166-1 alpha-2 code.
- `name` (str): Full country name.
- `fiat` (str): ISO 4217 currency code.
- `stablecoins` (list): List of relevant stablecoins.
- `expected_payment_methods` (list): Common local payment methods.
- `exchange_rate_sources` (list): URLs for exchange rate APIs.
- `p2p_platforms` (list): P2P platforms active in the region.
- `start_date` (str): The start date for data collection (YYYY-MM-DD).
- `notes` (str): Qualitative context about the market.

Functions
---------
- load_profiles(filepath): Loads all country profiles from YAML.
- get_profile_by_country_code(code): Retrieves a specific profile by code.
- get_profile_by_country_name(name): Retrieves a specific profile by country name.
- list_supported_countries(): Returns a list of available countries.

Author: Clement MUGISHA
License: MIT
"""

from functools import lru_cache

import yaml


@lru_cache(maxsize=1)
def load_profiles(filepath="config/countries.yml"):
    """
    Load all country profiles from a YAML configuration file.

    The result is cached to avoid repeated file I/O.

    Parameters:
    -----------
    filepath : str
        The path to the YAML file containing the country profiles.

    Returns:
    --------
    list of dict
        List of country profiles. Each profile is a dictionary, for example:
        {
            'country_code': 'SD',
            'name': 'Sudan',
            'fiat': 'SDG',
            'stablecoins': ['USDT'],
            'expected_payment_methods': ['MTN', 'Zain', 'Bank Transfer'],
            'exchange_rate_sources': ['https://xe.com'],
            'p2p_platforms': ['binance', 'okx', 'paxful'],
            'start_date': '2019-01-01',
            'notes': 'Conflict zone, high mobile money use, USD scarcity'
        }

    Example:
    --------
    >>> # This is a conceptual example. It assumes a file is present.
    >>> # profiles = load_profiles('config/countries.yml')
    >>> # print(profiles[0]['name'])
    >>> # Sudan
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The configuration file was not found at {filepath}")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return []


def get_profile_by_country_code(country_code, filepath="config/countries.yml"):
    """
    Retrieve a country profile by ISO 3166-1 alpha-2 country code.

    The search is case-insensitive and ignores leading/trailing whitespace.

    Parameters:
    -----------
    country_code : str
        Two-letter country code (e.g., "SD", "ve").

    filepath : str
        Path to the YAML configuration file.

    Returns:
    --------
    dict
        The matched country profile dictionary.

    Raises:
    -------
    ValueError
        If the country profile is not found in the list.

    Example:
    --------
    >>> # Assuming 'config/countries.yml' contains a profile for Sudan ('SD')
    >>> # profile = get_profile_by_country_code('sd')
    >>> # print(profile['name'])
    >>> # Sudan
    """
    profiles = load_profiles(filepath)
    search_code = country_code.strip().upper()
    for profile in profiles:
        if profile["country_code"].upper() == search_code:
            return profile
    raise ValueError(f"No profile found for country code: {country_code}")


def get_profile_by_country_name(name, filepath="config/countries.yml"):
    """
    Retrieve a country profile by country name.

    The search is case-insensitive and ignores leading/trailing whitespace.

    Parameters:
    -----------
    name : str
        The full country name (e.g., "Sudan", "venezuela").

    filepath : str
        Path to the YAML configuration file.

    Returns:
    --------
    dict
        The matched country profile dictionary.

    Raises:
    -------
    ValueError
        If the country profile is not found in the list.

    Example:
    --------
    >>> # Assuming 'config/countries.yml' contains a profile for Venezuela
    >>> # profile = get_profile_by_country_name('  Venezuela  ')
    >>> # print(profile['fiat'])
    >>> # VES
    """
    profiles = load_profiles(filepath)
    search_name = name.strip().lower()
    for profile in profiles:
        if profile["name"].lower() == search_name:
            return profile
    raise ValueError(f"No profile found for country name: {name}")


def list_supported_countries(filepath="config/countries.yml"):
    """
    List all supported countries from the loaded profiles.

    Parameters:
    -----------
    filepath : str
        Path to the YAML configuration file.

    Returns:
    --------
    list of dict
        List of all country profile dictionaries.

    Example:
    --------
    >>> # Assuming 'config/countries.yml' has Sudan and Venezuela
    >>> # countries = list_supported_countries()
    >>> # print(countries[0]['country_code'])
    >>> # SD
    """
    profiles = load_profiles(filepath)
    return profiles
