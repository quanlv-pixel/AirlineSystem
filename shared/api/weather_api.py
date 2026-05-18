"""
shared/api/weather_api.py
-------------------------
Enhanced Weather Information API.
Maps extreme weather conditions to UI icons and operational risks.
"""
from __future__ import annotations
from shared.api.mock_api import MOCK_WEATHER

def get_weather_by_airport(airport_code: str) -> dict:
    """
    Returns formatted weather data for a specific airport.
    Provides temperature, conditions, delay risk, and UI-ready icons.
    """
    code = airport_code.upper()
    data = MOCK_WEATHER.get(code)
    
    if not data:
        return {
            "airport": code,
            "temperature": 20,
            "condition": "Unknown",
            "delay_risk": "N/A",
            "icon": "❓"
        }
        
    # Map comprehensive conditions to icons for UI usage
    icons = {
        "Sunny": "☀️",
        "Clear": "✨",
        "Cloudy": "☁️",
        "Partly Cloudy": "⛅",
        "Breezy": "🌬️",
        "Drizzle": "🌦️",
        "Rainy": "🌧️",
        "Thunderstorm": "⛈️",
        "Heavy Fog": "🌫️",
        "Typhoon": "🌀",
        "Snowstorm": "❄️",
        "Sandstorm": "🏜️"
    }
    
    return {
        "airport": code,
        "temperature": data["temp"],
        "condition": data["condition"],
        "delay_risk": data["delay_risk"],
        "icon": icons.get(data["condition"], "❓")
    }
