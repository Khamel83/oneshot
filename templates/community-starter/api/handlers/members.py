"""Members handler — list, view profile, update profile."""
from api._supabase import db, get_user_from_request

PUBLIC_COLUMNS = 'user_id,name,avatar_url,bio,joined_at'
OWN_COLUMNS = 'user_id,name,email,avatar_url,bio,joined_at,is_admin'


def handle_GET(request):
    params = request['params']
    action = params.get('action', [''])[0]
    member_id = params.get('id', [''])[0]

    if action == 'me':
        return _handle_me(request)
    elif member_id:
        return _handle_view_member(member_id)
    else:
        return _handle_list()


def handle_POST(request):
    data = request['data']
    action = data.get('action', '')

    if action == 'update_profile':
        return _handle_update_profile(request, data)
    return None


def _handle_me(request):
    user = get_user_from_request(request['headers'])
    if not user:
        return (401, {'success': False, 'error': 'Authentication required'})
    result = db().table('members').select(OWN_COLUMNS).eq('user_id', user.id).single().execute()
    if not result.data:
        return (404, {'success': False, 'error': 'Member not found'})
    return (200, {'success': True, 'member': result.data})


def _handle_view_member(member_id):
    result = db().table('members').select(PUBLIC_COLUMNS).eq('user_id', member_id).single().execute()
    if not result.data:
        return (404, {'success': False, 'error': 'Member not found'})
    return (200, {'success': True, 'member': result.data})


def _handle_list():
    result = db().table('members').select(PUBLIC_COLUMNS).order('name').execute()
    return (200, {'success': True, 'members': result.data or []})


def _handle_update_profile(request, data):
    user = get_user_from_request(request['headers'])
    if not user:
        return (401, {'success': False, 'error': 'Authentication required'})
    allowed = {'name', 'bio', 'avatar_url'}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return (400, {'success': False, 'error': 'No valid fields to update'})
    try:
        result = db().table('members').update(updates).eq('user_id', user.id).execute()
        if not result.data:
            return (500, {'success': False, 'error': 'Update failed'})
        return (200, {'success': True, 'member': result.data[0]})
    except Exception as e:
        print(f'Profile update error: {e}')
        return (500, {'success': False, 'error': 'An unexpected error occurred'})
