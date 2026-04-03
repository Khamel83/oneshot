# Omar's Standard Stack

## Overview

Every web project uses this stack unless there's a good reason not to:

```
[Local Dev]
    ↓ git push / vercel deploy
[Vercel] ← hosting (static frontend + Python serverless)
    ↓
[Supabase Postgres] ← database (hosted, free tier: 500MB)
    ↓
[Supabase Auth] ← authentication (email/password + Google OAuth)
```

**Why this stack:**
- $0 cost (Vercel Hobby + Supabase Free)
- No self-hosted database to maintain
- Fast (Vercel edge + Supabase connection pooling)
- Simple (Python functions + SQL + HTML)
- LLM-friendly (every AI knows this stack)

---

## Database (Supabase Postgres)

### Setup

1. Create project at [supabase.com](https://supabase.com)
2. Get connection string from Project Settings → Database
3. Store in secrets: `secrets set PROJECT_NAME 'DATABASE_URL=postgresql://...'`

### Connection Info

```
Host: db.<project-ref>.supabase.co
Port: 5432 (or 6543 via pooler)
Database: postgres
```

### Common Operations

**Run migrations:**
```bash
supabase db push          # Push local migrations
supabase db reset         # Reset to migration baseline
supabase migration new <name>  # Create new migration
```

**Direct SQL:**
```bash
# Via Supabase CLI
supabase db execute --file schema.sql

# Via psql
psql "postgresql://postgres:[PASSWORD]@db.<ref>.supabase.co:5432/postgres"
```

**Backup:**
```bash
supabase db dump --data-only > backup.sql
```

---

## Authentication (Supabase Auth)

### Default Setup

Supabase Auth handles email/password and social logins out of the box.

**Install client:**
```bash
npm install @supabase/supabase-js
# or pip install supabase
```

**Frontend init:**
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
```

**Google OAuth setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID
3. Set redirect URI: `https://<project-ref>.supabase.co/auth/v1/callback`
4. Add credentials to Supabase Dashboard → Authentication → Providers → Google

### Environment Variables

```
NEXT_PUBLIC_SUPABASE_URL=https://<ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>
```

Store in secrets: `secrets set PROJECT_NAME 'NEXT_PUBLIC_SUPABASE_URL=...'`

---

## Frontend (HTML + Vanilla JS)

No build step required. Plain HTML, CSS, and JavaScript.

### Structure

```
my-project/
├── public/              # Static assets
├── api/                 # Python serverless functions (Vercel)
│   ├── index.py         # Router
│   └── handlers/        # Handler modules
├── pages/               # HTML pages
│   ├── index.html
│   └── dashboard.html
├── js/                  # Client-side JavaScript
├── css/                 # Stylesheets
├── vercel.json          # Vercel config
├── supabase/            # Supabase migrations
│   └── migrations/
├── .env.local           # Local dev (gitignored)
└── package.json         # Supabase client only
```

---

## Backend (Python Serverless on Vercel)

Vercel runs Python functions as serverless endpoints.

### vercel.json

```json
{
  "builds": [{ "src": "api/index.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/api/(.*)", "dest": "/api/index.py" }]
}
```

### Router Pattern

```python
# api/index.py
from handlers.auth import handle_auth
from handlers.data import handle_data

def handler(request):
    path = request.path

    if path.startswith('/api/auth'):
        return handle_auth(request)
    elif path.startswith('/api/data'):
        return handle_data(request)
    else:
        return {'statusCode': 404, 'body': 'Not found'}
```

### Database in Functions

```python
import os
import supabase

# Init once (reused across invocations in same runtime)
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_KEY']
db = supabase.create_client(url, key)

def get_users():
    result = db.table('users').select('*').execute()
    return result.data
```

---

## Deployment

**Deploy to Vercel:**
```bash
vercel                 # Deploy (prompts for project setup on first run)
vercel --prod          # Deploy to production
```

**Or connect GitHub for auto-deploy:**
1. Go to [vercel.com](https://vercel.com) → Add New Project
2. Import GitHub repository
3. Framework preset: Other
4. Deploy

**Environment variables:**
```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_KEY
```

Or set in Vercel Dashboard → Settings → Environment Variables.

---

## Local Development

### Supabase Local

```bash
# Start local Supabase stack (Postgres, Auth, Storage)
supabase start

# Run migrations locally
supabase db reset

# Local Supabase URL
# http://localhost:54321 (API)
# http://localhost:54322 (Studio)
```

### Vercel Local

```bash
vercel dev    # Starts local dev server with serverless functions
```

### .env.local

```
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<local-anon-key>
SUPABASE_SERVICE_KEY=<local-service-key>
```

---

## Per-Project Setup

### 1. Create Supabase Project

Go to [supabase.com](https://supabase.com) → New Project

### 2. Run Schema Migrations

```bash
supabase init                    # Initialize local Supabase
supabase migration new initial   # Create migration
# Edit supabase/migrations/<timestamp>_initial.sql
supabase db push                 # Apply to remote
```

### 3. Configure Vercel

```bash
vercel link                      # Link to Vercel project
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_KEY
```

### 4. Set Up Auth (optional)

Enable providers in Supabase Dashboard → Authentication → Providers

### 5. Deploy

```bash
vercel --prod
```

---

## Cost

| Component | Cost |
|-----------|------|
| Vercel Hobby | Free (100GB bandwidth, serverless functions) |
| Supabase Free | 500MB database, 50K monthly active users, 5GB bandwidth |
| Supabase Auth | Free (50K MAU) |
| **Total** | **$0** |

**Scale triggers:**
- >500MB DB or >50K MAU → Supabase Pro ($25/mo)
- >100GB bandwidth → Vercel Pro ($20/mo)

---

## Troubleshooting

### Can't connect to Supabase

1. Check `SUPABASE_URL` and key are set: `vercel env ls`
2. Verify project is not paused (Supabase pauses free projects after 1 week inactivity)
3. Check Supabase Dashboard → Settings → Database for connection info

### Serverless function timeout

1. Vercel Hobby: 10s max (configurable in vercel.json)
2. Move long-running tasks to background processing
3. Use `vercel.json` to increase: `{"functions": {"api/**/*.py": {"maxDuration": 60}}}`

### Migration conflicts

1. `supabase db pull` to sync remote state
2. Resolve conflicts manually
3. `supabase db push` to apply

---

## Internal Tools: Cloudflare Access

For admin dashboards and internal tools, use Cloudflare Access (already configured). No code needed — just toggle on in the Cloudflare dashboard.
