from tkinter import *
from tkinter import messagebox
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import csv
import os
import glob
import datetime as dt
import requests
from PIL import ImageTk, Image
import re
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.widgets import Button as MplButton
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        # In developer mode use current directory
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_weather_icon_path(description, hour):
    """
    Selects an icon based on the description and hour (day/night).
    Night is assumed to be from 18:00 to 6:00.
    """
    is_night = hour >= 18 or hour < 6
    desc = description.lower()
    icon_name = "sun.png" # Default icon
    
    # --- Logic for mapping descriptions to files ---
    if "clear" in desc:
        icon_name = "moon.png" if is_night else "sun.png"
    elif "few clouds" in desc:
        icon_name = "cloudy_moon.png" if is_night else "cloud_few.png"
    elif "scattered" in desc or "broken" in desc:
        icon_name = "cloudy_moon.png" if is_night else "cloud_broken.png"
    elif "overcast" in desc:
        icon_name = "cloud_overcast.png"
    elif "freezing" in desc:
        icon_name = "rain_snow.png"
    elif "shower" in desc:
        icon_name = "rain_moon.png" if is_night else "cloud_rain.png"
    elif "light rain" in desc:
        icon_name = "rain_moon.png" if is_night else "cloud_light_rain.png"
    elif "heavy" in desc:
        icon_name = "rain_moon.png" if is_night else "cloud_heavy_rain.png"
    elif "rain" in desc:
        icon_name = "rain_moon.png" if is_night else "cloud_rain.png"
    elif "thunderstorm" in desc:
        icon_name = "thunder_moon.png" if is_night else "cloud_lightning.png"
    elif "snow" in desc:
        if "rain" in desc or "sleet" in desc:
            icon_name = "rain_snow.png"
        elif "light" in desc:
            icon_name = "snow_moon.png" if is_night else "light_snow.png"
        else:
            icon_name = "snow_moon.png" if is_night else "cloud_snow.png"
    elif "mist" in desc or "smoke" in desc or "haze" in desc:
        icon_name = "fog.png"
    elif "fog" in desc:
        icon_name = "cloud_fog.png"
    elif "tornado" in desc:
        icon_name = "tornado.png"
    elif "squall" in desc or "wind" in desc:
        icon_name = "windy.png"
        
    return f"icons/{icon_name}"

def remove_diacritics(text):
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
        'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    return ''.join(replacements.get(c, c) for c in text)

