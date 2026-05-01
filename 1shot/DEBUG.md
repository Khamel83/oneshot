## Symptom
Codex reports: `MCP client for argus failed to start: MCP startup failed: Environment variable ARGUS_API_KEY for MCP server 'argus' is not set`.

## Expected vs Actual
- Expected: Codex starts the `argus` MCP server using `ARGUS_API_KEY` from the shell environment.
- Actual: New clean shells can find `secrets` after startup, but `ARGUS_API_KEY` is not exported during startup.

## Error Output
```text
MCP client for `argus` failed to start: MCP startup failed: Environment variable ARGUS_API_KEY for MCP server 'argus' is not set
```

Clean-shell reproduction before the fix:
```text
ARGUS=
secrets=/home/ubuntu/.local/bin/secrets
```

## Context
- Files read: `~/.codex/config.toml`, `~/.bashrc`, `~/.profile`, `~/.bash_profile`, `config/search.yaml`, `core/search/argus_client.py`, `.claude/memory/memory.md`, `.claude/memory/learnings.md`
- Recent changes: `ccf4f59 fix: align argus search modes` updated Argus config/client docs; `ff7dfc6 fix: restore ci routing checks` did not affect MCP startup.
- Tests: Argus HTTP health passed with the current environment.

## Root Cause
`~/.bashrc` tried to export `ARGUS_API_KEY` before adding `~/.local/bin` to `PATH`, so clean shell startup skipped the `secrets` lookup.

## Bug Class
Environment issue: shell startup order / missing config in parent process.

## Evidence
- `/home/ubuntu/.codex/config.toml` configures `mcp_servers.argus.bearer_token_env_var = "ARGUS_API_KEY"`, so Codex requires that environment variable before MCP startup.
- `/home/ubuntu/.bashrc` exported `ARGUS_API_KEY` before the PATH block that makes `/home/ubuntu/.local/bin/secrets` available.
- Clean login and interactive shells showed `ARGUS_API_KEY` empty while `secrets` was available by the time the prompt finished loading.

## Proposed Fix
Move the PATH/tool initialization block before the vault-backed API key exports in `~/.bashrc`.

## Risk Assessment
- Could break: early shell startup if `nvm` or PATH initialization has side effects.
- Safe because: the same PATH/tool block already ran before the interactive guard; this only moves it a few lines earlier so vault exports can find `secrets`.

## Verification Plan
Start a clean login shell and confirm `ARGUS_API_KEY` is set without inheriting the current session environment. Then confirm Argus health still returns OK.

## Fix Applied
- Changed: `/home/ubuntu/.bashrc` now initializes PATH before calling `secrets get ARGUS_API_KEY argus`.
- Verification: clean login shell and clean interactive shell both report `ARGUS=set`; clean-shell Argus health returned `{"status": "ok"}`.
- Regression test: `bash -n ~/.bashrc` passed.

## Follow-up: Same-Shell Retry Still Fails

### Symptom
After the `.bashrc` fix, running `codex --yolo` again from the same terminal prompt still reports:

```text
MCP client for `argus` failed to start: MCP startup failed: Environment variable ARGUS_API_KEY for MCP server 'argus' is not set
```

### Root Cause
The retry was launched from the already-running parent shell that had started before `.bashrc` was fixed. Codex reads `ARGUS_API_KEY` from its parent process environment at startup; editing `.bashrc` cannot retroactively update an existing shell.

### Evidence
- Clean login shell: `ARGUS_API_KEY` is set.
- Clean interactive shell: `ARGUS_API_KEY` is set.
- Current fixed Codex process: `ARGUS_API_KEY` is set.
- `codex mcp list` from a clean login shell shows `argus` enabled with `ARGUS_API_KEY`.
- Argus `/api/health` from a clean login shell returns `{"status": "ok"}`.

### Operational Fix
From any terminal that was open before the `.bashrc` fix, run:

```bash
source ~/.bashrc
hash -r
codex --yolo
```

Opening a new login shell also works.
