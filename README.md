# ONE_SHOT: AI-Powered Autonomous Project Builder

**Version**: 1.6
**Philosophy**: Ask everything upfront, then execute autonomously
**Security**: SOPS-encrypted secrets (never commit plaintext)

---

## 🎯 What This Is

ONE_SHOT is a **single-file specification** for building projects with AI coding agents (Claude Code, Cursor, etc.). It captures the complete philosophy, patterns, and workflows learned from 8 real-world projects (135K+ records, 29 services, $1-3/month AI costs).

**The Contract**: Answer questions once → Generate PRD → Autonomous build

---

## 🚀 Quick Start (5 Minutes)

### 1. Setup Central Secrets (One-Time - REQUIRED)

```bash
# Install SOPS and age
brew install sops age  # Mac
# OR for Linux:
sudo apt install age
wget https://github.com/getsops/sops/releases/latest/download/sops-v3.8.1.linux.amd64 -O /usr/local/bin/sops && chmod +x /usr/local/bin/sops

# Generate encryption key
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt

# CRITICAL: Back up this key to 1Password NOW
# (You can't decrypt secrets without it)

# Create central secrets repo
mkdir -p ~/secrets-vault && cd ~/secrets-vault

# Create SOPS config (replace age1xxx with your public key)
cat > .sops.yaml << 'EOF'
creation_rules:
  - path_regex: .*\.env\.encrypted$
    age: YOUR_AGE_PUBLIC_KEY_HERE
EOF

# Create your secrets
cat > secrets.env << 'EOF'
OPENROUTER_API_KEY=sk-or-v1-your-key-here
GITHUB_TOKEN=ghp_your-token-here
FIRECRAWL_API_KEY=fc-your-key-here
EOF

# Encrypt and push
sops --encrypt secrets.env > secrets.env.encrypted
rm secrets.env
echo "*.env" > .gitignore
echo "!*.env.encrypted" >> .gitignore
git init && git add . && git commit -m "Central secrets"
gh repo create secrets-vault --private --source=. --push
```

**Why Central Secrets?** ONE place for ALL your secrets (OpenRouter, GitHub, Firecrawl, etc.). Update once, every project gets it. Never duplicate secrets again.

See [CENTRAL_SECRETS.md](CENTRAL_SECRETS.md) for details.

### 2. Use ONE_SHOT in Your Project

```bash
# 1. Create new project directory
mkdir my-project && cd my-project

# 2. Copy ONE_SHOT.md to your project
cp /path/to/oneshot/one_shot.md ONE_SHOT.md

# 3. Open in your AI coding agent (Claude Code, Cursor, etc.)
# Tell it:
#   "Use ONE_SHOT.md as the spec. Ask me all Core Questions (Section 2) first.
#    Don't write code until I say 'PRD approved. Execute autonomous build.'"

# 4. Answer questions once
# 5. Review generated PRD
# 6. Say: "PRD approved. Execute autonomous build."
# 7. Watch it build autonomously
```

---

## 📁 What's in This Repo

```
oneshot/
├── one_shot.md              # Main spec (use this in your projects)
├── how_to_improve_one_shot.md  # Lessons from 8 real projects
├── CENTRAL_SECRETS.md       # Central secrets guide (THE way)
├── .env.example             # Reference (not used, everything from central)
├── .gitignore.example       # Git ignore patterns
└── scripts/
    ├── setup_secrets.sh     # Pull secrets from central repo
    └── update_secrets.sh    # Edit central secrets
```

---

## 🔑 Core Philosophy

### 1. Central Secrets (NEW in v1.6)
- ONE private GitHub repo for ALL secrets (OpenRouter, GitHub token, etc.)
- SOPS-encrypted, safe to push
- Every project pulls from central repo (no duplication)
- One age key in 1Password unlocks everything
- Update once, all projects get it

### 2. Ownership & FOSS
- 100% free & open-source stack
- No vendor lock-in
- Runs on OCI Always Free OR homelab
- Cost: $0/month infra (AI optional at $1-3/month)

### 3. Simplicity First
- Start with simplest thing (files → SQLite → PostgreSQL)
- Build only what you need NOW
- Document upgrade triggers
- Real problems only, no imaginary users

### 4. Local-First
- Own your data
- Works offline
- Cloud is optional

