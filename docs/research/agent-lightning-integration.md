# Agent Lightning Integration into ONE_SHOT

**Date**: 2026-02-14
**Builds on**: PR #5 (Intelligent Delegation v12.1, based on DeepMind arXiv:2602.11865)
**Informed by**: Microsoft Agent Lightning (https://github.com/microsoft/agent-lightning)

---

## What is Agent Lightning?

Agent Lightning (Microsoft, 2025) is an RL training framework for AI agents. It captures agent execution as structured **spans** (prompt → completion → tool calls → reward), assembles them into **trajectories**, applies **hierarchical credit assignment** to determine which steps mattered, and feeds that into a training loop.

Its key insight: you can improve agent performance by recording what happened, scoring each step, and using that signal to route future decisions.

## What We Took (Concepts, Not Code)

We didn't install Agent Lightning. ONE_SHOT is a prompt framework, not an RL training pipeline. But the conceptual architecture maps cleanly onto our delegation system:

| Agent Lightning | ONE_SHOT v12.2 | Notes |
|-----------------|----------------|-------|
| **Span** | Enriched JSONL entry in delegation-log | Each delegation event captures: span_id, session_id, agent_type, model, tool_sequence, task_input/output, reward |
| **Trajectory** | `/delegation-trajectory` command | Groups spans by session_id into ordered execution paths |
| **Credit assignment** | Heuristics in delegation.md | Output reuse = credit, last-before-failure = blame, low-cost success = efficient |
| **LightningStore** | `.claude/delegation-log.jsonl` | Append-only JSONL — the central data exchange |
| **Training loop** | `/delegation-stats` → rules update | Aggregated performance data informs future delegation routing (prompt-level "training") |

## Why Adapt Instead of Adopt?

1. **No GPU needed** — Agent Lightning's value is in its RL training loop, which requires model fine-tuning. We operate at the prompt level, so we extract the data architecture and skip the training.

2. **No new dependencies** — Everything stays as shell scripts, JSONL, and markdown. No Python packages, no databases, no infrastructure.

3. **Complementary to DeepMind framework** — PR #5 gave us the decision framework (assess → delegate → verify → escalate). Agent Lightning's concepts give us the data layer (trace → score → learn). Together: decide intelligently, then learn from what happened.

## The Data Flow

```
Delegation happens
    ↓
SubagentStop hook fires (deterministic)
    ↓
Span written to delegation-log.jsonl
  (span_id, session_id, agent, model, tools, reward)
    ↓
/delegation-log — view recent spans
/delegation-trajectory — view session execution paths
/delegation-stats — view aggregated performance + recommendations
    ↓
Human reads stats → adjusts delegation rules
  (this is the "training loop" at prompt level)
```

## What This Enables

### Today
- See what every delegation did, not just whether it "succeeded"
- Identify bottleneck delegations (low reward on the critical path)
- Know which agent+model combos work best for which task types
- Track delegation patterns across sessions

### Future (if needed)
- Automated routing: stats feed into assessment rules, closing the loop
- Anomaly detection: flag sessions with unusual reward distributions
- Cost optimization: identify where haiku suffices vs where opus is needed
- If Agent Lightning adds a Claude provider, actual RL training on our span data

## Files Changed

| File | Change |
|------|--------|
| `.claude/hooks/delegation-log-hook.sh` | Enriched with span_id, session_id, tool_sequence, reward |
| `.claude/rules/delegation.md` | Added credit assignment heuristics, bumped to v12.2 |
| `.claude/commands/delegation-trajectory.md` | New — trajectory assembly command |
| `.claude/commands/delegation-stats.md` | New — reward-weighted performance stats |
| `AGENTS.md` | Updated to v12.2, added new commands to router |

## Sources

- [Agent Lightning (GitHub)](https://github.com/microsoft/agent-lightning)
- [Agent Lightning Blog Post](https://www.microsoft.com/en-us/research/blog/agent-lightning-adding-reinforcement-learning-to-ai-agents-without-code-rewrites/)
- [Intelligent AI Delegation (arXiv:2602.11865)](https://arxiv.org/abs/2602.11865) — DeepMind paper that informed PR #5
