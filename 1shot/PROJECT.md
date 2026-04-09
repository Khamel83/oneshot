# Project: Document Intelligence Mode for Janitor

## Goal
Add a document/non-code project type to janitor that provides actionable intelligence for repos containing documents, data, markdown, PDFs, emails, etc. — not just Python code.

## Acceptance Criteria
- Janitor auto-detects project type (code vs document) based on repo contents
- Code projects continue running all existing signals unchanged
- Document projects run document-specific signals instead of code signals
- CLAUDE.local.md and onboarding.md show actionable, file-referenced intelligence for both types
- Each file processed once, only re-processed when it changes (staleness gating)
- OpenCode/AGENTS.md templates updated for document project type
- Cron job works for both project types

## Scope
In:
- Research best practices for non-code project intelligence
- New document signal functions (staleness, orphans, cross-references, size outliers, etc.)
- Updated onboarding prompt for document projects
- Project type auto-detection
- Full pipeline: signals → onboarding → CLAUDE.local.md → hooks

Out:
- Multi-language code support (still Python-only for code signals)
- UI changes
- New hooks
- Processing binary files (PDFs, images) — only metadata and filenames

## Riskiest Parts
- What signals actually matter for document repos
- Prompt quality for non-code onboarding summaries
- Performance on large document repos (mitigated by staleness gating)

## Constraints
- Must not break existing code project signals
- Must follow existing patterns in jobs.py
- Zero additional API cost — pure-compute signals only
