"""Weather tool — fetches current conditions from OpenWeatherMap.

Supports single or multi-city lookups. Multi-city lookups run in parallel
via a thread pool so latency is roughly one round-trip regardless of count.
"""

import concurrent.futures
import os
from typing import List, Union

import requests

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
TIMEOUT_SECONDS = 10
MAX_PARALLEL = 8

# US state codes — these confuse OpenWeather, which expects ISO country
# codes after the comma. Strip them so "Chicago, IL" → "Chicago, IL, US".
_US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
}

# Added this as most people type "city, state" but weather app will reject it.
# We will add the country so it is accepted.
def _normalize_city(city: str) -> str:
    """Normalize a city string for OpenWeather's API.

    OpenWeather accepts:  "Chicago"  or  "Chicago,US"  or  "Chicago,IL,US"
    OpenWeather rejects:  "Chicago, IL"   (US state alone, no country)

    This helper detects US state codes and appends ",US" so the lookup
    succeeds.
    """
    parts = [p.strip() for p in city.split(",")]

    # Single part — pass through unchanged
    if len(parts) == 1:
        return parts[0]

    # Two parts where the second is a US state → add country
    if len(parts) == 2 and parts[1].upper() in _US_STATE_CODES:
        return f"{parts[0]},{parts[1].upper()},US"

    # Already has 3 parts (city, state, country) → rejoin without spaces
    if len(parts) >= 3:
        return ",".join(parts)

    # Two parts where second is a country code → rejoin without space
    return f"{parts[0]},{parts[1]}"

def _fetch_one_weather(city: str) -> dict:
    """Fetch weather for a single city. Always returns a dict.

    On any failure, returns a dict with an 'error' key so the calling
    agent can describe the problem to the user instead of crashing.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"city": city, "error": "OPENWEATHER_API_KEY not set in .env"}

    try:
        response = requests.get(
            OPENWEATHER_URL,
            params={"q": _normalize_city(city), "appid": api_key, "units": "imperial"},
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as e:
        return {"city": city, "error": f"Network error: {e}"}

    if response.status_code == 401:
        return {
            "city": city,
            "error": (
                "Invalid OpenWeather API key. New keys can take up to an "
                "hour to activate after signup."
            ),
        }
    if response.status_code == 404:
        return {"city": city, "error": f"City '{city}' not found."}
    if response.status_code != 200:
        return {
            "city": city,
            "error": f"OpenWeather returned status {response.status_code}.",
        }

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


def get_weather(cities: Union[str, List[str]]) -> dict:
    """Get current weather for one or more cities, in parallel.

    Args:
        cities: A single city name (e.g. "Tokyo") OR a list of city names
            (e.g. ["Tokyo", "Paris", "London"]). When multiple cities are
            given, lookups run concurrently for speed.

    Returns:
        A dictionary with a 'results' key containing one weather report per
        city. Each report has either weather fields (city, country, temp,
        feels_like, condition, humidity, wind_speed) or an 'error' key
        explaining what went wrong for that specific city.
    """
    city_list = [cities] if isinstance(cities, str) else list(cities)

    if not city_list:
        return {"results": [], "error": "No cities provided."}

    worker_count = min(MAX_PARALLEL, len(city_list))
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as pool:
        results = list(pool.map(_fetch_one_weather, city_list))

    return {"results": results}
