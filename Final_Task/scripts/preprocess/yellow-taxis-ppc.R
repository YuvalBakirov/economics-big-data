library(dplyr)
library(lubridate)
library(geosphere)
library(arrow)

# Constants for the Empire State Building coordinates
empire_state_coords <- c(-73.985428, 40.748817)

# Haversine formula to calculate distances in meters
haversine_vectorized <- function(lat, lon) {
  geosphere::distHaversine(matrix(c(lon, lat), ncol = 2), empire_state_coords)
}

# Get the current script directory
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)

# Initialize paths and year
year <- 2014

# Load the zone centroids CSV file
zone_centroids_file <- file.path(script_dir, '../../data/raw/yellow-taxis', 'taxi-zones', 'zone_centroids.csv')
zone_centroids_df <- read.csv(zone_centroids_file)

# List to hold the pickup_counts for each month
pickup_counts_1000_list <- list()
pickup_counts_2000A_list <- list()

# Loop through the months and process each parquet file individually
for (month in c('04', '05', '06', '07', '08', '09')) {
  # Load the parquet file for the current month
  file_path <- file.path(script_dir, sprintf('../../data/raw/yellow-taxis/yellow_tripdata_%d-%s.parquet', year, month))
  df <- read_parquet(file_path)
  
  # Select only the required columns
  df <- df %>%
    select(tpep_pickup_datetime, tpep_dropoff_datetime, trip_distance, PULocationID, DOLocationID, total_amount)
  
  # Merge centroids for Pickup Location (PULocationID)
  df <- df %>%
    left_join(zone_centroids_df %>% select(LocationID, latitude, longitude), by = c("PULocationID" = "LocationID")) %>%
    rename(pickup_latitude = latitude, pickup_longitude = longitude)
  
  # Merge centroids for Drop-off Location (DOLocationID)
  df <- df %>%
    left_join(zone_centroids_df %>% select(LocationID, latitude, longitude), by = c("DOLocationID" = "LocationID")) %>%
    rename(dropoff_latitude = latitude, dropoff_longitude = longitude)
  
  # Calculate distance between pickup location and Empire State Building
  df$distance_to_empire <- haversine_vectorized(df$pickup_latitude, df$pickup_longitude)
  
  # Filter for pickups within 1000 meters (1 km) from the Empire State Building
  df_filtered_1000 <- df %>% filter(distance_to_empire <= 1000)
  df_filtered_2000A <- df %>% filter(distance_to_empire >= 2000)
  
  # Create a new column 'pickup_time_15min' by rounding pickup times to the nearest 15 minutes
  df_filtered_1000 <- df_filtered_1000 %>%
    mutate(pickup_time_15min = floor_date(tpep_pickup_datetime, "15 minutes"))
  
  df_filtered_2000A <- df_filtered_2000A %>%
    mutate(pickup_time_15min = floor_date(tpep_pickup_datetime, "15 minutes"))
  
  # Group by the 15-minute intervals and count the number of pickups
  pickup_counts_1000 <- df_filtered_1000 %>%
    group_by(pickup_time_15min) %>%
    summarise(pickup_count = n())
  
  pickup_counts_2000A <- df_filtered_2000A %>%
    group_by(pickup_time_15min) %>%
    summarise(pickup_count = n())
  
  # Append the current month's pickup_counts to the list
  pickup_counts_1000_list[[month]] <- pickup_counts_1000
  pickup_counts_2000A_list[[month]] <- pickup_counts_2000A
}

# Concatenate all monthly pickup_counts DataFrames into one
final_pickup_counts_1000_df <- bind_rows(pickup_counts_1000_list)
final_pickup_counts_2000A_df <- bind_rows(pickup_counts_2000A_list)

# Save the merged dataframe as a CSV file
folder_path <- "../../data/processed/"
output_file_1000 <- file.path(script_dir, folder_path, 'yellow_taxis_pickup_counts_1000m.csv')
write.csv(final_pickup_counts_1000_df, output_file_1000, row.names = FALSE)

output_file_2000A <- file.path(script_dir, folder_path, 'yellow_taxis_pickup_counts_2000Am.csv')
write.csv(final_pickup_counts_2000A_df, output_file_2000A, row.names = FALSE)

cat("Merged csv files saved to:", output_file_1000, "and", output_file_2000A)
