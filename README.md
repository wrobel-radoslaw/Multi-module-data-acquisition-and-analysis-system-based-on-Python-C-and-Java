# Multi-module Data Acquisition and Analysis System

This repository contains the source code for the paper submitted to *Advances in IT and Electrical Engineering*:

**Multi-module data acquisition and analysis system based on Python, C++ and Java**

## Architecture

The project is a modular IT system divided into three independent modules, all operated via a central Python launcher:

1. **Weather module (Python)**  
   Uses `requests` and `Tkinter` to retrieve and display current weather data from the OpenWeatherMap API. The user can enter a location name. The module saves selected weather data to CSV files and supports local PostgreSQL-based storage for historical analysis.

2. **Statistical module (C++)**  
   Uses `cpr` and `nlohmann/json` to retrieve and parse selected demographic and economic datasets from the Eurostat API. The user can select one of the supported statistical indicators, enter a supported country code, save the results to CSV, load previously saved CSV files in offline mode, and generate charts with Gnuplot.

3. **Financial module (Java)**  
   Downloads historical stock quotes from Stooq.pl for a user-selected Warsaw Stock Exchange ticker. It calculates selected technical indicators, including SMA-50, Momentum, and RSI, and visualizes the results using XChart.

## Notes

The example datasets and screenshots used in the paper, such as Rzeszow weather data, Polish Eurostat data, and CD Projekt SA stock data, are demonstration cases. They are not fixed input values of the whole system.

## Setup Instructions

### Python module

To run the weather application, create a file named `api_key.txt` in the root directory and paste your personal OpenWeatherMap API key inside it.

### C++ module

The C++ module requires Gnuplot to be installed and added to the system `PATH` variable for chart generation.

### Java module

The Java module uses Gradle for dependency management and can be built and run using the provided Gradle wrapper.
