# Document Intelligence for Non-Code Repositories

> Research into background intelligence systems for document-heavy repositories.
> Focus: actionable patterns implementable as pure-compute functions (git + file analysis, no LLM needed for signals).

**Date**: 2026-04-08
**Search Backend**: Argus (research mode, Tavily provider)

---

## Table of Contents

1. [Signals That Matter for Document-Heavy Repos](#1-signals-that-matter)
2. [How PKM Tools Detect Stale/Orphan/Linked Content](#2-pkm-tools)
3. [Detecting Document Relationships](#3-document-relationships)
4. [Detecting "Attention Needed" Items](#4-attention-needed)
5. [Onboarding Summaries for Non-Code Projects](#5-onboarding-summaries)

---

## 1. Signals That Matter for Document-Heavy Repos <a name="1-signals-that-matter"></a>

Document-heavy repositories (markdown, text, CSV, JSON, emails) produce different signals than code repos. The janitor already tracks test gaps, code smells, config drift, and dependency maps for code. For documents, the signals are structural and temporal rather than syntactic.

### 1.1 Temporal Signals (Git-Derivable)

These are computable from `git log` with zero API calls:

| Signal | Git Command | What It Reveals |
|--------|------------|-----------------|
| **File staleness** | `git log -1 --format="%ai" -- $file` | Days since last meaningful edit. Files untouched for 90+ days may be stale. |
| **Edit frequency** | `git log --oneline -- $file \| wc -l` | How often a file is touched. Low-frequency files with many backlinks = candidate for review. |
| **Commit velocity** | `git log --since="30 days ago" --oneline \| wc -l` | Overall project activity. A sudden drop signals neglect. |
| **New additions** | `git diff --name-only --diff-filter=A $BASE..HEAD` | Recently added files that may lack cross-references. |
| **Deletions** | `git diff --name-only --diff-filter=D $BASE..HEAD` | Files removed that may leave dangling references elsewhere. |
| **Author diversity** | `git log --format="%aN" -- $file \| sort -u \| wc -l` | Files edited by only one person carry key-person risk. |
| **Burst detection** | `git log --since="7 days ago" --format="%ad" --date=short -- $file \| sort \| uniq -c` | Unusual spike in edits may indicate churn or restructuring. |

**Implementation pattern** (from research on git file age analysis):
```bash
# All tracked files sorted by last commit (staleness ranking)
git ls-tree -r --name-only HEAD | while read f; do
  echo "$(git log -1 --format='%ai' -- $f) $f"
done | sort
```

### 1.2 Structural Signals (File-System-Derivable)

| Signal | Detection Method | What It Reveals |
|--------|-----------------|-----------------|
| **Orphan files** | Files with zero incoming `[[wiki-links]]` or markdown references | Documents that exist but nothing points to -- may be forgotten or intentionally standalone. |
| **Dangling references** | `[[link]]` targets that don't exist on disk | Broken links, renamed files, deleted content. |
| **File size outliers** | `wc -c $file` across all docs | Oversized documents that may need splitting. |
| **Depth distribution** | Count directory nesting levels | Documents buried 5+ levels deep are harder to discover. |
| **File type distribution** | Extension frequency counts | Whether the repo is balanced or dominated by one type. |
| **Empty/near-empty files** | `wc -l < 5` for markdown | Stub documents that were never filled in. |

### 1.3 Content Signals (Regex-Derivable)

For markdown and text files, these patterns are detectable without an LLM:

| Signal | Pattern | What It Reveals |
|--------|---------|-----------------|
| **TODO/FIXME markers** | `/TODO|FIXME|HACK|XXX/i` | Unresolved items embedded in documents. |
| **Unresolved questions** | `/\?\s*$/m` (lines ending with `?`) | Open questions that may need answers. |
| **Placeholder text** | `/TBD|PLACEHOLDER|COMING SOON/i` | Documents with incomplete content. |
| **Email addresses** | `/[a-z]+@[a-z]+\.[a-z]+/i` | Contact info that may need updating. |
| **Date references** | `/\d{4}-\d{2}-\d{2}/` | Explicit dates that can be checked for staleness. |
| **Front matter completeness** | YAML front matter presence and fields | Structured metadata that may be missing or outdated. |
| **Heading structure** | `/^#{1,6}\s+/m` | Missing H1 = no clear document title. |

### 1.4 Relationship Signals (Cross-File-Derivable)

| Signal | Detection Method | What It Reveals |
|--------|-----------------|-----------------|
| **Backlink count** | Count of `[[filename]]` occurrences across all files | Popularity/importance. Zero backlinks = orphan candidate. |
| **Outlink count** | Count `[[...]]` in a single file | Documents that reference many others (hubs/indexes). |
| **Reciprocal links** | A links to B AND B links to A | Strongly related pair. |
| **Transitive closure** | A -> B -> C but no A -> C | Potential missing cross-reference. |
| **Orphan clusters** | Files that only link to each other, nothing else | Isolated knowledge silos. |

---

## 2. How PKM Tools Detect Stale/Orphan/Linked Content <a name="2-pkm-tools"></a>

PKM (Personal Knowledge Management) tools have solved many of these problems. Their approaches map directly to what we can implement as batch processing on a document repo.

### 2.1 Obsidian

Obsidian is the most relevant reference because it works on local markdown files -- the same format as a git-tracked document repo.

**Orphan detection** (from `find-unlinked-files` plugin by Vinzent03):
- Scans all markdown files in the vault
- Builds a graph of `[[wiki-links]]`
- Reports files with zero incoming links (no backlinks)
- Also detects broken links (links to files that don't exist)

**Key implementation detail**: The plugin works purely on the link graph, not content analysis. It reads `.md` files, extracts all `[[target]]` patterns, builds an adjacency list, and finds nodes with zero in-degree. This is a pure-compute function.

**Obsidian CLI (v1.12)** adds terminal access to the vault graph:
- `obsidian search "query"` -- full-text search across vault
- `obsidian graph` -- access the link graph programmatically
- Backlinks are now properly detected for canvas files too

**What Obsidian does NOT do** (gaps we can fill):
- No staleness detection based on file age
- no cross-reference with git history
- No "attention needed" aggregation
- No onboarding summary generation
- No detection of content-level issues (TODOs, placeholders, etc.)

### 2.2 Logseq

Logseq uses block-level references (more granular than Obsidian's file-level). Key differences:
- **Block references**: `((block-id))` allows referencing individual paragraphs
- **Journal-based**: Daily pages accumulate; content is organized by date
- **Query system**: Supports Datalog queries over the graph (powerful but complex)

**Relevant patterns for document intelligence**:
- Logseq's graph query system can find "pages created but never linked" (orphans)
- The "related pages" feature uses outgoing links to suggest connections
- Property-based queries can find pages with specific metadata patterns

### 2.3 Notion (SaaS, Less Relevant)

Notion is SaaS-based, so its detection is server-side and not directly applicable. However, its patterns are worth noting:
- "Last edited" timestamps with automatic staleness flags
- "Linked database" references that propagate updates
- Relationship properties between database items

### 2.4 Mapping PKM Patterns to Git-Based Intelligence

| PKM Feature | Obsidian/Logseq Approach | Git-Based Equivalent |
|------------|------------------------|---------------------|
| Orphan detection | Zero backlinks in graph | Zero `[[]]` references across all `.md` files |
| Broken links | Link target doesn't exist | `[[target]]` where `target.md` not in `git ls-files` |
| File staleness | Not available (no git) | `git log -1 --format="%ai" -- $file` |
| Recent changes | Not available | `git log --since="7 days ago" -- $file` |
| Edit frequency | Not available | `git log --oneline -- $file \| wc -l` |
| Content completeness | Not available | Regex for TODO, TBD, placeholder patterns |
| Popularity ranking | Backlink count | Count of `[[]]` references to file across repo |

---

## 3. Detecting Document Relationships <a name="3-document-relationships"></a>

Building a relationship graph for documents requires extracting links and references from file content.

### 3.1 Link Types in Document Repos

| Link Type | Pattern | Example |
|-----------|---------|---------|
| **Wiki links** (Obsidian-style) | `\[\[([^\]]+)\]\]` | `[[project-overview]]` |
| **Markdown links** | `\[text\]\(([^)]+)\)` | `[see here](./other-file.md)` |
| **Relative file refs** | `\.\.?/[\w-]+` | `../config/settings.json` |
| **Section anchors** | `#([\w-]+)` within links | `[[file#section-heading]]` |
| **Tag references** | `#([\w-]+)` standalone | `#important`, `#review-needed` |
| **@mentions** | `@([\w-]+)` | `@person-name` |
| **Front matter refs** | YAML `related:` fields | Structured metadata links |

### 3.2 Building the Link Graph

The core algorithm (pure Python, no external dependencies):

```python
import re
from collections import defaultdict
from pathlib import Path

def build_link_graph(repo_dir: str) -> dict:
    """Build adjacency list from markdown wiki-links."""
    graph = defaultdict(lambda: {"out": set(), "in": set()})
    all_files = set()

    for md in Path(repo_dir).rglob("*.md"):
        name = md.stem  # filename without .md
        all_files.add(name)
        content = md.read_text(errors="ignore")

        # Extract [[wiki-links]]
        targets = set(re.findall(r'\[\[([^\]|]+)', content))

        for target in targets:
            # Handle [[file#section]] -> extract just file
            target_file = target.split("#")[0].strip()
            graph[name]["out"].add(target_file)
            graph[target_file]["in"].add(name)

    return dict(graph), all_files
```

### 3.3 Graph Queries (Derived Signals)

From the link graph, we can compute:

**Orphans** (zero in-degree, not in root/index files):
```python
orphans = [f for f in all_files if f not in graph or len(graph[f]["in"]) == 0]
```

**Hubs** (high out-degree -- likely index/overview files):
```python
hubs = sorted(graph.items(), key=lambda x: len(x[1]["out"]), reverse=True)[:10]
```

**Broken links** (references to files that don't exist):
```python
broken = []
for source, refs in graph.items():
    for target in refs["out"]:
        if target not in all_files:
            broken.append((source, target))
```

**Orphan clusters** (connected components with no external links):
```python
# Find connected components, then check which have zero edges to outside
def find_components(graph, all_files):
    visited = set()
    components = []
    for f in all_files:
        if f not in visited:
            component = set()
            stack = [f]
            while stack:
                node = stack.pop()
                if node in visited or node not in graph:
                    continue
                visited.add(node)
                component.add(node)
                stack.extend(graph[node]["out"])
                stack.extend(graph[node]["in"])
            components.append(component)
    return components
```

### 3.4 Semantic Proximity (Without LLM)

Even without an LLM, we can detect likely-related documents:

| Technique | Method | Cost |
|-----------|--------|------|
| **Shared tags** | Documents with same `#tag` patterns | Free |
| **Shared directory** | Files in the same folder | Free |
| **Filename similarity** | Levenshtein distance on stems | Free |
| **Title overlap** | H1 heading word overlap | Free |
| **Mutual references** | Both reference a third document | Free |
| **TF-IDF similarity** | Word frequency vectors (scikit-learn) | Free, but heavier |

---

## 4. Detecting "Attention Needed" Items <a name="4-attention-needed"></a>

This is the actionable output layer: given all the signals above, what should be surfaced to a human?

### 4.1 Attention Categories

| Category | Signals | Priority |
|----------|---------|----------|
| **Stale docs** | Not touched in 90+ days AND has backlinks (others rely on it) | High |
| **Stale orphans** | Not touched in 180+ days AND zero backlinks | Low (may be archive-worthy) |
| **Broken references** | `[[target]]` where target.md doesn't exist | High |
| **Stubs** | File < 10 lines, has TODO/TBD | Medium |
| **Unresolved items** | TODO, FIXME, HACK count by file | Medium |
| **Orphan clusters** | Connected group with no external links | Medium |
| **Missing context** | File references a topic but no linked source | Low |
| **Oversized docs** | File > 500 lines markdown | Low |
| **Key-person risk** | File edited by only one author, not touched in 30+ days | Medium |
| **Recent orphans** | Files added in last 30 days with zero backlinks | Medium |

### 4.2 Scoring Algorithm

A simple weighted score to rank files by "attention needed":

```
attention_score = (
    3.0 * broken_ref_count +
    2.0 * (1 if stale_days > 90 and backlink_count > 0 else 0) +
    1.5 * (stub_flag + unresolved_count) +
    1.0 * (1 if orphan and recent else 0) +
    0.5 * (1 if single_author else 0) +
    0.3 * oversize_flag
)
```

Files with the highest scores get surfaced first.

### 4.3 Staleness Tiers

Not all staleness is equal. The context determines whether a stale file is a problem:

| File Role | Staleness Tolerance | Action |
|-----------|--------------------|--------|
| **Index/hub pages** | Low (30 days) | These should reflect current state. Flag if stale. |
| **Reference docs** | Medium (90 days) | Flag if they have many backlinks (others rely on them). |
| **Archive/historical** | High (365+ days) | Expected to be stale. Don't flag. Detect via path prefix or front matter. |
| **Meeting notes** | Low (7 days) | If no activity in a week, probably forgotten. |
| **Decision logs** | Medium (60 days) | These should be referenced, not updated. |
| **Templates** | High (never) | Templates don't go stale. |

**Detection heuristic**: Files under `archive/`, `historical/`, or with front matter `status: archived` get a staleness exemption.

### 4.4 Change Impact Detection

When files are modified or deleted, identify downstream impact:

```python
def find_dependents(target: str, graph: dict) -> list[str]:
    """All files that reference the target (direct dependents)."""
    if target not in graph:
        return []
    return list(graph[target]["in"])

def find_all_affected(target: str, graph: dict) -> list[str]:
    """BFS to find all transitively affected files."""
    visited = set()
    queue = find_dependents(target, graph)
    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        queue.extend(find_dependents(node, graph))
    return list(visited)
```

---

## 5. Onboarding Summaries for Non-Code Projects <a name="5-onboarding-summaries"></a>

A useful onboarding summary for a document repository answers: "What is this project, what's the current state, and where should I start?"

### 5.1 Structure of a Good Onboarding Summary

Based on research into AGENTS.md, CLAUDE.md, and knowledge base best practices:

```markdown
# Project: [Name]

## What This Is
[1-2 sentence description of the project's purpose]

## Current State
- Total documents: N files (M markdown, K CSV, J JSON)
- Active (edited in last 30 days): N files
- Stale (not edited in 90+ days): N files
- Attention needed: N items (broken refs, stale hubs, etc.)

## Key Documents (Highest Backlink Count)
1. [[file]] - [brief description from H1 or first line] (N references)
2. [[file]] - [brief description] (N references)
3. [[file]] - [brief description] (N references)

## Orphan Files (Unlinked)
- N files with zero incoming links
- [If few, list them. If many, just the count and top candidates.]

## Broken References
- N broken [[wiki-links]] detected
- [List: source -> missing target]

## Activity Timeline
- Last commit: [date]
- Most active file (last 30 days): [[file]]
- Files added recently: [[file]], [[file]]

## Document Map
[Auto-generated tree of the directory structure, annotated with backlink counts]

## Attention Items
[Top 5 files by attention_score with reason]
```

### 5.2 Generating the Summary (Pure Compute)

The entire onboarding summary can be generated without an LLM:

1. **What This Is**: Extract from README.md H1, or directory name if no README.
2. **Current State**: File counts by type, staleness distribution from git log.
3. **Key Documents**: Sort by backlink count, extract H1 from each.
4. **Orphan Files**: Files with zero in-degree in link graph.
5. **Broken References**: Link targets not found in file system.
6. **Activity Timeline**: Git log --since for recent activity.
7. **Document Map**: `tree` or `find` output, annotated with link counts.
8. **Attention Items**: Top files by attention_score.

### 5.3 What the LLM Adds (Optional Enhancement)

An LLM pass can improve the onboarding summary by:
- Generating a natural-language "project description" from document titles and structure
- Identifying the project's domain/topic from content analysis
- Suggesting "start here" recommendations based on hub documents
- Summarizing what's changed recently in plain language
- Detecting thematic clusters (grouping related documents by topic)

The current janitor `generate_onboarding` job already does this with the free openrouter model. The pure-compute version above provides the foundation; the LLM pass adds polish.

### 5.4 Incremental Updates

The onboarding summary should update incrementally, not regenerate from scratch:

| Trigger | What to Update |
|---------|---------------|
| New files added | Recompute orphan count, file totals |
| Files deleted | Check for broken references, recompute graph |
| Files modified | Update staleness scores, activity timeline |
| Session start | Refresh all signals (current janitor behavior) |

---

## Implementation Plan: Document Intelligence Jobs

New pure-compute jobs for `core/janitor/jobs.py`:

### Phase 1: Link Graph (Zero Dependencies)

```python
def build_doc_graph(project_dir: str) -> dict:
    """Build link graph from markdown wiki-links.
    Returns: {file: {out: [targets], in: [sources]}}
    """
    # 1. Walk all .md files
    # 2. Extract [[wiki-links]] from each
    # 3. Build adjacency list
    # 4. Detect orphans, broken links, hubs
    # Output: .janitor/doc-graph.json

def detect_broken_refs(project_dir: str) -> dict:
    """Find [[links]] pointing to non-existent files."""
    # 1. Build link graph
    # 2. Check each target against git ls-files
    # Output: .janitor/broken-refs.json
```

### Phase 2: Staleness Analysis (Git-Dependent)

```python
def detect_doc_staleness(project_dir: str, days_threshold: int = 90) -> dict:
    """Rank documents by staleness and backlink importance."""
    # 1. Get last-modified date for each tracked file
    # 2. Cross-reference with link graph (importance)
    # 3. Apply staleness tiers based on file role
    # Output: .janitor/doc-staleness.json
```

### Phase 3: Attention Score Aggregation

```python
def compute_attention_scores(project_dir: str) -> dict:
    """Aggregate all signals into ranked attention list."""
    # 1. Load doc-graph, broken-refs, staleness
    # 2. Apply scoring algorithm
    # 3. Return top-N items with reasons
    # Output: .janitor/attention-items.json
```

### Phase 4: Enhanced Onboarding

```python
def generate_doc_onboarding(project_dir: str) -> dict:
    """Generate onboarding summary for document repos."""
    # 1. Load all signal files
    # 2. Extract H1/headings from key docs
    # 3. Build structured summary
    # 4. Write to CLAUDE.local.md or similar
    # Output: CLAUDE.local.md section
```

---

## Sources

### Argus Search Queries (Research Mode)
1. "document management intelligence system file analysis staleness tracking knowledge base signals"
2. "personal knowledge management PKM tools Obsidian Logseq stale orphan detection backlinks"
3. "document repository orphan detection cross reference backlinks knowledge graph file relationships"
4. "file staleness detection knowledge decay monitoring repository health git analysis"
5. "non-code repository onboarding summary documentation project knowledge base overview generation"
6. "Obsidian vault analysis orphan files missing backlinks broken links graph analysis CLI tool"
7. "git log file age analysis last modified document staleness detection bash script"
8. "markdown cross-reference detection link validation document relationship graph python"

### Key Extracted Articles
- [Stale Data: Causes, Detection, and Freshness SLAs](https://tacnode.io/post/what-is-stale-data) -- Framework for staleness tiers and freshness thresholds
- [Measuring the Health of Git Repositories](https://augmentable.medium.com/measuring-the-health-of-git-repositories-c0dea98c9ca5) -- Recency of commits, key-person risk, dependency indicators
- [Anomaly Detection in Git](https://hoop.dev/blog/anomaly-detection-in-git-catching-issues-before-they-break-your-workflow) -- Time-series monitoring, content analysis, contributor patterns
- [Project Onboarding for AI Agents](https://agenticoding.ai/docs/practical-techniques/lesson-6-project-onboarding) -- Hierarchical context files, AGENTS.md, CLAUDE.md patterns
- [Orphan Pages SEO](https://searchenginezine.com/on-page/links/orphan-pages-seo/) -- Trilateral URL discovery, graph-based isolation detection, semantic reintegration
- [Obsidian find-unlinked-files](https://github.com/Vinzent03/find-unlinked-files) -- Orphan detection implementation in PKM context
- [mdrefcheck](https://github.com/gospodima/mdrefcheck) -- Markdown reference validation CLI tool
- [DEVONthink Note Graphs](https://github.com/FabrizioMusacchio/DEVONthink_Note_Graphs) -- Interactive link graph visualization for markdown notes

---

## Appendix: File Types and Their Signal Profiles

| File Type | Signals | Notes |
|-----------|---------|-------|
| **Markdown (.md)** | Full signal set: links, headings, TODOs, front matter, size, staleness | Primary target for document intelligence |
| **CSV** | Row count, header completeness, staleness, size | Check for header consistency if schema is known |
| **JSON** | Schema validation, key completeness, staleness | Check for required keys if schema is known |
| **Text (.txt)** | Size, staleness, line count | Minimal signals available |
| **Email (.eml, .mbox)** | Date fields, thread structure, staleness | Extract From/To/Subject headers |
| **YAML/TOML** | Structure validation, staleness | Check for required keys |
| **HTML** | Link extraction, heading structure, staleness | Similar to markdown but more complex parsing |
