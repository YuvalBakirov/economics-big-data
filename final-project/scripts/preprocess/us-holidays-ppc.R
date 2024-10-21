library(dplyr)
library(lubridate)
library(rstudioapi)

# Get the directory of the currently open script
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)

# Define the file path for the dataset
file_path <- file.path(script_dir, "../../data/raw/US Federal Pay and Leave Holidays 2004 to 2100.csv")

# Load the dataset
us_federal_holidays <- read.csv(file_path)

# Filter only year 2014
us_2014_federal_holidays <- us_federal_holidays %>%
  filter(Year == 2014) %>%
  select(Title, Date, Year, Month, Day)

# Fix the 'Date' column, making sure to combine 'Year', 'Month', and 'Day' correctly
us_2014_federal_holidays <- us_2014_federal_holidays %>%
  mutate(
    Title = as.character(Title),  # Convert 'Title' to string
    Date = as.Date(paste(Year, Month, Day, sep = "-"), format = "%Y-%m-%d"),  # Fix 'Date' by combining Year, Month, and Day
    Year = as.integer(Year),  # Convert 'Year' to integer
    Month = as.integer(Month),  # Convert 'Month' to integer
    Day = as.integer(Day)  # Convert 'Day' to integer
  )

# Define the output file path
folder_path <- "../../data/processed/"
output_file <- file.path(script_dir, folder_path, "US_2014_federal_holidays.csv")

# Save the result to a CSV file
write.csv(us_2014_federal_holidays, output_file, row.names = FALSE)

cat("File saved:", output_file, "\n")
