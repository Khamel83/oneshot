# MCP Quota Awareness - Best Practices

**Last Updated**: 2026-02-02

ZAI MCP servers have quota limits. This guide helps you use them efficiently and avoid interruptions.

---

## Quota Tiers

| Plan Tier | Web Search + Zread | Vision Pool | Monthly Cost |
|-----------|-------------------|-------------|--------------|
| Lite | 100 total/month | 5 hours | Free/TBD |
| Pro | 1,000 total/month | 5 hours | TBD |
| Max | 4,000 total/month | 5 hours | TBD |

**Important**: Web Search and Zread share a combined quota. Vision has a separate quota.

---

## Check Quota Status

### Via ZAI CLI

```bash
# If ZAI CLI is installed
zai quota

# Example output:
# Web Search + Zread: 47/100 used (53 remaining)
# Vision Pool: 2.3h/5h used
```

### Via Dashboard

Visit: https://dashboard.z.ai/

---

## Quota-Smart Strategies

### 1. Prefer MCP Over Built-in Tools

**When quota is healthy (>50% remaining):**
- Use Web Search MCP instead of WebSearch
- Use Zread MCP instead of git clone
- Use Vision MCP for all image analysis

**When quota is low (<20% remaining):**
- Use built-in WebSearch for research
- Use git clone for GitHub repos
- Use manual description for image analysis

### 2. Batch Requests

Combine multiple queries into single requests:

**INEFFICIENT** (3 API calls):
```bash
webSearchPrime("Python async best practices")
webSearchPrime("FastAPI async patterns")
webSearchPrime("asyncio error handling")
```

**EFFICIENT** (1 API call):
```bash
webSearchPrime("Python async best practices, FastAPI async patterns, and asyncio error handling")
```

### 3. Cache Results Locally

Store MCP results in `findings.md` to avoid re-searching:

```markdown
## MCP-Enabled Research

### Web Search (via webSearchPrime)
- **Query**: "Python async best practices"
- **Results**: [cached results here]
- **Date**: 2026-02-02

# Next time, read from findings.md instead of re-searching
```

### 4. Prioritize High-Value Queries

Use MCP for:
- Latest documentation (changes frequently)
- Complex GitHub repos (large, hard to navigate)
- Error screenshots (hard to describe in text)

Use built-in tools for:
- Stable documentation (changes rarely)
- Small repos (easy to clone)
- Simple images (easy to describe)

---

## Quota Tracking Template

Add to your project's `progress.md`:

```markdown
## MCP Quota Tracking

### Current Status
- **Web Search + Zread**: X/100 used
- **Vision Pool**: Xh/5h used
- **Last Checked**: YYYY-MM-DD

### This Session
- **Web Search calls**: X
- **Zread calls**: X
- **Vision calls**: X
- **Total MCP calls**: X

### Recommendations
- [ ] Continue using MCP (quota healthy)
- [ ] Switch to built-in tools (quota low)
- [ ] Upgrade plan (quota exhausted)
```

---

## Fallback Patterns

### Web Search Fallback

```python
# Try MCP first
try:
    results = webSearchPrime(query)
except QuotaExceeded:
    # Fallback to built-in
    results = WebSearch(query)
```

### Zread Fallback

```python
# Try MCP first
try:
    structure = get_repo_structure(repo)
except QuotaExceeded:
    # Fallback to git clone
    run("git clone https://github.com/{repo}.git")
    structure = glob("**/*.py")
```

### Vision Fallback

```python
# Try MCP first
try:
    analysis = diagnose_error_screenshot(image)
except QuotaExceeded:
    # Fallback to manual description
    analysis = "User describes error: {description}"
```

---

## Emergency Actions

### Quota Exceeded Mid-Session

1. **Check remaining quota**:
   ```bash
   zai quota
   ```

2. **Switch to fallback tools**:
   - Web Search MCP → WebSearch
   - Zread MCP → git clone + Glob/Grep
   - Vision MCP → manual description

3. **Document the switch** in `progress.md`:
   ```markdown
   ## MCP Fallback Activated
   - **Reason**: Quota exceeded
   - **Fallback tools**: WebSearch, git clone
   - **Resume MCP**: Next month
   ```

### Upgrade Plan

If quota is consistently exhausted:

1. Visit: https://dashboard.z.ai/billing
2. Upgrade to next tier
3. Update `quota-aware.md` with new limits

---

## Examples

### Efficient Research Session

```bash
# Batch query (1 API call)
webSearchPrime("FastAPI async patterns, error handling, and testing")

# Cache results
echo "- **Query**: 'FastAPI async...' - **Results**: [cached]" >> findings.md

# Reuse from cache
cat findings.md | grep "FastAPI async"
```

### Inefficient Research Session

```bash
# Multiple queries (3 API calls)
webSearchPrime("FastAPI async patterns")
webSearchPrime("FastAPI error handling")
webSearchPrime("FastAPI testing")

# No caching - will repeat if needed again
```

---

## Monitoring

### Daily Quota Check

```bash
# Add to crontab or run manually
daily_quota_check() {
    zai quota | tee -a ~/.claude/mcp-usage.log
}
```

### Alert Threshold

Set up alerts when quota drops below threshold:

```bash
# Check quota and alert if low
check_quota_alert() {
    REMAINING=$(zai quota | grep "remaining" | awk '{print $1}')
    if [ "$REMAINING" -lt 20 ]; then
        echo "⚠️  MCP quota low: $REMAINING remaining"
    fi
}
```

---

## References

- [ZAI MCP Setup Guide](./zai-mcp-setup.md)
- [MCP Tool Catalog](./README.md)
- [ZAI Dashboard](https://dashboard.z.ai/)
