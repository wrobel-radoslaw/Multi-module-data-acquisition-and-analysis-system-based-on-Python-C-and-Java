#define WIN32_LEAN_AND_MEAN
#undef byte
#include <windows.h>
#include "eurostat.h"
#include <cpr/cpr.h>
#include <nlohmann/json.hpp>
#include <map>
#include <string>
#include <iostream>
#include <filesystem>
#include <ctime>
#include <sstream>
#include <iomanip>
#include <vector>

using namespace std;
namespace fs = std::filesystem;
using json = nlohmann::json;

void SaveEurostatData(const std::map<int, double>& data, string countryCode, string statName)
{
    string EurostatDataPath = "EurostatData";
    std::ostringstream oss;

    if (!fs::exists(EurostatDataPath)) fs::create_directory(EurostatDataPath);

    std::time_t Time = std::time(nullptr);
    std::tm tm = *std::localtime(&Time);
    oss << std::put_time(&tm, "%Y%m%d");
    string ConvertedTime = oss.str();

    string EurostatCSVName = countryCode + "-" + statName + "-" + ConvertedTime + ".csv";
    std::ostringstream DuplicatePrevention;
    DuplicatePrevention << "year;value\n";
    DuplicatePrevention << std::fixed << std::setprecision(2);
    
    for (auto const& [year, value] : data) DuplicatePrevention << year << ";" << value << "\n";
    string DupPrevData = DuplicatePrevention.str();

    cout << "Checking folder contents...\n";
    for (const auto& entry : fs::directory_iterator(EurostatDataPath))
    {
        string fileName = entry.path().filename().string();
        string prefix = countryCode + "-" + statName + "-";

        if (fileName.find(prefix) == 0)
        {
            std::ifstream oldFile(entry.path());
            std::stringstream buffer;
            buffer << oldFile.rdbuf();
            string oldText = buffer.str();

            if (oldText == DupPrevData)
            {
                cout << "Data in file " << fileName << " is identical. Skipping save." << endl;
                return;
            }
        }
    }

    std::ofstream ExitFileCSV(fs::path(EurostatDataPath) / EurostatCSVName);
    if (ExitFileCSV.is_open())
    {
        ExitFileCSV << DupPrevData;
        ExitFileCSV.close();
        cout << "Data saved to file: " << EurostatCSVName << endl;
    }
}

void parseEurostatData(const json& data, std::map<int, double>& yearToValue)
{
    if (!data.contains("dimension") || !data["dimension"].contains("time") || !data.contains("value")) return;
    map<int, int> idx2year;
    for (auto& [yearStr, idx] : data["dimension"]["time"]["category"]["index"].items())
        idx2year[idx.get<int>()] = stoi(yearStr);

    for (auto& [idxStr, val] : data["value"].items())
    {
        int idx = stoi(idxStr);
        if (val.is_null()) continue;
        if (idx2year.count(idx)) yearToValue[idx2year[idx]] = val.get<double>();
    }
}

std::map<int, double> eurostatGDP(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_gdp?geo=" + countryCode + "&na_item=B1GQ&unit=CLV10_MEUR";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int, double> yearToGDP;
    parseEurostatData(data, yearToGDP);
    if(yearToGDP.empty()) cout << "No GDP data for " << countryCode << endl;
    return yearToGDP;
}

std::map<int, double> eurostatPopulation(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_pjan?geo=" + countryCode + "&unit=NR&sex=T&age=TOTAL";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int, double> yearToPop;
    parseEurostatData(data, yearToPop);
    if(yearToPop.empty()) cout << "No population data for " << countryCode << endl;
    return yearToPop;
}

std::map<int,double> eurostatPopulationDensity(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_r_d3dens?geo=" + countryCode + "&unit=PER_KM2";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int,double> yearToDensity;
    parseEurostatData(data, yearToDensity);
    if(yearToDensity.empty()) cout << "No population density data for " << countryCode << endl;
    return yearToDensity;
}

std::map<int,double> eurostatUnemployment(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m?geo=" + countryCode + "&unit=PC_ACT";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int,double> yearToUE;
    parseEurostatData(data, yearToUE);
    if(yearToUE.empty()) cout << "No unemployment data for " << countryCode << endl;
    return yearToUE;
}

