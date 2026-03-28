"""
Supabase client — server-side only.

Uses the SERVICE_ROLE_KEY so RLS is bypassed at the DB level.
Authorization is enforced in the API layer (get_user_from_request).

Usage:
    from api._supabase import db, get_user_from_request

    user = get_user_from_request(self.headers)
    if not user:
        return self._send_error(401, "Authentication required")

    result = db.table('members').select('*').eq('user_id', user.id).execute()
"""
import os
from supabase import create_client, Client

_client: Client | None = None


def db() -> Client:
    """Return the Supabase admin client (service role key, bypasses RLS)."""
    global _client
    if _client is None:
        url = os.environ['SUPABASE_URL']
        key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
        _client = create_client(url, key)
    return _client


def get_user_from_request(headers):
    """
    Validate the Bearer token from the Authorization header.
    Returns a Supabase User object if valid, None otherwise.

    The token is a Supabase Auth JWT — issued on login, valid for 1 hour,
    auto-refreshed by the frontend Supabase client.
    """
    token = headers.get('Authorization', '').replace('Bearer ', '').strip()
    if not token:
        return None
    try:
        response = db().auth.get_user(token)
        return response.user
    except Exception as e:
        print(f"Auth validation error: {e}")
        return None


def is_admin(user_id: str) -> bool:
    """Check if the given user_id has is_admin=true in the members table."""
    try:
        result = db().table('members').select('is_admin').eq('user_id', user_id).single().execute()
        return bool(result.data and result.data.get('is_admin'))
    except Exception:
        return False
