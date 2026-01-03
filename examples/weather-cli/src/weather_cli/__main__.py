"""CLI entry point for weather_cli."""

import argparse
import sys

from rich.console import Console

from .api import WeatherAPI
from .display import display_weather, display_error


def main() -> int:
    """Main entry point for the weather CLI.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        prog="weather_cli",
        description="Fetch and display weather data for any city.",
    )
    parser.add_argument(
        "city",
        help="City name to get weather for (e.g., 'San Francisco')",
    )
    parser.add_argument(
        "--units",
        choices=["metric", "imperial"],
        default="metric",
        help="Temperature units: metric (Celsius) or imperial (Fahrenheit)",
    )

    args = parser.parse_args()
    console = Console()

    try:
        api = WeatherAPI(units=args.units)
        data = api.get_weather_for_city(args.city)

        if data is None:
            display_error(f"City not found: {args.city}", console)
            return 1

        display_weather(data, console)
        return 0

    except Exception as e:
        display_error(str(e), console)
        return 1


if __name__ == "__main__":
    sys.exit(main())
