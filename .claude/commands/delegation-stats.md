---
name: delegation-stats
description: Aggregate delegation performance stats with reward-weighted metrics
---

# Delegation Stats (Agent Lightning-inspired)

Aggregate delegation log data into performance insights. This is the "learning loop" — the prompt-level equivalent of Agent Lightning's training cycle.

## Instructions

1. Read `.claude/delegation-log.jsonl` (or `~/.claude/delegation-log.jsonl`)
2. Parse all JSONL entries and compute aggregates:

### By Agent Type
For each agent_type, calculate:
- Total delegations
- Success rate (result=success / total)
- Average reward (mean of reward field)
- Average tool calls per delegation
- Average duration
- Most common tool sequences (top 3 patterns)

### By Model
For each model, calculate:
- Total delegations
- Average reward
- Which agent types it was used with

### Credit Patterns
Identify:
- **Best performers**: agent+model combos with highest avg reward
- **Bottlenecks**: agent+model combos with lowest avg reward
- **Efficient delegations**: high reward + low tool call count
- **Wasteful delegations**: low reward + high tool call count

3. Display results as a summary report.

4. If user provided arguments:
   - `agent:<type>` → detailed stats for one agent type
   - `model:<name>` → detailed stats for one model
   - `since:<date>` → filter to entries after date
   - `recommendations` → generate routing recommendations based on data

## Example Output

```
Delegation Performance Report
═══════════════════════════════════════════════════════════════════

By Agent Type                                          (last 30 days)
─────────────────────────────────────────────────────────────────
Agent         | Count | Success | Avg Reward | Avg Calls | Avg Time
Explore       |    47 |   89%   |    0.82    |    6.2    |  14.3s
Bash          |    23 |   96%   |    0.96    |    1.8    |   3.2s
general       |    31 |   77%   |    0.71    |   12.1    |  38.4s
Plan          |     8 |   88%   |    0.84    |    9.4    |  22.1s

By Model
─────────────────────────────────────────────────────────────────
Model   | Count | Avg Reward | Best At             | Struggles With
haiku   |    52 |    0.88    | search, formatting  | synthesis
sonnet  |    41 |    0.79    | multi-step tasks    | deep reasoning
opus    |    16 |    0.91    | architecture        | (small sample)

Recommendations
─────────────────────────────────────────────────────────────────
• Explore+haiku: strong combo (0.88 reward). Keep using for search tasks.
• general+sonnet: underperforming (0.71). Consider opus for complex research.
• Bash+haiku: near-perfect (0.96). Ideal for all command execution.
• Bottleneck: general-purpose agents averaging 12 tool calls. Consider
  breaking large tasks into smaller delegations.
```

## Recommendations Mode (`recommendations`)

When the user asks for recommendations, analyze the data and output actionable routing advice:
- "For [task pattern], prefer [agent+model] (avg reward: X)"
- "Avoid [agent+model] for [task pattern] (avg reward: X, consider [alternative])"
- "High-value optimization: [specific change] would improve avg reward by ~X"
