# Shared Provider Routing Module

Reference this module from any skill that needs delegation or multi-model routing.
This is a DRY reference — skills include it by mention, not import.

---

## Provider Detection

```bash
command -v codex >/dev/null 2>&1 && echo "codex: yes" || echo "codex: no"
command -v gemini >/dev/null 2>&1 && echo "gemini: yes" || echo "gemini: no"
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
| cheap | claude_code | opencode_stepfun_flash, opencode_mimo_flash, opencode_minimax | claude_code |
| research | claude_code | gemini_cli, opencode_gemini_flash_lite | claude_code |

---

## Dispatch Commands

**Codex** (adversarial review, challenge):
```bash
unset OPENAI_API_KEY && codex exec --sandbox danger-full-access "PROMPT"
```

**Gemini** (research fallback):
```bash
printf '%s' "PROMPT" | gemini -p "" -o text --approval-mode yolo
```

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
