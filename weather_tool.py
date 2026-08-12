import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(city: str):
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {
            "error": response.json().get("message", "Weather API error")
        }

    data = response.json()

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["description"]
    }


def get_forecast(city: str):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {
            "error": response.json().get("message", "Forecast API error")
        }

    data = response.json()

    forecast = []

    for item in data["list"][:8]:
        forecast.append({
            "time": item["dt_txt"],
            "temperature": item["main"]["temp"],
            "weather": item["weather"][0]["description"]
        })

    return forecast

def get_air_quality(city: str):
    # First get city coordinates
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"

    geo_params = {
        "q": city,
        "limit": 1,
        "appid": API_KEY
    }

    geo_response = requests.get(geo_url, params=geo_params)

    if geo_response.status_code != 200 or not geo_response.json():
        return {"error": "City not found"}

    location = geo_response.json()[0]

    lat = location["lat"]
    lon = location["lon"]

    # Get AQI
    url = "https://api.openweathermap.org/data/2.5/air_pollution"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {
            "error": "Air quality API error"
        }

    data = response.json()["list"][0]

    return {
        "aqi": data["main"]["aqi"],
        "pm2_5": data["components"]["pm2_5"],
        "pm10": data["components"]["pm10"],
        "co": data["components"]["co"],
        "no2": data["components"]["no2"]
    }