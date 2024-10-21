library(dplyr)
library(lubridate)
library(geosphere)
library(rstudioapi)

# Get the directory of the currently open script
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)

# Define the file path for the dataset
file_path <- file.path(script_dir, "../../data/raw/NYPD_Shooting_Incident_Data.csv")

# Load the dataset
shootings_df <- read.csv(file_path)

# Selecting the required columns
shootings_df <- shootings_df %>%
  select(OCCUR_DATE, OCCUR_TIME, STATISTICAL_MURDER_FLAG, Latitude, Longitude) %>%
  rename(
    occur_date = OCCUR_DATE,
    occur_time = OCCUR_TIME,
    statistical_murder = STATISTICAL_MURDER_FLAG,
    latitude = Latitude,
    longitude = Longitude
  )

# Combine 'occur_date' and 'occur_time' into a single datetime column
shootings_df <- shootings_df %>%
  mutate(occur_datetime = as.POSIXct(paste(occur_date, occur_time), format = "%m/%d/%Y %H:%M:%S"))

# Drop the original 'occur_date' and 'occur_time' columns
shootings_df <- shootings_df %>%
  select(occur_datetime, everything(), -occur_date, -occur_time)

# Sort the DataFrame by 'occur_datetime'
shootings_df <- shootings_df %>%
  arrange(occur_datetime)

# Create a new column 'shooting_time_15min' by rounding to the nearest 15 minutes
shootings_df <- shootings_df %>%
  mutate(shooting_time_15min = floor_date(occur_datetime, unit = "15 minutes"))

shootings_df <- shootings_df %>%
  select(occur_datetime, shooting_time_15min, statistical_murder, latitude, longitude)

# Apply the Haversine formula to calculate distance from Empire State Building
empire_state_coords <- c(-73.985428, 40.748817)

haversine_vectorized <- function(lat, lon) {
  distHaversine(cbind(lon, lat), empire_state_coords)
}

shootings_df <- shootings_df %>%
  mutate(distance_to_empire = haversine_vectorized(latitude, longitude))

# Filter for shootings within 1000 meters and beyond 2000 meters from Empire State Building
shootings_df_1000 <- shootings_df %>% filter(distance_to_empire <= 1000)
shootings_df_2000A <- shootings_df %>% filter(distance_to_empire >= 2000)

shootings_df_1000_boolean <- shootings_df_1000 %>%
  select(shooting_time_15min)

# Create a 15-minute time range from April 1, 2014, to September 30, 2014
time_range <- seq.POSIXt(from = as.POSIXct("2014-04-01 00:00:00"), to = as.POSIXct("2014-09-30 23:59:59"), by = "15 min")

# Create a DataFrame for the 15-minute intervals
time_df <- data.frame(shooting_time_15min = time_range)

# Group shootings by the 15-minute intervals and count the number of occurrences
shootings_grouped <- shootings_df_2000A %>%
  group_by(shooting_time_15min) %>%
  summarise(murder_count = n())

# Merge the full timeline with the grouped shooting data
final_shootings_2000A_df <- time_df %>%
  left_join(shootings_grouped, by = "shooting_time_15min") %>%
  mutate(murder_count = ifelse(is.na(murder_count), 0, murder_count))

final_shootings_2000A_boolean <- final_shootings_2000A_df %>%
  mutate(was_shooting = murder_count > 0) %>%
  select(shooting_time_15min, was_shooting)

# Save to CSV
folder_path <- "../../data/processed/"

write.csv(shootings_df, file.path(script_dir, folder_path, "shootings.csv"), row.names = FALSE)
write.csv(shootings_df_1000_boolean, file.path(script_dir, folder_path, "shootings_1000m_boolean.csv"), row.names = FALSE)
write.csv(final_shootings_2000A_boolean, file.path(script_dir, folder_path, "shootings_2000Am_boolean.csv"), row.names = FALSE)
write.csv(final_shootings_2000A_df, file.path(script_dir, folder_path, "shootings_2000Am.csv"), row.names = FALSE)

# Print confirmation of saved files
cat("Files saved:\n",
    file.path(script_dir, folder_path, "shootings.csv"), "\n",
    file.path(script_dir, folder_path, "shootings_1000m_boolean.csv"), "\n",
    file.path(script_dir, folder_path, "shootings_2000Am_boolean.csv"), "\n",
    file.path(script_dir, folder_path, "shootings_2000Am.csv"), "\n")
