# Machine Readiness

`oneshot doctor` checks whether each machine has the tools, auth, and secrets needed to run the delegation harness.

## Quick Start

```bash
# Check this machine
./bin/oneshot doctor

# Fix what we can
./bin/oneshot doctor --fix

# Check all machines
./bin/oneshot doctor --all-machines

# Fix all machines
./bin/oneshot doctor --all-machines --fix
```

## What It Checks

| Check | What it verifies |
|-------|-----------------|
| `python3` | Python 3 runtime |
| `git` | Git version control |
| `claude` | Claude Code CLI installed |
| `opencode` | OpenCode CLI installed |
| `oc launcher` | Local `oc` wrapper exists on PATH |
| `opencode auth` | At least one provider authenticated |
| `gemini` | Gemini CLI installed |
| `gemini auth` | Gemini can actually respond (runs `gemini -p "Say READY"`) |
| `codex` | Codex CLI installed |
| `codex auth` | `~/.codex/auth.json` exists with valid refresh token |
| `secrets cli` | `secrets` command on PATH |
| `secrets decrypt` | `secrets list` successfully decrypts the vault |
| `age key` | `~/.age/key.txt` exists |
| `worktree path` | Worktree parent directory exists and is writable |
| `repo path` | `.oneshot/tasks/` exists |
| `ssh config` | All machine hosts are in `~/.ssh/config` |

## Status Values

| Status | Meaning |
|--------|---------|
| `OK` | Check passed. Detail shows version/path. |
| `MISSING` | Tool not installed or path doesn't exist. |
| `AUTH_REQUIRED` | Tool installed but not authenticated. |
| `BLOCKED_BY_PASSPHRASE` | SOPS/age decrypt failed (bad key or passphrase). |
| `UNKNOWN_ERROR` | Unexpected error. Check the detail. |

## Exit Codes

- `0` — all checks passed
- `1` — some checks failing (no auth blockers)
- `2` — at least one AUTH_REQUIRED or BLOCKED_BY_PASSPHRASE

## Local vs Remote Checks

- Local runs include `worktree path` and `repo path` checks.
- Remote runs do not mark those local-only paths as missing; they only report what can be checked meaningfully over SSH.

## Env Var Overrides

Machine config in `.oneshot/config/machines.yaml` supports `${VAR:-default}` syntax:

```bash
# Override a single machine's host
ONESHOT_MACHINE_OCI_HOST=my-custom-alias ./bin/oneshot doctor --all-machines

# Override a repo path
ONESHOT_MACHINE_HOMELAB_REPO=/home/me/projects/oneshot ./bin/oneshot doctor --all-machines
```

## Adding a New Machine

1. Add the SSH alias to `~/.ssh/config` on all machines:
   ```
   Host newmachine-ts
       HostName 100.x.x.x
       User youruser
   ```

2. Add to `.oneshot/config/machines.yaml`:
   ```yaml
   machines:
     newmachine:
       host: newmachine-ts
       repo_path: /home/user/github/oneshot
       role: worker
       enabled: true
   ```

3. Clone oneshot on the new machine and run `./bin/oneshot doctor`

## SSH Alias Convention

All machine SSH aliases use the `-ts` Tailscale suffix: `oci-ts`, `macmini-ts`, `homelab-ts`. This is the canonical form. Never use raw Tailscale IPs.

## Why Not `gog`

Gemini CLI readiness is tested directly with `gemini -p "Say READY"`. We do not use `gog` for any readiness check. `gog` may prompt for a keyring passphrase and block execution. If you see `BLOCKED_BY_PASSPHRASE` on a secrets check, the issue is with the SOPS/Age key at `~/.age/key.txt`, not with Gemini.

## Troubleshooting

### `BLOCKED_BY_PASSPHRASE` on secrets decrypt

1. Check `~/.age/key.txt` exists and is non-empty
2. Verify it's the correct age private key (from 1Password: "SOPS age encryption key")
3. Run `secrets list` manually to see the exact error

### `AUTH_REQUIRED` on gemini auth

Run `gemini` directly — it will open a browser for Google login. This is interactive and cannot be autofixed.

### `AUTH_REQUIRED` on codex auth

Run `codex login --device-auth` on a machine with browser access. Copy `~/.codex/auth.json` from there.

### SSH failing for a machine

1. Verify the host alias works: `ssh -o BatchMode=yes oci-ts echo ok`
2. Check `~/.ssh/config` has the correct `HostName` and `User`
3. Ensure SSH keys are shared across machines
