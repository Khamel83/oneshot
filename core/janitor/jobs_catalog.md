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

Limits: 1000/day, 20/minute.

| Trigger | Frequency | Calls/session | Calls/day |
|---------|-----------|---------------|-----------|
| Turn summarizer | Every 5-10 min during active work | 20-50 | 40-100 |
| Decision extractor | Every few turns | 5-10 | 10-20 |
| File change analysis | Every commit | 5-10 | 10-20 |
| Memory hygiene | Once per session | 1-2 | 2-4 |
| Session digest | End of session | 1 | 1-3 |
| Stale detection | Once per session | 1 | 1-3 |
| **Total** | | **30-70** | **60-150** |

60-150/day is 6-15% of the 1000/day budget. Comfortable margin.
20/min limit is the real ceiling — avoid batching many calls at once.
Rate tracker in .oneshot/usage.jsonl catches problems before they matter.
