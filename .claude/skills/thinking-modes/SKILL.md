---
name: thinking-modes
description: "Extended thinking modes for deeper analysis. Use when user says 'think', 'think hard', 'ultrathink', 'super think', or 'mega think'."
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Task
---

# Thinking Modes

You are an expert at applying different levels of cognitive depth to problems. This skill activates extended thinking based on user-specified intensity levels.

## When To Use

- User says "think" or "think about this"
- User says "think hard" or "really think about this"
- User says "ultrathink" or "ultra think"
- User says "super think"
- User says "mega think" or "super mega think"
- User ends request with "please do a good job" (implicit ultrathink)
- Complex architectural decisions
- Debugging elusive issues
- Multi-step implementation planning

## The Karpathy Principle

> Don't think of LLMs as entities but as simulators. When exploring a topic, don't ask "What do you think about xyz?" - there is no "you". Instead try: "What would be a good group of people to explore xyz? What would they say?"

The LLM can channel/simulate many perspectives. Use this for deeper analysis by adopting relevant expert personas.

## Thinking Levels

| Level | Trigger | Depth | Use Case |
|-------|---------|-------|----------|
| **Think** | "think", "consider" | Light | Quick sanity check, simple decisions |
| **Think Hard** | "think hard", "really think" | Medium | Non-trivial decisions, trade-off analysis |
| **Ultrathink** | "ultrathink", "ultra think" | Deep | Complex architecture, critical debugging |
| **Super Think** | "super think" | Very Deep | Multi-system design, novel solutions |
| **Mega Think** | "mega think", "super mega think" | Maximum | Paradigm shifts, comprehensive analysis |

## Workflow

### Level 1: Think (Light)
1. Pause and consider the immediate problem
2. Identify obvious issues or improvements
3. Provide direct, focused answer
4. Duration: Brief reflection

### Level 2: Think Hard (Medium)
1. Consider multiple approaches
2. Evaluate trade-offs between options
3. Identify potential edge cases
4. Consider short-term vs long-term implications
5. Provide recommendation with reasoning
6. Duration: Extended reflection

### Level 3: Ultrathink (Deep)
1. Deeply analyze the problem space
2. Simulate perspectives from multiple expert personas:
   - Senior engineer: "What are the technical risks?"
   - Product manager: "Does this solve the actual problem?"
   - Security engineer: "What could go wrong?"
   - Future maintainer: "Will this be understandable in 6 months?"
3. Consider architectural implications
4. Explore alternative solutions exhaustively
5. Identify hidden assumptions
6. Provide comprehensive analysis with prioritized recommendations
7. Duration: Thorough reflection

### Level 4: Super Think (Very Deep)
1. All of Ultrathink, plus:
2. Consider system-wide implications
3. Simulate a design review committee:
   - Principal engineer: "How does this fit the overall architecture?"
   - DevOps: "How will this deploy and scale?"
   - Data engineer: "What are the data flow implications?"
   - Customer: "Does this actually help me?"
4. Map dependencies and ripple effects
5. Consider migration paths and backwards compatibility
6. Provide detailed implementation roadmap
7. Duration: Comprehensive reflection

### Level 5: Mega Think (Maximum)
1. All of Super Think, plus:
2. Question fundamental assumptions
3. Consider if the problem is even the right problem to solve
4. Simulate advisory board:
   - CTO: "Is this aligned with technical strategy?"
   - CEO: "Is this the best use of resources?"
   - Skeptic: "Why would this fail?"
   - Optimist: "What's the best-case outcome?"
   - Historian: "What similar approaches have been tried?"
5. Explore paradigm-shifting alternatives
6. Consider 1-year, 3-year, 5-year implications
7. Provide strategic analysis with multiple scenarios
8. Duration: Exhaustive reflection

## Output Format

When thinking mode is activated, structure output as:

```markdown
## [Level] Thinking: [Topic]

### Initial Assessment
[Quick summary of the problem/request]

### Perspectives Considered
[List of expert personas/viewpoints simulated]

### Analysis
[Detailed thinking based on level depth]

### Trade-offs
[Pros/cons of different approaches]

### Recommendation
[Clear recommendation with reasoning]

### Confidence Level
[High/Medium/Low + explanation]
```

## Inputs

- User request with thinking level trigger
- Context about the problem/decision

## Outputs

- Structured analysis at appropriate depth
- Clear recommendations with reasoning
- Identified risks and trade-offs
- Confidence assessment

## Integration with OneShot

Use thinking modes during:
- **PRD Review**: Ultrathink before approving requirements
- **Architecture Decisions**: Super Think for system design
- **Hard Stops**: Think Hard before storage/auth/deployment decisions
- **Debugging**: Ultrathink for elusive bugs
- **Feature Planning**: Think Hard for scope decisions

## Keywords

think, think hard, ultrathink, ultra think, super think, mega think, super mega think, deep analysis, consider carefully, really think, do a good job, analyze deeply, extended thinking
