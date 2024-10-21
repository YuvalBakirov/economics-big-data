library(dplyr)
library(lubridate)
library(geosphere)
library(rstudioapi)

# Get the directory of the currently open script
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)

# Define the file path for the dataset
file_path <- file.path(script_dir, "../../data/raw/Motor_Vehicle_Collisions_Crashes_Data.csv")

# Load the dataset
collisions <- read.csv(file_path)

# Select and rename columns
collisions <- collisions %>%
  select(CRASH.DATE, CRASH.TIME, LATITUDE, LONGITUDE, 
         NUMBER.OF.PERSONS.INJURED, NUMBER.OF.PERSONS.KILLED, 
         NUMBER.OF.PEDESTRIANS.INJURED, NUMBER.OF.PEDESTRIANS.KILLED,
         NUMBER.OF.CYCLIST.INJURED, NUMBER.OF.CYCLIST.KILLED,
         NUMBER.OF.MOTORIST.INJURED, NUMBER.OF.MOTORIST.KILLED) %>%
  rename(
    crash_date = CRASH.DATE,
    crash_time = CRASH.TIME,
    latitude = LATITUDE,
    longitude = LONGITUDE,
    number_of_persons_injured = NUMBER.OF.PERSONS.INJURED,
    number_of_persons_killed = NUMBER.OF.PERSONS.KILLED,
    number_of_pedestrians_injured = NUMBER.OF.PEDESTRIANS.INJURED,
    number_of_pedestrians_killed = NUMBER.OF.PEDESTRIANS.KILLED,
    number_of_cyclist_injured = NUMBER.OF.CYCLIST.INJURED,
    number_of_cyclist_killed = NUMBER.OF.CYCLIST.KILLED,
    number_of_motorist_injured = NUMBER.OF.MOTORIST.INJURED,
    number_of_motorist_killed = NUMBER.OF.MOTORIST.KILLED
  )

# Drop rows where latitude or longitude is missing
collisions <- collisions %>% drop_na(latitude, longitude)

# Combine crash_date and crash_time into one datetime column
collisions <- collisions %>%
  mutate(crash_datetime = as.POSIXct(paste(crash_date, crash_time), format = "%m/%d/%Y %H:%M"))

# Remove the crash_date and crash_time columns
collisions <- collisions %>% select(-crash_date, -crash_time)

# Sort the data by crash_datetime
collisions <- collisions %>% arrange(crash_datetime)

# Create a new column 'crash_time_15min' by rounding to the nearest 15 minutes
collisions <- collisions %>%
  mutate(crash_time_15min = floor_date(crash_datetime, "15 minutes"))

collisions$was_crash <- TRUE

# Reorder to have crash_datetime and crash_time_15min first
collisions <- collisions %>% select(crash_datetime, crash_time_15min, everything())

# Calculate distance from the Empire State Building (geodesic distance)
empire_state_coords <- c(-73.985428, 40.748817)
collisions <- collisions %>%
  mutate(distance_to_empire = distHaversine(cbind(longitude, latitude), empire_state_coords))

# Filter for crashes within 1000 meters and beyond 2000 meters from the Empire State Building
df_filtered_1000 <- collisions %>% filter(distance_to_empire <= 1000)
df_filtered_2000A <- collisions %>% filter(distance_to_empire >= 2000)

# Initialize the 15-minute time range from April 1, 2014, to September 30, 2014
time_range <- seq.POSIXt(from = as.POSIXct('2014-04-01 00:00:00'), to = as.POSIXct('2014-09-30 23:59:59'), by = '15 min')
time_df <- data.frame(crash_time_15min = time_range)

# Summing the total number of injured, killed, and counting crashes for the 1000m filtered data
crashes_sums_1000 <- df_filtered_1000 %>%
  group_by(crash_time_15min) %>%
  summarise(
    number_of_persons_injured = sum(number_of_persons_injured, na.rm = TRUE),
    number_of_persons_killed = sum(number_of_persons_killed, na.rm = TRUE),
    number_of_crashes = n()
  )

# Summing the total number of injured, killed, and counting crashes for the 2000m filtered data
crashes_sums_2000A <- df_filtered_2000A %>%
  group_by(crash_time_15min) %>%
  summarise(
    number_of_persons_injured = sum(number_of_persons_injured, na.rm = TRUE),
    number_of_persons_killed = sum(number_of_persons_killed, na.rm = TRUE),
    number_of_crashes = n()
  )

# Merge with the full time range
final_df_1000 <- time_df %>%
  left_join(crashes_sums_1000, by = "crash_time_15min") %>%
  mutate(across(everything(), ~replace_na(.x, 0)))

final_df_2000A <- time_df %>%
  left_join(crashes_sums_2000A, by = "crash_time_15min") %>%
  mutate(across(everything(), ~replace_na(.x, 0)))

# Save the resulting DataFrames to CSV
folder_path = "../../data/processed/"
write.csv(final_df_1000, file.path(script_dir, folder_path, 'crashes_sums_1000m.csv'), row.names = FALSE)
write.csv(final_df_2000A, file.path(script_dir, folder_path, 'crashes_sums_2000Am.csv'), row.names = FALSE)
write.csv(collisions, file.path(script_dir, folder_path, 'crashes.csv'), row.names = FALSE)

# Print confirmation of saved files

cat("Files saved:\n",
    file.path(script_dir, folder_path, 'crashes_sums_1000m.csv'), "\n",
    file.path(script_dir, folder_path, 'crashes_sums_2000Am.csv'), "\n",
    file.path(script_dir, folder_path, 'crashes.csv'), "\n")

