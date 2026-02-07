# /diagnose — Structured Hypothesis-Based Debugging

Systematic debugging using isolation and evidence-based diagnosis.

## Workflow

### 1. Gather Symptoms
- What error message (exact text)?
- Expected vs actual behavior?
- When did it last work?
- What changed since then?

### 2. Reproduce the Issue
- Run the failing command/action
- Capture full error output
- Note environment details

### 3. Isolate the Layer

```
Network → Process → Config → Dependencies → Data → Code
```

- Can you reach the service? (`curl`, `nc -zv`)
- Is the process running? (`systemctl status`, `docker ps`)
- Any recent config changes?
- All dependencies up? (`pip list`, `npm ls`)
- Database accessible? (`sqlite3 db ".tables"`)
- Logic error in code?

### 4. Check Past Lessons

```bash
cd ~/.claude && bd list -l lesson --json 2>/dev/null | jq -r '.[] | select(.labels | any(test("LAYER_TAG"))) | "- \(.title)"'
```

If a matching lesson exists, announce it and verify applicability.

### 5. Form Hypothesis

Based on evidence, what's the most likely cause? What's the simplest test to confirm/refute?

### 6. Test Hypothesis

Make minimal change to test. Observe result. If wrong, return to step 3.

### 7. Apply Fix

Smallest change that fixes the issue. Do NOT refactor while debugging.

### 8. Verify and Document

Confirm fix works. After fixing, suggest: "Save this as a lesson? Say `/oops`"

## Quick Reference

| Symptom | Likely Cause | Check |
|---------|-------------|-------|
| Connection refused | Service not running | `systemctl status` |
| 404 | Wrong URL/route | Check routes config |
| 500 | Unhandled exception | Check logs |
| Timeout | Slow query/network | Profile, check latency |
| Permission denied | File permissions | `ls -la` |
| Module not found | Missing dependency | `pip list`, `npm ls` |

## Anti-Patterns

- Multiple changes at once (can't isolate what fixed it)
- Refactoring while debugging
- Assuming cause without evidence
- Not checking logs first
