"""
This script processes INFORM Severity Index data from raw XLSX files.
It extracts relevant information, cleans it, collapses data to one row per country-year,
adds a crisis flag, and saves the aggregated data to a CSV file.
"""

import os

import pandas as pd
from pandas.errors import EmptyDataError  # Import specific error for better handling


def find_header_row(df, possible_severity_cols, max_rows_to_check=5):
    """
    Attempts to find the header row in a DataFrame by checking for 'ISO3'
    and one of the possible severity column names.
    Assumes df is loaded with header=None.
    """
    for i in range(min(max_rows_to_check, len(df))):
        row_values = (
            df.iloc[i].astype(str).str.strip()
        )  # Get row values and strip whitespace

        # Check for 'ISO3'
        iso3_found = "ISO3" in row_values.values

        # Check for a severity column
        severity_found = False
        for col in possible_severity_cols:
            if col in row_values.values:
                severity_found = True
                break

        if iso3_found and severity_found:
            return i  # Return the 0-based index of the header row
    return -1  # Header row not found


def process_inform_severity_data(raw_data_path, processed_data_path):
    """
    Processes INFORM Severity Index data from raw XLSX files, cleans it,
    and saves the aggregated data to a CSV file.

    Args:
        raw_data_path (str): Path to the directory containing raw INFORM Severity XLSX files.
        processed_data_path (str): Path to the directory where the processed CSV will be saved.
    """

    all_years_data = []

    # Define possible sheet names to try, in order of preference
    preferred_sheet_names = [
        "INFORM Severity - all crises",
        "INFORM Severity - hidden",
        "INFORM Severity - country",
        "Crisis Data",
    ]

    # Define possible severity column names
    possible_severity_col_names = ["Severity AI", "INFORM Severity Index"]

    # Iterate through each year's file (2019-2024)
    for year in range(2019, 2025):
        # Construct possible filenames (December or May release)
        dec_filename = f"inform_severity_-_december_{year}.xlsx"
        may_filename = f"inform_severity_-_may_{year}.xlsx"

        file_path = None
        if os.path.exists(os.path.join(raw_data_path, dec_filename)):
            file_path = os.path.join(raw_data_path, dec_filename)
        elif os.path.exists(os.path.join(raw_data_path, may_filename)):
            file_path = os.path.join(raw_data_path, may_filename)
        else:
            print(f"Warning: No INFORM Severity file found for {year}. Skipping.")
            continue

        df = None
        header_row_idx = -1

        for sheet_name in preferred_sheet_names:
            try:
                # Load sheet without a header to find it dynamically
                temp_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

                # Find the actual header row index
                header_row_idx = find_header_row(temp_df, possible_severity_col_names)

                if header_row_idx != -1:
                    # Re-load the sheet with the identified header row
                    df = pd.read_excel(
                        file_path, sheet_name=sheet_name, header=header_row_idx
                    )
                    print(
                        f"Info: Found sheet '{sheet_name}' with header at row "
                        f"{header_row_idx + 1} in {os.path.basename(file_path)}."
                    )
                    break
                else:
                    print(
                        f"Info: Sheet '{sheet_name}' in "
                        f"{os.path.basename(file_path)} does not contain expected "
                        "headers in first few rows. Trying next sheet."
                    )
            except EmptyDataError:  # Handle specific case of an empty sheet
                print(
                    f"Info: Sheet '{sheet_name}' in "
                    f"{os.path.basename(file_path)} is empty. Trying next sheet."
                )
                continue
            except ValueError:  # Handle general ValueError (e.g., sheet not found)
                continue
            except (
                Exception
            ) as e:  # Catch any other unexpected errors during read_excel
                print(
                    f"Error reading sheet '{sheet_name}' from "
                    f"{os.path.basename(file_path)}: {e}. Trying next sheet."
                )
                continue

        if df is None:  # If no preferred sheet worked or found valid header
            print(
                f"Error: Could not find a suitable sheet with 'ISO3' and severity "
                f"column in {os.path.basename(file_path)}. Skipping."
            )
            continue

        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()

        # Identify the correct severity column name after stripping
        current_severity_col = None
        for col_name in possible_severity_col_names:
            if col_name in df.columns:
                current_severity_col = col_name
                break

        # Additional check for ISO3 and severity column AFTER header detection
        if "ISO3" not in df.columns or current_severity_col is None:
            print(
                f"Error: After header detection, still missing 'ISO3' or "
                "expected severity column in "
                f"{os.path.basename(file_path)}. Found columns: "
                f"{df.columns.tolist()}. Skipping."
            )
            continue

        if "Year" not in df.columns:
            df["Year"] = year
            print(
                f"Info: 'Year' column not found in {os.path.basename(file_path)}. "
                f"Added year {year} from filename."
            )

        df = df[["ISO3", "Year", current_severity_col]].copy()
        df.rename(columns={current_severity_col: "severity_score"}, inplace=True)

        # Convert severity_score to numeric, coercing errors to NaN
        df["severity_score"] = pd.to_numeric(df["severity_score"], errors="coerce")

        all_years_data.append(df)

    if not all_years_data:
        print("No data processed. Exiting.")
        return

    # Concatenate all yearly data
    combined_df = pd.concat(all_years_data, ignore_index=True)

    # Drop rows with missing ISO3 codes
    initial_rows = len(combined_df)
    combined_df.dropna(subset=["ISO3"], inplace=True)
    if len(combined_df) < initial_rows:
        print(
            f"Dropped {initial_rows - len(combined_df)} rows due to missing ISO3 codes."
        )

    # Collapse to one row per country-year, taking the maximum Severity AI
    processed_df = (
        combined_df.groupby(["ISO3", "Year"])["severity_score"].max().reset_index()
    )

    # Add crisis_flag
    processed_df["crisis_flag"] = (processed_df["severity_score"] >= 2.5).astype(int)

    # Quick QA Checklist
    # 1. No missing ISO3 codes (already handled by dropna)
    # 2. No duplicate ISO3–Year rows (handled by groupby)
    # 3. severity_score between 0 and 5
    if not (
        (processed_df["severity_score"].dropna() >= 0)
        & (processed_df["severity_score"].dropna() <= 5)
    ).all():
        print(
            "Warning: Some 'severity_score' values are not between 0 and 5. "
            "Please review the raw data."
        )

    # Ensure final column schema
    final_cols = ["ISO3", "Year", "severity_score", "crisis_flag"]
    processed_df = processed_df[final_cols]

    # Save the finished file
    output_filename = "crisis_severity_2019-24.csv"
    output_path = os.path.join(processed_data_path, output_filename)
    os.makedirs(processed_data_path, exist_ok=True)  # Ensure directory exists
    processed_df.to_csv(output_path, index=False)

    print(f"Data processing complete. Saved to: {output_path}")
    print("\nQuick QA Checklist Results:")
    print(f"- Missing ISO3 codes: {processed_df['ISO3'].isnull().sum()}")
    print(
        f"- Duplicate ISO3-Year rows: "
        f"{processed_df.duplicated(subset=['ISO3', 'Year']).sum()}"
    )
    print(
        f"- Severity Score min: {processed_df['severity_score'].min()}, "
        f"max: {processed_df['severity_score'].max()}"
    )


if __name__ == "__main__":
    # Define your paths relative to the script location or absolute paths
    script_dir = os.path.dirname(__file__)
    raw_datasets_path = os.path.join(script_dir, "..", "1_datasets", "raw_datasets")
    processed_datasets_path = os.path.join(script_dir, "..", "1_datasets", "processed")

    # Uncomment and use these absolute paths if you prefer and comment out the
    # relative paths above
    # raw_datasets_path = r"D:\MIT Data s projet\ET6-CDSP-group-13-repo\1_datasets\raw_datasets"
    # processed_datasets_path = r"D:\MIT Data s projet\ET6-CDSP-group-13-repo\1_datasets\processed"

    process_inform_severity_data(raw_datasets_path, processed_datasets_path)
