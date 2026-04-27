#!/usr/bin/env python3
"""validate-agents.py - Validate agent files in .claude/agents/

Checks:
- Frontmatter exists (starts with ---)
- Has required fields: name, description
- Has closing frontmatter
- Line count in reasonable range (20-500)
"""

import sys
import os
from pathlib import Path

AGENTS_DIR = Path(".claude/agents")
SKIP_FILES = {"INDEX.md", "TEMPLATE.md"}


def validate_agent(filepath: Path) -> list[str]:
    errors = []
    name = filepath.stem

    lines = filepath.read_text().splitlines()

    if not lines or lines[0].strip() != "---":
        errors.append(f"{name}: Missing frontmatter (must start with ---)")
        return errors

    content = "\n".join(lines)

    if "name:" not in content.split("---")[1].split("---")[0]:
        errors.append(f"{name}: Missing 'name:' field in frontmatter")

    if "description:" not in content.split("---")[1].split("---")[0]:
        errors.append(f"{name}: Missing 'description:' field in frontmatter")

    if content.count("---") < 2:
        errors.append(f"{name}: Missing closing frontmatter (---)")

    line_count = len(lines)
    if line_count < 20:
        errors.append(f"{name}: Too short ({line_count} lines, minimum 20)")
    elif line_count > 500:
        errors.append(f"{name}: Too long ({line_count} lines, maximum 500)")

    return errors


def main():
    if not AGENTS_DIR.exists():
        print(f"ERROR: {AGENTS_DIR} directory not found")
        sys.exit(1)

    agent_files = sorted(AGENTS_DIR.glob("*.md"))
    if not agent_files:
        print("No agent files found")
        sys.exit(1)

    total_errors = 0
    total_agents = 0

    print(f"Validating agents in {AGENTS_DIR}...")
    print()

    for filepath in agent_files:
        if filepath.name in SKIP_FILES:
            continue

        total_agents += 1
        errors = validate_agent(filepath)

        if errors:
            for e in errors:
                print(f"  ERROR: {e}")
            total_errors += len(errors)
        else:
            line_count = len(filepath.read_text().splitlines())
            print(f"  OK: {filepath.name} ({line_count} lines)")

    print()
    if total_errors == 0:
        print(f"All {total_agents} agent(s) validated successfully")
        sys.exit(0)
    else:
        print(f"Found {total_errors} error(s) across {total_agents} agent(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
