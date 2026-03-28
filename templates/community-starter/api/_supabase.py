"""
Supabase client — server-side only, multi-tenant aware.

Uses the SERVICE_ROLE_KEY so RLS is bypassed at the DB level.
Authorization is enforced in the API layer (get_user_from_request).

Multi-tenant: call set_site(slug) before any db() calls in a request.
This sets the Accept-Profile header so all queries target the correct schema.

Usage:
    from api._supabase import db, get_user_from_request, set_site

    set_site('gambling')  # targets gambling.members, gambling.email_log
    user = get_user_from_request(headers)
    result = db().table('members').select('*').eq('user_id', user.id).execute()
"""
import os
from urllib.parse import urlparse, parse_qs
from supabase import create_client, Client

_client: Client | None = None
_current_site: str | None = None


def set_site(slug: str):
    """Set the site context for all subsequent db() calls in this request."""
    global _current_site
    _current_site = slug


def get_site() -> str | None:
    """Return the current site context."""
    return _current_site


def db() -> Client:
    """Return the Supabase admin client, scoped to the current site schema."""
    global _client
    if _client is None:
        url = os.environ['SUPABASE_URL']
        key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
        _client = create_client(url, key)
    if _current_site:
        _client.postgrest.session.headers["Accept-Profile"] = _current_site
    return _client


def _raw_db() -> Client:
    """Return the Supabase client without any site schema context (queries public schema)."""
    global _client
    if _client is None:
        url = os.environ['SUPABASE_URL']
        key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
        _client = create_client(url, key)
    # Remove site schema if set
    _client.postgrest.session.headers.pop("Accept-Profile", None)
    return _client


def get_user_from_request(headers):
    """
    Validate the Bearer token from the Authorization header.
    Returns a Supabase User object if valid, None otherwise.
    """
    token = headers.get('Authorization', '').replace('Bearer ', '').strip()
    if not token:
        return None
    try:
        response = db().auth.get_user(token)
        return response.user
    except Exception as e:
        print(f'Auth validation error: {e}')
        return None


def is_admin(user_id: str) -> bool:
    """Check if the given user_id has is_admin=true in the current site's members table."""
    try:
        result = db().table('members').select('is_admin').eq('user_id', user_id).single().execute()
        return bool(result.data and result.data.get('is_admin'))
    except Exception:
        return False


def site_exists(slug: str) -> bool:
    """Check if a site exists in the public.sites table."""
    try:
        result = _raw_db().table('sites').select('id').eq('slug', slug).execute()
        return bool(result.data)
    except Exception:
        return False


def parse_request_path(path: str) -> tuple:
    """
    Parse a request path into (site_slug, endpoint, query_params).

    /gambling/api/auth?action=session → ('gambling', 'api/auth', {'action': ['session']})
    /api/system                       → (None, 'api/system', {})
    /gambling/login                    → ('gambling', 'login', {})
    /                                  → (None, '', {})
    """
    parsed = urlparse(path)
    parts = parsed.path.strip('/').split('/')
    params = parse_qs(parsed.query)

    # No path parts
    if not parts or parts == ['']:
        return None, '', params

    # API calls: /{site}/api/{handler} or /api/{handler}
    if len(parts) >= 2 and parts[1] == 'api':
        # Has site prefix
        return parts[0], 'api/' + '/'.join(parts[2:]), params

    if parts[0] == 'api':
        # No site prefix, direct API call
        return None, 'api/' + '/'.join(parts[1:]), params

    # Page requests: /{site}/login, /{site}/dashboard, etc.
    if len(parts) >= 2:
        return parts[0], parts[1], params

    # Single segment like "login" with no site prefix
    return None, parts[0], params
