# ACKNOWLEDGEMENT
# This script was developed with assistance from Artificial Intelligence tools
import pandas as pd
import os

def process_satellite_ages(input_csv):
    satellite_ages = pd.read_csv(input_csv) # Load the satellite ages CSV
    satellite_ages['AGE'] = pd.to_numeric(satellite_ages['AGE'], errors='coerce')
    satellite_ages['LAUNCH'] = pd.to_datetime(satellite_ages['LAUNCH'], errors='coerce')
    satellite_ages['LAUNCH_YEAR'] = satellite_ages['LAUNCH'].dt.year # Extract the year and compute the decade
    satellite_ages['DECADE'] = (satellite_ages['LAUNCH_YEAR'] // 10) * 10

    # Mean age by decade
    mean_age_by_decade = satellite_ages.groupby('DECADE')['AGE'].mean().reset_index()
    mean_age_by_decade.columns = ['DECADE', 'MEAN_AGE']

    # Mean age by country
    mean_age_by_country = satellite_ages.groupby('COUNTRY')['AGE'].mean().reset_index()
    mean_age_by_country.columns = ['COUNTRY', 'MEAN_AGE']

    # Mean age by decade and country
    mean_age_by_decade_country = satellite_ages.groupby(['DECADE', 'COUNTRY'])['AGE'].mean().reset_index()
    mean_age_by_decade_country.columns = ['DECADE', 'COUNTRY', 'MEAN_AGE']

    # Satellites in age ranges by decade and country
    age_ranges = {
        "less_than_5": (0, 5),
        "between_5_and_10": (5, 10),
        "between_10_and_25": (10, 25),
        "between_25_and_30": (25, 30),
        "greater_than_30": (30, float('inf'))
    }

    range_files = {}
    for label, (min_age, max_age) in age_ranges.items():
        range_df = satellite_ages[
            (satellite_ages['AGE'] > min_age) & (satellite_ages['AGE'] <= max_age)
        ]
        grouped_range = range_df.groupby(['DECADE', 'COUNTRY']).size().reset_index(name='SATELLITE_COUNT')
        range_files[label] = grouped_range

    # Satellites with ages > 30
    satellites_greater_than_30 = satellite_ages[satellite_ages['AGE'] > 30]

    # Satellites between 25 and 30
    satellites_25_to_30 = satellite_ages[(satellite_ages['AGE'] > 25) & (satellite_ages['AGE'] <= 30)]

    # Total satellites in each age bracket
    age_bracket_counts = []
    for label, (min_age, max_age) in age_ranges.items():
        count = satellite_ages[(satellite_ages['AGE'] > min_age) & (satellite_ages['AGE'] <= max_age)].shape[0]
        age_bracket_counts.append({'Age Bracket': label, 'Satellite Count': count})
    age_bracket_counts_df = pd.DataFrame(age_bracket_counts)

    output_dir = './AnalysisResults/WithConst' # Save outputs
    os.makedirs(output_dir, exist_ok=True)

    mean_age_by_decade.to_csv(os.path.join(output_dir, 'mean_age_by_decade.csv'), index=False)
    mean_age_by_country.to_csv(os.path.join(output_dir, 'mean_age_by_country.csv'), index=False)
    mean_age_by_decade_country.to_csv(os.path.join(output_dir, 'mean_age_by_decade_country.csv'), index=False)
    age_bracket_counts_df.to_csv(os.path.join(output_dir, 'satellite_age_bracket_counts.csv'), index=False)

    for label, df in range_files.items():
        df.to_csv(os.path.join(output_dir, f'satellites_{label}.csv'), index=False)

    satellites_greater_than_30.to_csv(os.path.join(output_dir, 'satellites_ages_greater_than_30.csv'), index=False)

    satellites_25_to_30.to_csv(os.path.join(output_dir, 'satellites_ages_25_to_30.csv'), index=False)

    print(f"Output files saved in {output_dir}")

input_csv = "./SatAgeFiles/satellite_ages_all_LEO_processed.csv"  # Input satellite ages CSV
process_satellite_ages(input_csv)
