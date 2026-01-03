"""Rich terminal display for weather data."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Weather code to emoji/description mapping (WMO codes)
WEATHER_CODES = {
    0: ("☀️", "Clear sky"),
    1: ("🌤️", "Mainly clear"),
    2: ("⛅", "Partly cloudy"),
    3: ("☁️", "Overcast"),
    45: ("🌫️", "Foggy"),
    48: ("🌫️", "Depositing rime fog"),
    51: ("🌧️", "Light drizzle"),
    53: ("🌧️", "Moderate drizzle"),
    55: ("🌧️", "Dense drizzle"),
    61: ("🌧️", "Slight rain"),
    63: ("🌧️", "Moderate rain"),
    65: ("🌧️", "Heavy rain"),
    71: ("🌨️", "Slight snow"),
    73: ("🌨️", "Moderate snow"),
    75: ("❄️", "Heavy snow"),
    80: ("🌦️", "Slight rain showers"),
    81: ("🌦️", "Moderate rain showers"),
    82: ("⛈️", "Violent rain showers"),
    95: ("⛈️", "Thunderstorm"),
    96: ("⛈️", "Thunderstorm with hail"),
    99: ("⛈️", "Thunderstorm with heavy hail"),
}


def get_wind_direction(degrees: float) -> str:
    """Convert wind direction degrees to cardinal direction."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]


def display_weather(data: dict, console: Console = None) -> None:
    """Display weather data in a nice format.

    Args:
        data: Weather data from API
        console: Rich console (created if not provided)
    """
    if console is None:
        console = Console()

    location = data["location"]
    current = data["current"]
    units = data["units"]

    # Get weather description
    weather_code = current.get("weather_code", 0)
    emoji, description = WEATHER_CODES.get(weather_code, ("❓", "Unknown"))

    # Build the display
    title = f"Weather for {location['name']}, {location['country']}"

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Label", style="dim")
    table.add_column("Value", style="bold")

    # Temperature
    temp = current.get("temperature_2m", "N/A")
    table.add_row("Temperature", f"{temp}{units['temperature']}")

    # Conditions
    table.add_row("Conditions", f"{emoji} {description}")

    # Humidity
    humidity = current.get("relative_humidity_2m", "N/A")
    table.add_row("Humidity", f"{humidity}%")

    # Wind
    wind_speed = current.get("wind_speed_10m", "N/A")
    wind_dir = current.get("wind_direction_10m", 0)
    wind_cardinal = get_wind_direction(wind_dir)
    table.add_row("Wind", f"{wind_speed} {units['wind']} {wind_cardinal}")

    panel = Panel(table, title=title, border_style="blue")
    console.print(panel)


def display_error(message: str, console: Console = None) -> None:
    """Display an error message.

    Args:
        message: Error message to display
        console: Rich console (created if not provided)
    """
    if console is None:
        console = Console()

    console.print(f"[red]Error:[/red] {message}")
