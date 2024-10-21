import os
import pandas as pd
import numpy as np


# Constants for the Empire State Building coordinates in radians
empire_state_lon = np.radians(-73.985428)
empire_state_lat = np.radians(40.748817)

# Vectorized Haversine formula to calculate distances in meters
def haversine_vectorized(lat, lon):
    # Convert lat/lon to radians
    lat = np.radians(lat)
    lon = np.radians(lon)
    
    # Difference between the points
    dlat = lat - empire_state_lat
    dlon = lon - empire_state_lon
    
    # Haversine formula
    a = np.sin(dlat / 2)**2 + np.cos(lat) * np.cos(empire_state_lat) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Earth radius in meters
    meters = 6371000 * c
    return meters


# Get current working directory
script_dir = os.getcwd()
file_path = os.path.join(script_dir, "unprocessed-data/NYPD_Arrests_Data.csv")
arrests_df = pd.read_csv(file_path)


arrests_df = arrests_df[["ARREST_DATE", "LAW_CAT_CD", "Latitude", "Longitude"]]

# Renaming the columns to lowercase and understandable names
arrests_df = arrests_df.rename(columns={
    "ARREST_DATE": "arrest_date",
    "LAW_CAT_CD": "law_category",
    "Latitude": "latitude",
    "Longitude": "longitude"
})

# Take only Felony and Misdemeanor
arrests_df = arrests_df[arrests_df["law_category"].isin(['F', 'M'])]

# Sort the DataFrame by 'occur_datetime'
arrests_df = arrests_df.sort_values(by='arrest_date')

# Apply the vectorized function to the DataFrame columns
arrests_df['distance_to_empire'] = haversine_vectorized(arrests_df['latitude'], arrests_df['longitude'])

# Filter for pickups within 1000 meters (1 km) from the Empire State Building
arrests_df_1000 = arrests_df[arrests_df['distance_to_empire'] <= 1000].copy() 
arrests_df_2000A = arrests_df[arrests_df['distance_to_empire'] >= 2000].copy()  


import pandas as pd

# Create a day time range from April 1, 2014, to September 30, 2014
time_range = pd.date_range(start='2014-04-01', end='2014-09-30', freq='1D')

# Create a DataFrame for the 1-day intervals
time_df = pd.DataFrame(time_range, columns=['arrest_date'])

# Ensure 'arrest_date' in both datasets is in datetime format
arrests_df_1000['arrest_date'] = pd.to_datetime(arrests_df_1000['arrest_date'])
arrests_df_2000A['arrest_date'] = pd.to_datetime(arrests_df_2000A['arrest_date'])

# Filter and group by 'arrest_date' for F (Felony) and M (Misdemeanor) categories
# For arrests_df_1000 (within 1000 meters)
felony_grouped_1000 = arrests_df_1000[arrests_df_1000['law_category'] == 'F'].groupby('arrest_date').size().reset_index(name='felony_count')
misdemeanor_grouped_1000 = arrests_df_1000[arrests_df_1000['law_category'] == 'M'].groupby('arrest_date').size().reset_index(name='misdemeanor_count')

# For arrests_df_2000A (beyond 2000 meters)
felony_grouped_2000A = arrests_df_2000A[arrests_df_2000A['law_category'] == 'F'].groupby('arrest_date').size().reset_index(name='felony_count')
misdemeanor_grouped_2000A = arrests_df_2000A[arrests_df_2000A['law_category'] == 'M'].groupby('arrest_date').size().reset_index(name='misdemeanor_count')

# Merge the full timeline (time_df) with the grouped felony and misdemeanor data
final_arrests_df_1000 = pd.merge(time_df, felony_grouped_1000, on='arrest_date', how='left')
final_arrests_df_1000 = pd.merge(final_arrests_df_1000, misdemeanor_grouped_1000, on='arrest_date', how='left')

final_arrests_df_2000A = pd.merge(time_df, felony_grouped_2000A, on='arrest_date', how='left')
final_arrests_df_2000A = pd.merge(final_arrests_df_2000A, misdemeanor_grouped_2000A, on='arrest_date', how='left')

# Fill missing values with 0 (for days where no arrests occurred)
final_arrests_df_1000[['felony_count', 'misdemeanor_count']] = final_arrests_df_1000[['felony_count', 'misdemeanor_count']].fillna(0).astype(int)
final_arrests_df_2000A[['felony_count', 'misdemeanor_count']] = final_arrests_df_2000A[['felony_count', 'misdemeanor_count']].fillna(0).astype(int)

# Calculate the total number of arrests for each day and convert it to integer
final_arrests_df_1000['total_arrests'] = (final_arrests_df_1000['felony_count'] + final_arrests_df_1000['misdemeanor_count']).astype(int)
final_arrests_df_2000A['total_arrests'] = (final_arrests_df_2000A['felony_count'] + final_arrests_df_2000A['misdemeanor_count']).astype(int)


# Save to CSV
output_file_1000 = os.path.join(script_dir, 'arrests_F_and_M_1000m.csv')
final_arrests_df_1000.to_csv(output_file_1000, index=False)

output_file_2000A = os.path.join(script_dir, 'arrests_F_and_M_2000Am.csv')
final_arrests_df_2000A.to_csv(output_file_2000A, index=False)

output_file_raw = os.path.join(script_dir, 'arrests_F_and_M_raw.csv')
arrests_df.to_csv(output_file_raw, index=False)

print(f"Files saved:\n{output_file_1000}\n{output_file_2000A}\n{output_file_raw}")
