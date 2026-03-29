# LLM-OVERVIEW: ONE_SHOT

> Supplement to [llms.txt](../llms.txt). This file provides depth that llms.txt summarizes.
> **Primary entry point for any LLM**: [llms.txt](../llms.txt)
>
> **Last Updated**: 2026-03-28
> **ONE_SHOT Version**: 13.2

---

## 1. Philosophy & Design Decisions

1. **Context is scarce** — Fewer commands, on-demand discovery. ~300 tokens always-on vs ~2000 in v9.
2. **Decide autonomously** — Decision defaults prevent constant questions. Ambiguous? Pick simplest, note in DECISIONS.md.
3. **State to disk** — Handoffs survive `/clear`. Tasks persist via native TaskCreate/TaskList.
4. **Operators, not menus** — 3 entry points cover all use cases. Replaced 25+ menu commands.
5. **User time > agent compute** — Make reasonable choices without asking. Don't write scripts when a CLI exists.

---

## 2. Token Optimization Strategy

| Technique | Savings |
|-----------|---------|
| **Progressive disclosure** | Rules load by project type (~300 always-on vs ~2000) |
| **On-demand discovery** | Operators discover skills when needed, not all in memory |
| **State to disk** | Handoffs save progress, don't carry full history |
| **External tools** | `/freesearch` uses Exa API (zero Claude tokens), `/research` uses Gemini CLI |
| **Minimal CLAUDE.md** | Per-project instructions, ~100 lines max |

---

## 3. Multi-Model Orchestration

The `/conduct` operator routes work across three providers:

| Task Type | Provider | Why |
|----------|----------|-----|
| Implementation, planning | Claude (sonnet/opus) | Full context, tool access |
| Adversarial review, challenge | Codex | Fresh perspective, different model |
| Research, documentation | Gemini | Free, different training data |

Protocol: intake questions (blocking) → plan → build loop → verify → adversarial challenge.

---

## 4. Infrastructure & Operations

### Heartbeat (daily)
8 modules run once per day via systemd timer or `heartbeat.sh`:

| Module | What it checks |
|--------|----------------|
| check-oneshot.sh | Repo up to date with origin |
| check-glm.sh | GLM model version pinned and current |
| sync-secrets.sh | SOPS/Age key exists, vault decrypts |
| check-clis.sh | Claude Code, Codex, Gemini CLI installed |
| check-apis.sh | 14 API keys validated with real HTTP calls |
| check-mcps.sh | MCP server processes running |
| check-connections.sh | Tailscale connected, internet reachable |
| check-backup.sh | Encrypted recovery snapshot (vault inventory, machine status, git state) |

Plus cross-machine reachability test (oci-dev, homelab, macmini via SSH aliases).

### Backup Snapshot

Daily encrypted file at `secrets/backup-snapshot.env.encrypted`. Contains NO secret values — only metadata needed to rebuild from scratch: age public key, vault file inventory, machine aliases, active skills, git state, and machine reachability. Includes step-by-step restore instructions. Decrypt with `sops -d --input-type dotenv secrets/backup-snapshot.env.encrypted`.

### Secrets Vault
- **Encryption**: SOPS + Age, one key at `~/.age/key.txt` (600 permissions, same on all 3 machines)
- **Location**: `~/github/oneshot/secrets/*.encrypted` (17 files)
- **Access**: `secrets get KEY` — searches all vault files alphabetically, returns first match
- **Sync**: git push/pull to keep all machines in sync

### Machines
| Alias | User | IP | Role |
|-------|------|----|------|
| oci-dev | ubuntu | 100.126.13.70 | Services, APIs, Claude Code |
| homelab | khamel83 | 100.112.130.100 | Docker, 26TB storage |
| macmini | macmini | 100.113.216.27 | Apple Silicon GPU |

Always use SSH aliases, never raw IPs.

---

## 5. Glossary

| Term | Definition |
|------|------------|
| **Operator** | Entry point skill that orchestrates work (`/short`, `/full`, `/conduct`) |
| **Handoff** | Context snapshot that survives `/clear` — `/handoff` to save, `/restore` to resume |
| **Progressive disclosure** | Loading rules based on project type (web, CLI, service, generic) |
| **Decision defaults** | Pre-set choices for ambiguous situations (simplest implementation, match patterns, skip refactors) |
| **Native Tasks** | Claude Code's built-in task tracking (TaskCreate/TaskGet/TaskUpdate/TaskList) |
| **Skill discovery** | Finding relevant skills on demand from `~/.claude/skills/` index |
| **Vault** | SOPS/Age encrypted directory at `secrets/` — single source of truth for all secrets |
