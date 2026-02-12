# Omar's Standard Stack

## Overview

Every project uses this stack unless there's a good reason not to:

```
[Local Dev]
    ↓ git push
[Cloudflare Pages] ← static frontend (Astro)
    ↓
[Cloudflare Workers] ← serverless API
    ↓
[Cloudflare Hyperdrive] ← connection pooler + query cache
    ↓
[Postgres on OCI] ← data (self-hosted, free forever)
```

**Why this stack:**
- $0 cost (Cloudflare free tier + OCI free tier)
- No vendor lock-in on data (Postgres is yours)
- Fast (edge compute + cached queries)
- Simple (Astro + Workers + SQL)
- LLM-friendly (every AI knows this stack)

---

## Database

### Connection Info

**Host:** `100.126.13.70` (Tailscale IP - only accessible from Tailscale network)
**Port:** `5432`
**User:** `omar`
**Password:** See `~/pg-server/.env` on OCI box

**Connection string format:**
```
postgresql://omar:PASSWORD@100.126.13.70:5432/DATABASE_NAME
```

### Common Operations

**Create new database for a project:**
```bash
# From any machine on Tailscale
ssh ubuntu@100.126.13.70 "docker exec pg-server createdb -U omar project_name"

# Or if already on OCI
docker exec pg-server createdb -U omar project_name
```

**List all databases:**
```bash
docker exec pg-server psql -U omar -c "\l"
```

**Access psql directly:**
```bash
docker exec -it pg-server psql -U omar -d database_name
```

**Run a SQL file:**
```bash
docker exec -i pg-server psql -U omar -d database_name < schema.sql
```

**Backup all databases:**
```bash
cd ~/pg-server && ./backup.sh
```

**Backup single database:**
```bash
docker exec pg-server pg_dump -U omar database_name > backup.sql
```

---

## Cloudflare Tunnel (Already Configured)

The tunnel connects Cloudflare's network to the Postgres instance on OCI without exposing it to the public internet.

**Tunnel hostname:** `pg.omarsnewgroove.com` (or check `~/.cloudflared/config.yml` on OCI)

**Status check:**
```bash
ssh ubuntu@100.126.13.70 "sudo systemctl status cloudflared"
```

**If tunnel needs restart:**
```bash
ssh ubuntu@100.126.13.70 "sudo systemctl restart cloudflared"
```

---

## Per-Project Setup

### 1. Create the Database

```bash
docker exec pg-server createdb -U omar my_project
```

### 2. Set Up Hyperdrive

```bash
# One-time per project
npx wrangler hyperdrive create my-project-db \
  --connection-string="postgresql://omar:PASSWORD@pg.omarsnewgroove.com:5432/my_project"
```

Save the ID it returns.

### 3. Configure wrangler.toml

```toml
name = "my-project"
main = "src/worker.ts"
compatibility_date = "2024-01-01"

[[hyperdrive]]
binding = "HYPERDRIVE"
id = "your-hyperdrive-id-here"
```

### 4. Use in Worker Code

```typescript
import postgres from 'postgres'

export interface Env {
  HYPERDRIVE: Hyperdrive
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const sql = postgres(env.HYPERDRIVE.connectionString)

    const users = await sql`SELECT * FROM users WHERE active = true`

    return Response.json(users)
  }
}
```

### 5. Astro + Cloudflare Adapter

```bash
npx astro add cloudflare
```

In `astro.config.mjs`:
```javascript
import { defineConfig } from 'astro/config'
import cloudflare from '@astrojs/cloudflare'

export default defineConfig({
  output: 'server',
  adapter: cloudflare()
})
```

---

## Local Development

For local dev, connect directly via Tailscale (no Hyperdrive needed):

**.env.local:**
```
DATABASE_URL=postgresql://omar:PASSWORD@100.126.13.70:5432/my_project
```

**In code, handle both environments:**
```typescript
const connectionString = env.HYPERDRIVE?.connectionString || process.env.DATABASE_URL
const sql = postgres(connectionString)
```

---

## Project Structure (Astro + Workers)

```
my-project/
├── src/
│   ├── pages/           # Astro pages
│   ├── components/      # UI components
│   ├── layouts/         # Page layouts
│   └── lib/
│       └── db.ts        # Database client
├── functions/           # Cloudflare Workers (if separate from Astro)
├── public/              # Static assets
├── astro.config.mjs
├── wrangler.toml        # Cloudflare config
├── .env.local           # Local dev (gitignored)
├── .env.example         # Template for others
└── package.json
```

---

## Deployment

**Deploy to Cloudflare Pages:**
```bash
npm run build
npx wrangler pages deploy dist
```

**Or connect GitHub for auto-deploy:**
1. Go to Cloudflare Dashboard → Pages
2. Connect repository
3. Build command: `npm run build`
4. Output directory: `dist`

---

## Backups

**Automated (cron on OCI):**
```bash
# Add to crontab: crontab -e
0 3 * * * cd ~/pg-server && ./backup.sh
```

**Manual backup:**
```bash
ssh ubuntu@100.126.13.70 "cd ~/pg-server && ./backup.sh"
```

**Backup location:** `~/pg-server/backups/` on OCI (7-day retention)

---

## Troubleshooting

### Can't connect to database
1. Check Tailscale is connected: `tailscale status`
2. Check Postgres is running: `ssh oci "docker ps | grep pg-server"`
3. Check credentials: `ssh oci "cat ~/pg-server/.env"`

### Hyperdrive not working
1. Verify tunnel is running: `ssh oci "sudo systemctl status cloudflared"`
2. Check Hyperdrive config: `npx wrangler hyperdrive list`
3. Test direct connection first before debugging Hyperdrive

### Worker can't reach database
1. Confirm Hyperdrive binding in wrangler.toml
2. Check you're using `env.HYPERDRIVE.connectionString`
3. Verify the Hyperdrive ID matches

---

## Authentication

### Default: Better Auth + Google OAuth

**Better Auth** is the default auth library. Sessions stored in your Postgres.

**Install:**
```bash
npm install better-auth
```

**Setup `src/lib/auth.ts`:**
```typescript
import { betterAuth } from 'better-auth'
import postgres from 'postgres'

const sql = postgres(process.env.DATABASE_URL!)

export const auth = betterAuth({
  database: sql,
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
})
```

**Google OAuth setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID
3. Set redirect URI: `https://your-site.pages.dev/api/auth/callback/google`
4. Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to `.env.local`

**Environment variables needed:**
```
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Internal Tools: Cloudflare Access

For admin dashboards and internal tools, use Cloudflare Access (already configured). No code needed — just toggle on in the Cloudflare dashboard.

---

## Cost

| Component | Cost |
|-----------|------|
| Cloudflare Pages | Free (unlimited sites) |
| Cloudflare Workers | Free (100k requests/day) |
| Cloudflare Hyperdrive | Free tier available |
| Cloudflare Tunnel | Free |
| OCI Compute | Free tier (ARM, 24GB RAM) |
| Postgres | Free (self-hosted) |
| Better Auth | Free (open-source) |
| Cloudflare Access | Free (50 users) |
| **Total** | **$0** |
