"""Admin handler — admin-only operations."""
from api._supabase import db, get_user_from_request, is_admin


def _require_admin(headers):
    """Returns user if valid admin session, None otherwise."""
    user = get_user_from_request(headers)
    if not user:
        return None
    if not is_admin(user.id):
        return None
    return user


def handle_GET(request):
    user = _require_admin(request['headers'])
    if not user:
        return (403, {'success': False, 'error': 'Admin access required'})
    params = request['params']
    action = params.get('action', [''])[0]

    if action == 'members':
        result = db().table('members').select('*').order('name').execute()
        return (200, {'success': True, 'members': result.data or []})
    return (400, {'success': False, 'error': 'Unknown action'})


def handle_POST(request):
    user = _require_admin(request['headers'])
    if not user:
        return (403, {'success': False, 'error': 'Admin access required'})
    data = request['data']
    action = data.get('action', '')

    if action == 'set_admin':
        return _handle_set_admin(data)
    elif action == 'delete_member':
        return _handle_delete_member(data)
    return (400, {'success': False, 'error': 'Unknown action'})


def _handle_set_admin(data):
    target_id = data.get('user_id', '')
    new_value = bool(data.get('is_admin', False))
    if not target_id:
        return (400, {'success': False, 'error': 'user_id required'})
    result = db().table('members').update({'is_admin': new_value}).eq('user_id', target_id).execute()
    return (200, {'success': True, 'updated': bool(result.data)})


def _handle_delete_member(data):
    target_id = data.get('user_id', '')
    if not target_id:
        return (400, {'success': False, 'error': 'user_id required'})
    db().table('members').delete().eq('user_id', target_id).execute()
    return (200, {'success': True, 'deleted': True})
