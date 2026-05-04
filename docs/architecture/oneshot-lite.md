# OneShot Lite Architecture

Date: 2026-05-04

## Decision

OneShot Lite is not a general orchestration framework and is not the owner of
the developer machine fleet.

OneShot Lite is a small private adapter kit that makes better-maintained agent
workflow projects usable in Khamel's repos. It owns private repo/context glue;
`homelab` owns physical infrastructure, machine readiness, SSH/Tailscale, cron,
repo sync, and CLI bootstrap.

## Target Split

| Layer | Owner | Why |
|---|---|---|
| Machine fleet and CLI readiness | `homelab` | SSH aliases, Tailscale, cron, auth files, shell setup, and repo sync are infrastructure. |
| Coding workflow | Superpowers or Matt skills | Generic planning, execution, debugging, review, and TDD should be maintained upstream. |
| Behavioral guardrails | Karpathy-style guidelines | Low-overhead rules fit the always-on instruction layer. |
| Knowledge/wiki | External wiki skills | Persistent Markdown knowledge should not become another OneShot subsystem. |
| Private repo glue | OneShot Lite | Argus, secrets wrappers, repo source-of-truth maps, handoff/restore, and adapters. |

## OneShot Lite Owns

- Argus-backed `/doc`, `/research`, and `/freesearch`
- `/handoff` and `/restore`
- repo source-of-truth and verification maps
- private context injection for sensitive repos and local conventions
- thin adapters that recommend or invoke external workflows
- small wrappers around private tools such as the secrets vault

## OneShot Lite Does Not Own

- machine inventory
- cross-machine CLI installation or auth readiness
- Tailscale reachability
- cron ownership
- repo auto-sync
- generic `/short`, `/full`, `/conduct`, `/debug`, or `/tdd` process bodies
- a second custom task router when an upstream workflow can own the behavior

## Homelab Dependency

When OneShot needs fleet state, it should consume `homelab` instead of encoding
its own truth:

```bash
make -C ~/github/homelab doctor-dev-tools
make -C ~/github/homelab doctor-dev-tools-local
```

The homelab source of truth is `config/developer-fleet.tsv` plus
`scripts/doctor-dev-tools.sh`.

## Target Layout

```text
oneshot/
├── bin/
│   └── oneshot
├── config/
│   ├── repos.yaml
│   └── adapters.yaml
├── core/
│   ├── argus/
│   ├── handoff/
│   ├── secrets/
│   └── context/
├── docs/
│   ├── architecture/
│   └── research/
├── 1shot/
│   └── handoffs/
└── scripts/
    ├── oneshot-update.sh
    └── validate-lite.sh
```

Compatibility files such as `.oneshot/config/machines.yaml` may remain during
the transition, but they are not the target ownership model.

## Migration Rules

1. Freeze new generic OneShot skills.
2. Replace broad process commands with wrappers or deprecation notices.
3. Keep Argus, secrets, handoff, restore, and repo-context behavior small.
4. Delegate fleet checks and bootstrap to `homelab`.
5. Archive `core/router/` and `core/dispatch/` when external workflow adapters
   have replaced the custom routing surface.
