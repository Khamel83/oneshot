# /sync-secrets — SOPS/Age Secret Synchronization

Sync secrets between the master vault and the current project.

## Pull secrets into project
1. Identify which secrets this project needs (check .env.example or imports)
2. Decrypt from vault: `sops -d ~/github/oneshot/secrets/<namespace>.enc.env`
3. Write to project `.env` (gitignored)
4. Verify the app can start with the new secrets

## Push new secrets to vault
1. Identify new secrets added to project (diff .env against vault)
2. Encrypt and add to vault: `sops -e` with age key from `.sops.yaml`
3. Commit the encrypted file to oneshot repo

## Safety
- Never display secret values in output
- Always verify .env is in .gitignore before writing
- Namespace secrets by project in the vault
