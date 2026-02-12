# Stack Setup Skill

Configure a project to use Omar's standard Cloudflare + Postgres stack.

## Triggers

Activate this skill when the user says:
- "set up cloudflare"
- "add database" / "add postgres" / "need a database"
- "configure for deploy"
- "set up the stack"
- "make this deployable"
- "push to cloud" (if no deployment config exists)

## Prerequisites

Before running this skill, verify:
1. Cloudflare Tunnel is running on OCI (`pg.omarsnewgroove.com` resolves)
2. User has `wrangler` CLI authenticated (`npx wrangler whoami`)
3. Postgres is running (`docker exec pg-server psql -U omar -c "SELECT 1"`)

## Actions

### 1. Read Infrastructure Docs

```
Read .claude/infrastructure/STACK.md for connection details and patterns.
```

### 2. Create Database

```bash
# Ask user for project/database name if not obvious from context
docker exec pg-server createdb -U omar PROJECT_NAME
```

### 3. Create Schema File

Create `schema.sql` with initial tables based on project requirements:

```sql
-- schema.sql
-- Run with: docker exec -i pg-server psql -U omar -d PROJECT_NAME < schema.sql

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add project-specific tables
```

### 4. Set Up Hyperdrive

```bash
npx wrangler hyperdrive create PROJECT_NAME-db \
  --connection-string="postgresql://omar:PASSWORD@pg.omarsnewgroove.com:5432/PROJECT_NAME"
```

Capture the returned ID for wrangler.toml.

### 5. Create/Update wrangler.toml

```toml
name = "PROJECT_NAME"
main = "src/worker.ts"  # or appropriate entry point
compatibility_date = "2024-01-01"

[[hyperdrive]]
binding = "HYPERDRIVE"
id = "HYPERDRIVE_ID_FROM_STEP_4"

[vars]
ENVIRONMENT = "production"
```

### 6. Add Astro Cloudflare Adapter (if Astro project)

```bash
npx astro add cloudflare
```

Update `astro.config.mjs`:
```javascript
import { defineConfig } from 'astro/config'
import cloudflare from '@astrojs/cloudflare'

export default defineConfig({
  output: 'server',
  adapter: cloudflare()
})
```

### 7. Create Database Client

Create `src/lib/db.ts`:

```typescript
import postgres from 'postgres'

export function createClient(env: { HYPERDRIVE?: Hyperdrive }) {
  const connectionString = env.HYPERDRIVE?.connectionString || process.env.DATABASE_URL

  if (!connectionString) {
    throw new Error('No database connection string available')
  }

  return postgres(connectionString)
}

// Type helper for Hyperdrive
export interface Env {
  HYPERDRIVE: Hyperdrive
}
```

### 8. Create Environment Files

**.env.example:**
```
# Local development (connect via Tailscale)
DATABASE_URL=postgresql://omar:YOUR_PASSWORD@100.126.13.70:5432/PROJECT_NAME
```

**.env.local** (gitignored):
```
DATABASE_URL=postgresql://omar:ACTUAL_PASSWORD@100.126.13.70:5432/PROJECT_NAME
```

### 9. Update .gitignore

Ensure these are ignored:
```
.env
.env.local
.env.*.local
.wrangler/
node_modules/
dist/
```

### 10. Set Up Better Auth

Create `src/lib/auth.ts`:
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

Add to `.env.example`:
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 11. Install Dependencies

```bash
npm install postgres better-auth
```

### 12. Test Connection

Create a simple test:
```typescript
// test-db.ts
import postgres from 'postgres'

const sql = postgres(process.env.DATABASE_URL!)

async function test() {
  const result = await sql`SELECT NOW() as time`
  console.log('Connected! Server time:', result[0].time)
  await sql.end()
}

test().catch(console.error)
```

Run: `npx tsx test-db.ts`

## Output Checklist

- [ ] Database created on pg-server
- [ ] schema.sql with initial tables
- [ ] wrangler.toml with Hyperdrive configured
- [ ] Astro cloudflare adapter (if applicable)
- [ ] src/lib/db.ts client
- [ ] .env.example and .env.local
- [ ] Updated .gitignore
- [ ] Better Auth configured with Google OAuth
- [ ] postgres + better-auth packages installed
- [ ] Verified database connection

## Notes

- Always use the Tailscale IP (100.126.13.70) for local dev
- Always use the tunnel hostname (pg.omarsnewgroove.com) for Hyperdrive
- Password is in `~/pg-server/.env` on OCI - never commit it
- Test locally before deploying to catch connection issues early
