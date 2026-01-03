"""Weather API client using Open-Meteo (free, no API key required)."""

import requests
from typing import Optional


class WeatherAPI:
    """Client for Open-Meteo weather API."""

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, units: str = "metric"):
        """Initialize the weather client.

        Args:
            units: 'metric' (Celsius) or 'imperial' (Fahrenheit)
        """
        self.units = units
        self.temp_unit = "celsius" if units == "metric" else "fahrenheit"
        self.wind_unit = "kmh" if units == "metric" else "mph"

    def geocode(self, city: str) -> Optional[dict]:
        """Get coordinates for a city name.

        Args:
            city: City name to search for

        Returns:
            Dict with lat, lon, name, country or None if not found
        """
        response = requests.get(
            self.GEOCODING_URL,
            params={"name": city, "count": 1, "language": "en"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            return None

        result = data["results"][0]
        return {
            "lat": result["latitude"],
            "lon": result["longitude"],
            "name": result["name"],
            "country": result.get("country", ""),
        }

    def get_weather(self, lat: float, lon: float) -> dict:
        """Get current weather for coordinates.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Weather data dict
        """
        response = requests.get(
            self.WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m",
                ],
                "temperature_unit": self.temp_unit,
                "wind_speed_unit": self.wind_unit,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_weather_for_city(self, city: str) -> Optional[dict]:
        """Get weather for a city by name.

        Args:
            city: City name

        Returns:
            Combined location and weather data, or None if city not found
        """
        location = self.geocode(city)
        if not location:
            return None

        weather = self.get_weather(location["lat"], location["lon"])

        return {
            "location": location,
            "current": weather.get("current", {}),
            "units": {
                "temperature": "°C" if self.units == "metric" else "°F",
                "wind": "km/h" if self.units == "metric" else "mph",
            },
        }
