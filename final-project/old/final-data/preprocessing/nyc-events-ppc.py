import os
import pandas as pd

# Get current working directory
script_dir = os.getcwd()
file_path = os.path.join(script_dir, "unprocessed-data/NYC_Permitted_Event_Information_Data.csv")
events_df = pd.read_csv(file_path)

# Convert 'Start Date/Time' and 'End Date/Time' to datetime
events_df['Start Date/Time'] = pd.to_datetime(events_df['Start Date/Time'])
events_df['End Date/Time'] = pd.to_datetime(events_df['End Date/Time'])

# Filter events to only include those before October 1, 2014
cutoff_date = pd.to_datetime('2014-10-01')
events_df = events_df[events_df['Start Date/Time'] < cutoff_date]

# Sort the DataFrame by 'Start Date/Time'
events_df = events_df.sort_values(by='Start Date/Time')

# Create a new DataFrame to hold counts for each 15-minute interval
time_range = pd.date_range(events_df['Start Date/Time'].min(), events_df['End Date/Time'].max(), freq='15T')
counts_df = pd.DataFrame(time_range, columns=['time_interval'])
counts_df['event_count'] = 0

# For each event, mark the 15-minute intervals in which the event is active
for index, row in events_df.iterrows():
    event_range = pd.date_range(row['Start Date/Time'], row['End Date/Time'], freq='15T')
    counts_df.loc[counts_df['time_interval'].isin(event_range), 'event_count'] += 1

# Ensure the final counts DataFrame doesn't go beyond the cutoff date
counts_df = counts_df[counts_df['time_interval'] < cutoff_date]

# Save the results to a CSV file
output_file = os.path.join(script_dir, 'nyc_event_counts.csv')
counts_df.to_csv(output_file, index=False)

print(f"Event counts saved to {output_file}")
