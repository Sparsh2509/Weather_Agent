import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(city: str):

    try:

        if not API_KEY:
            return {
                "error": "OpenWeather API key is missing."
            }

        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 401:
            return {
                "error": "Invalid OpenWeather API key."
            }

        if response.status_code == 404:
            return {
                "error": f"City '{city}' was not found."
            }

        if response.status_code == 429:
            return {
                "error": "OpenWeather API rate limit exceeded."
            }

        if response.status_code != 200:
            return {
                "error": f"Weather API error: {response.status_code}"
            }

        data = response.json()

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"]
        }

    except requests.Timeout:

        return {
            "error": "Weather API request timed out."
        }

    except requests.RequestException as e:

        return {
            "error": f"Weather API request failed: {str(e)}"
        }

    except Exception as e:

        return {
            "error": f"Unexpected weather error: {str(e)}"
        }


def get_forecast(city: str):

    try:

        if not API_KEY:
            return {
                "error": "OpenWeather API key is missing."
            }

        url = "https://api.openweathermap.org/data/2.5/forecast"

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 401:
            return {
                "error": "Invalid OpenWeather API key."
            }

        if response.status_code == 404:
            return {
                "error": f"City '{city}' was not found."
            }

        if response.status_code == 429:
            return {
                "error": "OpenWeather API rate limit exceeded."
            }

        if response.status_code != 200:
            return {
                "error": f"Forecast API error: {response.status_code}"
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

    except requests.Timeout:

        return {
            "error": "Forecast API request timed out."
        }

    except requests.RequestException as e:

        return {
            "error": f"Forecast API request failed: {str(e)}"
        }

    except Exception as e:

        return {
            "error": f"Unexpected forecast error: {str(e)}"
        }


def get_air_quality(city: str):

    try:

        if not API_KEY:
            return {
                "error": "OpenWeather API key is missing."
            }

        # -------------------------
        # GET CITY COORDINATES
        # -------------------------

        weather_url = (
            "https://api.openweathermap.org/data/2.5/weather"
        )

        params = {
            "q": city,
            "appid": API_KEY
        }

        response = requests.get(
            weather_url,
            params=params,
            timeout=10
        )

        if response.status_code == 401:
            return {
                "error": "Invalid OpenWeather API key."
            }

        if response.status_code == 404:
            return {
                "error": f"City '{city}' was not found."
            }

        if response.status_code == 429:
            return {
                "error": "OpenWeather API rate limit exceeded."
            }

        if response.status_code != 200:
            return {
                "error": f"Location API error: {response.status_code}"
            }

        data = response.json()

        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        # -------------------------
        # GET AIR QUALITY
        # -------------------------

        aqi_url = (
            "https://api.openweathermap.org/data/2.5/air_pollution"
        )

        aqi_params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY
        }

        aqi_response = requests.get(
            aqi_url,
            params=aqi_params,
            timeout=10
        )

        if aqi_response.status_code == 401:
            return {
                "error": "Invalid OpenWeather API key."
            }

        if aqi_response.status_code == 429:
            return {
                "error": "Air quality API rate limit exceeded."
            }

        if aqi_response.status_code != 200:
            return {
                "error": f"Air quality API error: {aqi_response.status_code}"
            }

        aqi_data = aqi_response.json()["list"][0]

        components = aqi_data["components"]

        return {
            "city": city,
            "aqi": aqi_data["main"]["aqi"],
            "pm2_5": components["pm2_5"],
            "pm10": components["pm10"],
            "co": components["co"],
            "no2": components["no2"]
        }

    except requests.Timeout:

        return {
            "error": "Air quality API request timed out."
        }

    except requests.RequestException as e:

        return {
            "error": f"Air quality request failed: {str(e)}"
        }

    except Exception as e:

        return {
            "error": f"Unexpected air quality error: {str(e)}"
        }