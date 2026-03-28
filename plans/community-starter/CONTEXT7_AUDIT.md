# Context7 API Signature Audit

Verified via Context7 MCP against current docs (2026-03-27).

## supabase-py

| Call | File | Status | Notes |
|------|------|--------|-------|
| `create_client(url, key)` | _supabase.py:17 | ✅ matches | Standard constructor |
| `db().auth.get_user(token)` | _supabase.py:44 | ✅ matches | Sync client, JWT param |
| `db().auth.sign_in_with_password({'email':..., 'password':...})` | auth.py:68 | ✅ matches | Dict form confirmed for sync client |
| `db().auth.sign_up({'email':..., 'password':...})` | auth.py:93 | ✅ matches | Dict form confirmed |
| `db().auth.reset_password_email(email, options={'redirect_to':...})` | auth.py:122 | ✅ matches | Standard supabase-py signature |
| `.table('x').select('cols').eq('col','val').single().execute()` | auth.py:32,75; members.py:33,40; _supabase.py:54 | ✅ matches | Postgrest query builder |
| `.table('x').insert({...}).execute()` | auth.py:99; email.py:76 | ✅ matches | |
| `.table('x').update({...}).eq(...).execute()` | admin.py:65; members.py:79 | ✅ matches | |
| `.table('x').delete().eq(...).execute()` | admin.py:74 | ✅ matches | |
| `.table('x').select('cols').order('name').execute()` | admin.py:39; members.py:48 | ✅ matches | |
| `.table('x').select('cols').gte('col', val).execute()` | email.py:160 | ✅ matches | |

## resend-python

| Call | File | Status | Notes |
|------|------|--------|-------|
| `resend.Emails.send(params)` | email.py:46 | ✅ matches | Params dict: from, to, subject, html, reply_to |
| `resend.exceptions.RateLimitError` | email.py:48 | ✅ matches | Confirmed exception class |
| `resend.api_key = key` | email.py:25 | ✅ matches | Standard init pattern |

## Deprecation Notice

Context7 returned a deprecation warning for the `gotrue` package:
> "The `gotrue` package is deprecated, is not going to receive updates in the future. Please, use `supabase_auth` instead."

This is a transitive dependency (supabase-py → gotrue). It appears in pytest warnings but does NOT affect API signatures. The supabase-py client wraps this internally. No code changes needed now — the supabase team will migrate in a future release.

## Verdict

**All 13 API calls match current docs.** No fixes required.
