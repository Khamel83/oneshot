# task_06: Context7 MCP — verify API call signatures

## Goal
Use Context7 MCP to pull live supabase-py and resend docs and verify every API call in
the community-starter code matches the current documented signatures.

## Tool to use
`mcp__plugin_context7_context7__resolve-library-id` then `mcp__plugin_context7_context7__query-docs`

## Calls to verify in _supabase.py
```python
create_client(url, key)                          # Constructor
db().auth.get_user(token)                        # Auth validation
db().auth.sign_in_with_password({'email', 'password'})  # Login
db().auth.sign_up({'email', 'password'})         # Signup
db().auth.reset_password_email(email, options={}) # Password reset
db().table('x').select('cols').eq('col','val').single().execute()  # Query
db().table('x').insert({...}).execute()          # Insert
db().table('x').update({...}).eq(...).execute()  # Update
db().table('x').delete().eq(...).execute()       # Delete
```

## Calls to verify in email.py
```python
resend.Emails.send(params)                       # Send email
resend.ApiKeys.list()                            # Connectivity check
resend.exceptions.RateLimitError                 # Exception class
```

## Output
Write results to `/home/ubuntu/github/oneshot/plans/community-starter/CONTEXT7_AUDIT.md`

Format per call:
```
✅ create_client(url, key) — matches docs (supabase-py 2.x)
✅ auth.get_user(token) — matches docs
❌ auth.sign_up({'email','password'}) — docs show options dict changed in 2.x, fix needed
```

## If any calls are wrong
Fix the code in `templates/community-starter/api/` directly.
