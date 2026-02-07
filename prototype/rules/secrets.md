# Secrets Management

All secrets use SOPS + Age encryption. Master vault at `~/github/oneshot/secrets/`.

To decrypt: `sops -d secrets/<file>.enc.env`
To encrypt: `sops -e --age <age-key> <file>.env > secrets/<file>.enc.env`
Config at `~/github/oneshot/.sops.yaml`

Never commit plaintext secrets. Never put secrets in CLAUDE.md or rules files.
Never suggest .env files without encryption.
