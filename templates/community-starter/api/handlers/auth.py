"""Auth handler — login, logout, signup, password reset."""
import json
import os

from api._supabase import db, get_user_from_request


def handle_GET(request):
    """GET /api/auth?action=session — validate current token."""
    params = request['params']
    action = params.get('action', [''])[0]

    if action == 'session':
        return _handle_session(request)
    return None  # Unknown action


def handle_POST(request):
    """POST /api/auth — login, logout, signup, reset_password."""
    data = request['data']
    action = data.get('action', '')

    if action == 'login':
        return _handle_login(data)
    elif action == 'signup':
        return _handle_signup(data)
    elif action == 'reset_password':
        return _handle_reset_password(data)
    return None


def _handle_session(request):
    user = get_user_from_request(request['headers'])
    if not user:
        return (401, {'success': False, 'error': 'Not authenticated'})
    result = db().table('members').select('*').eq('user_id', user.id).single().execute()
    if not result.data:
        return (404, {'success': False, 'error': 'Member not found'})
    return (200, {'success': True, 'user': _safe_member(result.data)})


def _handle_login(data):
    email = (data.get('email') or '').lower().strip()
    password = data.get('password', '')
    if not email or not password:
        return (400, {'success': False, 'error': 'Email and password required'})
    try:
        response = db().auth.sign_in_with_password({'email': email, 'password': password})
        session = response.session
        user = response.user
        if not session or not user:
            return (401, {'success': False, 'error': 'Invalid email or password'})
        result = db().table('members').select('*').eq('user_id', user.id).single().execute()
        member = result.data or {}
        return (200, {'success': True, 'token': session.access_token, 'member': _safe_member(member)})
    except Exception as e:
        print(f'Login error: {e}')
        return (401, {'success': False, 'error': 'Invalid email or password'})


def _handle_signup(data):
    email = (data.get('email') or '').lower().strip()
    password = data.get('password', '')
    name = (data.get('name') or '').strip()
    if not email or not password or not name:
        return (400, {'success': False, 'error': 'Email, password, and name required'})
    try:
        response = db().auth.sign_up({'email': email, 'password': password})
        user = response.user
        if not user:
            return (400, {'success': False, 'error': 'Signup failed'})
        db().table('members').insert({
            'user_id': user.id,
            'email': email,
            'name': name,
            'is_admin': False,
        }).execute()
        return (200, {'success': True, 'message': 'Account created. Check your email to confirm.'})
    except Exception as e:
        print(f'Signup error: {e}')
        return (400, {'success': False, 'error': 'Signup failed. Email may already be in use.'})


def _handle_reset_password(data):
    email = (data.get('email') or '').lower().strip()
    if not email:
        return (400, {'success': False, 'error': 'Email required'})
    site = os.environ.get('SITE_URL', '')
    try:
        db().auth.reset_password_email(email, options={
            'redirect_to': f'{site}/reset-password',
        })
    except Exception as e:
        print(f'Reset password error: {e}')
    return (200, {'success': True, 'message': 'If that email exists, a reset link has been sent.'})


def _safe_member(member: dict) -> dict:
    """Strip server-only fields before returning to client."""
    sensitive = {'password_hash', 'password_reset_token', 'password_reset_expires'}
    return {k: v for k, v in member.items() if k not in sensitive}
