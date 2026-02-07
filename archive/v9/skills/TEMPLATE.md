# Skill Template

Use this template when creating new skills for ONE_SHOT.

---

## Template

```markdown
---
name: skill-name
description: "Brief description. Use when user says 'trigger1', 'trigger2', or 'trigger3'."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Skill Name

You are an expert at [domain].

## When To Use

- User says "[trigger phrase 1]"
- User says "[trigger phrase 2]"
- [Situation that warrants this skill]

## Inputs

- [Input 1]
- [Input 2]

## Outputs

- [Output 1]
- [Output 2]

## Workflow

### 1. [First Step]

[Description]

### 2. [Second Step]

[Description]

### 3. [Third Step]

[Description]

## [Key Concept]

[Table, code example, or reference]

## Anti-Patterns

- [What NOT to do]
- [Common mistake]

## Keywords

keyword1, keyword2, keyword3
```

---

## Guidelines

### Naming
- Use kebab-case: `my-skill-name`
- Be specific: `api-designer` not `designer`
- Avoid generic names: `helper`, `utils`

### Description
- Start with verb: "Design", "Handle", "Create"
- Include 2-3 trigger phrases in quotes
- Keep under 200 characters

### Allowed Tools
- Only include tools the skill actually needs
- `Read` - almost always needed
- `Write` - for creating new files
- `Edit` - for modifying existing files
- `Bash` - for running commands
- `Glob` - for finding files by pattern
- `Grep` - for searching file contents
- `Task` - for spawning sub-agents (use sparingly)

### Content
- Target 150-250 lines
- Include practical examples
- Use tables for quick reference
- Add anti-patterns section
- End with keywords for discoverability

### Workflow
- 3-5 clear steps
- Each step actionable
- Include decision points

---

## Checklist for New Skills

- [ ] Unique name (not overlapping with existing skills)
- [ ] Clear trigger phrases
- [ ] Minimal tool set (only what's needed)
- [ ] Practical examples included
- [ ] Anti-patterns documented
- [ ] Keywords for discoverability
- [ ] Added to AGENTS.md skill router
- [ ] Added to oneshot.sh SKILLS array
- [ ] Added to INDEX.md
- [ ] Tested with Claude Code
