# Web App Rules (Convex + Next.js + Clerk)

## Default Stack

When building web apps for this user:

```
Convex (backend) + Next.js (frontend) + Clerk (auth) → Deploy to Vercel
```

## When to Use

Detect by presence of:
- `package.json` with `convex` dependency
- `convex/` directory
- `app/` or `pages/` directory

## Convex-Specific Rules

- **Backend is Convex** - Don't suggest Express, FastAPI, or custom backends
- **File-based routing** - Use `convex/schema.ts` for data model
- **Real-time by default** - Leverage Convex subscriptions
- **Auth via Clerk** - Don't build custom auth

## Next.js-Specific Rules

- **App Router preferred** - Use `app/` directory over `pages/`
- **Server Components** - Default to RSC, use Client Components sparingly
- **API Routes via Convex** - Don't use Next.js API routes, use Convex functions

## Deployment

- **Vercel** - Default deploy target, no configuration needed
- **Convex dashboard** - `npx convex dev` for local development

## Anti-Patterns

- ❌ Don't suggest PostgreSQL, MongoDB, or other databases
- ❌ Don't suggest custom authentication
- ❌ Don't suggest API routes (use Convex functions)
- ❌ Don't suggest server-side frameworks (Express, FastAPI)
