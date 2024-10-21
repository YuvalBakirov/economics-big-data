library(dplyr)
library(lubridate)
library(geosphere)
library(tidyr)

# Get the directory of the currently open script
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)

# Define the file path for the dataset
file_path <- file.path(script_dir, "../../data/raw/NYPD_Arrests_Data.csv")

# Load the dataset
arrests_df <- read.csv(file_path)

# Select and rename columns
arrests_df <- arrests_df %>%
  select(ARREST_DATE, LAW_CAT_CD, Latitude, Longitude) %>%
  rename(
    arrest_date = ARREST_DATE,
    law_category = LAW_CAT_CD,
    latitude = Latitude,
    longitude = Longitude
  )

# Filter only Felony and Misdemeanor
arrests_df <- arrests_df %>% filter(law_category %in% c('F', 'M'))

# Calculate distance to Empire State Building
empire_state_coords <- c(-73.985428, 40.748817)
arrests_df <- arrests_df %>%
  mutate(
    distance_to_empire = distHaversine(cbind(longitude, latitude), empire_state_coords)
  )

# Filter arrests within 1000 meters and beyond 2000 meters from Empire State Building
arrests_df_1000 <- arrests_df %>% filter(distance_to_empire <= 1000)
arrests_df_2000A <- arrests_df %>% filter(distance_to_empire >= 2000)

# Create date range from April 1, 2014 to September 30, 2014
time_range <- seq.Date(as.Date('2014-04-01'), as.Date('2014-09-30'), by = 'day')
time_df <- data.frame(arrest_date = time_range)

# Assuming the format of the date is 'MM/DD/YYYY'
arrests_df_1000$arrest_date <- as.Date(arrests_df_1000$arrest_date, format = "%m/%d/%Y")
arrests_df_2000A$arrest_date <- as.Date(arrests_df_2000A$arrest_date, format = "%m/%d/%Y")


# Group by 'arrest_date' and count felony and misdemeanor arrests
# For arrests within 1000 meters
felony_grouped_1000 <- arrests_df_1000 %>%
  filter(law_category == 'F') %>%
  group_by(arrest_date) %>%
  summarise(felony_count = n())

misdemeanor_grouped_1000 <- arrests_df_1000 %>%
  filter(law_category == 'M') %>%
  group_by(arrest_date) %>%
  summarise(misdemeanor_count = n())

# For arrests beyond 2000 meters
felony_grouped_2000A <- arrests_df_2000A %>%
  filter(law_category == 'F') %>%
  group_by(arrest_date) %>%
  summarise(felony_count = n())

misdemeanor_grouped_2000A <- arrests_df_2000A %>%
  filter(law_category == 'M') %>%
  group_by(arrest_date) %>%
  summarise(misdemeanor_count = n())

# Merge felony and misdemeanor counts with the full timeline
final_arrests_df_1000 <- time_df %>%
  left_join(felony_grouped_1000, by = "arrest_date") %>%
  left_join(misdemeanor_grouped_1000, by = "arrest_date") %>%
  mutate(
    felony_count = replace_na(felony_count, 0),
    misdemeanor_count = replace_na(misdemeanor_count, 0),
    total_arrests = felony_count + misdemeanor_count
  )

final_arrests_df_2000A <- time_df %>%
  left_join(felony_grouped_2000A, by = "arrest_date") %>%
  left_join(misdemeanor_grouped_2000A, by = "arrest_date") %>%
  mutate(
    felony_count = replace_na(felony_count, 0),
    misdemeanor_count = replace_na(misdemeanor_count, 0),
    total_arrests = felony_count + misdemeanor_count
  )


# Sort by arrest_date
final_arrests_df_1000 <- final_arrests_df_1000 %>% arrange(arrest_date, format = "%m/%d/%Y")
final_arrests_df_2000A <- final_arrests_df_2000A %>% arrange(arrest_date, format = "%m/%d/%Y")
arrests_df <- arrests_df %>% arrange(arrest_date, format = "%m/%d/%Y")

# Write results to CSV files
folder_path = "../../data/processed/"
write.csv(final_arrests_df_1000, file.path(script_dir, folder_path,  "arrests_F_and_M_1000m.csv"), row.names = FALSE)
write.csv(final_arrests_df_2000A, file.path(script_dir, folder_path, "arrests_F_and_M_2000Am.csv"), row.names = FALSE)
write.csv(arrests_df, file.path(script_dir, folder_path, "arrests_F_and_M.csv"), row.names = FALSE)

print("Files saved successfully.")
