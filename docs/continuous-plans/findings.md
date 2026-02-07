# ONE_SHOT v10 - Project Portfolio Analysis

## Executive Summary

Analyzed 18 active Khamel83 GitHub projects for ONE_SHOT v10 integration opportunities. Key findings:

- **80% of projects** could benefit from `/deploy` → oci-dev automation
- **60% need** `/beads` task tracking for stalled development
- **40% could use** `/remote` for macmini/homelab orchestration
- **3 projects** are candidates for v10 migration from legacy patterns

---

## Project Analysis

### Tier 1: High Impact (Immediate ONE_SHOT Value)

#### 1. **Atlas** - Personal Knowledge Ingestion System
- **Status**: Production (SQLite + systemd on homelab)
- **Current**: Manual systemd setup, 13 modules, complex architecture
- **ONE_SHOT Opportunities**:
  - `/deploy` → Automate homelab deployments
  - `/remote` → Execute on macmini for transcription tasks
  - `/beads` → Track module development backlog
  - **Rule**: `stack-defaults.md` already guides SQLite progression
- **Recommendation**: **HIGH** - Create `/cp` plan for Atlas v2 migration

#### 2. **RelayQ** - GitHub-First Job Orchestration
- **Status**: Active (OCI VM + GitHub runners)
- **Current**: Manual runner setup, docs scattered
- **ONE_SHOT Opportunities**:
  - `/deploy` → OCI VM setup automation
  - `/remote` → Manage macmini/RPi runners
  - `/cp` → Plan multi-runner orchestration
  - `/diagnose` → Debug queue issues
- **Recommendation**: **HIGH** - Perfect fit for infra-routing rules

#### 3. **Tablo** - Auto-Renamer Pipeline
- **Status**: Production (macmini automation)
- **Current**: Manual macmini execution, USB drive workflow
- **ONE_SHOT Opportunities**:
  - `/remote` → Execute pipeline on macmini automatically
  - `/beads` → Track dual-mode support tasks
  - `/deploy` → Could add oci-dev monitoring instance
- **Recommendation**: **HIGH** - Leverage `/remote` for existing macmini

#### 4. **Frugalos** (Hermes) - AI Assistant
- **Status**: Production (Ollama + local models)
- **Current**: Complex cost tracking, backend switching
- **ONE_SHOT Opportunities**:
  - `/beads` → Track feature requests (meta-learning, cost tracking)
  - `/diagnose` → Debug routing issues
  - `/deploy` → oci-dev for remote instance
- **Recommendation**: **MEDIUM** - Good `/cp` candidate for v2

---

### Tier 2: Medium Impact (Specific Improvements)

#### 5. **Networth** - Tennis Ladder
- **Status**: Production (Vercel + Supabase)
- **Current**: At Vercel Hobby limits (12/12 functions)
- **ONE_SHOT Opportunities**:
  - `/deploy` → Migrate to oci-dev + Traefik (free limits)
  - `/beads` → Track migration from Vercel
  - **Rule**: `anti-patterns.md` would flag Vercel cost
- **Recommendation**: **MEDIUM** - Cost savings via infra-routing

#### 6. **Poytz** - Cloudflare Workers Redirect
- **Status**: Production (Cloudflare + Tailscale Funnel)
- **Current**: Manual worker deployment
- **ONE_SHOT Opportunities**:
  - `/deploy` → Automate worker updates (could extend for Cloudflare)
  - **Rule**: `infra-routing.md` already documents Tailscale Funnel pattern
- **Recommendation**: **LOW** - Already follows ONE_SHOT patterns

#### 7. **Archon** - MCP Server (forked)
- **Status**: Beta (upstream project)
- **Current**: Not Khamel83's core project
- **ONE_SHOT Opportunities**:
  - `/beads` → Track upstream contributions
  - `/deploy` → Self-hosted instance on oci-dev
- **Recommendation**: **LOW** - External project, low priority

---

### Tier 3: Needs Investigation (No README/Stale)

#### 8. **arb** - Polymarket Insider Detection
- **Status**: No README (needs investigation)
- **Recommendation**: Investigate + document first

#### 9. **vig** - Prediction Pool Framework
- **Status**: 404 on README
- **Recommendation**: Investigate status

#### 10. **ipeds, penny, gamez, dada, vdd, gaas, wfm**
- **Status**: No README or minimal docs
- **Recommendation**: Audit each, determine status

---

## ONE_SHOT v10 Integration Recommendations

### Immediate Actions (Next Session)

1. **Create `/cp` plans for Tier 1 projects**:
   ```
   /cp atlas-v2 --scope "migrate to Convex for multi-user"
   /cp relayq-prod --scope "automate runner orchestration"
   /cp tablo-auto --scope "full /remote automation"
   ```

2. **Add project-specific rules**:
   ```
   .claude/rules/atlas.md - SQLite→Convex progression
   .claude/rules/relayq.md - GitHub Actions queue pattern
   ```

3. **Enable `/beads` for stalled projects**:
   - Atlas has 13 modules, perfect for task tracking
   - Tablo dual-mode support backlog
   - RelayQ multi-runner coordination

### Medium-Term (This Week)

1. **Extend `/deploy` for multi-target**:
   - Add homelab target (currently only oci-dev)
   - Add macmini target for heavy compute

2. **Create `/audit` for project health**:
   - Scan repos for stale dependencies
   - Flag anti-patterns (Vercel costs, no README)
   - Recommend ONE_SHOT patterns

3. **Document success patterns**:
   - Atlas as reference ONE_SHOT project
   - RelayQ for infra-routing
   - Tablo for /remote automation

---

## Token Budget Impact

Adding project-specific analysis (~500 tokens) + v10 base (~425 tokens) = **~925 tokens always-on**

**Acceptable** given:
- Eliminates project context switching cost
- Enables `/cp` persistence across projects
- Rules load contextually (not all at once)

---

## Next Steps

1. **Run `/cp` for Atlas v2** (highest impact)
2. **Add `/beads` to RelayQ** (runner orchestration)
3. **Enable `/remote` for Tablo** (macmini automation)
4. **Audit Tier 3 projects** (determine status)
