# Web App Rules (Astro + Cloudflare + Better Auth + Postgres)

## Default Stack

When building web apps for this user:

```
Astro (frontend) + Cloudflare Workers (API) + Better Auth (auth) + Postgres on OCI (data)
Deploy to: Cloudflare Pages
```

## When to Use

Detect by presence of:
- `astro.config.mjs` or `astro.config.ts`
- `wrangler.toml`
- `package.json` with `astro` dependency

## Astro-Specific Rules

- **Astro is the framework** - Don't suggest Next.js, Remix, SvelteKit
- **Cloudflare adapter** - Use `@astrojs/cloudflare` for SSR
- **Islands architecture** - Server-first, add interactivity with client directives
- **Content Collections** - Use for structured content when applicable

## Cloudflare Workers Rules

- **API via Workers** - Don't suggest Express, FastAPI, or standalone API servers
- **Hyperdrive** - Use for Postgres connection pooling in production
- **wrangler.toml** - All deployment config lives here
- **Local dev** - Connect directly to Postgres via Tailscale (no Hyperdrive needed)

## Auth Rules

- **Better Auth** - Default auth library, don't suggest Clerk, Auth0, or NextAuth
- **Google OAuth** - Default provider via Better Auth
- **Sessions in Postgres** - Auth data lives in your database, you own it
- **Cloudflare Access** - Use for internal/admin tools only

## Database Rules

- **Postgres on OCI** - Default database for all web apps
- **Direct Tailscale connection** - For local dev (100.126.13.70:5432)
- **Hyperdrive** - For production (via Cloudflare Tunnel)
- **`postgres` npm package** - Use this, not pg/knex/prisma/drizzle unless needed

## Deployment

- **Cloudflare Pages** - Default deploy target
- **GitHub auto-deploy** - Connect repo in CF dashboard
- **Manual**: `npm run build && npx wrangler pages deploy dist`

## Anti-Patterns

- ❌ Don't suggest Convex, Next.js, Clerk, or Vercel (old stack)
- ❌ Don't suggest MongoDB, MySQL, or other databases
- ❌ Don't suggest Lucia auth (deprecated)
- ❌ Don't suggest standalone API servers (Express, FastAPI)
- ❌ Don't suggest heavy ORMs (Prisma, Drizzle) unless explicitly needed
