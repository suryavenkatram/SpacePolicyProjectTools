# ACKNOWLEDGEMENT
# This script was developed with assistance from Artificial Intelligence tools
import os
from datetime import datetime, timedelta
import numpy as np

MU = 398600.4418
EARTH_RADIUS = 6378.137

tle_directory = "./Data/TLEs"  # Directory with TLE files

output_directory = "./AltitudeHistories"  # Output directory
os.makedirs(output_directory, exist_ok=True)

def compute_altitude(mean_motion): # Find altitude from mean motion
    mean_motion_rad = mean_motion * (2 * np.pi) / 86400
    semimajor_axis = (MU / (mean_motion_rad ** 2)) ** (1 / 3)
    return semimajor_axis - EARTH_RADIUS

def extract_epoch(line): # Get epoch dates
    epoch_year = int(line[18:20])  # YY format
    if epoch_year > 50:  # Years greater than 50 will be in the 1900s (57-99)
        epoch_year += 1900
    else:  # Years less than 50 will be in the 2000s (0-24)
        epoch_year += 2000

    epoch_day = float(line[20:32])  # Day
    epoch_datetime = datetime(epoch_year, 1, 1) + timedelta(days=epoch_day - 1)
    return epoch_datetime

def extract_mean_motion(line2): # Get mean motion from 2nd line of TLE or GP
    try: # Classical TLEs
        if len(line2) >= 69 and line2[0] == '2':
            mean_motion = float(line2[52:63].strip())  # Columns 53-63
        else: # GP in "TLE" format
            fields = line2.split()
            mean_motion = float(fields[-1])  # Last field
    except (ValueError, IndexError) as e:
        raise ValueError(f"Could not parse mean motion from Line 2: {line2}, Error: {e}")

    return mean_motion

for file in os.listdir(tle_directory):
    if file.endswith(".txt"):
        norad_id = os.path.splitext(file)[0]  # Assume files are listed as "NORAD_ID.txt"
        file_path = os.path.join(tle_directory, file)
        output_file = os.path.join(output_directory, f"{norad_id}.csv")

        with open(file_path, "r") as f:
            lines = [line.strip() for line in f.readlines()]

        epochs = []
        altitudes = []

        for i in range(0, len(lines), 2):
            if i + 1 < len(lines): # Make sure you can get full TLE
                try:
                    line1 = lines[i]
                    line2 = lines[i + 1]
                    epoch = extract_epoch(line1)
                    mean_motion = extract_mean_motion(line2)
                    altitude = compute_altitude(mean_motion)
                    epochs.append(epoch)
                    altitudes.append(altitude)
                except Exception as e:
                    print(f"Error processing lines in {file}: {e}")

        if epochs and altitudes:
            sorted_data = sorted(zip(epochs, altitudes), key=lambda x: x[0])
            epochs, altitudes = zip(*sorted_data)
            with open(output_file, "w", newline="") as output:
                for epoch, altitude in zip(epochs, altitudes):
                    output.write(f"{epoch},{altitude:.6f}\n") # Write epoch/altitude to corresponding output file

        print(f"Processed {file} -> {output_file}")
