# Secrets Management

Vault: `~/github/oneshot/secrets/` — single source of truth, SOPS/Age encrypted, auto-synced to all machines.

```bash
secrets get KEY                        # fetch one value
secrets set FILE KEY=value [--commit]  # add/update (--commit pushes immediately)
secrets list                           # show all vault files and key names
secrets init FILE                      # write FILE.env → .env in current dir
secrets decrypt FILE                   # dump full file to stdout
```

Which file has which key: run `secrets list`. Full vault index: `docs/instructions/secrets-reference.md`

Never commit `.env` files. Never hardcode keys in scripts. Never use `~/github/secrets-vault/` (deprecated).
