# ONE_SHOT: AI-Powered Autonomous Project Builder

> Ask everything upfront, then execute autonomously

**Philosophy**: Documentation-first, security-first, quality-focused development powered by AI agents and Claude Skills.

## What is ONE_SHOT?

ONE_SHOT is a specification and skill system for building projects autonomously using AI agents (Claude Code, Cursor, etc.). Instead of back-and-forth iterations, you answer questions once, approve a PRD, and the AI builds the entire project.

**Version**: 1.5
**Validated By**: 8 real-world projects (135K+ records, 29 services)
**Cost**: $0/month infrastructure (OCI Always Free Tier or homelab)
**AI Costs**: $1-3/month

## Quick Start

### For New Projects

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Khamel83/oneshot.git
   cd oneshot
   ```

2. **Copy ONE_SHOT.md to your new project**:
   ```bash
   cp one_shot.md /path/to/your/project/ONE_SHOT.md
   ```

3. **Open in Claude Code or Cursor**:
   ```bash
   cd /path/to/your/project
   code . # or cursor .
   ```

4. **Tell your AI agent**:
   ```
   "Use ONE_SHOT.md as the spec. Ask me all Core Questions first.
   Don't write code until I say 'PRD approved. Execute autonomous build.'"
   ```

5. **Answer questions once, approve PRD, and let it build**

### For Using Claude Skills

The `.claude/skills/` directory contains 8 production-ready skills that work **autonomously** with Claude Code:

```bash
# Copy skills to your project
cp -r .claude/skills /path/to/your/project/.claude/
```

**The skills work automatically** - you don't need to invoke them. Claude will use them when appropriate.

## Claude Skills Overview

### What Are Skills?

Skills are knowledge packages that teach Claude how to perform tasks autonomously. They load progressively (only when needed) and work together to handle complete workflows.

### Available Skills (8 Total)

#### Meta Skills
- **skill-creator**: Builds new skills following best practices
- **marketplace-browser**: Discovers community skills from skillsmp.com

#### Project Management
- **project-initializer**: Bootstraps projects with ONE_SHOT standards
- **feature-planner**: Breaks down features into implementable plans

#### Development Workflow
- **git-workflow**: Conventional commits, branches, PRs
- **code-reviewer**: Quality (DRY/KISS/YAGNI) + Security (OWASP Top 10)
- **documentation-generator**: READMEs, ADRs, API docs

#### Security
- **secrets-vault-manager**: Integrates with [secrets-vault](https://github.com/Khamel83/secrets-vault)

### How Skills Work Autonomously

**You DON'T need to ask Claude to use skills.** Claude automatically uses them based on context:

#### Automatic Triggers

| When You... | Claude Automatically... |
|------------|-------------------------|
| Start a new project | Uses **project-initializer** to bootstrap structure |
| Mention "secrets" or "API keys" | Uses **secrets-vault-manager** to set up secrets |
| Describe a feature | Uses **feature-planner** to break it down |
| Make changes | Uses **git-workflow** for commits |
| Ask for review | Uses **code-reviewer** for quality/security scan |
| Need documentation | Uses **documentation-generator** for docs |
| Need to find a skill | Uses **marketplace-browser** to search |
| Want custom automation | Uses **skill-creator** to build new skills |

#### Skill Chaining (Automatic)

Skills chain together without you asking:

**Example 1: Starting a New Project**
```
You: "I want to build a FastAPI project for user management"

Claude autonomously:
1. Uses project-initializer → Creates structure
2. Uses secrets-vault-manager → Sets up secrets
3. Uses documentation-generator → Creates README/CLAUDE.md
4. Uses git-workflow → Makes initial commit
```

**Example 2: Building a Feature**
```
You: "Add JWT authentication"

Claude autonomously:
1. Uses feature-planner → Breaks down into tasks
2. Uses documentation-generator → Creates ADR
3. Uses git-workflow → Creates feature branch
4. [You implement]
5. Uses code-reviewer → Security scan (JWT best practices)
6. Uses git-workflow → Creates PR with proper description
```

**Example 3: Code Review**
```
You: "I finished the authentication code"

Claude autonomously:
1. Uses code-reviewer → Scans for:
   - OWASP Top 10 vulnerabilities
   - DRY/KISS/YAGNI violations
   - Missing tests
   - Security issues (password hashing, JWT secrets)
