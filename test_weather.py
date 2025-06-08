import requests

API_KEY = "API-key"
location = "New York"  # You can change this to test other locations

url = f"https://api.openweathermap.org/data/2.5/weather"
params = {
    "q": location,
    "appid": API_KEY,
    "units": "metric"
}

response = requests.get(url, params=params)
data = response.json()

if response.status_code == 200:
    print(f"Weather for {data['name']}, {data['sys']['country']}:")
    print(f"Temperature: {data['main']['temp']}°C")
    print(f"Description: {data['weather'][0]['description']}")
    print(f"Humidity: {data['main']['humidity']}%")
    print(f"Wind Speed: {data['wind']['speed']} m/s")
else:
    print("Error:", data.get("message", "Failed to fetch weather data"))
