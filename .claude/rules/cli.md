# Coding Standards

**Authoritative source**: `docs/instructions/coding.md`

See @docs/instructions/coding.md

## Claude-Specific Additions

- When detecting project type, check for `*.service` files last (some repos have unrelated .service files)
- For web apps: always verify `package.json` has `astro` before using web rules
