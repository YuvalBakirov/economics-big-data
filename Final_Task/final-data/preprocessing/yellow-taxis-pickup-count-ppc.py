import os
import pandas as pd
import numpy as np
from geopy.distance import geodesic

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
script_dir = os.path.dirname(__file__)

# Initialize paths and year
year = 2014

# Load the zone centroids CSV file
zone_centroids_file = 'taxi-zones/zone_centroids.csv'
zone_centroids_df = pd.read_csv(zone_centroids_file)

# List to hold the pickup_counts for each month
pickup_counts_1000_list = []
pickup_counts_2000A_list = []

# Loop through the months and process each parquet file individually
for month in ['04', '05', '06', '07', '08', '09']:
    # Load the parquet file for the current month
    file_path = os.path.join(script_dir, f'data/yellow_tripdata_{year}-{month}.parquet')
    df = pd.read_parquet(file_path)
    
    # Select only the required columns
    df = df[["tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance", "PULocationID", "DOLocationID", "total_amount"]]
    
    # Merge centroids for Pickup Location (PULocationID)
    df = df.merge(zone_centroids_df[['LocationID', 'latitude', 'longitude']],
                  left_on='PULocationID', right_on='LocationID', suffixes=('', '_pu'))
    df = df.rename(columns={'latitude': 'pickup_latitude', 'longitude': 'pickup_longitude'})
    df = df.drop(columns=['LocationID'])
    
    # Merge centroids for Drop-off Location (DOLocationID)
    df = df.merge(zone_centroids_df[['LocationID', 'latitude', 'longitude']],
                  left_on='DOLocationID', right_on='LocationID', suffixes=('', '_do'))
    df = df.rename(columns={'latitude': 'dropoff_latitude', 'longitude': 'dropoff_longitude'})
    df = df.drop(columns=['LocationID'])
    
    # Calculate distance between pickup location and Empire State Building
    df['distance_to_empire'] = haversine_vectorized(df['pickup_latitude'], df['pickup_longitude'])
    
    # Filter for pickups within 1000 meters (1 km) from the Empire State Building
    df_filtered_1000 = df[df['distance_to_empire'] <= 1000].copy() 
    df_filtered_2000A = df[df['distance_to_empire'] >= 2000].copy()  
    
    # Create a new column 'pickup_time_15min' by rounding pickup times to the nearest 15 minutes
    df_filtered_1000.loc[:, 'pickup_time_15min'] = df_filtered_1000['tpep_pickup_datetime'].dt.floor('15T')
    df_filtered_2000A.loc[:, 'pickup_time_15min'] = df_filtered_2000A['tpep_pickup_datetime'].dt.floor('15T')

    # Group by the 15-minute intervals and count the number of pickups
    pickup_counts_1000 = df_filtered_1000.groupby('pickup_time_15min').size().reset_index(name='pickup_count')
    pickup_counts_2000A = df_filtered_2000A.groupby('pickup_time_15min').size().reset_index(name='pickup_count')
    
    # Append the current month's pickup_counts to the list
    pickup_counts_1000_list.append(pickup_counts_1000)
    pickup_counts_2000A_list.append(pickup_counts_1000)

# Concatenate all monthly pickup_counts DataFrames into one
final_pickup_counts_1000_df = pd.concat(pickup_counts_1000_list, ignore_index=True)
final_pickup_counts_2000A_df = pd.concat(pickup_counts_2000A_list, ignore_index=True)


# Save the merged dataframe as a single parquet file
output_file = os.path.join(script_dir, 'yellow_taxis_pickup_counts_1000m.csv')
final_pickup_counts_1000_df.to_csv(output_file, index=False)

print(f"Merged csv file saved to {output_file}")

output_file = os.path.join(script_dir, 'yellow_taxis_pickup_counts_2000Am.csv')
final_pickup_counts_2000A_df.to_csv(output_file, index=False)

print(f"Merged csv file saved to {output_file}")

