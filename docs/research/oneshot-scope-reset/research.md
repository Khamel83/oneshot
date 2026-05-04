# OneShot Scope Reset: Skills, Orchestration, and Knowledge Wikis

Date: 2026-05-04

## Executive Answer

OneShot should stop trying to be a general-purpose public skills/orchestration framework.

The closest project category to what OneShot is trying to become is **owned assistant infrastructure**, not "a better skills repo."

Superpowers and Matt's skills solve process discipline inside coding sessions. OneShot is trying to solve a larger personal-infrastructure problem: persistent memory, private context, trusted tools, repo/machine routing, and always-available agent workflows. That is the OpenClaw / NanoClaw / LLM-wiki / context-injection lane.

After inspecting the local repos, the important correction is: **the closest project may already be the user's Zeno/OpenClaw setup**, not a new NanoClaw migration.

Local evidence:

- `/Users/khamel83/github/zeno` describes itself as the planning repo and configuration hub for a unified AI agent gateway built on OpenClaw.
- Runtime is under `~/.openclaw/`.
- Gateway runs on `oci-dev` at `100.126.13.70`.
- Agents already exist for `zeno`, `marcus`, `eagle`, `talon`, `forge`, and `trojan`.
- OpenClaw config already uses Gemini/Codex models, OpenRouter embeddings, heartbeat model routing, tool-deny boundaries, and per-agent workspaces.
- Zeno/OpenClaw already wires Gmail, Google Voice SMS, iMessage, homelab RPC, divorce/case source docs, and agent-specific memory.

So the answer is not "switch to NanoClaw." NanoClaw is useful as a reference architecture for small isolated assistant infrastructure, but the current network already has an OpenClaw-based version of the same idea.

The stronger path is to make OneShot a small private operating layer for Khamel-specific context, either on top of NanoClaw or beside it:

1. Private profile and memory rules that should follow the user across repos and machines.
2. Private infrastructure glue: Argus, secrets, homelab, worker availability, machine-specific dispatch, and repo update/sync.
3. Decision hygiene around mixed worktrees, handoffs, litigation/project-specific source-of-truth rules, and "what should happen next."

Everything else should be treated as replaceable by external skill systems unless OneShot has a specific private advantage.

That means OneShot can shrink from "15 things" to roughly three owned responsibilities:

- **Khamel Context**: durable preferences, project routing, and personal operating rules.
- **Private Tool Bridge**: Argus/search, secrets, homelab, worker routing, and local machine realities.
- **Handoff/Continuity Layer**: clear saved state, next-session artifacts, and repo-specific source-of-truth checks.

For process discipline, TDD, debugging, planning, architecture review, and skill authoring, the external ecosystem now has better-maintained options. OneShot should adopt or wrap those rather than duplicate them.

The practical answer after checking `zeno`, `openclaw`, and `openclaw-config`:

- **Base personal assistant / always-on memory / messaging / scheduled tasks**: use the existing Zeno/OpenClaw setup.
- **Knowledge compounding / research wiki**: use a Karpathy-style wiki implementation, likely `wiki-skills` first.
- **Coding-process skills**: use Matt Pocock skills or Superpowers as adapters, not as OneShot's identity.
- **OneShot-owned layer**: keep only the private coding/repo glue OpenClaw and public skills should not own: Argus document/research workflows, repo-local handoffs, source-of-truth checks, mixed-worktree discipline, and exact worker/machine routing for code tasks.

## Scope and Caveats

The pasted RTFD file from the macOS shared pasteboard was not available by the time this research ran. The pasteboard `items/` directory was empty, so this report does not treat that pasted content as evidence.

This report used:

- Direct local inspection of the OneShot repo.
- Direct shallow clones of the named public repos and adjacent candidates.
- Argus research search through the authenticated homelab endpoint.
- Web checks for GitHub, Reddit, and marketplace pages.

Reddit and marketplace summaries are useful for signal, not truth. GitHub repo contents and official plugin pages carry more weight.

## Current OneShot Reality

OneShot currently describes itself as a multi-model orchestration framework for Claude Code. Its README lists these main layers:

- Claude Code as planner/reviewer.
- Workers: Codex, Gemini CLI, Manus, OpenCode Go, OpenRouter.
- Router in `core/router/`.
- Dispatch runner in `core/dispatch/run.py`.
- Janitor in `core/janitor/`.
- Skills in `.claude/skills/`.

Local repo evidence shows the maintenance burden is real:

