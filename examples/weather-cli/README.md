# Weather CLI

**Built with ONE_SHOT in 6 iterations.**

A simple Python CLI that fetches weather data and displays it nicely in the terminal.

## What This Demonstrates

This example shows what a completed ONE_SHOT autonomous build looks like:

```bash
oneshot-build "A Python CLI that fetches weather data and displays it nicely"
```

The agent:
1. Interviewed itself (front-door skill)
2. Created a structured plan
3. Parsed plan into 6 beads tasks
4. Implemented each task, committing after every file
5. Completed in 6 iterations

## Usage

```bash
# Install in development mode
pip install -e .

# Get weather for a city
weather-cli "San Francisco"

# Get weather with units
weather-cli "London" --units imperial

# Or using Python module
python -m weather_cli "Tokyo"
```

## Project Structure

```
weather-cli/
├── README.md              # This file
├── pyproject.toml         # Modern Python packaging
├── requirements.txt       # Dependencies (for pip install -r)
├── src/
│   └── weather_cli/
│       ├── __init__.py
│       ├── __main__.py    # CLI entry point
│       ├── api.py         # Weather API client
│       └── display.py     # Terminal display
├── .agent/
│   └── STATUS.md          # Build status from autonomous run
└── thoughts/plans/
    └── weather-cli.md     # The plan that was executed
```

## How It Was Built

### The Prompt

```
"A Python CLI that fetches weather data and displays it nicely"
```

### What ONE_SHOT Did

1. **front-door**: Asked clarifying questions (answered with reasonable defaults)
   - Which weather API? → Open-Meteo (free, no API key)
   - Output format? → Rich terminal display
   - Features? → City search, current weather, basic forecast

2. **create-plan**: Generated structured plan with 6 tasks

3. **implement-plan**: Executed each task via beads tracking
   - Task 1: Project structure + requirements.txt
   - Task 2: Weather API client
   - Task 3: Display formatting
   - Task 4: CLI with Click (argument parsing)
   - Task 5: Main entry point
   - Task 6: Error handling

4. **Completed**: All tasks closed, final status written

### Build Stats

- **Iterations**: 6
- **Time**: ~3 minutes
- **Commits**: 6 (one per task)
- **Status**: SUCCESS

## Files Created by ONE_SHOT

- `.agent/STATUS.md` - Real-time progress log
- `thoughts/plans/weather-cli.md` - The implementation plan

## Recreate This Example

```bash
cd examples/weather-cli
oneshot-build "A Python CLI that fetches weather data and displays it nicely"
```

Note: Results may vary slightly based on Claude's decisions, but the structure and approach will be similar.
