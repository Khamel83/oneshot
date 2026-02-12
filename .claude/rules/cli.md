# CLI Rules (Python + Click + SQLite)

## Default Stack

When building CLIs for this user:

```
Python + Click + SQLite
```

## When to Use

Detect by presence of:
- `setup.py` or `pyproject.toml`
- CLI entry points defined
- No `astro.config.*` or `wrangler.toml` or web framework files

## Click-Specific Rules

- **Use Click for CLI** - Don't suggest argparse, typer, or other CLI libs
- **Command groups** - Use `@click.group()` for multi-command CLIs
- **Context objects** - Use `@click.pass_context` for shared state
- **Auto-completion** - Add shell completion support

## SQLite-Specific Rules

- **SQLite is default** - Don't suggest PostgreSQL, MongoDB
- **Use sqlite3 module** - No ORM needed for simple CLIs
- **Migrations** - Simple schema versioning, avoid heavy migration tools

## Packaging

- **pip install -e .** - For development
- **pyproject.toml** - Modern packaging standard
- **Entry points** - Define console scripts in pyproject.toml

## Anti-Patterns

- ❌ Don't suggest web frameworks (FastAPI, Flask)
- ❌ Don't suggest external databases
- ❌ Don't suggest Docker for local development
- ❌ Don't suggest complex ORMs (SQLAlchemy, Django ORM)
