#define WIN32_LEAN_AND_MEAN
#undef byte
#include <iostream>
#include <windows.h>
#include "eurostat.h"
#include <map>
#include <string>
#include <iomanip>
#include <filesystem>
#include <ctime>

using namespace std;

string translit(string s) 
{
    for (auto const& [z, na] : map<string, string>
    {
        {"ą","a"}, {"ć","c"}, {"ę","e"}, {"ł","l"}, {"ń","n"},
        {"ó","o"}, {"ś","s"}, {"ź","z"}, {"ż","z"}, {"€","EUR"},
        {"_", "-"}
    }) 
    {
        for (size_t p = 0; (p = s.find(z, p)) != string::npos; p += na.length())
            s.replace(p, z.length(), na);
    }
    return s;
}

void drawChart(const map<int, double>& data, const string& title, const string& xAxis, const string& yAxis)
{
    FILE* gp = _popen("gnuplot -persistent", "w");
    if(!gp) return;

    fprintf(gp, "set title \"%s\"\n", translit(title).c_str());
    fprintf(gp, "set xlabel \"%s\"\n", translit(xAxis).c_str());
    fprintf(gp, "set ylabel \"%s\"\n", translit(yAxis).c_str());
    
    // No legend in the upper right corner of the chart
    fprintf(gp, "set key off\n");
    
    // Grid settings
    fprintf(gp, "set grid ytics lc rgb \"#00379cff\" lw 1 lt 1\n");
    fprintf(gp, "set grid xtics lc rgb \"#00379cff\" lw 1 lt 1\n");
    fprintf(gp, "plot '-' with linespoints lc rgb '#4169E1' lw 2 pt 7 ps 1.5\n");

    for(auto &[year, value] : data)
        fprintf(gp, "%d %f\n", year, value);
    
    // End of Gnuplot commands
    fprintf(gp, "e\n");
    // Flush buffer to Gnuplot
    fflush(gp);
    // End Gnuplot execution
    _pclose(gp);
}

