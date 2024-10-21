library(dplyr)
library(lubridate)
library(rstudioapi)

# Get the directory of the currently open script
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)

# Define the file path for the dataset
file_path <- file.path(script_dir, "../../data/raw/NYC_Permitted_Event_Information_Data.csv")

# Load the dataset
events_df <- read.csv(file_path)

# Convert 'Start.Date.Time' and 'End.Date.Time' to POSIXct datetime format
events_df$Start.Date.Time <- as.POSIXct(events_df$Start.Date.Time, format = "%m/%d/%Y %H:%M")
events_df$End.Date.Time <- as.POSIXct(events_df$End.Date.Time, format = "%m/%d/%Y %H:%M")

# Filter events to only include those before October 1, 2014
cutoff_date <- as.POSIXct('2014-10-01 00:00:00')
events_df <- events_df %>% filter(Start.Date.Time < cutoff_date)

# Remove rows where the 'End.Date.Time' is earlier than 'Start.Date.Time'
events_df <- events_df %>% filter(End.Date.Time >= Start.Date.Time)

# Sort the DataFrame by 'Start.Date.Time'
events_df <- events_df %>% arrange(Start.Date.Time)

# Create a new DataFrame to hold counts for each 15-minute interval
time_range <- seq.POSIXt(from = min(events_df$Start.Date.Time), 
                         to = max(events_df$End.Date.Time), by = "15 min")
counts_df <- data.frame(time_interval = time_range, event_count = 0)

# Use 'findInterval' to locate the 15-minute bins for each event's start and end time
for (i in 1:nrow(events_df)) {
  start_idx <- findInterval(events_df$Start.Date.Time[i], time_range)
  end_idx <- findInterval(events_df$End.Date.Time[i], time_range)
  
  # Increment the count for each 15-minute interval the event spans
  counts_df$event_count[start_idx:end_idx] <- counts_df$event_count[start_idx:end_idx] + 1
}

# Ensure the final counts DataFrame doesn't go beyond the cutoff date
counts_df <- counts_df %>% filter(time_interval < cutoff_date)

# Save the results to a CSV file
folder_path <- "../../data/processed/"
output_file <- file.path(script_dir, folder_path, "nyc_event_counts.csv")
write.csv(counts_df, output_file, row.names = FALSE)

cat("Event counts saved to", output_file)
