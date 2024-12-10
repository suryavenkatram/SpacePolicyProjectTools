# ACKNOWLEDGEMENT
# This script was developed with assistance from Artificial Intelligence tools
import pandas as pd
import os

def check_altitude_conditions(altitude_dir, norad_ids_file, catalog_file):
    with open(norad_ids_file, 'r') as f: # Load the NORAD IDs from the input CSV
        norad_ids = f.read().strip().split(',')

    catalog = pd.read_csv(catalog_file) # Load the satellite catalog

    valid_ids = []
    invalid_ids = []

    for norad_id in norad_ids:
        file_path = os.path.join(altitude_dir, f"{norad_id}.csv")

        if not os.path.exists(file_path):
            print(f"Warning: Altitude history file for NORAD ID {norad_id} not found.")
            invalid_ids.append(norad_id)  # Mark as invalid
            continue

        try:
            altitudes = pd.read_csv(file_path, header=None, names=["epoch", "altitude"]) # Read the altitude history
        except Exception as e:
            print(f"Error reading file for NORAD ID {norad_id}: {e}")
            invalid_ids.append(norad_id)
            continue

        if altitudes["altitude"].min() >= 150 and altitudes["altitude"].max() <= 2000: # Check altitude conditions
            valid_ids.append(norad_id)
        else:
            invalid_ids.append(norad_id)

    valid_catalog = catalog[catalog["NORAD_CAT_ID"].astype(str).isin(valid_ids)]
    invalid_catalog = catalog[catalog["NORAD_CAT_ID"].astype(str).isin(invalid_ids)]

    valid_ids_output = "./SatFilterFiles/ProcessedData/valid_norad_ids_no_const_LEO.csv"
    invalid_ids_output = "./SatFilterFiles/ProcessedData/invalid_norad_ids_no_const_LEO.csv"
    valid_catalog_output = "./SatFilterFiles/ProcessedData/valid_catalog_no_const_LEO.csv"
    invalid_catalog_output = "./SatFilterFiles/ProcessedData/invalid_catalog_no_const_LEO.csv"

    with open(valid_ids_output, 'w') as f: # Save the valid/invalid NORAD IDs
        f.write(','.join(valid_ids))

    with open(invalid_ids_output, 'w') as f:
        f.write(','.join(invalid_ids))

    valid_catalog.to_csv(valid_catalog_output, index=False) # Save the valid/invalid catalogs
    invalid_catalog.to_csv(invalid_catalog_output, index=False)

    print(f"Results saved to:\n"
          f"- {valid_ids_output}\n"
          f"- {invalid_ids_output}\n"
          f"- {valid_catalog_output}\n"
          f"- {invalid_catalog_output}")

altitude_histories_directory = "./AltitudeHistories"  # Directory containing altitude history files
norad_ids_csv = "./SatFilterFiles/AnalysisInputs/noconstellation_norad.csv"  # Input file with NORAD IDs
catalog_csv = "./SatFilterFiles/no_constellation_LEO_catalog.csv"  # Input catalog file with satellite metadata

check_altitude_conditions(altitude_histories_directory, norad_ids_csv, catalog_csv)