2. Provides structured feedback (Critical/Important/Suggestions)
3. Uses git-workflow → Commits fixes
```

### Skill Integration with ONE_SHOT

When using ONE_SHOT.md with Claude Skills:

1. **Questions Phase**: Skills don't interfere, Claude follows ONE_SHOT.md
2. **PRD Generation**: documentation-generator helps structure the PRD
3. **Autonomous Execution**: All skills activate automatically:
   - project-initializer sets up structure
   - secrets-vault-manager configures secrets
   - git-workflow manages commits
   - code-reviewer validates code
   - documentation-generator maintains docs

### Configuration

Skills are configured in `.claude/skills/`. Each skill has:
- `SKILL.md`: Instructions and triggers
- `templates/`: Reusable templates (optional)
- `examples/`: Reference examples (optional)
- `scripts/`: Validation scripts (optional)

**No configuration needed** - skills work out of the box.

## Repository Structure

```
oneshot/
├── .claude/
│   └── skills/              # 8 Claude Code skills
│       ├── README.md        # Comprehensive skill documentation
│       ├── skill-creator/
│       ├── marketplace-browser/
│       ├── project-initializer/
│       ├── feature-planner/
│       ├── git-workflow/
│       ├── code-reviewer/
│       ├── documentation-generator/
│       └── secrets-vault-manager/
├── one_shot.md              # Main specification (copy to your projects)
├── how_to_improve_one_shot.md
└── README.md                # This file
```

## Key Features

### ONE_SHOT Specification
- **Question Once**: Answer all requirements upfront
- **PRD Generation**: AI creates detailed Product Requirements Document
- **Autonomous Execution**: Builds entire project without further prompting
- **Validated**: 8 real-world projects, 135K+ database records

### Claude Skills System
- **Autonomous**: Skills activate based on context
- **Chained Workflows**: Skills work together automatically
- **Progressive Loading**: Token-efficient (only loads when needed)
- **Documentation-First**: Checks current docs before coding
- **Security-First**: OWASP Top 10 scanning, secrets management
- **Quality-Focused**: DRY/KISS/YAGNI analysis

### Integration Points
- **Secrets Vault**: Encrypted secrets management ([repo](https://github.com/Khamel83/secrets-vault))
- **Skills Marketplace**: Community skills from [skillsmp.com](https://skillsmp.com)
- **Conventional Commits**: Automated git workflows
- **SOPS Integration**: Built-in secrets encryption

## Philosophy

### Documentation-First Development

**CRITICAL RULE**: Before writing any code that uses external APIs, libraries, or configuration syntax:

1. **Check local cached docs first**: `~/homelab/docs/services/<service-name>/`
2. **If local docs don't exist**: Use WebFetch/WebSearch for current documentation
3. **Verify version compatibility**: Check which version is actually running
4. **Write code using current syntax**: Follow examples from current docs, not training data

### Why Documentation-First Matters

Your training data becomes outdated quickly. Writing code based on outdated patterns causes:
- Syntax errors from deprecated formats
- Missing required fields in newer versions
- Using features that no longer exist
- Incompatibility with current software versions

**Example**: Traefik v3.0 syntax from training data fails with "API version 1.24 too old" error because v2.11 is the stable version.

### Security-First

- Never commit secrets (`.env`, keys, credentials)
- Use secrets-vault for all projects
- OWASP Top 10 scanning on all code
- Proper .gitignore from day one

### Quality-Focused

- **DRY**: Don't repeat yourself
- **KISS**: Keep it simple
- **YAGNI**: You aren't gonna need it
- Test early and often
- Code review before merging

## Use Cases

### Personal Projects
- Homelab infrastructure automation
- Personal tools and utilities
- Side projects and experiments

### Team Projects
- Startup MVPs
- Internal tools
- API services
- Infrastructure as Code

### Learning
- Study autonomous AI workflows
- Learn best practices through skill templates
- Understand systematic project structure

## Examples

### Example 1: Building a Homelab Service

```bash
# 1. Copy ONE_SHOT.md to project
cp one_shot.md ~/my-homelab/ONE_SHOT.md

# 2. Copy skills
cp -r .claude/skills ~/my-homelab/.claude/

# 3. Open in Claude Code
cd ~/my-homelab
claude-code .

# 4. Tell Claude:
"Use ONE_SHOT.md to build a Docker Compose stack for Traefik + Pi-hole + Uptime Kuma"

# Claude will:
# - Ask questions (versions, domains, requirements)
# - Generate PRD
# - Autonomously build:
#   * docker-compose.yml (validated against current docs)
#   * Traefik configs (v2.11 syntax)
#   * Pi-hole setup
#   * Uptime Kuma integration
#   * Documentation
#   * Secrets management
#   * Git commits
```

### Example 2: Building an API

```bash
# Tell Claude:
"Build a FastAPI user management API with JWT auth"

