# OpenClaw Findings

## What OpenClaw Does

**Core Concept**: Standalone personal AI assistant with Gateway control plane

### Key Features
1. **Gateway WebSocket**: Single control plane for sessions, channels, tools, events
2. **Multi-Channel**: WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, Teams, Matrix, Zalo, WebChat
3. **Companion Apps**: macOS menu bar, iOS/Android nodes
4. **Voice Wake + Talk Mode**: Always-on speech with ElevenLabs
5. **Live Canvas**: Agent-driven visual workspace
6. **Skills Platform**: Bundled, managed, workspace skills
7. **Security**: DM pairing policy for unknown senders

### Architecture
```
[15+ Messaging Channels] → [Gateway WS :18789] → [Pi Agent / CLI / Apps]
```

---

## ONE_SHOT Relevance

### Key Differences

| Aspect | OpenClaw | ONE_SHOT |
|--------|----------|----------|
| **Architecture** | Standalone npm app | Claude Code config |
| **Deployment** | `npm install -g openclaw` | Symlink skills to `~/.claude` |
| **Scope** | Full AI assistant (channels, apps, voice) | Dev-focused productivity |
| **Control Plane** | Gateway WebSocket | AGENTS.md + CLAUDE.md |
| **Channel Support** | 15+ messaging platforms | Terminal only |
| **Session Model** | Main + group isolation | Single Claude session |

### Low Synergy Areas

| OpenClaw Feature | ONE_SHOT Equivalent | Notes |
|------------------|---------------------|-------|
| Multi-channel inbox | N/A | ONE_SHOT is dev-focused, not messaging |
| Companion apps | N/A | Outside ONE_SHOT scope |
| Voice/Talk mode | N/A | Feature mismatch |
| Gateway WS | N/A | Different architecture |
| Skills platform | ONE_SHOT skills | **Similar but different scale** |

### Potential Learning

**1. Progressive Skills Loading**
- OpenClaw: Bundled → Managed → Workspace skills
- ONE_SHOT: All skills loaded at once
- **Opportunity**: Consider tiered skill loading

**2. Security-First Design**
- OpenClaw: DM pairing policy for unknown senders
- ONE_SHOT: No equivalent (terminal only)
- **Opportunity**: Document security model clearly

**3. Doctor Command Pattern**
- OpenClaw: `openclaw doctor` for troubleshooting
- ONE_SHOT: No diagnostic command
- **Opportunity**: Add `/doctor` skill for health checks

---

## Priority Assessment
**LOW-MEDIUM** - OpenClaw solves a different problem (personal AI assistant vs dev productivity).

## Recommendations for ONE_SHOT
1. **Document scope boundary** - ONE_SHOT is dev-focused, not multi-channel
2. **Consider doctor command** - Add `/doctor` skill for troubleshooting
3. **Study progressive loading** - Consider tiered skill loading (core → managed → workspace)

## Conclusion
OpenClaw is impressive but orthogonal to ONE_SHOT's mission. OpenClaw = full AI assistant ecosystem; ONE_SHOT = lean dev productivity kit.