def save_weather_data_to_csv(city, country, longitude, latitude, 
                             temp_celsius, humidity, wind_speed, 
                             description, sunrise_time, sunset_time):
    if not os.path.exists("CSVWeatherData"):
        os.makedirs("CSVWeatherData")
    filename = dt.datetime.now().strftime("CSVWeatherData/weather_data_%Y%m%d_%H%M%S.csv")
    city_ascii = remove_diacritics(city)
    description_ascii = remove_diacritics(description)
    data = [{
        "City": city_ascii, "Country": country, "Longitude": longitude,
        "Latitude": latitude, "Temperature (C)": temp_celsius,
        "Humidity (%)": humidity, "Wind Speed (m/s)": wind_speed,
        "Description": description_ascii,
        "Sunrise": sunrise_time.strftime('%H:%M:%S'),
        "Sunset": sunset_time.strftime('%H:%M:%S')
    }]
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["City", "Country", "Longitude", "Latitude", "Temperature (C)",
                      "Humidity (%)", "Wind Speed (m/s)", "Description", "Sunrise", "Sunset"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def run_weather_app():
    program_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
    api_path = os.path.join(program_folder, "api_key.txt")
    try:
        with open(api_path, "r", encoding="utf-8") as file:
            api_key = file.read().strip()
    except FileNotFoundError:
        messagebox.showerror("File Error", f"api_key.txt not found in folder:\n{program_folder}")
        return
    
    root = Tk()
    root.title("Engineering Project - Weather Application")
    root.geometry("450x700")
    root['background'] = "#DDEEFF"

    current_weather_data = {}

    new = ImageTk.PhotoImage(Image.open(resource_path('logo.png')))
    panel = Label(root, image=new)
    panel.place(x=0, y=520)
    
    dt_now = dt.datetime.now()
    
    # English days and months explicitly
    en_days = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    en_months = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    
    day_name = en_days[dt_now.weekday()]
    date_day = Label(root, text=day_name, bg='#DDEEFF', font=("bold", 15))
    date_day.place(x=5, y=155) 
    
    date_full = f"{dt_now.day} {en_months[dt_now.month]} {dt_now.year}"
    date = Label(root, text=date_full, bg='#DDEEFF', font=("bold", 15))
    date.place(x=5, y=185) 
    
    hour = Label(root, text=dt_now.strftime('%H : %M'), bg='#DDEEFF', font=("bold", 15))
    hour.place(x=5, y=215) 
    
    if 8 <= int(dt_now.strftime('%H')) <= 18:
        img = ImageTk.PhotoImage(Image.open(resource_path('sun.png')))
    else:
        img = ImageTk.PhotoImage(Image.open(resource_path('moon.png')))
    panel_icon = Label(root, image=img)
    panel_icon.place(x=300, y=75) 
    
    city_name_var = StringVar()
    city_entry = Entry(root, textvariable=city_name_var, width=45)
    city_entry.grid(row=1, column=0, ipady=10, stick=W + E + N + S)

    def kelvin_to_celsius(kelvin): return kelvin - 273.15
    
    def get_weather():
        nonlocal current_weather_data
        try:
            api_request = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city_entry.get()}&appid={api_key}")
            response = api_request.json()
            
            if response.get('cod') != 200:
                raise ValueError(f"API Error: {response.get('message', 'Unknown error')}")

            temp_celsius = int(kelvin_to_celsius(response['main']['temp']))
            wind_speed = response['wind']['speed']
            humidity = response['main']['humidity']
            description_en = response['weather'][0]['description'].lower()
            local_offset = dt.timedelta(seconds=response['timezone'])
            
            if 'sys' not in response:
                 raise ValueError("Missing sunrise/sunset data.")
                 
            sunrise_time = dt.datetime.fromtimestamp(response['sys']['sunrise'], dt.timezone(local_offset)).replace(tzinfo=None)
            sunset_time = dt.datetime.fromtimestamp(response['sys']['sunset'], dt.timezone(local_offset)).replace(tzinfo=None)
            longitude = response['coord']['lon']
            latitude = response['coord']['lat']
            country = response['sys']['country']
            city = remove_diacritics(response['name'])
            
            label_temp.configure(text=f"Temperature: {temp_celsius}°C")
            label_humidity.configure(text=f"Humidity: {humidity}%")
            label_wind_speed.configure(text=f"Wind speed: {wind_speed} m/s")
            label_description.configure(text=f"Weather: {description_en.capitalize()}")
            label_sunrise.configure(text=f"Sunrise: {sunrise_time.strftime('%H:%M:%S')}")
            label_sunset.configure(text=f"Sunset: {sunset_time.strftime('%H:%M:%S')}")
            label_lon.configure(text=f"Longitude: {longitude}")
            label_lat.configure(text=f"Latitude: {latitude}")
            label_country.configure(text=f"Country: {country}")
            label_city.configure(text=f"City: {city}")
            
            current_weather_data = {
                'city': city, 'country': country, 'longitude': longitude, 'latitude': latitude,
                'temp_celsius': temp_celsius, 'humidity': humidity, 'wind_speed': wind_speed,
                'description': description_en, 'sunrise_time': sunrise_time, 'sunset_time': sunset_time
            }
            saveButton.config(state=NORMAL)
            
        except Exception as e:
            messagebox.showerror("API Error", "Failed to retrieve data. Please check the city name.")
            label_temp.configure(text="Temperature: Error!") 
            saveButton.config(state=DISABLED)
            print("Error processing data:", e)
    
    def manual_save_data():
        if current_weather_data:
            try:
                save_weather_data_to_csv(**current_weather_data)
                print("Weather data successfully saved to CSV.")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save data: {e}")
        else:
            messagebox.showwarning("No data", "No data to save. Please search for a city first.")

    button_frame = Frame(root, bg='#DDEEFF')
    button_frame.grid(row=1, column=1, padx=5, stick=W + E + N + S)

    city_nameButton = Button(button_frame, text="Search", command=get_weather)
    city_nameButton.pack(side=LEFT, fill=BOTH, expand=True)
    
    saveButton = Button(button_frame, text="Save data", command=manual_save_data, state=DISABLED)
    saveButton.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))
    
    label_city = Label(root, text="City: ...", bg='#DDEEFF', font=("bold", 15))
    label_city.place(x=5, y=45)
    label_country = Label(root, text="Country: ...", bg='#DDEEFF', font=("bold", 15))
    label_country.place(x=5, y=70)
    label_lon = Label(root, text="Longitude: ...", bg='#DDEEFF', font=("Helvetica", 15))
    label_lon.place(x=5, y=95) 
    label_lat = Label(root, text="Latitude: ...", bg='#DDEEFF', font=("Helvetica", 15))
    label_lat.place(x=5, y=120) 
    label_temp = Label(root, text="Temperature: ...", bg='#DDEEFF', font=("Helvetica", 32), fg='black')
    label_temp.place(x=10, y=260) 
    label_humidity = Label(root, text="Humidity: ...", bg='#DDEEFF', font=("bold", 15))
    label_humidity.place(x=10, y=340) 
    label_wind_speed = Label(root, text="Wind speed: ...", bg='#DDEEFF', font=("bold", 15))
    label_wind_speed.place(x=10, y=370) 
    label_description = Label(root, text="Weather: ...", bg='#DDEEFF', font=("bold", 15))
    label_description.place(x=10, y=400) 
    label_sunrise = Label(root, text="Sunrise: ...", bg='#DDEEFF', font=("bold", 15))
    label_sunrise.place(x=10, y=430) 
    label_sunset = Label(root, text="Sunset: ...", bg='#DDEEFF', font=("bold", 15))
    label_sunset.place(x=10, y=460) 
    
    root.mainloop()