int main() 
{
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);

    map<string, string> countryNames =
    {
        {"AT", "Austria"}, {"BE", "Belgium"}, {"BG", "Bulgaria"}, {"CY", "Cyprus"}, {"CZ", "Czechia"}, {"DE", "Germany"},
        {"DK", "Denmark"}, {"EE", "Estonia"}, {"EL", "Greece"}, {"ES", "Spain"}, {"FI", "Finland"}, {"FR", "France"},
        {"HR", "Croatia"}, {"HU", "Hungary"}, {"IE", "Ireland"}, {"IS", "Iceland"}, {"IT", "Italy"}, {"LT", "Lithuania"},
        {"LU", "Luxembourg"}, {"LV", "Latvia"}, {"MT", "Malta"}, {"NL", "Netherlands"}, {"NO", "Norway"}, {"PL", "Poland"},
        {"PT", "Portugal"}, {"RO", "Romania"}, {"SE", "Sweden"}, {"SI", "Slovenia"}, {"SK", "Slovakia"}, {"UK", "United Kingdom"}
    };

    while(true) 
    {
        system("cls");
        cout << "==================================\n";
        cout << "          EUROSTAT DATA          \n";
        cout << "==================================\n\n";

        cout << "Enter function number:\n";
        cout << "1. GDP\n";
        cout << "2. Population\n";
        cout << "3. Population density\n";
        cout << "4. Unemployment rate\n";
        cout << "5. Inflation\n";
        cout << "6. Life expectancy\n";
        cout << "7. Renewable energy\n";
        cout << "8. Birth rate\n";
        cout << "9. Road fatalities\n";
        cout << "10. Internet access\n";
        cout << "11. Offline analysis (Load from file)\n";
        cout << "12. List of supported countries\n"; 
        cout << "Q. Exit\n";

        string choice; getline(cin, choice);
        if(choice == "q" || choice == "Q" || choice == "exit" || choice == "quit") break;

        map<int,double> data;
        string uniqueLabel = "";
        string graphTitle = "";
        string statName = ""; 
        string countryCode = "";
        string fullCountryName = "";
        int precision = 0;

        // Display list of countries option
        if (choice == "12" || choice == "LP" || choice == "lp" || choice == "list")
        {
            cout << "\n======== Country List (Code - Country): ========\n";
            for(auto &[code, country] : countryNames)
                cout << code << " - " << country << "\n";
            cout << "\nPress Enter to continue..." << endl;
            cin.get();
            continue;
        }

        // Offline loading option
        if (choice == "11")
        {
            string loadedFileName;
            data = LoadEurostatDataOffline(loadedFileName);
            
            if (!data.empty())
            {
                fullCountryName = loadedFileName;
                graphTitle = "Chart from file";
                precision = 2;

                if (loadedFileName.find("GDP") != string::npos || loadedFileName.find("PKB") != string::npos) { uniqueLabel = " MLN EUR"; }
                else if (loadedFileName.find("Population") != string::npos || loadedFileName.find("Populacja") != string::npos) { uniqueLabel = " people"; precision = 0; }
                else if (loadedFileName.find("Density") != string::npos || loadedFileName.find("Gestosc") != string::npos) { uniqueLabel = " people/km^2"; precision = 0; }
                else if (loadedFileName.find("Unemployment") != string::npos || loadedFileName.find("Bezrobocie") != string::npos) { uniqueLabel = "%"; }
                else if (loadedFileName.find("Inflation") != string::npos || loadedFileName.find("Inflacja") != string::npos) { uniqueLabel = "% HICP"; }
                else if (loadedFileName.find("LifeExpectancy") != string::npos || loadedFileName.find("Dlugosc") != string::npos) { uniqueLabel = " years"; precision = 0; }
                else if (loadedFileName.find("RenewableEnergy") != string::npos || loadedFileName.find("Energia") != string::npos) { uniqueLabel = "% share"; }
                else if (loadedFileName.find("Births") != string::npos || loadedFileName.find("Urodzen") != string::npos) { uniqueLabel = " Birth rate"; }
                else if (loadedFileName.find("Fatalities") != string::npos || loadedFileName.find("Wypadki") != string::npos) { uniqueLabel = " fatalities"; precision = 0; }
                else if (loadedFileName.find("InternetAccess") != string::npos || loadedFileName.find("Internet") != string::npos) { uniqueLabel = "% households"; }

                goto SHOW_RESULTS;
            } else {
                continue; 
            }
        }

        // Main options 1-10
        if (choice == "1" || choice == "2" || choice == "3" || choice == "4" || 
            choice == "5" || choice == "6" || choice == "7" || choice == "8" || 
            choice == "9" || choice == "10") 
        {
            cout << "Select country (code, e.g. PL, DE): ";
            getline(cin, countryCode);
            for(auto &c : countryCode) c = toupper(c);
            
            if (countryNames.find(countryCode) == countryNames.end()) {
                cout << "Invalid country code!\nPress Enter to continue..." << endl;
                cin.get();
                continue;
            }
            fullCountryName = countryNames[countryCode];

            if(choice == "1") {statName = "GDP"; data = eurostatGDP(countryCode);}
            else if(choice == "2") { statName = "Population"; data = eurostatPopulation(countryCode); }
            else if(choice == "3") { statName = "PopulationDensity"; data = eurostatPopulationDensity(countryCode); }
            else if(choice == "4") { statName = "Unemployment"; data = eurostatUnemployment(countryCode); }
            else if(choice == "5") { statName = "Inflation"; data = eurostatInflation(countryCode); }
            else if(choice == "6") { statName = "LifeExpectancy"; data = eurostatLifeExpectancy(countryCode); }
            else if(choice == "7") { statName = "RenewableEnergy"; data = eurostatRenewableEnergy(countryCode); }
            else if(choice == "8") { statName = "Births"; data = eurostatBirths(countryCode); }
            else if(choice == "9") { statName = "RoadFatalities"; data = eurostatRoadFatalities(countryCode); }
            else if(choice == "10") { statName = "InternetAccess"; data = eurostatInternetAccess(countryCode); }

            if (!data.empty() && !statName.empty()) {
                SaveEurostatData(data, countryCode, statName);
            }

            if(choice == "1") { uniqueLabel = " MLN EUR"; precision = 2; graphTitle = "Chart showing GDP"; }
            else if(choice == "2") { uniqueLabel = " people"; precision = 0; graphTitle = "Chart showing population"; }
            else if(choice == "3") { uniqueLabel = " people/km^2"; precision = 0; graphTitle = "Chart showing population density";}
            else if(choice == "4") { uniqueLabel = "%"; precision = 2; graphTitle = "Chart showing unemployment rate";}
            else if(choice == "5") { uniqueLabel = "% HICP"; precision = 2; graphTitle = "Chart showing inflation";}
            else if(choice == "6") { uniqueLabel = " years"; precision = 0; graphTitle = "Chart showing life expectancy";}
            else if(choice == "7") { uniqueLabel = "% share"; precision = 2; graphTitle = "Chart showing renewable energy";}
            else if(choice == "8") { uniqueLabel = " Birth rate"; precision = 2; graphTitle = "Chart showing birth rate";}
            else if(choice == "9") { uniqueLabel = " fatalities"; precision = 0; graphTitle = "Chart showing road fatalities";}
            else if(choice == "10") { uniqueLabel = "% households"; precision = 2; graphTitle = "Chart showing internet access";}
        } 
        else 
        {
            cout << "Invalid choice.\nPress Enter to continue..." << endl;
            cin.get();
            continue;
        }

        SHOW_RESULTS:
        if (!data.empty())
        {
            cout << "\n======== Results: " << fullCountryName << " ========\n";
            for(auto &[year, val] : data)
                cout << "Year: " << year << ", Value: " << std::fixed << std::setprecision(precision) 
                     << val << uniqueLabel << endl;

            cout <<"\nDo you want to draw a chart? (Yes / No)\n";
            string drawInput;
            getline(cin, drawInput);
            for (auto &c : drawInput) c = toupper(c);
            
            if (drawInput == "YES" || drawInput == "Y" || drawInput == "TAK" || drawInput == "T"){
                drawChart(data, graphTitle + " - " + fullCountryName, "Year", uniqueLabel);
            }
            cout << "\nPress Enter to continue..." << endl;
            cin.get();
        }
        else
        {
            cout << "\nNo data available." << endl;
            cout << "\nPress Enter to continue..." << endl;
            cin.get();
        }
    }
    return 0;
}