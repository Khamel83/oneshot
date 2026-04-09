# Background Project Intelligence Systems: Research Findings

> How tools analyze codebases in the background and provide fresh context to developers.
> Researched April 2026. Sources listed at bottom.

---

## Executive Summary

Background project intelligence is the practice of continuously analyzing a codebase outside of active development sessions and surfacing actionable context when developers start work. The field has converged on a clear architecture:

1. **Collect signals** from the codebase (changes, dependencies, tests, complexity)
2. **Build a dependency graph** that maps relationships between symbols, files, and services
3. **Compute impact** for any proposed change (blast radius, risk score, affected tests)
4. **Inject context** at session start (onboarding summary, recent activity, blockers)
5. **Track debt** automatically (code smells, missing tests, stale dependencies)

The most successful systems separate **operational context** (dynamic, ephemeral: "what changed today") from **decision context** (static, stable: "how does this system work"). This separation enables prompt caching (90% cost reduction), prevents context drift, and respects the "lost in the middle" problem where models degrade when relevant information is buried in large context windows.

The critical insight from the research: the problem is not model capability -- all current models are "good enough." The differentiator is **context engineering** -- the quality, structure, and freshness of the data you feed into the model. As one researcher put it: "The difference between an agent with the right context and an agent without it is larger than the difference between any two models."

---

## 1. Signals That Matter

### What to Collect

The most valuable signals for background intelligence, ranked by information density:

| Signal | How to Collect | Value |
|--------|---------------|-------|
| **File change frequency** (churn) | Git log per-file commit counts | High-churn files are where debt hurts most. CodeScene's key differentiator. |
| **Dependency graph** (imports, callers, dependents) | Static analysis / AST parsing | Foundation for blast radius calculation. Enables impact analysis. |
| **Test coverage gaps** | Coverage tool output per-file | Untested files are dangerous to modify. Uncovered debt is invisible debt. |
| **Complexity metrics** (cyclomatic, cognitive) | Static analysis (radon, lizard, eslint) | Functions exceeding thresholds are refactoring candidates. |
| **Dead code** | Reachability analysis from entry points | Dead code inflates cognitive load and confuses AI agents. |
| **Code smells** | Pattern matching (duplication, long functions, god classes) | Specific remediation targets. SonarQube, CodeAnt, CodeScene. |
| **Dependency health** (outdated, vulnerable) | SCA tools (Snyk, Dependabot, pip-audit) | Security debt grows silently until forced action. |
| **Knowledge concentration** (bus factor) | Git blame + contributor count per-file | Files touched by only 1 person are knowledge risks. |
| **Stale dependencies** (declared but unused) | Dependency inference tools (Pants, Bazel) | Unnecessary rebuilds, misleading dependency graph. |
| **Fan-in trends** | Compare dependency graphs across versions | Symbols with growing fan-in are "amplifiers" -- their blast radius increases over time. |

### What to Ignore