# Claude autonomously:
# 1. Uses project-initializer:
#    - Creates FastAPI structure
#    - Sets up pytest
#    - Configures linting (black, pylint)

# 2. Uses secrets-vault-manager:
#    - Sets up .env with JWT secrets
#    - Configures database credentials

# 3. Uses feature-planner:
#    - Breaks down auth into:
#      * Database schema (users table)
#      * Password hashing
#      * JWT generation/validation
#      * Login/register endpoints
#      * Protected routes middleware
#      * Tests

# 4. Implements features

# 5. Uses code-reviewer:
#    - Checks OWASP Top 10 (A07: Authentication)
#    - Validates password hashing
#    - Checks JWT secret security
#    - Ensures proper error handling

# 6. Uses documentation-generator:
#    - Creates API docs with examples
#    - Generates ADR for JWT choice
#    - Updates README

# 7. Uses git-workflow:
#    - Creates conventional commits
#    - Generates PR description
```

## Skills Deep Dive

For detailed information about each skill, see [.claude/skills/README.md](.claude/skills/README.md).

### Creating Custom Skills

Use the `skill-creator` skill to build project-specific skills:

```
You: "I need a skill for validating Terraform configurations against AWS best practices"

Claude: [Uses skill-creator]
- Asks about validation rules
- Creates skill structure
- Generates SKILL.md with AWS-specific checks
- Adds validation scripts
- Tests the skill
```

### Finding Community Skills

Claude automatically uses `marketplace-browser` when it needs capabilities:

```
# You don't say this:
"Search the marketplace for a Playwright skill"

# Claude autonomously does this:
[Detects need for browser testing]
[Uses marketplace-browser to find webapp-testing skill]
[Suggests installation]
```

## Integration with Other Tools

### Cursor
Copy `.claude/` to `.cursor/` for Cursor AI:
```bash
cp -r .claude .cursor
```

### VS Code with Continue
Skills work with Continue extension (uses Claude)

### CLI
Use skills with Claude Code CLI:
```bash
claude-code --chat "Build a new FastAPI project"
```

## Maintenance

### Updating Skills

```bash
# Pull latest ONE_SHOT
cd oneshot
git pull

# Copy updated skills to your project
cp -r .claude/skills /path/to/your/project/.claude/
```

### Creating Project-Specific Skills

```bash
# In your project, tell Claude:
"Create a skill for [your specific need]"

# Skill is created in:
/path/to/your/project/.claude/skills/custom-skill/
```

## Troubleshooting

### Skills Not Activating

**Problem**: Claude doesn't use skills automatically

**Solution**:
1. Ensure `.claude/skills/` exists in project root
2. Check each skill has `SKILL.md` with proper YAML frontmatter
3. Restart Claude Code after adding skills
4. Be more specific in your requests to trigger relevant keywords

### Skill Conflicts

**Problem**: Multiple skills seem to overlap

**Solution**: Skills are designed to work together. If you see conflicts, check `.claude/skills/README.md` for skill descriptions and triggers.

## Resources

### Official
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Claude Skills Guide](https://docs.claude.com/en/docs/claude-code/skills)
- [Skills Marketplace](https://skillsmp.com)

### ONE_SHOT
- [Main Specification](./one_shot.md)
- [Skills Documentation](./.claude/skills/README.md)
- [Secrets Vault](https://github.com/Khamel83/secrets-vault)

### Community
- [Awesome Claude Skills](https://github.com/travisvn/awesome-claude-skills)
- [Anthropic Official Skills](https://github.com/anthropics/skills)

## Contributing

### Adding Skills
1. Use `skill-creator` to generate proper structure
2. Test thoroughly
3. Document in `.claude/skills/README.md`
4. Submit PR with: `feat(skills): add [skill-name] skill`

### Improving ONE_SHOT
See [how_to_improve_one_shot.md](./how_to_improve_one_shot.md)

## License

[Your License Here]

## Support

- **Issues**: [GitHub Issues](https://github.com/Khamel83/oneshot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Khamel83/oneshot/discussions)

---

🤖 Built with Claude Code and ONE_SHOT Skills

**Version**: 1.5.0
**Skills**: 8 autonomous agents
**Lines of Code**: 4,193 lines of skill documentation
**Philosophy**: Ask once, build autonomously
