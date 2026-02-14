# Gap Analysis: ONE_SHOT v11 vs. DeepMind Intelligent Delegation

**Paper**: "Intelligent AI Delegation" (Tomasev, Franklin, Osindero - Google DeepMind, Feb 2026)
**arXiv**: 2602.11865

---

## 1. Dynamic Assessment

### Paper says:
Before delegating, evaluate: capability, resource availability, risk, cost, verifiability, reversibility. Not "who has the tool?" but "who should be trusted with this specific task under these constraints?"

### ONE_SHOT v11 does:
Pattern-matching triggers in AGENTS.md:
- `>5 files` → spawn Explore agent
- `npm|pytest|docker` → run in background
- `auth/secrets` edits → spawn security auditor
- `context >30%` → delegate to subagent

### Gap:
Triggers are binary (fire or don't). No assessment of:
- Is this agent capable of this specific task?
- What's the risk if delegation fails?
- Is the result verifiable?
- Can we reverse the action if wrong?
- Is the cost (tokens) proportional to the value?

### Fix:
Module 1 adds a 4-dimension assessment (complexity, criticality, uncertainty, cost) evaluated before delegation. This transforms delegation from "pattern matched → delegate" to "pattern matched → assess → decide how to delegate."

---

## 2. Adaptive Execution

### Paper says:
If the delegatee underperforms, don't wait for failure. Reassign mid-execution. Switch agents. Escalate to human. Restructure the task graph.

### ONE_SHOT v11 does:
- `failure-recovery` skill exists but is manual (user invokes `/failure-recovery`)
- No automatic escalation
- If a subagent fails, the main agent sees the failure and... tries again the same way or gives up

### Gap:
No structured retry/escalation. No mid-execution intervention. No automatic model upgrade on failure.

### Fix:
Module 3 adds fallback chains (haiku → sonnet → opus → human) and intervention triggers (stuck loops, scope violations, budget overruns).

---

## 3. Structural Transparency

### Paper says:
AI-to-AI delegation is opaque. When something fails, you can't tell if it was incompetence, misalignment, bad decomposition, malicious behavior, or tool failure. Agents must prove what they did, not just say they did it.

### ONE_SHOT v11 does:
- Beads tracks task status (created, in_progress, done)
- Git commits track code changes
- No logging of delegation decisions or outcomes
- No audit trail of what subagents did

### Gap:
If an Explore agent returns wrong information, there's no record of what it searched, how many tool calls it made, or whether its output was verified. The main agent just trusts the result.

### Fix:
Module 2 adds a JSONL audit log capturing every delegation event with assessment, result, and verification status. This creates the "structural transparency" the paper calls for.

---

## 4. Trust Calibration

### Paper says:
Humans routinely over-trust AI. AI agents may over-trust other agents. Delegation must align trust with actual capability. Too much trust = catastrophe. Too little = wasted potential.

### ONE_SHOT v11 does:
- All subagent types are treated identically
- No tracking of which agents succeed at which tasks
- Model selection is manual or based on simple heuristics
- No concept of "this agent type struggles with X"

### Gap:
The system has no memory of past delegation outcomes. It can't learn that Explore agents are great at file discovery but bad at synthesis, or that haiku works fine for simple searches but fails at complex reasoning.

### Fix:
Module 4 adds performance tracking aggregated from the audit log. This is advisory (not autonomous) - it informs the main agent's decisions without overriding human control.

---

## 5. Systemic Resilience

### Paper says:
If every agent delegates to the same high-performing model, you create a monoculture. One failure → system-wide collapse. Efficiency without redundancy = fragility.

### ONE_SHOT v11 does:
- tmux resilience (survives terminal disconnects)
- Checkpoint commits every 5 minutes
- Beads sync on state changes
- No limits on delegation depth or parallelism
- No circuit breakers

### Gap:
ONE_SHOT handles infrastructure resilience (terminal dies, state recovers) but not logical resilience (agent chain fails, delegation cascades, resource exhaustion). A subagent could theoretically delegate to another subagent infinitely. Multiple parallel delegations could exhaust API limits.

### Fix:
Module 5 adds: max delegation depth (2), max parallel delegations (4), per-agent-type timeouts, circuit breakers (3 consecutive failures → cooldown), and scope enforcement rules.

---

## Summary: What ONE_SHOT Gets Right

- **Skill routing** is solid (pattern → skill mapping)
- **Context management** is thoughtful (30%/50% thresholds, handoffs)
- **Infrastructure resilience** works (tmux, checkpoints, beads sync)
- **Philosophy** is aligned ("delegate aggressively, parallelize always")

## Summary: What's Missing

- **No intelligence in delegation** - triggers are pattern-based, not assessment-based
- **No memory** - can't learn from past delegation outcomes
- **No accountability** - no audit trail of delegated work
- **No recovery** - failures aren't automatically escalated
- **No guardrails** - no limits on delegation chains, parallelism, or scope