Signals that sound useful but have low signal-to-noise ratio:
- Lines of code (doesn't capture complexity)
- Raw commit count (doesn't account for size of changes)
- Language popularity metrics (irrelevant to your specific codebase)
- Generic "code quality score" without per-file breakdown

### The Three Types of AI-Generated Technical Debt

Research from practitioner reports (2025-2026) identifies three distinct debt types that background intelligence should detect:

1. **Cognitive Debt** -- Code shipped faster than anyone can understand it. Detected by: knowledge concentration metrics, documentation gaps, files with no clear owner who can explain them.
2. **Verification Debt** -- Diffs approved without full understanding. Detected by: PR size (large PRs are less reviewed), time-to-merge (fast merges = shallow review), missing test coverage on changed files.
3. **Architectural Debt** -- AI generates working solutions that violate system design. Detected by: pattern duplication across files, new dependencies added without justification, circular dependencies.

---

## 2. Context Delivery

### The Context Layer Architecture

Production systems in 2026 converge on a two-tier context architecture:

**Tier 1: Decision Context (static, cached)**
- Project structure, coding standards, architectural decisions
- API specs, database schemas, design patterns
- Injected at the start of the prompt
- Benefits from prompt caching (90% cost reduction with OpenAI/Anthropic)
- Changes rarely -- on deployment or policy updates

**Tier 2: Operational Context (dynamic, immediate)**
- Recent changes, current errors, active blockers
- File-level churn data, test failures, open PRs
- Injected at the end of the prompt (recency bias)
- Changes every session or every action

This separation is critical. Mixing static and dynamic context in one block triggers the "lost in the middle" problem confirmed by Stanford research: models perform best when relevant information appears at the beginning or end of input, degrading significantly when it's buried in the middle.

### Onboarding Injection Format

The optimal format for "fresh eyes" context when starting a session:

```
## Project Status
[1-2 sentences on current activity level and state]

## Active Blockers
- [Item 1 with file reference]
- [Item 2 with file reference]

## Recent Changes (last N commits)
- [Change with affected files and why it matters]

## Attention Items
- [Things that need awareness, ranked by urgency]

## Recommended Next Steps
1. [Immediate action]
2. [Short-term follow-up]
3. [Ongoing monitoring]
```

Key principles:
- **Small, linked files** over one large document. The agent reads the index, finds what it needs, reads just that file.
- **Structured data** (JSON, tables) over prose. Agents can parse and prioritize structured signals faster.
- **File references** in every finding. "The auth module has debt" is useless. "core/auth.py has 200+ commits, 0 tests, and 1 contributor" is actionable.
- **Keep it under 500 words** for the onboarding summary. Detail lives in linked files.

### The AGENTS.md Pattern

The emerging standard for AI-readable project documentation:
- AGENTS.md at repo root as the entry point ("read this first")
- docs/ folder with one file per feature/decision/constraint
- Instruct the agent to maintain documentation as part of every task
- This is a knowledge transfer problem, not a tooling problem

### Staleness Detection

Context goes stale. Systems must detect and flag staleness:
- Compare generated summary against current git HEAD
- Track which files have changed since last analysis
- Re-run analysis on changed files only (incremental)
- Flag when dependency graph edges are older than N commits
- Self-healing: automated ingestion pipelines that refresh external docs on schedule

---

## 3. Change Impact Analysis

### Blast Radius Calculation

The state-of-the-art approach (SDL-MCP, Augment Code, Depwire):

1. **Build a symbol-level dependency graph** -- not file-level, but function/class/interface level
2. **For each changed symbol**, compute:
   - **Semantic diff**: Did the signature change? Invariants added/removed? Side effects changed?
   - **Blast radius**: All direct and transitive dependents, ranked by distance, fan-in, test proximity
   - **Fan-in trend**: Is this symbol's blast radius growing over time? (amplifier detection)
3. **Score risk** using weighted formula:
   - Changed Symbols (40%) -- interface stability, behavior stability, side-effect changes
   - Blast Radius (30%) -- number of dependents, transitive distance
   - Interface Stability (20%) -- proportion of changes with signature modifications
   - Side Effects (10%) -- proportion of changes affecting observable behavior

### Impact Flow Analysis (Claude Code Skill)

A Claude Code skill pattern for token-efficient impact analysis:
- Uses Serena MCP for symbol metadata (60x fewer tokens than traditional file scanning)
- Generates A-F health grades based on coupling and complexity metrics
- Produces dependency graph visualizations
- Identifies dead code via reachability analysis

### Key Insight: ABI Awareness

File-level change detection (git diff) is insufficient. A method reordering in a Java class or a docstring addition in Python marks the file as "changed," but doesn't affect downstream behavior. Semantic-aware analysis that detects whether the public interface actually changed avoids false positives in blast radius calculations.

Build systems like Buck (Java ABI) and Bazel (dormant dependencies) are pioneering this approach. Background intelligence systems should adopt ABI-level change detection rather than file-level diffing.

### Dependency Graph Maintenance

Common issues in large codebases that degrade impact analysis accuracy:
- **Diamond dependencies**: Same library required at different versions through different paths
- **Re-exports**: Module imports from another module and re-exports it, creating implicit transitive dependencies
- **Stale declared dependencies**: Build metadata says module A depends on B, but A no longer uses B
- **Large transitive closures**: Changes to widely-used modules trigger rebuilds of almost everything
- **Cross-component dependencies**: Applications depending on other applications instead of shared libraries

All of these corrupt the dependency graph and produce incorrect blast radius calculations. Regular graph hygiene is essential.

---

## 4. Session Continuity

### "Where You Left Off" Signals

The most valuable signals for session continuity:

1. **Uncommitted changes** -- `git status` and `git diff`
2. **Recent file access** -- files read/written in the last session
3. **Active tasks** -- task tracker state (pending, in_progress, blocked)
4. **Last commit message** -- provides context on what was being worked on
5. **Open blockers** -- items logged as BLOCKERS.md or similar
6. **Decisions made** -- DECISIONS.md with recent entries
7. **Handoff documents** -- structured context saved via /handoff or similar

### The Feedback Loop

Best practice from production systems:

```
Plan (agent reads docs, identifies what needs to change)
  -> Implement (agent writes code, runs tests)
  -> Review (human catches what agent missed)
  -> Enrich (update docs and tests with learned insights)
  -> Repeat (each cycle is smoother than the last)
```

The fourth step (Enrich) is the one everyone skips and it's the most important. Every constraint documented, every test added, every decision captured makes the agent smarter for next time -- not because the model learns, but because the context it operates in gets richer.

### The "Discard and Redo" Technique

When review reveals many issues with AI-generated code:
1. Capture all problems found and update documentation/tests
2. Throw away the implementation
3. Ask the agent to implement again from scratch with enriched context
4. The second attempt is almost always cleaner

This serves as a signal: if you're constantly discarding and redoing, the knowledge base isn't rich enough.

---

## 5. Blocker and Debt Tracking

### Automatic Detection Methods

| Debt Type | Detection Method | Tools |
|-----------|-----------------|-------|
| Security debt | SCA scanning, secrets detection | Snyk, SonarQube Secrets Radar |
| Code quality debt | Complexity analysis, duplication detection | SonarQube, CodeAnt, CodeScene |
| Architectural debt | Dependency graph analysis, coupling metrics | vFunction, Augment Code, SDL-MCP |
| Documentation debt | Docstring coverage, README freshness | Custom scripts, AGENTS.md validators |
| Dependency debt | Version audit, vulnerability scanning | Dependabot, Snyk, pip-audit |
| Cognitive debt | Knowledge concentration, owner count | Git blame analysis, CodeScene |
| Verification debt | PR size, review time, test coverage on changes | CI/CD metrics, custom analysis |

### Prioritization Framework

Don't try to fix everything. Prioritize by:
1. **Change frequency** -- Debt in code that changes weekly hurts more than code unchanged for two years
2. **People impact** -- Code touched by 10 people creates coordination costs; code touched by 1 person creates knowledge risk
3. **Criticality** -- Debt in payment processing is worse than debt in logging
4. **Test coverage** -- Untested debt is dangerous because you don't know what breaks when you fix it

### The Detection-Remediation-Tracking Stack

Production teams run tools from each layer:
- **Detection**: SonarQube or CodeScene (measure where debt lives)
- **Remediation**: Autonomous agents (Codegen) or developer-led (Cursor)
- **Tracking**: Project management (ClickUp, Jira) with debt as first-class items

Without the tracking layer, discovery and remediation tools generate signal that never converts to closed items.

---

## 6. Efficient Background Processing

### Cost Minimization Strategies

| Strategy | Cost Impact | Quality Impact |
|----------|------------|----------------|
| Incremental analysis (only changed files) | 10-50x reduction | Minimal -- most changes are localized |
| Free model for housekeeping tasks | $0 | Sufficient for categorization, summarization |
| Static analysis over LLM calls | $0 | Better for deterministic checks (linting, complexity) |
| Prompt caching for stable context | 90% reduction | None -- cached prefix is identical |
| Batch processing (cron every 15 min) | Amortized | Slight staleness (acceptable for background) |

### When to Use LLMs vs Static Analysis

| Task | Approach | Why |
|------|----------|-----|
| Complexity metrics | Static analysis | Deterministic, fast, no hallucination risk |
| Dependency graph building | Static analysis (AST parsing) | Exact, reproducible |
| Code smell detection | Static analysis | Pattern matching is reliable for known smells |
| Test gap identification | Static analysis + coverage data | Deterministic |
| Decision extraction from sessions | LLM (free tier) | Requires natural language understanding |
| Blocker summarization | LLM (free tier) | Requires synthesis of multiple signals |
| Pattern mining across sessions | LLM (free tier) | Requires reasoning about events |
| Impact risk scoring | Hybrid (static graph + LLM for context) | Graph provides structure, LLM provides nuance |

### Staleness Windows

| Signal | Max Staleness | Refresh Strategy |
|--------|--------------|-----------------|
| Dependency graph | 50 commits or 1 day | Re-index on push hook |
| Test coverage | Per-commit | Coverage tool in CI |
| Complexity metrics | Per-commit | Fast enough to run on every push |
| Code smells | Daily | Batch cron job |
| Session summaries | On session end | PostToolUse hook |
| External documentation | 7 days | Scheduled cron with Firecrawl/Argus |
| Security vulnerabilities | 24 hours | SCA tool scheduled scan |

---

## 7. Anti-Patterns

### What Background Intelligence Systems Get Wrong

**1. Context Window Stuffing**
"The solution to a confused model is a larger context window." This is lazy engineering. Stuffing 2M tokens into a model triggers the "lost in the middle" problem. Curated context beats raw volume every time.

**2. Ignoring the Dependency Graph**
"AI tools have no map of your codebase. Every new chat starts from zero. They burn tokens scanning files they already saw." (Depwire, HN). Without a pre-built dependency graph, agents waste enormous context on discovery.

**3. Alert Fatigue from False Positives**
"AI code review tools that generate too many false positives train developers to ignore their findings." (Kusari). Every finding must be actionable and specific. "This function is too complex" is noise. "core/auth.py:validateToken() has cyclomatic complexity 18 and is called by 12 other functions -- consider extracting" is signal.

**4. Measuring Velocity Instead of Understanding**
"41% of all new commercial code is AI-generated in 2026. Yet experienced developers report a 19% productivity decrease when using AI tools." The paradox: AI made the fast part faster and the slow parts slower. Writing code was never the bottleneck -- understanding, debugging, and modifying code is.

**5. Treating All Technical Debt Equally**
A high-complexity file nobody touches is different from a high-complexity file three teams modify weekly. CodeScene's behavioral analysis distinguishes actively painful debt from dormant, low-risk code. Most tools don't.

**6. No Feedback Loop**
Generating intelligence without closing the loop back into documentation and tests is monitoring, not intelligence. The system must enrich its own context with every cycle, or it generates the same insights forever.

**7. Ignoring AI-Generated Debt**
AI coding tools create a new category of debt: code that works but nobody understands. This "cognitive debt" accumulates invisibly behind green test suites and high velocity metrics. Background systems must track who understands what, not just what works.

**8. Over-Commenting**
AI agents tend to over-comment code. Comments should be reserved for non-obvious constraints and the "why" behind surprising decisions. Every comment that explains "what" is a sign the code should be refactored to be more readable.

---

## Key Takeaways for OneShot's Janitor System

1. **The dependency graph is the foundation.** Build it first, maintain it continuously, and derive everything else from it. Without a symbol-level graph, blast radius and impact analysis are impossible.

2. **Separate static and dynamic context.** Static context (project structure, rules, architecture) belongs in cached prompts. Dynamic context (recent changes, blockers, session state) belongs at the end of prompts.

3. **Use free models for housekeeping.** Categorization, summarization, and pattern mining don't need expensive models. Route janitor tasks to the free worker.

4. **Incremental analysis only.** Full codebase re-analysis on every event is wasteful. Track what changed and only re-analyze those files.

5. **Track cognitive debt.** Add knowledge concentration metrics (files with 1 contributor, modules nobody can explain) alongside code quality metrics.

6. **Close the feedback loop.** Every session should enrich the context for the next session. Decisions, blockers, and lessons learned must be captured automatically.

7. **Guard against alert fatigue.** Every finding must include a specific file reference, a concrete action, and a priority ranking. No vague warnings.

8. **ABI-aware change detection.** Don't just track which files changed -- track whether the public interface of changed symbols actually changed. This eliminates false positives in blast radius calculations.

---

## Sources

- [Onboarding AI into Your Codebase](https://alessio.franceschelli.me/posts/ai/onboarding-ai-into-your-codebase/) -- Alessio Franceschelli. Knowledge transfer approach to AI codebase preparation. AGENTS.md pattern, feedback loops, discard-and-redo technique.

- [Context Layer for AI Agents](https://www.firecrawl.dev/blog/context-layer-for-ai-agents) -- Firecrawl blog. Two-tier context architecture (operational vs decision context), lost-in-the-middle problem, context drift, self-healing pipelines.

- [AI Is Creating a New Kind of Tech Debt](https://dev.to/harsh2644/ai-is-creating-a-new-kind-of-tech-debt-and-nobody-is-talking-about-it-3pm6) -- Harsh (DEV Community). Three types of AI debt (cognitive, verification, architectural), the productivity paradox, the "can you debug at 2am?" rule.

- [How to Automate Technical Debt Detection with AI](https://www.augmentcode.com/learn/how-to-automate-technical-debt-detection-with-ai) -- Augment Code. Visibility problem framing, multidimensional prioritization, compound effect of continuous debt management.

- [Delta and Blast Radius](https://www.mintlify.com/GlitterKill/sdl-mcp/concepts/delta-blast-radius) -- SDL-MCP documentation. Semantic diffs (signature, invariant, side-effect), blast radius ranking, fan-in trend analysis (amplifiers), risk scoring formula, CI/CD integration.

- [8 AI Tools for Technical Debt That Actually Reduce It](https://codegen.com/blog/ai-tools-for-technical-debt/) -- Codegen blog. Detection-remediation-tracking stack, tool comparison (SonarQube, CodeScene, Snyk, etc.), economics of debt reduction.

- [Reducing Technical Debt with Automated Code Quality Analysis](https://www.codeant.ai/blogs/automated-code-quality-analysis-reduces-technical-debt) -- CodeAnt AI. Five debt types (security, quality, architectural, documentation, dependency), CI/CD integration, DORA metrics correlation.

- [Managing Dependency Graph in a Large Codebase](https://tweag.io/blog/2025-09-18-managing-dependency-graph/) -- Tweag. Diamond dependencies, re-exports, stale dependencies, ABI-aware change propagation, build system integration.

- [Impact Flow Analysis](https://mcpmarket.com/tools/skills/impact-flow-analysis) -- MCP Market. Claude Code skill for dependency graph analysis, blast radius calculation, health scoring with token efficiency.

- [Microservices Impact Analysis](https://www.augmentcode.com/tools/microservices-impact-analysis) -- Augment Code. Live blast radius visualization for downstream service changes.

- [13 Best AI Coding Tools for Complex Codebases in 2026](https://www.augmentcode.com/tools/13-best-ai-coding-tools-for-complex-codebases) -- Augment Code. Context engineering, cross-repository intelligence, enterprise tool evaluation criteria.

- [5 AI Code Review Pattern Predictions in 2026](https://www.qodo.ai/blog/5-ai-code-review-pattern-predictions-in-2026/) -- Qodo. Attribution-based review, specialist-agent review, context-first review patterns.

- [Are Bugs and Incidents Inevitable with AI Coding Agents?](https://stackoverflow.blog/2026/01/28/are-bugs-and-incidents-inevitable-with-ai-coding-agents/) -- Stack Overflow. AI error handling vs human, readability issues (3x in AI code), review bottleneck.

- [Best AI Coding Agents for 2026](https://www.faros.ai/blog/best-ai-coding-agents-2026) -- Faros AI. Context engineering as the key differentiator, cost-effectiveness, model benchmarking for task selection.

- [Application Security Trends 2026](https://www.ox.security/blog/application-security-trends-in-2026/) -- OX Security. AI-driven triage, runtime intelligence, lifecycle visibility, PBOM traceability.

- [Managing Dependency Graph in a Large Codebase](https://tweag.io/blog/2025-09-18-managing-dependency-graph/) -- Tweag. Diamond dependencies, re-exports, stale dependencies, cross-component violations, ABI-aware propagation.
