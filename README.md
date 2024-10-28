# Big Data 

<b>About</b><br>
We were required to analyze a dataset by Uber. To predict the demand for Uber rides within 1000-meters radius distance from Empire State Building (lat-lng: 40.7484, -73.985), for each 15 minutes interval, during 10 to 30 of September 2014.<br> Our predictions will be evaluated based on a list of time intervals, when we do not have access to the real number of Uber pickups that have already occurred during those times.<br>

For this project we have 2 different datasets, and one test_set that we will use 2 times, once with each train dataset:<br>
train_sets - This is the fundamental data you are going to analyze and use for modeling. This file contains raw data on over 3.5 million Uber pickups in New York City from 1st April to 9 of September 2014. <br>
a version with all the raw uber pickups - train_raw_data.csv.<br>
a version with all the raw uber pickups that are not in the radios of 2000 meters from the Empire State Building - train_raw_data_dists_more_then_2000.csv.
<br>
test_set - contains aggregated data of 10 of September to the end of September. We keep the data in time intervals of 15 minutes, and keep only the hour of the day above 18:00 to 00:00.<br>
We will make our predictions, based on the model we created, and fill the ‘number_of_pickups’ for each time interval.
