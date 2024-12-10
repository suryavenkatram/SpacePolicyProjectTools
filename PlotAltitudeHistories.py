# ACKNOWLEDGEMENT
# This script was developed with assistance from Artificial Intelligence tools
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Directories and file paths
altitude_histories_directory = "./AltitudeHistories"
compliant_sats_file = "./SatFilterFiles/ProcessedData/valid_catalog_no_const_LEO.csv"  # CSV file with satellite info
output_ages_file = "./SatAgeFiles/satellite_ages_no_const_LEO_processed.csv"  # Output file for satellite ages
output_plot = "satellite_altitude_history_processed_no_const_LEO.png"  # Output plot file
sats_for_analysis_file = "./SatFilterFiles/ProcessedData/valid_catalog_no_const_LEO.csv"

with open(sats_for_analysis_file, "r") as f: # Load satellite IDs for analysis
    analysis_norad_ids = [id.strip() for id in f.read().split(",")]

compliant_sats = pd.read_csv(compliant_sats_file) # Load compliant satellite data

all_last_peaks = []
def find_last_significant_peak(altitudes, min_peak_distance=10): # find the last significant peak for a satellite
    last_peak = altitudes[0]
    for i in range(len(altitudes) - min_peak_distance):
        if altitudes[i] >= max(altitudes[i + 1:]):
            last_peak = altitudes[i]
            break
    all_last_peaks.append(last_peak)
    return last_peak

def determine_global_threshold(satellites): # determine the global threshold across all satellites
    last_peaks = []
    for sat_id, data in satellites.items():
        altitudes = data['altitudes']
        if len(altitudes) > 10:  # Only consider satellites with enough data
            last_peak = find_last_significant_peak(altitudes)
            last_peaks.append(last_peak)
    return min(last_peaks) if last_peaks else None

satellites = {}
for norad_id in analysis_norad_ids:
    input_file = os.path.join(altitude_histories_directory, f"{norad_id}.csv") # Process each satellite in the analysis list

    if os.path.exists(input_file): # Read the altitude history
        epochs = []
        altitudes = []
        with open(input_file, "r") as f:
            for line in f:
                epoch, altitude = line.strip().split(",")
                if float(altitude.strip()) < 2000.0 and float(altitude.strip()) > 160.0:
                    epochs.append(datetime.fromisoformat(epoch.strip()))
                    altitudes.append(float(altitude.strip()))

        if epochs and altitudes:
            satellites[norad_id] = {'epochs': list(epochs), 'altitudes': list(altitudes)}  # Store satellite data

age_data = []

threshold = determine_global_threshold(satellites) # Determine the global threshold across all satellites

plt.figure(figsize=(12, 8))
for norad_id, data in satellites.items(): # Plot all satellite altitudes with the global threshold
    epochs = data['epochs']
    altitudes = data['altitudes']

    decay_date = None
    comments = "Calculated"
    for i, altitude in enumerate(altitudes):
        if altitude <= threshold:     # Find crossing point and age
            decay_date = epochs[i]
            break

    sat_info = compliant_sats[compliant_sats["NORAD_CAT_ID"].astype(str) == norad_id]     # If no crossing point or age < 1 day, use LAUNCH and DECAY
    if decay_date is None or (decay_date - epochs[0]).days < 1:
        if not sat_info.empty:
            launch_date = pd.to_datetime(sat_info.iloc[0]["LAUNCH"], utc=True)
            decay_date = pd.to_datetime(sat_info.iloc[0]["DECAY"], utc=True)
            age_days = (decay_date - launch_date).days
            comments = "SpaceTrack"
        else:
            age_days = 0
    else:
        age_days = (decay_date - epochs[0]).days

    # Add data to age table
    object_name = sat_info.iloc[0]["OBJECT_NAME"] if not sat_info.empty else "Unknown"
    country = sat_info.iloc[0]["COUNTRY"] if not sat_info.empty else "Unknown"
    launch_date = sat_info.iloc[0]["LAUNCH"] if not sat_info.empty else "Unknown"
    age_data.append([norad_id, object_name, country, launch_date, decay_date, age_days/365, comments])

    plt.plot(epochs, altitudes, label=f"{object_name} ({norad_id})")     # Plot this satellite's altitude history

# Plot the global threshold as a horizontal line
if threshold is not None:
    plt.axhline(threshold, color='red', linestyle='--', label=f"Decay Threshold: {threshold:.2f} km")

print(f"Decay Threshold: {threshold:.2f} km")

plt.xlabel("Epoch (UTC)")
plt.ylabel("Altitude (km)")
plt.title("Satellite Altitude History")
# plt.legend()
plt.grid()
plt.savefig(output_plot)
plt.show()

age_df = pd.DataFrame(age_data, columns=["NORAD_ID", "OBJECT_NAME", "COUNTRY", "LAUNCH", "DECAY", "AGE", "COMMENTS"])
age_df.to_csv(output_ages_file, index=False)

print(f"Satellite ages saved to {output_ages_file}.")
