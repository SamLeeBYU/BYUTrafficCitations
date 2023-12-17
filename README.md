# BYU Traffic Citations Research: How Parking Demand Changes in Response to Environmental Factors

## Introduction

Both private and public universities across the United Sates typically have university-specific parking service to enforce university parking regulations due to limited parking space supply. For the purposes of this analysis, we will analyze traffic citation data specific to my univerity, Brigham Young Univeristy.

The purpose behind this analysis will be to see if we can trace out any signal behind the relationship of number of traffic citations given on a particular day and effects in weather and air quality. We hypothesize that when adjusted for confounding effects such as changes in enrollment, seasonality, type of day (whether the day is a holiday), day of week, and trends in time, we can isolate the effect of all influential factors that affect trends in traffic citations given at BYU.

We hypothesize that changes in weather patterns change the incentives of students' choices in transportation choice *as well as* incentives for BYU's parking enforcement task force. We make the assumption that incentives for students' choices in transportation are more inelastic in regards to changes in weather as opposed to incentives for BYU's parking enforcement task force.

If this theory holds then through regression analysis, we hope to show that increase in negative weather effects will significantly decrease the amount of traffic citations distributed on a particular day. 

If incentives for students' choices in transportation are indeed more inelastic than the incentives for parking police at BYU with respect to changes in weather and air quality, then this provides convincing evidence that as trends in weather and air quality become more severe, weather factors become a greater indicator of changes in parking demand than parking citations.

## Essential Scripts
---
###  [analysis.qmd](analysis.qmd)
This quarto file runs through the multilinear regression methods R. This performs multilinear regression with lags, applies lasso regression, and uses Random Forest modeling to model this data. The multilinear regression models are duplicated in *dashboard.py*.

