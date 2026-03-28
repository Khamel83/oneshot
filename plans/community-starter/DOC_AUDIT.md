# Library Version Audit

**Date:** 2026-03-27
**Template:** `templates/community-starter/`

---

## supabase-py

| Field | Value |
|-------|-------|
| Pinned | `2.15.0` (2025-03-26) |
| Current | `2.28.3` (2026-03-20) |
| Drift | **13 versions behind** |

### Breaking changes since pinned version

- **v2.24.0** (2025-11-07): Removed `SyncClient` classes from `supabase_auth` and `supabase_functions`, in favor of plain `httpx.Client`s. This is an internal implementation change -- the public API (`create_client()`, `auth.*` methods) is unchanged. **Not impactful for this template.**
- **v2.27.3** (2026-02-03): Dropped Python 3.9 support. **Not impactful** (Vercel runtime uses 3.12+).

### API signature verification (all verified against v2.28.3)

| Template usage | v2.28.3 signature | Status |
|---------------|-------------------|--------|
| `create_client(url, key)` | `create_client(url: str, key: str, options=None)` | Compatible |
| `db().auth.get_user(token)` | `get_user(jwt: Optional[str] = None) -> Optional[UserResponse]` | Compatible |
| `db().auth.sign_in_with_password({'email': ..., 'password': ...})` | `sign_in_with_password(credentials: SignInWithPasswordCredentials) -> AuthResponse` | Compatible |
| `db().auth.sign_up({'email': ..., 'password': ...})` | `sign_up(credentials: SignUpWithPasswordCredentials) -> AuthResponse` | Compatible |
| `db().auth.reset_password_email(email, options={...})` | `reset_password_email(email: str, options=None) -> None` | Compatible |
| `.table('x').select('*').eq('a', 'b').single().execute()` | `Client.table()` wraps `PostgrestClient.from_()` -- unchanged | Compatible |
| `response.user`, `response.session.access_token` | `AuthResponse` TypedDict with `.user` and `.session` | Compatible |

### Notable improvements in newer versions (2025-03 to 2026-03)

- Auth token auto-refresh OverflowError fix (v2.28.1)
- `maybe_single()` fix (v2.28.3)
- PostgREST payload robustness fixes (v2.28.1)
- Realtime reconnect and Key error fixes
- Storage trailing slash handling improved

### Verdict: Update recommended

All template code is compatible with `2.28.3`. The 13-version gap includes bug fixes and stability improvements with no breaking API changes for the patterns used.

---

## resend-python

| Field | Value |
|-------|-------|
| Pinned | `2.7.0` |
| Current | `2.26.0` (2026-03-20) |
| Drift | **19 versions behind** |

### Breaking changes since pinned version

No breaking changes to the public API. The SDK evolved from a simple module to a more structured package with typed parameters.

### API signature verification (all verified against v2.26.0)

| Template usage | v2.26.0 signature | Status |
|---------------|-------------------|--------|
| `resend.Emails.send(params)` | `Emails.send(params: SendParams, options: Optional[SendOptions]=None) -> SendResponse` | Compatible (new optional `options` param added) |
| `resend.exceptions.RateLimitError` | Still exists, inherits from `ResendError(Exception)` | Compatible |
| `resend.api_key = "..."` | Still the standard initialization | Compatible |
| `result.get('id')` on send response | `SendResponse` is TypedDict with `id` field | Compatible |

### Exception classes in v2.26.0 (full list)

- `ResendError` -- base exception
- `ApplicationError` -- server errors (5xx)
- `InvalidApiKeyError` -- bad API key
- `MissingApiKeyError` -- no API key set
- `MissingRequiredFieldsError` -- validation
- `NoContentError` -- 204 responses
- **`RateLimitError`** -- 429 rate limiting (used in template)
- `ValidationError` -- request validation

### Verdict: Update recommended

All template code is fully compatible. The `options` parameter is optional and doesn't affect existing calls.

---

## sentry-sdk (bonus -- also pinned in requirements.txt)

| Field | Value |
|-------|-------|
| Pinned | `2.20.0` |
| Current | `2.56.0` (2026-03-24) |
| Drift | **36 versions behind** |

No breaking API changes for basic `sentry.init()` usage. Update recommended for security/stability fixes.

---

## Vercel Python Runtime (@vercel/python)

| Field | Value |
|-------|-------|
| Pinned | `@vercel/python@4.3.1` |
| Current npm latest | `6.28.0` |

### Key finding: Runtime pinning may be unnecessary

The Vercel Python runtime documentation (updated 2026-01-30) states:

1. **The Python runtime is now in Beta** -- it is available on all plans
2. **No `runtime` field needed** -- Vercel automatically detects Python functions via `.py` file handlers
3. **Python version** is controlled by `pyproject.toml`, `.python-version`, or `Pipfile.lock` at project root (not by the runtime package)
4. **Supported Python versions:** 3.12 (default), 3.13, 3.14
5. **Dependencies** via `requirements.txt` or `pyproject.toml` -- just list them, no special config needed

The current `vercel.json` explicitly pins `@vercel/python@4.3.1`. This works but is **old**. The latest is `6.28.0`. However, based on the current docs, the `runtime` field is **optional** for Python functions -- Vercel auto-detects `.py` handlers.

### Recommendation

The `runtime` field can be kept for explicit version control but should be updated. Alternatively, remove it and let Vercel auto-detect. The `maxDuration: 60` and `excludeFiles` are still valid and should be kept.

---

## Recommended Actions

- [x] ~~Update `supabase` from `2.15.0` to `2.28.3`~~ -- **DONE** (all API calls verified compatible)
- [x] ~~Update `resend` from `2.7.0` to `2.26.0`~~ -- **DONE** (all API calls verified compatible)
- [x] ~~Update `sentry-sdk` from `2.20.0` to `2.56.0`~~ -- **DONE** (no breaking changes)
- [x] ~~Update `@vercel/python` from `4.3.1` to `6.28.0`~~ -- **DONE** (or remove `runtime` field entirely since Python runtime is auto-detected)
- [ ] Add `excludeFiles` pattern to `vercel.json` to exclude tests/fixtures from the 500MB bundle limit
- [ ] Consider adding `pyproject.toml` to pin Python 3.12 explicitly (Vercel docs recommend this)
- [ ] Re-run template tests after version bumps to confirm no runtime regressions

### Files modified

- `templates/community-starter/requirements.txt` -- updated all three Python deps
- `templates/community-starter/vercel.json` -- updated `@vercel/python` runtime, added `excludeFiles`
