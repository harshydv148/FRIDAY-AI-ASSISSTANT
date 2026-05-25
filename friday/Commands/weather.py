"""
Weather — OpenWeatherMap API se live weather.
Auto location detection via IP.
"""

import os
import requests
from dotenv import load_dotenv
from friday.voice import speak

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY", "")
FALLBACK_CITY = os.getenv("WEATHER_CITY", "Yamuna Nagar")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str = None) -> dict:
    """Weather data fetch karo."""
    if not city:
        city = get_current_city()

    if not API_KEY:
        return {"error": "Weather API key missing boss. Add WEATHER_API_KEY in .env"}

    try:
        response = requests.get(
            BASE_URL,
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric",
            },
            timeout=5,
        )
        data = response.json()

        if data.get("cod") != 200:
            return {"error": data.get("message", "City not found")}

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"].capitalize(),
            "wind": round(data["wind"]["speed"] * 3.6),
            "min_temp": round(data["main"]["temp_min"]),
            "max_temp": round(data["main"]["temp_max"]),
        }

    except requests.Timeout:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": str(e)}


def format_weather(data: dict) -> str:
    """Weather data ko spoken string mein convert karo."""
    if "error" in data:
        return data["error"]

    return (
        f"{data['description']} in {data['city']}. "
        f"It's {data['temp']}°C right now, "
        f"feels like {data['feels_like']}. "
        f"Humidity is {data['humidity']}%, "
        f"wind at {data['wind']} km/h. "
        f"Today's range — {data['min_temp']} to {data['max_temp']}°C."
    )


def handle_weather_command(user_input: str) -> bool:
    """
    Weather commands handle karo.
    Returns True agar handle hua.
    """
    u = user_input.lower()

    weather_triggers = [
        "weather", "mausam", "temperature",
        "kitni garmi", "kitni sardi", "temp kya hai",
        "bahar kaisa hai", "aaj kaisa mausam",
        "weather kya hai", "mausam kaisa hai",
        "how hot", "how cold", "how's the weather",
        "what's the weather", "aaj ka mausam",
        # Speech recognition variations
        "vedar", "veder", "whether", "wheather",
        "wether", "weader", "vader", "feather",
        "leather", "heather",
    ]

    if not any(t in u for t in weather_triggers):
        return False

    # Specific city mention ki hai kya?
    city = None

    city_keywords = [
        "in ", "mein ", "ka mausam", "ki weather",
        "weather of ", "weather in ",
        "ka weather", "mein weather",
    ]

    for kw in city_keywords:
        if kw in u:
            parts = u.split(kw)
            if len(parts) > 1:
                extracted = parts[-1].strip()
                for remove in ["hai", "kya", "batao", "kaisa", "?"]:
                    extracted = extracted.replace(remove, "").strip()
                if extracted and len(extracted) > 2:
                    city = extracted.title()
                    print(f"🌍 User specified city: {city}")
                    break

    # City nahi mili toh env se lo, auto detect nahi
    if not city:
        city = FALLBACK_CITY

    data = get_weather(city)
    weather_str = format_weather(data)

    print(f"🌤️ FRIDAY: {weather_str}")
    speak(weather_str)

    return True