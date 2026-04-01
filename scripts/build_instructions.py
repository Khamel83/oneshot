"""Build CLAUDE.md from docs/instructions/ source files.

Usage:
    python scripts/build_instructions.py          # generate CLAUDE.md
    python scripts/build_instructions.py --check  # validate @imports exist
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTRUCTIONS_DIR = ROOT / "docs" / "instructions"
CLAUDE_MD = ROOT / "CLAUDE.md"

INSTRUCTION_FILES = ["core", "workflow", "coding", "search", "review"]
PROJECT_FILE = "oneshot"


def build_claude_md() -> None:
    """Generate CLAUDE.md as thin @imports to docs/instructions/."""
    sections = [
        "# OneShot Project Instructions\n",
        "",
        "## Operator Rules\n",
    ]
    for name in INSTRUCTION_FILES:
        path = INSTRUCTIONS_DIR / f"{name}.md"
        if path.exists():
            sections.append(f"See @{path}\n")
        else:
            print(f"Warning: {path} does not exist", file=sys.stderr)

    sections.append("\n## Project-Specific\n")
    path = INSTRUCTIONS_DIR / f"{PROJECT_FILE}.md"
    if path.exists():
        sections.append(f"See @{path}\n")
    else:
        print(f"Warning: {path} does not exist", file=sys.stderr)

    CLAUDE_MD.write_text("\n".join(sections))
    print(f"Generated {CLAUDE_MD}")


def check_imports() -> bool:
    """Validate that all @imports in CLAUDE.md reference existing files."""
    content = CLAUDE_MD.read_text()
    ok = True

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("See @"):
            ref = line[5:]
            path = ROOT / ref
            if not path.exists():
                print(f"Broken import: {ref}", file=sys.stderr)
                ok = False

    return ok


def main():
    parser = argparse.ArgumentParser(description="Build/regenerate CLAUDE.md")
    parser.add_argument("--check", action="store_true", help="Validate @imports only")
    args = parser.parse_args()

    if args.check:
        ok = check_imports()
        sys.exit(0 if ok else 1)
    else:
        build_claude_md()


if __name__ == "__main__":
    main()
