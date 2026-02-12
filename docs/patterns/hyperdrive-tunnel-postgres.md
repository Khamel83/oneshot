# Hyperdrive + Tunnel + Postgres Pattern

Connect Cloudflare Workers to a private Postgres database via Hyperdrive.

## Architecture

```
Worker → Hyperdrive → Access → Tunnel → Postgres
```

## Prerequisites

1. Postgres database with SSL enabled
2. Cloudflare Tunnel (`cloudflared`) running on the database host
3. Cloudflare API token with: Hyperdrive:Edit, Access: Service Tokens:Edit, Access: Apps and Policies:Edit

## Setup (Dashboard - Recommended)

The dashboard auto-creates Access app + Service Token. API approach has integration issues.

1. **Enable SSL on Postgres:**
   ```bash
   # Generate self-signed cert
   mkdir -p ~/pg-server/certs
   openssl req -new -x509 -days 3650 -nodes \
     -out ~/pg-server/certs/server.crt \
     -keyout ~/pg-server/certs/server.key \
     -subj "/CN=pg-server"
   
   # Copy to postgres data dir with correct ownership
   docker run --rm -v pg-server_pgdata:/data -v ~/pg-server/certs:/certs alpine \
     sh -c "cp /certs/* /data/ && chown 999:999 /data/server.key && chmod 600 /data/server.key"
   
   # Update docker-compose.yml to enable SSL
   # command: -c ssl=on -c ssl_cert_file=/var/lib/postgresql/data/server.crt -c ssl_key_file=/var/lib/postgresql/data/server.key
   ```

2. **Create Tunnel:**
   ```bash
   cloudflared tunnel create <tunnel-name>
   cloudflared tunnel route dns <tunnel-name> <hostname>
   ```

3. **Create Hyperdrive (Dashboard):**
   - Go to: Cloudflare Dashboard → Storage & Databases → Hyperdrive
   - Select "Private database"
   - Choose tunnel and hostname
   - Select "Create new (automatic)" for Access Token and Application
   - SSL Mode: Require
   - Enter database credentials

## Worker Configuration

**wrangler.jsonc:**
```json
{
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_flags": ["nodejs_compat"],
  "hyperdrive": [
    {
      "binding": "HYPERDRIVE",
      "id": "<hyperdrive-config-id>"
    }
  ]
}
```

**src/index.ts:**
```typescript
import { Client } from "pg";

export default {
  async fetch(request, env, ctx) {
    const client = new Client({ connectionString: env.HYPERDRIVE.connectionString });
    await client.connect();
    
    const result = await client.query("SELECT * FROM my_table");
    return Response.json({ data: result.rows });
  },
};
```

## Secrets

Store in `secrets/cloudflare.env.encrypted`:
```
CLOUDFLARE_API_TOKEN=<token>
CLOUDFLARE_ACCOUNT_ID=<account-id>
CLOUDFLARE_HYPERDRIVE_ID=<hyperdrive-id>
```

## Troubleshooting

- **403 Forbidden**: Access app not properly integrated with tunnel. Use dashboard to create.
- **SSL errors**: Postgres must have SSL enabled with valid cert (self-signed OK).
- **Connection refused**: Check tunnel is running and hostname resolves.

## Reference

- Tunnel ID: `ef168144-ee55-48f6-aa93-a1c2c6d0d02b` (oneshot-pg)
- Hostname: `pg.khamel.com`
- Hyperdrive ID: `6a5f56df186a4ec4953a4fa77e0681f6`
