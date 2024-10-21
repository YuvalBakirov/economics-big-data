import os
import numpy as np
import pandas as pd


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
file_path = os.path.join(script_dir, "unprocessed-data/NYPD_Shooting_Incident_Data.csv")
shootings_df = pd.read_csv(file_path)

# Selecting the required columns
shootings_df = shootings_df[["OCCUR_DATE", "OCCUR_TIME", "STATISTICAL_MURDER_FLAG", "Latitude", "Longitude"]]

# Renaming the columns to lowercase and understandable names
shootings_df = shootings_df.rename(columns={
    "OCCUR_DATE": "occur_date",
    "OCCUR_TIME": "occur_time",
    "STATISTICAL_MURDER_FLAG": "statistical_murder",
    "Latitude": "latitude",
    "Longitude": "longitude"
})

# Combine 'occur_date' and 'occur_time' into a single datetime column
shootings_df['occur_datetime'] = pd.to_datetime(
    shootings_df['occur_date'] + ' ' + shootings_df['occur_time'],
    format='%m/%d/%Y %H:%M:%S'
)

# Drop the original 'occur_date' and 'occur_time' columns
shootings_df = shootings_df.drop(columns=['occur_date', 'occur_time'])

# Reorder columns to place 'occur_datetime' first
cols = ['occur_datetime'] + [col for col in shootings_df.columns if col != 'occur_datetime']
shootings_df = shootings_df[cols]

# Sort the DataFrame by 'occur_datetime'
shootings_df = shootings_df.sort_values(by='occur_datetime')

# Create a new column 'shooting_time_15min' by rounding to the nearest 15 minutes
shootings_df['shooting_time_15min'] = shootings_df['occur_datetime'].dt.floor('15T')
shootings_df = shootings_df[["occur_datetime", "shooting_time_15min", "statistical_murder", "latitude", "longitude"]]


# Apply the vectorized function to the DataFrame columns
shootings_df['distance_to_empire'] = haversine_vectorized(shootings_df['latitude'], shootings_df['longitude'])

# Filter for pickups within 1000 meters (1 km) from the Empire State Building
shootings_df_1000 = shootings_df[shootings_df['distance_to_empire'] <= 1000].copy() 
shootings_df_2000A = shootings_df[shootings_df['distance_to_empire'] >= 2000].copy()  


shootings_df_1000_boolean = shootings_df_1000[["shooting_time_15min"]]



# Create a 15-minute time range from April 1, 2014 to September 30, 2014
time_range = pd.date_range(start='2014-04-01 00:00:00', end='2014-09-30 23:59:59', freq='15T')

# Create a DataFrame for the 15-minute intervals
time_df = pd.DataFrame(time_range, columns=['shooting_time_15min'])


# Group shootings by the 15-minute intervals and count the number of occurrences
shootings_grouped = shootings_df_2000A.groupby('shooting_time_15min').size().reset_index(name='murder_count')

# Merge the full timeline (time_df) with the grouped shooting data
final_shootings_2000A_df = pd.merge(time_df, shootings_grouped, on='shooting_time_15min', how='left')

# Fill any missing values with 0 to ensure all 15-minute intervals are included
final_shootings_2000A_df['murder_count'] = final_shootings_2000A_df['murder_count'].fillna(0)



final_shootings_2000A_boolean = final_shootings_2000A_df.copy()

# Create a new column 'was_shooting' where murder_count > 0
final_shootings_2000A_boolean['was_shooting'] = final_shootings_2000A_df['murder_count'] > 0


final_shootings_2000A_boolean = final_shootings_2000A_boolean[["shooting_time_15min", "was_shooting"]]


# Save to CSV


output_file_raw = os.path.join(script_dir, 'shootings_raw.csv')
shootings_df.to_csv(output_file_raw, index=False)

output_file_1000_boolean = os.path.join(script_dir, 'shootings_1000m_boolean.csv')
shootings_df_1000_boolean.to_csv(output_file_1000_boolean, index=False)

output_file_2000A_boolean = os.path.join(script_dir, 'shootings_2000Am_boolean.csv')
final_shootings_2000A_boolean.to_csv(output_file_2000A_boolean, index=False)

output_file_2000A = os.path.join(script_dir, 'shootings_2000Am.csv')
final_shootings_2000A_df.to_csv(output_file_2000A, index=False)

print(f"Files saved:\n{output_file_raw}\n{output_file_1000_boolean}\n{output_file_2000A_boolean}\n{output_file_2000A}")