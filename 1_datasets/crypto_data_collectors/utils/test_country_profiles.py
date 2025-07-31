"""
Test script for country_profiles.py functions
"""

import json

from utils.country_profiles import (
    get_profile_by_country_code,
    get_profile_by_country_name,
    list_supported_countries,
    load_profiles,
)


def test_all_functions():
    print("=" * 60)
    print("TESTING COUNTRY PROFILES UTILITY")
    print("=" * 60)

    # Test 1: load_profiles
    print("\n1. Testing load_profiles():")
    profiles = load_profiles()
    print(f"   ✅ Loaded {len(profiles)} country profiles")

    # Test 2: list_supported_countries
    print("\n2. Testing list_supported_countries():")
    countries = list_supported_countries()
    print(f"   ✅ Found {len(countries)} countries:")
    for country in countries:
        print(
            f"      • {country['country_code']} - {country['name']} ({country['fiat']})"
        )

    # Test 3: get_profile_by_country_code
    print("\n3. Testing get_profile_by_country_code():")
    test_codes = ["SD", "sd", "VE", "ng"]
    for code in test_codes:
        try:
            profile = get_profile_by_country_code(code)
            print(f"   ✅ {code} -> {profile['name']} ({profile['fiat']})")
        except ValueError as e:
            print(f"   ❌ {code} -> {e}")

    # Test 4: get_profile_by_country_name
    print("\n4. Testing get_profile_by_country_name():")
    test_names = ["Sudan", "venezuela", "  Nigeria  ", "InvalidCountry"]
    for name in test_names:
        try:
            profile = get_profile_by_country_name(name)
            print(f"   ✅ '{name}' -> {profile['country_code']} ({profile['fiat']})")
        except ValueError as e:
            print(f"   ❌ '{name}' -> {e}")

    # Test 5: Show a complete profile
    print("\n5. Sample complete profile (Sudan):")
    sudan_profile = get_profile_by_country_code("SD")
    print(json.dumps(sudan_profile, indent=3))

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_all_functions()
