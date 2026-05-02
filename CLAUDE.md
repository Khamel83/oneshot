# OneShot Project Instructions

## Operator Rules
See @docs/instructions/core.md
See @docs/instructions/workflow.md
See @docs/instructions/coding.md
See @docs/instructions/search.md
See @docs/instructions/review.md
See @docs/instructions/secrets.md

## Project-Specific
See @docs/instructions/oneshot.md

## Harness Eval & Traces
After changing `core/task_schema.py`, `config/lanes.yaml`, or routing code: run `./scripts/eval.sh`. Fix any regression before moving on.
Full reference: `docs/meta-harness/eval_framework.md`, `docs/meta-harness/trace_architecture.md`

## My Active Projects

| Project | What it does | Where | Status |
|---------|-------------|-------|--------|
| **oneshot** | Orchestration control plane — Claude + workers, skills, routing | MBA | Active dev |
| **atlas** | Knowledge ingestion: podcasts, articles, Gmail → 440K searchable chunks | oci-dev, 13 timers | Production |
| **penny** | Voice memo → classify → route (Telegram, Keep, TrojanHorse…) | oci-dev | Production |
| **poytz** | URL routing: khamel.com/* → homelab services | Cloudflare Workers | Live |
| **homelab** | All Docker infra, Makefile ops, 26TB storage | homelab server | Running |
| **argus** | Search plane: SearXNG+Brave+Exa+Tavily, MCP+HTTP | homelab:8270 | Running |
| **n8n** | Workflow automation | homelab / khamel.com/workflows | Running |
| **networth** | Tennis ladder platform | Vercel + Supabase | Production |
| **ralex** | Multi-model chat: Claude + 10 OpenRouter models | local | Active |
| **kid-friendly-ai** | Kids voice assistant (ElevenLabs) | buddy.khamel.com | Production |
| **Argus corpus** | Canonical docs and research corpus for `/doc`, search, and MCP workflows | homelab appdata + optional local mirror | Running |
| **archon** | RAG knowledge base + MCP server | local | MVP |
| **atlas-voice** | Writing-style model from Atlas corpus | local | Active |
| **oos** | Dev workflow context optimizer | local | Active |
| **dada** | Family comms: video/audio → Telegram | local | Planned |
| **divorce** | SB 1427 joint petition tooling | local | Personal |

Dormant (keep): `atlas_researcher`, `vig`, `WFM`
Full services catalog: `~/github/homelab/docs/SERVICES.md`

## Tool-Specific (Claude Code)
See @.claude/rules/khamel-mode.md
- For code-change requests, dispatch via /dispatch — see @.claude/rules/delegation-enforcement.md
- Codex setup/auth reference: `.claude/rules/codex.md`

## Project Intelligence
Need to understand what's been happening? Start here:

| Question | Look at |
|----------|---------|
| What's the current state of the project? | `CLAUDE.local.md` (auto-generated onboarding summary) |
| What type is this project? | `.janitor/project-type.json` (code, document, or hybrid) |
| What files were changed recently? | `.janitor/events.jsonl` — grep for `file_written` or `commit` |
| What decisions were made? | `.janitor/events.jsonl` — grep for `decision` |
| What's broken or stuck? | `.janitor/events.jsonl` — grep for `blocker` or `dead_end` |
| What approaches already failed? | `.janitor/events.jsonl` — grep for `dead_end` |
| What files have no tests? | `.janitor/test-gaps.json` (code/hybrid) |
| What files are too big? | `.janitor/code-smells.json` (code/hybrid) |
| What config is uncommitted? | `.janitor/config-drift.json` |
| What files have the most dependents? | `.janitor/dep-graph.json` (code/hybrid) |
| What patterns repeat across sessions? | `.janitor/patterns.json` |
| What documents are stale? | `.janitor/doc-staleness.json` (document/hybrid) |
| What documents are orphaned? | `.janitor/doc-orphans.json` (document/hybrid) |
| What documents link to what? | `.janitor/doc-crossrefs.json` (document/hybrid) |
| What documents changed recently? | `.janitor/doc-recent-activity.json` (document/hybrid) |
| What are the document clusters? | `.janitor/doc-clusters.json` (document/hybrid) |
| What files are unusually large? | `.janitor/doc-size-outliers.json` (all types) |
| What files are touched most? | `.janitor/critical-files.json` (all types) |
| What files have bus-factor risk? | `.janitor/knowledge-risk.json` (all types) |
