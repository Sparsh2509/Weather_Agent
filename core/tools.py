from langchain_core.tools import tool

from core.weather_tool import (
    get_weather,
    get_forecast,
    get_air_quality
)

from core.search_tool import web_search


@tool
def weather_tool(city: str):
    """Get current weather information for a city."""
    return get_weather(city)


@tool
def forecast_tool(city: str):
    """Get future weather forecast information for a city."""
    return get_forecast(city)


@tool
def air_quality_tool(city: str):
    """Get current air quality information for a city."""
    return get_air_quality(city)


@tool
def search_tool(query: str):
    """Search the web for latest, recent or news information."""
    return web_search(query)


tools = [
    weather_tool,
    forecast_tool,
    air_quality_tool,
    search_tool
]