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
file_path = os.path.join(script_dir, "unprocessed-data/Motor_Vehicle_Collisions_Crashes_Data.csv")
collisions = pd.read_csv(file_path)

# Filter columns that start with 'NUMBER OF'
number_of_cols = collisions.filter(like='NUMBER OF')

# Select the specific columns: "CRASH DATE", "CRASH TIME", "LATITUDE", "LONGITUDE"
specific_cols = collisions[["CRASH DATE", "CRASH TIME", "LATITUDE", "LONGITUDE"]]

# Concatenate both sets of columns into a single DataFrame
collisions = pd.concat([specific_cols, number_of_cols], axis=1)


collisions = collisions.dropna(subset=["LATITUDE", "LONGITUDE"])

# Rename specific columns
collisions = collisions.rename(columns={
    "CRASH DATE": "crash_date",
    "CRASH TIME": "crash_time",
    "LATITUDE": "latitude",
    "LONGITUDE": "longitude",
    "NUMBER OF PERSONS INJURED": "number_of_persons_injured",
    "NUMBER OF PERSONS KILLED": "number_of_persons_killed",
    "NUMBER OF PEDESTRIANS INJURED": "number_of_pedestrians_injured",
    "NUMBER OF PEDESTRIANS KILLED": "number_of_pedestrians_killed",
    "NUMBER OF CYCLIST INJURED": "number_of_cyclist_injured",
    "NUMBER OF CYCLIST KILLED": "number_of_cyclist_killed",
    "NUMBER OF MOTORIST INJURED": "number_of_motorist_injured",
    "NUMBER OF MOTORIST KILLED": "number_of_motorist_killed"
})


# Convert 'crash_date' and 'crash_time' to datetime
collisions['crash_date'] = pd.to_datetime(collisions['crash_date'], format='%m/%d/%Y')
collisions['crash_time'] = pd.to_datetime(collisions['crash_time'], format='%H:%M').dt.time

# Sort the DataFrame by 'crash_date' and 'crash_time'
collisions = collisions.sort_values(by=['crash_date', 'crash_time'])

# Combine 'crash_date' and 'crash_time' into a single 'crash_datetime' column
collisions['crash_datetime'] = pd.to_datetime(collisions['crash_date'].astype(str) + ' ' + collisions['crash_time'].astype(str))

# Drop the original 'crash_date' and 'crash_time' columns if no longer needed
collisions = collisions.drop(columns=['crash_date', 'crash_time'])

# Reorder columns to place 'crash_datetime' first
cols = ['crash_datetime'] + [col for col in collisions.columns if col != 'crash_datetime']
collisions = collisions[cols]

# Sort by the new 'crash_datetime' column
collisions = collisions.sort_values(by='crash_datetime')

# Create a new column 'pickup_time_15min' by rounding pickup times to the nearest 15 minutes
collisions['crash_time_15min'] = collisions['crash_datetime'].dt.floor('15T')

collisions = collisions[["crash_datetime", "crash_time_15min", "latitude", "longitude", "number_of_persons_injured", "number_of_persons_killed"]]

collisions['was_crash'] = True

# Apply the vectorized function to the DataFrame columns
collisions['distance_to_empire'] = haversine_vectorized(collisions['latitude'], collisions['longitude'])

# Filter for pickups within 1000 meters (1 km) from the Empire State Building
df_filtered_1000 = collisions[collisions['distance_to_empire'] <= 1000].copy() 
df_filtered_2000A = collisions[collisions['distance_to_empire'] >= 2000].copy()  

# Option 1 --------------------------------------------------------------------------------------------------
# Group by the 15-minute intervals and count the number of pickups
# crashes_counts_1000 = df_filtered_1000.groupby('crash_time_15min').size().reset_index(name='crash_count')
# crashes_counts_2000A = df_filtered_2000A.groupby('crash_time_15min').size().reset_index(name='crash_count')

# Option 2 --------------------------------------------------------------------------------------------------
# Group by the 15-minute intervals and sum the total number of injured and killed

# Initialize the 15-minute time range from April 1, 2014, to September 30, 2014
time_range = pd.date_range(start='2014-04-01 00:00:00', end='2014-09-30 23:59:59', freq='15T')

# Create a DataFrame for the 15-minute intervals
time_df = pd.DataFrame(time_range, columns=['crash_time_15min'])

# Group by the 15-minute intervals, sum the total number of injured and killed, and count the number of rows
crashes_sums_1000 = df_filtered_1000.groupby('crash_time_15min').agg({
    'number_of_persons_injured': 'sum',
    'number_of_persons_killed': 'sum',
    'crash_time_15min': 'size'  # Counting rows
}).rename(columns={'crash_time_15min': 'number_of_crashes'}).reset_index()

crashes_sums_2000A = df_filtered_2000A.groupby('crash_time_15min').agg({
    'number_of_persons_injured': 'sum',
    'number_of_persons_killed': 'sum',
    'crash_time_15min': 'size'  # Counting rows
}).rename(columns={'crash_time_15min': 'number_of_crashes'}).reset_index()

# Merge with the full time range to ensure all 15-minute intervals are represented
final_df_1000 = pd.merge(time_df, crashes_sums_1000, on='crash_time_15min', how='left').fillna(0)
final_df_2000A = pd.merge(time_df, crashes_sums_2000A, on='crash_time_15min', how='left').fillna(0)

# Save to CSV
output_file_1000 = os.path.join(script_dir, 'crashes_sums_1000m.csv')
final_df_1000.to_csv(output_file_1000, index=False)

output_file_2000A = os.path.join(script_dir, 'crashes_sums_2000Am.csv')
final_df_2000A.to_csv(output_file_2000A, index=False)

output_file_raw = os.path.join(script_dir, 'crashes_raw.csv')
collisions.to_csv(output_file_raw, index=False)

print(f"Files saved:\n{output_file_1000}\n{output_file_2000A}\n{output_file_raw}")