### 5. Cost-Conscious AI
- Default: Gemini 2.5 Flash Lite (~$0.10-0.30/M tokens)
- Upgrade only when necessary
- Track costs in SQLite
- Typical: $1-3/month

### 6. Documentation as Code
- WHY documentation for decisions
- README with Quick Start ≤5 commands
- Status scripts for observability
- Future-you friendly

---

## 🏗️ Canonical Stack

```
Application:   Python / Node / Go / Rust
Web:          FastAPI, Flask, Express
DB:           SQLite → PostgreSQL (upgrade when needed)
Web server:   Nginx Proxy Manager OR Caddy
DNS:          Cloudflare (free tier)
OS:           Ubuntu Server 24.04 LTS
Network:      Tailscale (zero-config VPN)
VC:           Git + GitHub (or Gitea)
Containers:   Docker + Docker Compose
Secrets:      SOPS + age (THIS IS NON-NEGOTIABLE)
```

---

## 📊 Validated By Real Projects

ONE_SHOT v1.6 patterns validated by:

1. **Divorce** - Legal discovery (135K records, SQLite, web RAG)
2. **Homelab** - 29 services, Docker Compose, Nginx PM
3. **Atlas** - Podcast transcripts (750 transcripts, status scripts)
4. **TrojanHorse** - Note processing (local-first, AI classification)
5. **Frugalos/Hermes** - AI router (cost tracking, local→cloud)
6. **Atlas-voice** - Voice analysis (privacy-first, 104M chars)
7. **Tablo** - TV automation (dual mode, AI identification)
8. **VDD/OOS** - Dev framework (27.5% code reduction)

**Results**:
- ✅ $0-3/month total cost (AI included)
- ✅ Sub-second queries on 135K records (SQLite)
- ✅ 29 services on single machine (homelab)
- ✅ Months of uptime with systemd
- ✅ ZERO secrets leaks (SOPS since day 1 on new projects)

---

## 🎓 How to Use ONE_SHOT

### For New Projects

1. Copy `one_shot.md` to your project as `ONE_SHOT.md`
2. Open in AI agent (Claude Code, Cursor)
3. Tell agent: "Use ONE_SHOT.md as spec. Ask Core Questions."
4. Answer questions once
5. Review PRD
6. Say: "PRD approved. Execute autonomous build."

### For Existing Projects

Use ONE_SHOT patterns piecemeal:
- **Secrets**: Add SOPS encryption
- **Docs**: Add WHY documentation
- **Ops**: Add status scripts, health endpoints
- **Data**: Follow data-first implementation order
- **AI**: Add cost tracking

### For Learning

Read in order:
1. `one_shot.md` - Main spec (complete reference)
2. `CENTRAL_SECRETS.md` - Setup central secrets (5 minutes)
3. `how_to_improve_one_shot.md` - Real-world lessons from 8 projects

---

## 🔒 Central Secrets: The Secret Sauce

**Problem**: How do you manage secrets across multiple projects without duplication?

**Old way** (BAD):
```
project-a/.env (OpenRouter key)
project-b/.env (OpenRouter key again)
project-c/.env (OpenRouter key again)
# Update key? Change in 3 places
# Lost .env file? Secrets gone
```

**ONE_SHOT way** (GOOD):
```
github.com/you/secrets-vault
├── secrets.env.encrypted  (ONE place for ALL secrets)
└── .sops.yaml

All projects pull from here!
```

**How it works**:
1. You have ONE age key in 1Password (decrypts everything)
2. ONE private repo with ALL your secrets (encrypted)
3. Every project: `./scripts/setup_secrets.sh` (pulls from central, decrypts)
4. Update secrets: Edit central repo, all projects get update

**Result**: One OpenRouter key, one GitHub token, one place for everything. Update once, all projects work.

See [CENTRAL_SECRETS.md](CENTRAL_SECRETS.md) for 5-minute setup.

---

## 🆚 ONE_SHOT vs Other Approaches

### vs Project Templates (Cookiecutter, etc.)
- ONE_SHOT: Complete philosophy + automation (not just file structure)
- Templates: Static snapshots (no upgrade path, no AI integration)

### vs Frameworks (Rails, Django, etc.)
- ONE_SHOT: Language-agnostic, pick your tools
- Frameworks: Opinionated about language/stack