- `core/janitor/jobs.py`: 1855 lines.
- `core/dispatch/run.py`: 909 lines.
- `oneshot_cli/doctor_cmd.py`: 790 lines.
- `oneshot_cli/memory.py`: 603 lines.
- `.claude/skills/` and untracked `.agents/skills/` currently duplicate the same 15 skills.
- `.claude/commands/` has slash-command wrappers for the same conceptual surface.

The recent May 3 work was about making skills available as true slash commands and syncing `.claude/commands/` during update. That solved an immediate usability gap, but it also increases the number of surfaces OneShot must keep coherent: skills, commands, instructions, update scripts, docs, router config, dispatch code, and Janitor output.

## External Options

### Matt Pocock Skills

Source: [mattpocock/skills](https://github.com/mattpocock/skills)

Matt Pocock's repo is a compact, engineering-focused skills set. The repo frames itself as "Skills For Real Engineers" and explicitly argues for small, composable, adaptable skills rather than a system that owns the whole process.

The useful pieces for OneShot are:

- `grill-with-docs`: asks hard questions, sharpens terminology, updates `CONTEXT.md` and ADRs.
- `tdd`: vertical-slice red/green/refactor discipline.
- `diagnose`: disciplined debugging loop: feedback loop, reproduce, hypotheses, instrument, fix, regression test, cleanup.
- `improve-codebase-architecture`: architecture review using "deep module" language.
- `to-prd` and `to-issues`: convert context/plans into PRDs and vertical-slice issues.
- `caveman`: compressed communication mode.
- `git-guardrails-claude-code`: hook-based blocking of dangerous git commands.
- `write-a-skill`: simple guidance for creating skills.

This repo overlaps heavily with OneShot's `debug`, `tdd`, `full`, `short`, and architecture/planning ambitions. Matt's design is less bespoke and easier to audit. It also has a strong idea OneShot should steal: a repo-level `CONTEXT.md` plus ADRs as the vocabulary and decision layer.

Recommendation: adopt selected Matt skills as upstream reference or installed plugin material. Do not fork the whole repo into OneShot. Use it to replace OneShot's generic process skills.

### Superpowers

Sources: [obra/superpowers](https://github.com/obra/superpowers), [Anthropic Superpowers plugin page](https://claude.com/plugins/superpowers)

Superpowers is a full software-development methodology encoded as composable skills and commands. It supports Claude Code, Codex, Cursor, OpenCode, Gemini CLI, and other agent surfaces. The current repo includes skills for:

- brainstorming
- writing plans
- executing plans
- dispatching parallel agents
- subagent-driven development
- TDD
- systematic debugging
- code review request/receipt
- git worktrees
- verification before completion
- finishing a branch
- writing skills

The official Claude plugin page describes it as a structured framework for brainstorming, subagent development with code review, debugging, TDD, and skill authoring. This is close to the broad thing OneShot has been trying to become.

Strengths:

- Larger, better-maintained external surface.
- Cross-agent/plugin support.
- Strong process coverage.
- Built-in review/checkpoint pattern.

Risks:

- It may be too heavy for simple tasks.
- It can become another process layer on top of OneShot instead of reducing complexity.
- Community reports include both strong endorsements and complaints that big skill bundles can over-trigger, consume context, or make the agent over-process straightforward work.

Recommendation: treat Superpowers as the default external "big process" option for complex coding tasks. OneShot should not compete with it feature-for-feature. If using it, OneShot should mostly decide when to invoke it and what private context to inject.

### Karpathy Guidelines

Source: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)

This repo is intentionally tiny: one CLAUDE.md-style behavioral guideline plus a skill wrapper. Its four principles are:

- think before coding
- simplicity first
- surgical changes
- goal-driven execution

This aligns with OneShot's own editing constraints and the user's repeated preference for exact scope control.

Recommendation: adopt the principle set directly into OneShot's core behavioral layer. This is low-overhead and belongs in the always-on private context, not as another optional skill that may or may not trigger.

### Context Feeder

Source: [friends0485-cyber/context-feeder](https://github.com/friends0485-cyber/context-feeder)

Context Feeder is a Claude Code hook system that injects context based on keyword/tag matching. Its core claim is important: skills are model-selected, hooks are system-enforced. It uses JSON/TOML tags and a `UserPromptSubmit` hook to inject relevant context into Claude's prompt.

This addresses a real OneShot pain point: repo-specific and user-specific rules should not depend on the model deciding a skill is relevant.

Recommendation: do not adopt the full project blindly, but adopt the pattern. OneShot's memory/rules layer should move toward deterministic injection for a small set of high-value rules:

- mixed-worktree git safety
- repo source-of-truth docs
- Argus/secrets/homelab rules
- litigation-private-material scope rules
- current-number authority in the divorce repo
- "run from repo root" verification rules

This may be more useful than adding more skills.

### LLM Wiki / Karpathy Wiki Pattern

Sources: [Karpathy llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), [kfchou/wiki-skills](https://github.com/kfchou/wiki-skills), [lewislulu/llm-wiki-skill](https://github.com/lewislulu/llm-wiki-skill)

Karpathy's wiki pattern argues that most RAG re-derives answers from raw documents every time. A persistent Markdown wiki compiles knowledge once, accumulates synthesis, tracks contradictions, and stays useful across future questions.

The core architecture is:

- raw immutable sources
- LLM-maintained wiki pages
- schema/instructions that define conventions and operations
- index/log files for navigation and chronology
- lint/audit/update/query workflows

This is directly relevant to the user's "wiki thing of knowledge" question.

Two public skill implementations are worth considering:

- `kfchou/wiki-skills`: Claude Code plugin with `wiki-init`, `wiki-ingest`, `wiki-query`, `wiki-lint`, `wiki-update`, and `wiki-audit`.
- `lewislulu/llm-wiki-skill`: OpenClaw/Codex-compatible skill with scaffold/lint/audit scripts, plus optional Obsidian and web preview tooling.

Recommendation: pilot a wiki outside OneShot core first. The wiki should become a durable knowledge artifact, not another feature buried in `core/janitor/jobs.py`.

Candidate pilots:

- `~/github/oneshot-wiki`: OneShot operating knowledge, decisions, sources, tool comparisons.
- A separate private wiki for litigation/case materials if and only if private-material handling and source-of-truth rules are explicit.
- A research wiki for AI-agent tooling and skills, fed by GitHub repos, Reddit threads, papers, and docs.

OneShot's role should be to know where the wiki is and how to hand it to agents, not to implement a custom wiki engine.

### Community Signal

Sources include Reddit threads such as [multi-agent orchestration overcomplication](https://www.reddit.com/r/ClaudeAI/comments/1t2i664/set_up_multiagent_orchestration_with_claude_code/) and [skills worth installing](https://www.reddit.com/r/claude/comments/1s51b5u/the_claude_code_skills_actually_worth_installing/).

Recurring themes:

- Many people are building roughly the same orchestration pattern: main agent plans/reviews, worker agents execute, separate accounts/configs avoid quota collisions, memory persists across sessions, and sensitive work stays with the planner.
- The routing logic is often just a hand-rolled if-statement in Markdown. That is not unique to OneShot.
- Skills can be a token drain.
- Skill trigger reliability is imperfect because the model chooses whether to use them.
- People increasingly prefer explicit slash commands or hooks for rules that must fire.
- The best skills tend to do one thing the base model does not reliably do by itself.

This supports a scope reduction. The market has caught up to OneShot's generic ideas. OneShot's durable value is the private context and infrastructure that public tools cannot know.

## Replace, Keep, or Retire

| OneShot Surface | Recommendation | Rationale |
|---|---|---|
| `secrets` | Keep | Private vault and machine sync are Khamel-specific. |
| Argus `/doc` and `/freesearch` glue | Keep, simplify | Argus/homelab corpus is private infrastructure. |
| worker routing config | Keep only if it stays thin | Your machines, quotas, and accounts are private. Do not build a public router fantasy. |
| `handoff` / `restore` | Keep | Continuity across sessions is high-value and personal. |
| `update` | Keep | Project sync across machines is private operational glue. |
| `janitor` | Keep only as background signal | Useful, but should not be a sprawling product surface. Split large code before adding features. |
| `tdd` | Replace with Matt or Superpowers | External implementations are stronger. |
| `debug` | Replace with Matt `diagnose` or Superpowers `systematic-debugging` | External workflows are more mature. |
| `full` / `short` / `conduct` | Collapse | These overlap with Superpowers planning/execution. Keep one OneShot entrypoint that decides whether to invoke external process. |
| `adversarial-review` | Keep as small wrapper | Gemini second opinion is useful, but keep it tiny. |
| `research` | Keep as Argus-specific wrapper | Research should use Argus and write artifacts. Avoid duplicating wiki/research tooling. |
| `vision` | Reassess | Browser-use and visual plugins may already cover most of this. |
| `write skill` equivalents | Replace with Matt/Superpowers | Not private enough to own. |
| `.agents/skills` mirror | Decide or remove | Duplicates `.claude/skills`; keep only if it is the new cross-agent packaging target. |

## Proposed Target Architecture

```
OneShot
├── private-context/
│   ├── user-preferences
│   ├── repo routing rules
│   ├── source-of-truth maps
│   └── deterministic injection tags
├── private-tools/
│   ├── Argus search/doc/corpus client
│   ├── secrets wrapper
│   ├── homelab and machine dispatch facts
│   └── worker availability probes
├── continuity/
│   ├── handoff
│   ├── restore
│   ├── next-session artifacts
│   └── mixed-worktree guardrails
└── adapters/
    ├── Superpowers or Matt skills
    ├── Karpathy guidelines
    ├── wiki-skills / llm-wiki
    └── browser/document/presentation/spreadsheet plugins
```

The important inversion: OneShot should not own every workflow. OneShot should decide which workflow to use and provide the private context that off-the-shelf workflows lack.

## 30-Day Migration Plan

### Week 1: Freeze and Compare

- Do not add new OneShot skills.
- Install/test these externally in a sandbox repo:
  - Superpowers
  - Matt Pocock skills
  - Karpathy guidelines
  - one wiki implementation (`kfchou/wiki-skills` first; `lewislulu/llm-wiki-skill` if Codex/OpenClaw compatibility matters more)
- Run the same two real tasks through OneShot-native vs external flow:
  - one coding/debug task
  - one research/knowledge task
- Save transcripts or summaries under `docs/research/oneshot-scope-reset/evals/`.

### Week 2: Decide Ownership

- Make a keep/replace map for every current OneShot skill.
- Pick exactly one "big process" system:
  - Superpowers for a more complete workflow.
  - Matt skills for lighter composable workflows.
- Make OneShot call or reference that system rather than reimplementing it.
- Decide whether `.agents/skills` is the future packaging surface. If not, remove it from the working tree.

### Week 3: Pilot the Wiki

- Create a small wiki for OneShot operating knowledge.
- Ingest:
  - this report
  - `docs/meta-harness/refactor_plan.md`
  - README
  - relevant research links
  - current Janitor findings
- Query it for: "What should OneShot own that no external tool can own?"
- Keep the answer as a wiki page and compare it with this report.

### Week 4: Prune

- Archive or delete replaced generic skills.
- Split or freeze `core/janitor/jobs.py` and `core/dispatch/run.py`; do not keep adding to them.
- Rewrite README around the smaller identity:
  - private context
  - private tools
  - continuity
  - adapters to external workflows
- Keep a migration log explaining what was removed and what external tool now owns it.

## Immediate Recommendation

Do not install every appealing skill into OneShot.

Do this first:

1. Add Karpathy guidelines to the always-on OneShot behavior layer.
2. Pick either Matt skills or Superpowers for process discipline, not both as defaults.
3. Pilot `wiki-skills` for a OneShot knowledge wiki.
4. Build or adopt a tiny deterministic context-injection mechanism for high-value private rules.
5. Collapse OneShot's skill catalog after the pilot, not before.

If the pilot works, OneShot becomes smaller and more useful:

> OneShot is not my AI framework. OneShot is the private operating layer that tells my AI tools who I am, where my tools live, what the repo's source of truth is, and when to hand work to better-maintained external workflows.

That is worth keeping. The rest is optional.

## Source Index

- [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)
- [mattpocock/skills](https://github.com/mattpocock/skills)
- [obra/superpowers](https://github.com/obra/superpowers)
- [Superpowers official Claude plugin](https://claude.com/plugins/superpowers)
- [friends0485-cyber/context-feeder](https://github.com/friends0485-cyber/context-feeder)
- [Karpathy llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [kfchou/wiki-skills](https://github.com/kfchou/wiki-skills)
- [lewislulu/llm-wiki-skill](https://github.com/lewislulu/llm-wiki-skill)
- [Reddit: multi-agent orchestration overcomplication](https://www.reddit.com/r/ClaudeAI/comments/1t2i664/set_up_multiagent_orchestration_with_claude_code/)
- [Reddit: Claude Code skills worth installing](https://www.reddit.com/r/claude/comments/1s51b5u/the_claude_code_skills_actually_worth_installing/)
