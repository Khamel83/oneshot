# claude-sneakpeek Findings

## What It Does
Parallel Claude Code build that unlocks **feature-flagged capabilities**:
- Swarm mode - Native multi-agent orchestration with TeammateTool
- Delegate mode - Task tool spawns background agents
- Team coordination - Teammate messaging and task ownership

Fork of cc-mirror by Mike Kelly.

## ONE_SHOT Relevance

**CRITICAL**: This unlocks features that Anthropic has built but not publicly released!

### Swarm Mode vs ONE_SHOT
| Feature | claude-sneakpeek | ONE_SHOT v10 |
|---------|-----------------|--------------|
| Multi-agent | Native TeammateTool | /diagnose, /implement commands |
| Background agents | Delegate mode | delegate-to-agent (v9, removed v10) |
| Task ownership | TeammateTool | beads (external) |

### Key Insight
Anthropic is **building native multi-agent orchestration** into Claude Code. ONE_SHOT v10 removed this complexity, but Claude itself is adding it natively.

## Recommendations for ONE_SHOT

### 1. Monitor Swarm Mode Development ⭐⭐⭐
Anthropic's native swarm mode may make external orchestration obsolete.

**Action**: Install claude-sneakpeek, test swarm mode, document for future ONE_SHOT decisions.

### 2. Re-evaluate v10 Simplification
If Claude Code gets native multi-agent, v10's "back to basics" approach is validated.

**Action**: Track Claude Code releases for swarm mode public availability.

### 3. Study TeammateTool Pattern
Native coordination tool may be better than custom skill routing.

**Action**: Use claude-sneakpeek to understand TeammateTool capabilities.

## Priority
**CRITICAL** - This shows where Claude Code is heading. ONE_SHOT should align with Anthropic's roadmap.

## Next Steps
1. Install claude-sneakpeek to test swarm mode
2. Document TeammateTool vs /beads vs CC-MIRROR tasks
3. Re-evaluate ONE_SHOT v10 roadmap based on Claude's native features
