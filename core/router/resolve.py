"""CLI resolver - resolve a task class to a routing directive.

Usage:
    python -m core.router.resolve --class implement_small
    python -m core.router.resolve --class implement_small --category coding
    python -m core.router.resolve --class research
"""

import argparse
import json
import sys

from core.router.lane_policy import resolve


def main():
    parser = argparse.ArgumentParser(description="Resolve task class to routing directive")
    parser.add_argument("--class", dest="task_class", required=True,
                        help="Task class (plan, research, implement_small, etc.)")
    parser.add_argument("--category", default=None,
                        help="Task category override (coding, research, writing, review, general)")
    parser.add_argument("--config", default=None,
                        help="Path to config directory")
    args = parser.parse_args()

    try:
        result = resolve(args.task_class, category=args.category, config_path=args.config)
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
