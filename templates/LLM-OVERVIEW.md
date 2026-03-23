# LLM-OVERVIEW: [PROJECT NAME]

> Complete context for any LLM to understand this project.
> **Last Updated**: [date]
> **Status**: [Active Development / Stable / Archived]

---

## 1. WHAT IS THIS?

### One-Line Description
[One sentence: what does this project do?]

### The Problem It Solves
[2-3 sentences on why this exists and what it replaces or improves]

### Current State
- **Status**: [what's working]
- **Stack**: [key technologies]
- **Deploy target**: [where it runs]

---

## 2. ARCHITECTURE

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | [e.g. Astro + Cloudflare Pages] |
| **Backend** | [e.g. Python + systemd on oci-dev] |
| **Database** | [e.g. SQLite / Postgres on OCI] |
| **Auth** | [e.g. Better Auth + Google OAuth] |
| **Secrets** | SOPS/Age |

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| [name] | [what it does] | [file/dir] |

### How It Fits Together
[2-4 sentences describing the data flow or main interactions between components]

---

## 3. KEY FILES

| File | Purpose |
|------|---------|
| `AGENTS.md` | ONE_SHOT operator spec |
| `CLAUDE.md` | Project-specific Claude instructions |
| `1shot/PROJECT.md` | Current project goals and acceptance criteria |
| `1shot/STATE.md` | Current phase and loop state |
| [other key files] | [purpose] |

---

## 4. HOW TO RUN

```bash
# Install / setup
[command]

# Run locally
[command]

# Run tests
[command]

# Deploy
[command]
```

---

## 5. CURRENT STATE

### What Works
- [working feature]
- [working feature]

### In Progress
- [what's being built]

### Known Issues / Limitations
- [issue]

---

## 6. CONVENTIONS

- **Naming**: [e.g. snake_case for files, camelCase for functions]
- **Commits**: [e.g. feat/fix/chore prefix]
- **Branching**: [e.g. feature branches off master]
- **Secrets**: All secrets via SOPS/Age — never commit plaintext

---

## 7. RELATED PROJECTS

| Project | Relationship |
|---------|--------------|
| [ONE_SHOT](https://github.com/Khamel83/oneshot) | Operator framework used here |

---

**Last Updated**: [date]
**Maintainer**: @Khamel83
