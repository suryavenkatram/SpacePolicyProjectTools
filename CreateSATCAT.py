# ACKNOWLEDGEMENT
# This script was developed with assistance from Artificial Intelligence tools
import pandas as pd

input_file = "alldecayedsats.csv"  # Full Space-Track SATCAT file
output_filtered_file = "./SatFilterFiles/no_constellation_LEO_catalog.csv"
output_norad_file = "./SatFilterFiles/AnalysisInputs/noconstellation_norad.csv"

df = pd.read_csv(input_file)

filtered_df = df[~df['OBJECT_NAME'].str.contains(r'OBJECT|R/B|DEB', case=False, na=False)]
filtered_df = filtered_df[(df['APOGEE'] <= 2000)]
filtered_df = filtered_df[(df['PERIGEE'] <= 2000)]

exclude_constellations = True
if exclude_constellations is True:
    filtered_df = filtered_df[~df['OBJECT_NAME'].str.contains(r'Starlink|OneWeb|SpaceBee|Iridum|Global|Orbcomm|Kepler', case=False, na=False)]

save_output_csv = False

if save_output_csv is True:
    filtered_df.to_csv(output_filtered_file, index=False)
    print(f"- Filtered satellites: {output_filtered_file}")

norad_ids = ','.join(filtered_df['NORAD_CAT_ID'].astype(str)) # Create a new CSV containing comma-separated NORAD_CAT_IDs of compliant satellites
with open(output_norad_file, 'w') as norad_file:
    norad_file.write(norad_ids)
print(f"- NORAD IDs CSV: {output_norad_file}")
