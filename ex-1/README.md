# Big Data Analysis Project - Airbnb Boston Listings

## Project Overview

This project provides an in-depth analysis of Airbnb listings in Boston, focusing on property types, pricing strategies, occupancy rates, and guest satisfaction. The goal is to offer actionable insights and recommendations to improve Airbnb's revenue and optimize host performance. The analysis was performed using R, employing key metrics such as **RevPAN** (Revenue Per Available Night) to assess revenue efficiency and guide pricing adjustments.

---

## Table of Contents
- [Technologies Used](#technologies-used)
- [Dataset Overview](#dataset-overview)
- [Descriptive Statistics](#descriptive-statistics)
- [Key Metrics](#key-metrics)
- [Neighborhood Analysis](#neighborhood-analysis)
- [Outlier Detection](#outlier-detection)
- [Business Recommendations](#business-recommendations)
- [Conclusion](#conclusion)

---

## Technologies Used
- **R**: The primary programming language used for data analysis.
- **Libraries**: 
  - `dplyr` for data manipulation.
  - `ggplot2` for data visualization.
  - `tidyverse` for data management.

---

## Dataset Overview

The dataset used for analysis includes:
1. **listings_clean**: Information about property listings, such as the number of beds, type of property, and initial pricing.
2. **calendar_clean**: Daily records of property availability and pricing, including whether a property was booked or available.

Assumptions:
- **available_category = 0**: Property offered but not booked.
- **available_category = 1**: Property offered and booked.
- **Prices**: The prices listed in the `listings_clean` table are assumed to be the initial nightly price when the property was first listed, while the `calendar_clean` table reflects actual nightly prices paid.

---

## Descriptive Statistics

### Distribution of Beds
- **Key Finding**: Most properties have one bed. Interestingly, the data does not distinguish between different types of beds (single vs. double), which could skew guest capacity estimates and impact pricing.
  
### Distribution of Property Types
- **Key Finding**: Apartments dominate the listings (72%), with a limited presence of unique property types such as boats and guesthouses. This may limit diversity, potentially deterring travelers seeking unique accommodations.
  
### Histogram of Property Ratings
- **Key Finding**: Most properties have high ratings, primarily between 90 and 100. However, the possibility of grade inflation exists. Addressing the causes behind lower ratings could further improve the customer experience.

### Correlation Analysis: Review Scores and Overall Ratings
- **Key Finding**: There is a strong positive correlation between cleanliness, accuracy, communication, and check-in experience with the overall rating score. Cleanliness has the highest impact, suggesting that improving cleanliness can significantly boost property ratings.

### Average Price vs. Number of Beds
- **Key Finding**: Larger properties generally command higher prices, but pricing is not directly proportional to the number of beds. For example, properties with zero beds (likely studio apartments) have a higher average price than those with one bed, indicating the influence of other factors such as location or property type.

---

## Key Metrics

### Annual Growth of New Listings
- **Metric Definition**: Annual Growth = New Listings in the current year.
- **Finding**: The platform's property supply has grown each year. However, the analysis notes a limitation in confirming whether these new properties were successfully booked by customers, especially for data pre-2016.

### RevPAN (Revenue Per Available Night)
- **Metric Definition**: 
  - RevPAN = ADR (Average Daily Rate) × Occupancy Rate.
  - ADR = Total Listing Revenue / Nights Booked.
  - Occupancy Rate = Nights Booked / Total Nights Available.
- **Finding**: RevPAN declined at the end of 2016 but started recovering in mid-2017. The analysis suggests adjusting prices based on RevPAN to improve revenue potential during low-occupancy periods.

---

## Neighborhood Analysis

### Monthly Neighborhood RevPAN
- **Metric Definition**: 
  - Monthly Neighborhood RevPAN = Total Revenue in Neighborhood / Total Available Nights in Neighborhood.
- **Finding**: Some neighborhoods perform better than others, with a significant variation in RevPAN. Airbnb should explore why certain areas underperform and consider adjusting pricing strategies in these neighborhoods to attract more guests.

---

## Outlier Detection

### Time Range with Unusual Behavior
- **Key Finding**: During the Boston Marathon in April 2017, occupancy rates dropped while prices spiked. This suggests that hosts raised prices in anticipation of increased demand, but the high prices discouraged bookings. Adding a Boolean variable (`Event`) to mark special events could improve future analyses.

### Bed and Price Anomalies
- **Key Finding**: Some properties had unusual values, such as 0 beds or 16 beds. These values were addressed by reclassifying studio apartments (0 beds) to have 1 bed and converting NA values to the average bed count. Outliers in price data (e.g., properties priced over $1000) were retained, as there was demand for high-end properties.

---

## Business Recommendations

1. **Increase Property Diversity**: Encourage hosts to offer a wider variety of properties, such as boats or guesthouses, to cater to travelers seeking unique experiences. The current dominance of apartments may limit appeal.
   
2. **RevPAN-Based Pricing Alerts**: Implement a system that alerts hosts to adjust prices based on RevPAN trends. Hosts with low occupancy should lower prices to attract more bookings, while those with high occupancy could increase prices to maximize revenue.

3. **Neighborhood Strategy**: Airbnb should focus on high-performing neighborhoods with high RevPAN and occupancy rates. Conversely, in low-performing neighborhoods, Airbnb can recommend lowering prices or promoting listings more aggressively to boost demand.

4. **Event-Driven Pricing**: During major events like the Boston Marathon, Airbnb should advise hosts on how to balance price increases with occupancy to avoid discouraging bookings with excessive pricing.

--- 

## Conclusion

This project provides valuable insights into how Airbnb hosts can optimize their pricing strategies using metrics like RevPAN. By focusing on property diversity, understanding neighborhood performance, and adjusting prices based on event-driven demand, Airbnb can improve revenue while maintaining guest satisfaction. The analysis highlights the importance of data-driven decision-making for both hosts and the platform.
