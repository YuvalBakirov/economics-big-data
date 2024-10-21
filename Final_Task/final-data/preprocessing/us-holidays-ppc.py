import pandas as pd
import os

# Get current working directory
script_dir = os.getcwd()
file_path = os.path.join(script_dir, "unprocessed-data/US Federal Pay and Leave Holidays 2004 to 2100.csv")
us_federal_holidays = pd.read_csv(file_path)

# Filter only year 2014
us_2014_federal_holidays = us_federal_holidays[us_federal_holidays["Year"] == 2014]
us_2014_federal_holidays = us_2014_federal_holidays[["Title", "Date", "Year", "Month", "Day"]]

# Convert specific columns to desired types
us_2014_federal_holidays['Title'] = us_2014_federal_holidays['Title'].astype(str)  # Convert 'Title' to string
us_2014_federal_holidays['Date'] = pd.to_datetime(us_2014_federal_holidays['Date'])  # Convert 'Date' to datetime
us_2014_federal_holidays['Year'] = us_2014_federal_holidays['Year'].astype(int)  # Convert 'Year' to integer
us_2014_federal_holidays['Month'] = us_2014_federal_holidays['Month'].astype(int)  # Convert 'Month' to integer
us_2014_federal_holidays['Day'] = us_2014_federal_holidays['Day'].astype(int)  # Convert 'Day' to integer

output_file = os.path.join(script_dir, 'US_2014_federal_holidays.csv')
us_2014_federal_holidays.to_csv(output_file, index=False)