def plot_weather_graphs(df, city_name):
    df["hour"] = df["hour_minute"].apply(lambda x: x.hour)
    df = df.sort_values(by=["date", "hour_minute"])
    all_unique_dates = sorted(df["date"].unique())
    WINDOW_SIZE = 31
    
    class GraphNavigator:
        def __init__(self, ax, fig, graph_type):
            self.ax = ax
            self.fig = fig
            self.graph_type = graph_type
            self.current_start_index = 0
            self.max_index = max(0, len(all_unique_dates) - WINDOW_SIZE)
            
            ax_prev = plt.axes([0.15, 0.01, 0.1, 0.05])
            ax_next = plt.axes([0.26, 0.01, 0.1, 0.05])
            self.btn_prev = MplButton(ax_prev, '<')
            self.btn_next = MplButton(ax_next, '>')
            self.btn_prev.on_clicked(self.prev_page)
            self.btn_next.on_clicked(self.next_page)
            
            self.update_plot()

        def prev_page(self, event):
            if self.current_start_index > 0:
                self.current_start_index -= 1
                self.update_plot()

        def next_page(self, event):
            if self.current_start_index < self.max_index:
                self.current_start_index += 1
                self.update_plot()
        
        def update_plot(self):
            self.ax.clear()
            start = self.current_start_index
            end = start + WINDOW_SIZE
            visible_dates = all_unique_dates[start:end]
            
            subset_df = df[df['date'].isin(visible_dates)].copy()
            morning_subset = subset_df[subset_df["hour"] < 18].copy()
            evening_subset = subset_df[subset_df["hour"] >= 18].copy()
            
            date_labels = [d.strftime('%Y-%m-%d') for d in visible_dates]
            date_pos = {date: idx for idx, date in enumerate(date_labels)}
            
            morning_subset["date_cat"] = morning_subset["date"].apply(lambda d: date_pos[d.strftime('%Y-%m-%d')])
            evening_subset["date_cat"] = evening_subset["date"].apply(lambda d: date_pos[d.strftime('%Y-%m-%d')])
            
            if self.graph_type == 'temp':
                self.ax.plot(morning_subset["date_cat"], morning_subset["temperature_celsius"], marker='o', color='blue', label="Morning")
                self.ax.plot(evening_subset["date_cat"], evening_subset["temperature_celsius"], marker='o', color='orange', label="Evening")
                self.ax.set_title(f"Temperature in: {city_name} (Morning and Evening)")
                self.ax.set_ylabel("Temperature (°C)")
                
                if not subset_df.empty:
                    y_min = int(subset_df["temperature_celsius"].min()) - 2
                    y_max = int(subset_df["temperature_celsius"].max()) + 3
                    self.ax.set_yticks(range(y_min, y_max))
                
                self.add_icons(morning_subset)
                self.add_icons(evening_subset)
                
            elif self.graph_type == 'humidity':
                self.ax.plot(morning_subset["date_cat"], morning_subset["humidity"], marker='o', color='blue', label="Morning")
                self.ax.plot(evening_subset["date_cat"], evening_subset["humidity"], marker='o', color='orange', label="Evening")
                self.ax.set_title(f"Humidity in: {city_name} (Morning and Evening)")
                self.ax.set_ylabel("Humidity (%)")
                if not subset_df.empty:
                     self.ax.set_yticks(range(int(subset_df["humidity"].min()), int(subset_df["humidity"].max())+1, 5))

            elif self.graph_type == 'wind':
                self.ax.plot(morning_subset["date_cat"], morning_subset["wind_speed"], marker='o', color='blue', label="Morning")
                self.ax.plot(evening_subset["date_cat"], evening_subset["wind_speed"], marker='o', color='orange', label="Evening")
                self.ax.set_title(f"Wind speed in: {city_name} (Morning and Evening)")
                self.ax.set_ylabel("Wind speed (m/s)")
                
                if not subset_df.empty:
                    y_wind_min = int(subset_df["wind_speed"].min())
                    y_wind_max = int(subset_df["wind_speed"].max()) + 1
                    self.ax.set_yticks(range(y_wind_min, y_wind_max))
                    self.ax.set_ylim(subset_df["wind_speed"].min() - 1, subset_df["wind_speed"].max() + 1)

            self.ax.set_xlabel("Date")
            self.ax.set_xticks(range(len(date_labels)))
            self.ax.set_xticklabels(date_labels, rotation=80)
            self.ax.legend()
            self.ax.grid(True)
            self.fig.canvas.draw_idle()

        def add_icons(self, subset):
            for i, row in subset.iterrows():
                desc = row["description"]
                hour = row["hour"] 
                icon_path = get_weather_icon_path(desc, hour)
                full_icon_path = resource_path(icon_path)
                
                if os.path.exists(full_icon_path):
                    img = plt.imread(full_icon_path)
                    imagebox = OffsetImage(img, zoom=0.04)
                    ab = AnnotationBbox(imagebox, (row["date_cat"], row["temperature_celsius"] + 0.7), frameon=False)
                    self.ax.add_artist(ab)

    fig1, ax1 = plt.subplots(figsize=(12, 7)) 
    plt.subplots_adjust(bottom=0.25) 
    nav1 = GraphNavigator(ax1, fig1, 'temp')

    fig2, ax2 = plt.subplots(figsize=(12, 7))
    plt.subplots_adjust(bottom=0.25)
    nav2 = GraphNavigator(ax2, fig2, 'humidity')

    fig3, ax3 = plt.subplots(figsize=(12, 7))
    plt.subplots_adjust(bottom=0.25)
    nav3 = GraphNavigator(ax3, fig3, 'wind')

    plt.show()

