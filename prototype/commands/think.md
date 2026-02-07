# /think — Multi-Perspective Analysis

Apply different levels of cognitive depth using expert personas (the Karpathy principle: LLMs are simulators, not entities — channel relevant experts).

## Thinking Levels

| Level | Trigger | Personas |
|-------|---------|----------|
| Think | "think" | Quick sanity check, 1-2 perspectives |
| Think Hard | "think hard" | 3-4 perspectives, trade-off analysis |
| Ultrathink | "ultrathink" | 4-6 perspectives, exhaustive alternatives |
| Super Think | "super think" | Full committee, system-wide implications |
| Mega Think | "mega think" | Advisory board, paradigm questioning |

## Personas by Level

### Ultrathink (most commonly used)
- **Senior Engineer**: "What are the technical risks? Blast radius?"
- **Product Manager**: "Does this solve the actual problem?"
- **Security Engineer**: "What could go wrong? Attack surface?"
- **Future Maintainer**: "Will this be understandable in 6 months?"

### Super Think (add these)
- **Principal Engineer**: "How does this fit overall architecture?"
- **DevOps/SRE**: "How will this deploy and scale? How does it fail?"
- **Data Engineer**: "Data flow implications?"
- **Customer**: "Does this actually help me?"

### Mega Think (add these)
- **CTO**: "Aligned with technical strategy?"
- **Skeptic**: "Why would this fail?"
- **Optimist**: "Best-case outcome? What doors does this open?"
- **Historian**: "What similar approaches have been tried?"
- **Simplifier**: "Is this the simplest solution? What can we remove?"

## Problem-Type Guides

**Debugging**: QA Engineer → Detective → Skeptic
**Architecture**: Simplifier → SRE → Future Maintainer
**Performance**: Performance Engineer → Skeptic → Customer
**Security**: Attacker → Security Engineer → Auditor

## Output Format

```markdown
## [Level] Thinking: [Topic]

### Initial Assessment
[Quick summary]

### Perspectives Considered
[Expert personas used]

### Analysis
[Detailed per-perspective analysis]

### Trade-offs
[Pros/cons of approaches]

### Recommendation
[Clear recommendation with reasoning]

### Confidence: [High/Medium/Low]
[Explanation]
```