### vs "Just Ask AI"
- ONE_SHOT: Consistent patterns across projects
- Ad-hoc: Every project different, no learnings captured

### vs Manual Setup
- ONE_SHOT: Questions → PRD → Autonomous build
- Manual: Repeat decisions for every project

---

## 🛠️ Archon Principles (Non-Negotiable)

Every ONE_SHOT project MUST have:

1. **Never Commit Plaintext Secrets** - SOPS-encrypted, always
2. **Validate Before Create** - Check environment first
3. **WHY Documentation** - Explain decisions, not just commands
4. **Systematic Debugging** - Health checks, logs, status scripts
5. **Health First** - Every service has `/health` endpoint
6. **Future-You Documentation** - Understandable in 6 months

---

## 📈 Version History

- **v1.6** (2024-11-29)
  - **BREAKING**: SOPS now MANDATORY (non-negotiable)
  - Added Q14 (SOPS Setup) to Core Questions
  - SOPS validation in environment checks
  - SOPS setup automated in Phase 0
  - Complete SOPS integration (scripts, docs, templates)
  - Updated Archon Principles (Never Commit Plaintext Secrets)

- **v1.5** (2024-11-26)
  - Integrated patterns from 8 real-world projects
  - Added Reality Check questions (Q2.5)
  - Added Upgrade Path Principle
  - Data-first implementation order
  - Required automation scripts
  - AI cost management
  - Anti-patterns section

- **v1.4** (2024-11-26)
  - Single-file layout
  - Clear Core Questions vs Advanced
  - Unified AI section

- **v1.0-1.3** (2024-11-21)
  - Initial framework
  - Archon integration
  - AI/Agent patterns

---

## 💡 Philosophy in Practice

### "Works on My Machine" is Good
- Ubuntu 24.04 LTS (homelab standard)
- Mac (development)
- OCI Always Free (cloud)
- No wasted effort on unused platforms

### The Upgrade Path
```
Files → SQLite → PostgreSQL
Local script → systemd → Docker Compose → (not Kubernetes)
```

### The Reality Check
Before building, ask:
1. Do I have this problem RIGHT NOW?
2. What's my current painful workaround?
3. What's the simplest thing that helps?
4. How will I know it's working?

If you can't answer these, **don't build it**.

---

## 🎯 Success Metrics

A ONE_SHOT project is successful when:

- ✅ You USE it (daily/weekly/monthly)
- ✅ Setup takes ≤5 commands
- ✅ Works 6 months later without remembering details
- ✅ Secrets never leaked (SOPS-encrypted)
- ✅ Costs ≤$3/month (AI included)
- ✅ Runs unattended (cron, systemd)
- ✅ Observable (status scripts, health checks)

---

## 🚀 Next Steps

1. **Setup SOPS** (5 minutes, one-time):
   ```bash
   brew install sops age
   mkdir -p ~/.config/sops/age
   age-keygen -o ~/.config/sops/age/keys.txt
   # Back up to 1Password!
   ```

2. **Start a new project**:
   - Copy `one_shot.md` to `ONE_SHOT.md`
   - Open in Claude Code / Cursor
   - Answer Core Questions
   - Build autonomously

3. **Retrofit existing project**:
   - Add SOPS: `cp scripts/*.sh your-project/scripts/`
   - Encrypt secrets: `./scripts/encrypt_secrets.sh`
   - Add docs: README with Quick Start
   - Add observability: status script

---

## 📚 Additional Resources

- **SOPS GitHub**: https://github.com/getsops/sops
- **age encryption**: https://age-encryption.org
- **OpenRouter** (AI): https://openrouter.ai
- **Tailscale**: https://tailscale.com

---

## 🤝 Contributing

ONE_SHOT is a living document. Improvements come from real project usage.

**To contribute**:
1. Use ONE_SHOT on a real project
2. Document what worked / what didn't
3. Submit patterns that improved your workflow

**Do NOT**:
- Add complexity without real-world validation
- Suggest patterns you haven't used yourself
- Recommend paid services (unless truly better + documented tradeoff)

---

## 📄 License

MIT License - Use freely, modify, share. Credit appreciated but not required.

---

**ONE_SHOT: One file. One workflow. Infinite possibilities.**

**100% Free & Open-Source** • **Deploy Anywhere** • **No Vendor Lock-in** • **Secrets Always Encrypted**
