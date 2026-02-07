# /secrets — SOPS/Age Secret Management

Manage encrypted secrets between the master vault and projects.

## Master Vault

Location: `~/github/oneshot/secrets/`
Encryption: SOPS + Age (config in `~/github/oneshot/.sops.yaml`)

## Pull Secrets into Project

1. Identify which secrets this project needs (check .env.example or imports)
2. Decrypt from vault:
   ```bash
   sops -d ~/github/oneshot/secrets/<namespace>.enc.env
   ```
3. Write to project `.env` (must be gitignored)
4. Verify the app can start with the new secrets

## Push New Secrets to Vault

1. Identify new secrets (diff .env against vault)
2. Encrypt and add:
   ```bash
   sops -e ~/github/oneshot/secrets/<namespace>.enc.env
   ```
3. Commit the encrypted file to oneshot repo

## Common Operations

```bash
# Decrypt and view
sops -d ~/github/oneshot/secrets/research_keys.env.encrypted

# Edit in-place (opens in $EDITOR)
sops ~/github/oneshot/secrets/research_keys.env.encrypted

# Extract single key
sops -d --output-type dotenv ~/github/oneshot/secrets/file.enc.env | grep KEY_NAME

# Create new encrypted file
sops -e --age $(cat ~/.sops/age/keys.txt | grep public | cut -d: -f2) plaintext.env > encrypted.enc.env
```

## Safety Rules

- Never display secret values in output
- Always verify .env is in .gitignore before writing
- Namespace secrets by project in the vault
- Never commit plaintext secrets
- Never suggest .env files without encryption