def run_postgresql():
    hostname = 'localhost'
    database = 'engineeringproject'
    username = 'postgres'
    pwd = 'admin'
    port_id = 5432
    csv_folder = r"CSVWeatherData"
    try:
        conn = psycopg2.connect(host=hostname, database=database, user=username, password=pwd, port=port_id)
        cursor = conn.cursor()
        print("*** Connected to PostgreSQL database ***")
        print("1. Create charts based on data in the database.")
        print("2. Save data from CSV files to the database.\n")
        SelectFunction = input("Select function (1/2): ")
        
        if SelectFunction in ["1", "charts", "create", "chart"]:
            try:
                cursor.execute("SELECT DISTINCT city FROM weatherdata ORDER BY city;")
                available_cities = [row[0] for row in cursor.fetchall()]
                
                print("\n--- Available cities in database: ---")
                if available_cities:
                    for city in available_cities:
                        print(f"- {city}")
                else:
                    print("No cities in database. Use option 2 to import data.")
                    conn.close() 
                    return 
                print("------------------------------------------")
            except Exception as e:
                print(f"Error fetching city list. Make sure 'weatherdata' table exists. Details: {e}")
                conn.close()
                return 
            
            city_to_plot = input("Enter city name from database to create a chart: ")
            city_to_plot_ascii = remove_diacritics(city_to_plot)

            query = """
                SELECT city, country, temperature_celsius, humidity, wind_speed, description, date, hour_minute
                FROM weatherdata WHERE city = %s ORDER BY date, hour_minute;
            """
            cursor.execute(query, (city_to_plot_ascii,))
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=["city", "country", "temperature_celsius", "humidity", "wind_speed", "description", "date", "hour_minute"])

            if not df.empty:
                city_name = df["city"].iloc[0]
                plot_weather_graphs(df, city_name)
            else:
                print(f"No data found for: {city_to_plot}.")
                
        elif SelectFunction in ["2", "save", "import"]:
            delete_table_query = "DROP TABLE IF EXISTS weatherdata;"
            cursor.execute(delete_table_query)
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS weatherdata (
                id SERIAL PRIMARY KEY, city VARCHAR(50) NOT NULL, country VARCHAR(50) NOT NULL,
                longitude DOUBLE PRECISION NOT NULL, latitude DOUBLE PRECISION NOT NULL,
                temperature_celsius INTEGER NOT NULL, humidity INTEGER NOT NULL,
                wind_speed DOUBLE PRECISION NOT NULL, description VARCHAR(255) NOT NULL,
                sunrise_time TIME NOT NULL, sunset_time TIME NOT NULL,
                date DATE NOT NULL, hour_minute TIME NOT NULL
            );
            '''
            cursor.execute(create_table_query)
            conn.commit()
            csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))
            for file in csv_files:
                print(f"Processing file: {os.path.basename(file)}")
                match = re.search(r'weather_data_(\d{8})_(\d{6})\.csv', os.path.basename(file))
                if match:
                    date_str, time_str = match.group(1), match.group(2)
                    date_obj = dt.datetime.strptime(date_str, '%Y%m%d').date()
                    hour_minute_obj = dt.time(int(time_str[:2]), int(time_str[2:4]))
                else:
                    date_obj = dt.datetime.now().date()
                    hour_minute_obj = dt.datetime.now().time().replace(second=0, microsecond=0)
                with open(file, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    headers = next(reader)
                    data = []
                    for row in reader:
                        try:
                            lon, lat = float(row[2].replace(',', '.')), float(row[3].replace(',', '.'))
                            temp, wind = int(float(row[4].replace(',', '.'))), float(row[6].replace(',', '.'))
                            data.append((row[0], row[1], lon, lat, temp, int(row[5]), wind, row[7], row[8], row[9], date_obj, hour_minute_obj))
                        except Exception as e:
                            print(f"Error processing row: {row}. Details: {e}")
                            
                    insert_query = '''
                    INSERT INTO weatherdata (city, country, longitude, latitude, temperature_celsius, humidity, wind_speed, description, sunrise_time, sunset_time, date, hour_minute)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    '''
                    try:
                        execute_batch(cursor, insert_query, data)
                        conn.commit()
                        print(f"Inserted {len(data)} records from {os.path.basename(file)}")
                    except Exception as e:
                        print(f"Insertion error {os.path.basename(file)}. {e}")
                        conn.rollback()
    except Exception as error:
        print(f"Unexpected error: {error}")
    finally:
        if 'cursor' in locals() and cursor is not None: cursor.close()
        if 'conn' in locals() and conn is not None: conn.close()
        print("*** Disconnected from PostgreSQL database. ***\n")

while True:
    print("\n--- MENU ---")
    print("1. Weather Application Window")
    print("2. PostgreSQL Database and Charts")
    print("3. Exit\n")
    SelectFunction = input("Select option number: ").lower()
    if SelectFunction in ["1", "window", "app", "application", "weather"]: run_weather_app()
    elif SelectFunction in ["2", "database", "postgresql", "chart", "charts"]: run_postgresql()
    elif SelectFunction in ["3", "exit", "quit", "close"]: 
        print("Closing application...")
        break
    else: print("Invalid choice.")