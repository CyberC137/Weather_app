import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime
from collections import defaultdict

API_KEY = "API_Key" 
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_weather():
    location = entry.get()
    if not location:
        messagebox.showwarning("Input Error", "Please enter a location.")
        return

    current_params = {
        "q": location,
        "appid": API_KEY,
        "units": "metric"
    }

    forecast_params = {
        "q": location,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        current_response = requests.get(CURRENT_URL, params=current_params)
        current_data = current_response.json()
        if current_response.status_code != 200:
            raise Exception(current_data.get("message", "Failed to retrieve current weather."))

        current_weather = f"""
Location: {current_data['name']}, {current_data['sys']['country']}
Temperature: {current_data['main']['temp']} °C
Condition: {current_data['weather'][0]['description'].title()}
Humidity: {current_data['main']['humidity']}%
Wind Speed: {current_data['wind']['speed']} m/s
"""

        forecast_response = requests.get(FORECAST_URL, params=forecast_params)
        forecast_data = forecast_response.json()
        if forecast_response.status_code != 200:
            raise Exception(forecast_data.get("message", "Failed to retrieve forecast."))

        forecast_dict = defaultdict(list)
        for item in forecast_data['list']:
            dt_txt = item['dt_txt']
            date = dt_txt.split()[0]
            temp = item['main']['temp']
            description = item['weather'][0]['description']
            forecast_dict[date].append((temp, description))

        forecast_lines = ["\n5-Day Forecast:"]
        for i, (date, entries) in enumerate(forecast_dict.items()):
            if i == 0:
                continue  
            avg_temp = sum(temp for temp, _ in entries) / len(entries)
            common_desc = max(set([desc for _, desc in entries]), key=[desc for _, desc in entries].count)
            readable_date = datetime.strptime(date, "%Y-%m-%d").strftime("%A %d %b")
            forecast_lines.append(f"{readable_date}: {avg_temp:.1f}°C, {common_desc.title()}")

            if len(forecast_lines) >= 6:
                break  

        output_label.config(text=current_weather + "\n".join(forecast_lines))

    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI setup
app = tk.Tk()
app.title("Weather App with 5-Day Forecast")
app.geometry("500x500")
app.resizable(True, True)

tk.Label(app, text="Enter Location:", font=("Arial", 14)).pack(pady=10)

entry = tk.Entry(app, font=("Arial", 14), width=30)
entry.pack(pady=5)

tk.Button(app, text="Get Weather", command=get_weather, font=("Arial", 12)).pack(pady=10)

output_label = tk.Label(app, text="", font=("Arial", 12), justify="left", wraplength=480)
output_label.pack(pady=10)

app.mainloop()