### [AirQuality.ipynb](AirQuality.ipynb)
This data set uses the [Weather Bit](https://www.weatherbit.io/) API to extract local and historical air quality data for Provo, UT. This API only goes back to 2022, so it was further merged with data from *ProvoAQ.csv* created by *PDF Extraction.ipynb*. This notebook then merges the two data sets (the modern air quality data obtained by the API and *ProvoAQ.csv*) into the final usable air quality data set, *AQ.csv*. Additionally this notebook takes *ParkingCitations.csv" and merges it with *WeatherCitations.csv" and "AQ.csv" and produces *citations.csv*

### [dashboard.py](dashboard.py)
This python script creates the visualization dashboard for our final data set, *Provo.csv*, using the Streamlit platform. The dashboard app is hosted live on the Streamlit platflorm: [https://byutrafficcitations.streamlit.app/](https://byutrafficcitations.streamlit.app/).

### [EDA.ipynb](EDA.ipynb)
This notebook combines all the final data sets (*citations.csv*, *weather.json*, *AQ.csv*) and merges them into a final data set (*Provo.csv*) to explore. This notebook summarizes key vizualizations.

### [main.py](main.py)
This is the main script used to scrape the data from BYU's server. I break down this script [here](https://samleebyu.github.io/2023/09/29/selenium-best-practices/). I use Selenium to iterate through all possible combinations of citation numbers and dynamically scrape the data. Outputs scraped data to *ParkingCitations.csv*, although for this repository, I've encrypted the citations for ethical purposes (see *ParkingCitationsEncypted.csv*). The citations in this file aren't real license plate numbers, although the state acronyms are preserved.

### [PDF Extraction.ipynb](main.py)
This notebook uses the [ExtractTable](https://extracttable.com/) API to extract the all the historical air quality data (see *Provo Air Quality Data* directory) from the Provo area [3]. This saves the data set as *ProvoAQ.csv*

### [Weather.ipynb](main.py)
This notebook uses the climate API [2] to obtain historical weather data for Provo. This saves the fetched data to *weather.json*. It also merges the citations with the weather data to create "WeatherCitations.csv"

## Non-essential Scripts
---
### [dashboard.ipynb](dashboard.ipynb)
This notebook explores potential visualizations for the Streamlit dashboard prepared in *dashboard.py*

### [DataAnalysis.ipynb](DataAnalysis.ipynb)
A jupyter notebook used for basic exploratory data analysis on the *ParkingCitations* data set.

### [scraper.ipynb](scraper.ipynb)
A jupyter notebook used for Selenium experimentation. Used as a prototype and a sandbox for *main.py*.


## Essential Data Sets
---
### [AQ.csv](AQ.csv) [3]
This data set consists of the daily maximums for key pollutants: $CO$, $NO_2$, $O_3$, $PM 10$, and $PM 2.5$ for every day going back to January, 1, 2014. This data set was obtained through running *PDF Extraction.ipynb* and *AirQuality.ipynb*--raw data for 2014-2022 is contained in the *Provo Air Quality Data* directory. Images were manually obtained through Utah's Environmental Agency [3], csv files were converted through python. *AirQuality.ipynb* uses the [Weather Bit](https://www.weatherbit.io/) API to extract air quality data for 2023. Ultimately, the year 2023 wasn't used for the analysis as it contained inconsistent unit measurements we used for matching 2014-2022 data with thresholds as defined by the EPA [4].

### [AQI-Criteria.csv](AQI-Criteria.csv) [4]
This defines the thresholds for what qualifies as an unhealthy level for each pollutant as defined by the EPA. Data was obtained manually.

### [citations.csv](citations.csv)
This is the script produced by *AirQuality.ipynb*. This is the merged version of *ParkingCitationsEncrypted.csv*, *WeatherCitations.csv*, and *AQ.csv*. In other words, it a data set that has all the traffic citations of interest matched with corresponding air quality and weather data.

### [citations_cleaned.csv](citations_cleaned.csv)
This data set is produced by *EDA.ipynb*. This notebook cleans the merged data (*citations.csv*): It adds summary statistic columns such as *Month, Day, Year, Week,WeeklyNumFines, DailyNumFines, TotalFineAmount, NumPaidFines, AvgPaidFine*. It also fills in missing pollutant data by taking each missing value and substituting it for the average value of that pollutant for the corresponding month across all years.

### [citations_cleaned_compact.csv](citations_cleaned_compact.csv)
*citations_cleaned.csv* is an hourly record of when each traffic citation was given. Since we only have daily maximums for pollutant and weather factors, I aggregated *citations_cleaned.csv* by the day and reported the sum of the number of traffic tickets and total fine given on that day to yield *citations_cleaned_compact.csv*. If daily maximum levels for environmental factors are, at least somewhat, a consistent estimator for the severity of the weather for that day--that is, if individuals more or less make decisions based on how they *anticipate* how *severe* the weather and their surroundings will be--then I expect that there will exist some signal in regard to the effect of daily maximum levels for environmental factors on changes in daily number of fines and total fines. 

### [enrollment.csv](enrollment.csv) [5] [6]
A data set that was manually curated from BYU enrollment [5] and BYU archive data [6]. This maps out BYU's full-time and part-time enrollment over time, allong with holiday and exam dates regarding the BYU semesters.

### [environment.csv](environment.csv)
This data set is an intermediate file of *EDA.ipynb*. This merges weather data and air quality into one data set for Provo.

### (predictions.csv)[predictions.csv]
This file is produced by *dashboard.py*. This is the saved predicte values from each of the three models used to model the number of traffic citations over time.

### [ParkingCitationsEncrypted.csv](ParkingCitationsEncrypted.csv) [1]
The full data set of BYU parking citations as scraped from the data set. License plate numbers have been encrypted (the encryption script is not included on this repository) so the data set cannot be easily matched with other records across the internet, though state (Residence) records have been maintained. The data set contains citations from June, 2010 to Present (Oct, 2023).

### [Provo.csv](Provo.csv)
The final cleaned data set, merged with all other necessary data sets (including *enrollment.csv*), and will be the data set used for regression analysis. This contains all the air quality and weather factors linked to each day corresponding to the number of traffic citations given on that day and the total fine given on that day.

| Column            | Type         | Description                                     | First 5 Values                        |
|-------------------|--------------|-------------------------------------------------|---------------------------------------|
| DATE              | Date         | Date (yyyy-mm-dd)                                           | 2014-01-06, 2014-01-07, 2014-01-08, 2014-01-09, 2014-01-10 |
| Month             | Numeric      | Month (1-12)                                          | 1, 1, 1, 1, 1                         |
| Day               | Character    | Day (Monday-Sunday)                                             | Monday, Tuesday, Wednesday, Thursday, Friday |
| NA_Correction     | Logical      | Whether the a pollutant value was corrected for NA                                   | FALSE, FALSE, FALSE, FALSE, FALSE     |
| MaxTemp           | Numeric      | Celcius                            | -3.3, 1.1, 0.9, 0.1, 3.1              |
| MinTemp           | Numeric      | Celcius                             | -17.6, -11.6, -2.6, -10.3, -4.1       |
| MeanTemp          | Numeric      | Celcius                               | -10.5, -4.7, -0.5, -4.4, -0.5         |
| RainPrecip        | Numeric      | mm                              | 0, 0, 0, 0, 0                         |
| SnowPrecip        | Numeric      | cm                             | 0, 0.21, 2.66, 3.92, 0.91            |
| Wind              | Numeric      | km/h                                           | 6.8, 5.9, 7.9, 8.9, 7                |
| CO                | Numeric      | PPM 8-hour                                              | 1.8, 1.9, 0.8, 0.7, 1                |
| NO2               | Numeric      | PPB 1-hour                                             | 47, 47, 48, 42, 46                   |
| O3                | Numeric      | PPM 8-hour                                              | 0.022, 0.007, 0.003, 0.021, 0.021    |
| PM10              | Numeric      | Micrograms/Cubic Meter 24-Hour                                            | 47, 66, 53, 46, 38                   |
| PM25              | Numeric      | Micrograms/Cubic Meter                                           | 13.7, 21, 33.9, 18, 7.9              |
| CO_LEVEL          | Character    | EPA Classification                                        | "Good", "Good", "Good", "Good", "Good" |
| NO2_LEVEL         | Character    | EPA Classification                                      | "Good", "Good", "Good", "Good", "Good" |
| O3_LEVEL          | Character    | EPA Classification                                        | "Good", "Good", "Good", "Good", "Good" |
| PM10_LEVEL        | Character    | EPA Classification                                     | "Good", "Moderate", "Good", "Good", "Good" |
| PM25_LEVEL        | Character    | EPA Classification                                    | "Moderate", "Moderate", "Moderate", "Moderate", "Moderate" |
| AQI               | Numeric      | Air Quality Index                               | 54, 70, 97, 63, 43                   |
| AQI_LEVEL         | Character    | AQI Level                                       | "Moderate", "Moderate", "Moderate", "Moderate", "Good" |
| Year              | Numeric      | Year (2014-2022)                                           | 2014, 2014, 2014, 2014, 2014         |
| DailyNumFines     | Numeric      | Daily Number of Fines                           | 23, 52, 13, 3, 16                    |
| NumPaidFines      | Numeric      | Number of Paid Fines                            | 17, 46, 8, 3, 11                     |
| TotalFineAmount   | Numeric      | Total Fine Amount                               | 386, 1238, 216, 350, 221             |
| AvgPaidFine       | Numeric      | Average Paid Fine (Aggregated over the day)                              | 22.7, 26.9, 27, 116.7, 20.1          |
| Fri               | Numeric      | Friday Indicator (0 or 1)                       | 0, 0, 0, 0, 1                       |
| Mon               | Numeric      | Monday Indicator (0 or 1)                       | 1, 0, 0, 0, 0                       |
| Sat               | Numeric      | Saturday Indicator (0 or 1)                     | 0, 0, 0, 0, 0                       |
| Sun               | Numeric      | Sunday Indicator (0 or 1)                       | 0, 0, 0, 0, 0                       |
| Thurs             | Numeric      | Thursday Indicator (0 or 1)                     | 0, 0, 0, 1, 0                       |
| Tues              | Numeric      | Tuesday Indicator (0 or 1)                      | 0, 1, 0, 0, 0                       |
| Wed               | Numeric      | Wednesday Indicator (0 or 1)                    | 0, 0, 1, 0, 0                       |
| Term              | Character    | Winter, Spring, Summer, Fall                                   | "Winter", "Winter", "Winter", "Winter", "Winter" |
| Enrollment        | Numeric      | Total Enrollment                                      | 29642, 29642, 29642, 29642, 29642     |
| FullTime          | Numeric      | Full-Time Enrollment                            | 25191, 25191, 25191, 25191, 25191     |
| Holiday           | Numeric      | Holiday Indicator (0 or 1)                      | 0, 0, 0, 0, 0                       |
| Exam              | Numeric      | Exam Indicator (0 or 1)                         | 0, 0, 0, 0, 0                       |

### [ProvoAQ.csv](ProvoAQ.csv) [3]
This data set contains all the merged air quality data from the directory, *Provo Air Quality Data*. This is a data set of historical air quality data from 2014-2022

### [WeatherCitations.csv](WeatherCitations.csv)
This data set is created by *Weather.ipynb*. This is the result of the merged *ParkingCitationsEncrypted.csv* and the weather data obtained from the climate API, [Open-Meteo](https://open-meteo.com/en/docs/climate-api). 

### [weather.json](weather.json)
This is the raw json response from the API call. This is used when formatting the weather data into pandas data frames to merge with rest of the data

## Non-Essential Data Sets
---
### [aq2023.csv](aq2023.csv)
This data set is a subset of *AQ.csv*. This contains air quality data for Provo, UT specifically 2023. This data was completely obtained through the [Weather Bit](https://www.weatherbit.io/) API.

### [FinesByMonth.csv](FinesByMonth.csv)
A simple summary data set that shows the fines and unpaid proportion per month.

## Data Sources
---
[1] University traffic citations data come from BYU's citations server: [https://cars.byu.edu/citations](https://cars.byu.edu/citations). Data obtained through web scraping techniques which I explain [here](https://samleebyu.github.io/2023/09/29/selenium-best-practices/). Raw data can be viewed [here](https://github.com/SamLeeBYU/BYUTrafficCitations/blob/main/ParkingCitationsEncrypted.csv), though license plate/vin numbers have been encrypted so the data set cannot be easily merged with other data sets containing these license plate/vin numbers.

[2] Local and historical weather data for Provo, UT were obtained through the climate API, [Open-Meteo](https://open-meteo.com/en/docs/climate-api).

[3] Local historical air quality data containing measurements for $CO$, $NO_2$, $O_3$, $PM 10$, and $PM 2.5$ were obtained through parsing through data on the Utah Department of Environmental Quality's [website](https://air.utah.gov/dataarchive/archall.htm). Missing data were corrected by subtituting the missing values for the average of the given metric for the corresponding month aggregated overall all the data (years 2014-2022, April-August of 2020 excluded).

[4] Air quality pollutant specific sub-category metrics are determined by the U.S. Environmental Protection Agency Office of Air Quality Planning and Standards Air Quality Assessment Division. See [here](https://airnowtomed.app.cloud.gov/sites/default/files/2020-05/aqi-technical-assistance-document-sept2018.pdf) (pages 4 and 5). Appropriate AQI was also calculated using EPA's documentation found here.

[5] Past enrollment data of BYU for the past ten years was obtained curtesy of [BYU Research & Reporting Enrollment Services](https://tableau.byu.edu/#/site/BYUCommunity/views/UniversityEnrollmentStatistics/EnrollmentStatistics).

[6] BYU academic archive data were found courtesy of the HBLL. Records were used to link up when classes started and ended for each semester. Archives can be found [here](https://lib.byu.edu/collections/byu-history/).