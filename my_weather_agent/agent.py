import os
import requests
from google.adk.agents import LlmAgent

def get_weather(city: str) -> dict:
    """Get the current weather for a given city.

    Args:
        city: The name of the city to get weather for (e.g. "London", "Tokyo", "New York").

    Returns:
        A dictionary with the city, temperature in Fahrenheit, condition,
        humidity, and wind speed. On error, returns a dictionary with an
        'error' key explaining what went wrong.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OPENWEATHER_API_KEY is not set in the .env file."}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial",  # use "metric" for Celsius
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException as e:
        return {"error": f"Network error contacting OpenWeather: {e}"}

    if response.status_code == 401:
        return {"error": "Invalid OpenWeather API key (new keys can take up to an hour to activate)."}
    if response.status_code == 404:
        return {"error": f"City '{city}' not found."}
    if response.status_code != 200:
        return {"error": f"OpenWeather returned status {response.status_code}: {response.text}"}

    data = response.json()
    return {
        "city": data.get("name", city),
        "country": data.get("sys", {}).get("country", ""),
        "temp": f"{round(data['main']['temp'])}°F",
        "feels_like": f"{round(data['main']['feels_like'])}°F",
        "condition": data["weather"][0]["description"].title(),
        "humidity": f"{data['main']['humidity']}%",
        "wind_speed": f"{data['wind']['speed']} mph",
    }


root_agent = LlmAgent(
    name="weather_bot",
    model="gemini-2.5-flash",
    description="Provides real-time weather information for any city.",
    instruction=(
        "You are a helpful weather assistant. When a user asks about the weather, "
        "call the get_weather tool with the city name. Summarize the results in a "
        "friendly, conversational way. If the tool returns an 'error' key, "
        "tell the user what went wrong instead of inventing data."
    ),
    tools=[get_weather],
)