#pragma once
#define WIN32_LEAN_AND_MEAN
#undef byte
#include <map>
#include <string>
#include <windows.h>

using namespace std;

void SaveEurostatData(const std::map<int, double>& data, std::string countryCode, std::string statName);
std::map<int, double> LoadEurostatDataOffline(std::string& outFileName);
std::map<int, double> eurostatGDP(string countryCode);               // GDP
std::map<int, double> eurostatPopulation(string countryCode);        // Total population
std::map<int, double> eurostatPopulationDensity(string countryCode); // Population density
std::map<int, double> eurostatUnemployment(string countryCode);      // Unemployment rate
std::map<int, double> eurostatInflation(string countryCode);         // Inflation
std::map<int, double> eurostatLifeExpectancy(string countryCode);    // Life expectancy
std::map<int, double> eurostatRenewableEnergy(string countryCode);   // Renewable energy (%)
std::map<int, double> eurostatBirths(string countryCode);            // Number of births
std::map<int, double> eurostatRoadFatalities(string countryCode);    // Road fatalities
std::map<int,double> eurostatInternetAccess(string countryCode);     // Internet access