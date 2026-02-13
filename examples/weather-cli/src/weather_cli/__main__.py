"""CLI entry point for weather_cli."""

import sys

import click

from .api import WeatherAPI
from .display import display_error, display_weather


@click.command()
@click.argument("city")
@click.option(
    "--units",
    type=click.Choice(["metric", "imperial"], case_sensitive=False),
    default="metric",
    show_default=True,
    help="Temperature units",
)
def main(city: str, units: str) -> None:
    """Fetch and display weather data for any CITY.

    Example: weather-cli "San Francisco" --units imperial
    """
    try:
        api = WeatherAPI(units=units)
        data = api.get_weather_for_city(city)

        if data is None:
            display_error(f"City not found: {city}")
            sys.exit(1)

        display_weather(data)
        sys.exit(0)

    except Exception as e:
        display_error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
