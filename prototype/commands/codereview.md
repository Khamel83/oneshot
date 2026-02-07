# /codereview — Structured Code Review (OWASP + Quality)

Three-pass code review for safety, design, and testing.

## Pass 1: Safety & Correctness

- Off-by-one errors
- Unhandled None/null
- Error paths not covered
- Data leaks, unsafe logging
- Injection risks (SQL, command, XSS)
- Auth bypasses

### OWASP Top 10 Checklist
- [ ] **A01**: Broken Access Control
- [ ] **A02**: Cryptographic Failures
- [ ] **A03**: Injection
- [ ] **A04**: Insecure Design
- [ ] **A05**: Security Misconfiguration
- [ ] **A06**: Vulnerable Components
- [ ] **A07**: Authentication Failures
- [ ] **A08**: Software/Data Integrity
- [ ] **A09**: Security Logging Failures
- [ ] **A10**: SSRF

## Pass 2: Design & Maintainability

- Over-engineering vs under-structuring
- Duplicated logic
- Violation of project conventions
- Unclear naming
- DRY, KISS, YAGNI

## Pass 3: Tests & Docs

- Are there tests? Do they cover critical paths?
- Are docs updated?

### Accessibility (web/frontend only)
- Semantic HTML (not divs for everything)
- Alt text on images
- Keyboard navigation
- Color contrast (4.5:1 normal, 3:1 large)
- Form labels
- ARIA where needed

## Output Format

```markdown
## Code Review: [File/PR Name]

### Critical Issues
- **[Location]**: [Issue] | **Fix**: [How]

### Important Suggestions
- **[Location]**: [Suggestion] | **Benefit**: [Why]

### Minor Improvements
- [Item]

### What's Good
- [Positive observation]

### Summary
[Approve / Request Changes / Needs Discussion]
```

| Severity | Description | Action |
|----------|-------------|--------|
| Critical | Security risk, data loss | Must fix before merge |
| Important | Bug, poor design | Should fix before merge |
| Minor | Style, optimization | Nice to have |
