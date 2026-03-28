"""
Auth handler — login, logout, OAuth callback.

Uses Supabase Auth (handles hashing, JWTs, OAuth).
Supports Google OAuth and email/password.

Endpoints:
    POST /api/auth  {"action": "login", "email": "...", "password": "..."}
    POST /api/auth  {"action": "logout"}
    GET  /api/auth?action=session   (validate current token)
"""
import json
import os
from http.server import BaseHTTPRequestHandler

from api._supabase import db, get_user_from_request


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(self.path).query)
        action = params.get('action', [''])[0]

        if action == 'session':
            user = get_user_from_request(self.headers)
            if not user:
                self._send_error(401, 'Not authenticated')
                return
            # Fetch member profile
            result = db().table('members').select('*').eq('user_id', user.id).single().execute()
            if not result.data:
                self._send_error(404, 'Member not found')
                return
            self._send_success({'user': self._safe_member(result.data)})
        else:
            self._send_error(400, 'Unknown action')

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length) or '{}')
        except Exception:
            self._send_error(400, 'Invalid JSON')
            return

        action = data.get('action', '')

        if action == 'login':
            self._handle_login(data)
        elif action == 'logout':
            self._handle_logout()
        elif action == 'signup':
            self._handle_signup(data)
        elif action == 'reset_password':
            self._handle_reset_password(data)
        else:
            self._send_error(400, 'Unknown action')

    def _handle_login(self, data):
        email = (data.get('email') or '').lower().strip()
        password = data.get('password', '')
        if not email or not password:
            self._send_error(400, 'Email and password required')
            return
        try:
            response = db().auth.sign_in_with_password({'email': email, 'password': password})
            session = response.session
            user = response.user
            if not session or not user:
                self._send_error(401, 'Invalid email or password')
                return
            # Load member profile
            result = db().table('members').select('*').eq('user_id', user.id).single().execute()
            member = result.data or {}
            self._send_success({
                'token': session.access_token,
                'member': self._safe_member(member),
            })
        except Exception as e:
            print(f'Login error: {e}')
            self._send_error(401, 'Invalid email or password')

    def _handle_signup(self, data):
        email = (data.get('email') or '').lower().strip()
        password = data.get('password', '')
        name = (data.get('name') or '').strip()
        if not email or not password or not name:
            self._send_error(400, 'Email, password, and name required')
            return
        try:
            response = db().auth.sign_up({'email': email, 'password': password})
            user = response.user
            if not user:
                self._send_error(400, 'Signup failed')
                return
            # Create member row
            db().table('members').insert({
                'user_id': user.id,
                'email': email,
                'name': name,
                'is_admin': False,
            }).execute()
            self._send_success({'message': 'Account created. Check your email to confirm.'})
        except Exception as e:
            print(f'Signup error: {e}')
            self._send_error(400, 'Signup failed. Email may already be in use.')

    def _handle_logout(self):
        # Client should discard the token; nothing server-side to invalidate for JWTs
        # (Supabase supports server-side revocation via sign_out if needed)
        self._send_success({'message': 'Logged out'})

    def _handle_reset_password(self, data):
        email = (data.get('email') or '').lower().strip()
        if not email:
            self._send_error(400, 'Email required')
            return
        site_url = os.environ.get('SITE_URL', '')
        try:
            db().auth.reset_password_email(email, options={
                'redirect_to': f'{site_url}/reset-password',
            })
            # Always 200 — don't reveal whether email exists
            self._send_success({'message': 'If that email exists, a reset link has been sent.'})
        except Exception as e:
            print(f'Reset password error: {e}')
            self._send_success({'message': 'If that email exists, a reset link has been sent.'})

    def _safe_member(self, member: dict) -> dict:
        """Strip any server-only fields before returning to client."""
        sensitive = {'password_hash', 'password_reset_token', 'password_reset_expires'}
        return {k: v for k, v in member.items() if k not in sensitive}

    def _send_success(self, data: dict):
        body = json.dumps({'success': True, **data}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str):
        body = json.dumps({'success': False, 'error': message}).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Suppress default Vercel request logs
