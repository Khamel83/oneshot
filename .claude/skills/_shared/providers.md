# Shared Provider Routing Module

Reference this module from any skill that needs delegation or multi-model routing.
This is a DRY reference — skills include it by mention, not import.

---

## Provider Detection

```bash
command -v codex >/dev/null 2>&1 && echo "codex: yes" || echo "codex: no"
command -v gemini >/dev/null 2>&1 && echo "gemini: yes" || echo "gemini: no"
[ -d ~/github/claw-code-agent/src ] && echo "claw_code: yes" || echo "claw_code: no"
python -c "from core.search.argus_client import is_available; print('argus:', is_available())" 2>/dev/null || echo "argus: no"
```

Also read `config/workers.yaml` for machine-level worker placement.

---

## Lane-Based Routing

**Route by task class, not provider name.** See `docs/instructions/task-classes.md`.

```
task → task_class → lane → worker_pool → reviewer
```

Resolve routing:
```bash
python -m core.router.resolve --class <task_class>
```

Returns JSON: `{task_class, lane, workers[], review_with, search_backend, fallback_lane}`

---

## Lane Summary

| Lane | Planner | Workers | Review |
|------|---------|---------|--------|
| premium | claude_code | claude_code, codex | claude_code |
| balanced | claude_code | opencode_gemini_flash, codex, opencode_minimax | claude_code |
| cheap | claude_code | claw_code, gemini_cli, codex | claude_code |
| research | claude_code | gemini_cli, opencode_gemini_flash_lite | claude_code |

---

## Dispatch Commands

**Codex** (adversarial review, challenge, worker tasks):

Structured output (preferred for all programmatic dispatch):
```bash
unset OPENAI_API_KEY && codex exec --json --sandbox danger-full-access "PROMPT"
# Returns JSONL stream: thread.started, turn.started, item.*, turn.completed
# Parse final agent message:  | jq 'select(.type == "item.completed") | select(.item.type == "agent_message")'
```

Quick single-run with last-message capture:
```bash
unset OPENAI_API_KEY && codex exec --sandbox danger-full-access -o /tmp/codex-output.txt "PROMPT"
```

Structured output with schema (for downstream processing):
```bash
unset OPENAI_API_KEY && codex exec --sandbox danger-full-access --output-schema ./schema.json -o ./result.json "PROMPT"
```

Resume a previous session:
```bash
unset OPENAI_API_KEY && codex exec resume --last "follow-up prompt"
```

**Gemini** (research fallback):
```bash
printf '%s' "PROMPT" | gemini -p "" -o text --approval-mode yolo
```

**Claw Code** (OpenRouter models — cheap lane):
```bash
cd ~/github/claw-code-agent && \
OPENAI_BASE_URL=https://openrouter.ai/api/v1 \
OPENAI_MODEL=openai/gpt-4o-mini \
python3 -m src.main agent "PROMPT" --cwd /path/to/repo --allow-write --allow-shell
```
Model is configurable via `OPENAI_MODEL` env var or `--model` flag on dispatch.
See `config/models.yaml` `claw_code` section for supported models.

**Argus** (search):
```bash
curl -s -X POST http://localhost:8005/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "QUERY", "mode": "discovery"}'
```

---

## Worker Placement

From `config/workers.yaml`:
- `local` (localhost) — planner, claude_code
- `oci` (oci-dev) — planner, claude_code
- `claw` (localhost) — worker, claw_code (OpenRouter models)
- `macmini` — worker, opencode (future)
- `homelab` — worker, opencode (future)

Dispatch to remote worker via SSH when configured.

---

## Quality Gate

75% consensus required when multiple providers contribute. If not reached:
- Log disagreement to `1shot/ISSUES.md`
- Claude makes final call

---

## Circuit Breaker

- Same task fails 3x → log blocker → skip → continue
- 3 consecutive tasks fail → stop, surface to user
- Lane escalation: cheap → balanced → premium → inline (Claude handles directly)
