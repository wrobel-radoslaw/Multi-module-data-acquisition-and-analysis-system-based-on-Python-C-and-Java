Multi-module Data Acquisition and Analysis System
This repository contains the source code for the research paper: "Multi-module data acquisition and analysis system based on Python, C++ and Java".

Architecture
The project is a hybrid IT system divided into three distinct modules, all operated via a central Python launcher:

Weather Module (Python): Uses the requests library and Tkinter to fetch and display real-time OpenWeatherMap API data. It implements data pre-selection and saves historical logs to a PostgreSQL database for long-term analysis.

Statistical Module (C++): A high-performance console application utilizing cpr (C++ Requests) and nlohmann/json to download and deserialize large demographic and economic datasets from the Eurostat API. It features native integration with Gnuplot for data visualization.

Financial Module (Java): Analyzes historical stock quotes from the Warsaw Stock Exchange (Stooq.pl). It implements complex mathematical algorithms to calculate Simple Moving Average (SMA-50), Momentum, and Relative Strength Index (RSI), rendering results via the XChart library.

Setup Instructions
Python Module: To run the weather application, you must create a file named api_key.txt in the root directory and paste your personal OpenWeatherMap API key inside it.

C++ Module: Requires Gnuplot to be installed and added to the system's PATH variable for chart generation to work correctly.

Java Module: Uses Gradle for dependency management. It can be built and run using the provided gradlew wrapper.