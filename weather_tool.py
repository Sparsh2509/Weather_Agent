import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(city: str):
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {
                "error": response.json().get(
                    "message",
                    "Weather API error"
                )
            }

        data = response.json()

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"]
        }

    except requests.RequestException as e:
        return {
            "error": f"Weather API request failed: {str(e)}"
        }


def get_forecast(city: str):
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {
                "error": response.json().get(
                    "message",
                    "Forecast API error"
                )
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

    except requests.RequestException as e:
        return {
            "error": f"Forecast API request failed: {str(e)}"
        }