# Agents Index

ONE_SHOT v10.3 uses skills instead of agents. See `.claude/skills/INDEX.md` for available skills.

---

## Migration Notes

v9 used a directory-based agent system. v10 simplified to:
- **Slash commands** - Invoke via `/skill-name`
- **Skills** - Located in `.claude/skills/`
- **Routing** - Defined in `AGENTS.md`

No standalone agent files are needed in v10+.