std::map<int,double> eurostatInflation(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_aind?geo=" + countryCode + "&coicop=CP00&unit=RCH_A_AVG";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int,double> yearToInflation;
    parseEurostatData(data, yearToInflation);
    if(yearToInflation.empty()) cout << "No inflation data for " << countryCode << endl;
    return yearToInflation;
}

std::map<int,double> eurostatLifeExpectancy(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_mlexpec?geo=" + countryCode + "&unit=YR";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int,double> yearToLE;
    parseEurostatData(data, yearToLE);
    if(yearToLE.empty()) cout << "No life expectancy data for " << countryCode << endl;
    return yearToLE;
}

std::map<int,double> eurostatRenewableEnergy(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ind_ren?geo=" + countryCode + "&unit=PC";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int,double> yearToRE;
    parseEurostatData(data, yearToRE);
    if(yearToRE.empty()) cout << "No renewable energy data for " << countryCode << endl;
    return yearToRE;
}

std::map<int,double> eurostatBirths(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_frate?geo=" + countryCode + "&unit=NR";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int,double> yearToBirths;
    parseEurostatData(data, yearToBirths);
    if(yearToBirths.empty()) cout << "No birth data for " << countryCode << endl;
    return yearToBirths;
}

std::map<int,double> eurostatRoadFatalities(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_40?geo=" + countryCode + "&unit=NR";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int,double> yearToFatalities;
    parseEurostatData(data, yearToFatalities);
    if(yearToFatalities.empty()) cout << "No road fatalities data for " << countryCode << endl;
    return yearToFatalities;
}

std::map<int,double> eurostatInternetAccess(string countryCode)
{
    string url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/isoc_ci_in_h?geo=" + countryCode + "&hhtyp=TOTAL&unit=PC_HH";
    auto resp = cpr::Get(cpr::Url{url});
    json data = json::parse(resp.text);
    map<int,double> yearToInternetAccess;
    parseEurostatData(data, yearToInternetAccess);
    if(yearToInternetAccess.empty()) cout << "No internet access data for " << countryCode << endl;
    return yearToInternetAccess;
}

std::map<int, double> LoadEurostatDataOffline(std::string& outFileName)
{
    string EurostatDataPath = "EurostatData";
    std::map<int, double> loadedData;
    vector<string> fileList;

    if (!fs::exists(EurostatDataPath) || fs::is_empty(EurostatDataPath))
    {
        cout << "EurostatData folder does not exist or is empty." << endl;
        return loadedData;
    }

    cout << "\nAVAILABLE FILES IN OFFLINE MODE:\n";
    int index = 1;
    for (const auto& entry : fs::directory_iterator(EurostatDataPath))
    {
        if (entry.path().extension() == ".csv")
        {
            cout << index << ". " << entry.path().filename().string() << endl;
            fileList.push_back(entry.path().string());
            index++;
        }
    }

    if (fileList.empty())
    {
        cout << "No CSV files found." << endl;
        return loadedData;
    }

    cout << "\nSelect file number: ";
    int choice;
    if (!(cin >> choice))
    {
        cin.clear();
        cin.ignore(1000, '\n');
        return loadedData;
    }
    cin.ignore();

    if (choice < 1 || choice > fileList.size())
    {
        cout << "Invalid number." << endl;
        return loadedData;
    }

    string selectedFile = fileList[choice - 1];
    outFileName = fs::path(selectedFile).filename().string();
    
    ifstream file(selectedFile);
    string line;
    
    getline(file, line); 

    while (getline(file, line))
    {
        stringstream ss(line);
        string segment;
        vector<string> seglist;

        while (getline(ss, segment, ';'))
        {
            seglist.push_back(segment);
        }

        if (seglist.size() >= 2)
        {
            try
            {
                int year = stoi(seglist[0]);
                double val = stod(seglist[1]);
                loadedData[year] = val;
            }
            catch (...)
            {
                continue;
            }
        }
    }
    return loadedData;
}