# Lessons System

At session start, check for past lessons before diving in:

```bash
cd ~/.claude && bd list -l lesson --json 2>/dev/null | jq -r '.[] | "- \(.title): \(.description | split("\n")[0])"' | head -10
```

If lessons exist for the current domain (debugging, deployment, config, etc.), announce them:
"Note: We've seen similar issues before: [lesson title]"

After fixing bugs or discovering gotchas, suggest: "Save this as a lesson? Say `/oops`"
