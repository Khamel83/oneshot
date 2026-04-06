# Janitor Jobs Catalog

All jobs use openrouter/free ($0). Each is a bounded extraction task.

## Implemented

| Job | Function | Trigger | What it does |
|-----|----------|---------|-------------|
| Turn Summarizer | `summarize_recent_turns()` | Idle (every 5-10 min) | Extracts decisions, blockers, discoveries from recent events |
| Memory Hygiene | `memory_hygiene()` | Idle (daily) | Identifies overlapping memory files that should be merged |
| Session Digest | `generate_session_digest()` | Session end | Full structured summary of session for handoff |
| File Change Analysis | `analyze_file_changes()` | After commits | Categorizes git changes, identifies hotspot files |
| Stale File Detection | `detect_stale_files()` | Idle (daily) | Finds files not modified in 30+ days |

## Planned (High Value)

| Job | Description | Effort |
|-----|-------------|--------|
| **Dependency Graph Builder** | Scan imports/requires across project, build file dependency map. Feed into impact prediction. | Small — shell + graph |
| **Impact Predictor** | Before editing a file, show which other files import from it. Read-only bounded query. | Small — depends on dep graph |
| **Pattern Miner** | Scan recent sessions for repeated patterns: same bug fixed 3x, same file touched every session. | Medium — needs session history |
| **Test Gap Detector** | Compare files changed (git diff) against test files touched. Flag untested changes. | Small — git + file matching |
| **Code Smell Scanner** | Files that grew >500 lines since last review, functions >100 lines, deep nesting. | Small — line counting |
| **Work Pattern Analysis** | Aggregate: when does coding happen, what types of tasks, average session length. | Small — SQL query on events |
| **Commit Message Enricher** | After commit, extract what changed and why for searchability. | Small — git + extract |

## Planned (Medium Value)

| Job | Description | Effort |
|-----|-------------|--------|
| **Session Similarity** | Compare current session topic against past sessions. "You solved this before in session #42." | Medium — embeddings or keyword overlap |
| **Config Drift Monitor** | Compare lanes.yaml/workers.yaml against last-known-good commit. | Small — git diff |
| **Documentation Freshness** | Check if README/docs match current code structure. | Medium — code vs doc diff |
| **Import Health** | Scan for unused imports, circular dependencies, missing dependencies. | Small — AST parsing |
| **Error Pattern Collector** | Track all error events across sessions, group by type/file. | Small — SQL query |

## Planned (Lower Priority)

| Job | Description | Effort |
|-----|-------------|--------|
| **Changelog Generator** | Auto-generate changelog entries from commit history. | Small |
| **Onboarding Index** | For new sessions, generate a "state of the project" summary from accumulated data. | Medium |
| **Cost Tracker** | Track OpenRouter usage across sessions, project daily/weekly cost estimates. | Small — already have usage.jsonl |
| **Search Index Builder** | Index all project files + session summaries for fast full-text search. | Medium — whoosh or sqlite FTS |

## Storage Budget

| Data | Size/session | Size/year |
|------|-------------|-----------|
| events.jsonl | ~30KB | ~10MB |
| usage.jsonl | ~1KB | ~365KB |
| intelligence.db | ~50KB | ~18MB |
| **Total** | **~80KB** | **~30MB** |

Negligible. Even 10x growth is fine.

## Rate Budget

| Trigger | Calls/session | Calls/day |
|---------|--------------|-----------|
| Turn summarizer | 3-5 | 3-5 |
| Session digest | 1 | 1 |
| Memory hygiene | 0-1 | 1 |
| File analysis | 1-2 | 2 |
| **Total** | **5-9** | **7-9** |

Well under 1000/day and 20/min limits.
