# Plan: Weather CLI

**Created**: 2025-01-03
**Status**: Completed

## Overview

Build a Python CLI that fetches weather data and displays it nicely in the terminal.

## Decisions Made

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Weather API | Open-Meteo | Free, no API key required |
| Display | Rich library | Beautiful terminal output |
| Units | Configurable | Support both metric and imperial |

## Architecture

```
weather_cli/
├── __init__.py      # Package init
├── __main__.py      # CLI entry point
├── api.py           # Weather API client
└── display.py       # Terminal display
```

## Tasks

### Group 1: Setup
1. **Create project structure** - requirements.txt, package directories
   - Dependencies: requests, rich

### Group 2: Core
2. **Implement weather API client** - Open-Meteo geocoding + forecast
   - Geocode city name → lat/lon
   - Fetch current weather data

3. **Create display formatting** - Rich panels and tables
   - Weather code → emoji mapping
   - Wind direction conversion

### Group 3: Integration
4. **Add CLI argument parsing** - argparse with city and units
5. **Create main entry point** - Wire together API and display
6. **Add error handling** - Network errors, city not found

## Success Criteria

- [ ] `python -m weather_cli "London"` shows current weather
- [ ] `--units imperial` shows Fahrenheit
- [ ] Invalid city shows helpful error
- [ ] Network errors handled gracefully

## Notes

- Using Open-Meteo because it's free and doesn't require API key
- Rich library provides nice terminal formatting out of the box
- Weather codes follow WMO standard
