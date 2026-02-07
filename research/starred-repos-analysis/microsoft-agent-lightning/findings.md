# Agent Lightning Findings

## What It Does
Microsoft's framework for **training AI agents with reinforcement learning**:
- Zero code change agent optimization
- Works with ANY agent framework (LangChain, AutoGen, CrewAI)
- RL, prompt optimization, supervised fine-tuning

## ONE_SHOT Relevance

### Training vs Configuration

| Agent Lightning | ONE_SHOT |
|----------------|----------|
| Train agents with RL | Configure Claude behavior |
| Optimize prompts/prompts | Fixed rules/commands |
| Framework-agnostic | Claude-specific |
| Research/production | Personal productivity |

### Key Insight
Agent Lightning is about **improving agent capabilities** through training. ONE_SHOT is about **configuring Claude Code** for personal workflows.

## Recommendations for ONE_SHOT

### 1. Separate Concerns ⭐
ONE_SHOT should NOT try to train agents. That's Agent Lightning's job.

**Action**: Document clear boundary: ONE_SHOT = configuration, Agent Lightning = training.

### 2. Potential Integration
If ONE_SHOT ever adds "learning from patterns," Agent Lightning could be the backend.

**Action**: Noted for future consideration, but out of scope for v10.

## Priority
**LOW** - Different problem domain. ONE_SHOT is about configuration, not training.

## Next Steps
None - this is orthogonal to ONE_SHOT's mission.
