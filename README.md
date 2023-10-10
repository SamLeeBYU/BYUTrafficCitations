# BYU Traffic Citations Research

This repository contains all the scripts and files used for parking allocation research

## Research Questions: 
## 1. Can we responsibly forecast the expected revenue for BYU parking services for a given week?
## 2. Can we create a posterior distribution for when students are most likely to get ticketed (for the factors: time of day, time of week, and type of ticket)?

## Scripts

### main.py
This is the main script used to scrape the data from BYU's server. I break down this script [here](https://samleebyu.github.io/2023/09/29/selenium-best-practices/). I use Selenium to iterate through all possible combinations of citation numbers and dynamically scrape the data.

### scraper.ipynb
A jupyter notebook used for Selenium experimentation. Used as a prototype and a sandbox for *main.py*.

### DataAnalysis.ipynb
A jupyter notebook used for basic exploratory data analysis on the *ParkingCitations* data set.

## Data Sets

### ParkingCitationsEncrypted.csv
The full data set of BYU parking citations as scraped from the data set. License plate numbers have been encrypted (the encryption script is not included on this repository) so the data set cannot be easily matched with other records across the internet, though state (Residence) records have been maintained. The data set contains citations from June, 2010 to Present (Oct, 2023).

### FinesByMonth.csv
A simple summary data set that shows the fines and unpaid proportion per month.